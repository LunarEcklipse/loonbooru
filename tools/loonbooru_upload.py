import mysql.connector
import os
import sys
import json
import shutil
from datetime import datetime
from PIL import Image

class InvalidCategoryTag(Exception):
    def __init__(self, tag: str):
        self.message = f"\"{tag}\" is not a valid category. Valid categories are \"s\", \"q\", \"f\", \"e\", and \"u\"."
        super().__init__(self.message)
        return
    
class InvalidParamCharacter(Exception):
    def __init__(self, char: str):
        self.message = f"\"{char}\" is an invalid character and cannot be in any insertion."
        super().__init__(self.message)
        return

class InvalidJSONFormat(Exception):
    def __init__(self):
        self.message = f"\"params.json\" could not be processed as valid JSON. Do you have a typo in your document?"
        super().__init__(self.message)
        return

class MissingUploadFile(Exception):
    def __init__(self, filename: str):
        self.message = f"File: \"{filename}\" could not be found in the \"umbreone_upload\" directory. Is the name AND extension identical to the one described in params.json (case-sensitive)?"
        super().__init__(self.message)
        return

class MySQLConnectionError(Exception):
    def __init__(self):
        self.message = "A MySQL database connection could not be established. This error is not your fault. Contact lunar if you see this."
        super().__init__(self.messsage)
        return

absPath = os.path.abspath(__file__) # This little chunk makes sure the working directory is correct.
dname = os.path.dirname(absPath)
os.chdir(dname)
paramfileloc = "/home/lunar/projects/webserv/loonbooru/loonbooru_upload_params.json"

if (os.path.exists(paramfileloc)) == False:
    print("Couldn't find the parameters file. It should be named \"loonbooru_upload_params.json\" in the \"umbreone_upload_params\" folder.")
    sys.exit()

raw = ""
with open(paramfileloc, 'r') as f:
    raw = f.read()
    f.close()
try:
    js = json.loads(raw)
except json.JSONDecodeError as exception:
    raise InvalidJSONFormat()
dbase = mysql.connector.connect(host="127.0.0.1", user="loonbooru", password="BgjplxX3jqUuiyV3", database="loonbooru")
dbcs = dbase.cursor(prepared=True)
for i in js:
    if i["filename"].find(',') != -1 or i["display_name"].find(',') != -1 or i["artist"].find(',') != -1 or i["category"].find(',') != -1:
        raise InvalidParamCharacter(',')
    if i["filename"].find(':') != -1 or i["display_name"].find(':') != -1 or i["artist"].find(':') != -1 or i["category"].find(':') != -1:
        raise InvalidParamCharacter(':')
    for j in i["tags"]:
        if j["n"].find(',') != -1:
            raise InvalidParamCharacter(',')
        if j["n"].find(':') != -1:
            raise InvalidParamCharacter(':')
    if i["category"].lower() != 's' and i["category"].lower() != 'q' and i["category"].lower() != 'f' and i["category"].lower() != 'e' and i["category"].lower() != 'u':
        raise InvalidCategoryTag(i["category"])
    if os.path.exists("/home/polo/umbreone_upload" + "/" + i["filename"]) == False:
        raise MissingUploadFile(i["filename"])
    extension = (os.path.splitext("/home/polo/umbreone_upload" + "/" + i["filename"]))[1]
    extension = extension[1:]
    flat = False
    if i["category"] == "f":
        flat = True
    dbcs.execute("INSERT INTO `files` (`File_EXT`, `Display_Name`, `Rating`, `Artist`, `Flat`, `Upload_Datetime`) VALUES (%s, %s, %s, %s, %s, %s);", (extension.lower(), i["display_name"], i["category"].lower(), i["artist"].lower(), flat, datetime.now()))
    dbcs.execute("SELECT LAST_INSERT_ID()")
    idr = dbcs.fetchone()
    id = idr[0]
    for j in i["tags"]:
        if j["n"].lower() == "pokemon":
            j["n"] == "pokemon"
        dbcs.execute("INSERT INTO `tags` (`File_ID`, `Tag`) VALUES (%s, %s);", (id, j["n"].lower()))
    dbase.commit()
    size256 = 256, 256
    size128 = 128, 128
    size64 = 64, 64
    if extension == "png" or extension == "jpg" or extension == "jpeg":
        shutil.copyfile(("/home/polo/umbreone_upload" + "/" + i["filename"]), ("/web/umbreone/rsc/file/thumb/256/" + str(id) + "." + extension))
        im = Image.open("/web/umbreone/rsc/file/thumb/256/" + str(id) + "." + extension)
        im.thumbnail(size256, Image.ANTIALIAS)
        im.save("/web/umbreone/rsc/file/thumb/256/" + str(id) + "." + extension)
        im.close()
        shutil.copyfile(("/home/polo/umbreone_upload" + "/" + i["filename"]), ("/web/umbreone/rsc/file/thumb/128/" + str(id) + "." + extension))
        im = Image.open("/web/umbreone/rsc/file/thumb/128/" + str(id) + "." + extension)
        im.thumbnail(size128, Image.ANTIALIAS)
        im.save("/web/umbreone/rsc/file/thumb/128/" + str(id) + "." + extension)
        im.close()
        shutil.copyfile(("/home/polo/umbreone_upload" + "/" + i["filename"]), ("/web/umbreone/rsc/file/thumb/64/" + str(id) + "." + extension))
        im = Image.open("/web/umbreone/rsc/file/thumb/64/" + str(id) + "." + extension)
        im.thumbnail(size64, Image.ANTIALIAS)
        im.save("/web/umbreone/rsc/file/thumb/64/" + str(id) + "." + extension)
        im.close()
    elif extension == "gif":
        im = Image.open("/home/polo/umbreone_upload" + "/" + i["filename"])
        im.seek(0)
        im.save("/web/umbreone/rsc/file/thumb/256/" + str(id) + ".png")
        im.save("/web/umbreone/rsc/file/thumb/128/" + str(id) + ".png")
        im.save("/web/umbreone/rsc/file/thumb/64/" + str(id) + ".png")
        im.close()
        im = Image.open("/web/umbreone/rsc/file/thumb/256/" + str(id) + ".png")
        im.thumbnail(size256, Image.ANTIALIAS)
        im.save("/web/umbreone/rsc/file/thumb/256/" + str(id) + ".png")
        im.close()
        im = Image.open("/web/umbreone/rsc/file/thumb/128/" + str(id) + ".png")
        im.thumbnail(size128, Image.ANTIALIAS)
        im.save("/web/umbreone/rsc/file/thumb/128/" + str(id) + ".png")
        im.close()
        im = Image.open("/web/umbreone/rsc/file/thumb/64/" + str(id) + ".png")
        im.thumbnail(size64, Image.ANTIALIAS)
        im.save("/web/umbreone/rsc/file/thumb/64/" + str(id) + ".png")
        im.close()
    shutil.move(("/home/polo/umbreone_upload" + "/" + i["filename"]), ("/web/umbreone/rsc/file/" + str(id) + "." + extension))
    print("Finished processing " + i["filename"])
dbcs.close()
dbase.close()

print("Done! Refresh your site!")