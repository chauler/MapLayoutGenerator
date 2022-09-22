from operator import index
import random
import math
from PIL import Image, ImageDraw, ImageTk
import tkinter as tk
from tkinter import NW, ttk
import UIHandling
import time

FLOOR = (51, 23, 12)
DOOR = (146, 41, 41)
WALL = (93, 89, 97)
EMPTY = (0, 0, 0)
COLORLIST = [EMPTY, FLOOR, WALL, DOOR, WALL, EMPTY, WALL, EMPTY, WALL]
DIR = [[1,0],[0,1],[-1,0],[0,-1]]

class Room:
    def __init__(self, maxSize=10):
        self.length = random.randint(4,maxSize-1) #-1 because of how I calculate the points of the rectangles (x + length) with x of 0 and size of 5, shape would go 0-5, size 6
        self.height = random.randint(4,maxSize-1)
        self.x = None #no coordinates until room is placed
        self.y = None
    def UpdateVertices(self, coords:list): #sets a rooms x,y coords
        self.x = coords[0]
        self.y = coords[1]

class Square:
    def __init__(self):
        self.status:int = 0 #0: empty 1: floor 3: door 2,4,6,8: wall

#Used in Map objects for pathfinding
class Graph:
    def __init__(self, edges, vertices, adjList):
        self.edges = edges #Generally a list of tuples
        self.vertices = vertices #List of squares
        self.adjList = adjList #Dictionary

#Used in pathfinding
class Node:
    parent = None
    def __init__(self, coords, parent=None):
        self.coords:tuple = coords
        self.f = 999999 #Combined total distance
        self.g = 999999 #Distance from parent node
        self.h = 0 #Estimated distance to end node
        self.parent = parent
    def __eq__(self, other):
        return self.coords == other.coords

class Map:
    ppi = 10
    numrooms = 10
    roomsize = 10
    animate = True

    def __init__(self, size:int, **params):
        self.size = size
        self.grid = [[Square() for x in range(size)] for y in range(size)] #2D array of default squares
        self.rooms = []
        Map.ppi = params.get('ppi', Map.ppi)
        Map.numrooms = params.get('numrooms', Map.numrooms)
        Map.roomsize = params.get('roomsize', Map.roomsize)
        self.minx = self.size
        self.maxx = 0
        self.miny = self.size
        self.maxy = 0
        self.xsize = 0
        self.ysize = 0
        self.graph = None #stored as (x,y):[(x,y),(x,y)]
        self.nodes = [] #stored as (x,y)
        self.animCache = AnimationCache()

    #Used to get rid of empty space on the sides of the generated grid
    def TrimGrid(self):
        #Iterates entire grid, updating min and max values based on the farthest walls in each direction
        for indexy, y in enumerate(self.grid):
            for indexx, x in enumerate(y):
                if x.status > 1: #if cell is wall
                    self.miny = indexy if indexy < self.miny else self.miny
                    self.maxy = indexy if indexy > self.maxy else self.maxy
                    self.minx = indexx if indexx < self.minx else self.minx
                    self.maxx = indexx if indexx > self.maxx else self.maxx

        #Initialize new shrunken grid, copy values
        newGrid = [[Square() for x in range(self.minx, self.maxx+1)] for y in range(self.miny, self.maxy+1)]
        for indexy, y, in enumerate(newGrid):
            for indexx, x in enumerate(y):
                newGrid[indexy][indexx] = self.grid[indexy+self.miny][indexx+self.minx]

        #Update the map's grid and sizes
        self.grid = newGrid
        self.xsize = self.maxx-self.minx+1
        self.ysize = self.maxy-self.miny+1

    def GenDoors(self):
        doorGroups = []
        doors = []

        #Loop through entire grid horizontally searching for valid locations for doors.
        #Tile is valid if it is a wall with 2 adjacent floors, indicating rooms on both sides
        for indexy, y in enumerate(self.grid):
            for indexx, x in enumerate(y):
                #Skip everything that isn't a wall
                if indexx == 0 or indexx == self.xsize-1 or indexy==0 or indexy==self.ysize-1 or x.status == 0 or x.status == 1:
                    continue

                #Generate lists of horizontally adjacent doorable tiles
                if self.grid[indexy+1][indexx].status==1 and self.grid[indexy-1][indexx].status ==1: #if doorable
                    doors.append(x)
                elif doors != []: #if not doorable and list isn't empty, then that's the end of a group
                    doorGroups.append(doors)
                    doors = []

        #Loop through entire grid vertically
        for x in range(self.xsize):
            for y in range(self.ysize):
                    if x == 0 or x == self.xsize-1 or y==0 or y==self.ysize-1 or self.grid[y][x].status == 0 or self.grid[y][x].status == 1:
                        continue
                    #Generate lists of vertically adjacent doorable tiles
                    if self.grid[y][x+1].status==1 and self.grid[y][x-1].status ==1: #if doorable
                        doors.append(self.grid[y][x])
                    elif doors != []:
                        doorGroups.append(doors)
                        doors = []

        #Generate 1 door from each group
        for group in doorGroups:
            door = random.choice(group)
            door.status = 3

    #Creates a graph from the Map's grid with each walkable tile as a node.
    def CreateGraph(self):
        edges = []
        vertices = []
        adjList = {}
        for y in range(self.ysize):
            for x in range(self.xsize): #Iterate through tiles in relevant portion of map
                if self.grid[y][x].status == 1 or self.grid[y][x].status == 3: #If tile is a floor or door, meaning it is traversable, make it a node on the graph
                    vertices.append(Node((x,y)))
                    tempadj = []
                    #Search adjacent nodes for walkable tiles
                    if self.grid[y][x-1].status == 1 or self.grid[y][x-1].status == 3:
                        edges.append(((x,y),(x-1,y)))
                        tempadj.append((x-1, y))
                    if self.grid[y][x+1].status == 1 or self.grid[y][x+1].status ==3:
                        edges.append(((x,y),(x+1,y)))
                        tempadj.append((x+1, y))
                    if self.grid[y-1][x].status == 1 or self.grid[y-1][x].status == 3:
                        edges.append(((x,y),(x,y-1)))
                        tempadj.append((x, y-1))
                    if self.grid[y+1][x].status == 1 or self.grid[y+1][x].status ==3:
                        edges.append(((x,y),(x,y+1)))
                        tempadj.append((x, y+1))
                    adjList.update({(x,y) : tempadj}) #Add vertex and its list of edges to dictionary
        self.graph = Graph(edges, vertices, adjList)

class App(tk.Tk):
    def __init__(self, **params):
        super().__init__()
        self.tk.call("source", "./Assets/azure.tcl")
        self.tk.call("set_theme", "dark")

        #Window attributes
        self.title("Map Generator")
        icon = ImageTk.PhotoImage(file = "./Assets/icon.png")
        self.wm_iconphoto(False, icon)

        self.bind('<Configure>', lambda event: UIHandling.onResize(event, self))

        #Initialize widgets
        self.img:Image = None
        self.imgtk:ImageTk = None
        self.canvasFrame = ttk.Frame(self, width=750, height=750)
        self.map = Map(0)
        self.UIFrame = ttk.Frame(self)
        self.canvas = tk.Canvas(self.canvasFrame, width= 750, height= 750, bg='#f0f0c0')
        self.imageDisplay = self.canvas.create_image(0, 0, anchor=NW, tags='image')
        self.canvas.bind("<Button-1>", lambda event: UIHandling.CanvasOnClick(event, self))
        self.roomNumText = ttk.Label(self.UIFrame, text='# of Rooms: ')
        self.roomNum = ttk.Label(self.UIFrame, text="10")
        self.maxSizeText = ttk.Label(self.UIFrame, text="Max Room Size:")
        self.maxSize = ttk.Label(self.UIFrame, text="10")
        self.ppiText = ttk.Label(self.UIFrame, text="Pixels per tile:")
        self.ppi = ttk.Label(self.UIFrame, text="10")
        self.roomNumScale = ttk.Scale(self.UIFrame, from_=1, to=100, value=10, command= lambda event: self.roomNum.configure(text='{:.0f}'.format(math.floor(self.roomNumScale.get()))))
        self.maxSizeScale = ttk.Scale(self.UIFrame, from_=6, to=20, value=10, command= lambda event: self.maxSize.configure(text='{:.0f}'.format(math.floor(self.maxSizeScale.get()))))
        self.ppiScale = ttk.Scale(self.UIFrame, from_=5, to=50, value=10, command= lambda event: self.ppi.configure(text='{:.0f}'.format(math.floor(self.ppiScale.get()))))
        self.animateValue = tk.IntVar()
        self.animateButton = ttk.Checkbutton(self.UIFrame, text='Animate?', variable=self.animateValue)
        self.genButton = ttk.Button(self.UIFrame, text='Generate', width=15, command= lambda: UIHandling.ButtonOnClick(math.floor(self.roomNumScale.get()), math.floor(self.maxSizeScale.get()), math.floor(self.ppiScale.get()), self.animateValue.get(), self))

        #Place and configure widgets
        self.canvas.grid(row=0, column=0, sticky='nsew')
        self.canvasFrame.grid(row=0,column=0, sticky='nsew')
        self.grid_columnconfigure(0, minsize=750, weight=1)
        self.grid_rowconfigure(0, minsize=750, weight=1)
        self.canvasFrame.grid_columnconfigure(0, minsize=750, weight=1)
        self.canvasFrame.grid_rowconfigure(0, minsize=750, weight=1)
        self.canvasFrame.grid_propagate(False)
        self.ppiText.grid(row=0, column=0)
        self.ppi.grid(row=1, column=0)
        self.ppiScale.grid(row=2, column=0)
        self.roomNumText.grid(row=3, column=0)
        self.roomNum.grid(row=4,column=0)
        self.roomNumScale.grid(row=5, column=0, sticky='n')
        self.maxSizeText.grid(row=6,column=0)
        self.maxSize.grid(row=7, column=0)
        self.maxSizeScale.grid(row=8, column=0)
        self.genButton.grid(row=9, column=0)
        self.animateButton.grid(row=10, column=0)
        self.UIFrame.grid(row=0,column=1)

    def DisplayImage(self, resolution = None):
        if resolution == None:
            resolution = (self.canvas.winfo_width(), self.canvas.winfo_height())
        
        self.imgtk = ImageTk.PhotoImage(self.img.resize((resolution[0], resolution[1])))
        self.canvas.itemconfig('image', image = self.imgtk)

class AnimationCache:
    def __init__(self):
        self.steps = []
        self.center = None



def DrawPicture(map:Map):
    ppi = Map.ppi
    map.biggerDim = map.maxx-map.minx if map.maxx-map.minx > map.maxy-map.miny else map.maxy-map.miny #get the bigger dimension so that the image is always square
    image = Image.new("RGB", (map.biggerDim*ppi+ppi, map.biggerDim*ppi+ppi))
    draw = ImageDraw.Draw(image)

    #for each cell, draw (ppi) pixels
    for y in range(map.ysize):
        for x in range(map.xsize):
            if map.grid[y][x].status == 1: #Floor, draw brown
                draw.rectangle([x*ppi,y*ppi,(x*ppi)+ppi,(y*ppi)+ppi], outline="black", fill = FLOOR)
            elif map.grid[y][x].status == 3: #Door, draw red
                draw.rectangle([x*ppi,y*ppi,(x*ppi)+ppi,(y*ppi)+ppi], outline="black", fill = DOOR)
            elif map.grid[y][x].status > 1: #Wall, draw grey
                draw.rectangle([x*ppi,y*ppi,(x*ppi)+ppi,(y*ppi)+ppi], outline="black", fill = WALL)
    return image

def GenRooms(rooms):
    for x in range(Map.numrooms):
        rooms.append(Room(Map.roomsize))
    
#Sum length and height of rooms, returns the bigger dimension to ensure map is big enough for all rooms
def GetMaxDimension(rooms):
    totalLength=0
    totalHeight=0

    for room in rooms:
        totalLength += room.length
        totalHeight += room.height

    return totalLength if totalLength > totalHeight else totalHeight

def PlaceRooms(rooms, placedRooms, map):
    coord = [map.size // 2, map.size // 2]
    map.animCache.center = [map.size // 2, map.size // 2]
    #dir = [[1,0],[0,1],[-1,0],[0,-1]]

    #Start by taking 10 steps from center.
    for i in range(10):
        #Repeats until the taken step is valid.
        while True:
            move = random.choice(DIR)
            coord[0] += move[0]
            coord[1] += move[1]
            #map.animCache.steps.append((move[0],move[1]))
            map.animCache.steps.append(DIR.index(move))
            if coord[0] >= map.size or coord[1] >= map.size or coord[0] < 0 or coord[1] < 0: #go oob
                coord[0] -= move[0] #undo move and try again
                coord[1] -= move[1]
                map.animCache.steps.append(DIR.index([-move[0],-move[1]]))
            else: #breaks only if move is valid and doesnt go oob
                break

    #Place each room individually
    for room in rooms:
        #Place the room on a hypothetical position, then adjust position in while loop
        room.UpdateVertices(coord) 
        #Loop True for invalid position, run until valid
        while CheckCollision(room, placedRooms, map) or CheckDisconnected(room, placedRooms, map):
            move = random.choice(DIR)
            coord[0] += move[0]
            coord[1] += move[1]
            #map.animCache.steps.append((move[0],move[1]))
            map.animCache.steps.append(DIR.index(move))
            #If move takes us out of bounds, undo and loop
            if coord[0] >= map.size or coord[1] >= map.size or coord[0] < 0 or coord[1] < 0:
                coord[0] -= move[0]
                coord[1] -= move[1]
                #map.animCache.steps.append((-move[0],-move[1]))
                map.animCache.steps.append(DIR.index([-move[0],-move[1]]))

            room.UpdateVertices(coord) #update with new coords, try again

        placedRooms.append(room) #add room to list for later collision checks
        for x in range(room.x, room.x+room.length+1): #for each tile in the room, update the maps grid
            for y in range(room.y, room.y+room.height+1):
                    if x == room.x or y == room.y or x == room.x+room.length or y == room.y+room.height:
                        map.grid[y][x].status += 2 #make walls 2
                    else:
                        map.grid[y][x].status = 1 #make cells occupied

#Returns true if given room would collide with previously placed rooms. False otherwise.
def CheckCollision(room, rooms, map):
    if room.x + room.length >= map.size or room.y + room.height >= map.size: #checking with map bounds
        return True

    #Basic 2D collision checking with existing rooms. Allow walls to overlap with each other but not with floor tiles.
    for obj in rooms:
        if room is obj:
            continue
        elif room.x < obj.x+obj.length and room.x+room.length > obj.x and room.y < obj.y+obj.height and room.y+room.height > obj.y:
            return True

    #TODO: Fix this to look for 3 *consecutive* overlapping wall tiles. 3 corners could overlap, giving no valid door location.
    #Counts existing wall tiles overlapping with room. If >3, there's a good chance the room will have a valid door placement.
    count=0
    for y in range(room.y, room.y+room.height+1):
        for x in range(room.x, room.x+room.length+1):
            count = count+1 if map.grid[y][x].status > 1 else count

    if count < 3 and len(rooms) != 0:
        return True

    return False
    
def GenerateMap():
    rooms = [] #initial roomlist
    placedRooms = [] #rooms already placed in map, this is used for collision checking

    GenRooms(rooms)

    maxDimension = GetMaxDimension(rooms)

    map = Map(15+maxDimension*2) #generates map big enough for the rooms + a buffer

    #Room and door generation
    PlaceRooms(rooms, map.rooms, map)
    map.TrimGrid() #grab the indices of the min and max x and y positions that aren't empty. Will use these to draw to eliminate black space around the layout
    map.GenDoors()
    map.CreateGraph()
    newImage = DrawPicture(map)
    return map, newImage

#Takes in a (x,y) tuple, draws associated square in given color. Kwargs: color: (rr,gg,bb) or color keyword.
def DrawOnCanvas(cell:tuple, window, **params):
    draw = ImageDraw.Draw(window.img)
    draw.rectangle((cell[0]*Map.ppi, cell[1]*Map.ppi, cell[0]*Map.ppi+Map.ppi, cell[1]*Map.ppi+Map.ppi), outline = "black", fill = params.get('color', "green"))

#A* pathfinding, takes in a map as a parameter
def FindPath(map):
    #given list of 2 (x,y) for starting and ending nodes
    #given adjacency list, keys are (x,y)
    #Modify return list with path
    openList = [] #Unsearched nodes
    closedList = [] #Searched nodes
    startNode = Node(map.nodes[0])
    endNode = Node(map.nodes[1])
    openList.append(startNode) #Search from startNode
    while openList != []: #Loop until no nodes to search
        #f is estimated cost to a node + estimated cost from node to the end
        #Sort openlist by lowest to highest f and search from the start.
        openList.sort(key=lambda item: item.f)
        currNode = openList.pop(0)
        closedList.append(currNode)

        if currNode == endNode:
            pathList = []
            while currNode is not None: #Backtracks from currNode to the start
                pathList.append(currNode.coords)
                currNode = currNode.parent
            return pathList

        childList = []
        for item in map.graph.adjList[currNode.coords]: #Generate a new node for each edge from this node
            childList.append(Node(item, currNode))

        #Calculate the costs of all the children from this node
        for child in childList:
            #if this square has already been searched, skip
            if [closedChild for closedChild in closedList if closedChild == child] != []:
                continue

            child.g = currNode.g + 1
            child.h = (abs(child.coords[0] - endNode.coords[0]) + abs(child.coords[1] - endNode.coords[1])) #manhattan distance.
            child.f = child.g + child.h

            #If theres a cheaper path to this node already, dont add this path to the open list
            if [openChild for openChild in openList if openChild == child and child.g >= openChild.g] != []:
                continue

            openList.append(child)

    #Returns if loop ended without finding a path
    return 'Failed'

#Called from PlaceRooms(). Returns True if disconnected, continuing the search for valid location. False otherwise, causing room to be placed.
def CheckDisconnected(room, placedRooms, map):
    if placedRooms == []: #If this is the first room being placed, it doesn't need a connection
        return False

    #Scan entire room for connections
    for x in range(room.x, room.x+room.length+1):
        for y in range(room.y, room.y+room.height+1):
            #Loop continues until it finds a single connection. If it finds one, returns True.
            if x == room.x or x == room.x+room.length or y == room.y or y == room.y+room.height:
                if x==0 or x==map.size-1 or y==0 or y==map.size-1 or x==room.x and y==room.y or x==room.x and y==room.y+room.height or x==room.x+room.length and y==room.y or x==room.x+room.length and y==room.y+room.height:
                    continue
                #Room has a connection if it has a floor connection with an existing room.
                if map.grid[y][x+1].status==1 or map.grid[y][x-1].status ==1 or map.grid[y+1][x].status==1 or map.grid[y-1][x].status ==1:
                    return False
    return True #If no wall tile is adjacent to an existing floor, room has no connection.

def AnimateGeneration(map, window):
    #Center changed after trimming the image.
    cursor = [map.animCache.center[0] - map.minx, map.animCache.center[1] - map.miny]
    window.img = Image.new("RGB", (map.biggerDim*Map.ppi+Map.ppi, map.biggerDim*Map.ppi+Map.ppi))
    draw = ImageDraw.Draw(window.img)
    #draw.rectangle((cursor[0]*Map.ppi, cursor[1]*Map.ppi, cursor[0]*Map.ppi+Map.ppi, cursor[1]*Map.ppi+Map.ppi), outline = "black", fill = 'yellow')
    placedTiles = []

    for room in map.rooms:
        room.x -= map.minx
        room.y -= map.miny

    #TODO: INDEX OUT OF RANGE
    for step in map.animCache.steps:
        cursor = [cursor[0]+DIR[step][0], cursor[1]+DIR[step][1]]
        if cursor[0] < 0 or cursor[1] < 0 or cursor[0] >= map.xsize or cursor[1] >= map.ysize:
            continue
        #cursor = [cursor[0]+step[0], cursor[1]+step[1]]
        #if not (cursor[0] < 0 or cursor[1] < 0 or cursor[0] >= map.xsize or cursor[1] >= map.ysize):
        draw.rectangle((cursor[0]*Map.ppi, cursor[1]*Map.ppi, cursor[0]*Map.ppi+Map.ppi, cursor[1]*Map.ppi+Map.ppi), outline = "black", fill = 'yellow')
        for room in map.rooms:
            if [room.x, room.y] == cursor:
                for x in range(room.x, room.x+room.length+1): #for each tile in the room, update the maps grid
                    for y in range(room.y, room.y+room.height+1):
                        placedTiles.append([x, y])
                        if map.grid[y][x].status == 1:
                            DrawOnCanvas((x, y), window, color= COLORLIST[1])
                            #draw.rectangle((x*Map.ppi, y*Map.ppi, x*Map.ppi+Map.ppi, y*Map.ppi+Map.ppi), outline = "black", fill = COLORLIST[1])
                        elif map.grid[y][x].status % 2 == 0:
                            DrawOnCanvas((x, y), window, color= COLORLIST[2])
                            #draw.rectangle((x*Map.ppi, y*Map.ppi, x*Map.ppi+Map.ppi, y*Map.ppi+Map.ppi), outline = "black", fill = COLORLIST[2])
                        else:
                            DrawOnCanvas((x, y), window, color= COLORLIST[3])
                            #draw.rectangle((x*Map.ppi, y*Map.ppi, x*Map.ppi+Map.ppi, y*Map.ppi+Map.ppi), outline = "black", fill = COLORLIST[3])
        window.DisplayImage()
        window.update_idletasks()
        if cursor in placedTiles:
            DrawOnCanvas((cursor[0], cursor[1]), window, color= COLORLIST[map.grid[cursor[1]][cursor[0]].status])
        else:
            DrawOnCanvas((cursor[0], cursor[1]), window,  color= 'black')
