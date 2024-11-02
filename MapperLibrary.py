# -*- coding: utf-8 -*-
"""
Created on 25.02.2023

@author: DarkMatter1
"""
import numpy as np
from PIL import Image, ImageDraw, ImageFont


###############################################################################
# ---Data-Functions------------------------------------------------------------#
###############################################################################


def str2img(image, string, yval, mode="w"):
    # Takes an image and a string and converts the string into image pixels via
    # ASCII code. yval is the position of the pixels
    # Write mode
    if mode == "w":
        # integer array for storage
        ch = np.zeros(len(string), dtype="int")
        for i in range(len(string)):
            # transforms each character into int (ASCII)
            ch[i] = ord(string[i])

        k = len(string) % 4
        for i in range(0, len(string) - k, 4):
            # Always puts the Characters into the 4 channels RGBA
            image.putpixel((i // 4, yval - 1), (ch[i], ch[i + 1], ch[i + 2], ch[i + 3]))

        i = i + 4
        if k == 3:  # Remaining strings that get filled to RGB, RG or R
            image.putpixel((i // 4, yval - 1), (ch[i], ch[i + 1], ch[i + 2], 255))
        elif k == 2:
            image.putpixel((i // 4, yval - 1), (ch[i], ch[i + 1], 255, 255))
        elif k == 1:
            image.putpixel((i // 4, yval - 1), (ch[i], 255, 255, 255))
    # Readmode
    else:
        i = 0
        ch = ""
        while i >= 0:
            # Get the Pixel values
            pixvals = image.getpixel((i, yval - 1))
            for j in range(4):
                # If the value==255 end of String
                if pixvals[j] == 255:
                    i = -1
                    return ch
                # Append the Character to the string
                ch = ch + chr(pixvals[j])
            i = i + 1


def xy2uv(GridDim, hexSize, pos):
    # Converts the parametric xy Coordinates in Pixels

    # Size of an individual Hexagon
    hexLen = 4 * np.floor(hexSize / 2) - 1
    hexHeight = 2 * np.round(np.sqrt(3) * np.floor(hexSize / 2)) - 1
    # Size of the Canvas
    # x=GridDim[0]
    y = GridDim[1]

    # Step between middles
    stepX = (hexLen + hexSize - 2)
    stepY = (hexHeight - 1)

    # stepX/2 due to the shifting nature of the hexagons
    v = pos[0] * stepX / 2
    # If x is odd shift up the y by half a hexagon
    u = abs(pos[1] - y) * stepY - 1
    if np.mod(pos[0], 2) == 1:
        u = u - np.floor(hexHeight / 2)

    u = int(u)
    v = int(v)
    return u, v


###############################################################################
# ---Image-Functions-----------------------------------------------------------#
###############################################################################


def addMargin(pil_img, top, right, bottom, left):
    width, height = pil_img.size
    new_width = width + right + left
    new_height = height + top + bottom
    result = Image.new(pil_img.mode, (new_width, new_height))
    result.paste(pil_img, (left, top))
    return result


def standardMap(BorderSize, Minor, Grayval, Round, LogoText, Title, Map):
    # Start of the process that collects the correct Data, generates the Border,
    # puts the Logo in the correct Spot, adds the coordinates Markers and
    # saves the Metadata once again

    # Load the Map and fetch the metadata
    Map = Map.convert('RGBA')
    sz = Map.size
    data = Map.getpixel((0, 0))
    GridSize = (data[0], data[1])
    Resolution = data[2]

    # Load the Font
    StrikeHeader = ImageFont.truetype("Resources/Standards/StrikeFighter.otf", 18)
    StrikeFighter = ImageFont.truetype("Resources/Standards/StrikeFighter.otf", 13)

    # Make a blank Border around the Map
    Border = Image.new('RGBA', (sz[0] + BorderSize, sz[1] + Minor), (Grayval, Grayval, Grayval, 255))
    image_editable = ImageDraw.Draw(Border)

    # Title
    w, h = image_editable.textsize(Title, font=StrikeHeader)
    image_editable.text((Border.size[0] / 2 - w / 2, 5), Title, (0, 0, 0),
                        font=ImageFont.truetype("Resources/Standards/StrikeFighter.otf", 40))

    # Coordinate Labels on x-Axis
    for i in range(1, GridSize[0]):
        pos = xy2uv(GridSize, Resolution, (i, GridSize[1]))
        w, h = image_editable.textsize(str(i), font=StrikeFighter)
        pos = (pos[1] + BorderSize - w / 2, Minor - 5 - h)
        image_editable.text(pos, str(i), (Grayval - 100, Grayval - 100, Grayval - 100), font=StrikeFighter)
    # Coordinate Labels on y-Axis
    for i in range(GridSize[1]):
        pos = xy2uv(GridSize, Resolution, (0, i))
        w, h = image_editable.textsize(str(i), font=StrikeFighter)
        pos = (BorderSize - 5 - w, pos[0] + Minor - h / 2)
        image_editable.text(pos, str(i), (Grayval - 100, Grayval - 100, Grayval - 100), font=StrikeFighter)

    # Logo in the top left corner
    Logo = Image.open("Resources/" + LogoText).convert('RGBA')
    Logo = Logo.resize((BorderSize, BorderSize))
    Logo = addMargin(Logo, 0, Border.size[0] - BorderSize, Border.size[1] - BorderSize, 0)
    Border = Image.alpha_composite(Border, Logo)

    # Save the metadata in the LowerLeft
    str2img(Border, str((BorderSize, Minor, Grayval, Round, LogoText, Title)), Border.size[1])

    return Map, Border, GridSize, Resolution


def finishing(Border, Map, BorderSize, Minor, offset, Round):
    # Adds the remaining Headers, and combines the Border with the map

    image_editable = ImageDraw.Draw(Border)
    StrikeHeader = ImageFont.truetype("Resources/Standards/StrikeFighter.otf", 18)

    # Ship Locations header
    w, h = image_editable.textsize("Ship Locations", font=StrikeHeader)
    image_editable.text((BorderSize / 2 - w / 2, BorderSize + 25), "Ship Locations", (0, 0, 0), font=StrikeHeader)

    # Round Counter
    w, h = image_editable.textsize("Round " + str(Round + 1), font=StrikeHeader)
    image_editable.text((BorderSize / 2 - w / 2, offset + 25), "Round " + str(Round + 1), (0, 0, 0), font=StrikeHeader)

    # Combine the Map and the Border together
    MapShift = addMargin(Map, Minor, 0, 0, BorderSize)
    BattleMap = Image.alpha_composite(Border, MapShift)
    return BattleMap
