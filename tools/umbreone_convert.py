import mysql.connector
import uuid
import shutil
import json
import os
from datetime import datetime

umbre_user_uuid = "aa1a725e40d142a7b84ad1d0fef481eb"

dbase = mysql.connector.connect(host="127.0.0.1", user="umbreone", password="dYZ7g75WMAJ8CQPO", database="umbreone")
dbcs = dbase.cursor(prepared=True)

try:
    dbcs.execute("CREATE TABLE `Artist_Base` (`Artist_ID` varchar(32) NOT NULL, `User_ID` varchar(32) DEFAULT NULL COMMENT 'User ID of the artist if one exists', `Artist_Name` tinytext NOT NULL, `Artist_Name_Proper` tinytext NOT NULL) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;")
    dbcs.execute("CREATE TABLE `Campaign_Base` (`Campaign_ID` varchar(32) NOT NULL, `Campaign_Name` tinytext NOT NULL, `Campaign_Name_Proper` tinytext NOT NULL) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;")
    dbcs.execute("CREATE TABLE `Campaign_Owner` (`Campaign_ID` varchar(32) DEFAULT NULL, `User_ID` varchar(32) DEFAULT NULL) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='There can be multiple \"owners\" per campaign.';")
    dbcs.execute("CREATE TABLE `Campaign_Universe` (`Campaign_ID` varchar(32) DEFAULT NULL, `Universe_ID` varchar(32) DEFAULT NULL) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='A campaign can take place in multiple universes';")
    dbcs.execute("CREATE TABLE `Character_Alias` (`Character_ID` varchar(32) DEFAULT NULL, `Character_Alias` tinytext NOT NULL, `Character_Alias_Proper` tinytext NOT NULL) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;")
    dbcs.execute("CREATE TABLE `Character_Base` (`Character_ID` varchar(32) NOT NULL, `Character_Name` tinytext DEFAULT NULL COMMENT 'Character name all lowercase', `Character_Name_Proper` tinytext DEFAULT NULL) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;")
    dbcs.execute("CREATE TABLE `Character_Owner` (`Character_ID` varchar(32) DEFAULT NULL, `User_ID` varchar(32) DEFAULT NULL, `Username` tinytext DEFAULT NULL, `Username_Proper` tinytext DEFAULT NULL) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='There can be multiple \"owners\" per character.';")
    dbcs.execute("CREATE TABLE `Character_Species` (`Character_ID` varchar(32) DEFAULT NULL, `Species_ID` varchar(32) NOT NULL) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;")
    dbcs.execute("CREATE TABLE `Files_Artist` (`File_ID` varchar(32) DEFAULT NULL, `Artist_ID` varchar(32) DEFAULT NULL) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='A file can have multiple artists.';")
    dbcs.execute("CREATE TABLE `Files_Base` (`File_ID` varchar(32) NOT NULL, `User_ID` varchar(32) DEFAULT NULL COMMENT 'Uploader''s ID', `File_EXT` tinytext NOT NULL, `Display_Name` tinytext NOT NULL, `Description` longtext DEFAULT NULL, `Rating` enum('s','q','e','') NOT NULL, `Upload_Datetime` datetime NOT NULL DEFAULT current_timestamp(), `Display_Browse` tinyint(1) NOT NULL, `Display_Search` tinyint(1) NOT NULL) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;")
    dbcs.execute("CREATE TABLE `Files_Campaign` (`File_ID` varchar(32) DEFAULT NULL, `Campaign_ID` varchar(32) DEFAULT NULL) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;")
    dbcs.execute("CREATE TABLE `Files_Characters` (`File_ID` varchar(32) DEFAULT NULL, `Character_ID` varchar(32) DEFAULT NULL, `Species_ID` varchar(32) NOT NULL) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;")
    dbcs.execute("CREATE TABLE `Files_Commissioner` (`File_ID` varchar(32) DEFAULT NULL, `User_ID` varchar(32) DEFAULT NULL) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;")
    dbcs.execute("CREATE TABLE `Files_Species` (`File_ID` varchar(32) DEFAULT NULL,`Species_ID` varchar(32) NOT NULL) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;")
    dbcs.execute("CREATE TABLE `Files_Tags` (`File_ID` varchar(32) DEFAULT NULL,`Tag_ID` varchar(32) DEFAULT NULL) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='A file can have multiple tags.';")
    dbcs.execute("CREATE TABLE `Files_Universe` (`File_ID` varchar(32) DEFAULT NULL,`Universe_ID` varchar(32) DEFAULT NULL) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;")
    dbcs.execute("CREATE TABLE `File_Search_Master` (`File_ID` varchar(32) DEFAULT NULL,`Search_Term` tinytext NOT NULL) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;")
    dbcs.execute("CREATE TABLE `Species_Alias` (`Species_ID` varchar(32) NOT NULL,`Species_Alias` tinytext NOT NULL,`Species_Alias_Proper` tinytext NOT NULL) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;")
    dbcs.execute("CREATE TABLE `Species_Base` (`Species_ID` varchar(32) NOT NULL,`Species_Name` tinytext NOT NULL,`Species_Name_Proper` tinytext NOT NULL) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;")
    dbcs.execute("CREATE TABLE `Species_Universe` (`Species_ID` varchar(32) NOT NULL,`Universe_ID` varchar(32) DEFAULT NULL) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;")
    dbcs.execute("CREATE TABLE `Tag_Base` (`Tag_ID` varchar(32) NOT NULL,`Tag` tinytext NOT NULL,`Tag_Proper` tinytext NOT NULL) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;")
    dbcs.execute("CREATE TABLE `Universe_Base` (`Universe_ID` varchar(32) NOT NULL,`Universe_Name` tinytext NOT NULL,`Universe_Name_Proper` tinytext NOT NULL) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;")
    dbcs.execute("CREATE TABLE `Universe_Owner` (`Universe_ID` varchar(32) DEFAULT NULL,`User_ID` varchar(32) DEFAULT NULL) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='A universe can have multiple \"owners\".';")
    dbcs.execute("CREATE TABLE `User_Base` (`User_ID` varchar(32) NOT NULL,`Username` tinytext NOT NULL,`Username_Proper` tinytext NOT NULL,`Join_Datetime` datetime NOT NULL DEFAULT current_timestamp()) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;")
    dbcs.execute("CREATE TABLE `User_DiscordLink` (`User_ID` varchar(32) DEFAULT NULL,`Discord_ID` bigint(20) UNSIGNED DEFAULT NULL) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;")
    dbcs.execute("ALTER TABLE `Artist_Base` ADD PRIMARY KEY (`Artist_ID`);")
    dbcs.execute("ALTER TABLE `Campaign_Base` ADD PRIMARY KEY (`Campaign_ID`);")
    dbcs.execute("ALTER TABLE `Character_Base` ADD PRIMARY KEY (`Character_ID`);")
    dbcs.execute("ALTER TABLE `Files_Base` ADD PRIMARY KEY (`File_ID`);")
    dbcs.execute("ALTER TABLE `Species_Base` ADD PRIMARY KEY (`Species_ID`);")
    dbcs.execute("ALTER TABLE `Tag_Base` ADD PRIMARY KEY (`Tag_ID`);")
    dbcs.execute("ALTER TABLE `Universe_Base` ADD PRIMARY KEY (`Universe_ID`);")
    dbcs.execute("ALTER TABLE `User_Base` ADD PRIMARY KEY (`User_ID`);")
    dbase.commit()
except mysql.connector.errors.InterfaceError as exception:
    pass
print("Database tables created.")
dbcs.execute("SELECT * FROM `files` WHERE 1;")
out = dbcs.fetchall()
for i in out:
    break # NOTE: Remove this line if you don't want this code block skipped.
    oldfilename = f"{str(i[0])}.{str(i[1])}"
    newfileid = uuid.uuid4().hex
    newfilename = f"{newfileid}.{str(i[1])}"
    try:
        shutil.copy(f"/web/umbreone/rsc/file/{oldfilename}", f"/web/umbreone/rsc/file/full/{newfilename}")
    except FileNotFoundError as exception:
        continue
    dbcs.execute("INSERT INTO `Files_Base`(`File_ID`, `User_ID`, `File_EXT`, `Display_Name`, `Description`, `Rating`, `Upload_Datetime`, `Display_Browse`, `Display_Search`) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s);", (newfileid, umbre_user_uuid, i[1], i[2], None, i[3], i[6], 1, 1))
    dbcs.execute("INSERT INTO `Files_Umbreone_Old_ID`(`New_File_ID`, `Old_File_ID`) VALUES (%s, %s);", (newfileid, i[0]))
    dbase.commit()
    os.remove(f"/web/umbreone/rsc/file/{oldfilename}")
dbcs.execute("SELECT * FROM `files` INNER JOIN `Files_Umbreone_Old_ID` ON files.Internal_ID = Files_Umbreone_Old_ID.Old_File_ID WHERE 1;")
out = dbcs.fetchall() # The FOLLOWING SECTION CONVERTS ARTISTS
for i in out:
    break # NOTE: Remove this line if you don't want this code block skipped.
    artistuserid = None
    if i[4] == "epic umbreon":
        artistname = "epic umbreon"
        artistnameproper = "Epic Umbreon"
        artistuserid = umbre_user_uuid
    elif i[4] == "drajjin":
        artistname = "anonymous"
        artistnameproper = "Anonymous"
    elif i[4] == "potoo brigham":
        artistname = "potoo brigham"
        artistnameproper = "Potoo brigham"
    elif i[4] == "pikacshu":
        artistname = "pikacshu"
        artistnameproper = "Pikacshu"
    elif i[4] == "punkdrake":
        artistname = i[4]
        artistnameproper = "Punkdrake"
    elif i[4] == "sybil lumara":
        artistname = i[4]
        artistnameproper = "Sybil lumara"
    elif i[4] == "newputty":
        artistname = i[4]
        artistnameproper = "Newputty"
    elif i[4] == "brackets":
        artistname = i[4]
        artistnameproper = "Brackets"
    else:
        artistname = i[4]
        artistnameproper = i[4]
    dbcs.execute("SELECT * FROM `Artist_Base` WHERE `Artist_Name` = %s LIMIT 1;", (artistname,))
    artistuuid = None
    if dbcs.rowcount == -1:
        artistuuid = str(uuid.uuid4().hex)
        dbcs.execute("INSERT INTO `Artist_Base`(`Artist_ID`, `User_ID`, `Artist_Name`, `Artist_Name_Proper`) VALUES (%s, %s, %s, %s);", (artistuuid, artistuserid, artistname, artistnameproper))
        out = dbcs.fetchone()
        del out
    else:
        out = dbcs.fetchone()
        if out == None:
            artistuuid = str(uuid.uuid4().hex)
            dbcs.execute("INSERT INTO `Artist_Base`(`Artist_ID`, `User_ID`, `Artist_Name`, `Artist_Name_Proper`) VALUES (%s, %s, %s, %s);", (artistuuid, artistuserid, artistname, artistnameproper))
        else:
            artistuuid = out[0]
        del out
    dbcs.execute("INSERT INTO `Files_Artist`(`File_ID`, `Artist_ID`) VALUES (%s, %s);", (i[7], artistuuid))
    dbase.commit()
    print(i)
# NOTE: THE FOLLOWING SECTION CONVERTS CHARACTERS AND SPECIES
# dbcs.execute("TRUNCATE `Character_Base`;")
# dbcs.execute("TRUNCATE `Character_Owner`;")
# dbcs.execute("TRUNCATE `Character_Species`;")
# dbcs.execute("TRUNCATE `Species_Base`;")
# dbase.commit()
dbcs.execute("SELECT `File_ID`, `Tag` From `tags` WHERE 1;")
out = dbcs.fetchall()
for i in out:
    oldfileid = i[0]
    dbcs.execute("SELECT `New_File_ID` FROM `Files_Umbreone_Old_ID` WHERE `Old_File_ID` = %s LIMIT 1;", (oldfileid,))
    out = dbcs.fetchone()
    if out == None:
        continue
    newfileid = out[0]

    # break # NOTE: COMMENT THIS OUT IF YOU WANT TO USE THIS SECTION AGAIN, AND THEN COMMENT BACK IN THE STUFF ABOVE THIS LINE (THE TRUNCATE STATEMENTS)
    # Your Tuple looks like this: (Old File ID, Tag)
    tagcategory = "tag"
    characterowner = "Epic Umbreon"
    characterspecies = ["Unknown"]
    charactercampaign = None
    name = i[1]
    nameproper = i[1]
    characteraliases = None
    speciesaliases = None
    speciesuniverses = None # List of dicts: {"Name": "Universe Name", "Owner": "Universe Owner"}
    characterspeciesuniverse = [{"Universe": [{"n": "Pokémon", "o": "The Pokémon Company"}, {"n": "Polyverse", "o": "Epic Umbreon"}, {"n": "Macinaverse", "o": "MaxisOp"}]}]
    campaignuniverse = None
    campaignowner = None
    universeowner = None
    if i[1] == "zuko":
        tagcategory = "character"
        characterspecies = ["Weavile"]
        nameproper = "Zuko"
    elif i[1] == "zikki":
        tagcategory = "character"
        characterspecies = ["Foxfolk"]
        characterspeciesuniverse = ["Ascania"]
        nameproper = "Zikki"
        characterspeciesuniverse = [{"Universe": [{"n": "Ascania", "o": "LunarEcklipse"}]}]
    elif i[1] == "veronica":
        tagcategory = "character"
        nameproper = "Veronica"
        characterspecies = ["Absol"]
    elif i[1] == "wanda":
        tagcategory = "character"
        nameproper = "Wanda"
        characterspecies = ["Ampharos"]
    elif i[1] == "susan":
        tagcategory = "character"
        nameproper = "Susan"
        characterspecies = ["Audino"]
    elif i[1] == "5t3v3n":
        tagcategory = "character"
        nameproper = "5T3V3N"
        characterspecies = ["Porygon-Z"]
        characteraliases = ["Steven"]
    elif i[1] == "sharon":
        tagcategory = "character"
        nameproper = "Sharon"
        characterspecies = ["Rapidash", "Rapidash (Galarian)"]
    elif i[1] == "raymond":
        tagcategory = "character"
        nameproper = "Raymond"
        characterspecies = ["Smeargle"]
    elif i[1] == "flamepaw":
        tagcategory = "character"
        nameproper = "Flamepaw"
        characterspecies = ["Pandaren"]
    elif i[1] == "laurie":
        tagcategory = "character"
        characterspecies = ["Lopunny"]
        nameproper = "Laurie"
    elif i[1] == "fyta":
        tagcategory = "character"
        nameproper = "Fyta"
        characterspecies = ["Tauren"]
    elif i[1] == "mark":
        tagcategory = "character"
        nameproper = "Mark"
        characterspecies = ["Machamp"]
    elif i[1] == "jill":
        tagcategory = "character"
        characterspecies = ["Tsareena"]
        nameproper = "Jill"
    elif i[1] == "jessica":
        tagcategory = "character"
        characterspecies = ["Primarina"]
        nameproper = "Jessica"
    elif i[1] == "ozlac":
        tagcategory = "character"
        characterspecies = ["Dry Bones"]
        nameproper = "Ozlac"
    elif i[1] == "hideo":
        tagcategory = "character"
        characterspecies = ["Trevenant"]
        nameproper = "Hideo"
    elif i[1] == "brian":
        tagcategory = "character"
        characterspecies = ["Marowak", "Marowak (Kantonian)"]
        nameproper = "Brian"
    elif i[1] == "elijah":
        tagcategory = "character"
        characterspecies = ["Honchkrow"]
        nameproper = "Elijah"
    elif i[1] == "violet":
        tagcategory = "character"
        nameproper = "Violet"
        characterspecies = ["Mismagius"]
    elif i[1] == "blip":
        tagcategory = "character"
        nameproper = "Blip"
        characterspecies = ["Rotom", "Rotom (Rotomdex)"]
    elif i[1] == "glacia":
        tagcategory = "character"
        characterspecies = ["Glaceon", "Eevelution"]
        nameproper = "Glacia"
    elif i[1] == "francine":
        tagcategory = "character"
        characterspecies = ["Altaria"]
        nameproper = "Francine"
    elif i[1] == "seijin":
        tagcategory = "character"
        nameproper = "Seijin"
        characterspecies = ["Gallade"]
    elif i[1] == "umbra":
        tagcategory = "character"
        nameproper = "Umbra"
        characterspecies = ["Umbreon", "Eeveelution"]
    elif i[1] == "tara (maxis.op)":
        tagcategory = "character"
        name = "tara"
        nameproper = "Tara"
        characterspecies = ["Staraptor"]
        characterowner = "MaxisOp"
    elif i[1] == "captain (that sprite)":
        tagcategory = "character"
        name = "captain"
        nameproper = "Captain"
        characterowner = "That Sprite"
        characterspecies = ["Hawlucha"]
    elif i[1] == "jody (that sprite)":
        tagcategory = "character"
        name = "jody"
        nameproper = "Jody"
        characterowner = "That Sprite"
        characterspecies = ["Gardevoir"]
    elif i[1] == "reshad (treann)":
        tagcategory = "character"
        name = "reshad"
        nameproper = "Reshad"
        characterowner = "Nightfury Treann"
        characterspecies = ["Blaziken"]
    elif i[1] == "richter (sammun)":
        tagcategory = "character"
        name = "richter"
        nameproper = "Richter"
        characterowner = "Sammun"
        characterspecies = ["Sylveon", "Eeveelution"]
    elif i[1] == "sophie (unknown)":
        tagcategory = "character"
        name = "sophie"
        nameproper = "Sophie"
        characterowner = "Unknown"
        characterspecies = ["Gardevoir"]
    elif i[1] == "fang":
        tagcategory = "character"
        name = "fang"
        nameproper = "Fang"
        characterspecies = ["Lycanroc", "Lycanroc (Midnight)"]
    elif i[1] == "jess":
        tagcategory = "character"
        nameproper = "Jess"
        characterspecies = ["Toxtricity", "Toxtricity (Amped)"]
    elif i[1] == "leyna (eliktroniq)":
        tagcategory = "character"
        name = "leyna"
        nameproper = "Leyna"
        characterowner = "Eliktroniq"
        characterspecies = ["Weavile"]
    elif i[1] == "leon":
        tagcategory = "character"
        nameproper = "Leon"
        characterspecies = ["Toxtricity", "Toxtricity (Low Key)"]
    elif i[1] == "nancy":
        tagcategory = "character"
        nameproper = "Nancy"
        characterspecies = ["Floatzel"]
    elif i[1] == "chip":
        tagcategory = "character"
        nameproper = "Chip"
        characterspecies = ["Cinderace"]
    elif i[1] == "pomo":
        tagcategory = "character"
        nameproper = "Pomo"
        characterspecies = ["Emboar"]
    elif i[1] == "max":
        tagcategory = "character"
        nameproper = "Max"
        characterspecies = ["Sharpedo"]
    elif i[1] == "gabby":
        tagcategory = "character"
        nameproper = "Gabby"
        characterspecies = ["Salazzle"]
    elif i[1] == "elizabeth":
        tagcategory = "character"
        nameproper = "Elizabeth"
        characterspecies = ["Gardevoir"]
    elif i[1] == "jack (oc)":
        tagcategory = "character"
        nameproper = "Jack"
        characterspecies = ["Gogoat"]
    elif i[1] == "frank":
        tagcategory = "character"
        nameproper = "Frank"
        characterspecies = ["Dewott"]
    elif i[1] == "clover":
        tagcategory = "character"
        nameproper = "Clover"
        characterspecies = ["Decidueye"]
    elif i[1] == "bruce":
        tagcategory = "character"
        nameproper = "Bruce"
        characterspecies = ["Blastoise"]
    elif i[1] == "blaze (oc)":
        tagcategory = "character"
        nameproper = "Blaze"
        characterspecies = ["Delphox"]
    elif i[1] == "cinder":
        tagcategory = "character"
        nameproper = "Cinder"
        characterspecies = ["Braixen"]
    elif i[1] == "ryujo":
        tagcategory = "character"
        nameproper = "Ryujo"
        characterspecies = ["Staraptor"]
    elif i[1] == "lucy":
        tagcategory = "character"
        nameproper = "Lucy"
        characterspecies = ["Indeedee", "Indeedee (Female)"]
    elif i[1] == "lucas":
        tagcategory = "character"
        nameproper = "Lucas"
        characterspecies = ["Indeedee", "Indeedee (Male)"]
    elif i[1] == "sylar":
        tagcategory = "character"
        nameproper = "Sylar"
        characterspecies = ["Greninja"]
    elif i[1] == "rion":
        tagcategory = "character"
        nameproper = "Rion"
        characterspecies = ["Inteleon"]
    elif i[1] == "unnamed mafia pangoro":
        tagcategory = "character"
        nameproper = "Unnamed Mafia Pangoro"
        characterspecies = ["Pangoro"]
    elif i[1]  == "alexander":
        tagcategory = "character"
        nameproper = "Alexander"
        characterspecies = ["Charizard"]
    elif i[1] == "carrie":
        tagcategory = "character"
        nameproper = "Carrie"
        characterspecies = ["Mandibuzz"]
    elif i[1] == "hannah":
        tagcategory = "character"
        nameproper = "Hannah"
        characterspecies = ["Girafarig"]
    elif i[1] == "munch":
        tagcategory = "character"
        nameproper = "Munch"
        characterspecies = ["Feraligatr"]
    elif i[1] == "james (eliktroniq)":
        tagcategory = "character"
        name = "james"
        nameproper = "James"
        characterowner = "Eliktroniq"
        characterspecies = ["Mawile"]
        characteraliases = ["Dearie", "Dear"]
    elif i[1] == "samba":
        tagcategory = "character"
        nameproper = "Samba"
        characterspecies = ["Maractus"]
    elif i[1] == "zinnia":
        nameproper = "Zinnia"
        tagcategory = "character"
        characterspecies = ["Lurantis"]
    elif i[1] == "tyler":
        tagcategory = "character"
        nameproper = "Tyler"
        characterspecies = ["Furfrou", "Furfrou (Dandy)"]
    elif i[1] == "jake":
        tagcategory = "character"
        nameproper = "Jake"
        characterspecies = ["Blaziken"]
    elif i[1] == "athyra":
        tagcategory = "character"
        nameproper = "Athyra"
        characterspecies = ["Dragonborn", "Wyrmkin", "Wyrmkin (Halfwyrm)"]
        characterspeciesuniverse = [{"Name": "Dragonborn", "Universe": [{"n": "Forgotten Realms", "o": "Wizards of the Coast"},]}, {"Name": "Wyrmkin", "Universe": [{"n": "Ascania", "o": "LunarEcklipse"}], "Aliases": [{"n": "Dragonfolk"}]}, {"Name": "Wyrmkin (Halfwyrm)", "Universe": [{"n": "Ascania", "o": "LunarEcklipse"}], "Aliases": [{"n": "Halfwyrm"}, {"n": "Dragonfolk"}]}]
        characteraliases = ["Athy"]
    elif i[1] == "noxia venomtalon":
        tagcategory = "character"
        nameproper = "Noxia Venomtalon"
        characteraliases = ["Noxia", "Venomtalon"]
        characterspecies = ["Kenku", "Tengu", "Birdfolk"]
        characterspeciesuniverse = [{"Name": "Birdfolk", "Universe": [{"n": "Ascania", "o": "LunarEcklipse"}], "Aliases": [{"n": "Crowfolk"}]}, {"Name": "Kenku", "Universe": [{"n": "Forgotten Realms", "o": "Wizards of the Coast"}, {"n": "Sammunverse", "o": "Sammun"}]}, {"Name": "Tengu", "Universe": [{"n": "Golarion", "o": "Paizo"}]}]
    elif i[1] == "briallan (nightskyflyhigh)":
        tagcategory = "character"
        name = "briallan"
        nameproper = "Briallan"
        characterowner = "NightSkyFlyHigh"
        characterspecies = ["Lurantis"]
    elif i[1] == "spyro":
        tagcategory = "character"
        name = "spyro"
        nameproper = "Spyro"
        characteraliases = ["Spyro the Dragon"]
        characterowner = "Activision"
        characterspecies = ["Dragon"]
        characterspeciesuniverse = [{"Universe": [{"n": "Spyro the Dragon", "o": "Activision"}]}]
    elif i[1] == "yoshi":
        tagcategory = "character"
        name = "yoshi"
        nameproper = "Yoshi"
        characterowner = "Nintendo"
        characteraliases = ["Super Yoshi"]
        characterspecies = ["Yoshi", "Dinosaur"]
        characterspeciesuniverse = [{"Name": "Yoshi", "Universe": [{"n": "Super Mario", "o": "Nintendo"}]}]
    elif i[1] == "boom boom":
        tagcategory = "character"
        name = "boom boom"
        nameproper = "Boom Boom"
        characterowner = "Nintendo"
        characteraliases = ["Boom-Boom", "Bum Bum", "Bum-Bum"]
        characterspecies = ["Koopa", "Turtle"]
        characterspeciesuniverse = [{"Name": "Koopa", "Universe": [{"n": "Super Mario", "o": "Nintendo"}]}]
    elif i[1] == "larry":
        tagcategory = "character"
        nameproper = "Larry"
        characterowner = "Nintendo"
        characteraliases = ["Koopaling", "Koopalings"]
        characterspecies = ["Koopa", "Turtle"]
        characterspeciesuniverse = [{"Name": "Koopa", "Universe": [{"n": "Super Mario", "o": "Nintendo"}]}]
    elif i[1] == "lemmy":
        tagcategory = "character"
        nameproper = "Lemmy"
        characterowner = "Nintendo"
        characteraliases = ["Koopaling", "Koopalings"]
        characterspecies = ["Koopa", "Turtle"]
        characterspeciesuniverse = [{"Name": "Koopa", "Universe": [{"n": "Super Mario", "o": "Nintendo"}]}]
    elif i[1] == "wendy":
        tagcategory = "character"
        nameproper = "Wendy"
        characterowner = "Nintendo"
        characteraliases = ["Koopaling", "Koopalings"]
        characterspecies = ["Koopa", "Turtle"]
        characterspeciesuniverse = [{"Name": "Koopa", "Universe": [{"n": "Super Mario", "o": "Nintendo"}]}]
    elif i[1] == "iggy":
        tagcategory = "character"
        nameproper = "Iggy"
        characterowner = "Nintendo"
        characteraliases = ["Koopaling", "Koopalings"]
        characterspecies = ["Koopa", "Turtle"]
        characterspeciesuniverse = [{"Name": "Koopa", "Universe": [{"n": "Super Mario", "o": "Nintendo"}]}]
    elif i[1] == "ludwig":
        tagcategory = "character"
        nameproper = "Ludwig"
        characterowner = "Nintendo"
        characteraliases = ["Koopaling", "Koopalings"]
        characterspecies = ["Koopa", "Turtle"]
        characterspeciesuniverse = [{"Name": "Koopa", "Universe": [{"n": "Super Mario", "o": "Nintendo"}]}]
    elif i[1] == "morton":
        tagcategory = "character"
        nameproper = "Morton"
        characterowner = "Nintendo"
        characteraliases = ["Koopaling", "Koopalings"]
        characterspecies = ["Koopa", "Turtle"]
        characterspeciesuniverse = [{"Name": "Koopa", "Universe": [{"n": "Super Mario", "o": "Nintendo"}]}]
    elif i[1] == "roy":
        tagcategory = "character"
        nameproper = "Roy"
        characterowner = "Nintendo"
        characteraliases = ["Koopaling", "Koopalings"]
        characterspecies = ["Koopa", "Turtle"]
        characterspeciesuniverse = [{"Name": "Koopa", "Universe": [{"n": "Super Mario", "o": "Nintendo"}]}]
    elif i[1] == "fox mccloud":
        tagcategory = "character"
        nameproper = "Fox McCloud"
        characterowner = "Nintendo"
        characteraliases = ["Fox", "Star Fox", "Foxie", "Fox McCloud Jr", "Fox McCloud Junior", "Fox McCloud Jr."]
        characterspecies = ["Red Fox", "Fox"]
        characterspeciesuniverse = [{"Universe": [{"n": "Star Fox", "o": "Nintendo"}]}]
    elif i[1] == "wolf o'donnell":
        tagcategory = "character"
        nameproper = "Wolf O'Donnell"
        characterowner = "Nintendo"
        characteraliases = ["Star Wolf", "Lord O'Donnell", "Cap'n Wolf"]
        characterspecies = ["Wolf"]
        characterspeciesuniverse = [{"Universe": [{"n": "Star Fox", "o": "Nintendo"}]}]
    elif i[1] == "blaze (sonic)":
        tagcategory = "character"
        name = "blaze the cat"
        nameproper = "Blaze the Cat"
        characterowner = "Sega"
        characteraliases = ["Blaze", "Princess Blaze"]
        characterspecies = ["Cat"]
        characterspeciesuniverse = [{"Universe": [{"n": "Sonic the Hedgehog", "o": "Sega"}]}]
    elif i[1] == "jack (chameleon twist)":
        tagcategory = "character"
        name = "jack"
        nameproper = "Jack"
        characterowner = "Japan System Supply"
        characterspecies = ["Chameleon"]
        characterspeciesuniverse = [{"Universe": [{"n": "Chameleon Twist", "o": "Japan System Supply"}]}]
    elif i[1] == "anubis":
        tagcategory = "character"
        nameproper = "Anubis"
        characterowner = "Public Domain"
        characterspecies = ["Jackal"]
        characterspeciesuniverse = [{"Universe": [{"n": "Egyptian Mythology", "o": "Public Domain"}]}]
    elif i[1] == "tails":
        tagcategory = "character"
        nameproper = "Tails"
        characterowner = "Sega"
        characterspecies = ["Fox"]
        characteraliases = ["Miles Prower", "Miles \"Tails\" Prower", "Two-Tailed Fox"]
        characterspeciesuniverse = [{"Universe": [{"n": "Sonic the Hedgehog", "o": "Sega"}]}]
    elif i[1] == "silver":
        tagcategory = "character"
        name = "silver the hedgehog"
        nameproper = "Silver the Hedgehog"
        characterowner = "Sega"
        characteraliases = ["Silver", "Psychic Hedgehog", "Silver Boy"]
        characterspecies = ["Hedgehog"]
        characterspeciesuniverse = [{"Universe": [{"n": "Sonic the Hedgehog", "o": "Sega"}]}]
    elif i[1] == "sobek":
        tagcategory = "character"
        nameproper = "Sobek"
        characterowner = "Public Domain"
        characteraliases = ["Sobki", "Ⲥⲟⲩⲕ", "Souk"]
        characterspecies = ["Crocodile"]
        characterspeciesuniverse = [{"Universe": [{"n": "Egyptian Mythology", "o": "Public Domain"}]}]
    elif i[1] == "kukulkan":
        tagcategory = "character"
        nameproper = "Kukulkan"
        characterowner = "Public Domain"
        characteraliases = ["K'uk'ulkan"]
        characterspecies = ["Snake", "Feathered Serpent"]
        characterspeciesuniverse = [{"Universe": [{"n": "Mesoamerican Mythology", "o": "Public Domain"}]}]
    elif i[1] == "khepri":
        tagcategory = "character"
        nameproper = "Khepri"
        characterowner = "Public Domain"
        characterspecies = ["Scarab"]
        characterspeciesuniverse = [{"Universe": [{"n": "Egyptian Mythology", "o": "Public Domain"}]}]
    elif i[1] == "klonoa":
        tagcategory = "character"
        nameproper = "Klonoa"
        characterowner = "Bandai Namco"
        characterspecies = ["Chimera"]
        characterspeciesuniverse = [{"Universe": [{"n": "Klonoa", "o": "Bandai Namco"}]}]
    elif i[1] == "fenrir":
        tagcategory = "character"
        nameproper = "Fenrir"
        characterowner = "Public Domain"
        characterspecies = ["Wolf"]
        characterspeciesuniverse = [{"Universe": [{"n": "Norse Mythology", "o": "Public Domain"}]}]
    elif i[1] == "thorth":
        tagcategory = "character"
        nameproper = "Thorth"
        characterowner = "Public Domain"
        characterspecies = ["Unknown"]
        characterspeciesuniverse = [{"Universe": [{"n": "Norse Mythology", "o": "Public Domain"}]}]
    elif i[1] == "master hand":
        tagcategory = "character"
        nameproper = "Master Hand"
        characterowner = "Nintendo"
        characterspecies = ["Hand"]
        characterspeciesuniverse = [{"Universe": [{"n": "Super Smash Bros.", "o": "Nintendo"}]}]
    elif i[1] == "dry bowser":
        tagcategory = "character"
        nameproper = "Dry Bowser"
        characterowner = "Nintendo"
        characterspecies = ["Koopa", "Turtle"]
        characterspeciesuniverse = [{"Name": "Koopa", "Universe": [{"n": "Super Mario", "o": "Nintendo"}]}]
    elif i[1] == "foxfolk":
        tagcategory = "species"
        nameproper = "Foxfolk"
        speciesaliases = ["Kitsune"]
        speciesuniverses = [{"Name": "Ascania", "Owner": "LunarEcklipse"}]
    elif i[1] == "pandaren":
        tagcategory = "species"
        nameproper = "Pandaren"
        speciesuniverses = [{"Name": "Azeroth", "Owner": "Activision Blizzard"}]
    elif i[1] == "tauren":
        tagcategory = "species"
        nameproper = "Tauren"
        speciesuniverses = [{"Name": "Azeroth", "Owner": "Activision Blizzard"}]
    elif i[1] == "renamon":
        tagcategory = "species"
        nameproper = "Renamon"
        speciesuniverse = [{"Name": "Digimon", "Owner": "Bandai Namco"}]
    elif i[1] == "dry bones":
        tagcategory = "species"
        nameproper = "Dry Bones"
        speciesuniverse = [{"Name": "Super Mario", "Owner": "Nintendo"}]
    elif i[1] == "flamedramon":
        tagcategory = "species"
        nameproper = "Flamedramon"
        speciesuniverse = [{"Name": "Digimon", "Owner": "Bandai Namco"}]
    elif i[1] == "guilmon":
        tagcategory = "species"
        nameproper = "Guilmon"
        speciesuniverse = [{"Name": "Digimon", "Owner": "Bandai Namco"}]
    elif i[1] == "impmon":
        tagcategory = "species"
        nameproper = "Impmon"
        speciesuniverse = [{"Name": "Digimon", "Owner": "Bandai Namco"}]
    elif i[1] == "warbear":
        tagcategory = "species"
        nameproper = "Warbear"
        speciesuniverse = [{"Name": "Summoners War", "Owner": "Com2uS"}]
    elif i[1] == "bearman":
        tagcategory = "species"
        nameproper = "Bearman"
        speciesuniverse = [{"Name": "Summoners War", "Owner": "Com2uS"}]
    elif i[1] == "golem (summoners war)":
        tagcategory = "species"
        name = "golem"
        nameproper = "Golem"
        speciesuniverse = [{"Name": "Summoners War", "Owner": "Com2uS"}]
    elif i[1] == "yoshi":
        tagcategory = "species"
        nameproper = "Yoshi"
        speciesuniverse = [{"Name": "Super Mario", "Owner": "Nintendo"}]
    elif i[1] == "koopa troopa":
        tagcategory = "species"
        nameproper = "Koopa Troopa"
        speciesuniverse = [{"Name": "Super Mario", "Owner": "Nintendo"}]
    elif i[1] == "royal ludroth":
        tagcategory = "species"
        nameproper = "Royal Ludroth"
        speciesuniverse = [{"Name": "Monster Hunter", "Owner": "Capcom"}]
    elif i[1] == "uragaan":
        tagcategory = "species"
        nameproper = "Uragaan"
        speciesuniverse = [{"Name": "Monster Hunter", "Owner": "Capcom"}]
    elif i[1] == "thwomp":
        tagcategory = "species"
        nameproper = "Thwomp"
        speciesuniverse = [{"Name": "Super Mario", "Owner": "Nintendo"}]
    elif i[1] == "barroth":
        tagcategory = "species"
        nameproper = "Barroth"
        speciesuniverse = [{"Name": "Monster Hunter", "Owner": "Capcom"}]
    elif i[1] == "great jaggi":
        tagcategory = "species"
        nameproper = "Great Jaggi"
        speciesaliases = ["G. Jaggi", "G Jaggi"]
        speciesuniverse = [{"Name": "Monster Hunter", "Owner": "Capcom"}]
    elif i[1] == "dragonborn":
        tagcategory = "species"
        nameproper = "Dragonborn"
        speciesuniverse = [{"Name": "Forgotten Realms", "Owner": "Wizards of the Coast"}]
    elif i[1] == "kenku":
        tagcategory = "species"
        nameproper = "Kenku"
        speciesuniverse = [{"Name": "Forgotten Realms", "Owner": "Wizards of the Coast"}]
    elif i[1] == "tox box":
        tagcategory = "species"
        nameproper = "Tox Box"
        speciesuniverse = [{"Name": "Super Mario", "Owner": "Nintendo"}]
    elif i[1] == "rathalos":
        tagcategory = "species"
        nameproper = "Rathalos"
        speciesuniverse = [{"Name": "Monster Hunter", "Owner": "Capcom"}]
    elif i[1] == "project thumper":
        tagcategory = "campaign"
        nameproper = "Project Thumper"
        campaignowner = ["LunarEcklipse"]
        campaignuniverse = ["Ascania"]
    elif i[1] == "sleeping in class":
        tagcategory = "campaign"
        nameproper = "Sleeping in Class"
        campaignowner = ["Epic Umbreon", "Sammun"]
        campaignuniverse = ["Polyverse"]
    elif i[1] == "a world above":
        tagcategory = "campaign"
        nameproper = "A World Above"
        campaignowner = ["LunarEcklipse"]
        campaignuniverse = ["Ascania"]
    elif i[1] == "okarthel":
        tagcategory = "campaign"
        nameproper = "Okarthel"
        campaignowner = ["Epic Umbreon"]
        campaignuniverse = ["Polyverse"]
    elif i[1] == "ardent dawn":
        tagcategory = "campaign"
        nameproper = "Ardent Dawn"
        campaignowner = ["MaxisOp"]
        campaignuniverse = ["Macinaverse"]
    elif i[1] == "strathmore of astrium":
        tagcategory = "campaign"
        nameproper = "Strathmore of Astrium"
        campaignowner = ["That Sprite"]
        campaignuniverse = ["Macinaverse"]
    elif i[1] == "season turning grey":
        tagcategory = "campaign"
        nameproper = "Season Turning Grey"
        campaignowner = ["That Sprite"]
        campaignuniverse = ["Macinaverse"]
    elif i[1] == "darkness campaign":
        tagcategory = "campaign"
        name = "darkness"
        nameproper = "darkness"
        campaignowner = ["That Sprite"]
        campaignuniverse = ["Macinaverse"]
    elif i[1] == "darkness returns":
        tagcategory = "campaign"
        nameproper = "Darkness Returns"
        campaignowner = ["That Sprite"]
        campaignuniverse = ["Macinaverse"]
    elif i[1] == "dwellers of the night":
        tagcategory = "campaign"
        nameproper = "Dwellers of the Night"
        campaignowner = ["zLamp"]
        campaignuniverse = ["Lampverse"]
    elif i[1] == "ascania" or i[1] == "lunarverse":
        tagcategory = "universe"
        name = "ascania"
        nameproper = "Ascania"
        universeowner = ["LunarEcklipse"]
    elif i[1] == "macina" or i[1] == "macinaverse":
        tagcategory = "universe"
        name = "macinaverse"
        nameproper = "macinaverse"
        universeowner = ["MaxisOp"]
    if tagcategory == "species":
        continue # Comment this out if you want this block to run!
        dbcs.execute("SELECT `Species_ID` FROM `Species_Base` WHERE `Species_Name` = %s LIMIT 1;", (name,))
        speccheck = dbcs.fetchone()
        species_id = None
        universe_id = None
        universe_owner_id = None
        if speccheck == None:
            species_id = str(uuid.uuid4().hex)
            dbcs.execute("INSERT INTO `Species_Base`(`Species_ID`, `Species_Name`, `Species_Name_Proper`) VALUES (%s, %s, %s);", (species_id, name, nameproper))
            dbcs.execute("INSERT INTO `Species_Alias`(`Species_ID`, `Species_Alias`, `Species_Alias_Proper`) VALUES (%s, %s, %s);", (species_id, name, nameproper))
            if speciesaliases != None:
                for k in speciesaliases:
                    dbcs.execute("INSERT INTO `Species_Alias`(`Species_ID`, `Species_Alias`, `Species_Alias_Proper`) VALUES (%s, %s, %s);", (species_id, k.lower(), k))
            for k in speciesuniverse:
                dbcs.execute("SELECT `Universe_ID` FROM `Universe_Base` WHERE `Universe_Name` = %s LIMIT 1;", (k["Name"].lower(),))
                unicheck = dbcs.fetchone()
                if unicheck == None:
                    universe_id = str(uuid.uuid4().hex)
                    dbcs.execute("INSERT INTO `Universe_Base`(`Universe_ID`, `Universe_Name`, `Universe_Name_Proper`) VALUES (%s, %s, %s);", (universe_id, k["Name"].lower(), k["Name"]))
                    dbcs.execute("SELECT `User_ID` FROM `User_Base` WHERE `Username` = %s LIMIT 1;", (k["Owner"].lower(),))
                    usercheck = dbcs.fetchone()
                    if usercheck == None:
                        universe_owner_id = str(uuid.uuid4().hex)
                        dbcs.execute("INSERT INTO `User_Base`(`User_ID`, `Username`, `Username_Proper`, `Join_Datetime`) VALUES (%s, %s, %s, %s);", (universe_owner_id, k["Owner"].lower(), k["Owner"], datetime.now()))
                    else:
                        universe_owner_id = usercheck[0]
                    dbcs.execute("INSERT INTO `Universe_Owner`(`Universe_ID`, `User_ID`) VALUES (%s, %s);", (universe_id, universe_owner_id))
                else:
                    universe_id = unicheck[0]
                if universe_owner_id == None:
                    dbcs.execute("SELECT `User_ID` FROM `User_Base` WHERE `Username` = %s LIMIT 1;", (k["Owner"].lower(),))
                    usercheck = dbcs.fetchone()
                    if usercheck == None:
                        universe_owner_id = str(uuid.uuid4().hex)
                        dbcs.execute("INSERT INTO `User_Base`(`User_ID`, `Username`, `Username_Proper`, `Join_Datetime`) VALUES (%s, %s, %s, %s);", (universe_owner_id, k["Owner"].lower(), k["Owner"], datetime.now()))
                    else:
                        universe_owner_id = usercheck[0]
                if universe_id == None:
                    print("The universe ID never got made. This is an error!")
                    raise
                elif universe_owner_id == None:
                    print("The universe owner ID never got made. This is an error!")
                    raise
                dbcs.execute("SELECT `Universe_ID`, `User_ID` FROM `Universe_Owner` WHERE `Universe_ID` = %s AND `User_ID` = %s LIMIT 1;", (universe_id, universe_owner_id)) # Check still if the universe-owner link exists
                uniownercheck = dbcs.fetchone()
                if uniownercheck == None:
                    dbcs.execute("INSERT INTO `Universe_Owner`(`Universe_ID`, `User_ID`) VALUES (%s, %s);", (universe_id, universe_owner_id))
                dbcs.execute("SELECT * FROM `Species_Universe` WHERE `Species_ID` = %s AND `Universe_ID` = %s LIMIT 1;", (species_id, universe_id))
                specunicheck = dbcs.fetchone() # This will probably never fire but it's a safety check regardless.
                if specunicheck == None:
                    dbcs.execute("INSERT INTO `Species_Universe`(`Species_ID`, `Universe_ID`) VALUES (%s, %s);", (species_id, universe_id))
                dbase.commit()
        else:
            species_id = speccheck[0]
            if speciesaliases != None:
                dbcs.execute("SELECT * FROM `Species_Alias` WHERE `Species_ID` = %s AND `Species_Alias` = %s LIMIT 1;", (species_id, name))
                aliascheck = dbcs.fetchone()
                if aliascheck == None:
                    dbcs.execute("INSERT INTO `Species_Alias`(`Species_ID`, `Species_Alias`, `Species_Alias_Proper`) VALUES (%s, %s, %s);", (species_id, name, nameproper))
                for k in speciesaliases:
                    dbcs.execute("SELECT * FROM `Species_Alias` WHERE `Species_ID` = %s AND `Species_Alias` = %s LIMIT 1;", (species_id, k.lower()))
                    aliascheck = dbcs.fetchone()
                    if aliascheck == None:
                        dbcs.execute("INSERT INTO `Species_Alias`(`Species_ID`, `Species_Alias`, `Species_Alias_Proper`) VALUES (%s, %s, %s);", (species_id, k.lower(), k))
            for k in speciesuniverse:
                dbcs.execute("SELECT `Universe_ID` FROM `Universe_Base` WHERE `Universe_Name` = %s LIMIT 1;", (k["Name"].lower(),))
                unicheck = dbcs.fetchone()
                if unicheck == None:
                    universe_id = str(uuid.uuid4().hex)
                    dbcs.execute("INSERT INTO `Universe_Base`(`Universe_ID`, `Universe_Name`, `Universe_Name_Proper`) VALUES (%s, %s, %s);", (universe_id, k["Name"].lower(), k["Name"]))
                    dbcs.execute("SELECT `User_ID` FROM `User_Base` WHERE `Username` = %s LIMIT 1;", (k["Owner"].lower(),))
                    usercheck = dbcs.fetchone()
                    if usercheck == None:
                        universe_owner_id = str(uuid.uuid4().hex)
                        dbcs.execute("INSERT INTO `User_Base`(`User_ID`, `Username`, `Username_Proper`, `Join_Datetime`) VALUES (%s, %s, %s, %s);", (universe_owner_id, k["Owner"].lower(), k["Owner"], datetime.now()))
                    else:
                        universe_owner_id = usercheck[0]
                    dbcs.execute("INSERT INTO `Universe_Owner`(`Universe_ID`, `User_ID`) VALUES (%s, %s);", (universe_id, universe_owner_id))
                else:
                    universe_id = unicheck[0]
                if universe_owner_id == None:
                    dbcs.execute("SELECT `User_ID` FROM `User_Base` WHERE `Username` = %s LIMIT 1;", (k["Owner"].lower(),))
                    usercheck = dbcs.fetchone()
                    if usercheck == None:
                        universe_owner_id = str(uuid.uuid4().hex)
                        dbcs.execute("INSERT INTO `User_Base`(`User_ID`, `Username`, `Username_Proper`, `Join_Datetime`) VALUES (%s, %s, %s, %s);", (universe_owner_id, k["Owner"].lower(), k["Owner"], datetime.now()))
                    else:
                        universe_owner_id = usercheck[0]
                if universe_id == None:
                    print("The universe ID never got made. This is an error!")
                    raise
                elif universe_owner_id == None:
                    print("The universe owner ID never got made. This is an error!")
                    raise
                dbcs.execute("SELECT `Universe_ID`, `User_ID` FROM `Universe_Owner` WHERE `Universe_ID` = %s AND `User_ID` = %s LIMIT 1;", (universe_id, universe_owner_id)) # Check still if the universe-owner link exists
                uniownercheck = dbcs.fetchone()
                if uniownercheck == None:
                    dbcs.execute("INSERT INTO `Universe_Owner`(`Universe_ID`, `User_ID`) VALUES (%s, %s);", (universe_id, universe_owner_id))
                dbcs.execute("SELECT * FROM `Species_Universe` WHERE `Species_ID` = %s AND `Universe_ID` = %s LIMIT 1;", (species_id, universe_id))
                specunicheck = dbcs.fetchone() # Safety check
                if specunicheck == None:
                    dbcs.execute("INSERT INTO `Species_Universe`(`Species_ID`, `Universe_ID`) VALUES (%s, %s);", (species_id, universe_id))
                dbase.commit()
        dbcs.execute("SELECT * FROM `Files_Species` WHERE `File_ID` = %s AND `Species_ID` = %s LIMIT 1;", (newfileid, species_id))
        filespeccheck = dbcs.fetchone()
        if filespeccheck == None:
            dbcs.execute("INSERT INTO `Files_Species`(`File_ID`, `Species_ID`) VALUES (%s, %s);", (newfileid, species_id))
        dbase.commit()
    elif tagcategory == "universe":
        dbcs.execute("SELECT `Universe_ID` FROM `Universe_Base` WHERE `Universe_Name` = %s LIMIT 1;", (name,))
        uniout = dbcs.fetchone()
        universe_id = uniout[0]
        dbcs.execute("SELECT * FROM `Files_Universe` WHERE `File_ID` = %s AND `Universe_ID` = %s LIMIT 1;", (newfileid, universe_id))
        uniout = dbcs.fetchone()
        if uniout == None:
            dbcs.execute("INSERT INTO `Files_Universe`(`File_ID`, `Universe_ID`) VALUES (%s, %s);", (newfileid, universe_id))
        dbase.commit()
    elif tagcategory == "campaign":
        continue
        campaign_id = None
        campaign_owner_id = []
        campaign_universe_id = None
        dbcs.execute("SELECT `Campaign_ID` FROM `Campaign_Base` WHERE `Campaign_Name` = %s LIMIT 1;", (name,))
        campaigncheck = dbcs.fetchone()
        if campaigncheck == None:
            campaign_id = str(uuid.uuid4().hex)
            dbcs.execute("INSERT INTO `Campaign_Base`(`Campaign_ID`, `Campaign_Name`, `Campaign_Name_Proper`) VALUES (%s, %s, %s);", (campaign_id, name, nameproper))
        else:
            campaign_id = campaigncheck[0]
        for k in campaignowner:
            dbcs.execute("SELECT `User_ID` FROM `User_Base` WHERE `Username` = %s LIMIT 1;", (k.lower(),))
            usercheck = dbcs.fetchone()
            if usercheck == None:
                campaign_owner_id.append(str(uuid.uuid4().hex))
                dbcs.execute("INSERT INTO `User_Base`(`User_ID`, `Username`, `Username_Proper`, `Join_Datetime`) VALUES (%s, %s, %s, %s);", (campaign_owner_id, k.lower(), k, datetime.now()))
            else:
                campaign_owner_id.append(usercheck[0])
        if campaign_owner_id == []:
            print("There was no campaign owner IDs found or made. This is an error!")
            raise
        for k in campaign_owner_id:
            dbcs.execute("SELECT * FROM `Campaign_Owner` WHERE `Campaign_ID` = %s AND `User_ID` = %s LIMIT 1;", (campaign_id, k))
            # TODO: Continue here with checking if each ID already exists and appending it if it doesn't.
            campownrcheck = dbcs.fetchone()
            if campownrcheck == None:
                dbcs.execute("INSERT INTO `Campaign_Owner`(`Campaign_ID`, `User_ID`) VALUES (%s, %s);", (campaign_id, k))
        for k in campaignuniverse:
            dbcs.execute("SELECT `Universe_ID` FROM `Universe_Base` WHERE `Universe_Name` = %s LIMIT 1;", (k.lower(),))
            unicheck = dbcs.fetchone()
            if unicheck == None:
                campaign_universe_id = str(uuid.uuid4().hex)
                dbcs.execute("INSERT INTO `Universe_Base`(`Universe_ID`, `Universe_Name`, `Universe_Name_Proper`) VALUES (%s, %s, %s);", (campaign_universe_id, k.lower(), k))
            else:
                campaign_universe_id = unicheck[0]
        dbcs.execute("SELECT * FROM `Campaign_Universe` WHERE `Campaign_ID` = %s AND `Universe_ID` = %s LIMIT 1;", (campaign_id, campaign_universe_id))
        campunichk = dbcs.fetchone()
        if campunichk == None:
            dbcs.execute("INSERT INTO `Campaign_Universe`(`Campaign_ID`, `Universe_ID`) VALUES (%s, %s);", (campaign_id, campaign_universe_id))
        dbcs.execute("SELECT * FROM `Files_Campaign` WHERE `File_ID` = %s AND `Campaign_ID` = %s LIMIT 1;", (newfileid, campaign_id))
        campfilechk = dbcs.fetchone()
        if campfilechk == None:
            dbcs.execute("INSERT INTO `Files_Campaign` (`File_ID`, `Campaign_ID`) VALUES (%s, %s);", (newfileid, campaign_id))
        dbcs.execute("SELECT * FROM `Files_Universe` WHERE `File_ID` = %s AND `Universe_ID` = %s LIMIT 1;", (newfileid, campaign_universe_id))
        unifilechk = dbcs.fetchone()
        if unifilechk == None:
            dbcs.execute("INSERT INTO `Files_Universe` (`File_ID`, `Universe_ID`) VALUES (%s, %s);", (newfileid, campaign_id))
        dbase.commit()
    elif tagcategory == "character":
        continue # COMMENT THIS OUT IF YOU WANT TO ACCESS THESE FUNCTIONS AGAIN
        dbcs.execute("SELECT `Character_ID` FROM `Character_Base` WHERE `Character_Name` = %s LIMIT 1;", (name,))
        characterid = dbcs.fetchone()
        dbcs.execute("SELECT `Species_ID` FROM `Character_Species` WHERE `Character_ID` = %s;", (characterid[0],))
        speciesidlist = dbcs.fetchall()
        for j in speciesidlist:
            dbcs.execute("INSERT INTO `Files_Species`(`File_ID`, `Species_ID`) VALUES (%s, %s);", (newfileid, j[0]))
        #     dbcs.execute("INSERT INTO `Files_Characters`(`File_ID`, `Character_ID`, `Species_ID`) VALUES (%s, %s, %s);", (newfileid, characterid[0], j[0]))
            dbase.commit()
        # continue


        
        # dbcs.execute("SELECT * FROM `Character_Alias` WHERE `Character_ID` = %s AND `Character_Alias` = %s;", (characterid[0], name))
        # checkfordupe = dbcs.fetchall()
        # if checkfordupe != []:
        #     continue
        # dbcs.execute("INSERT INTO `Character_Alias`(`Character_ID`, `Character_Alias`, `Character_Alias_Proper`) VALUES (%s, %s, %s);", (characterid[0], name, nameproper))
        # if characteraliases != None:
        #     for j in characteraliases:
        #             dbcs.execute("INSERT INTO `Character_Alias`(`Character_ID`, `Character_Alias`, `Character_Alias_Proper`) VALUES (%s, %s, %s);", (characterid[0], j.lower(), j))
        # dbase.commit()
        # continue
        # if i[1] != "blaze (sonic)": # NOTE: Comment this out after a run to not ruin your data!
            # continue # NOTE: This is done already, so skip characters.
        new_character_id = str(uuid.uuid4().hex)
        newcharactercreated = False
        for j in characterspecies:
            dbcs.execute("SELECT Character_Base.Character_ID, Character_Base.Character_Name, Character_Owner.User_ID, Character_Owner.Username, Species_Base.Species_ID, Species_Base.Species_Name FROM `Character_Base` INNER JOIN `Character_Owner` ON Character_Base.Character_ID = Character_Owner.Character_ID INNER JOIN `Character_Species` ON Character_Base.Character_ID = Character_Species.Character_ID INNER JOIN `Species_Base` ON Character_Species.Species_ID = Species_Base.Species_ID WHERE Character_Base.Character_Name = %s AND Character_Owner.Username = %s AND Species_Base.Species_Name = %s LIMIT 1;", (name, characterowner, j))
            out = dbcs.fetchone()
            if (out == () or out == None) and newcharactercreated == False:
                newcharactercreated = True
                dbcs.execute("INSERT INTO `Character_Base`(`Character_ID`, `Character_Name`, `Character_Name_Proper`) VALUES (%s, %s, %s);", (new_character_id, name, nameproper))
                dbcs.execute("SELECT `User_ID` FROM `User_Base` WHERE `Username` = %s LIMIT 1;", (characterowner.lower(),))
                outuser = dbcs.fetchone()
                if outuser == () or outuser == None:
                    new_user_id = str(uuid.uuid4().hex)
                    dbcs.execute("INSERT INTO `User_Base`(`User_ID`, `Username`, `Username_Proper`, `Join_Datetime`) VALUES (%s, %s, %s, %s);", (new_user_id, characterowner.lower(), characterowner, datetime.now()))
                    dbcs.execute("INSERT INTO `Character_Owner`(`Character_ID`, `User_ID`, `Username`, `Username_Proper`) VALUES (%s, %s, %s, %s);", (new_character_id, new_user_id, characterowner.lower(), characterowner))
                else:
                    dbcs.execute("INSERT INTO `Character_Owner`(`Character_ID`, `User_ID`, `Username`, `Username_Proper`) VALUES (%s, %s, %s, %s);", (new_character_id, outuser[0], characterowner.lower(), characterowner))
                del outuser
                dbcs.execute("SELECT `Species_ID` FROM `Species_Base` WHERE `Species_Name` = %s LIMIT 1;", (j.lower(),))
                outspec = dbcs.fetchone()
                if outspec == () or outspec == None:
                    new_species_id = str(uuid.uuid4().hex)
                    dbcs.execute("INSERT INTO `Species_Base`(`Species_ID`, `Species_Name`, `Species_Name_Proper`) VALUES (%s, %s, %s);", (new_species_id, j.lower(), j))
                    dbcs.execute("INSERT INTO `Character_Species`(`Character_ID`, `Species_ID`) VALUES (%s, %s);", (new_character_id, new_species_id))
                else:
                    dbcs.execute("INSERT INTO `Character_Species`(`Character_ID`, `Species_ID`) VALUES (%s, %s);", (new_character_id, outspec[0]))
                dbase.commit()
            dbcs.execute("SELECT `Species_ID` FROM `Species_Base` WHERE `Species_Name` = %s LIMIT 1;", (j.lower(),))
            speciesid = dbcs.fetchone()
            dbcs.execute("SELECT `Universe_ID` FROM `Species_Universe` WHERE `Species_ID` = %s;", (speciesid[0],))
            universeidlist = dbcs.fetchall()
            if len(universeidlist) == 0:
                universenameidentified = False
                for l in characterspeciesuniverse: # If a dict contains the "name" key, then you need to only associate that name with that universe. Otherwise, associate all species with all universes
                    if "Name" in l:
                        universenameidentified = True
                        break
                if universenameidentified == False:
                    for l in characterspeciesuniverse:
                        dbcs.execute("SELECT `Species_ID` FROM `Species_Base` WHERE `Species_Name` = %s LIMIT 1;", (j.lower(),))
                        out = dbcs.fetchone()
                        if out == None:
                            print(f"ERROR: Species: \"{j}\" wasn't inserted into the database!")
                            raise
                        species_id = out[0]
                        for n in l["Universe"]:
                            dbcs.execute("SELECT `Universe_ID` FROM `Universe_Base` WHERE `Universe_Name` = %s LIMIT 1;", ((n["n"].lower(),)))
                            out = dbcs.fetchone()
                            if out == None:
                                new_universe_id = str(uuid.uuid4().hex)
                                user_id = None
                                dbcs.execute("INSERT INTO `Universe_Base`(`Universe_ID`, `Universe_Name`, `Universe_Name_Proper`) VALUES (%s, %s, %s);", (new_universe_id, n["n"].lower(), n["n"]))
                                dbcs.execute("SELECT `User_ID` FROM `User_Base` WHERE `Username` = %s LIMIT 1;", (n["o"].lower(),))
                                out = dbcs.fetchone()
                                if out == None:
                                    user_id = str(uuid.uuid4().hex)
                                    dbcs.execute("INSERT INTO `User_Base`(`User_ID`, `Username`, `Username_Proper`, `Join_Datetime`) VALUES (%s, %s, %s, %s);", (user_id, n["o"].lower(), n["o"], datetime.now()))
                                else:
                                    user_id = out[0]
                                dbcs.execute("INSERT INTO `Universe_Owner`(`Universe_ID`, `User_ID`) VALUES (%s, %s);", (new_universe_id, user_id))
                                dbcs.execute("INSERT INTO `Species_Universe` (`Species_ID`, `Universe_ID`) VALUES (%s, %s);", (species_id, new_universe_id))
                                dbase.commit()
                        else:
                            universe_id = out[0]
                            user_id = None
                            for n in l["Universe"]:
                                dbcs.execute("SELECT `User_ID` FROM `User_Base` WHERE `Username` = %s LIMIT 1;", (n["o"].lower(),))
                                out = dbcs.fetchone()
                                if out == None:
                                    user_id = str(uuid.uuid4().hex)
                                    dbcs.execute("INSERT INTO `User_Base`(`User_ID`, `Username`, `Username_Proper`, `Join_Datetime`) VALUES (%s, %s, %s, %s);", (user_id, n["o"].lower(), n["o"], datetime.now()))
                                    dbcs.execute("INSERT INTO `Universe_Owner`(`Universe_ID`, `User_ID`) VALUES (%s, %s);", (universe_id, user_id))
                                dbcs.execute("INSERT INTO `Species_Universe` (`Species_ID`, `Universe_ID`) VALUES (%s, %s);", (species_id, universe_id))
                                dbase.commit()
                else:
                    for l in characterspeciesuniverse:
                        if "Name" in l:
                            if l["Name"] == j:
                                dbcs.execute("SELECT `Species_ID` FROM `Species_Base` WHERE `Species_Name` = %s LIMIT 1;", (j.lower(),))
                                out = dbcs.fetchone()
                                if out == None:
                                    print(f"ERROR: Species: \"{j}\" wasn't inserted into the database!")
                                    raise
                                species_id = out[0]
                                for n in l["Universe"]:
                                    dbcs.execute("SELECT `Universe_ID` FROM `Universe_Base` WHERE `Universe_Name` = %s LIMIT 1;", ((n["n"].lower(),)))
                                    out = dbcs.fetchone()
                                    if out == None:
                                        new_universe_id = str(uuid.uuid4().hex)
                                        user_id = None
                                        dbcs.execute("INSERT INTO `Universe_Base`(`Universe_ID`, `Universe_Name`, `Universe_Name_Proper`) VALUES (%s, %s, %s);", (new_universe_id, n["n"].lower(), n["n"]))
                                        dbcs.execute("SELECT `User_ID` FROM `User_Base` WHERE `Username` = %s LIMIT 1;", (n["o"].lower(),))
                                        out = dbcs.fetchone()
                                        if out == None:
                                            user_id = str(uuid.uuid4().hex)
                                            dbcs.execute("INSERT INTO `User_Base`(`User_ID`, `Username`, `Username_Proper`, `Join_Datetime`) VALUES (%s, %s, %s, %s);", (user_id, n["o"].lower(), n["o"], datetime.now()))
                                        else:
                                            user_id = out[0]
                                        dbcs.execute("INSERT INTO `Universe_Owner`(`Universe_ID`, `User_ID`) VALUES (%s, %s);", (new_universe_id, user_id))
                                        dbcs.execute("INSERT INTO `Species_Universe` (`Species_ID`, `Universe_ID`) VALUES (%s, %s);", (species_id, new_universe_id))
                                        dbase.commit()
                                else:
                                    universe_id = out[0]
                                    user_id = None
                                    for n in l["Universe"]:
                                        dbcs.execute("SELECT `User_ID` FROM `User_Base` WHERE `Username` = %s LIMIT 1;", (n["o"].lower(),))
                                        out = dbcs.fetchone()
                                        if out == None:
                                            user_id = str(uuid.uuid4().hex)
                                            dbcs.execute("INSERT INTO `User_Base`(`User_ID`, `Username`, `Username_Proper`, `Join_Datetime`) VALUES (%s, %s, %s, %s);", (user_id, n["o"].lower(), n["o"], datetime.now()))
                                            dbcs.execute("INSERT INTO `Universe_Owner`(`Universe_ID`, `User_ID`) VALUES (%s, %s);", (universe_id, user_id))
                                        dbcs.execute("INSERT INTO `Species_Universe` (`Species_ID`, `Universe_ID`) VALUES (%s, %s);", (species_id, universe_id))
                                        dbase.commit()
    elif tagcategory == "tag":
        continue
        dbcs.execute("SELECT * FROM `Species_Base` WHERE `Species_Name` = %s LIMIT 1;", (name.lower(),))
        isspecieschk = dbcs.fetchone()
        if isspecieschk != None:
            continue
        tag_id = None
        dbcs.execute("SELECT `Tag_ID` FROM `Tag_Base` WHERE `Tag` = %s LIMIT 1;", (name,))
        tagchk = dbcs.fetchone()
        if tagchk == None:
            tag_id = str(uuid.uuid4().hex)
            dbcs.execute("INSERT INTO `Tag_Base`(`Tag_ID`, `Tag`, `Tag_Proper`) VALUES (%s, %s, %s);", (tag_id, name, name.title()))
        else:
            tag_id = tagchk[0]
        dbcs.execute("SELECT * FROM `Files_Tags` WHERE `File_ID` = %s AND `Tag_ID` = %s LIMIT 1;", (newfileid, tag_id))
        tagchk = dbcs.fetchone()
        if tagchk == None:
            dbcs.execute("INSERT INTO `Files_Tags`(`File_ID`, `Tag_ID`) VALUES (%s, %s);", (newfileid, tag_id))
        dbase.commit()

raw = None
with open("/home/lunar/projects/webserv/pokemonlist.json", 'r') as file:
    raw = file.read()
pokelist = json.loads(raw)
for i in pokelist:
    break # Comment this out if you don't want this list redone
    print(f"Currently inserting {i}.")
    dbcs.execute("SELECT `Species_ID` FROM `Species_Base` WHERE `Species_Name` = %s LIMIT 1;", (i.lower(),))
    out = dbcs.fetchone()
    species_id = None
    if out == None:
        species_name = i.lower()
        species_name_proper = i
        species_id = str(uuid.uuid4().hex)
        dbcs.execute("INSERT INTO `Species_Base`(`Species_ID`, `Species_Name`, `Species_Name_Proper`) VALUES (%s, %s, %s);", (species_id, species_name, species_name_proper))
    else:
        species_id = out[0]
    dbcs.execute("SELECT * FROM `Species_Universe` WHERE `Species_ID` = %s AND `Universe_ID` = \"7b7ebe9590004bd7a3a7fee9cf73a899\" LIMIT 1;", (species_id,))
    out = dbcs.fetchone()
    if out == None:
        dbcs.execute("INSERT INTO `Species_Universe`(`Species_ID`, `Universe_ID`) VALUES (%s, %s);", (species_id, "7b7ebe9590004bd7a3a7fee9cf73a899"))
    dbcs.execute("SELECT * FROM `Species_Universe` WHERE `Species_ID` = %s AND `Universe_ID` = \"c8a152dabb4d4970bab50d793fcd72f8\" LIMIT 1;", (species_id,))
    out = dbcs.fetchone()
    if out == None:
        dbcs.execute("INSERT INTO `Species_Universe`(`Species_ID`, `Universe_ID`) VALUES (%s, %s);", (species_id, "c8a152dabb4d4970bab50d793fcd72f8"))
    dbcs.execute("SELECT * FROM `Species_Universe` WHERE `Species_ID` = %s AND `Universe_ID` = \"f8a8e0823389494286f5cfe98ac1f282\" LIMIT 1;", (species_id,))
    out = dbcs.fetchone()
    if out == None:
        dbcs.execute("INSERT INTO `Species_Universe`(`Species_ID`, `Universe_ID`) VALUES (%s, %s);", (species_id, "f8a8e0823389494286f5cfe98ac1f282"))
    dbase.commit()
del raw

print("Processing flats...")

dbcs.execute("TRUNCATE TABLE `Files_Flat`;")
dbcs.execute("TRUNCATE TABLE `File_Search_Master`;")
dbase.commit()
dbcs.execute("SELECT Files_Umbreone_Old_ID.New_File_ID, files.Flat FROM `files` INNER JOIN Files_Umbreone_Old_ID ON files.Internal_ID = Files_Umbreone_Old_ID.Old_File_ID WHERE 1;")
out = dbcs.fetchall()
for i in out:
    if i[1] == 1:
        dbcs.execute("INSERT INTO `Files_Flat`(`File_ID`) VALUES (%s);", (i[0],))
        dbase.commit()
        searchinsertlist = []
        searchinsertlist.append(f"flat:true")
        searchinsertlist.append(f"flat:yes")
        searchinsertlist.append(f"is_flat:true")
        searchinsertlist.append(f"is_flat:yes")
        searchinsertlist.append(f"isflat:true")
        searchinsertlist.append(f"isflat:yes")
        for j in searchinsertlist:
            dbcs.execute("INSERT INTO `File_Search_Master`(`File_ID`, `Search_Term`) VALUES (%s, %s);", (i[0], j))
    elif i[0] == 0:
        searchinsertlist = []
        searchinsertlist.append(f"flat:false")
        searchinsertlist.append(f"flat:no")
        searchinsertlist.append(f"is_flat:false")
        searchinsertlist.append(f"is_flat:no")
        searchinsertlist.append(f"isflat:false")
        searchinsertlist.append(f"isflat:no")
        for j in searchinsertlist:
            dbcs.execute("INSERT INTO `File_Search_Master`(`File_ID`, `Search_Term`) VALUES (%s, %s);", (i[0], j))
    dbase.commit()

print("Flats processed.")
print("Processing file data...")

dbcs.execute("SELECT * FROM `Files_Base` WHERE `Display_Search` = 1;")
fileout = dbcs.fetchall()
for i in fileout:
    fileid = i[0]
    searchinsertlist = []
    searchinsertlist.append(f"file_id:{i[0]}")
    searchinsertlist.append(f"fileid:{i[0]}")
    searchinsertlist.append(f"uploader_id:{i[1]}")
    searchinsertlist.append(f"uploaderid:{i[1]}")
    dbcs.execute("SELECT `Username` FROM `User_Base` WHERE `User_ID` = %s LIMIT 1;", (i[1],))
    out = dbcs.fetchone()
    if out != None:
        searchinsertlist.append(f"uploader:{out[0]}")
        searchinsertlist.append(f"uploader_name:{out[0]}")
        searchinsertlist.append(f"uploadername:{out[0]}")
        searchinsertlist.append(f"uploader_username:{out[0]}")
        searchinsertlist.append(f"uploaderusername:{out[0]}")
    searchinsertlist.append(f"file_extension:{i[2]}")
    searchinsertlist.append(f"fileextension:{i[2]}")
    searchinsertlist.append(f"fileext:{i[2]}")
    searchinsertlist.append(f"file_ext:{i[2]}")
    searchinsertlist.append(f"ext:{i[2]}")
    searchinsertlist.append(f"extension:{i[2]}")
    searchinsertlist.append(f"filename:{i[3]}")
    searchinsertlist.append(f"file_name:{i[3]}")
    searchinsertlist.append(f"name:{i[3]}")
    searchinsertlist.append(f"display_name:{i[3]}")
    searchinsertlist.append(f"displayname:{i[3]}")
    searchinsertlist.append(f"rating:{i[4]}")
    searchinsertlist.append(f"filerating:{i[4]}")
    searchinsertlist.append(f"file_rating:{i[4]}")
    if i[4] == "s":
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
    for j in searchinsertlist:
        dbcs.execute("INSERT INTO `File_Search_Master`(`File_ID`, `Search_Term`) VALUES (%s, %s);", (fileid, j))
    dbase.commit()
    searchinsertlist = []

print("Files processed.")
print("Processing artists...")

dbcs.execute("SELECT * FROM `Files_Artist` WHERE 1;")
artistout = dbcs.fetchall()
for i in artistout:
    file_id = i[0]
    searchinsertlist = []
    searchinsertlist.append(f"artist_id:{i[1]}")
    searchinsertlist.append(f"artistid:{i[1]}")
    dbcs.execute("SELECT `User_ID`, `Artist_Name`, `Artist_Name_Proper` FROM `Artist_Base` WHERE `Artist_ID` = %s LIMIT 1;", (i[1],))
    out = dbcs.fetchone()
    if out != None:
        searchinsertlist.append(f"artist_user_id:{out[0]}")
        searchinsertlist.append(f"artistuserid:{out[0]}")
        searchinsertlist.append(f"artist:{out[1]}")
        searchinsertlist.append(f"artistname:{out[1]}")
        searchinsertlist.append(f"artist_name:{out[1]}")
    for j in searchinsertlist:
        dbcs.execute("INSERT INTO `File_Search_Master`(`File_ID`, `Search_Term`) VALUES (%s, %s);", (file_id, j))
    dbase.commit()
    searchinsertlist = []

print("Artists processed.")
del artistout
print("Processing campaigns...")

dbcs.execute("SELECT * FROM `Files_Campaign` WHERE 1;")
campaignout = dbcs.fetchall()
for i in campaignout:
    file_id = i[0]
    searchinsertlist = []
    searchinsertlist.append(f"campaign_id:{i[1]}")
    searchinsertlist.append(f"campaignid:{i[1]}")
    dbcs.execute("SELECT * FROM `Campaign_Base` WHERE `Campaign_ID` = %s LIMIT 1;", (i[1],))
    out = dbcs.fetchone()
    if out != None:
        searchinsertlist.append(f"campaign:{out[1]}")
        searchinsertlist.append(f"campaignname:{out[1]}")
        searchinsertlist.append(f"campaign_name:{out[1]}")
    dbcs.execute("SELECT `User_ID` FROM `Campaign_Owner` WHERE `Campaign_ID` = %s LIMIT 1;", (i[1],))
    out = dbcs.fetchone()
    if out != None:
        userid = out[0]
        dbcs.execute("SELECT `Username` FROM `User_Base` WHERE `User_ID` = %s LIMIT 1;", (userid,))
        out = dbcs.fetchone()
        if out != None:
            searchinsertlist.append(f"campaignowner:{out[0]}")
            searchinsertlist.append(f"campaign_owner:{out[0]}")
    for j in searchinsertlist:
        dbcs.execute("INSERT INTO `File_Search_Master`(`File_ID`, `Search_Term`) VALUES (%s, %s);", (file_id, j))
    dbase.commit()
    searchinsertlist = []

del campaignout
print("Campaigns processed.")
print("Processing species...")

dbcs.execute("SELECT * FROM `Files_Species` WHERE 1;")
speciesout = dbcs.fetchall()
for i in speciesout:
    file_id = i[0]
    searchinsertlist = []
    searchinsertlist.append(f"species_id:{i[1]}")
    searchinsertlist.append(f"speciesid:{i[1]}")
    dbcs.execute("SELECT * FROM `Species_Alias` WHERE `Species_ID` = %s;", (i[1],))
    out = dbcs.fetchall()
    if out != []:
        for j in out:
            searchinsertlist.append(f"species:{j[1]}")
            searchinsertlist.append(f"speciesname:{j[1]}")
            searchinsertlist.append(f"species_name:{j[1]}")
    for j in searchinsertlist:
        dbcs.execute("INSERT INTO `File_Search_Master`(`File_ID`, `Search_Term`) VALUES (%s, %s);", (file_id, j))
    dbase.commit()
    searchinsertlist = []

del speciesout
print("Species processed.")
print("Processing characters...")

dbcs.execute("SELECT * FROM `Files_Characters` WHERE 1;")
characterout = dbcs.fetchall()
for i in characterout:
    file_id = i[0]
    searchinsertlist = []
    searchinsertlist.append(f"character_id:{i[1]}")
    searchinsertlist.append(f"characterid:{i[1]}")
    dbcs.execute("SELECT * FROM `Character_Alias` WHERE `Character_ID` = %s;", (i[1],))
    out = dbcs.fetchall()
    if out != []:
        for j in out:
            searchinsertlist.append(f"character:{j[1]}")
            searchinsertlist.append(f"charactername:{j[1]}")
            searchinsertlist.append(f"character_name:{j[1]}")
    for j in searchinsertlist:
        dbcs.execute("INSERT INTO `File_Search_Master`(`File_ID`, `Search_Term`) VALUES (%s, %s);", (file_id, j))
    dbase.commit()
    searchinsertlist = []

del characterout
print("Characters processed.")
print("Processing universes...")

dbcs.execute("SELECT * FROM `Files_Universe` WHERE 1;")
universeout = dbcs.fetchall()
for i in universeout:
    file_id = i[0]
    searchinsertlist = []
    searchinsertlist.append(f"universe_id:{i[1]}")
    searchinsertlist.append(f"universeid:{i[1]}")
    dbcs.execute("SELECT `Universe_Name` FROM `Universe_Base` WHERE `Universe_ID` = %s LIMIT 1;", (i[1],))
    out = dbcs.fetchone()
    if out != None:
        searchinsertlist.append(f"universe:{out[0]}")
        searchinsertlist.append(f"universe_name:{out[0]}")
        searchinsertlist.append(f"universename:{out[0]}")
    for j in searchinsertlist:
        dbcs.execute("INSERT INTO `File_Search_Master`(`File_ID`, `Search_Term`) VALUES (%s, %s);", (file_id, j))
    dbase.commit()
    searchinsertlist = []

del universeout
print("Universes processed.")
print("Processing tags...")

dbcs.execute("SELECT * FROM `Files_Tags` WHERE 1;")
tagout = dbcs.fetchall()
for i in tagout:
    file_id = i[0]
    searchinsertlist = []
    searchinsertlist.append(f"tag_id:{i[1]}")
    searchinsertlist.append(f"tagid:{i[1]}")
    dbcs.execute("SELECT `Tag` FROM `Tag_Base` WHERE `Tag_ID` = %s LIMIT 1;", (i[1],))
    out = dbcs.fetchone()
    if out != None:
        searchinsertlist.append(f"tag:{out[0]}")
        searchinsertlist.append(f"{out[0]}")
    for j in searchinsertlist:
        dbcs.execute("INSERT INTO `File_Search_Master`(`File_ID`, `Search_Term`) VALUES (%s, %s);", (file_id, j))
    dbase.commit()
    searchinsertlist = []

dbase.commit()
dbcs.close()
dbase.close()

print("Done!")