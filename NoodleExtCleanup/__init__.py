"""A simple python script to cleanup Noodle Extensions levels.
It removes:
- Unused tracks on notes
- Unused tracks on obstacles
- AnimateTracks that animates a track that isn't assigned to anything
- AssignPlayerToTrack that animates incorrect properties
"""

import json, io
from typing import Union
from tqdm import tqdm

class Level:
    '''A simple data container for levels.'''

    path = ""

    customEvents = []
    events = []
    notes = []
    obstacles = []

    def toDict(self):
        return {
            "version":"2.0.0",
            "_customData":{
                "_customEvents":self.customEvents
            },
            "_events":self.events,
            "_notes":self.notes,
            "_obstacles":self.obstacles
        }

def cleanup(levelIn:str, levelOut:str, ignore=False):
    """Cleans up your Noodle Extension level.
    :param: levelIn - The level.dat path to check.
    :param: levelOut - The file where the cleaned up level will be outputted.
    :param: ignore - Whether or not to output all errors to console.
    """

    level = Level()
    data = json.load(open(levelIn))

    if data.get("_notes"):
        level.notes = data["_notes"]
    if data.get("_obstacles"):
        level.obstacles = data["_obstacles"]
    if data.get("_customData"):
        if data["_customData"].get("_customEvents"):
            level.customEvents = data["_customData"]["_customEvents"]
    levelIn = levelIn.replace("/", "\\")
    if not levelIn.endswith("\\"):
        levelIn += "\\"

    level.path = levelIn

    # TODO add more error checkings 
    
    level.customEvents = [x for x in level.customEvents if x.get("_time") is not None]

    for x in range(len(level.customEvents)):
        level.customEvents[x]["_time"] = float(level.customEvents[x]["_time"])
    level.customEvents.sort(key=lambda x: x["_time"])
    
    allErrors = [] # error as string to be printed
    errorData = [] # error dict info
    errorCodeNames = [] # code names to help with cleanup


    # get all tracks used on notes
    noteTracks = []
    notesWithTrack = []
    for n in level.notes:
        if n.get("_customData"):
            if n["_customData"].get("_track"):
                if n["_customData"]["_track"] not in noteTracks:
                    notesWithTrack.append(n)
                    noteTracks.append(n["_customData"]["_track"])
    
    # get all tracks used on obstacles
    obstacleTracks = []
    obstaclesWithTracks = []
    for o in level.obstacles:
        if o.get("_customData"):
            if o["_customData"].get("_track"):
                if o["_customData"]["_track"] not in obstacleTracks:
                    obstacleTracks.append(o["_customData"]["_track"])
                    obstaclesWithTracks.append(o)
        
    # get all tracks used on player
    animatePlayerTracks = []
    for anmpl in level.customEvents:
        if anmpl.get("_type"):
            if anmpl["_type"] == "AssignPlayerToTrack":
                animatePlayerTracks.append(anmpl["_data"]["_track"])

    # get all parent tracks
    parentTracks = []
    childrenTracks = []
    for ptrack in level.customEvents:
        if ptrack.get("_type"):
            if ptrack["_type"] == "AssignTrackParent":
                if ptrack["_data"]["_parentTrack"] not in parentTracks:
                    parentTracks.append(ptrack["_data"]["_parentTrack"])
                    childrenTracks += ptrack["_data"]["_childrenTracks"]

    # check if they are used
    for ce in level.customEvents:
        # while I'm at it I might as well check if there's tracks that are being animated
        # but aren't assigned to anything
        if not ce.get("_data"):
            continue

        if ce["_data"].get("_track"):
            # check if track is animated but not assigned to anything
            if not ce["_data"]["_track"] in (obstacleTracks + noteTracks + animatePlayerTracks + parentTracks):
                allErrors.append(f"Track '{ce['_data']['_track']}' is animated at {ce['_time']} in {ce['_type']} but is not assigned to any objects.")
                errorData.append(ce)
                errorCodeNames.append("USELESS_TRACK_ANIMATION")
        
            else:
                if ce["_data"]["_track"] in obstacleTracks:
                    obstaclesWithTracks = [x for x in obstaclesWithTracks if x["_customData"]["_track"] != ce["_data"]["_track"]]
                elif ce["_data"]["_track"] in noteTracks:
                    notesWithTrack = [x for x in notesWithTrack if x["_customData"]["_track"] != ce["_data"]["_track"]]
        


                    

    if len(notesWithTrack) != 0:
        for unused in notesWithTrack:
            allErrors.append(f'\'{unused["_customData"]["_track"]}\' is assigned to one or more notes but never animated.')

    if len(obstaclesWithTracks) != 0:
        for unused in obstaclesWithTracks:
            allErrors.append(f'\'{unused["_customData"]["_track"]}\' is assigned to one or more obstacles but never animated.')



    errorData += notesWithTrack + obstaclesWithTracks
    errorCodeNames += ["CONTAINS_UNUSED_TRACK" for _ in range(len(notesWithTrack + obstaclesWithTracks))]

    # check if there is a "Noodle Extensions" requirement
    
    # find the Info.dat
    infoDatPath = '\\'.join(level.path.split("\\")[:-2]) + "\\Info.dat"
    infoDat = json.load(open(infoDatPath))

    allOutputFiles = []
    for beatmapset in infoDat["_difficultyBeatmapSets"]:
        for beatmap in beatmapset["_difficultyBeatmaps"]:
            if beatmap["_beatmapFilename"] == levelOut:
                if beatmap["_customData"].get("_requirements"):
                    if not "Noodle Extensions" in beatmap["_customData"]["_requirements"]:
                        allErrors.append(f"{levelOut} does not have \"Noodle Extensions\" requirement")
            allOutputFiles.append(beatmap["_beatmapFilename"])

    if levelOut not in allOutputFiles:
        allErrors.append(f"{levelOut} is not referenced in the level.dat and will not be playable in-game.")


    # check if properties are animated on unavailable event types

    for ce in level.customEvents:
        currentPlayerTrack = ""
        if ce["_type"] == "AssignPlayerToTrack":
            currentPlayerTrack = ce["_data"]["_track"]
        
        elif ce["_type"] == "AnimateTrack":
            if ce["_data"]["_track"] == currentPlayerTrack:
                properties = ce["_data"].keys()
                properties.remove("_duration")
                properties.remove("_track")
                for p in properties:
                    if p not in "_position _rotation _localRotation".split():
                        allErrors.append(f"Attempting to animate property {p} on player track {currentPlayerTrack}")
                        errorData.append(ce)
                        errorCodeNames.append(f"CANNOT_ANIMATE_THIS_WAY-{p}")



    if not ignore:
        print("\n".join(allErrors))

    print(f"{len(allErrors)} errors found, {len(errorData)} can be cleaned up.\nSet `ignore` to True to not display them.")

    # None                              No possible fixes to this error.
    # USELESS_TRACK_ANIMATION           Animating a track but not assigned to anything (or assigned to player)
    # CONTAINS_UNUSED_TRACK             A note/obstacle that contains a track that is not animated
    # CANNOT_ANIMATE_THIS_WAY           When animating a property on an object that doesn't support said property
    # 



    for i in tqdm (range(len(errorData)), desc="Cleaning up errors"):
        if errorCodeNames[i] == "USELESS_TRACK_ANIMATION":
            level.customEvents.pop(level.customEvents.index(errorData[i]))
        elif errorCodeNames[i] == "CONTAINS_UNUSED_TRACK":
            if errorData[i] in level.notes:
                noteInd = level.notes.index(errorData[i])
                level.notes[noteInd]["_customData"].pop("_track")
            elif errorData[i] in level.obstacles:
                obstacleInd = level.obstacles.index(errorData[i])
                level.obstacles[obstacleInd]["_customData"].pop("_track")
            elif errorData[i] in level.customEvents:
                customInd = level.customEvents.index(errorData[i])
                level.customEvents.pop(customInd)
        elif errorCodeNames[i].startswith("CANNOT_ANIMATE_THIS_WAY"):
            ceInd = level.customEvents.index(errorData[i])
            errorProp = errorCodeNames[i].split("-")[1]
            level.customEvents[ceInd]["_data"].pop(errorProp)

    json.dump(level.toDict(), open(levelOut, 'w'))

