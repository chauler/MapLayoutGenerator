import random
from PIL import Image, ImageDraw, ImageTk

class ImageContainer:
    img:Image = None
    imgtk:ImageTk = None

class Room:
    def __init__(self, maxSize=10):
        random.seed()
        self.length = random.randint(4,maxSize-1) #-1 because of how I calculate the points of the rectangles (x + length) with x of 0 and size of 5, shape would go 0-5, size 6
        self.height = random.randint(4,maxSize-1)
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
        self.adjFloors:int = 0

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

def TrimImage(map):
    for indexy, y in enumerate(map.grid): #grabs farthest left wall
        for indexx, x in enumerate(y):
            if x.status > 1: #if cell is wall
                map.miny = indexy if indexy < map.miny else map.miny
                map.maxy = indexy if indexy > map.maxy else map.maxy
                map.minx = indexx if indexx < map.minx else map.minx
                map.maxx = indexx if indexx > map.maxx else map.maxx

def DrawPicture(map:Map):
    ppi = Map.ppi
    biggerDim = map.maxx-map.minx if map.maxx-map.minx > map.maxy-map.miny else map.maxy-map.miny #get the bigger dimension so that the image is always square
    image = Image.new("RGB", (biggerDim*ppi+ppi, biggerDim*ppi+ppi))
    draw = ImageDraw.Draw(image)
    #for each cell, draw 10x10 pixels
    for y in range(map.miny, map.maxy+1):
        for x in range(map.minx, map.maxx+1):
            if map.grid[y][x].status == 1:
                draw.rectangle([(x-map.minx)*ppi,(y-map.miny)*ppi,((x-map.minx)*ppi)+ppi,((y-map.miny)*ppi)+ppi], outline="black", fill = (51, 23, 12))
            elif map.grid[y][x].status == 3:
                draw.rectangle([(x-map.minx)*ppi,(y-map.miny)*ppi,((x-map.minx)*ppi)+ppi,((y-map.miny)*ppi)+ppi], outline="black", fill = (146, 41, 41))
            elif map.grid[y][x].status > 1:
                draw.rectangle([(x-map.minx)*ppi,(y-map.miny)*ppi,((x-map.minx)*ppi)+ppi,((y-map.miny)*ppi)+ppi], outline="black", fill = (93, 89, 97))
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

def GenerateMap():
    random.seed()
    rooms = [] #initial roomlist
    placedRooms = [] #rooms already placed in map, this is used for collision checking

    GenRooms(rooms)

    maxDimension = GetMaxDimension(rooms)

    map = Map(5+maxDimension) #generates map big enough for the rooms + a buffer

#place rooms on the map, random walk from center
    PlaceRooms(rooms, placedRooms, map)
    TrimImage(map) #grab the indices of the min and max x and y positions that aren't empty. Will use these to draw to eliminate black space around the layout
    GenDoors(map)
    #for y in map.grid:
    #    for x in y:
    #        print(x.status, end='')
    #    print('')
    #for room in placedRooms:
    #    print(room.x, ' ', room.y, ' ', room.x+room.length, ' ', room.y+room.height)
    newImage = DrawPicture(map)
    return map, newImage

def ButtonCallback(numRooms, canvas, maxRoomSize):
    Map.numrooms = numRooms
    Map.roomsize = maxRoomSize
    map, ImageContainer.img = GenerateMap()
    ImageContainer.imgtk = ImageTk.PhotoImage(ImageContainer.img.resize((750,750), Image.ANTIALIAS))
    canvas.itemconfig('image', image = ImageContainer.imgtk)

def canvasOnClick(event, canvas):
    scale = ImageContainer.img.width / 750 #gets the multiplier used to convert to and from original image size
    imgCoords = (event.x*scale, event.y*scale) #convert canvas coordinates (post-resize) to raw image coordinates
    cell = (imgCoords[0]//Map.ppi, imgCoords[1]//Map.ppi) #convert image coordinates to map grid index. Integer division to always start at corner of cell even if click is from middle

    DrawOnCanvas(cell)
    ImageContainer.imgtk = ImageTk.PhotoImage(ImageContainer.img.resize((750,750), Image.ANTIALIAS)) #Save to class to avoid garbage collection
    canvas.itemconfig('image', image = ImageContainer.imgtk)

def DrawOnCanvas(cell):
    draw = ImageDraw.Draw(ImageContainer.img)
    draw.rectangle((cell[0]*Map.ppi, cell[1]*Map.ppi, cell[0]*Map.ppi+Map.ppi, cell[1]*Map.ppi+Map.ppi),outline="black", fill = "green")

def GenDoors(map):
    doorable = []
    doorGroups = []
    for y in range(map.miny, map.maxy+1):
        for x in range(map.minx, map.maxx+1):
            if x == 0 or x == map.size-1 or y==0 or y==map.size-1 or map.grid[y][x].status == 0 or map.grid[y][x].status == 1: #if pointer is on the edge of the map or not a wall, skip
                continue
            #Generate lists of horizontally adjacent doorable tiles
            if map.grid[y+1][x].status==1 and map.grid[y-1][x].status ==1: #if doorable
                doorGroups.append(map.grid[y][x])
            elif doorGroups != []: #if not doorable and list isn't empty, then that's the end of a group
                doorable.append(doorGroups)
                doorGroups = []

    for x in range(map.minx, map.maxx+1):
        for y in range(map.miny, map.maxy+1):
                if x == 0 or x == map.size-1 or y==0 or y==map.size-1 or map.grid[y][x].status == 0 or map.grid[y][x].status == 1: #if pointer is on the edge of the map or not a wall, skip
                    continue
                if map.grid[y][x+1].status==1 and map.grid[y][x-1].status ==1: #if doorable
                    doorGroups.append(map.grid[y][x])
                elif doorGroups != []: #if not doorable and list isn't empty, then that's the end of a group
                    doorable.append(doorGroups)
                    doorGroups = []

    for group in doorable:
        door = random.choice(group)
        door.status = 3