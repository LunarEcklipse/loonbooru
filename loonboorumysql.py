import mysql.connector
import os
from enum import Enum
from datetime import datetime, timedelta
from collections import Counter
import booruobj
import hashlib
import uuid
import json

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

dburl = flags["dburl"]
dbusr = flags["dbusr"]
dbpwd = flags["dbpwd"]
dbname = flags["dbname"]

class FileRating(Enum):
    Unknown = 0
    Safe = 1
    Questionable = 2
    Flat = 3
    Explicit = 4

class TaggedFile:
    def __init__(self, internal_id: int, file_ext: str, display_name: str, rating: str, artist: str, flat: int, upload: str, tags: list):
        self.InternalID = internal_id
        self.FileExtension = file_ext
        self.DisplayName = display_name
        if rating == "s":
            self.Rating = FileRating.Safe
        elif rating == "q":
            self.Rating = FileRating.Questionable
        elif rating == "f":
            self.Rating = FileRating.Flat
        elif rating == "e":
            self.Rating = FileRating.Explicit
        else:
            self.Rating = FileRating.Unknown
        self.Artist = artist
        if flat == 0:
            self.Flat = False
        else:
            self.Flat = True
        self.UploadDate = upload
        self.Tags = tags
        return
    
    def FileRatingStr(self):
        if self.Rating == FileRating.Safe:
            return "safe"
        elif self.Rating == FileRating.Questionable:
            return "questionable"
        elif self.Rating == FileRating.Flat:
            return "flat"
        elif self.Rating == FileRating.Explicit:
            return "explicit"
        else:
            return "unknown"

    def filename(self):
        return str(self.InternalID) + "." + self.FileExtension

def ConnectToDB() -> mysql.connector:
    dbase = mysql.connector.connect(host=dburl, user=dbusr, password=dbpwd, database=dbname)
    return dbase

def GetFileList(numPerPage: int, pageNum: int, tags=None) -> tuple: #TODO: Finish me!
    fileOffset = (numPerPage * pageNum) - numPerPage
    dbase = ConnectToDB()
    dbcs = dbase.cursor(prepared=True)
    if tags == None or tags == []:
        dbcs.execute("SELECT `File_ID`, `File_EXT`, `Upload_Datetime`, `Rating`, `Display_Browse`, `Display_Search` FROM `Files_Base` WHERE 1 ORDER BY `Upload_Datetime` DESC, `File_ID` DESC LIMIT %s, %s;", (fileOffset, numPerPage))
        filelist = dbcs.fetchall() # TODO: You need to continue from around here! Make sure you put your classes into booruobj.py!
        # TODO: Also note! You only need the file_id, file_ext, display name, and upload datetime to make your object appear on the list! Maybe separate this into a new function and make an object called BrowseFileDisplay()
        if filelist == None: 
            return None
        taggedfilelist = []
        for i in filelist:
            taggedfilelist.append(booruobj.FileBasic(i[0], i[1], i[2], i[3], i[4], i[5]))
        dbcs.close()
        dbase.close()
        statement = "SELECT * FROM `Files_Base` WHERE `Display_Browse` = 1 ORDER BY `Upload_Datetime` DESC, `File_ID` DESC LIMIT %s, %s;"
        exectuple = (fileOffset, numPerPage)
        nextpageexists = TestNextPageContentExists(statement, exectuple)
        return (taggedfilelist, nextpageexists)
    else: # TODO: FIX THIS PART
        taginsert = ""
        inc = 0
        for i in tags:
            if inc != 0:
                taginsert += " OR "
            taginsert += "`Search_Term` = %s"
            inc += 1
        tuplelist = []
        for i in tags:
            tuplelist.append(i.Tag)
        tuplelist.append(len(tags))
        tuplelist.append(fileOffset)
        tuplelist.append(numPerPage)
        exectuple = tuple(tuplelist)
        statement = f"SELECT Files_Base.File_ID, Files_Base.File_EXT, Files_Base.Upload_Datetime, Files_Base.Rating, COUNT(*) as tag_count FROM `File_Search_Master` INNER JOIN `Files_Base` ON File_Search_Master.File_ID = Files_Base.File_ID WHERE ({taginsert}) AND Files_Base.Display_Search = 1 GROUP BY Files_Base.File_ID HAVING tag_count >= %s ORDER BY Files_Base.Upload_Datetime DESC, Files_Base.File_ID DESC LIMIT %s, %s;"
        dbcs.execute(statement, exectuple)
        filelist = dbcs.fetchall()
        if filelist == None:
            return None
        taggedfilelist = []
        for i in filelist:
            taggedfilelist.append(booruobj.FileBasic(i[0], i[1], i[2], i[3], 1, 1))
        dbcs.close()
        dbase.close()
        nextpageexists = TestNextPageContentExists(statement, exectuple)
        return (taggedfilelist, nextpageexists)
        
def TestNextPageContentExists(statement: str, exectuple: tuple) -> bool:
    newtuplels = list(exectuple)
    newtuplels[-2] += newtuplels[-1]
    newtuplels[-1] = 1
    newtuple = tuple(newtuplels)
    dbase = ConnectToDB()
    dbcs = dbase.cursor(prepared=True)
    dbcs.execute(statement, newtuple)
    cnt = dbcs.rowcount
    trash = dbcs.fetchall()
    del trash
    dbcs.close()
    dbase.close()
    if cnt >= 0:
        return True
    return False

def FetchFileDetail(id_num: str) -> booruobj.FileDetail: # TODO: ADD TAGS TO ME!
    dbase = ConnectToDB()
    dbcs = dbase.cursor(prepared=True)
    dbcs.execute("SELECT * FROM `Files_Base` WHERE `File_ID` = %s LIMIT 1;", (id_num,))
    if dbcs.rowcount == -1:
        return None
    outtpl = dbcs.fetchone()
    File_ID = outtpl[0] # TODO: Nonetype object is not subscriptable
    User_ID = outtpl[1] # TODO: ADD UPLOADER ID!
    File_EXT = outtpl[2]
    Display_Name = outtpl[3] 
    Desc = outtpl[4]
    Rating = outtpl[5]
    UploadDT = outtpl[6]
    DisplayBrowse = outtpl[7]
    DisplaySearch = outtpl[8]
    del outtpl
    dbcs.execute("SELECT * FROM `Files_Artist` INNER JOIN `Artist_Base` ON Files_Artist.Artist_ID = Artist_Base.Artist_ID WHERE Files_Artist.File_ID = %s;", (File_ID,))
    artistout = dbcs.fetchall()
    artistlist = []
    for i in artistout:
        artistlist.append(booruobj.Artist(i[0], i[3], i[4], i[5]))
    del artistout
    dbcs.execute("SELECT * FROM `Files_Characters` INNER JOIN `Character_Base` ON Files_Characters.Character_ID = Character_Base.Character_ID INNER JOIN `Species_Base` ON Files_Characters.Species_ID = Species_Base.Species_ID WHERE Files_Characters.File_ID = %s;", (File_ID,))
    outchr = dbcs.fetchall()
    print(outchr)
    charls = []
    if len(outchr) != 0:
        charidls = []
        for i in outchr:
            iddupe = False
            for j in charidls:
                if j == i[1]:
                    iddupe = True
                    break
            if iddupe:
                for j in charls:
                    if j.CharacterID == i[1]:
                        specdupe = False
                        newspec = booruobj.Species(i[6], i[7], i[8], None)
                        for k in j.CharacterSpecies:
                            if k == newspec:
                                specdupe = True
                                break
                        if specdupe == False:
                            j.CharacterSpecies.append(booruobj.Species(i[6], i[7], i[8], None))
                        break
                continue
            charidls.append(i[1])
            Char_ID = i[1]
            Char_Name = i[4]
            Char_Name_Proper = i[5]
            speciesls = []
            speciesls.append(booruobj.Species(i[6], i[7], i[8], None))
            dbcs.execute("SELECT * FROM `Character_Owner` WHERE `Character_ID` = %s;", (Char_ID,))
            ownerls = []
            outownr = dbcs.fetchall()
            if len(outownr) != 0:
                for j in outownr:
                    CharOwner_ID = j[1]
                    dbcs.execute("SELECT * FROM `User_Base` WHERE `User_ID` = %s LIMIT 1;", (CharOwner_ID,))
                    charowner = dbcs.fetchone()
                    OwnerUsrNam = charowner[1]
                    OwnerUsrNameProp = charowner[2]
                    OwnerUsrJoin = charowner[3]
                    ownerls.append(booruobj.User(CharOwner_ID, OwnerUsrNam, OwnerUsrNameProp, OwnerUsrJoin))
            charls.append(booruobj.Character(Char_ID, Char_Name, Char_Name_Proper, speciesls, None, ownerls))
    del outchr
    filespeciesls = []
    dbcs.execute("SELECT * FROM `Files_Species` INNER JOIN `Species_Base` ON Files_Species.Species_ID = Species_Base.Species_ID WHERE Files_Species.File_ID = %s;", (File_ID,))
    outspecls = dbcs.fetchall()
    for i in outspecls:
        dbcs.execute("SELECT * FROM `Species_Universe` INNER JOIN `Universe_Base` ON Species_Universe.Universe_ID = Universe_Base.Universe_ID WHERE Species_Universe.Species_ID = %s;", (i[1],))
        outspecunivrls = dbcs.fetchall()
        specunils = []
        for j in outspecunivrls:
            specunils.append(booruobj.Universe(j[1], j[3], j[4], None))
        filespeciesls.append(booruobj.Species(i[1], i[3], i[4], specunils))
    dbcs.execute("SELECT * FROM `Files_Campaign` INNER JOIN `Campaign_Base` ON Files_Campaign.Campaign_ID = Campaign_Base.Campaign_ID WHERE Files_Campaign.File_ID = %s;", (File_ID,))
    campout = dbcs.fetchall()
    campls = []
    unils = []
    if len(campout) != 0:
        for i in campout:
            CampID = i[1]
            CampNm = i[3]
            CampNmProp = i[4]
            dbcs.execute("SELECT * FROM `Campaign_Owner` INNER JOIN `User_Base` ON Campaign_Owner.User_ID = User_Base.User_ID WHERE Campaign_Owner.Campaign_ID = %s;", (CampID,))
            campownrout = dbcs.fetchall()
            campownrls = []
            for j in campownrout:
                campownrls.append(booruobj.User(j[1], j[3], j[4], j[5]))
            campls.append(booruobj.Campaign(CampID, CampNm, CampNmProp, campownrls))
    dbcs.execute("SELECT * FROM `Files_Universe` INNER JOIN `Universe_Base` ON Files_Universe.Universe_ID = Universe_Base.Universe_ID WHERE Files_Universe.File_ID = %s;", (File_ID,))
    uniout = dbcs.fetchall()
    if len(uniout) != 0:
        for i in uniout:
            dbcs.execute("SELECT * FROM `Universe_Owner` INNER JOIN `User_Base` ON Universe_Owner.User_ID = User_Base.User_ID WHERE Universe_Owner.Universe_ID = %s;", (i[1],))
            outuniownr = dbcs.fetchall()
            uniownr = []
            for j in outuniownr:
                uniownr.append(booruobj.User(j[1], j[3], j[4], j[5]))
            unils.append(booruobj.Universe(i[1], i[3], i[4], uniownr))
    tagsls = []
    dbcs.execute("SELECT * FROM `Files_Tags` INNER JOIN `Tag_Base` ON Files_Tags.Tag_ID = Tag_Base.Tag_ID WHERE Files_Tags.File_ID = %s;", (File_ID,))
    tagout = dbcs.fetchall()
    if len(tagout) != 0:
        for i in tagout:
            tagsls.append(booruobj.TagBasic(i[1], i[3], i[4]))
    dbcs.close()
    dbase.close()
    return booruobj.FileDetail(File_ID, File_EXT, UploadDT, Rating, DisplayBrowse, DisplaySearch, Display_Name, Desc, artistlist, charls, filespeciesls, campls, unils, tagsls) #TODO: Replace none with tags!

def CompareUserPass(username, pwdhash):
    dbase = ConnectToDB()
    dbcs = dbase.cursor(prepared=True)
    dbcs.execute("SELECT `User_ID` FROM `User_Base` WHERE `Username` = %s LIMIT 1;", (username.lower(),))
    out = dbcs.fetchone()
    if out == None:
        dbcs.close()
        dbase.close()
        return (False, "NOT_FOUND", None)
    uid = out[0]
    dbcs.execute("SELECT `User_ID` FROM `User_PC` WHERE `User_ID` = %s AND `Hash` = %s LIMIT 1;", (uid, pwdhash))
    out = dbcs.fetchone()
    if out == None:
        dbcs.close()
        dbase.close()
        return (False, "WRONG_PASS", None)
    del out
    dbcs.close()
    dbase.close()
    auth = GrantAuthToken(uid)
    return (True, "OK", auth[0])

def GrantAuthToken(userid):
    auth_token = str(uuid.uuid4().hex)
    exp_time = datetime.now() + timedelta(hours=24)
    dbase = ConnectToDB()
    dbcs = dbase.cursor(prepared=True)
    dbcs.execute("SELECT * FROM `User_Auth` WHERE `User_ID` = %s LIMIT 1;", (userid,))
    out = dbcs.fetchone()
    if out == None:
        dbcs.execute("INSERT INTO `User_Auth`(`User_ID`, `Auth_Token`, `Expiration`) VALUES (%s, %s, %s);", (userid, auth_token, exp_time))
    else:
        dbcs.execute("UPDATE `User_Auth` SET `Auth_Token`= %s,`Expiration`= %s WHERE `User_ID` = %s;", (auth_token, exp_time, userid))
    dbase.commit()
    dbcs.close()
    dbase.close()
    return (auth_token, exp_time)

def ValidateAuthToken(auth_token):
    dbase = ConnectToDB()
    dbcs = dbase.cursor(prepared=True)
    dbcs.execute("SELECT * FROM `User_Auth` WHERE `Auth_Token` = %s LIMIT 1;", (auth_token,))
    out = dbcs.fetchone()
    if out == None:
        return (False, None, None)
    if out[2] < datetime.now():
        return (False, None, None)
    return (True, out[0], out[2])

def FetchUsernameFromAuthToken(auth_token):
    dbase = ConnectToDB()
    dbcs = dbase.cursor(prepared=True)
    dbcs.execute("SELECT `User_ID` From `User_Auth` WHERE `Auth_Token` = %s LIMIT 1;", (auth_token,))
    out = dbcs.fetchone()
    if out == None:
        return None
    dbcs.execute("SELECT `Username` FROM `User_Base` WHERE `User_ID` = %s LIMIT 1;", (out[0],))
    out = dbcs.fetchone()
    dbcs.close()
    dbase.close()
    if out == None:
        return None
    return out[0]