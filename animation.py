from PIL import Image
from generation import Map, DrawOnCanvas, COLORLIST, DIR

def AnimateGeneration(map, window):
    #Center changed after trimming the image.
    cursor = [map.animCache.center[0] - map.minx, map.animCache.center[1] - map.miny]
    window.img = Image.new("RGB", (map.biggerDim*Map.ppi+Map.ppi, map.biggerDim*Map.ppi+Map.ppi))
    window.DisplayImage()
    placedTiles = []
    placedRooms = []

    #Update the room origins to match the post-trim origins
    for room in map.rooms:
        room.x -= map.minx
        room.y -= map.miny

    #Recursive, iterates until there are no more steps left in the list.
    def AnimateHelper(cursor, window, map):
        #Base case, end the recursion and unlock the UI.
        if map.animCache.steps == []:
            window.genButton.state(['!disabled'])
            return

        #Grab the next step and move the cursor, don't draw if it's out of bounds
        step = map.animCache.steps.pop(0)
        cursor = [cursor[0]+DIR[step][0], cursor[1]+DIR[step][1]]
        if cursor[0] < 0 or cursor[1] < 0 or cursor[0] >= map.xsize or cursor[1] >= map.ysize:
            window.after(10, lambda: AnimateHelper(cursor, window, map))
            return

        #Check new cursor position to see if a room should be placed
        #Only place a room the first time we step on its origin. This reduces drawing.
        for room in map.rooms:
            if [room.x, room.y] == cursor and [rooms for rooms in placedRooms if rooms == room] == []:
                #Draw the room and log it as placed
                placedRooms.append(room)
                for x in range(room.x, room.x+room.length+1):
                    for y in range(room.y, room.y+room.height+1):
                        placedTiles.append([x, y])
                        if map.grid[y][x].status == 1:
                            DrawOnCanvas((x, y), window, color= COLORLIST[1])
                        elif map.grid[y][x].status % 2 == 0:
                            DrawOnCanvas((x, y), window, color= COLORLIST[2])
                        else:
                            DrawOnCanvas((x, y), window, color= COLORLIST[3])
        #Draw the cursor, update the image with all the changes
        DrawOnCanvas((cursor[0],cursor[1]), window, color= 'yellow')
        window.DisplayImage()

        #After image update, replace the tile that the cursor drew over
        if cursor in placedTiles:
            DrawOnCanvas((cursor[0], cursor[1]), window, color= COLORLIST[map.grid[cursor[1]][cursor[0]].status])
        else:
            DrawOnCanvas((cursor[0], cursor[1]), window,  color= 'black')

        #If there is still steps to take, call the function again
        if map.animCache.steps != []:
            window.after(10, lambda: AnimateHelper(cursor, window, map))
        else:
            window.genButton.state(['!disabled'])
    
    #Start the animation
    window.after(10, lambda: AnimateHelper(cursor, window, map))