import mysql.connector

dbase = mysql.connector.connect(host="127.0.0.1", user="umbreone", password="dYZ7g75WMAJ8CQPO", database="umbreone")
dbcs = dbase.cursor(dictionary=True)
dbcs.execute("SELECT * FROM `tags` WHERE `Tag` = 'pokemon';")
tagls = dbcs.fetchall()
for i in tagls:
    if i["Tag"] == "pokemon":
        dbcs.execute("DELETE FROM `tags` WHERE `Tag_ID` = %s;", (i["Tag_ID"],))
dbase.commit()
dbcs.close()
dbase.close()
