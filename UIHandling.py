from PIL import Image, ImageTk
import generation as dr
import tkinter as tk
from tkinter import NW, PhotoImage, ttk
import math
from animation import AnimateGeneration

class App(tk.Tk):
    def __init__(self, **params):
        super().__init__()
        self.tk.call("source", "./Assets/azure.tcl")
        self.tk.call("set_theme", "dark")

        #Window attributes
        self.title("Map Generator")
        icon = ImageTk.PhotoImage(file = "./Assets/icon.png")
        self.wm_iconphoto(False, icon)

        self.bind('<Configure>', lambda event: onResize(event, self))

        self._scale = (1, 1)

        #Initialize widgets
        self.canvasFrame = ttk.Frame(self, width=750, height=750)
        self.map = dr.Map()
        self.img:Image = self.map.DrawPicture()
        self.imgtk:ImageTk = ImageTk.PhotoImage(self.img.resize((750, 750), Image.BOX))
        self.UIFrame = ttk.Frame(self)
        self.canvas = tk.Canvas(self.canvasFrame, width= 750, height= 750, bg='#f0f0c0')
        self.imageDisplay = self.canvas.create_image(0, 0, image=self.imgtk, anchor=NW, tags='image')
        self.canvas.bind("<Button-1>", lambda event: CanvasOnClick(event, self))
        self.roomNumText = ttk.Label(self.UIFrame, text='# of Rooms: ')
        self.roomNum = ttk.Label(self.UIFrame, text="10")
        self.maxSizeText = ttk.Label(self.UIFrame, text="Max Room Size:")
        self.maxSize = ttk.Label(self.UIFrame, text="10")
        self.ppiText = ttk.Label(self.UIFrame, text="Pixels per tile:")
        self.ppi = ttk.Label(self.UIFrame, text="10")
        self.roomNumScale = ttk.Scale(self.UIFrame, from_=1, to=100, value=10, command= lambda event: self.roomNum.configure(text='{:.0f}'.format(math.floor(self.roomNumScale.get()))))
        self.maxSizeScale = ttk.Scale(self.UIFrame, from_=6, to=20, value=10, command= lambda event: self.maxSize.configure(text='{:.0f}'.format(math.floor(self.maxSizeScale.get()))))
        self.ppiScale = ttk.Scale(self.UIFrame, from_=5, to=25, value=10, command= lambda event: self.ppi.configure(text='{:.0f}'.format(math.floor(self.ppiScale.get()))))
        self.animateValue = tk.IntVar()
        self.animateButton = ttk.Checkbutton(self.UIFrame, text='Animate?', variable=self.animateValue)
        self.genButton = ttk.Button(self.UIFrame, text='Generate', width=15, command= lambda: ButtonOnClick(math.floor(self.roomNumScale.get()), math.floor(self.maxSizeScale.get()), math.floor(self.ppiScale.get()), self.animateValue.get(), self))

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

    @property
    def scale(self):
        self._scale =  (self.canvas.winfo_width() / self.map.biggerDim*self.map.ppi, self.canvas.winfo_height() / self.map.biggerDim*self.map.ppi)
        return self._scale

    def DisplayImage(self, resolution = None):
        if resolution == None:
            resolution = (self.canvas.winfo_width(), self.canvas.winfo_height())
        
        self.imgtk = ImageTk.PhotoImage(self.img.resize((resolution[0], resolution[1]), Image.BOX))
        self.canvas.itemconfig('image', image = self.imgtk)

def ButtonOnClick(numRooms, maxRoomSize, ppi, animate, window):
    window.map = dr.Map(numrooms= numRooms, roomsize= maxRoomSize, ppi= ppi, animate= animate) #Generate new map and send the new data to the window.
    if animate:
        window.genButton.state(["disabled"])
        AnimateGeneration(window.map, window)
    else:
        window.img = window.map.DrawPicture()
        window.DisplayImage()

def CanvasOnClick(event, window):
    xscale = window.img.width / window.canvas.winfo_width() #multiplier used to convert to and from original image size
    yscale = window.img.height / window.canvas.winfo_height()
    rawimgCoords = (event.x*xscale, event.y*yscale) #convert canvas coordinates (post-resize) to raw image coordinates
    cell = (int(rawimgCoords[0]//dr.Map.ppi), int(rawimgCoords[1]//dr.Map.ppi)) #convert image coordinates to map grid index. Integer division to always start at corner of cell even if click is from middle

    #Only allow clicking on floors or doors
    if window.map.grid[cell[1]][cell[0]].status != 1 and window.map.grid[cell[1]][cell[0]].status != 3:
        return

    #If existing path, clear it
    if len(window.map.nodes) >= 2: 
        for node in window.map.nodes:
            dr.DrawOnCanvas(node, window, color=dr.FLOOR if window.map.grid[node[1]][node[0]].status == 1 else dr.DOOR) # Recolor as floor, else door
        window.map.nodes = []

    window.map.nodes.append(cell)

    #If this was the second node clicked, find a path between the two
    if len(window.map.nodes) == 2:
        window.map.nodes = dr.FindPath(window.map)

    for node in window.map.nodes:
        dr.DrawOnCanvas(node, window, color="green") #Colors nodes on path

    window.imgtk = ImageTk.PhotoImage(window.img.resize((window.canvas.winfo_width(), window.canvas.winfo_height()))) #Save to class to avoid garbage collection
    window.canvas.itemconfig('image', image = window.imgtk)

def onResize(event, window):
    if event.widget == window.canvas:
        window.imgtk = ImageTk.PhotoImage(window.img.resize((window.canvas.winfo_width(), window.canvas.winfo_height())))
        window.canvas.itemconfig('image', image = window.imgtk)
