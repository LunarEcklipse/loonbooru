from datetime import datetime

class TagBasic(): #TODO: Finish me!
    def __init__(self, tag_id: str, tagname: str, tagnameproper: str):
        self.TagID = tag_id
        self.TagName = tagname
        self.TagNameProper = tagnameproper
        pass

class Artist():
    def __init__(self, artist_id: str, user_id: str, artist_name: str, artist_name_proper: str):
        self.ArtistID = artist_id
        self.UserID = user_id
        self.ArtistName = artist_name
        self.ArtistNameProper = artist_name_proper
        return

class Character():
    def __init__(self, character_id: str, character_name: str, character_name_proper: str, character_species: list, character_alias: list, character_owner: list):
        self.CharacterID = character_id
        self.CharacterName = character_name
        self.CharacterNameProper = character_name_proper
        self.CharacterSpecies = character_species
        self.CharacterOwner = character_owner
        return

class Species():
    def __init__(self, species_id: str, species_name: str, species_name_proper: str, species_universe: list):
        self.SpeciesID = species_id
        self.SpeciesName = species_name
        self.SpeciesNameProper = species_name_proper
        self.SpeciesUniverse = species_universe
        return
    
    def __eq__(self, other):
        return (self.SpeciesID == other.SpeciesID and self.SpeciesName == other.SpeciesName and self.SpeciesNameProper == other.SpeciesNameProper)

class Universe():
    def __init__(self, universe_id: str, universe_name: str, universe_name_proper: str, universe_owner: list):
        self.UniverseID = universe_id
        self.UniverseName = universe_name
        self.UniverseNameProper = universe_name_proper
        self.UniverseOwner = universe_owner
        return

class User():
    def __init__(self, user_id: str, username: str, username_proper: str, join_datetime: datetime):
        self.UserID = user_id
        self.Username = username
        self.UsernameProper = username_proper
        try:
            self.JoinDatetime = join_datetime
        except ValueError as exception:
            self.JoinDatetime = None
        return

class Campaign():
    def __init__(self, campaign_id: str, campaign_name: str, campaign_name_proper: str, campaign_owner: list):
        self.CampaignID = campaign_id
        self.CampaignName = campaign_name
        self.CampaignNameProper = campaign_name_proper
        self.CampaignOwner = campaign_owner
        return

class FileBasic(): # FileBasic only contains the information needed to display the file on a browse page. FileDetail contains more information.
    def __init__(self, file_id: str, file_ext: str, upload_datetime: datetime, file_rating: str, display_browse: int, display_search: int):
        self.FileID = file_id
        self.FileEXT = file_ext
        self.Filename = f"{file_id}.{file_ext}"
        try:
            self.UploadDatetime = upload_datetime
        except ValueError as exception:
            self.UploadDatetime = None
        self.FileRating = file_rating
        self.DisplayBrowse = True
        if display_browse == 0:
            self.DisplayBrowse = False
        self.DisplaySearch = True
        if display_search == 0:
            self.DisplaySearch = False
        return

    def FilepathFromStatic_Full(self):
        return f"img/full/{self.Filename}"

class FileDetail(FileBasic): #TODO: ADD UPLOADER ID AND TAGS!
    def __init__(self, file_id: str,
    file_ext: str,
    upload_datetime: str,
    file_rating: str,
    display_browse: int,
    display_search: int,
    display_name: str,
    description: str,
    artistlist: list,
    characterlist: list,
    specieslist: list,
    campaignlist: list,
    universelist: list,
    tagslist: list):
        super().__init__(file_id, file_ext, upload_datetime, file_rating, display_browse, display_search)
        self.DisplayName = str(display_name)
        self.Description = str(description)
        self.Artists = artistlist
        self.Characters = characterlist
        self.Species = specieslist
        self.Campaigns = campaignlist
        self.Universes = universelist
        self.Tags = tagslist
        return