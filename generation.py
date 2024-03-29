import random
from PIL import Image, ImageDraw

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
    animate = False

    def __init__(self, **params):
        self.ppi = params.get('ppi', Map.ppi)
        self.numrooms = params.get('numrooms', Map.numrooms)
        self.roomsize = params.get('roomsize', Map.roomsize)
        self.animate = params.get('animate', Map.animate)

        roomsToPlace = [] #initial roomlist
        roomsToPlace = GenRooms(self.numrooms, self.roomsize)
        maxDimension = GetMaxDimension(roomsToPlace)

        self.size = maxDimension+15
        self.grid = [[Square() for x in range(self.size)] for y in range(self.size)] #2D array of default squares
        self.rooms = []
        self.graph = None #stored as (x,y):[(x,y),(x,y)]
        self.nodes = [] #stored as (x,y)
        self.animCache = AnimationCache()

        self.PlaceRooms(roomsToPlace, self.rooms)
        self.TrimGrid() #grab the indices of the min and max x and y positions that aren't empty. Will use these to draw to eliminate black space around the layout
        self.GenDoors()
        self.CreateGraph()

    @property
    def xsize(self):
        return self.maxx-self.minx+1

    @property
    def ysize(self):
        return self.maxy-self.miny+1
    
    @property
    def biggerDim(self):
        return self.xsize if self.xsize > self.ysize else self.ysize

    def PlaceRooms(self, rooms, placedRooms):
        coord = [self.size // 2, self.size // 2]
        self.animCache.center = [self.size // 2, self.size // 2]

        #Start by taking 10 steps from center.
        for i in range(10):
            #Repeats until the taken step is valid.
            while True:
                move = random.choice(DIR)
                coord[0] += move[0]
                coord[1] += move[1]
                self.animCache.steps.append(DIR.index(move))
                if coord[0] >= self.size or coord[1] >= self.size or coord[0] < 0 or coord[1] < 0: #go oob
                    coord[0] -= move[0] #undo move and try again
                    coord[1] -= move[1]
                    self.animCache.steps.append(DIR.index([-move[0],-move[1]]))
                else: #breaks only if move is valid and doesnt go oob
                    break
        
        #Place each room individually
        for room in rooms:
            #Place the room on a hypothetical position, then adjust position in while loop
            room.UpdateVertices(coord) 
            #Loop True for invalid position, run until valid
            while CheckCollision(room, placedRooms, self) or CheckDisconnected(room, placedRooms, self):
                move = random.choice(DIR)
                coord[0] += move[0]
                coord[1] += move[1]
                self.animCache.steps.append(DIR.index(move))
                #If move takes us out of bounds, undo and loop
                if coord[0] >= self.size or coord[1] >= self.size or coord[0] < 0 or coord[1] < 0:
                    coord[0] -= move[0]
                    coord[1] -= move[1]
                    self.animCache.steps.append(DIR.index([-move[0],-move[1]]))

                room.UpdateVertices(coord) #update with new coords, try again

            placedRooms.append(room) #add room to list for later collision checks
            for x in range(room.x, room.x+room.length+1): #for each tile in the room, update the selfs grid
                for y in range(room.y, room.y+room.height+1):
                        if x == room.x or y == room.y or x == room.x+room.length or y == room.y+room.height:
                            self.grid[y][x].status += 2 #make walls 2
                        else:
                            self.grid[y][x].status = 1 #make cells occupied
    #Used to get rid of empty space on the sides of the generated grid
    def TrimGrid(self):
        self.minx = self.size
        self.maxx = 0
        self.miny = self.size
        self.maxy = 0
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

        #Update the room origins to match the post-trim origins
        for room in self.rooms:
            room.x -= self.minx
            room.y -= self.miny

        #Update the map's grid and sizes
        self.grid = newGrid

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

    def DrawPicture(self):
        image = Image.new("RGB", (self.biggerDim*self.ppi+self.ppi, self.biggerDim*self.ppi+self.ppi))
        draw = ImageDraw.Draw(image)

        #for each cell, draw (ppi) pixels
        for y in range(self.ysize):
            for x in range(self.xsize):
                if self.grid[y][x].status == 1: #Floor, draw brown
                    draw.rectangle([x*self.ppi,y*self.ppi,(x*self.ppi)+self.ppi,(y*self.ppi)+self.ppi], outline="black", fill = FLOOR)
                elif self.grid[y][x].status == 3: #Door, draw red
                    draw.rectangle([x*self.ppi,y*self.ppi,(x*self.ppi)+self.ppi,(y*self.ppi)+self.ppi], outline="black", fill = DOOR)
                elif self.grid[y][x].status > 1: #Wall, draw grey
                    draw.rectangle([x*self.ppi,y*self.ppi,(x*self.ppi)+self.ppi,(y*self.ppi)+self.ppi], outline="black", fill = WALL)
        return image

class AnimationCache:
    def __init__(self):
        self.steps = []
        self.center = None

def GenRooms(numrooms, roomsize):
    rooms = []
    for x in range(numrooms):
        rooms.append(Room(roomsize))
    return rooms
    
#Sum length and height of rooms, returns the bigger dimension to ensure map is big enough for all rooms
def GetMaxDimension(rooms):
    totalLength=0
    totalHeight=0

    for room in rooms:
        totalLength += room.length
        totalHeight += room.height

    return totalLength if totalLength > totalHeight else totalHeight

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

#Takes in a (x,y) tuple, draws associated square in given color. Kwargs: color: (rr,gg,bb) or color keyword.
def DrawOnCanvas(cell:tuple, window,**params):
    draw = ImageDraw.Draw(params.get("image", window.img))
    ppi = params.get("ppi", window.imageppi)
    draw.rectangle((cell[0]*ppi[0], cell[1]*ppi[1], cell[0]*ppi[0]+ppi[0], cell[1]*ppi[1]+ppi[1]), outline = "black", fill = params.get('color', "green"))

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
