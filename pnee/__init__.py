"""PNEEv2
Because PNEE was bad™

This is a much simpler, user-friendly, python library to help you make Noodle Extensions levels.
It contains more flexibility, easier usage, and is less limiting.
"""

import json, io
from typing import Union


class Level:
    '''A simple data container for levels.'''

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

def loadLevel(level:Union[str, io.TextIOWrapper]) -> Level:
    '''Loads a level from a path.'''
    print(level)

    lvl = {}
    return True
    l = Level()

    l.customEvents = lvl["_customData"]["_customEvents"]
    l.events = lvl["_events"]

    l.notes = lvl["_notes"]
    l.obstacles = lvl["_obstacles"]

    return l

def dumpLevel(levelPath, level:Level):
    # go over unused tracks

    print("\n".join(_getAllErrors(level)))

    json.dump(level.toDict(), open(levelPath, 'w'))

def _getAllErrors(level:Level):
    # get all tracks
    
    allErrors = [] # error as string to be printed
    errorData = [] # error dict info

    noteTracks = []
    notesWithTrack = []
    for n in level.notes:
        if n["_customData"]["_track"] not in noteTracks:
            noteTracks.append(n["_customData"]["_track"])
    
    # get obstacle tracks
    obstacleTracks = []
    for o in level.obstacles:
        if o["_customData"]["_track"] not in obstacleTracks:
            obstacleTracks.append(o["_customData"]["_track"])
    
    # check if they are used
    for ce in level.customEvents:
        # while I'm at it I might as well check if there's tracks that are being animated
        # but aren't assigned to anything
        if ce["_data"]["_track"] not in obstacleTracks + noteTracks:
            allErrors.append(f"Track '{ce['_data']['_track']}' is animated at {ce['_time']} in {ce['_type']} but is not assigned to any objects.")
            errorData.append(ce)
        
        else:
            if ce["_data"]["_track"] in obstacleTracks:
                obstacleTracks.remove(ce["_data"]["_track"])
            else:
                noteTracks.remove(ce["_data"]["_track"])
    if len(noteTracks) != 0:
        unusedNoteTracks = ', '.join(noteTracks)
        allErrors.append(f'There are {len(noteTracks)} tracks that are unused but assigned to notes:\n{unusedNoteTracks}')
    if len(obstacleTracks) != 0:
        unusedObstacleTracks = ', '.join(obstacleTracks)
        allErrors.append(f'There are {len(obstacleTracks)} tracks that are unused but assigned to obstacles:\n{unusedObstacleTracks}')

    return (allErrors, errorData)