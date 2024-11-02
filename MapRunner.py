# -*- coding: utf-8 -*-
"""
Created on 18.04.2022

@author: DarkMatter1
"""
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import MapperLibrary

# Map_Runner
# | updateMap
# | | str2img
# | | clean
# | | clean
# | | standardMap
# | | | xy2uv
# | | | xy2uv
# | | | addMargin
# | | | str2img
# | | clean
# | | str2img
# | | normData
# | | adder
# | | | xy2qrs
# | | | qrs2xy
# | | placeShips
# | | | xy2uv
# | | | addImageOver
# | | | | addMargin
# | | | str2img
# | | finishing
# | | | addMargin


###############################################################################
# ---Image-Functions-----------------------------------------------------------#
###############################################################################

def addImageOver(pil_background, pil_foreground, pos):
    # Takes an image and places it over the background (centered)
    sz = pil_background.size
    szSmall = pil_foreground.size
    left = pos[1] - int(np.floor(szSmall[0] / 2))
    top = pos[0] - int(np.floor(szSmall[1] / 2))
    bottom = sz[1] - pos[0] - int(np.ceil(szSmall[1] / 2))
    right = sz[0] - pos[1] - int(np.ceil(szSmall[0] / 2))
    pil_foreground = MapperLibrary.addMargin(pil_foreground, top, right, bottom, left)
    pil_background = Image.alpha_composite(pil_background, pil_foreground)
    return pil_background


###############################################################################
# ---Data-Functions------------------------------------------------------------#
###############################################################################


def normData(data):
    # Important function for the "add" command - this way the data is reliable
    # If no faction is given it defaults to "u"
    if len(data[1]) != 1:
        data.insert(1, "u")
    k = len(data)
    # If no facing value is given, it defaults to up
    if k > 5:
        Facing = int(data[5]) % 6
    else:
        data.append(0)
    # If no acceleration value is given, it defaults to 0
    if k < 8:
        data.extend([0, 0, 0])
    return data


def clean(data):
    # Clean the string from '
    data = data.replace(" '", "")
    data = data.replace("'", "")
    data = data.replace('"', "")
    return data


###############################################################################
# ---Coordinate-System-Converters----------------------------------------------#
###############################################################################

def xy2qrs(coords):
    # Converts the xy Coordinates (starting from the bottom left) into qrs Coords
    x = coords[0]
    y = coords[1]
    q = int(x)
    s = int(y - np.floor(x / 2))
    r = int(q + s)
    return q, r, s


def qrs2xy(coords):
    # Converts the qrs Coordinates (starting from the bottom left) into xy Coords
    q = coords[0]
    s = coords[2]
    x = int(q)
    y = int(s + np.floor(q / 2))
    return x, y


###############################################################################
# ---Ship-Functions------------------------------------------------------------#
###############################################################################

def adder(pos, add):
    # CAUTION, NOT COMMUTATIVE
    pos = xy2qrs(pos)
    q = pos[0]
    r = pos[1]
    s = pos[2]

    # Adds the q-component to the position
    firstpos = add[0]
    r = r + firstpos
    s = s + firstpos

    # Adds the r-component to the position
    secondpos = add[1]
    q = q + secondpos
    r = r + secondpos

    # Adds the s-component to the position
    thirdpos = add[2]
    q = q + thirdpos
    s = s - thirdpos

    newpos = qrs2xy((q, r, s))

    return newpos


def placeShips(Border, Map, shipData, BorderSize, GridSize, Resolution):
    # Goes through every ship and places it on the map, as well as the descriptive
    # Text on the side

    image_editable = ImageDraw.Draw(Border)
    StrikeFighter = ImageFont.truetype("Resources/Standards/StrikeFighter.otf", 13)
    # Load the Ship Icons
    ShipPlayer = Image.open("Resources/Standards/ShipPlayer.png").convert('RGBA')
    ShipEnemy = Image.open("Resources/Standards/ShipEnemy.png").convert('RGBA')
    ShipAlly = Image.open("Resources/Standards/ShipAlly.png").convert('RGBA')
    ShipUnknown = Image.open("Resources/Standards/ShipUnknown.png").convert('RGBA')

    # For every ship in the list
    for i in range(len(shipData)):
        Name = shipData[i][1]
        pos = (int(shipData[i][2]), int(shipData[i][3]))
        Facing = int(shipData[i][4])

        offset = BorderSize + 50 + 13 * i
        # Icon choosing depended on faction/Text on the side
        if shipData[i][0] == "p":
            Icon = ShipPlayer
            image_editable.text((20, offset), Name + " " + str(pos), (0, 0, 0), font=StrikeFighter)
        elif shipData[i][0] == "e":
            Icon = ShipEnemy
            image_editable.text((20, offset), Name + " " + str(pos), (200, 0, 0), font=StrikeFighter)
        elif shipData[i][0] == "a":
            Icon = ShipAlly
            image_editable.text((20, offset), Name + " " + str(pos), (0, 200, 0), font=StrikeFighter)
        else:
            Icon = ShipUnknown
            image_editable.text((20, offset), Name + " " + str(pos), (200, 200, 200), font=StrikeFighter)

        # Rotate the ship accordingly
        IconRot = Icon.rotate(-60 * Facing, resample=Image.BICUBIC)

        # Place the marker on the map
        PosUV = MapperLibrary.xy2uv(GridSize, Resolution, pos)
        Map = addImageOver(Map, IconRot, PosUV)
        Map_editable = ImageDraw.Draw(Map)
        Map_editable.text((PosUV[1] + 5, PosUV[0] - Resolution / 2), Name, (200, 200, 200), font=StrikeFighter)

        # Add the metadata on the bottom left
        MapperLibrary.str2img(Border, str(shipData[i]), Border.size[1] - i - 1)

    return Border, Map, offset


###############################################################################
# ---MAIN----------------------------------------------------------------------#
###############################################################################

def updateMap(Previous, Filename, BaseMap):
    # Takes the Previous map and updates it. It collects the data, as well as
    # the new instructions and saves it again.
    # Extract the Metadata - Image related
    data = MapperLibrary.str2img(Previous, "", Previous.size[1], "r")
    data = data.replace("(", "")
    data = data.replace(")", "")
    data = data.split(",")

    BorderSize = int(data[0])
    Minor = int(data[1])
    Grayval = int(data[2])
    Round = int(data[3]) + 1
    Logo = clean(data[4])
    Title = clean(data[5])
    Blank = BaseMap.crop((BorderSize, Minor, Previous.size[0], Previous.size[1]))
    # Generate the fitting Border, Logo, Coordinates...
    Map, Border, GridSize, Resolution = MapperLibrary.standardMap(BorderSize, Minor, Grayval, Round, Logo, Title, Blank)

    # Extract the Shipdata from the Lowerleft corner
    i = 1
    shipData = []
    while i >= 0:
        newdata = clean(MapperLibrary.str2img(Previous, "", Previous.size[1] - i, "r"))
        newdata = newdata.replace("[", "")
        newdata = newdata.replace("]", "")
        newdata = newdata.split(",")
        if len(newdata) != 1:
            shipData.append(newdata)
            i = i + 1
        else:
            i = -1

    # Open new instructions and split them into lines
    f = open(Filename, "r")
    f = f.read()
    f = f.splitlines()
    # Walk through for every instruction
    for i in range(len(f)):
        new = f[i]
        new = new.split(",")
        mode = new[0]
        # Add a new ship to the map
        if mode == "add":
            new = normData(new)
            NameAdd = new[2]
            # Check if the ship already exists, then do not add it
            valid = True
            for j in range(len(shipData)):
                Name = shipData[j][1]
                if NameAdd == Name:
                    valid = False
            if valid == True:
                shipData.append(new[1:])

        # Move an existing ship on the map (with Newtonian Physics)
        elif mode == "mov":
            NameMov = new[1]
            for j in range(len(shipData)):
                Name = shipData[j][1]
                if NameMov == Name:
                    # Takes the Position, Acceleration, as well as previous Acceleration
                    # and calculates the next position and heading
                    pos = (int(shipData[j][2]), int(shipData[j][3]))
                    previousAccel = np.array((int(shipData[j][5]), int(shipData[j][6]), int(shipData[j][7])))
                    accel = np.array((int(new[2]), int(new[3]), int(new[4])))
                    accel = accel + previousAccel
                    newpos = adder(pos, accel)
                    shipData[j][2] = newpos[0]
                    shipData[j][3] = newpos[1]
                    shipData[j][5] = accel[0]
                    shipData[j][6] = accel[1]
                    shipData[j][7] = accel[2]

                    # Heading being determined by the direction of the maximum
                    # acceleration
                    if abs(accel[0]) >= max(abs(accel[1]), abs(accel[2])):
                        if accel[0] > 0:
                            shipData[j][4] = 0
                        else:
                            shipData[j][4] = 3

                    if abs(accel[1]) >= max(abs(accel[0]), abs(accel[2])):
                        if accel[1] > 0:
                            shipData[j][4] = 1
                        else:
                            shipData[j][4] = 4

                    if abs(accel[2]) >= max(abs(accel[0]), abs(accel[1])):
                        if accel[2] > 0:
                            shipData[j][4] = 2
                        else:
                            shipData[j][4] = 5
                    break

        # Delete a ship from the Map
        elif mode == "del":
            NameDel = new[1]
            for j in range(len(shipData)):
                Name = shipData[j][1]
                if NameDel == Name:
                    shipData.pop(j)
                    break
    # With the new ships added, old ones moved or deleted, place the Ships at their correct locations
    Border, Map, offset = placeShips(Border, Map, shipData, BorderSize, GridSize, Resolution)
    # Pull everything together
    BattleMap = MapperLibrary.finishing(Border, Map, BorderSize, Minor, offset, Round)
    return BattleMap


def Map_Runner(round, map_name):
    #previous main
    Filename = "creation/data/commands.txt"
    try:
        string = 'creation/maps/' + str(map_name) + str(round - 1) + '.png'
        zerostring = 'creation/maps/' + str(map_name) + '0.png'
        BaseMap = Image.open(zerostring).convert('RGBA')
        BattleMap = Image.open(string).convert('RGBA')

        BattleMap = updateMap(BattleMap, Filename, BaseMap)
        print("Map ready for next round")
        BattleMap.save('creation/maps/' + str(map_name) + str(round) + '.png')
        return BattleMap
    except:
        print("Please first initialize the Map first")
