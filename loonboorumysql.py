import mysql.connector
import os
from enum import Enum
from datetime import datetime, timedelta
from collections import Counter

from numpy import str_
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
useflat = flags["useflat"]

class UseFlatException(Exception):
    def __init__(self):
        self.message = "Flat data was passed in but the database does not support flat."
        super().__init__(self.message)
        return

class InsufficientInsertionData(Exception):
    def __init__(self):
        self.message = "There was not sufficient data for file insertion."
        super().__init__(self.message)
        return

class DatabaseConnectionFailure(Exception):
    def __init__(self):
        self.message = "A database connection could not be established."
        super().__init__(self.message)
        return

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
    if outtpl == None:
        return None
    File_ID = outtpl[0]
    User_ID = outtpl[1]
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

def FetchUserIDFromAuthToken(auth_token):
    dbase = ConnectToDB()
    dbcs = dbase.cursor(prepared=True)
    dbcs.execute("SELECT `User_ID` FROM `User_Auth` WHERE `Auth_Token` = %s LIMIT 1;", (auth_token,))
    out = dbcs.fetchone()
    dbcs.close()
    dbase.close()
    if out == None:
        return None
    return out[0]

def CheckIfFileUUIDExists(uuid: str) -> bool:
    dbase = ConnectToDB()
    dbcs = dbase.cursor(prepared=True)
    dbcs.execute("SELECT `File_ID` FROM `Files_Base` WHERE `File_ID` = %s LIMIT 1;", (uuid,))
    out = dbcs.fetchone()
    dbcs.close()
    dbase.close()
    if out == None:
        return False
    return True

def AddFileIDToProcessingQueue(file_uuid: str):
    if file_uuid == None or file_uuid == "" or file_uuid.isspace() == True:
        return
    dbase = ConnectToDB()
    dbcs = dbase.cursor(prepared=True)
    if CheckFileIDInProcessingQueue(file_uuid):
        dbcs.execute("INSERT INTO `Files_ProcessingQueue`(`File_ID`) VALUES (%s);", (file_uuid,))
        dbase.commit()
    dbcs.close()
    dbase.close()
    return

def RemoveFileIDFromProcessingQueue(file_uuid: str):
    if file_uuid == None or file_uuid == "" or file_uuid.isspace() == True:
        return
    dbase = ConnectToDB()
    dbcs = dbase.cursor(prepared=True)
    dbcs.execute("DELETE FROM `File_ProcessingQueue` WHERE `File_ID` = %s;", (file_uuid,))
    dbcs.commit()
    dbcs.close()
    dbase.close()
    return

def CheckFileIDInProcessingQueue(file_uuid: str) -> bool:
    dbase = ConnectToDB()
    dbcs = dbase.cursor(prepared=True)
    dbcs.execute("SELECT `File_ID` FROM `File_ProcessingQueue` WHERE `File_ID` = %s LIMIT 1;")
    out = dbcs.fetchone()
    dbcs.close()
    dbase.close()
    if out != None:
        return True
    return False

def InsertNewFileIntoDatabase(file_uuid: str, user_id: str, file_ext: str, display_name: str, description: str, rating: str, flat: bool=None, artistlist: list=[], characterlist: list=[], specieslist: list=[], campaignlist:list=[], universelist: list=[], tagslist: list=[]):
    file_uuid = file_uuid.strip()
    user_id = user_id.strip()
    file_ext = file_ext.strip()
    display_name = display_name.strip()
    description = description.strip()
    rating = rating.strip()
    searchinsertlist = []
    if flat == None and useflat == True:
        flat = False
    if file_uuid == None:
        raise InsufficientInsertionData
    dbase = ConnectToDB()
    dbcs = dbase.cursor(prepared=True)
    if rating == "safe" or rating == "s":
        rating = "s"
    elif rating == "questionable" or rating == "q":
        rating = "q"
    elif rating == "explicit" or rating == "e":
        rating = "e"
    elif rating == "flat" or rating == "f":
        if useflat == False:
            raise UseFlatException
        rating = "f"
    else:
        rating = "e" # Play safe here and tag it as explicit. Can be adjusted later.
    searchinsertlist.append(f"file_id:{file_uuid}")
    searchinsertlist.append(f"fileid:{file_uuid}")
    searchinsertlist.append(f"uploader_id:{user_id}")
    searchinsertlist.append(f"uploaderid:{user_id}")
    dbcs.execute("SELECT `Username` FROM `User_Base` WHERE `User_ID` = %s LIMIT 1;", (user_id,))
    uploadername = dbcs.fetchone()
    uploadername = uploadername[0].strip()
    searchinsertlist.append(f"uploader:{uploadername}")
    searchinsertlist.append(f"uploader_name:{uploadername}")
    searchinsertlist.append(f"uploadername:{uploadername}")
    searchinsertlist.append(f"uploader_username:{uploadername}")
    searchinsertlist.append(f"uploaderusername:{uploadername}")
    searchinsertlist.append(f"file_extension:{file_ext}")
    searchinsertlist.append(f"fileextension:{file_ext}")
    searchinsertlist.append(f"fileext:{file_ext}")
    searchinsertlist.append(f"ext:{file_ext}")
    searchinsertlist.append(f"extension:{file_ext}")
    searchinsertlist.append(f"filename:{display_name}")
    searchinsertlist.append(f"file_name:{display_name}")
    searchinsertlist.append(f"name:{display_name}")
    searchinsertlist.append(f"display_name:{display_name}")
    searchinsertlist.append(f"displayname:{display_name}")
    searchinsertlist.append(f"rating:{rating}")
    searchinsertlist.append(f"filerating:{rating}")
    searchinsertlist.append(f"file_rating:{rating}")
    if rating == "s":
        searchinsertlist.append(f"sfw:true")
        searchinsertlist.append(f"issfw:true")
        searchinsertlist.append(f"is_sfw:true")
        searchinsertlist.append(f"nsfw:false")
        searchinsertlist.append(f"isnsfw:false")
        searchinsertlist.append(f"is_nsfw:false")
        searchinsertlist.append(f"sfw:yes")
        searchinsertlist.append(f"issfw:yes")
        searchinsertlist.append(f"is_sfw:yes")
        searchinsertlist.append(f"nsfw:no")
        searchinsertlist.append(f"isnsfw:no")
        searchinsertlist.append(f"is_nsfw:no")
    else:
        searchinsertlist.append(f"sfw:false")
        searchinsertlist.append(f"issfw:false")
        searchinsertlist.append(f"is_sfw:false")
        searchinsertlist.append(f"nsfw:true")
        searchinsertlist.append(f"isnsfw:true")
        searchinsertlist.append(f"is_nsfw:true")
        searchinsertlist.append(f"sfw:no")
        searchinsertlist.append(f"issfw:no")
        searchinsertlist.append(f"is_sfw:no")
        searchinsertlist.append(f"nsfw:yes")
        searchinsertlist.append(f"isnsfw:yes")
        searchinsertlist.append(f"is_nsfw:yes")
        
    dbcs.execute("INSERT INTO `Files_Base`(`File_ID`, `User_ID`, `File_EXT`, `Display_Name`, `Description`, `Rating`, `Upload_Datetime`, `Display_Browse`, `Display_Search`) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s);", (file_uuid, user_id, file_ext, display_name, description, rating, datetime.now(), 1, 1))
    dbase.commit()
    if flat != None:
        flatinsert = None
        if flat == True:
            searchinsertlist.append(f"flat:true")
            searchinsertlist.append(f"flat:yes")
            searchinsertlist.append(f"is_flat:true")
            searchinsertlist.append(f"is_flat:yes")
            searchinsertlist.append(f"isflat:true")
            searchinsertlist.append(f"isflat:yes")
            dbcs.execute("INSERT INTO `Files_Flat`(`File_ID`) VALUES (%s);", (file_uuid))
        else:
            searchinsertlist.append(f"flat:false")
            searchinsertlist.append(f"flat:no")
            searchinsertlist.append(f"is_flat:false")
            searchinsertlist.append(f"is_flat:no")
            searchinsertlist.append(f"isflat:false")
            searchinsertlist.append(f"isflat:no")
        dbase.commit()
    for i in artistlist:
        if i == None or i == "" or i.isspace() == True:
            continue
        i = i.strip()
        dbcs.execute("SELECT `Artist_ID` FROM `Artist_Base` WHERE `Artist_Name` = %s LIMIT 1;", (i.lower(),))
        out = dbcs.fetchone()
        artist_uuid = None
        if out == None:
            new_artist_uuid = str(uuid.uuid4().hex)
            dbcs.execute("SELECT `Artist_ID` FROM `Artist_Base` WHERE `Artist_ID` = %s LIMIT 1;", (new_artist_uuid,))
            out = dbcs.fetchone()
            if out != None:
                found_new_uuid = False
                while found_new_uuid == False:
                    new_artist_uuid = str(uuid.uuid4().hex)
                    dbcs.execute("SELECT `Artist_ID` FROM `Artist_Base` WHERE `Artist_ID` = %s LIMIT 1;", (new_artist_uuid,))
                    out = dbcs.fetchone()
                    if out == None:
                        found_new_uuid = True
                    else:
                        found_new_uuid = False
            artist_uuid = new_artist_uuid
            dbcs.execute("INSERT INTO `Artist_Base`(`Artist_ID`, `User_ID`, `Artist_Name`, `Artist_Name_Proper`) VALUES (%s, %s, %s, %s);", (new_artist_uuid, None, i.lower(), i))
            dbase.commit()
        else:
            artist_uuid = out[0]
        dbcs.execute("SELECT * FROM `Files_Artist` WHERE `File_ID` = %s AND `Artist_ID` = %s LIMIT 1;", (file_uuid, artist_uuid))
        out = dbcs.fetchone()
        if out == None:
            dbcs.execute("INSERT INTO `Files_Artist`(`File_ID`, `Artist_ID`) VALUES (%s, %s);", (file_uuid, artist_uuid))
        dbase.commit()
        searchinsertlist.append(f"artist_id:{artist_uuid}")
        searchinsertlist.append(f"artistid:{artist_uuid}")
        searchinsertlist.append(f"artist:{i.lower()}")
        searchinsertlist.append(f"artistname:{i.lower()}")
        searchinsertlist.append(f"artist_name:{i.lower()}")
    for i in characterlist:
        charactername = i["Name"].strip()
        characterspecies = i["Species"].strip()
        charactercampaign = i["Campaign"].strip()
        characterowner = i["Owner"].strip()
        if charactername == None or charactername == "" or charactername.isspace() == True:
            continue
        if characterowner != None and characterowner != "" and characterowner.isspace() == False:
            dbcs.execute("SELECT Character_Base.Character_ID FROM `Character_Base` INNER JOIN `Character_Owner` ON Character_Base.Character_ID = Character_Owner.Character_ID WHERE Character_Base.Character_Name = %s AND Character_Owner.Username = %s LIMIT 1;", (charactername.lower(), characterowner.lower()))
        else:
            dbcs.execute("SELECT Character_ID` FROM `Character_Base` WHERE `Character_Name` = %sLIMIT 1;", (charactername.lower(),))
        out = dbcs.fetchone()
        character_uuid = None
        if out == None:
            new_character_id = str(uuid.uuid4().hex)
            dbcs.execute("SELECT `Character_ID` FROM `Character_Base` WHERE `Character_ID` = %s LIMIT 1;", (new_character_id,))
            out = dbcs.fetchone()
            if out != None:
                found_new_uuid = False
                while found_new_uuid == False:
                    new_character_id = str(uuid.uuid4().hex)
                    dbcs.execute("SELECT `Character_ID` FROM `Character_Base` WHERE `Character_ID` = %s LIMIT 1;", (new_character_id,))
                    out = dbcs.fetchone()
                    if out == None:
                        found_new_uuid = True
                    else:
                        found_new_uuid = False
            character_uuid = new_character_id
            dbcs.execute("INSERT INTO `Character_Base`(`Character_ID`, `Character_Name`, `Character_Name_Proper`) VALUES (%s, %s, %s);", (new_character_id, charactername.lower(), charactername))
            dbase.commit()
        else:
            character_uuid = out[0]
        owner_uuid = None
        if characterowner != None and characterowner != "" and characterowner.isspace() == False:
            dbcs.execute("SELECT `User_ID` FROM `User_Base` WHERE `Username` = %s LIMIT 1;", (characterowner.lower(),))
            out = dbcs.fetchone()
            if out == None:
                new_user_id = str(uuid.uuid4().hex)
                dbcs.execute("SELECT `User_ID` FROM `User_Base` WHERE `User_ID` = %s LIMIT 1;", (new_user_id,))
                out = dbcs.fetchone()
                if out != None:
                    found_new_uuid = False
                    while found_new_uuid == False:
                        new_user_id = str(uuid.uuid4().hex)
                        dbcs.execute("SELECT `User_ID` FROM `User_Base` WHERE `User_ID` = %s LIMIT 1;", (new_user_id,))
                        out = dbcs.fetchone()
                        if out == None:
                            found_new_uuid = True
                        else:
                            found_new_uuid = False
                owner_uuid = new_user_id
                dbcs.execute("INSERT INTO `User_Base`(`User_ID`, `Username`, `Username_Proper`, `Join_Datetime`) VALUES (%s, %s, %s, %s);", (new_user_id, characterowner.lower(), characterowner, datetime.now()))
                dbase.commit()
            else:
                owner_uuid = out[0]
            dbase.commit()
            dbcs.execute("SELECT * FROM `Character_Owner` WHERE `Character_ID` = %s AND `User_ID` = %s LIMIT 1;", (character_uuid, owner_uuid))
            out = dbcs.fetchone()
            if out == None:
                dbcs.execute("INSERT INTO `Character_Owner`(`Character_ID`, `User_ID`, `Username`, `Username_Proper`) VALUES (%s, %s, %s, %s);", (character_uuid, owner_uuid, characterowner.lower(), characterowner))
            dbcs.execute("SELECT `Character_ID` FROM `Character_Alias` WHERE `Character_ID` = %s AND `Character_Alias` = %s LIMIT 1;", (character_uuid, charactername.lower()))
            out = dbcs.fetchone()
            if out == None:
                dbcs.execute("INSERT INTO `Character_Alias` (`Character_ID`, `Character_Alias`, `Character_Alias_Proper`) VALUES (%s, %s, %s);", (character_uuid, charactername.lower(), charactername))
            dbase.commit()
        species_uuid = None
        if characterspecies != None and characterspecies != "" and characterspecies.isspace() == False:
            dbcs.execute("SELECT `Species_ID` FROM `Species_Base` WHERE `Species_Name` = %s LIMIT 1;", (characterspecies.lower(),))
            out = dbcs.fetchone()
            if out == None:
                new_species_id = str(uuid.uuid4().hex)
                dbcs.execute("SELECT `Species_ID` FROM `Species_Base` WHERE `Species_ID` = %s LIMIT 1;", (new_species_id,))
                out = dbcs.fetchone()
                if out != None:
                    found_new_uuid = False
                    while found_new_uuid == False:
                        new_species_id = str(uuid.uuid4().hex)
                        dbcs.execute("SELECT `Species_ID` FROM `Species_Base` WHERE `Species_ID` = %s LIMIT 1;", (new_species_id,))
                        out = dbcs.fetchone()
                        if out == None:
                            found_new_uuid = True
                        else:
                            found_new_uuid = False
                species_uuid = new_species_id
                dbcs.execute("INSERT INTO `Species_Base`(`Species_ID`, `Species_Name`, `Species_Name_Proper`) VALUES (%s, %s, %s);", (new_species_id, characterspecies.lower(), characterspecies))
                dbase.commit()
            else:
                species_uuid = out[0]
            dbcs.execute("SELECT * FROM `Character_Species` WHERE `Character_ID` = %s AND `Species_ID` = %s LIMIT 1;", (character_uuid, species_uuid))
            out = dbcs.fetchone()
            if out == None:
                dbcs.execute("INSERT INTO `Character_Species`(`Character_ID`, `Species_ID`) VALUES (%s, %s);", (character_uuid, species_uuid))
            dbase.commit()
        campaign_uuid = None
        if charactercampaign != None and charactercampaign != "" and charactercampaign.isspace() == False:
            dbcs.execute("SELECT `Campaign_ID` FROM `Campaign_Base` WHERE `Campaign_Name` = %s LIMIT 1;", (charactercampaign.lower(),))
            out = dbcs.fetchone()
            if out == None:
                new_campaign_id = str(uuid.uuid4().hex)
                dbcs.execute("SELECT `Campaign_ID` FROM `Campaign_Base` WHERE `Campaign_ID` = %s LIMIT 1;", (new_campaign_id,))
                out = dbcs.fetchone()
                if out != None:
                    found_new_uuid = False
                    while found_new_uuid == False:
                        new_campaign_id = str(uuid.uuid4().hex)
                        dbcs.execute("SELECT `Campaign_ID` FROM `Campaign_Base` WHERE `Campaign_ID` = %s LIMIT 1;", (new_campaign_id,))
                        out = dbcs.fetchone()
                        if out == None:
                            found_new_uuid = True
                        else:
                            found_new_uuid = False
                campaign_uuid = new_campaign_id
                dbcs.execute("INSERT INTO `Campaign_Base`(`Campaign_ID`, `Campaign_Name`, `Campaign_Name_Proper`) VALUES (%s, %s, %s);", (new_campaign_id, charactercampaign.lower(), charactercampaign))
                dbase.commit()
            else:
                campaign_uuid = out[0]
            dbcs.execute("SELECT * FROM `Character_Campaign` WHERE `Character_ID` = %s AND `Campaign_ID` = %s LIMIT 1;", (character_uuid, campaign_uuid))
            out = dbcs.fetchone()
            if out == None:
                dbcs.execute("INSERT INTO `Character_Campaign`(`Character_ID`, `Campaign_ID`) VALUES (%s, %s);", (character_uuid, campaign_uuid))
            dbase.commit()
        dbcs.execute("SELECT * FROM `Files_Characters` WHERE `File_ID` = %s AND `Character_ID` = %s LIMIT 1;", (file_uuid, character_uuid))
        out = dbcs.fetchone()
        if out == None:
            dbcs.execute("INSERT INTO `Files_Characters` (`File_ID`, `Character_ID`, `Species_ID`) VALUES (%s, %s, %s);", (file_uuid, character_uuid, species_uuid))
        dbase.commit()
        searchinsertlist.append(f"character_id:{character_uuid}")
        searchinsertlist.append(f"characterid:{character_uuid}")
        searchinsertlist.append(f"character:{charactername.lower()}")
        searchinsertlist.append(f"charactername:{charactername.lower()}")
        searchinsertlist.append(f"character_name:{charactername.lower()}")
    for i in specieslist:
        speciesname = i["Name"].strip()
        speciesuniverse = i["Universe"].strip()
        if speciesname == None or speciesname == "" or speciesname.isspace() == True:
            continue
        dbcs.execute("SELECT `Species_ID` FROM `Species_Base` WHERE `Species_Name` = %s LIMIT 1;", (speciesname.lower(),))
        out = dbcs.fetchone()
        species_uuid = None
        if out == None:
            new_species_id = str(uuid.uuid4().hex)
            dbcs.execute("SELECT `Species_ID` FROM `Species_Base` WHERE `Species_ID` = %s LIMIT 1;", (new_species_id,))
            out = dbcs.fetchone()
            if out != None:
                found_new_uuid = False
                while found_new_uuid == False:
                    new_species_id = str(uuid.uuid4().hex)
                    dbcs.execute("SELECT `Species_ID` FROM `Species_Base` WHERE `Species_ID` = %s LIMIT 1;", (new_species_id,))
                    out = dbcs.fetchone()
                    if out == None:
                        found_new_uuid = True
                    else:
                        found_new_uuid = False
            species_uuid = new_species_id
            dbcs.execute("INSERT INTO `Species_Base`(`Species_ID`, `Species_Name`, `Species_Name_Proper`) VALUES (%s, %s, %s);", (new_species_id, speciesname.lower(), speciesname))
            dbase.commit()
        else:
            species_uuid = out[0]
        universe_uuid = None
        if speciesuniverse != None and speciesuniverse != "" and speciesuniverse.isspace() == False:
            dbcs.execute("SELECT `Universe_ID` FROM `Universe_Base` WHERE `Universe_Name` = %s LIMIT 1;", (speciesuniverse.lower(),))
            out = dbcs.fetchone()
            if out == None:
                new_universe_id = str(uuid.uuid4().hex)
                dbcs.execute("SELECT `Universe_ID` FROM `Universe_Base` WHERE `Universe_ID` = %s LIMIT 1;", (new_universe_id,))
                out = dbcs.fetchone()
                if out != None:
                    found_new_uuid = False
                    while found_new_uuid == False:
                        new_universe_id = str(uuid.uuid4().hex)
                        dbcs.execute("SELECT `Universe_ID` FROM `Universe_Base` WHERE `Universe_ID` = %s LIMIT 1;", (new_universe_id,))
                        out = dbcs.fetchone()
                        if out == None:
                            found_new_uuid = True
                        else:
                            found_new_uuid = False
                universe_uuid = new_universe_id
                dbcs.execute("INSERT INTO `Universe_Base`(`Universe_ID`, `Universe_Name`, `Universe_Name_Proper`) VALUES (%s, %s, %s);", (new_universe_id, speciesuniverse.lower(), speciesuniverse))
                dbase.commit()
            else:
                universe_uuid = out[0]
            dbcs.execute("SELECT * FROM `Species_Universe` WHERE `Species_ID` = %s AND `Universe_ID` = %s LIMIT 1;", (species_uuid, universe_uuid))
            out = dbcs.fetchone()
            if out == None:
                dbcs.execute("INSERT INTO `Species_Universe` (`Species_ID`, `Universe_ID`) VALUES (%s, %s);", (species_uuid, universe_uuid))
            dbase.commit()
        dbcs.execute("SELECT * FROM `Files_Species` WHERE `File_ID` = %s AND `Species_ID` = %s LIMIT 1;", (file_uuid, species_uuid))
        out = dbcs.fetchone()
        if out == None:
            dbcs.execute("INSERT INTO `Files_Species`(`File_ID`, `Species_ID`) VALUES (%s, %s);", (file_uuid, species_uuid))
        dbcs.execute("SELECT `Species_ID` FROM `Species_Alias` WHERE `Species_ID` = %s AND `Species_Alias` = %s LIMIT 1;", (species_uuid, speciesname.lower()))
        out = dbcs.fetchone()
        if out == None:
            dbcs.execute("INSERT INTO `Species_Alias`(`Species_ID`, `Species_Alias`, `Species_Alias_Proper`) VALUES (%s, %s, %s)", (species_uuid, speciesname.lower(), speciesname))
        dbase.commit()
        searchinsertlist.append(f"species_id:{species_uuid}")
        searchinsertlist.append(f"speciesid:{species_uuid}")
        searchinsertlist.append(f"species:{speciesname.lower()}")
        searchinsertlist.append(f"speciesname:{speciesname.lower()}")
        searchinsertlist.append(f"species_name:{speciesname.lower()}")
    for i in campaignlist:
        campaignname = i["Name"].strip()
        campaignuniverse = i["Universe"].strip()
        campaignowner = i["Owner"].strip()
        campaign_uuid = None
        if campaignname == None or campaignname == "" or campaignname.isspace() == True:
            continue
        else:
            dbcs.execute("SELECT `Campaign_ID` FROM `Campaign_Base` WHERE `Campaign_Name` = %s LIMIT 1;", (campaignname.lower(),))
            out = dbcs.fetchone()
            if out == None:
                new_campaign_id = str(uuid.uuid4().hex)
                dbcs.execute("SELECT `Campaign_ID` FROM `Campaign_Base` WHERE `Campaign_ID` = %s LIMIT 1;", (new_campaign_id,))
                out = dbcs.fetchone()
                if out != None:
                    found_new_uuid = False
                    while found_new_uuid == False:
                        new_campaign_id = str(uuid.uuid4().hex)
                        dbcs.execute("SELECT `Campaign_ID` FROM `Campaign_Base` WHERE `Campaign_ID` = %s LIMIT 1;", (new_campaign_id,))
                        out = dbcs.fetchone()
                        if out == None:
                            found_new_uuid = True
                        else:
                            found_new_uuid = False
                campaign_uuid = new_campaign_id
                dbcs.execute("INSERT INTO `Campaign_Base`(`Campaign_ID`, `Campaign_Name`, `Campaign_Name_Proper`) VALUES (%s, %s, %s);", (new_campaign_id, campaignname.lower(), campaignname))
                dbase.commit()
            else:
                campaign_uuid = out[0]
        universe_uuid = None
        if campaignuniverse != None and campaignuniverse != "" and campaignuniverse.isspace() == False:
            dbcs.execute("SELECT `Universe_ID` FROM `Universe_Base` WHERE `Universe_Name` = %s LIMIT 1;", (campaignuniverse.lower(),))
            out = dbcs.fetchone()
            if out == None:
                new_universe_id = str(uuid.uuid4().hex)
                dbcs.execute("SELECT `Universe_ID` FROM `Universe_Base` WHERE `Universe_ID` = %s LIMIT 1;", (new_universe_id,))
                if out != None:
                    found_new_uuid = False
                    while found_new_uuid == False:
                        new_universe_id = str(uuid.uuid4().hex)
                        dbcs.execute("SELECT `Universe_ID` FROM `Universe_Base` WHERE `Universe_ID` = %s LIMIT 1;", (new_universe_id,))
                        out = dbcs.fetchone()
                        if out == None:
                            found_new_uuid = True
                        else:
                            found_new_uuid = False
                universe_uuid = new_universe_id
                dbcs.execute("INSERT INTO `Universe_Base`(`Universe_ID`, `Universe_Name`, `Universe_Name_Proper`) VALUES (%s, %s, %s);", (new_universe_id, campaignuniverse.lower(), campaignuniverse))
                dbase.commit()
            else:
                universe_uuid = out[0]
            dbcs.execute("SELECT * FROM `Campaign_Universe` WHERE `Campaign_ID` = %s AND `Universe_ID` = %s LIMIT 1;", (campaign_uuid, universe_uuid))
            out = dbcs.fetchone()
            if out == None:
                dbcs.execute("INSERT INTO `Campaign_Universe`(`Campaign_ID`, `Universe_ID`) VALUES (%s, %s);", (campaign_uuid, universe_uuid))
            dbase.commit()
        owner_uuid = None
        if campaignowner != None and campaignowner != "" and campaignowner.isspace() == False:
            dbcs.execute("SELECT `User_ID` FROM `User_Base` WHERE `Username` = %s LIMIT 1;", (campaignowner.lower(),))
            out = dbcs.fetchone()
            if out == None:
                new_user_id = str(uuid.uuid4().hex)
                dbcs.execute("SELECT `User_ID` FROM `User_Base` WHERE `User_ID` = %s LIMIT 1;", (new_user_id,))
                out = dbcs.fetchone()
                if out != None:
                    found_new_uuid = False
                    while found_new_uuid == False:
                        new_user_id = str(uuid.uuid4().hex)
                        dbcs.execute("SELECT `User_ID` FROM `User_Base` WHERE `User_ID` = %s LIMIT 1;", (new_user_id,))
                        out = dbcs.fetchone()
                        if out == None:
                            found_new_uuid = True
                        else:
                            found_new_uuid = False
                owner_uuid = new_user_id
                dbcs.execute("INSERT INTO `User_Base`(`User_ID`, `Username`, `Username_Proper`, `Join_Datetime`) VALUES (%s, %s, %s, %s);", (new_user_id, campaignowner.lower(), campaignowner, datetime.now()))
                dbase.commit()
            else:
                owner_uuid = out[0]
            dbase.commit()
            dbcs.execute("SELECT * FROM `Campaign_Owner` WHERE `Campaign_ID` = %s AND `User_ID` = %s LIMIT 1;", (campaign_uuid, owner_uuid))
            out = dbcs.fetchone()
            if out == None:
                dbcs.execute("INSERT INTO `Campaign_Owner` (`Campaign_ID`, `User_ID`) VALUES (%s, %s);", (campaign_uuid, owner_uuid))
            dbase.commit()
        dbcs.execute("SELECT * FROM `Files_Campaign` WHERE `File_ID` = %s AND `Campaign_ID` = %s LIMIT 1;", (file_uuid, campaign_uuid))
        out = dbcs.fetchone()
        if out == None:
            dbcs.execute("INSERT INTO `Files_Campaign` (`File_ID`, `Campaign_ID`) VALUES (%s, %s);", (file_uuid, campaign_uuid))
        dbase.commit()
        searchinsertlist.append(f"campaign_id:{campaign_uuid}")
        searchinsertlist.append(f"campaignid:{campaign_uuid}")
        searchinsertlist.append(f"campaign:{campaignname.lower()}")
        searchinsertlist.append(f"campaignname:{campaignname.lower()}")
        searchinsertlist.append(f"campaign_name:{campaignname.lower()}")
    for i in universelist:
        universename = i["Name"].strip()
        universeowner = i["Owner"].strip()
        universe_uuid = None
        if universename == None or universename == "" or universename.isspace() == True: # Don't specify a blank universe
            continue
        dbcs.execute("SELECT `Universe_ID` FROM `Universe_Base` WHERE `Universe_Name` = %s LIMIT 1;", (universename.lower(),))
        out = dbcs.fetchone()
        if out == None:
            new_universe_id = str(uuid.uuid4().hex)
            dbcs.execute("SELECT `Universe_ID` FROM `Universe_Base` WHERE `Universe_ID` = %s LIMIT 1;", (new_universe_id,))
            out = dbcs.fetchone()
            if out != None:
                found_new_uuid = False
                while found_new_uuid == False:
                    new_universe_id = str(uuid.uuid4().hex)
                    dbcs.execute("SELECT `Universe_ID` FROM `Universe_Base` WHERE `Universe_ID` = %s LIMIT 1;", (new_universe_id,))
                    out = dbcs.fetchone()
                    if out == None:
                        found_new_uuid = True
                    else:
                        found_new_uuid = False
            universe_uuid = new_universe_id
            dbcs.execute("INSERT INTO `Universe_Base`(`Universe_ID`, `Universe_Name`, `Universe_Name_Proper`) VALUES (%s, %s, %s);", (new_universe_id, universename.lower(), universename))
            dbase.commit()
        else:
            universe_uuid = out[0]
        owner_uuid = None
        if universeowner != None and universeowner != "" and universeowner.isspace() == False:
            dbcs.execute("SELECT `User_ID` FROM `User_Base` WHERE `Username` = %s LIMIT 1;", (universeowner.lower(),))
            out = dbcs.fetchone()
            if out == None:
                new_user_id = str(uuid.uuid4().hex)
                dbcs.execute("SELECT `User_ID` FROM `User_Base` WHERE `User_ID` = %s LIMIT 1;", (new_user_id,))
                out = dbcs.fetchone()
                if out != None:
                    found_new_uuid = False
                    while found_new_uuid == False:
                        new_user_id = str(uuid.uuid4().hex)
                        dbcs.execute("SELECT `User_ID` FROM `User_Base` WHERE `User_ID` = %s LIMIT 1;", (new_user_id,))
                        out = dbcs.fetchone()
                        if out == None:
                            found_new_uuid = True
                        else:
                            found_new_uuid = False
                owner_uuid = new_user_id
                dbcs.execute("INSERT INTO `User_Base`(`User_ID`, `Username`, `Username_Proper`, `Join_Datetime`) VALUES (%s, %s, %s, %s);", (new_user_id, universeowner.lower(), universeowner, datetime.now()))
                dbase.commit()
            else:
                owner_uuid = out[0]
            dbase.commit()
            dbcs.execute("SELECT * FROM `Universe_Owner` WHERE `Universe_ID` = %s AND `User_ID` = %s LIMIT 1;", (universe_uuid, owner_uuid))
            out = dbcs.fetchone()
            if out == None:
                dbcs.execute("INSERT INTO `Universe_Owner` (`Universe_ID`, `User_ID`) VALUES (%s, %s);", (universe_uuid, owner_uuid))
                dbase.commit()
        dbcs.execute("SELECT * FROM `Files_Universe` WHERE `File_ID` = %s AND `Universe_ID` = %s LIMIT 1;", (file_uuid, universe_uuid))
        out = dbcs.fetchone()
        if out == None:
            dbcs.execute("INSERT INTO `Files_Universe` (`File_ID`, `Universe_ID`) VALUES (%s, %s);", (file_uuid, universe_uuid))
        dbase.commit()
        searchinsertlist.append(f"universe_id:{universe_uuid}")
        searchinsertlist.append(f"universeid:{universe_uuid}")
        searchinsertlist.append(f"universe:{universename.lower()}")
        searchinsertlist.append(f"universename:{universename.lower()}")
        searchinsertlist.append(f"universe_name:{universename.lower()}")
    for i in tagslist:
        i = i.strip()
        if i == None or i == "" or i.isspace():
            continue
        dbcs.execute("SELECT `Tag_ID` FROM `Tag_Base` WHERE `Tag` = %s LIMIT 1;", (i.lower(),))
        out = dbcs.fetchone()
        tag_uuid = None
        if out == None:
            new_tag_id = str(uuid.uuid4().hex)
            dbcs.execute("SELECT `Tag_ID` FROM `Tag_Base` WHERE `Tag_ID` = %s LIMIT 1;", (new_tag_id,))
            out = dbcs.fetchone()
            if out != None:
                found_new_uuid = False
                while found_new_uuid == False:
                    new_tag_id = str(uuid.uuid4().hex)
                    dbcs.execute("SELECT `Tag_ID` FROM `Tag_Base` WHERE `Tag_ID` = %s LIMIT 1;", (new_tag_id,))
                    out = dbcs.fetchone()
                    if out == None:
                        found_new_uuid = True
                    else:
                        found_new_uuid = False
            tag_uuid = new_tag_id
            dbcs.execute("INSERT INTO `Tag_Base`(`Tag_ID`, `Tag`, `Tag_Proper`) VALUES (%s, %s, %s);", (new_tag_id, i.lower(), i))
            dbase.commit()
        else:
            tag_uuid = out[0]
        dbcs.execute("SELECT * FROM `Files_Tags` WHERE `File_ID` = %s AND `Tag_ID` = %s LIMIT 1;", (file_uuid, tag_uuid))
        out = dbcs.fetchone()
        if out == None:
            dbcs.execute("INSERT INTO `Files_Tags` (`File_ID`, `Tag_ID`) VALUES (%s, %s);", (file_uuid, tag_uuid))
        dbase.commit()
        searchinsertlist.append(f"tag_id:{tag_uuid}")
        searchinsertlist.append(f"tagid:{tag_uuid}")
        searchinsertlist.append(f"tag:{i.lower()}")
        searchinsertlist.append(f"{i.lower()}")
    for i in searchinsertlist:
        i = i.strip()
        dbcs.execute("INSERT INTO `File_Search_Master`(`File_ID`, `Search_Term`) VALUES (%s, %s);", (file_uuid, i))
        dbase.commit()
    dbase.commit()
    dbcs.close()
    dbase.close()
    return

def CheckUserIsAdmin(user_id: str) -> bool:
    dbase = ConnectToDB()
    dbcs = dbase.cursor(prepared = True)
    dbcs.execute("SELECT `User_ID` FROM `User_Admin` WHERE `User_ID` = %s LIMIT 1;", (user_id,))
    out = dbcs.fetchone()
    dbcs.close()
    dbase.close()
    if out != None:
        return True
    return False

def AuthenticateAuthTokenAsAdmin(auth_token: str) -> bool:
    user_id = FetchUserIDFromAuthToken(auth_token)
    return CheckUserIsAdmin(user_id)

def CleanExpiredAuthTokens(): # This function is designed to be ran as a thread, but can be executed on its own as well.
    dbase = ConnectToDB()
    dbcs = dbase.cursor(prepared=True)
    dbcs.execute("DELETE FROM `User_Auth` WHERE `Expiration` < %s;", (datetime.now(),))
    dbase.commit()
    dbcs.close()
    dbase.close()
    return

def ForceDeleteAllAuthTokens(): # This will log out everybody. Only use me if there is a security issue.
    dbase = ConnectToDB()
    dbcs = dbase.cursor(prepared=True)
    dbcs.execute("TRUNCATE TABLE `User_Auth`;")
    dbase.commit()
    dbcs.close()
    dbase.close()
    return

def GetDatabaseStats() -> tuple: # Fetches how many of each data type the database has.
    dbase = ConnectToDB()
    dbcs = dbase.cursor(prepared=True)
    dbcs.execute("SELECT COUNT(*) FROM `Files_Base`;")
    out = dbcs.fetchone()
    filecnt = out[0]
    dbcs.execute("SELECT COUNT(*) FROM `Artist_Base`;")
    out = dbcs.fetchone()
    artistcnt = out[0]
    dbcs.execute("SELECT COUNT(*) FROM `Campaign_Base`;")
    out = dbcs.fetchone()
    campaigncnt = out[0]
    dbcs.execute("SELECT COUNT(*) FROM `Character_Base`;")
    out = dbcs.fetchone()
    charactercnt = out[0]
    dbcs.execute("SELECT COUNT(*) FROM `Species_Base`;")
    out = dbcs.fetchone()
    speciescnt = out[0]
    dbcs.execute("SELECT COUNT(*) FROM `Tag_Base`;")
    out = dbcs.fetchone()
    tagcnt = out[0]
    dbcs.execute("SELECT COUNT(*) FROM `Universe_Base`;")
    out = dbcs.fetchone()
    universecnt = out[0]
    dbcs.execute("SELECT COUNT(*) FROM `User_Base`;")
    out = dbcs.fetchone()
    usercnt = out[0]
    dbcs.execute("SELECT COUNT(*) FROM `User_Auth`;")
    out = dbcs.fetchone()
    authusrcnt = out[0]   
    dbcs.execute("SELECT COUNT(*) FROM `File_Search_Master`;")
    out = dbcs.fetchone()
    srchcnt = out[0]
    dbcs.close()
    dbase.close()
    return (artistcnt, campaigncnt, charactercnt, filecnt, speciescnt, srchcnt, tagcnt, universecnt, usercnt, authusrcnt)

