from email.mime import image
from operator import truediv
import random
from PIL import Image, ImageDraw, ImageTk

class Room:
    def __init__(self, maxSize=10):
        random.seed()
        self.length = random.randint(5,maxSize-1) #-1 because of how I calculate the points of the rectangles (x + length) with x of 0 and size of 5, shape would go 0-5, size 6
        self.height = random.randint(5,maxSize-1)
        self.x = None #no coordinates initially
        self.y = None
    def UpdateVertices(self, coords:list): #sets a rooms x,y coords
        self.blCorner = coords
        self.x = self.blCorner[0]
        self.y = self.blCorner[1]

def CheckCollision(room, rooms, map): #true if collision, false if valid
    if room.x + room.length >= map.size or room.y + room.height >= map.size: #checking with map bounds
        return True
    count=0
    for y in range(room.y, room.y+room.height+1):
        for x in range(room.x, room.x+room.length+1):
    #        print('x=',x,' y=', y)
            count = count+1 if map.grid[y][x].status > 1 else count
    #        print(count)
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
        self.status:int = 0

class Map:
    def __init__(self, size:int):
        self.size = size
        self.grid = [[Square() for x in range(size)] for y in range(size)]

def TrimImage(dimensions, map):
    dimensions[0]=map.size
    dimensions[1]=0
    dimensions[2]=map.size
    dimensions[3]=0
    for indexy, y in enumerate(map.grid): #grabs farthest left wall
        for indexx, x in enumerate(y):
            if x.status > 1: #if cell is wall
                dimensions[0] = indexy if indexy < dimensions[0] else dimensions[0]
                dimensions[1] = indexy if indexy > dimensions[1] else dimensions[1]
                dimensions[2] = indexx if indexx < dimensions[2] else dimensions[2]
                dimensions[3] = indexx if indexx > dimensions[3] else dimensions[3]

def DrawPicture(map:Map, ppi):
    dimensions = [map.size, 0, map.size, 0] #0=miny 1=maxy 2=minx 3=maxx
    TrimImage(dimensions, map) #grab the indices of the min and max x and y positions that aren't empty. Will use these to draw to eliminate black space around the layout
    biggerDim = dimensions[3]-dimensions[2] if dimensions[3]-dimensions[2] > dimensions[1]-dimensions[0] else dimensions[1]-dimensions[0] #get the bigger dimension so that the image is always square
    image = Image.new("RGB", (biggerDim*ppi+ppi, biggerDim*ppi+ppi))
    draw = ImageDraw.Draw(image)
    #for each cell, draw 10x10 pixels
    for y in range(dimensions[0], dimensions[1]+1):
        for x in range(dimensions[2], dimensions[3]+1):
            if map.grid[y][x].status == 1:
                draw.rectangle([(x-dimensions[2])*ppi,(y-dimensions[0])*ppi,((x-dimensions[2])*ppi)+ppi,((y-dimensions[0])*ppi)+ppi], outline="black", fill = "brown")
            elif map.grid[y][x].status > 1:
                draw.rectangle([(x-dimensions[2])*ppi,(y-dimensions[0])*ppi,((x-dimensions[2])*ppi)+ppi,((y-dimensions[0])*ppi)+ppi], outline="black", fill = "grey")
    image = image.resize((750,750), Image.ANTIALIAS)
    return image

def GenRooms(rooms, numRooms, maxRoomSize=10):
    for x in range(numRooms): #generate list of rooms with random sizes
        rooms.append(Room(maxRoomSize))
    
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
            if coord[0] >= map.size or coord[1] >= map.size: #go oob
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

def GenerateMap(numRooms, ppi=40, maxRoomSize=10):
    random.seed()
    rooms = [] #initial roomlist
    placedRooms = [] #rooms already placed in map, this is used for collision checking

    GenRooms(rooms, numRooms, maxRoomSize)

    maxDimension = GetMaxDimension(rooms)

    map = Map(5+maxDimension) #generates map big enough for the rooms + a buffer

#place rooms on the map, random walk from center
    PlaceRooms(rooms, placedRooms, map)
    #for y in map.grid:
    #    for x in y:
    #        print(x.status, end='')
    #    print('')
    #for room in placedRooms:
    #    print(room.x, ' ', room.y, ' ', room.x+room.length, ' ', room.y+room.height)
    image = DrawPicture(map, ppi)
    image = ImageTk.PhotoImage(image)
    return image

def ButtonCallback(numRooms, imgLabel, imgFrame, ppi, maxRoomSize):
    image = GenerateMap(numRooms, ppi, maxRoomSize)
    imgLabel.configure(image=image)
    imgLabel.image = image

def ScaleCallback(numRooms, label):
    pass