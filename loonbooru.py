from curses import noecho
import os
import sys
from flask import Flask, render_template, request, redirect, url_for, abort, flash, make_response, session, escape
from werkzeug.utils import secure_filename
import imghdr
import uuid
import json
from PIL import Image, ImageChops
import loonboorumysql
import re
import secrets
import hashlib

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
upload_allowed_extensions = {'jpg', 'png', 'gif', 'jpeg'}

app = Flask(__name__, template_folder=templatepath)
app.config['MAX_CONTENT_LENGTH'] = (32 * 1000 * 1000 * 1000) # Uploads limited to 16 mb
app.config['UPLOAD_FOLDER'] = upload_directory
app.secret_key = secrets.token_urlsafe(32)

# THE CODE FOR SPACE IS %20
# THE CODE FOR COMMA IS %2C

class TagType(): # Expand as necessary
    def __init__(self, tag: str):
        self.Tag = tag.lower()
        self.SpecialTagTerm = None 
        self.TagType = "Tag"
        if tag.find(':') != -1:
            if tag.lower().find('artist') != -1:
                self.TagType = "Artist"
                try:
                    self.SpecialTagTerm = tag.lower().split(':')[1]
                except IndexError as exception:
                    self.SpecialTagTerm = None
            elif tag.lower().find('rating') != -1:
                self.TagType = "Rating"
                try:
                    self.SpecialTagTerm = tag.lower().split(':')[1]
                except IndexError as exception:
                    self.SpecialTagTerm = None
            elif tag.lower().find('internal_id') != -1 or tag.lower().find('internalid') != -1:
                self.TagType = "Internal_ID"
                try:
                    self.SpecialTagTerm = tag.lower().split(':')[1]
                except IndexError as exception:
                    self.SpecialTagTerm = None
            elif tag.lower().find('file_ext') != -1 or tag.lower().find('fileext') != -1 or tag.lower().find('filext') != -1:
                self.TagType = "File_EXT"
                try:
                    self.SpecialTagTerm = tag.lower().split(':')[1]
                except IndexError as Exception:
                    self.SpecialTagTerm = None
            elif tag.lower().find('display_name') != -1 or tag.lower().find('displayname') != -1:
                self.TagType = "Display_Name"
                try:
                    self.SpecialTagTerm = tag.lower().split(':')[1]
                except IndexError as exception:
                    self.SpecialTagTerm = None
        return

def GenerateBrowseThumbnail(filename: str, browsepage: int, maxfiles: int) -> str: #TODO: UPDATE TO SUPPORT 64px and 256px thumbnails!
    file = (os.path.splitext(filename))
    file_ext = file[1]
    if file[1] == ".gif":
        file_ext = ".png"
    ### RETURN BELOW FOR DEEZ NUTS ###
    # return f"<div class=\"imgholder\" onclick=\"location.href='{site_url_name}/view/{file[0]}?browsepage={str(browsepage)}&maxfiles={str(maxfiles)}';\" style=\"overflow:hidden; cursor:pointer; min-width:128px; min-height:128px; width:20%; height:20%; max-width: 128px; max-height: 128px; border-style: solid; border-color: #c7ae40; overflow: hidden; border-radius:10px; display:inline-block; align-items: center;\"><div style=\"width: 100%; height: 100%; display:flex; justify-content: center; align-items: center;\"><img style = \"height: 128px; display:block; margin:auto; vertical-align:middle;\" src=\"https://cdn.dev.lunarecklipse.ca/dz.png\"></div></div>\n"
    return f"<div class=\"imgholder\" onclick=\"location.href='{site_url_name}/view/{file[0]}?browsepage={str(browsepage)}&maxfiles={str(maxfiles)}';\"><div class=\"imgholderinner\"><img class=\"tileimg\" src=\"{cdn_url}/thumb/128/{file[0]}{file_ext}\"></div></div>\n"

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
        if re.search(r"kiryu cha+n", re.escape(i)) != None:
            i = "jess"
        if i != "":
            tagls.append(TagType(i))
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
    if dest == "taglist":
        return redirect(f"{site_url_name}/taglist")
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
    browselisttpl = loonboorumysql.GetFileList(maxfiles, int(page), tags)
    browselist = browselisttpl[0]
    nextpgexists = browselisttpl[1]
    startbreak = 0
    linebreak = 5
    imginsert = ""
    for i in browselist:
        try:
            filepath = filestorepathfull + "/" + str(i.FileID) + "." + i.FileEXT
            with Image.open(filepath) as f:
                imginsert += GenerateBrowseThumbnail(i.Filename, page, maxfiles)
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

@app.route("/view/<page>") #TODO: FINISH ME
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
    tags = ""
    if "tags" in arg:
        tags = arg["tags"]
    if ValidateAge(session) == False:
        return redirect(f"{site_url_name}/agecheck?dest=view&page={str(page)}&browsetype={browsetype}&browsepage={browsepage}&maxfiles={maxfiles}&tags={tags}")
    try:
        page = str(page)
    except ValueError as exception:
        abort(404)
    file = loonboorumysql.FetchFileDetail(page) # TODO: Filedetail now passes through species, but it needs to be implemented here as well.
    if file == None:
        abort(404)
    tagprint = ""
    if file.Tags != None:
        file.Tags.sort(key=lambda lm: lm.TagName)
        for i in file.Tags:
            tagprint += i.TagName + ", "
    if tagprint == "":
        tagprint = "No tags found."
    else:
        tagprint = tagprint[:-1]
        tagprint = tagprint[:-1]
    artistprnt = "Unknown"
    if file.Artists != None and len(file.Artists) != 0:
        file.Artists.sort(key=lambda lm: lm.ArtistName)
        artistprnt = ""
        for i in file.Artists:
            artistprnt += i.ArtistNameProper + ", "
        artistprnt = artistprnt[:-1]
        artistprnt = artistprnt[:-1]
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
                charprnt += i.CharacterNameProper
                if i.CharacterOwner != None and len(i.CharacterOwner) != 0:
                    charprnt += " ("
                    for j in i.CharacterOwner:
                        charprnt += f"{j.UsernameProper}, "
                    charprnt = charprnt[:-1]
                    charprnt = charprnt[:-1]
                    charprnt += "), "
            charprnt = charprnt[:-1]
            charprnt = charprnt[:-1]
            del templs
            charprnt += "</p>"
    specprnt = ""
    if file.Species != None and len(file.Species) != 0:
        specprnt = "<p class=\"abouttxt\">Species: "
        file.Species.sort(key=lambda lm: lm.SpeciesName)
        for i in file.Species:
            specprnt += i.SpeciesNameProper + ", "
            # if i.SpeciesUniverse != None and len(i.SpeciesUniverse) != 0: # Leaving this code in because I wrote it, but otherwise I'm commenting it out after feedback.
            #     specprnt += " ("
            #     for j in i.SpeciesUniverse:
            #         specprnt += f"{j.UniverseNameProper}, "
            #     specprnt = specprnt[:-1]
            #     specprnt = specprnt[:-1]
            #     specprnt += "), "
        specprnt = specprnt[:-1]
        specprnt = specprnt[:-1]
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
            campprnt += i.CampaignNameProper
            if i.CampaignOwner != None and len(i.CampaignOwner) != 0:
                campprnt += " ("
                for j in i.CampaignOwner:
                    campprnt += f"{j.UsernameProper}, "
                campprnt = campprnt[:-1]
                campprnt = campprnt[:-1]
                campprnt += ")"
            campprnt += ", "
        campprnt = campprnt[:-1]
        campprnt = campprnt[:-1]
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
            uniprnt += i.UniverseNameProper
            if i.UniverseOwner != None and len(i.UniverseOwner) != 0:
                uniprnt += " ("
                for j in i.UniverseOwner:
                    uniprnt += f"{j.UsernameProper}, "
                uniprnt = uniprnt[:-1]
                uniprnt = uniprnt[:-1]
                uniprnt += ")"
            uniprnt += ", "
        uniprnt = uniprnt[:-1]
        uniprnt = uniprnt[:-1]
        uniprnt += "</p>"

    return render_template("view.html", SITE_NAME=site_name, DESCRIPTION=file.Description, DISPLAY_NAME=file.DisplayName, FILE_PATH=f"{cdn_url}/full/{file.FileID}.{file.FileEXT}", ARTIST_NAME=artistprnt, FILE_RATING=file.FileRating, UPLOAD_DATE=file.UploadDatetime, TAG_LIST=tagprint, CHAR_LIST=charprnt, SPEC_LIST=specprnt, CAMPAIGN_LIST=campprnt, UNIVERSE_LIST=uniprnt)

@app.route("/results/")
def ResultsNoQuery():
    arg = request.args.to_dict()
    maxfiles = "25"
    if "maxfiles" in arg:
        maxfiles = arg["maxfiles"]
    tags = ""
    if "tags" in arg:
        tags = arg["tags"]
    return redirect(f"{site_url_name}/browse/1?maxfiles={str(maxfiles)}&tags={tags}")

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
    return render_template("search.html", SITE_NAME=site_name)
    
def hash_string(inStr): # Creates a string hash for use
    hash_obj = hashlib.sha256(inStr.encode('utf-8'))
    hex_dig = hash_obj.hexdigest()
    return hex_dig

def validate_filename(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in upload_allowed_extensions

@app.route("/upload", methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        if 'file' not in request.files:
            return redirect(request.url)
        file = request.files['file']
        filename = f"temp_{str(uuid.uuid4().hex)}_{secure_filename(file.filename)}"
        if file.filename == '':
            flash("No file was selected.")
            return redirect(request.url)
        if validate_filename(file.filename) == False:
            flash("The provided filetype is not allowed at the moment.")
            return redirect(request.url)
        if file and validate_filename(file.filename):
            file.save(os.path.join(upload_directory, filename))
            print("File saved successfully")
        return redirect(request.url)
    elif request.method == 'GET':
        return render_template("upload.html")

# LOGIN FAIL REASONS:
# 0 = Incorrect username/password
# 1 = No username or password supplied
# 2 = No username supplied
# 3 = No password supplied

@app.route("/login", methods=['GET'])
def login():
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
    alreadyloggedin = False
    loginmsg = ""
    if 'auth_token' in session:
        authchk = loonboorumysql.ValidateAuthToken(session['auth_token'])
        if authchk[0] == True:
            username = loonboorumysql.FetchUsernameFromAuthToken(session['auth_token'])
            alreadyloggedin = True
            loginmsg = f"You are already logged in as {username}. Would you like to <a href=\"{site_url_name}/logout\">log out</a>?"
    if alreadyloggedin:
        return render_template("login.html", SITE_NAME=site_name, LOGIN_MESSAGE=loginmsg, LOGIN_ERROR="")
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
        return render_template("login.html", SITE_NAME=site_name, LOGIN_MESSAGE=login_message, LOGIN_ERROR=login_error)

# LOG OUT RESPONSE CODES:
# 0 = Success
# 1 = Not logged in

@app.route("/logout", methods=['GET', 'POST'])
def logout_user():
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