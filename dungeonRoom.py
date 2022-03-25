from operator import truediv
import random
from PIL import Image, ImageDraw

class Room:
    def __init__(self, size=5):
        random.seed()
        self.length = random.randint(3,size)
        self.height = random.randint(3,size)
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
    for y in range(room.y, room.y+room.height):
        for x in range(room.x, room.x+room.length):
            count = count+1 if map.grid[y][x].status > 1 else count
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

def DrawPicture(map:Map):
    image = Image.new("RGB", (10*map.size, 10*map.size))
    draw = ImageDraw.Draw(image)
    #for each cell, draw 10x10 pixels
    for indexy, y in enumerate(map.grid):
        for indexx, x in enumerate(y):
            if x.status == 1:
                draw.rectangle([indexx*10, indexy*10, (indexx*10)+10, (indexy*10)+10], outline="black", fill = "brown")
            elif x.status > 1:
                draw.rectangle([indexx*10, indexy*10, (indexx*10)+10, (indexy*10)+10], outline="black", fill = "grey")
    image.show()
    image = image.resize((500,500), Image.ANTIALIAS)
    return image

def GenRooms(rooms, numRooms):
    for x in range(numRooms): #generate list of rooms with random sizes
        rooms.append(Room(12))
    
def GetMaxDimension(rooms):
    totalLength=0
    totalHeight=0
    for room in rooms: #get combined height and height of all rooms
        totalLength += room.length
        totalHeight += room.height
    return totalLength if totalLength > totalHeight else totalHeight

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
        room.UpdateVertices(coord)
        while CheckCollision(room, placedRooms, map): #while there is a collision with border or existing rooms
            move = random.choice(dir)
            coord[0] += move[0]
            coord[1] += move[1]
            room.UpdateVertices(coord)
        placedRooms.append(room)
        for x in range(room.x, room.x+room.length+1):
            for y in range(room.y, room.y+room.height+1):
                    if x == room.x or y == room.y or x == room.x+room.length or y == room.y+room.height:
                        map.grid[y][x].status += 2 #make walls 2
                    else:
                        map.grid[y][x].status += 1 #make cells occupied