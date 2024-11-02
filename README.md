The Setup consists of:
4 Python programs (Main/Bot/MapInitialiser/MapRunner)
1 Input file (Parameters)

##################################################################################################
Discord Bot Controls:
(can either be activated with ! (public) or !# (private-only availiable sometimes))

!generate [name]
This command generates a map if the excel sheet Parameters is attached, 
if not it fetches the already generated map with the name.
If followed by "labels" the debug map is sent as well
Sends the generated map

!startgame [name]
Starts a gaming scession. The name selects the desired map to be played on.
Sends the blank map

!round
Starts a round, in which the commands can be entered (see Fight preparation/gameplay)

!finish
Ends a round and starts updating the map
Sends the updated map

!stopgame
Stops a gaming scession. Deletes all the different maps which were created during the game 
as well as the Commands and Parameters.

!resources {[name]} {showall}
Without additionals: Sends a list of all the filenames in the resource folder
With showall: Sends all the image files in the resource folder
With name: Sends the appropriate image file
With name + .png attachment: Saves the image in the resource folder

!help
Sends the basic commands
With docu: Sends this text
With param: Sends the Excel file needed to generate the maps

##################################################################################################
##################################################################################################
Map Preparation:
The Parameters.xslx is the way to prepare a Map in advance before the Battle starts
It has two Pages, the Commands and the Mapper

Commands:
x:		Is the number of Hexagons in the horizontal, x direction
y:		Is the number of Hexagons in the vertical, y direction
*Resolution:	*Not required-default:31	Size of the Hexagons.
*Background Image: Choosing the Background image eg "Stars".png

Logo:		Name of the Image eg "Gatewalkers".png
Title:		Title displayed above the Map
*Grayval:	*Not required-default:255	Brightness of the Border 0=Black, 255=White
*BorderSize:	*Not required-default:250	Left width of the Border in px
*Minor:		*Not required-default:75	Top height of the Border in px

Mapper:
The Mapper immidiatly indicates the Range selected in the Commands Pane.
Everywhere within these indications (top an left) Objects can be placed.

Objects have the format:
AABBCC
*AA: (INT)	*Not required-default:1	Scale of the Object
BB:  (STR)	Two letter Code for the Objects
*CC: (INT)	*Not required-default:random	Variation of the Object

##################################################################################################
##################################################################################################
Fight preparation/gameplay:
ShipPos.txt is the parameterList for the Battle game.

xy=0,0 in LLC
qrs=0,0,0 in LLC
(1,0,0) - ⇑1 -up
(-1,0,0)- ⇓1 -down
(0,1,0) - ⇗1 -rightup
(0,-1,0)- ⇙1 -leftdown
(0,0,1) - ⇘1 -rightdown
(0,0,-1)- ⇖1 -leftup

Formats:
add,Faction,Name,posX,posY,*Rotation,*Acceleration
mov,Name,q,r,s
del,Name

Alternatives:
Add Faction Name posX posY *Rotation *Acceleration
Move Name ⇑q ⇗r ⇘s with (⇑⇗⇘⇓⇙⇖) or (q r s)
Delete Name

Format [add]:
Indicator:		add
*Faction:  (STR[1])	Can be p(player), e(enemy), a(ally), anything else->unknown
Name: 	  (STR)		Any name in the ASCII alphabet (a-z,A-Z,0-9, punctations) (so no special characters like äöü...)
posX,posY:(2*INT)	Position of the ship in the xy Coordinates (LLC is (0|0))
*Rotation:(INT)		*Not required-default:0		Determines the rotation of the ship (0=6=up, 1=right-up, 2=right-down...)
*Acceleration:(3*INT)	*Not required-default: 0,0,0	Acceleration in the qrs coordinates System

Format [mov]:
Indicator:		mov
Name:			Name of the ship wanted to move
q,r,s			Acceleration in the qrs coordinates System

Format [del]:
Indicator:		del
Name:			Name of the ship wanted to delete

EXAMPLE:
add,p,OnlyLoc,1,1
add,p,WithRot,1,1,4
add,p,WithAccel,1,1,4,2,2,0
add,e,Enemy,1,1
add,a,Ally,1,1
add,u,Unknown,1,1
mov,AlreadyExistingShip,-1,0,3
del,DestroyedShip

Add Player OnlyLoc 1 1
Add p WithRot 1 1 4
Add p WithAccel 1 1 4 2 2 0
Add e Enemy 1 1
Add a Ally 1 1
Add u Unknown 1 1
Move AlreadyExistingShip ⇓1 ⇘3
Delete DestroyedShip

##################################################################################################
##################################################################################################

The Folder structure required is:
main.py
bot.py
MapInitialiser.py
MapRunner.py
Resources [Folder]
|
|Logos, Backgrounds, Objects
|
|Standards [Folder]
||
||Fonts,ShipIcons, Help
creation [Folder] (Everything below will be created automatically if not existing)
|
|data [Folder]
||
||temporary storage of Parameters and Commands
|
|maps [Folder]
||
||gameplay maps
||
||debug [Folder]
|||
|||debugging maps
