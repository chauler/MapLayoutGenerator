import tkinter
import dungeonRoom as dr
import math
import random
import tkinter as tk
from tkinter import NW, ttk
from PIL import ImageTk, Image

class App(tk.Tk):
    def __init__(self, **params):
        super().__init__()

        #Window attributes
        self.title("Map Generator")

        #Initialize widgets
        self.imageFrame = ttk.Frame(self)
        self.UIFrame = ttk.Frame(self)
        self.canvas = tk.Canvas(self.imageFrame, width=750, height=750)
        self.canvasImage = self.canvas.create_image(0, 0, anchor=NW, tags='image')
        self.canvas.bind("<Button-1>", lambda event: dr.canvasOnClick(event, self.canvas))
        self.scaleLabel = ttk.Label(self.UIFrame, text='# of Rooms: ')
        self.valueLabel = ttk.Label(self.UIFrame, text="10")
        self.maxRoomSizeLabel = ttk.Label(self.UIFrame, text="Max Room Size:")
        self.maxRoomSizeValueLabel = ttk.Label(self.UIFrame, text="10")
        self.roomNumScale = ttk.Scale(self.UIFrame, from_=1, to=100, value=10, command= lambda event: self.valueLabel.configure(text='{:.0f}'.format(math.floor(self.roomNumScale.get()))))
        self.maxRoomSizeScale = ttk.Scale(self.UIFrame, from_=6, to=20, value=10, command= lambda event: self.maxRoomSizeValueLabel.configure(text='{:.0f}'.format(math.floor(self.maxRoomSizeScale.get()))))
        self.genButton = ttk.Button(self.UIFrame, text='Generate', command= lambda: dr.ButtonCallback(math.floor(self.roomNumScale.get()), self.canvas, math.floor(self.maxRoomSizeScale.get())))

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

def main():
    window = App()
    window.resizable(False, False)
    dr.ImageContainer.img = Image.new("RGB", (10, 10))
    
    #generate initial image with default params
    map, dr.ImageContainer.img = dr.GenerateMap()
    dr.ImageContainer.imgtk = ImageTk.PhotoImage(dr.ImageContainer.img.resize((750,750), Image.ANTIALIAS))
    window.canvas.itemconfig('image', image = dr.ImageContainer.imgtk)
    window.mainloop()

if __name__ == "__main__":
    main()