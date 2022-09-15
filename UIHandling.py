from PIL import Image, ImageTk
import dungeonRoom as dr


def ButtonOnClick(numRooms, maxRoomSize, window):
    dr.Map.numrooms = numRooms
    dr.Map.roomsize = maxRoomSize

    window.map, window.img = dr.GenerateMap() #Generate new map and send the new data to the window.
    window.imgtk = ImageTk.PhotoImage(window.img.resize((750,750), Image.ANTIALIAS))
    window.canvas.itemconfig('image', image = window.imgtk) #Update the window's canvas with the new map image

def CanvasOnClick(event, window):
    scale = window.img.width / 750 #multiplier used to convert to and from original image size
    rawimgCoords = (event.x*scale, event.y*scale) #convert canvas coordinates (post-resize) to raw image coordinates
    cell = (int(rawimgCoords[0]//dr.Map.ppi), int(rawimgCoords[1]//dr.Map.ppi)) #convert image coordinates to map grid index. Integer division to always start at corner of cell even if click is from middle

    #Only allow clicking on floors or doors
    if window.map.grid[cell[1]][cell[0]].status != 1 and window.map.grid[cell[1]][cell[0]].status != 3:
        return

    #If existing path, clear it
    if len(window.map.nodes) >= 2: 
        for node in window.map.nodes:
            dr.DrawOnCanvas(node, window, color=(51, 23, 12) if window.map.grid[node[1]][node[0]].status == 1 else (146, 41, 41)) # Recolor as floor, else door
        window.map.nodes = []

    window.map.nodes.append(cell)

    #If this was the second node clicked, find a path between the two
    if len(window.map.nodes) == 2:
        window.map.nodes = dr.FindPath(window.map)

    for node in window.map.nodes:
        dr.DrawOnCanvas(node, window, color="green") #Colors nodes on path

    window.imgtk = ImageTk.PhotoImage(window.img.resize((750,750), Image.ANTIALIAS)) #Save to class to avoid garbage collection
    window.canvas.itemconfig('image', image = window.imgtk)