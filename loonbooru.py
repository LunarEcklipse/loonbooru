import os
import sys
import threading
from flask import Flask, render_template, request, redirect, url_for, abort, flash, make_response, session, escape
from flask import __version__ as currentflaskver
from werkzeug.utils import secure_filename
import imghdr
import uuid
import json
from PIL import Image, ImageChops
from PIL import __version__ as currentpilver
import loonboorumysql
import re
import secrets
import hashlib
import shutil
import loonbooru_adminfunc
import booruobj
from datetime import datetime
import html

loonbooru_version = "0.4.4"

if __name__ == "__main__":
    print("Hi, I don't run on my own. Please run \"wsgi.py\" instead.")
    sys.exit()

### FLAGS ###

absPath = os.path.abspath(__file__) # This little chunk makes sure the working directory is correct.
dname = os.path.dirname(absPath)
os.chdir(dname)
templatepath = os.path.join(dname + '/rsc/template')
filestorepath = os.path.join(dname + '/rsc/file')
filestorepathfull = os.path.join(dname + '/rsc/file/full')

raw = None
with open(dname + "/config.json") as flagsfl:
    raw = flagsfl.read()
flags = json.loads(raw)
del raw
site_name = flags["site_name"]
site_url_name = flags["site_url_name"]
cdn_url = flags["cdn_url"]
upload_directory = flags["upload_directory"]
use_flat_tag = flags["useflat"] # Hi Umbreon
upload_allowed_extensions = {'jpg', 'png', 'gif', 'jpeg'}
filesavepath = f"{upload_directory}/../tempprocessed"
fileparampath = f"{upload_directory}/../params"
# TODO: Make a task scheduling thread here!

def RemoveDeadFileProcesses():
    deadprocessingfilelist = [f for f in os.listdir(filesavepath) if os.path.isfile(os.path.join(filesavepath, f))] # TODO: This is super lazy and could be condensed a lot better. Also likely to become unused later on.
    for i in deadprocessingfilelist:
        try:
            os.remove(os.path.join(filesavepath, i))
        except FileNotFoundError as exception:
            pass
    deadprocessingfilelist = [f for f in os.listdir(fileparampath) if os.path.isfile(os.path.join(fileparampath, f))]
    for i in deadprocessingfilelist:
        try:
            os.remove(os.path.join(fileparampath, i))
        except FileNotFoundError as exception:
            pass
    deadprocessingfilelist = [f for f in os.listdir(upload_directory) if os.path.isfile(os.path.join(upload_directory, f))]
    for i in deadprocessingfilelist:
        try:
            os.remove(os.path.join(upload_directory, i))
        except FileNotFoundError as exception:
            pass
    return

deadfileprocesses = threading.Thread(target=RemoveDeadFileProcesses, daemon=True)
deadfileprocesses.start()

app = Flask(__name__, template_folder=templatepath)
app.config['MAX_CONTENT_LENGTH'] = (32 * 1000 * 1000 * 1000) # Uploads limited to 16 mb
app.config['UPLOAD_FOLDER'] = upload_directory
app.secret_key = secrets.token_urlsafe(32)

def GetFlaskVersion() -> str:
    return currentflaskver

# THE CODE FOR SPACE IS %20
# THE CODE FOR COMMA IS %2C

def GenerateBrowseThumbnail(filename: str, browsepage: int, maxfiles: int, browsetype:str="browse", browsepagespecial:str=None) -> str: #TODO: UPDATE TO SUPPORT 64px and 256px thumbnails!
    browsepage = str(browsepage)
    file = (os.path.splitext(filename))
    file_ext = file[1]
    if file[1] == ".gif":
        file_ext = ".png"
    ### RETURN BELOW FOR DEEZ NUTS ###
    # return f"<div class=\"imgholder\" onclick=\"location.href='{site_url_name}/view/{file[0]}?browsepage={str(browsepage)}&maxfiles={str(maxfiles)}';\" style=\"overflow:hidden; cursor:pointer; min-width:128px; min-height:128px; width:20%; height:20%; max-width: 128px; max-height: 128px; border-style: solid; border-color: #c7ae40; overflow: hidden; border-radius:10px; display:inline-block; align-items: center;\"><div style=\"width: 100%; height: 100%; display:flex; justify-content: center; align-items: center;\"><img style = \"height: 128px; display:block; margin:auto; vertical-align:middle;\" src=\"https://cdn.dev.lunarecklipse.ca/dz.png\"></div></div>\n"
    if browsetype == "browse":
        return f"<div class=\"imgholder\" onclick=\"location.href='{site_url_name}/view/{file[0]}?browsetype={browsetype}&browsepage={str(browsepage)}&maxfiles={str(maxfiles)}';\"><div class=\"imgholderinner\"><img class=\"tileimg\" src=\"{cdn_url}/thumb/128/{file[0]}{file_ext}\"></div></div>\n"
    return f"<div class=\"imgholder\" onclick=\"location.href='{site_url_name}/view/{file[0]}?browsetype={browsetype}&browsepage={str(browsepage)}&maxfiles={str(maxfiles)}&browsepagespecial={str(browsepagespecial)}';\"><div class=\"imgholderinner\"><img class=\"tileimg\" src=\"{cdn_url}/thumb/128/{file[0]}{file_ext}\"></div></div>\n"
    
def GenerateBrowseThumbnailKChan(filepath: str, filename: str, display_name: str, browsepage: int, maxfiles: int) -> str:
    file = (os.path.splitext(filename))
    file_ext = file[1]
    if file[1] == ".gif":
        file_ext = ".png"
    ### RETURN BELOW FOR DEEZ NUTS ###
    # return f"<div class=\"imgholder\" onclick=\"location.href='{site_url_name}/view/{file[0]}?browsepage={str(browsepage)}&maxfiles={str(maxfiles)}';\" style=\"overflow:hidden; cursor:pointer; min-width:128px; min-height:128px; width:20%; height:20%; max-width: 128px; max-height: 128px; border-style: solid; border-color: #c7ae40; overflow: hidden; border-radius:10px; display:inline-block; align-items: center;\"><div style=\"width: 100%; height: 100%; display:flex; justify-content: center; align-items: center;\"><img style = \"height: 128px; display:block; margin:auto; vertical-align:middle;\" src=\"https://cdn.dev.lunarecklipse.ca/dz.png\"></div></div>\n"
    return f"<div class=\"imgholder\" onclick=\"document.getElementById(\'kiryumode\').play();\"><div class=\"imgholderinner\"><img class=\"tileimg\" src=\"{cdn_url}/thumb/128/{file[0]}{file_ext}\"></div></div>\n"

def ValidateAge(ageses) -> bool: # Takes in a Flask session object, returns whether or not the user's age has been verified.
    if ageses != None:
        if 'auth_token' in ageses:
            authchk = loonboorumysql.ValidateAuthToken(ageses['auth_token'])
            if authchk[0] == True:
                return True
        if 'verified_age' in ageses:
            if ageses['verified_age'] == True:
                return True
    return False

def AuthenticateUserAuth(usrsession) -> bool:
    if usrsession != None:
        if "auth_token" in usrsession:
            authchk = loonboorumysql.ValidateAuthToken(usrsession['auth_token'])
            if authchk[0] == True:
                return True
    return False

def ParseTags(inStr: str) -> list:
    ls = inStr.split(',')
    tagls = []
    for i in ls:
        i = i.strip()
        # if re.search(r"kiryu cha+n", re.escape(i)) != None: # Umbreone exclusive feature... Shush.
        #     i = "jess"
        if i != "":
            tagls.append(booruobj.TagType(i))
    return tagls

@app.route('/agecheck', methods=['GET'])
def agecheck():
    arg = request.args.to_dict()
    dest = "browse"
    if "dest" in arg:
        dest = arg["dest"]
    page = "1"
    if "page" in arg:
        page = arg["page"]
    maxfiles = "25"
    if "maxfiles" in arg:
        maxfiles = arg["maxfiles"]
    browsetype = "browse"
    if browsetype in arg:
        browsetype = arg["browsetype"]
    browsepage = "1"
    if browsepage in arg:
        browsepage = arg["browsepage"]
    tags = ""
    if "tags" in arg:
        tags = arg["tags"]
    if ValidateAge(session) == True:
        return redirect(f"{site_url_name}/redirect?dest={dest}&page={page}&maxfiles={maxfiles}&tags={tags}", 302)
    return render_template("index.html", SITE_NAME=site_name, DESTINATION=dest, PAGE=page, MAXFILES=maxfiles, SEARCHTAGS=tags)

@app.route('/agevalidate', methods=['POST'])
def agevalidate():
    arg = request.args.to_dict()
    dest = "browse"
    if "dest" in request.form:
        dest = request.form["dest"]
    page = "1"
    if "page" in request.form:
        page = request.form["page"]
    maxfiles = "25"
    if "maxfiles" in request.form:
        maxfiles = request.form["maxfiles"]
    tags = ""
    if "tags" in request.form:
        tags = request.form["tags"]
    browsetype = "browse"
    if browsetype in request.form:
        browsetype = request.form["browsetype"]
    browsepage = "1"
    if browsepage in request.form:
        browsepage = arg["browsepage"]
    session['verified_age'] = True
    if dest == "view":
        return redirect(f"{site_url_name}/redirect?dest={dest}&page={page}&browsetype={browsetype}&browsepage={browsepage}&maxfiles={maxfiles}&tags={tags}")
    return redirect(f"{site_url_name}/redirect?dest={dest}&page={page}&maxfiles={maxfiles}&tags={tags}", 302)

@app.route('/redirect', methods=['GET']) # request.form prioritized over request.args
def pageredirect():
    arg = request.args.to_dict()
    dest = "browse"
    if "dest" in arg:
        dest = arg["dest"]
    page = "1"
    if "page" in arg:
        page = arg["page"]
    maxfiles = "25"
    if "maxfiles" in arg:
        maxfiles = arg["maxfiles"]
    browsetype = "browse"
    if browsetype in arg:
        browsetype = arg["browsetype"]
    browsepage = "1"
    if browsepage in arg:
        browsepage = arg["browsepage"]
    tags = ""
    if "tags" in arg:
        tags = arg["tags"]
    if ValidateAge(session) == False:
        return redirect(f"{site_url_name}/agecheck?dest={dest}&page={page}&maxfiles={maxfiles}&browsetype={browsetype}&browsepage={browsepage}&tags={tags}", 302)
    if dest == "upload":
        return redirect(f"{site_url_name}/upload")
    elif dest == "view":
        return redirect(f"{site_url_name}/view/{page}?maxfiles={maxfiles}&browsetype={browsetype}&browsepage={browsepage}&tags={tags}")
    return redirect(f"{site_url_name}/{dest}/{page}?maxfiles={maxfiles}&tags={tags}")

@app.route('/')
@app.route('/index')
def index():
    if ValidateAge(session) == False:
        return redirect(f"{site_url_name}/agecheck?dest=browse&page=1&maxfiles=25")
    return redirect(f"{site_url_name}/browse/1?maxfiles=25", code=301)

@app.route('/browse')
@app.route('/browse/')
def browseredir():
    arg = request.args.to_dict()
    maxfiles = "25"
    if "maxfiles" in arg:
         maxfiles = arg["maxfiles"]
    return redirect(f"{site_url_name}/browse/1?maxfiles={maxfiles}", code=302)

# BROWSE PARAMS:
# # filecount: number of files to return

@app.route('/browse/<page>')
def browse(page):
    arg = request.args.to_dict()
    maxfiles = 25
    if "maxfiles" in arg:
        try:
            maxfiles = int(arg["maxfiles"])
        except ValueError as exception:
            maxfiles = 25
        if maxfiles == 0:
            maxfiles = 1
        elif maxfiles < 0:
            maxfiles = maxfiles / -1
        elif maxfiles > 100:
            maxfiles = 100
    tags = None
    tagsstr = ""
    if "tags" in arg:
        tagsstr = arg["tags"]
        tags = ParseTags(arg["tags"])
    if page == None:
        return redirect(f"{site_url_name}/browse/1?maxfiles={str(maxfiles)}&tags={tagsstr}")
    if ValidateAge(session) == False:
        return redirect(f"{site_url_name}/agecheck?dest=browse&page={str(page)}&maxfiles={str(maxfiles)}&tags={tagsstr}")
    if page <= "0":
        return redirect(f"{site_url_name}/browse/1?maxfiles={str(maxfiles)}&tags={tagsstr}", code=302)
    try:
        page = int(page)
    except TypeError as exception:
        return redirect(f"{site_url_name}/browse/1?maxfiles={str(maxfiles)}&tags={tagsstr}", code=302)

    endoffiles = False

    browselisttpl = loonboorumysql.GetFileList(int(maxfiles), int(page), tags)
    browselist = browselisttpl[0]
    nextpgexists = browselisttpl[1]
    startbreak = 0
    linebreak = 5
    imginsert = ""
    for i in browselist:
        try:
            filepath = filestorepathfull + "/" + str(i.FileID) + "." + i.FileEXT
            with Image.open(filepath) as f:
                imginsert += GenerateBrowseThumbnail(i.Filename, page, maxfiles, browsetype="browse")
        except FileNotFoundError as exception:
            endoffiles = True
            break
        startbreak += 1
        if startbreak == linebreak:
            imginsert += "<br>"
            linebreak += 5
    if len(browselist) == 0:
        imginsert = "<p class=\"noimgtxt\">Sorry, seems there's nothing here!</p>"
    navinsert = "<hr style=\"border: solid 1px #c7ae40;\"><div style=\"text-align:center\">"
    nobtn = True
    if len(browselist) < maxfiles:
        endoffiles = True
    if nextpgexists == False:
        endoffiles = True
    if page != 1:
        nobtn = False
        prevpg = (int(page)) - 1
        navinsert += f"<div onclick=\"location.href='{site_url_name}/browse/{str(prevpg)}?maxfiles={str(maxfiles)}&tags={tagsstr}'\" style=\"cursor:pointer; border: 2px solid #c7ae40; display:inline-block; background:#3A3B3C; border-radius: 3px;\"><p style=\"margin:auto; padding:5px; color: #c7ae40;\">←</p></div>"
    if endoffiles == False:
        nobtn = False
        nextpg = (int(page)) + 1
        navinsert += f"<div onclick=\"location.href='{site_url_name}/browse/{str(nextpg)}?maxfiles={str(maxfiles)}&tags={tagsstr}'\" style=\"cursor:pointer; border: 2px solid #c7ae40; display:inline-block; background:#3A3B3C; border-radius: 3px;\"><p style=\"margin:auto; padding:5px; color: #c7ae40;\">→</p></div>"
    navinsert += "</div>"
    if nobtn:
        navinsert = ""
    loginstr = f"<p class=\"headertxt\">Not logged in. <a class=\"headertxt\" href=\"{site_url_name}/login?dest=browse&page={page}&maxfiles={maxfiles}&tags={tags}\">Log in.</a></p>"
    if AuthenticateUserAuth(session) == True:
        username = loonboorumysql.FetchUsernameFromAuthToken(session["auth_token"])
        loginstr = f"<p class=\"headertxt\">Logged in as {username}. <a class=\"headertxt\" href=\"{site_url_name}/logout?dest=browse&page={page}&maxfiles={maxfiles}&tags={tags}\">Log Out.</a></p>" # TODO: Continue here to put this into the render template at the header!
    return render_template("browse.html", SITE_NAME=site_name, IMAGEPAGEINSERT=imginsert, NAVBUTTONINSERT=navinsert, LOGIN_INFO=loginstr)

@app.route("/view/<page>") #TODO: Add back button that leads to the browse page so that people who pass through age check can get back!
def viewpage(page):
    arg = request.args.to_dict()
    maxfiles = "25"
    if "maxfiles" in arg:
        maxfiles = arg["maxfiles"]
    browsetype = "browse"
    if "browsetype" in arg:
        browsetype = arg["browsetype"]
    browsepage = "1"
    if "browsepage" in arg:
        browsepage = arg["browsepage"]
    browsepagespecial = None
    if "browsepagespecial" in arg:
        browsepagespecial = arg["browsepagespecial"]
    tags = ""
    if "tags" in arg:
        tags = arg["tags"]
    if ValidateAge(session) == False:
        if browsepagespecial == None:
            return redirect(f"{site_url_name}/agecheck?dest=view&page={str(page)}&browsetype={browsetype}&browsepage={browsepage}&maxfiles={maxfiles}&tags={tags}")
        return redirect(f"{site_url_name}/agecheck?dest=view&page={str(page)}&browsetype={browsetype}&browsepage={browsepage}&maxfiles={maxfiles}&tags={tags}&browsepagespecial={browsepagespecial}")
    try:
        page = str(page)
    except ValueError as exception:
        abort(404)
    backbtnlink = ""
    if browsetype == "browse":
        backbtnlink = f"{site_url_name}/{browsetype}/{browsepage}?maxfiles={maxfiles}&tags={tags}"
    else:
        backbtnlink = f"{site_url_name}/{browsetype}/{browsepagespecial}?page={browsepage}&maxfiles={maxfiles}"
    file = loonboorumysql.FetchFileDetail(page)
    if file == None:
        abort(404)
    tagprint = ""
    if file.Tags != None:
        file.Tags.sort(key=lambda lm: lm.TagName)
        for i in file.Tags:
            tagprint += html.escape(i.TagName) + ", "
    if tagprint == "":
        tagprint = "No tags found."
    else:
        tagprint = tagprint[:-2]
    artistprnt = "Unknown"
    if file.Artists != None and len(file.Artists) != 0:
        file.Artists.sort(key=lambda lm: lm.ArtistName)
        artistprnt = ""
        for i in file.Artists:
            artistname = html.escape(i.ArtistNameProper)
            artistprnt += f"{artistname}, "
        artistprnt = artistprnt[:-2]
        print(artistprnt)
    charprnt = ""
    if file.Characters != None and len(file.Characters) != 0:
        charprnt = ""
        if file.Characters != None and len(file.Characters) != 0:
            charprnt += "<p class=\"abouttxt\">"
            if len(file.Characters) == 1:
                charprnt += "Character: "
            else:
                charprnt += "Characters: "
            file.Characters.sort(key=lambda lm: lm.CharacterName)
            templs = file.Characters # This ensures that names don't show up twice when there's multiple declarations due to species.
            for i in file.Characters:
                occ = 0
                for j in templs:
                    if j.CharacterID == i.CharacterID and j.CharacterName == i.CharacterName:
                        occ += 1
                if occ > 1:
                    numtoremove = occ - 1
                    for j in range(numtoremove):
                        templs.remove(i)
            for i in templs:
                charname = html.escape(i.CharacterNameProper)
                charprnt += f"<a class=\"headertxt\" href=\"{site_url_name}/character/{i.CharacterID}?maxfiles={str(maxfiles)}&page=1\">{charname}</a>" # TODO: Continue here
                if i.CharacterOwner != None and len(i.CharacterOwner) != 0:
                    charprnt += " ("
                    for j in i.CharacterOwner:
                        characterusername = html.escape(j.UsernameProper)
                        charprnt += f"<a class=\"headertxt\" href=\"{site_url_name}/user/{j.UserID}?maxfiles={str(maxfiles)}&page=1\">{characterusername}</a>, "
                    charprnt = charprnt[:-2]
                    charprnt += "), "
            charprnt = charprnt[:-2]
            del templs
            charprnt += "</p>"
    specprnt = ""
    if file.Species != None and len(file.Species) != 0:
        specprnt = "<p class=\"abouttxt\">Species: "
        file.Species.sort(key=lambda lm: lm.SpeciesName)
        for i in file.Species:
            specnameinsert = html.escape(i.SpeciesNameProper)
            specprnt += f"<a class=\"headertxt\" href=\"{site_url_name}/species/{i.SpeciesID}?maxfiles={str(maxfiles)}&page=1\">{specnameinsert}</a>, "
            # if i.SpeciesUniverse != None and len(i.SpeciesUniverse) != 0: # Leaving this code in because I wrote it, but otherwise I'm commenting it out after feedback.
            #     specprnt += " ("
            #     for j in i.SpeciesUniverse:
            #         specprnt += f"{j.UniverseNameProper}, "
            #     specprnt = specprnt[:-1]
            #     specprnt = specprnt[:-1]
            #     specprnt += "), "
        specprnt = specprnt[:-2]
        specprnt += "</p>"
    campprnt = ""
    if file.Campaigns != None and len(file.Campaigns) != 0:
        campprnt = "<p class=\"abouttxt\">"
        if len(file.Campaigns) == 1:
            campprnt += "Campaign: "
        else:
            campprnt += "Campaigns: "
        file.Campaigns.sort(key=lambda lm: lm.CampaignName)
        for i in file.Campaigns:
            campnameinsert = html.escape(i.CampaignNameProper)
            campprnt += campnameinsert
            if i.CampaignOwner != None and len(i.CampaignOwner) != 0:
                campprnt += " ("
                for j in i.CampaignOwner:
                    campnameinsert = html.escape(j.UsernameProper)
                    campprnt += f"<a class=\"headertxt\" href=\"{site_url_name}/user/{j.UserID}?maxfiles={str(maxfiles)}&page=1\">{campnameinsert}</a>, "
                campprnt = campprnt[:-2]
                campprnt += ")"
            campprnt += ", "
        campprnt = campprnt[:-2]
        campprnt += "</p>"
    uniprnt = ""
    if file.Universes != None and len(file.Universes) != 0:
        uniprnt = "<p class=\"abouttxt\">"
        if len(file.Universes) == 1:
            uniprnt += "Universe: "
        else:
            uniprnt += "Universes: "
        file.Universes.sort(key=lambda lm: lm.UniverseName)
        for i in file.Universes:
            uninameinsert = html.escape(i.UniverseNameProper)
            uniprnt += uninameinsert
            if i.UniverseOwner != None and len(i.UniverseOwner) != 0:
                uniprnt += " ("
                for j in i.UniverseOwner:
                    uninameinsert = html.escape(j.UsernameProper)
                    uniprnt += f"<a class=\"headertxt\" href=\"{site_url_name}/user/{j.UserID}?maxfiles={str(maxfiles)}&page=1\">{uninameinsert}</a>, "
                uniprnt = uniprnt[:-2]
                uniprnt += ")"
            uniprnt += ", "
        uniprnt = uniprnt[:-2]
        uniprnt += "</p>"
    loginstr = f"<p class=\"headertxt\">Not logged in. <a class=\"headertxt\" href=\"{site_url_name}/login?dest=browse&page={page}&maxfiles={maxfiles}&tags={tags}\">Log in.</a></p>"
    if AuthenticateUserAuth(session) == True:
        username = html.escape(loonboorumysql.FetchUsernameFromAuthToken(session["auth_token"]))
        loginstr = f"<p class=\"headertxt\">Logged in as {username}. <a class=\"headertxt\" href=\"{site_url_name}/logout?dest=view&page={page}&maxfiles={maxfiles}&tags={tags}\">Log Out.</a></p>"
    return render_template("view.html", SITE_NAME=site_name, DESCRIPTION=file.Description, DISPLAY_NAME=file.DisplayName, FILE_PATH=f"{cdn_url}/full/{file.FileID}.{file.FileEXT}", ARTIST_NAME=artistprnt, FILE_RATING=file.FileRating, UPLOAD_DATE=file.UploadDatetime, TAG_LIST=tagprint, CHAR_LIST=charprnt, SPEC_LIST=specprnt, CAMPAIGN_LIST=campprnt, UNIVERSE_LIST=uniprnt, LOGIN_INFO=loginstr, BACK_BTN_LINK=backbtnlink)

@app.route("/search/<page>")
def SearchFSlashRedirect(page):
    arg = request.args.to_dict()
    maxfiles = "25"
    if "maxfiles" in arg:
        maxfiles = arg["maxfiles"]
    tags = ""
    if "tags" in arg:
        tags = arg["tags"]
    if page != None:
        if ValidateAge(session) == False:
            return redirect(f"{site_url_name}/agecheck?dest=search&page={page}&maxfiles={str(maxfiles)}&tags={tags}")
        return redirect(f"{site_url_name}/search?maxfiles={str(maxfiles)}&tags={tags}&page={page}")
    if ValidateAge(session) == False:
        return redirect(f"{site_url_name}/agecheck?dest=search&maxfiles={str(maxfiles)}&tags={tags}")
    return redirect(f"{site_url_name}/search?maxfiles={str(maxfiles)}&tags={tags}")

@app.route("/search/")
def searchpage():
    arg = request.args.to_dict()
    maxfiles = "25"
    if "maxfiles" in arg:
        maxfiles = arg["maxfiles"]
    tags = ""
    page = "1"
    if "page" in arg:
        page = arg["page"]
    if "tags" in arg:
        tags = arg["tags"]
        if tags != "":
            return redirect(f"{site_url_name}/browse/{page}?maxfiles={str(maxfiles)}&tags={tags}")
    if ValidateAge(session) == False:
        return redirect(f"{site_url_name}/agecheck?dest=search&maxfiles={str(maxfiles)}&page={page}")
    loginstr = f"<p class=\"headertxt\">Not logged in. <a class=\"headertxt\" href=\"{site_url_name}/login?dest=browse&page={page}&maxfiles={maxfiles}&tags={tags}\">Log in.</a></p>"
    if AuthenticateUserAuth(session) == True:
        username = html.escape(loonboorumysql.FetchUsernameFromAuthToken(session["auth_token"]))
        loginstr = f"<p class=\"headertxt\">Logged in as {username}. <a class=\"headertxt\" href=\"{site_url_name}/logout?dest=search&page={page}&maxfiles={maxfiles}&tags={tags}\">Log Out.</a></p>"
    return render_template("search.html", SITE_NAME=site_name, LOGIN_INFO=loginstr)

@app.route("/user/<user_id>") # TODO: Continue with these for each category type
def usersearch(user_id: str):
    arg = request.args.to_dict()
    maxfiles="25"
    if "maxfiles" in arg:
        try:
            maxfiles = int(arg["maxfiles"])
        except ValueError as exception:
            maxfiles = 25
        if maxfiles == 0:
            maxfiles = 1
        elif maxfiles < 0:
            maxfiles = maxfiles / -1
        elif maxfiles > 100:
            maxfiles = 100
    maxfiles=int(maxfiles)
    page="1"
    if "page" in arg:
        page = arg["page"]
    page=int(page)
    if page < 1:
        page = 1

    if user_id == None:
        abort(400)
    if ValidateAge(session) == False:
        return redirect(f"{site_url_name}/agecheck?dest=user&page={user_id}&maxfiles={str(maxfiles)}")
    searchuser = loonboorumysql.FetchUserByUserID(user_id)
    if searchuser == None:
        abort(404)
    userfile = loonboorumysql.FetchAnyFileByUser(user_id)
    fileid = "nofilefound"
    fileext = "png"
    if userfile != None:
        fileid = userfile.FileID
        fileext = userfile.FileEXT
    
    # TODO: List owned characters, campaigns, universes, etc here!

    endoffiles = False
    browselisttpl = loonboorumysql.GetFileList(int(maxfiles), int(page), [f"uploaderid:{str(user_id)}"])
    browselist = browselisttpl[0]
    nextpgexists = browselisttpl[1]
    startbreak = 0
    linebreak = 5
    imginsert = ""
    for i in browselist:
        try:
            filepath = filestorepathfull + "/" + str(i.FileID) + "." + i.FileEXT
            with Image.open(filepath) as f:
                imginsert += GenerateBrowseThumbnail(i.Filename, page, maxfiles, "user", user_id)
        except FileNotFoundError as exception:
            endoffiles = True
            break
        startbreak += 1
        if startbreak == linebreak:
            imginsert += "<br>"
            linebreak += 5
    print(imginsert)
    if len(browselist) == 0:
        imginsert = "<p class=\"noimgtxt\">Sorry, seems there's nothing here!</p>"
    navinsert = "<hr style=\"border: solid 1px #c7ae40;\"><div style=\"text-align:center\">"
    nobtn = True
    if len(browselist) < maxfiles:
        endoffiles = True
    if nextpgexists == False:
        endoffiles = True
    if page != 1:
        nobtn = False
        prevpg = (int(page)) - 1
        navinsert += f"<div onclick=\"location.href='{site_url_name}/user/{user_id}?maxfiles={str(maxfiles)}&page={str(prevpg)}'\" style=\"cursor:pointer; border: 2px solid #c7ae40; display:inline-block; background:#3A3B3C; border-radius: 3px;\"><p style=\"margin:auto; padding:5px; color: #c7ae40;\">←</p></div>"
    if endoffiles == False:
        nobtn = False
        nextpg = (int(page)) + 1
        navinsert += f"<div onclick=\"location.href='{site_url_name}/user/{user_id}?maxfiles={str(maxfiles)}?maxfiles={str(maxfiles)}&page={str(nextpg)}'\" style=\"cursor:pointer; border: 2px solid #c7ae40; display:inline-block; background:#3A3B3C; border-radius: 3px;\"><p style=\"margin:auto; padding:5px; color: #c7ae40;\">→</p></div>"
    navinsert += "</div>"
    if nobtn:
        navinsert = ""
    loginstr = f"<p class=\"headertxt\">Not logged in. <a class=\"headertxt\" href=\"{site_url_name}/login?dest=user&page={page}&maxfiles={maxfiles}\">Log in.</a></p>"
    if AuthenticateUserAuth(session) == True:
        loginusername = html.escape(loonboorumysql.FetchUsernameFromAuthToken(session["auth_token"]))
        loginstr = f"<p class=\"headertxt\">Logged in as {loginusername}. <a class=\"headertxt\" href=\"{site_url_name}/logout?dest=user&page={user_id}&maxfiles={maxfiles}\">Log Out.</a></p>"
    return render_template("user.html", SITE_NAME=site_name, USER_NAME=searchuser.UsernameProper, FILE_PATH=f"{cdn_url}/full/{fileid}.{fileext}", LOGIN_INFO=loginstr, IMAGEPAGEINSERT=imginsert, NAVBUTTONINSERT=navinsert) # TODO: Finish and test this

@app.route("/character/<character_id>") # TODO: Continue with these for each category type
def charactersearch(character_id):
    arg = request.args.to_dict()
    maxfiles="25"
    if "maxfiles" in arg:
        try:
            maxfiles = int(arg["maxfiles"])
        except ValueError as exception:
            maxfiles = 25
        if maxfiles == 0:
            maxfiles = 1
        elif maxfiles < 0:
            maxfiles = maxfiles / -1
        elif maxfiles > 100:
            maxfiles = 100
    maxfiles=int(maxfiles)
    page="1"
    if "page" in arg:
        page = arg["page"]
    page=int(page)
    if page < 1:
        page = 1

    if character_id == None:
        abort(400)
    if ValidateAge(session) == False:
        return redirect(f"{site_url_name}/agecheck?dest=character&page={character_id}&maxfiles={str(maxfiles)}")
    character = loonboorumysql.GetCharacter(character_id)
    if character == None:
        abort(404)
    characterfile = loonboorumysql.FetchAnyFileWithCharacter(character_id)
    fileid = "nofilefound"
    fileext = "png"
    if characterfile != None:
        fileid = characterfile.FileID
        fileext = characterfile.FileEXT
    characterspecstr = ""
    for i in character.CharacterSpecies:
        characterspecstr += i.SpeciesNameProper + ", "
    if characterspecstr == "":
        characterspecstr = "None"
    else:
        characterspecstr = characterspecstr[:-2]
    characterownrstr = ""
    for i in character.CharacterOwner:
        characterownrstr += i.UsernameProper + ", "
    if characterownrstr == "":
        characterownrstr = "None"
    else:
        characterownrstr = characterownrstr[:-2]
    characterspecstr = html.escape(f"Character Species: {characterspecstr}")
    characterownrleadin = "Character Owner:"
    if len(character.CharacterOwner) > 1:
        characterownrleadin = "Character Owners:"
    characterownrstr = html.escape(f"{characterownrleadin} {characterownrstr}")

    endoffiles = False
    browselisttpl = loonboorumysql.GetFileList(int(maxfiles), int(page), [f"characterid:{str(character_id)}"])
    browselist = browselisttpl[0]
    print(type(browselist))
    nextpgexists = browselisttpl[1]
    startbreak = 0
    linebreak = 5
    imginsert = ""
    for i in browselist:
        try:
            filepath = filestorepathfull + "/" + str(i.FileID) + "." + i.FileEXT
            with Image.open(filepath) as f:
                imginsert += GenerateBrowseThumbnail(i.Filename, page, maxfiles, "character", character_id)
        except FileNotFoundError as exception:
            endoffiles = True
            break
        startbreak += 1
        if startbreak == linebreak:
            imginsert += "<br>"
            linebreak += 5
    if len(browselist) == 0:
        imginsert = "<p class=\"noimgtxt\">Sorry, seems there's nothing here!</p>"
    navinsert = "<hr style=\"border: solid 1px #c7ae40;\"><div style=\"text-align:center\">"
    nobtn = True
    if len(browselist) < maxfiles:
        endoffiles = True
    if nextpgexists == False:
        endoffiles = True
    if page != 1:
        nobtn = False
        prevpg = (int(page)) - 1
        navinsert += f"<div onclick=\"location.href='{site_url_name}/character/{character_id}?maxfiles={str(maxfiles)}&page={str(prevpg)}'\" style=\"cursor:pointer; border: 2px solid #c7ae40; display:inline-block; background:#3A3B3C; border-radius: 3px;\"><p style=\"margin:auto; padding:5px; color: #c7ae40;\">←</p></div>"
    if endoffiles == False:
        nobtn = False
        nextpg = (int(page)) + 1
        navinsert += f"<div onclick=\"location.href='{site_url_name}/character/{character_id}?maxfiles={str(maxfiles)}?maxfiles={str(maxfiles)}&page={str(nextpg)}'\" style=\"cursor:pointer; border: 2px solid #c7ae40; display:inline-block; background:#3A3B3C; border-radius: 3px;\"><p style=\"margin:auto; padding:5px; color: #c7ae40;\">→</p></div>"
    navinsert += "</div>"
    if nobtn:
        navinsert = ""
    loginstr = f"<p class=\"headertxt\">Not logged in. <a class=\"headertxt\" href=\"{site_url_name}/login?dest=character&page={page}&maxfiles={maxfiles}\">Log in.</a></p>"
    if AuthenticateUserAuth(session) == True:
        username = html.escape(loonboorumysql.FetchUsernameFromAuthToken(session["auth_token"]))
        loginstr = f"<p class=\"headertxt\">Logged in as {username}. <a class=\"headertxt\" href=\"{site_url_name}/logout?dest=character&page={character_id}&maxfiles={maxfiles}\">Log Out.</a></p>"
    return render_template("character.html", SITE_NAME=site_name, CHARACTER_NAME=character.CharacterNameProper, FILE_PATH=f"{cdn_url}/full/{fileid}.{fileext}", CHARACTER_SPECIES=characterspecstr, CHARACTER_OWNER=characterownrstr, LOGIN_INFO=loginstr, IMAGEPAGEINSERT=imginsert, NAVBUTTONINSERT=navinsert) # TODO: Finish and test this

@app.route("/species/<species_id>") # TODO: Continue with these for each category type
def speciessearch(species_id):
    arg = request.args.to_dict()
    maxfiles="25"
    if "maxfiles" in arg:
        try:
            maxfiles = int(arg["maxfiles"])
        except ValueError as exception:
            maxfiles = 25
        if maxfiles == 0:
            maxfiles = 1
        elif maxfiles < 0:
            maxfiles = maxfiles / -1
        elif maxfiles > 100:
            maxfiles = 100
    maxfiles=int(maxfiles)
    page="1"
    if "page" in arg:
        page = arg["page"]
    page=int(page)
    if page < 1:
        page = 1

    if species_id == None:
        abort(400)
    if ValidateAge(session) == False:
        return redirect(f"{site_url_name}/agecheck?dest=species&page={species_id}&maxfiles={str(maxfiles)}")
    species = loonboorumysql.GetSpecies(species_id)
    if species == None:
        abort(404)
    speciesfile = loonboorumysql.FetchAnyFileWithSpecies(species_id)
    fileid = "nofilefound"
    fileext = "png"
    if speciesfile != None:
        fileid = speciesfile.FileID
        fileext = speciesfile.FileEXT
    specuniversestr = ""
    for i in species.SpeciesUniverse:
        specuniversestr += i.UniverseProper + ", "
    if specuniversestr == "":
        specuniversestr = "None"
    else:
        specuniversestr = specuniversestr[:-2]
    specuniverseleadin = "Species Universe:"
    if len(species.SpeciesUniverse) > 1:
        specuniverseleadin = "Species Universes:"
    specuniversestr = html.escape(f"{specuniverseleadin} {specuniversestr}")

    endoffiles = False
    browselisttpl = loonboorumysql.GetFileList(int(maxfiles), int(page), [f"speciesid:{str(species_id)}"])
    browselist = browselisttpl[0]
    print(type(browselist))
    nextpgexists = browselisttpl[1]
    startbreak = 0
    linebreak = 5
    imginsert = ""
    for i in browselist:
        try:
            filepath = filestorepathfull + "/" + str(i.FileID) + "." + i.FileEXT
            with Image.open(filepath) as f:
                imginsert += GenerateBrowseThumbnail(i.Filename, page, maxfiles, "species", species_id)
        except FileNotFoundError as exception:
            endoffiles = True
            break
        startbreak += 1
        if startbreak == linebreak:
            imginsert += "<br>"
            linebreak += 5
    if len(browselist) == 0:
        imginsert = "<p class=\"noimgtxt\">Sorry, seems there's nothing here!</p>"
    navinsert = "<hr style=\"border: solid 1px #c7ae40;\"><div style=\"text-align:center\">"
    nobtn = True
    if len(browselist) < maxfiles:
        endoffiles = True
    if nextpgexists == False:
        endoffiles = True
    if page != 1:
        nobtn = False
        prevpg = (int(page)) - 1
        navinsert += f"<div onclick=\"location.href='{site_url_name}/character/{species_id}?maxfiles={str(maxfiles)}&page={str(prevpg)}'\" style=\"cursor:pointer; border: 2px solid #c7ae40; display:inline-block; background:#3A3B3C; border-radius: 3px;\"><p style=\"margin:auto; padding:5px; color: #c7ae40;\">←</p></div>"
    if endoffiles == False:
        nobtn = False
        nextpg = (int(page)) + 1
        navinsert += f"<div onclick=\"location.href='{site_url_name}/character/{species_id}?maxfiles={str(maxfiles)}?maxfiles={str(maxfiles)}&page={str(nextpg)}'\" style=\"cursor:pointer; border: 2px solid #c7ae40; display:inline-block; background:#3A3B3C; border-radius: 3px;\"><p style=\"margin:auto; padding:5px; color: #c7ae40;\">→</p></div>"
    navinsert += "</div>"
    if nobtn:
        navinsert = ""
    loginstr = f"<p class=\"headertxt\">Not logged in. <a class=\"headertxt\" href=\"{site_url_name}/login?dest=character&page={page}&maxfiles={maxfiles}\">Log in.</a></p>"
    if AuthenticateUserAuth(session) == True:
        username = html.escape(loonboorumysql.FetchUsernameFromAuthToken(session["auth_token"]))
        loginstr = f"<p class=\"headertxt\">Logged in as {html.escape(username)}. <a class=\"headertxt\" href=\"{site_url_name}/logout?dest=species&page={species_id}&maxfiles={maxfiles}\">Log Out.</a></p>"
    return render_template("species.html", SITE_NAME=site_name, SPECIES_NAME=species.SpeciesNameProper, FILE_PATH=f"{cdn_url}/full/{fileid}.{fileext}", LOGIN_INFO=loginstr, SPECIES_UNIVERSES=specuniversestr, IMAGEPAGEINSERT=imginsert, NAVBUTTONINSERT=navinsert) # TODO: Finish and test this

def hash_string(inStr): # Creates a string hash for use
    hash_obj = hashlib.sha256(inStr.encode('utf-8'))
    hex_dig = hash_obj.hexdigest()
    return hex_dig

def validate_filename(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in upload_allowed_extensions

def ProcessImageForUse(filename): # Processes pngs, jpgs, and gifs. TODO: Add support for webp, tiff, raw, eps, and .bmp if possible.
    filename = filename.lower()
    filenamefull = f"p_full_{filename}"
    filename256 = f"p_256_{filename}"
    filename128 = f"p_128_{filename}"
    filename64 = f"p_64_{filename}"
    size256 = 256, 256
    size128 = 128, 128
    size64 = 64, 64
    fileext = os.path.splitext(filename)
    if fileext[1] == ".png" or fileext[1] == ".jpg" or fileext[1] == ".jpeg":
        shutil.copyfile(os.path.join(upload_directory, filename), os.path.join(filesavepath, filenamefull))
        shutil.copyfile(os.path.join(upload_directory, filename), os.path.join(filesavepath, filename256))
        im = Image.open(os.path.join(filesavepath, filename256))
        im.thumbnail(size256, Image.ANTIALIAS)
        im.save(os.path.join(filesavepath, filename256))
        im.close()
        shutil.copyfile(os.path.join(upload_directory, filename), os.path.join(filesavepath, filename128))
        im = Image.open(os.path.join(filesavepath, filename128))
        im.thumbnail(size128, Image.ANTIALIAS)
        im.save(os.path.join(filesavepath, filename128))
        im.close()
        shutil.copyfile(os.path.join(upload_directory, filename), os.path.join(filesavepath, filename64))
        im = Image.open(os.path.join(filesavepath, filename64))
        im.thumbnail(size64, Image.ANTIALIAS)
        im.save(os.path.join(filesavepath, filename64))
        im.close()
    elif fileext[1] == ".gif":
        shutil.copyfile(os.path.join(upload_directory, filename), os.path.join(filesavepath, filenamefull))
        im = Image.open(os.path.join(upload_directory, filename))
        im.seek(0)
        filename256parsed = os.path.splitext(filename256)
        filename128parsed = os.path.splitext(filename128)
        filename64parsed = os.path.splitext(filename64)
        im.save(os.path.join(filesavepath, filename256parsed[0], ".png"))
        im.save(os.path.join(filesavepath, filename128parsed[0], ".png"))
        im.save(os.path.join(filesavepath, filename64parsed[0], ".png"))
        im = Image.open(os.path.join(filesavepath, filename256parsed[0], ".png"))
        im.thumbnail(size256, Image.ANTIALIAS)
        im.save(os.path.join(filesavepath, filename256parsed[0], ".png"))
        im.close()
        im = Image.open(os.path.join(filesavepath, filename128parsed[0], ".png"))
        im.thumbnail(size128, Image.ANTIALIAS)
        im.save(os.path.join(filesavepath, filename128parsed[0], ".png"))
        im.close()
        im = Image.open(os.path.join(filesavepath, filename64parsed[0], ".png"))
        im.thumbnail(size64, Image.ANTIALIAS)
        im.save(os.path.join(filesavepath, filename64parsed[0], ".png"))
        im.close()
    try:
        os.remove(os.path.join(upload_directory, filename))
    except FileNotFoundError as exception:
        pass
    return

def ProcessFileIntoDatabase(file_uuid: str, file_processing_thread: threading.Thread, paramfilepath: str): # What the fuck is wrong with you
    if file_processing_thread != None:
        file_processing_thread.join() # Wait for the file processing thread to complete, as long as one actually got passed through that is. The image shit takes a while.
    file = None
    try:
        file = open(paramfilepath, 'r', encoding="utf-8")
    except FileNotFoundError as exception:
        with open(os.path.join(upload_directory, "..", "params", f"error_params_{file_uuid}.txt", 'w', encoding="utf-8")) as errfile:
            errfile.write(f"ERROR: Params file not found for file UUID: \"{file_uuid}\".")
        return
    raw = file.read()
    file.close()
    fileparams = json.loads(raw)
    del raw, file
    fileext = os.path.splitext(fileparams["Full_Filename"])[1]
    fileidalreadyexists = loonboorumysql.CheckIfFileUUIDExists(fileparams["New_File_ID"]) # A little contingency in the one in a bajillion chance this UUID is already occupied.
    if fileidalreadyexists:
        new_file_id = None
        while fileidalreadyexists:
            new_file_id = str(uuid.uuid4().hex)
            fileidalreadyexists = loonboorumysql.CheckIfFileUUIDExists(new_file_id)
        fileparams["New_File_ID"] = new_file_id
    new_file_id = fileparams["New_File_ID"]
    thumbfileext = fileext
    if fileext == ".gif": # .gif thumbnails are .pngs, so convert them. Use this line if you convert additional thumbnails.
        thumbfileext = ".png"
    newfullfilepath = os.path.join(filestorepath, "full", f"{new_file_id}{fileext}")
    new256filepath = os.path.join(filestorepath, "thumb", "256", f"{new_file_id}{thumbfileext}")
    new128filepath = os.path.join(filestorepath, "thumb", "128", f"{new_file_id}{thumbfileext}")
    new64filepath = os.path.join(filestorepath, "thumb", "64", f"{new_file_id}{thumbfileext}")
    shutil.copyfile(os.path.join(filesavepath, fileparams["Full_Filename"]), newfullfilepath) # These copies can go through because the file will just be overwritten. #300IQCode
    shutil.copyfile(os.path.join(filesavepath, fileparams["256_Filename"]), new256filepath)
    shutil.copyfile(os.path.join(filesavepath, fileparams["128_Filename"]), new128filepath)
    shutil.copyfile(os.path.join(filesavepath, fileparams["64_Filename"]), new64filepath)
    fileext = fileext.replace(".", "")
    loonboorumysql.InsertNewFileIntoDatabase(new_file_id, fileparams["Uploader_ID"], fileext, fileparams["Display_Name"], fileparams["Description"], fileparams["Rating"], None, fileparams["Artist_List"], fileparams["Character_List"], fileparams["Species_List"], fileparams["Campaign_List"], fileparams["Universe_List"], fileparams["Tags_List"])
    try:
        os.remove(os.path.join(filesavepath, fileparams["Full_Filename"]))
    except FileNotFoundError as exception:
        pass
    try:
        os.remove(os.path.join(filesavepath, fileparams["256_Filename"]))
    except FileNotFoundError as exception:
        pass
    try:
        os.remove(os.path.join(filesavepath, fileparams["128_Filename"]))
    except FileNotFoundError as exception:
        pass
    try:
        os.remove(os.path.join(filesavepath, fileparams["64_Filename"]))
    except FileNotFoundError as exception:
        pass
    try:
        os.remove(paramfilepath)
    except FileNotFoundError as exception:
        pass
    return

def DeleteFilesFromBadUpload(badthread: threading.Thread, temp_filename: str, file_id: str): # Catches the thread processing files and then deletes them.
    if badthread == None:
        return
    if file_id == None:
        raise IndexError
    badthread.join()
    filetype = os.path.splitext(temp_filename)[1]
    thumbfiletype = filetype
    if filetype == ".gif":
        thumbfiletype = ".png"
    try:
        os.remove(os.path.join(upload_directory, temp_filename))
    except FileNotFoundError as exception:
        pass
    newfullfilepath = os.path.join(filestorepath, "full", f"{file_id}{filetype}")
    new256filepath = os.path.join(filestorepath, "thumb", "256", f"{file_id}{thumbfiletype}")
    new128filepath = os.path.join(filestorepath, "thumb", "128", f"{file_id}{thumbfiletype}")
    new64filepath = os.path.join(filestorepath, "thumb", "64", f"{file_id}{thumbfiletype}")
    try:
        os.remove(newfullfilepath)
    except FileNotFoundError as exception:
        pass
    try:
        os.remove(new256filepath)
    except FileNotFoundError as exception:
        pass
    try:
        os.remove(new128filepath)
    except FileNotFoundError as exception:
        pass
    try:
        os.remove(new64filepath)
    except FileNotFoundError as exception:
        pass
    tempfilelist = [f for f in os.listdir(filesavepath) if os.path.isfile(os.path.join(filesavepath, f))]
    for i in tempfilelist:
        if i.find(file_id) != -1:
            try:
                os.remove(os.path.join(filesavepath, i))
            except FileNotFoundError as exception:
                pass
    try:
        os.remove(os.path.join(fileparampath, f"params_{file_id}.json"))
    except FileNotFoundError as exception:
        pass
    return

@app.route("/upload", methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        if AuthenticateUserAuth(session) == False:
            abort(403) # TODO: This will work for now, but make a nicer looking version!
        if 'file' not in request.files:
            upload_flat = ""
            if use_flat_tag == True:
                upload_flat = "<label for=\"fileflat\">Flat:</label><input type=\"radio\" id=\"fileflatyes\" name=\"fileflat\" value=\"flatyes\"><label for=\"fileflatyes\">Yes</label><input type=\"radio\" id=\"fileflatno\" name=\"fileflat\" value=\"flatno\"><label for=\"fileflatno\">No</label><br>"
            return render_template("upload.html", UPLOAD_STATUS="No file was selected.", FLAT_RADIO=upload_flat)
        file = request.files['file']
        if file.filename == '':
            upload_flat = ""
            if use_flat_tag == True:
                upload_flat = "<label for=\"fileflat\">Flat:</label><input type=\"radio\" id=\"fileflatyes\" name=\"fileflat\" value=\"flatyes\"><label for=\"fileflatyes\">Yes</label><input type=\"radio\" id=\"fileflatno\" name=\"fileflat\" value=\"flatno\"><label for=\"fileflatno\">No</label><br>"
            return render_template("upload.html", UPLOAD_STATUS="No file was selected.", FLAT_RADIO=upload_flat)
        temp_uuid = str(uuid.uuid4().hex)
        filename = f"temp_{temp_uuid}_{secure_filename(file.filename.lower())}"
        if validate_filename(file.filename) == False:
            upload_flat = ""
            if use_flat_tag == True:
                upload_flat = "<label for=\"fileflat\">Flat:</label><input type=\"radio\" id=\"fileflatyes\" name=\"fileflat\" value=\"flatyes\"><label for=\"fileflatyes\">Yes</label><input type=\"radio\" id=\"fileflatno\" name=\"fileflat\" value=\"flatno\"><label for=\"fileflatno\">No</label><br>"
            return render_template("upload.html", UPLOAD_STATUS="The selected file format cannot be uploaded at the moment.", FLAT_RADIO=upload_flat)
        if file and validate_filename(file.filename):
            file.save(os.path.join(upload_directory, filename))
            imgprocessthread = threading.Thread(target=ProcessImageForUse, args=(filename,))
            imgprocessthread.start()
            uploadinfo = request.form.to_dict()
            file_displayname = uploadinfo["filename"]
            if file_displayname == None or file_displayname == "" or file_displayname.isspace() == True:
                badfilethread = threading.Thread(target=DeleteFilesFromBadUpload, args=(imgprocessthread, filename, temp_uuid))
                badfilethread.start()
                upload_flat = ""
                if use_flat_tag == True:
                    upload_flat = "<label for=\"fileflat\">Flat:</label><input type=\"radio\" id=\"fileflatyes\" name=\"fileflat\" value=\"flatyes\"><label for=\"fileflatyes\">Yes</label><input type=\"radio\" id=\"fileflatno\" name=\"fileflat\" value=\"flatno\"><label for=\"fileflatno\">No</label><br>"
                return render_template("upload.html", UPLOAD_STATUS="No filename was supplied.", FLAT_RADIO=upload_flat)
            file_description = uploadinfo["filedesc"]
            if file_description == None or file_description == "" or file_description.isspace() == True:
                file_description = None
            file_rating = None
            try:
                file_rating = uploadinfo["filerating"]
            except KeyError as exception:
                badfilethread = threading.Thread(target=DeleteFilesFromBadUpload, args=(imgprocessthread, filename, temp_uuid))
                badfilethread.start()
                upload_flat = ""
                if use_flat_tag == True:
                    upload_flat = "<label for=\"fileflat\">Flat:</label><input type=\"radio\" id=\"fileflatyes\" name=\"fileflat\" value=\"flatyes\"><label for=\"fileflatyes\">Yes</label><input type=\"radio\" id=\"fileflatno\" name=\"fileflat\" value=\"flatno\"><label for=\"fileflatno\">No</label><br>"
                return render_template("upload.html", UPLOAD_STATUS="No file rating was supplied.", FLAT_RADIO=upload_flat)
            if use_flat_tag:
                try:
                    file_flat = uploadinfo["fileflat"]
                except KeyError as exception:
                    badfilethread = threading.Thread(target=DeleteFilesFromBadUpload, args=(imgprocessthread, filename, temp_uuid))
                    badfilethread.start()
                    upload_flat = ""
                    if use_flat_tag == True:
                        upload_flat = "<label for=\"fileflat\">Flat:</label><input type=\"radio\" id=\"fileflatyes\" name=\"fileflat\" value=\"flatyes\"><label for=\"fileflatyes\">Yes</label><input type=\"radio\" id=\"fileflatno\" name=\"fileflat\" value=\"flatno\"><label for=\"fileflatno\">No</label><br>"
                    return render_template("upload.html", UPLOAD_STATUS="The file's Flat rating was not supplied.", FLAT_RADIO=upload_flat)
            else:
                file_flat = None
            file_artistlist = []
            if uploadinfo["artistlist"] != "" and uploadinfo["artistlist"] != None:
                artistlstemp = uploadinfo["artistlist"].split("\r\n")
                artistlstempfmt = []
                for i in artistlstemp:
                    i = i.replace(",", "")
                    i = i.replace(":", "")
                    i = i.replace("\n", "")
                    i = i.replace("\r", "")
                    i = i.strip()
                    artistlstempfmt.append(i)
                for i in artistlstempfmt:
                    artistname = i
                    if artistname == None or artistname == "":
                        continue
                    else:
                        file_artistlist.append(artistname)
            try:
                del artistname, artistlstemp, artistlstempfmt
            except NameError as exception:
                pass
            file_characterlist = []
            if uploadinfo["characterlist"] != "" and uploadinfo["characterlist"] != None:
                characterlstemp = uploadinfo["characterlist"].split("\r\n")
                for i in characterlstemp:
                    brokencharls = i.split(",")
                    brokencharlsfmt = []
                    for j in brokencharls:
                        j = j.replace(":", "")
                        j = j.replace(",", "")
                        j = j.replace("\n", "")
                        j = j.replace("\r", "")
                        j = j.strip()
                        brokencharlsfmt.append(j)
                    charactername = ""
                    try:
                        charactername = brokencharlsfmt[0]
                    except IndexError as exception:
                        continue
                    characterspecies = ""
                    try:
                        characterspecies = brokencharlsfmt[1]
                    except IndexError as exception:
                        pass
                    charactercampaign = ""
                    try:
                        charactercampaign = brokencharlsfmt[2]
                    except IndexError as exception:
                        pass
                    characterowner = ""
                    try:
                        characterowner = brokencharlsfmt[3]
                    except IndexError as exception:
                        pass
                    file_characterlist.append({"Name": charactername,
                    "Species": characterspecies,
                    "Campaign": charactercampaign,
                    "Owner": characterowner})
            try:
                del brokencharls, brokencharlsfmt, characterlstemp
                del charactername, characterspecies, charactercampaign, characterowner 
            except NameError as exception:
                pass
            file_specieslist = []
            if uploadinfo["specieslist"] != "" and uploadinfo["specieslist"] != None:
                specieslstemp = uploadinfo["specieslist"].split("\r\n")
                for i in specieslstemp:
                    brokenspecls = i.split(",")
                    brokenspeclsfmt = []
                    for j in brokenspecls:
                        j = j.replace(":", "")
                        j = j.replace(",", "")
                        j = j.replace("\n", "")
                        j = j.replace("\r", "")
                        j = j.strip()
                        brokenspeclsfmt.append(j)
                    speciesname = ""
                    speciesuniverse = ""
                    try:
                        speciesname = brokenspeclsfmt[0]
                    except IndexError as exception:
                        continue
                    try:
                        speciesuniverse = brokenspeclsfmt[1]
                    except IndexError as exception:
                        pass
                    file_specieslist.append({"Name": speciesname, "Universe": speciesuniverse})
            try:
                del specieslstemp, brokenspecls, brokenspeclsfmt
                del speciesname, speciesuniverse
            except NameError as exception:
                pass
            file_campaignlist = []
            if uploadinfo["campaignlist"] != "" and uploadinfo["campaignlist"] != None:
                campaignlstemp = uploadinfo["campaignlist"].split("\r\n")
                for i in campaignlstemp:
                    brokencmpls = i.split(",")
                    brokencmplsfmt = []
                    for j in brokencmpls:
                        j = j.replace(":", "")
                        j = j.replace(",", "")
                        j = j.replace("\n", "")
                        j = j.replace("\r", "")
                        j = j.strip()
                        brokencmplsfmt.append(j)
                    campaignname = ""
                    try:
                        campaignname = brokencmplsfmt[0]
                    except IndexError as exception:
                        continue
                    campaignuniverse = ""
                    try:
                        campaignuniverse = brokencmplsfmt[1]
                    except IndexError as exception:
                        pass
                    campaignowner = ""
                    try:
                        campaignowner = brokencmplsfmt[2]
                    except IndexError as exception:
                        pass
                    file_campaignlist.append({
                        "Name": campaignname,
                        "Universe": campaignuniverse,
                        "Owner": campaignowner})
            try:
                del campaignlstemp, brokencmpls, brokencmplsfmt
                del campaignname, campaignuniverse, campaignowner
            except NameError as exception:
                pass
            file_universelist = []
            if uploadinfo["universelist"] != "" and uploadinfo["universelist"] != None:
                universelstemp = uploadinfo["universelist"].split("\r\n")
                for i in universelstemp:
                    brokenunils = i.split(",")
                    brokenunilsfmt = []
                    for j in brokenunils:
                        j = j.replace(":", "")
                        j = j.replace(",", "")
                        j = j.replace("\n", "")
                        j = j.replace("\r", "")
                        j = j.strip()
                        brokenunilsfmt.append(j)
                    universename = ""
                    try:
                        universename = brokenunilsfmt[0]
                    except IndexError as exception:
                        continue
                    universeowner = ""
                    try:
                        universeowner = brokenunilsfmt[1]
                    except IndexError as exception:
                        pass
                    file_universelist.append({"Name": universename, "Owner": universeowner})
            try:
                del universelstemp, brokenunils, brokenunilsfmt
                del universename, universeowner
            except NameError as exception:
                pass
            file_tagslist = []
            if uploadinfo["tagslist"] != "" and uploadinfo["tagslist"] != None:
                tagslstemp = uploadinfo["tagslist"].split("\r\n")
                taglstempfmt = []
                for i in tagslstemp:
                    i = i.replace(":", "")
                    i = i.replace(",", "")
                    i = i.replace("\n", "")
                    i = i.replace("\r", "")
                    i = i.strip()
                    taglstempfmt.append(i)
                for i in taglstempfmt:
                    file_tagslist.append(i)
            try:
                del tagslstemp, taglstempfmt
                del i, j
            except NameError as exception:
                pass            
            filenamefull = f"p_full_{filename}"
            filename256 = f"p_256_{filename}"
            filename128 = f"p_128_{filename}"
            filename64 = f"p_64_{filename}"
            paramdict = {
                "Uploader_Auth": session["auth_token"],
                "Uploader_Auth_Time": datetime.now().strftime("%m/%d/%Y, %H:%M:%S"),
                "Uploader_ID": loonboorumysql.FetchUserIDFromAuthToken(session['auth_token']),
                "New_File_ID": temp_uuid,
                "Filename": filename,
                "Full_Filename": filenamefull,
                "256_Filename": filename256,
                "128_Filename": filename128,
                "64_Filename": filename64,
                "Display_Name": file_displayname,
                "Description": file_description,
                "Rating": file_rating,
                "Flat": file_flat,
                "Artist_List": file_artistlist,
                "Character_List": file_characterlist,
                "Species_List": file_specieslist,
                "Campaign_List": file_campaignlist,
                "Universe_List": file_universelist,
                "Tags_List": file_tagslist
            }
            try:
                del filenamefull, filename256, filename128, filename64
            except NameError as exception:
                pass
            rawtofile = json.dumps(paramdict)
            paramfilepath = os.path.join(upload_directory, "..", "params", f"params_{temp_uuid}.json")
            with open(paramfilepath, 'w', encoding="utf-8") as paramfile:
                paramfile.write(rawtofile)
            try:
                del rawtofile, paramdict
            except NameError as exception:
                pass
            databaseprocessthread = threading.Thread(target=ProcessFileIntoDatabase, args=(temp_uuid, imgprocessthread, paramfilepath))
            databaseprocessthread.start()
        upload_flat = ""
        if use_flat_tag == True:
            upload_flat = "<label for=\"fileflat\">Flat:</label><input type=\"radio\" id=\"fileflatyes\" name=\"fileflat\" value=\"flatyes\"><label for=\"fileflatyes\">Yes</label><input type=\"radio\" id=\"fileflatno\" name=\"fileflat\" value=\"flatno\"><label for=\"fileflatno\">No</label><br>"
        return render_template("upload.html", UPLOAD_STATUS="Upload success! The file is now being processed.", FLAT_RADIO=upload_flat)
    elif request.method == 'GET':
        if AuthenticateUserAuth(session) == True: 
            upload_flat = ""
            if use_flat_tag == True:
                upload_flat = "<label for=\"fileflat\">Flat:</label><input type=\"radio\" id=\"fileflatyes\" name=\"fileflat\" value=\"flatyes\"><label for=\"fileflatyes\">Yes</label><input type=\"radio\" id=\"fileflatno\" name=\"fileflat\" value=\"flatno\"><label for=\"fileflatno\">No</label><br>"
            return render_template("upload.html", UPLOAD_STATUS="", FLAT_RADIO=upload_flat)
        return redirect(f"{site_url_name}/login?dest=upload", 302) # TODO: Pass through upload to this URL so that it automatically redirects back to upload after logging in.
    abort(403)

@app.route("/login", methods=['GET'])
def login():

    # LOGIN FAIL REASONS:
    # 0 = Incorrect username/password
    # 1 = No username or password supplied
    # 2 = No username supplied
    # 3 = No password supplied

    arg = request.args.to_dict()
    login_fail_reason = None
    if "login_fail_reason" in session:
        login_fail_reason = session["login_fail_reason"]
        session.pop("login_fail_reason")
    log_out_response = None
    if "log_out_response" in session:
        log_out_response = session["log_out_response"]
        session.pop("log_out_response")
    dest = "browse"
    if "dest" in arg:
        dest = arg["dest"]
    page = "1"
    if "page" in arg:
        page = arg["page"]
    maxfiles = "25"
    if "maxfiles" in arg:
        maxfiles = arg["maxfiles"]
    tags = ""
    if "tags" in arg:
        tags = arg["tags"]
    browsetype = "browse"
    if browsetype in arg:
        browsetype = arg["browsetype"]
    browsepage = "1"
    if browsepage in arg:
        browsepage = arg["browsepage"]
    alreadyloggedin = False
    loginmsg = ""
    if 'auth_token' in session:
        authchk = loonboorumysql.ValidateAuthToken(session['auth_token'])
        if authchk[0] == True:
            username = html.escape(loonboorumysql.FetchUsernameFromAuthToken(session['auth_token']))
            alreadyloggedin = True
            loginmsg = f"You are already logged in as {username}. Would you like to <a href=\"{site_url_name}/logout\">log out</a>?"
    if alreadyloggedin:
        return render_template("login.html", SITE_NAME=site_name, LOGIN_MESSAGE=loginmsg, LOGIN_ERROR="", SITE_URL=site_url_name, DESTINATION=dest, PAGE=page, MAXFILES=maxfiles, SEARCHTAGS=tags)
    else:
        login_message = ""
        if log_out_response != None:
            log_out_response = "Unknown Logout Error. Please contact the system administrator or the project author (LunarEcklipse#7066 on Discord)."
            if log_out_response == 0:
                login_message = "Successfully logged out."
            elif log_out_response == 1:
                login_message = "You are already logged out."
        login_error = ""
        if login_fail_reason != None:
            login_error = "Unknown Login Error. Please contact the system administrator or the project author (LunarEcklipse#7066 on Discord)."
            if login_fail_reason == 0:
                login_error = "Incorrect Username or Password."
            elif login_fail_reason == 1:
                login_error = "No username or password supplied. You must supply a username and password."
            elif login_fail_reason == 2:
                login_error = "No username supplied. You must supply a username."
            elif login_fail_reason == 3:
                login_error = "No password supplied. You must supply a password."
        return render_template("login.html", SITE_NAME=site_name, LOGIN_MESSAGE=login_message, LOGIN_ERROR=login_error, SITE_URL=site_url_name, DESTINATION=dest, PAGE=page, MAXFILES=maxfiles, SEARCHTAGS=tags)

@app.route("/logout", methods=['GET', 'POST'])
def logout_user():

    # LOG OUT RESPONSE CODES:
    # 0 = Success
    # 1 = Not logged in

    arg = request.args.to_dict()
    dest = "browse"
    if "dest" in request.form:
        dest = request.form["dest"]
    page = "1"
    if "page" in request.form:
        page = request.form["page"]
    maxfiles = "25"
    if "maxfiles" in request.form:
        maxfiles = request.form["maxfiles"]
    tags = ""
    if "tags" in request.form:
        tags = request.form["tags"]
    browsetype = "browse"
    if browsetype in request.form:
        browsetype = request.form["browsetype"]
    browsepage = "1"
    if browsepage in request.form:
        browsepage = arg["browsepage"]
    if "auth_token" in session:
        session.pop("auth_token")
        session["log_out_response"] = 0
    else:
        session["log_out_response"] = 1
    return redirect(f"{site_url_name}/login?dest={dest}&page={page}&maxfiles={maxfiles}&tags={tags}", 302)

@app.route("/authenticate", methods=['POST'])
def authenticate_user():
    arg = request.form.to_dict()
    dest = "browse"
    if "dest" in request.form:
        dest = request.form["dest"]
    page = "1"
    if "page" in request.form:
        page = request.form["page"]
    maxfiles = "25"
    if "maxfiles" in request.form:
        maxfiles = request.form["maxfiles"]
    tags = ""
    if "tags" in request.form:
        tags = request.form["tags"]
    browsetype = "browse"
    if browsetype in request.form:
        browsetype = request.form["browsetype"]
    browsepage = "1"
    if browsepage in request.form:
        browsepage = arg["browsepage"]
    formdat = request.form.to_dict()
    if formdat["uname"] == "" and formdat["password"] == "":
        session["login_fail_reason"] = 1
        if "auth_token" in session:
            session.pop("auth_token")
        return redirect(f"{site_url_name}/login?dest={dest}&page={page}&maxfiles={maxfiles}&tags={tags}", 302)
    elif formdat["uname"] == "":
        session["login_fail_reason"] = 2
        if "auth_token" in session:
            session.pop("auth_token")
        return redirect(f"{site_url_name}/login?dest={dest}&page={page}&maxfiles={maxfiles}&tags={tags}", 302)
    elif formdat["password"] == "":
        session["login_fail_reason"] = 3
        if "auth_token" in session:
            session.pop("auth_token")
        return redirect(f"{site_url_name}/login?dest={dest}&page={page}&maxfiles={maxfiles}&tags={tags}", 302)
    username = formdat["uname"]
    pwd = hash_string(formdat["password"])
    del formdat
    isvaliduser = loonboorumysql.CompareUserPass(username, pwd)
    loginerrortxt = ""
    if isvaliduser[0] == False:
        session["login_fail_reason"] = 0
        if "auth_token" in session:
            session.pop("auth_token")
        return redirect(f"{site_url_name}/login?dest={dest}&page={page}&maxfiles={maxfiles}&tags={tags}", 302)
    elif isvaliduser[0] == True:
        session['auth_token'] = isvaliduser[2]
        return redirect(f"{site_url_name}/redirect?dest={dest}&page={page}&maxfiles={maxfiles}&tags={tags}", 302)

@app.route("/admin", methods=['GET'])
def admin_pg():
    authorize_admin = False
    if "auth_token" in session:
        if loonboorumysql.AuthenticateAuthTokenAsAdmin(session["auth_token"]):
            authorize_admin = True
    if authorize_admin == False:
        abort(403)
    currpyver = loonbooru_adminfunc.GetPythonVersion()
    systemcpu = loonbooru_adminfunc.GetMachineProcessor()
    systemcpuusage = loonbooru_adminfunc.GetCPUUsagePercent()
    systemarchitecture = loonbooru_adminfunc.GetMachineArchitecture()
    operatingsys = loonbooru_adminfunc.GetMachineOS()
    processusage = f"{str(loonbooru_adminfunc.GetProcessMemoryUsageMegabytes())} MB"
    databasestats = loonboorumysql.GetDatabaseStats()
    return render_template("admin.html",
    SITE_NAME=site_name,
    SITE_URL=site_url_name,
    SITE_CDN_URL=cdn_url,
    CURRENT_PYTHON_VERSION=currpyver,
    CURRENT_FLASK_VERSION=currentflaskver,
    CURRENT_PIL_VERSION=currentpilver,
    CPU_NAME=systemcpu,
    CPU_BITS=systemarchitecture,
    SYSTEM_OS_DETAILS=operatingsys,
    CPU_USAGE=systemcpuusage,
    LOONBOORU_VERSION=loonbooru_version,
    LOONBOORU_MEMUSG=processusage,
    FLAT_ENABLED=use_flat_tag,
    UPLOAD_DIRECTORY=upload_directory,
    FILE_STORE_PATH=filestorepath,
    CURRENT_USER_LOGIN_COUNT=str(databasestats[9]),
    DATABASE_FILE_COUNT=str(databasestats[3]),
    DATABASE_ARTIST_COUNT=str(databasestats[0]),
    DATABASE_CHARACTER_COUNT=str(databasestats[2]),
    DATABASE_SPECIES_COUNT=str(databasestats[4]),
    DATABASE_CAMPAIGN_COUNT=str(databasestats[1]),
    DATABASE_UNIVERSE_COUNT=str(databasestats[7]),
    DATABASE_TAG_COUNT=str(databasestats[6]),
    DATABASE_SEARCH_LENGTH=str(databasestats[5]))

    # artistcnt, campaigncnt, charactercnt, filecnt, speciescnt, srchcnt, tagcnt, universecnt, usercnt, authusrcnt
