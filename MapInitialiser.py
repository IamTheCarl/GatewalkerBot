# -*- coding: utf-8 -*-
"""
Created on 18.04.2022

@author: DarkMatter1
"""
import numpy as np
import pandas as pd
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance
import os
import MapperLibrary


# Map_Initialiser
# | initMap
# | | hextile
# | | | drawHexagon
# | | gridMaker
# | initObjects
# | | xy2uv
# | | ObjectScatter
# | | | xy2uv
# | | | xy2uv
# | | | addMargin
# | initBattleMap
# | | standardMap
# | | | xy2uv
# | | | xy2uv
# | | | addMargin
# | | | str2img
# | | finishing
# | | | addMargin
# | debugGrid
# | | xy2uv


###############################################################################
# ---BATTLE-MAP DRAWING--------------------------------------------------------#
###############################################################################
def initBattleMap(Map):
    # First main for initialising the Map. It only takes the ini command
    List = pd.read_excel(r'creation/data/Parameters.xlsx', sheet_name='Commands')
    List = List.set_index('Map Dimensions')

    Logo = List.loc["Logo"].at["Value"] + ".png"
    Title = List.loc["Title"].at["Value"]
    Grayval = List.loc["Grayval"].at["Value"]
    BorderSize = List.loc["BorderSize"].at["Value"]
    Minor = List.loc["Minor"].at["Value"]

    if type(Grayval) != int:
        if np.isnan(Grayval):
            Grayval = 255
    Grayval = int(Grayval)
    if type(BorderSize) != int:
        if np.isnan(BorderSize):
            BorderSize = 200
    BorderSize = int(BorderSize)
    if type(Minor) != int:
        if np.isnan(Minor):
            Minor = 100
    Minor = int(Minor)

    Round = -1
    # Generate the fitting Border, Logo, Coordinates...
    Map, Border, GridSize, Resolution = MapperLibrary.standardMap(BorderSize, Minor, Grayval, Round, Logo, Title, Map)
    # Pull everything together
    BattleMap = MapperLibrary.finishing(Border, Map, BorderSize, Minor, BorderSize + 50, Round)
    print("Finished Initalising the Battlemap")
    return BattleMap


###############################################################################
# ---DATA-FUNCTIONS------------------------------------------------------------#
###############################################################################
def formatText(input_lines):
    output_text = ""
    for line in input_lines:
        if line.startswith("Add"):
            try:
                split_line = line.split('"')
                name = split_line[1]
                line = split_line[0] + split_line[2][1:]
                split_line = line.split(" ")
            except:
                split_line = line.split(" ")
                name = split_line[2]
                split_line = split_line[:2] + split_line[3:]
            faction = split_line[1][0].lower()
            pos_x = int(split_line[2])
            pos_y = int(split_line[3])
            rotation = 0
            acceleration = "0,0,0"
            if len(split_line) >= 5:
                rotation = int(split_line[4])
            if len(split_line) == 8:
                acceleration = split_line[5] + " " + split_line[6] + " " + split_line[7]
            output_text += f"add,{faction},{name},{pos_x},{pos_y},{rotation},{acceleration}\n"
        elif line.startswith("Move"):
            try:
                split_line = line.split('"')
                name = split_line[1]
                split_line = split_line[2].split(" ")
            except:
                split_line = line.split(' ')
                name = split_line[1]
                split_line = split_line[1:]
            q, r, s = 0, 0, 0
            for move in split_line[1:]:
                if "⇑" in move:
                    q += int(move[1:])
                elif "⇓" in move:
                    q -= int(move[1:])
                elif "⇗" in move:
                    r += int(move[1:])
                elif "⇙" in move:
                    r -= int(move[1:])
                elif "⇘" in move:
                    s += int(move[1:])
                elif "⇖" in move:
                    s -= int(move[1:])
                else:
                    q = int(split_line[1])
                    r = int(split_line[2])
                    s = int(split_line[3])
            output_text += f"mov,{name},{q},{r},{s}\n"
        elif line.startswith("Delete"):
            try:
                name = line.split('"')[1]
            except:
                name = line.split(" ")[1]
            output_text += f"del,{name}\n"
    return output_text.strip()


###############################################################################
# ---BASE-MAP-DRAWING----------------------------------------------------------#
###############################################################################
def initMap():
    # Read the Execl for the Map Parameters
    List = pd.read_excel(r'creation/data/Parameters.xlsx', sheet_name='Commands')
    List = List.set_index('Map Dimensions')
    xDim = int(List.loc["x"].at["Value"])
    yDim = int(List.loc["y"].at["Value"])
    Resolution = List.loc["Resolution"].at["Value"]
    BgImg = List.loc["Background Image"].at["Value"]
    # Get the GridSize
    GridSize = (xDim, yDim)

    if type(Resolution) != int:
        if np.isnan(Resolution):
            Resolution = 31
    Resolution = int(Resolution)
    if type(BgImg) != str:
        if np.isnan(BgImg):
            BgImg = 1

    # Check if the Values are correct
    if np.mod(Resolution, 2) == 0:
        Resolution = Resolution + 1
    if np.mod(GridSize[0], 2) == 1:
        GridSize = (GridSize[0] + 1, GridSize[1])

    tile, marker = hextile(Resolution)
    # tile=tile+marker
    Grid = gridMaker(tile, GridSize)

    # Get the Grid Sizes
    a = len(Grid)
    b = int(Grid.size / a)

    # The rgb gets filled with white the a is controlled by the Grid
    White = np.ones((a, b, 3))
    Grid = np.dstack((White, Grid))
    HexIm = Image.fromarray(np.uint8(Grid * 100)).convert("RGBA")

    # Blurring the Grid for visual effect
    blurImage = HexIm.filter(ImageFilter.GaussianBlur(1.5))
    HexIm = Image.alpha_composite(HexIm, blurImage)

    BgdImage = 0
    if BgImg == 1:
        # Black Background
        BgdImage = np.zeros((a, b))
        BgdImage = Image.fromarray(np.uint8(BgdImage)).convert("RGBA")
        # HexIm=Image.alpha_composite(Black,HexIm)
    if type(BgImg) == str:
        imageName = "Resources/" + BgImg + ".png"
        BgdImage = Image.open(imageName).convert('RGBA')
        BgdImage = BgdImage.resize((b, a))
        BgdImage = ImageEnhance.Brightness(BgdImage).enhance(0.3)
        # HexIm=Image.alpha_composite(Picture,HexIm)
    print("Finished Initalising the Background")
    return BgdImage, HexIm, GridSize, Resolution


def hextile(HexRes):
    #  /   \
    # --|   |--
    #  \___/

    # Draws the middle Hexagon
    hexagon = drawHexagon(HexRes)
    height = len(hexagon)
    side = int(np.size(hexagon) / height)
    halfs = int(np.floor(side / 2)) + 2
    halfh = int(np.floor(height / 2))

    # Prepare the lines on the sides
    filler = np.zeros((halfh, int(np.floor(halfs / 2))))
    line = np.ones(int(np.floor(halfs / 2)))
    side = np.vstack((filler, line, filler))

    # Stick the Lines onto the Hexagon
    tile = np.hstack((side, hexagon, side))

    # Rmove the outer edges to avoid doubling at the edges
    tile = tile[1:, :-1]

    # Marker for the Middle
    height = len(tile)
    side = int(np.size(tile) / height)
    middlemark = tile * 0
    middlemark[height - 1, 0] = 1
    middlemark[int(np.floor(height / 2) - 1), int(side / 2)] = 1
    return tile, middlemark


def drawHexagon(sidelen):
    # Diagonals
    sidelen = int(np.floor(sidelen / 2))
    # Prepare a canvas with size s/2 and sqrt(3)*s/2
    zero = np.zeros((sidelen, round(np.sqrt(3) * sidelen)))
    height = int(np.size(zero) / sidelen)

    # implicit formula 0=sqrt(3)*x-y
    for i in range(height):
        for j in range(sidelen):
            if abs(np.sqrt(3) * j - i) < 1:
                zero[j, i] = 1

    # Building up the Hexagonsides
    zero = np.transpose(zero)
    dzero = np.flip(zero, 0)
    dzero = dzero[1:, :]
    dzero = np.vstack((zero, dzero))

    # Building up the middle
    middleline = np.ones(sidelen * 2 - 1)
    middle = np.zeros((len(dzero) - 2, sidelen * 2 - 1))

    # Building the whole Hexagon
    middle = np.vstack((middleline, middle, middleline))

    hexagon = np.hstack((np.flip(dzero, 1), middle, dzero))
    # HexIm=Image.fromarray(np.uint8(hexagon*255))
    # HexIm.show()
    return hexagon


def gridMaker(tile, CanvasDim):
    # due to the shape of the base tile x will always be even
    x = CanvasDim[0]
    y = CanvasDim[1]
    x = int(x / 2)
    xcanvas = tile
    # Stacks the Hex-Tiles sideways then on top to create the grid
    for i in range(x - 1):
        xcanvas = np.hstack((xcanvas, tile))
    ycanvas = xcanvas
    for i in range(y - 1):
        ycanvas = np.vstack((ycanvas, xcanvas))
    return ycanvas


###############################################################################
# ---OBJECT-DRAWING------------------------------------------------------------#
###############################################################################
def initObjects(GridSize, Resolution):
    # Reads the Objects from the Excel file
    List = pd.read_excel(r'creation/data/Parameters.xlsx', sheet_name='Mapper')
    List = List.set_index('Coords')

    # Generates an empty canvas to stack the Objects onot
    param = MapperLibrary.xy2uv(GridSize, Resolution, (GridSize[0], 0))
    param = (param[1], param[0] + 1)
    Foreground = Image.new('RGBA', (param))

    # For every Cell in the Map go through
    sz = List.shape
    try:
        for x in range(sz[1]):
            for y in range(sz[0]):
                Object = List.loc[y].at[x]
                if isinstance(Object, str):
                    try:
                        Scale = int(Object[:2])
                        Object = Object[2:]
                    except:
                        try:
                            Scale = int(Object[0])
                            Object = Object[1:]
                        except:
                            Scale = 1

                    Name = Object[:2].lower()
                    Object = Object[2:]

                    count = sum(f.startswith(Name) for f in os.listdir('Resources'))
                    Variant = np.random.randint(count) if not Object else Object
                    String = f"Resources/{Name}_{Variant}.png"

                    try:
                        Picture = Image.open(String).convert('RGBA')
                    except:
                        Picture = Image.open("Resources/Test.png").convert('RGBA')

                    newForeground = ObjectScatter(Picture, Resolution, GridSize, (x, y), Scale)
                    Foreground = Image.alpha_composite(newForeground,
                                                       Foreground) if Scale > 4 else Image.alpha_composite(Foreground,
                                                                                                           newForeground)
    except Exception as e:
        print(e)
    Foreground.putpixel((0, 0), (GridSize[0], GridSize[1], Resolution, 255))
    print("Finished Initalising the Foreground")
    return Foreground


def ObjectScatter(Picture, Resolution, GridSize, pos, ObjectSize=1):
    # Canvas Size
    param = MapperLibrary.xy2uv(GridSize, Resolution, (GridSize[0], 0))
    param = (param[0] + 1, param[1])

    # Hexagon Size
    hexLen = int(4 * np.floor(Resolution / 2) - 1)
    hexHeight = int(2 * np.round(np.sqrt(3) * np.floor(Resolution / 2)) - 1)

    # Hexagon Size times the Size
    k = (2 * ObjectSize - 2)
    hexLen = (hexLen + Resolution) * ObjectSize - Resolution - k
    k = 2 * ObjectSize - 1
    hexHeight = ((hexHeight - 1) * k) + 1

    dim = np.min((hexLen, hexHeight))

    # Load Image
    Picture = Picture.resize((dim, dim))
    posNew = MapperLibrary.xy2uv(GridSize, Resolution, pos)

    # Add Margin
    Left = int(posNew[1] - np.floor(dim / 2))
    Right = int(param[1] - (posNew[1] + np.ceil(dim / 2)))
    Top = int(posNew[0] - np.floor(dim / 2))
    Bottom = int(param[0] - (posNew[0] + np.ceil(dim / 2)))

    Picture = MapperLibrary.addMargin(Picture, Top, Right, Bottom, Left)

    return Picture


def debugGrid(Canvas, Resolution, GridSize, map_name):
    # Inputs: Canvas(Image)
    # Adds labels to the Grid. In itself closed function, returns nothing, saves an image
    draw = ImageDraw.Draw(Canvas)
    xmax = GridSize[0]
    ymax = GridSize[1]
    for x in range(xmax + 1):
        for y in range(ymax + 1):
            Coords = MapperLibrary.xy2uv(GridSize, Resolution, (x, y))
            posx = Coords[1]
            posy = Coords[0]
            # Write the x and y Coordinates into the Grid
            draw.text((posx - Resolution / 2, posy - Resolution / 2), str(x) + "," + str(y),
                      (int(255 * x / xmax), int(255 * y / ymax), 255))
    Canvas.save(f'creation/maps/debug/{map_name}_debug.png')
    return


###############################################################################
# ---MAIN----------------------------------------------------------------------#
###############################################################################
def Map_Initialiser(file_data, map_name):
    # previous main
    if file_data != -1:
        # save the contents of the BytesIO object to a file
        with open('creation/data/Parameters.xlsx', 'wb') as f:
            f.write(file_data.getvalue())

    BgdImage, HexIm, GridSize, Resolution, = initMap()
    Foreground = initObjects(GridSize, Resolution)

    HexIm = Image.alpha_composite(Foreground, HexIm)
    HexIm = Image.alpha_composite(BgdImage, HexIm)

    BattleMap = initBattleMap(HexIm)
    BattleMap.save('creation/maps/' + str(map_name) + '0.png')
    debugGrid(HexIm, Resolution, GridSize, map_name)
    return BattleMap
