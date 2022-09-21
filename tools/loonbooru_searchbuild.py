import mysql.connector
from datetime import datetime

dburl = "127.0.0.1"
dbusr = "loonbooru"
dbpwd = "BgjplxX3jqUuiyV3"
dbname = "loonbooru"

def ConnectToDB() -> mysql.connector:
    dbase = mysql.connector.connect(host=dburl, user=dbusr, password=dbpwd, database=dbname)
    return dbase

dbase = ConnectToDB()
dbcs = dbase.cursor(prepared=True)
dbcs.execute("SELECT * FROM information_schema.tables WHERE table_schema = %s AND table_name = 'File_Search_Master' LIMIT 1", (dbname,))
tablechk = dbcs.fetchall()
if len(tablechk) == 0: # Table does not exist, so create.
    dbcs.execute("CREATE TABLE `File_Search_Master` (`File_ID` varchar(32) DEFAULT NULL, `Search_Term` tinytext NOT NULL) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;")
    dbcs.commit()
else: # Table does exist, so empty contents.
    dbcs.execute("TRUNCATE TABLE `File_Search_Master`")
    dbase.commit()

dbcs.execute("SELECT * FROM `Files_Base` WHERE 1;")
filels = dbcs.fetchall()
for i in filels:
    fileid = i[0]
    uploaderid = i[1]
    fileext = i[2]
    dispname = i[3]
    desc = i[4]
    rating = i[5]
    uploaddt = i[6]
    
    dbcs.execute("INSERT INTO `File_Search_Master` (`File_ID`, `Search_Term`) VALUES (%s, %s);", (fileid, f"file_id:{fileid.lower()}"))
    dbcs.execute("INSERT INTO `File_Search_Master` (`File_ID`, `Search_Term`) VALUES (%s, %s);", (fileid, f"uploader_id:{uploaderid.lower()}"))
    dbase.commit()
    dbcs.execute("SELECT `Username` FROM `User_Base` WHERE `User_ID` = %s LIMIT 1;", (uploaderid,))
    uploaderunamer = dbcs.fetchone()
    uploaderuname = uploaderunamer[0]
    if uploaderuname.find(",") != -1:
        uploaderuname = uploaderuname.replace(",", "")
    dbcs.execute("INSERT INTO `File_Search_Master` (`File_ID`, `Search_Term`) VALUES (%s, %s);", (fileid, f"uploader:{uploaderuname.lower()}"))
    dbase.commit()
    if uploaderuname.find(" ") != -1:
        uploaderuname = uploaderuname.replace(" ", "_")
        dbcs.execute("INSERT INTO `File_Search_Master` (`File_ID`, `Search_Term`) VALUES (%s, %s);", (fileid, f"uploader:{uploaderuname.lower()}"))
    dbase.commit()
    dbcs.execute("INSERT INTO `File_Search_Master` (`File_ID`, `Search_Term`) VALUES (%s, %s);", (fileid, f"file_ext:{fileext.lower()}"))
    dbase.commit()
    if dispname.find(",") != -1:
        dispname = dispname.replace(",", "")
    dbcs.execute("INSERT INTO `File_Search_Master` (`File_ID`, `Search_Term`) VALUES (%s, %s);", (fileid, f"file_name:{dispname.lower()}"))
    if dispname.find(" ") != -1:
        dispname = dispname.replace(" ", "_")
        dbcs.execute("INSERT INTO `File_Search_Master` (`File_ID`, `Search_Term`) VALUES (%s, %s);", (fileid, f"file_name:{dispname.lower()}"))
    dbase.commit()
    if desc.find(",") != -1:
        desc = desc.replace(",", "")
    if desc.find("/n") != -1:
        desc = desc.replace("/n", " ")
    dbcs.execute("INSERT INTO `File_Search_Master` (`File_ID`, `Search_Term`) VALUES (%s, %s);", (fileid, f"description:{desc.lower()}"))
    dbase.commit()
    if desc.find(" ") != -1:
        desc = desc.replace(" ", "_")
        dbcs.execute("INSERT INTO `File_Search_Master` (`File_ID`, `Search_Term`) VALUES (%s, %s);", (fileid, f"description:{desc.lower()}"))
    dbase.commit()
    if rating.lower() == "s":
        dbcs.execute("INSERT INTO `File_Search_Master` (`File_ID`, `Search_Term`) VALUES (%s, %s);", (fileid, "rating:safe"))
    elif rating.lower() == "q":
        dbcs.execute("INSERT INTO `File_Search_Master` (`File_ID`, `Search_Term`) VALUES (%s, %s);", (fileid, "rating:questionable"))
    elif rating == "e":
        dbcs.execute("INSERT INTO `File_Search_Master` (`File_ID`, `Search_Term`) VALUES (%s, %s);", (fileid, "rating:explicit"))
    elif rating == "f":
        dbcs.execute("INSERT INTO `File_Search_Master` (`File_ID`, `Search_Term`) VALUES (%s, %s);", (fileid, "rating:flat"))
    dbase.commit()

    # TODO: Fix the following to use whatever that function that converts datetime to string because I can't remember and don't have the time to do it right now.

    # dbcs.execute("INSERT INTO `File_Search_Master` (`File_ID`, `Search_Term`) VALUES (%s, %s);", (fileid, f"upload:{uploaddt.lower()}"))
    # dbcs.execute("INSERT INTO `File_Search_Master` (`File_ID`, `Search_Term`) VALUES (%s, %s);", (fileid, f"uploaddatetime:{uploaddt.lower()}"))
    # dbcs.execute("INSERT INTO `File_Search_Master` (`File_ID`, `Search_Term`) VALUES (%s, %s);", (fileid, f"upload_datetime:{uploaddt.lower()}"))
    # dbcs.execute("INSERT INTO `File_Search_Master` (`File_ID`, `Search_Term`) VALUES (%s, %s);", (fileid, f"uploaddt:{uploaddt.lower()}"))
    # dbcs.execute("INSERT INTO `File_Search_Master` (`File_ID`, `Search_Term`) VALUES (%s, %s);", (fileid, f"upload_dt:{uploaddt.lower()}"))
    # dbase.commit()

    dbcs.execute("SELECT `Campaign_ID` FROM `Files_Campaign` WHERE `File_ID` = %s;", (fileid,))

    campaignidlsr = dbcs.fetchall()
    campaignidls = []
    for j in campaignidlsr:
        campaignidls.append(j[0])
    campaignnamels = []
    for j in campaignidls:
        dbcs.execute("SELECT `Campaign_Name` FROM `Campaign_Base` WHERE `Campaign_ID` = %s LIMIT 1;", (j,))
        campaignnamels.append(dbcs.fetchone())

    for j in campaignidls:
        if j.find(",") != -1:
            j.replace(",", "")
        dbcs.execute("INSERT INTO `File_Search_Master` (`File_ID`, `Search_Term`) VALUES (%s, %s);", (fileid, f"campaign_id:{j.lower()}"))
        if j.find(" ") != -1:
            j.replace(" ", "_")
            dbcs.execute("INSERT INTO `File_Search_Master` (`File_ID`, `Search_Term`) VALUES (%s, %s);", (fileid, f"campaign_id:{j.lower()}"))
        dbase.commit()
    
    for j in campaignnamels:
        if j[0].find(",") != -1:
            j[0].replace(",", "")
        dbcs.execute("INSERT INTO `File_Search_Master` (`File_ID`, `Search_Term`) VALUES (%s, %s);", (fileid, f"campaign:{j[0].lower()}"))
        if j[0].find(" ") != -1:
            j[0].replace(" ", "_")
            dbcs.execute("INSERT INTO `File_Search_Master` (`File_ID`, `Search_Term`) VALUES (%s, %s);", (fileid, f"campaign:{j[0].lower()}"))
        dbase.commit()
    del campaignidlsr, campaignidls, campaignnamels

    dbcs.execute("SELECT `Universe_ID` FROM `Files_Universe` WHERE `File_ID` = %s;"), (fileid,)
    universeidlsr = dbcs.fetchall()
    universeidls = []
    for j in universeidlsr:
        universeidls.append(j[0])
    universenamels = []
    for j in universeidls:
        dbcs.execute("SELECT `Universe_Name` FROM `Universe_Base` WHERE `Universe_ID` = %s LIMIT 1;", (j,))
        universenamels.append(dbcs.fetchone())

    for j in universeidls:
        if j.find(",") != -1:
            j.replace(",", "")
        dbcs.execute("INSERT INTO `File_Search_Master` (`File_ID`, `Search_Term`) VALUES (%s, %s);", (fileid, f"universe_id:{j.lower()}"))
        if j.find(" ") != -1:
            j.replace(" ", "_")
            dbcs.execute("INSERT INTO `File_Search_Master` (`File_ID`, `Search_Term`) VALUES (%s, %s);", (fileid, f"universe_id:{j.lower()}"))
        dbcs.commit()
    
    for j in universenamels:
        if j.find(",") != -1:
            j.replace(",", "")
        dbcs.execute("INSERT INTO `File_Search_Master` (`File_ID`, `Search_Term`) VALUES (%s, %s);", (fileid, f"universe:{j.lower()}"))
        if j.find(" ") != -1:
            j.replace(" ", "_")
            dbcs.execute("INSERT INTO `File_Search_Master` (`File_ID`, `Search_Term`) VALUES (%s, %s);", (fileid, f"universe:{j.lower()}"))
        dbase.commit()
    del universeidlsr, universeidls, universenamels

    dbcs.execute("SELECT `Artist_ID` FROM `Files_Artist` WHERE `File_ID` = %s;", (fileid,))
    artistidlsr = dbcs.fetchall()
    artistidls = []
    for j in artistidlsr:
        artistidls.append(j[0])
    artistls = []
    for j in artistidls:
        dbcs.execute("SELECT * FROM `Artist_Base` WHERE `Artist_ID` = %s LIMIT 1;", (j,))
        artistls.append(dbcs.fetchone())
    
    for j in artistls:
        if j[0].find(",") != -1:
            j[0].replace(",", "")
        dbcs.execute("INSERT INTO `File_Search_Master` (`File_ID`, `Search_Term`) VALUES (%s, %s);", (fileid, f"artist_id:{j[0].lower()}"))
        if j[0].find(" ") != -1:
            j[0].replace(" ", "_")
            dbcs.execute("INSERT INTO `File_Search_Master` (`File_ID`, `Search_Term`) VALUES (%s, %s);", (fileid, f"artist_id:{j[0].lower()}"))
        dbase.commit()
        if j[1] != None:
            if j[1].find(",") != -1:
                j[1].replace(",", "")
            dbcs.execute("INSERT INTO `File_Search_Master` (`File_ID`, `Search_Term`) VALUES (%s, %s);", (fileid, f"artist_user_id:{j[1].lower()}"))
            if j[1].find(" ") != -1:
                j[1].replace(" ", "_")
                dbcs.execute("INSERT INTO `File_Search_Master` (`File_ID`, `Search_Term`) VALUES (%s, %s);", (fileid, f"artist_user_id:{j[1].lower()}"))
        dbase.commit()
        if j[2].find(",") != -1:
            j[2].replace(",", "")
        dbcs.execute("INSERT INTO `File_Search_Master` (`File_ID`, `Search_Term`) VALUES (%s, %s);", (fileid, f"artist:{j[2].lower()}"))
        if j[2].find(" ") != -1:
            j[2].replace(" ", "_")
            dbcs.execute("INSERT INTO `File_Search_Master` (`File_ID`, `Search_Term`) VALUES (%s, %s);", (fileid, f"artist:{j[2].lower()}"))
        dbase.commit()
    del artistidlsr, artistidls, artistls

    dbcs.execute("SELECT `Tag_ID` FROM `Files_Tags` WHERE `File_ID` = %s;", (fileid,))
    tagidlsr = dbcs.fetchall()
    tagidls = []
    for j in tagidlsr:
        tagidls.append(j[0])
    tagnamels = []
    for j in tagidls:
        dbcs.execute("SELECT `Tag` FROM `Tag_Base` WHERE `Tag_ID` = %s LIMIT 1;", (j,))
        tagnamels.append(dbcs.fetchone())
    for j in tagidls:
        if j.find(",") != -1:
            j.replace(",", "")
        dbcs.execute("INSERT INTO `File_Search_Master` (`File_ID`, `Search_Term`) VALUES (%s, %s);", (fileid, f"tag_id:{j.lower()}"))
        if j.find(" ") != -1:
            j.replace(" ", "_")
            dbcs.execute("INSERT INTO `File_Search_Master` (`File_ID`, `Search_Term`) VALUES (%s, %s);", (fileid, f"tag_id:{j.lower()}"))
        dbase.commit()
    for j in tagnamels:
        if j[0].find(",") != -1:
            j[0].replace(",", "")
        dbcs.execute("INSERT INTO `File_Search_Master` (`File_ID`, `Search_Term`) VALUES (%s, %s);", (fileid, f"{j[0].lower()}"))
        if j[0].find(" ") != -1:
            j[0].replace(" ", "_")
            dbcs.execute("INSERT INTO `File_Search_Master` (`File_ID`, `Search_Term`) VALUES (%s, %s);", (fileid, f"{j[0].lower()}"))
        dbase.commit()
    del tagidlsr, tagidls, tagnamels

    dbcs.execute("SELECT `Character_ID`, `Species_ID` FROM `Files_Characters` WHERE `File_ID` = %s;", (fileid,))
    chout = dbcs.fetchall()
    charspecidls = []
    for j in chout:
        charspecidls.append((j[0], j[1]))
    charnamels = []
    specnamels = []
    charownerls = []
    for j in charspecidls:
        dbcs.execute("SELECT `Character_Name` FROM `Character_Base` WHERE `Character_ID` = %s LIMIT 1;", (j[0],))
        out = dbcs.fetchone()
        if out[0] != None:
            charnamels.append(out[0])
        dbcs.execute("SELECT `Character_Alias` FROM `Character_Alias` WHERE `Character_ID` = %s AND `Character_Alias` != %s;", (j[0], out[0]))
        out = dbcs.fetchall()
        for k in out:
            if k[0] != None:
                charnamels.append(k[0])
        dbcs.execute("SELECT `Species_Name` FROM `Species_Base` WHERE `Species_ID` = %s LIMIT 1;", (j[1],))
        out = dbcs.fetchone()
        if out[0] != None:
            specnamels.append(out[0])
        dbcs.execute("SELECT `Species_Alias` FROM `Species_Alias` WHERE `Species_ID` = %s AND `Species_Alias` != %s;", (j[1], out[0]))
        out = dbcs.fetchall()
        for k in out:
            if out[0] != None:
                specnamels.append(out[0])
        dbcs.execute("SELECT `User_ID`, `Username` FROM `Character_Owner` WHERE `Character_ID` = %s;", (j[0]))
        out = dbcs.fetchall()
        for k in out:
            if out[0] != None:
                charownerls.append((k[0], k[1]))
        if j[0] != None:
            if j[0].find(",") != -1:
                j[0] = j[0].replace(",", "")
            dbcs.execute("INSERT INTO `File_Search_Master` (`File_ID`, `Search_Term`) VALUES (%s, %s);", (fileid, f"character_id:{j[0].lower()}"))
        if j[1] != None:
            if j[1].find(",") != -1:
                j[1] = j[1].replace(",", "")
            dbcs.execute("INSERT INTO `File_Search_Master` (`File_ID`, `Search_Term`) VALUES (%s, %s);", (fileid, f"species_id:{j[0].lower()}"))
    for j in charnamels:
        if j.find(",") != -1:
            j = j.replace(",", "")
        dbcs.execute("INSERT INTO `File_Search_Master` (`File_ID`, `Search_Term`) VALUES (%s, %s);", (fileid, f"character:{j[0].lower()}"))
        if j.find(" ") != -1:
            j = j.replace(" ", "_")
            dbcs.execute("INSERT INTO `File_Search_Master` (`File_ID`, `Search_Term`) VALUES (%s, %s);", (fileid, f"character:{j[0].lower()}"))
    #TODO: Continue here with specname

        
        
    

#TODO STILL: Characters (+ID, Name, Aliases, owners, species) & Species (IDs, Aliases,)

# SPECIAL FUNCTION SEARCHES:

# characterid:{Character_ID}
# character_id:{Character_ID}
# charid:{Character_ID}
# char_id:{Character_ID}
# character:{Character_Name}
# char:{Character_Name} (USE ALIASES)
# charname:{Character_Name} (USE ALIASES)
# char_name:{Character_Name} (USE ALIASES)
# characterowner:{Username}
# character_owner:{Username}
# charowner:{Username}
# char_owner:{Username}
# charownerid:{User_ID}
# char_ownerid:{User_ID}
# char_owner_id:{User_ID}
# charowner_id:{User_ID}
# characterownerid:{User_ID}
# character_ownerid:{User_ID}
# character_owner_id:{User_ID}
# characterowner_id:{User_ID}

# species:{Species_Name} (USE ALIASES)
# speciesname:{Species_Name} (USE ALIASES)
# species_name:{Species_Name} (USE ALIASES)
# species_id:{Species_ID}
# speciesid:{Species_ID}




    # TODO: Go through this and fill out for artists, species, campaigns, universes, and tags.