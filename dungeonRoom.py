import random
import math
from PIL import Image, ImageDraw, ImageTk
import tkinter as tk
from tkinter import NW, ttk

class Room:
    def __init__(self, maxSize=10):
        random.seed()
        self.length = random.randint(4,maxSize-1) #-1 because of how I calculate the points of the rectangles (x + length) with x of 0 and size of 5, shape would go 0-5, size 6
        self.height = random.randint(4,maxSize-1)
        self.x = None #no coordinates initially
        self.y = None
    def UpdateVertices(self, coords:list): #sets a rooms x,y coords
        self.x = coords[0]
        self.y = coords[1]

def CheckCollision(room, rooms, map): #true if collision, false if valid
    if room.x + room.length >= map.size or room.y + room.height >= map.size: #checking with map bounds
        return True
    count=0
    for y in range(room.y, room.y+room.height+1):
        for x in range(room.x, room.x+room.length+1):
            count = count+1 if map.grid[y][x].status > 1 else count
    if count < 3 and len(rooms) != 0:
        return True
    for obj in rooms: #passed bounds check, checking with other rooms
        if room is obj:
            continue
        elif room.x < obj.x+obj.length and room.x+room.length > obj.x and room.y < obj.y+obj.height and room.y+room.height > obj.y:
            return True
    return False

class Square:
    def __init__(self):
        self.status:int = 0 #0: black 1: floor door: 3 wall: 2,4,6,8
        self.adjFloors:int = 0

class Graph:
    def __init__(self, edges, vertices, adjList):
        self.edges = edges
        self.vertices = vertices
        self.adjList = adjList

class Node:
    parent = None
    def __init__(self, coords, parent=None):
        self.coords:tuple = coords
        self.f = 999999
        self.g = 999999
        self.h = 0
        self.parent = parent
    def __eq__(self, other):
        return self.coords == other.coords

class Map:
    ppi = 10
    numrooms = 10
    roomsize = 10
    def __init__(self, size:int, **params):
        self.size = size
        self.grid = [[Square() for x in range(size)] for y in range(size)]
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

def TrimGrid(map):
    for indexy, y in enumerate(map.grid): #grabs farthest left wall
        for indexx, x in enumerate(y):
            if x.status > 1: #if cell is wall
                map.miny = indexy if indexy < map.miny else map.miny
                map.maxy = indexy if indexy > map.maxy else map.maxy
                map.minx = indexx if indexx < map.minx else map.minx
                map.maxx = indexx if indexx > map.maxx else map.maxx

    newGrid = [[Square() for x in range(map.minx, map.maxx+1)] for y in range(map.miny, map.maxy+1)]
    for indexy, y, in enumerate(newGrid):
        for indexx, x in enumerate(y):
            newGrid[indexy][indexx] = map.grid[indexy+map.miny][indexx+map.minx]
    map.grid = newGrid
    map.xsize = map.maxx-map.minx+1
    map.ysize = map.maxy-map.miny+1

def DrawPicture(map:Map):
    ppi = Map.ppi
    biggerDim = map.maxx-map.minx if map.maxx-map.minx > map.maxy-map.miny else map.maxy-map.miny #get the bigger dimension so that the image is always square
    image = Image.new("RGB", (biggerDim*ppi+ppi, biggerDim*ppi+ppi))
    draw = ImageDraw.Draw(image)
    #for each cell, draw 10x10 pixels
    for y in range(map.ysize):
        for x in range(map.xsize):
            if map.grid[y][x].status == 1:
                draw.rectangle([x*ppi,y*ppi,(x*ppi)+ppi,(y*ppi)+ppi], outline="black", fill = (51, 23, 12))
            elif map.grid[y][x].status == 3:
                draw.rectangle([x*ppi,y*ppi,(x*ppi)+ppi,(y*ppi)+ppi], outline="black", fill = (146, 41, 41))
            elif map.grid[y][x].status > 1:
                draw.rectangle([x*ppi,y*ppi,(x*ppi)+ppi,(y*ppi)+ppi], outline="black", fill = (93, 89, 97))
    return image

def GenRooms(rooms):
    for x in range(Map.numrooms): #generate list of rooms with random sizes
        rooms.append(Room(Map.roomsize))
    
def GetMaxDimension(rooms):
    totalLength=0
    totalHeight=0
    for room in rooms: #get combined height and height of all rooms
        totalLength += room.length
        totalHeight += room.height
    return totalLength if totalLength > totalHeight else totalHeight #Returns bigger so that the map will always be big enough to hold all the rooms, even in worst case of side by side placement

def PlaceRooms(rooms, placedRooms, map):
    coord = [map.size // 2, map.size // 2]
    dir = [[1,0],[0,1],[-1,0],[0,-1]]
    for i in range(10): #start by taking 10 steps from center
        while True:
            move = random.choice(dir)
            coord[0] += move[0]
            coord[1] += move[1]
            if coord[0] >= map.size or coord[1] >= map.size or coord[0] < 0 or coord[1] < 0: #go oob
                coord[0] -= move[0] #undo move and try again
                coord[1] -= move[1]
            else: #breaks only if move is valid and doesnt go oob
                break
    for room in rooms:
        room.UpdateVertices(coord) #place the room on a hypothetical position, then adjust position in while loop
        while CheckCollision(room, placedRooms, map): #while there is a collision with border or existing rooms
            move = random.choice(dir)
            coord[0] += move[0]
            coord[1] += move[1]
            if coord[0] >= map.size or coord[1] >= map.size or coord[0] < 0 or coord[1] < 0: #go oob
                coord[0] -= move[0] #undo move and try again
                coord[1] -= move[1]
            room.UpdateVertices(coord) #update with new coords, try again

        placedRooms.append(room) #add room to list for later collision checks
        for x in range(room.x, room.x+room.length+1): #for each tile in the room, update the maps grid
            for y in range(room.y, room.y+room.height+1):
                    if x == room.x or y == room.y or x == room.x+room.length or y == room.y+room.height:
                        map.grid[y][x].status += 2 #make walls 2
                    else:
                        map.grid[y][x].status = 1 #make cells occupied

def GenerateMap():
    random.seed()
    rooms = [] #initial roomlist
    placedRooms = [] #rooms already placed in map, this is used for collision checking

    GenRooms(rooms)

    maxDimension = GetMaxDimension(rooms)

    map = Map(5+maxDimension) #generates map big enough for the rooms + a buffer

#place rooms on the map, random walk from center
    PlaceRooms(rooms, placedRooms, map)
    TrimGrid(map) #grab the indices of the min and max x and y positions that aren't empty. Will use these to draw to eliminate black space around the layout
    GenDoors(map)
    CreateGraph(map)
    newImage = DrawPicture(map)
    return map, newImage

def ButtonCallback(numRooms, maxRoomSize, window):
    Map.numrooms = numRooms #Generate button pressed. Update map parameters.
    Map.roomsize = maxRoomSize
    window.map, window.img = GenerateMap() #Generate new map and send the new data to the window.
    window.imgtk = ImageTk.PhotoImage(window.img.resize((750,750), Image.ANTIALIAS))
    window.canvas.itemconfig('image', image = window.imgtk) #Update the window's canvas with the new map image

def canvasOnClick(event, window):
    scale = window.img.width / 750 #gets the multiplier used to convert to and from original image size
    rawimgCoords = (event.x*scale, event.y*scale) #convert canvas coordinates (post-resize) to raw image coordinates
    cell = (int(rawimgCoords[0]//Map.ppi), int(rawimgCoords[1]//Map.ppi)) #convert image coordinates to map grid index. Integer division to always start at corner of cell even if click is from middle
    if window.map.grid[cell[1]][cell[0]].status != 1 and window.map.grid[cell[1]][cell[0]].status != 3: #Only allow clicking on floors or doors
        return

    if len(window.map.nodes) >= 2: #If existing path, clear it
        for node in window.map.nodes:
            DrawOnCanvas(node, window, color=(51, 23, 12) if window.map.grid[node[1]][node[0]].status == 1 else (146, 41, 41)) # Recolor as floor, else door
        window.map.nodes = []

    window.map.nodes.append(cell)
    if len(window.map.nodes) == 2: #If this was the second node clicked, find a path between the two
        window.map.nodes = FindPath(window.map) #Adds nodes in path to nodes[]
        for node in window.map.nodes:
            DrawOnCanvas(node, window, color='green')
    for node in window.map.nodes:
        DrawOnCanvas(node, window, color="green") #Colors nodes on path

    window.imgtk = ImageTk.PhotoImage(window.img.resize((750,750), Image.ANTIALIAS)) #Save to class to avoid garbage collection
    window.canvas.itemconfig('image', image = window.imgtk)

def DrawOnCanvas(cell:tuple, window, **params): #Takes in a (x,y) tuple, draws associated square in given color. Default color green
    draw = ImageDraw.Draw(window.img)
    draw.rectangle((cell[0]*Map.ppi, cell[1]*Map.ppi, cell[0]*Map.ppi+Map.ppi, cell[1]*Map.ppi+Map.ppi), outline = "black", fill = params.get('color', "green"))

def GenDoors(map):
    doorable = []
    doorGroups = []

    for indexy, y in enumerate(map.grid):
        for indexx, x in enumerate(y):
            if indexx == 0 or indexx == map.xsize-1 or indexy==0 or indexy==map.ysize-1 or x.status == 0 or x.status == 1: #if pointer is on the edge of the map or not a wall, skip
                continue
            #Generate lists of horizontally adjacent doorable tiles
            if map.grid[indexy+1][indexx].status==1 and map.grid[indexy-1][indexx].status ==1: #if doorable
                doorGroups.append(x)
            elif doorGroups != []: #if not doorable and list isn't empty, then that's the end of a group
                doorable.append(doorGroups)
                doorGroups = []
    for x in range(map.xsize):
        for y in range(map.ysize):
                if x == 0 or x == map.xsize-1 or y==0 or y==map.ysize-1 or map.grid[y][x].status == 0 or map.grid[y][x].status == 1: #if pointer is on the edge of the map or not a wall, skip
                    continue
                if map.grid[y][x+1].status==1 and map.grid[y][x-1].status ==1: #if doorable
                    doorGroups.append(map.grid[y][x])
                elif doorGroups != []: #if not doorable and list isn't empty, then that's the end of a group
                    doorable.append(doorGroups)
                    doorGroups = []

    for group in doorable:
        door = random.choice(group)
        door.status = 3

def CreateGraph(map):
    edges = []
    vertices = []
    adjList = {}
    for y in range(map.ysize):
        for x in range(map.xsize): #Iterate through tiles in relevant portion of map
            if map.grid[y][x].status == 1 or map.grid[y][x].status == 3: #If tile is a floor or wall, meaning it is traversable, make it a node on the graph
                vertices.append(Node((x,y))) #Create new node and add it to vertex list
                tempadj = []
                if map.grid[y][x-1].status == 1 or map.grid[y][x-1].status == 3:
                    edges.append(((x,y),(x-1,y)))
                    tempadj.append((x-1, y))
                if map.grid[y][x+1].status == 1 or map.grid[y][x+1].status ==3:
                    edges.append(((x,y),(x+1,y)))
                    tempadj.append((x+1, y))
                if map.grid[y-1][x].status == 1 or map.grid[y-1][x].status == 3:
                    edges.append(((x,y),(x,y-1)))
                    tempadj.append((x, y-1))
                if map.grid[y+1][x].status == 1 or map.grid[y+1][x].status ==3:
                    edges.append(((x,y),(x,y+1)))
                    tempadj.append((x, y+1))
                adjList.update({(x,y) : tempadj}) #Add most recent (current) vertex and its list of edges to dictionary
    map.graph = Graph(edges, vertices, adjList)
class App(tk.Tk):
    def __init__(self, **params):
        super().__init__()

        #Window attributes
        self.title("Map Generator")

        #Initialize widgets
        self.img:Image = None
        self.imgtk:ImageTk = None
        self.imageFrame = ttk.Frame(self)
        self.map = Map(0)
        self.UIFrame = ttk.Frame(self)
        self.canvas = tk.Canvas(self.imageFrame, width=750, height=750)
        self.canvasImage = self.canvas.create_image(0, 0, anchor=NW, tags='image')
        self.canvas.bind("<Button-1>", lambda event: canvasOnClick(event, self))
        self.scaleLabel = ttk.Label(self.UIFrame, text='# of Rooms: ')
        self.valueLabel = ttk.Label(self.UIFrame, text="10")
        self.maxRoomSizeLabel = ttk.Label(self.UIFrame, text="Max Room Size:")
        self.maxRoomSizeValueLabel = ttk.Label(self.UIFrame, text="10")
        self.roomNumScale = ttk.Scale(self.UIFrame, from_=1, to=100, value=10, command= lambda event: self.valueLabel.configure(text='{:.0f}'.format(math.floor(self.roomNumScale.get()))))
        self.maxRoomSizeScale = ttk.Scale(self.UIFrame, from_=6, to=20, value=10, command= lambda event: self.maxRoomSizeValueLabel.configure(text='{:.0f}'.format(math.floor(self.maxRoomSizeScale.get()))))
        self.genButton = ttk.Button(self.UIFrame, text='Generate', command= lambda: ButtonCallback(math.floor(self.roomNumScale.get()), math.floor(self.maxRoomSizeScale.get()), self))

        self.roomNumScale.grid(row=2, column=0, sticky='n')
        self.valueLabel.grid(row=1,column=0)
        self.scaleLabel.grid(row=0, column=0)
        self.maxRoomSizeLabel.grid(row=3,column=0)
        self.maxRoomSizeValueLabel.grid(row=4, column=0)
        self.maxRoomSizeScale.grid(row=5, column=0)
        self.genButton.grid(row=6, column=0)
        self.canvas.grid(row=0, column=0)
        self.imageFrame.grid(row=0,column=0)
        self.UIFrame.grid(row=0,column=1)

def FindPath(map):
    #given list of 2 (x,y) for starting and ending nodes
    #given adjacency list, keys are (x,y)
    #Modify map.nodes attribute with path
    openList = []
    closedList = []
    startNode = Node(map.nodes[0]) #Create nodes for our start and endpoint.
    endNode = Node(map.nodes[1])
    openList.append(startNode) #Add start to openList
    while openList != []: #Loop until no nodes to search
        #Look for the lowest F cost square on the open list. We refer to this as the current square.
        #Switch it to the closed list.
        openList.sort(key=lambda item: item.f) #Sort openList by f
        currNode = openList.pop(0) #Set current node to openList node with lowest f
        closedList.append(currNode)

        if currNode == endNode:
            pathList = []
            while currNode is not None: #Backtracks from currNode, adding it to the return list and going to the parent
                pathList.append(currNode.coords)
                currNode = currNode.parent
            return pathList

        childList = []
        for item in map.graph.adjList[currNode.coords]: #Generate a new node for each edge from this node
            childList.append(Node(item, currNode))

        for child in childList:
            if [closedChild for closedChild in closedList if closedChild == child] != []:
                continue

            child.g = currNode.g + 1
            child.h = (abs(child.coords[0] - endNode.coords[0]) + abs(child.coords[1] - endNode.coords[1]))#a**2 + b**2 = c**2
            child.f = child.g + child.h

            if [openChild for openChild in openList if openChild == child and child.g >= openChild.g] != []:
                continue

            openList.append(child)


        #for entry in map.graph.adjList[]:
        #For each of the 8 squares adjacent to this current square:
        #If it isn’t on the open list, add it to the open list. Make the current square the parent of this square. Record the F, G, and H costs of the square.
        #If it is on the open list already, check to see if this path to that square is better, using G cost as the measure. 
        #A lower G cost means that this is a better path. If so, change the parent of the square to the current square, and recalculate the G and F scores of the square. 
        #If you are keeping your open list sorted by F score, you may need to resort the list to account for the change.
        
        
        #Stop when you:
        #Add the target square to the closed list, in which case the path has been found, or
        #Fail to find the target square, and the open list is empty. In this case, there is no path.
        #Save the path. Working backwards from the target square, go from each square to its parent square until you reach the starting square. That is your path.
    return 'Failed'