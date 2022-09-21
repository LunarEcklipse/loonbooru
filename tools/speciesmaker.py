import json
import uuid

tabl = []

filepath = "/home/lunar/projects/webserv/loonbooru/tools/speciesmaker/speciesout.json"
raw = None

with open(filepath, 'r') as file:
    raw = file.read()

try:
    tabl = json.loads(raw)
except:
    tabl = []

while True:
    name = input("Species Name: ")
    if name == None or name == "":
        print("A name is needed.")
        continue
    universe = input("Species Universe: ")
    if universe == "Pokemon":
        universe = "Pokémon"
    
    name.replace(",", "")
    universe.replace(",", "")

    nameproper = name
    name = name.lower()

    if universe == "":
        universe = None
    uniproper = universe
    if universe != None:
        universe = universe.lower()

    alreadyexists = False
    specalreadyexists = False
    specuid = None
    unialreadyexists = False
    uniuid = None
    for i in tabl:
        if i["name"] == name and i["universe"] == universe:
            alreadyexists = True
        if i["name"] == name:
            specalreadyexists = True
            specuid = i["species_uid"]
        if i["universe"] == universe:
            unialreadyexists = True
            uniuid = i["universe_uid"]
    if alreadyexists:
        print("This species already (apparently) exists.")
        continue
    if specalreadyexists == False:
        specuid = uuid.uuid4().hex
    if unialreadyexists == False:
        uniuid = uuid.uuid4().hex
    if universe == None:
        uniuid = None
    outdc = {
        "species_uid": specuid,
        "name": name,
        "name_proper": nameproper,
        "universe_uid": uniuid,
        "universe": universe,
        "universe_proper": uniproper
    }
    tabl.append(outdc)
    with open(filepath, 'w') as file:
        raw = json.dumps(tabl)
        file.write(raw)