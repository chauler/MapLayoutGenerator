from ctypes import resize
import dungeonRoom as dr
import math
import random
import tkinter as tk
from tkinter import ttk
from PIL import ImageTk, Image
window = tk.Tk()
#window.geometry('1280x720')
window.resizable(False, False)
image = Image.new("RGB", (10, 10))
imageFrame = ttk.Frame(window)
imgLabel = ttk.Label(imageFrame)
UIFrame = ttk.Frame(window)

#default params
numRooms = 10
ppi = 40
maxRoomSize = 10

#Build UI elements
scaleLabel = ttk.Label(UIFrame, text='# of Rooms: ')
valueLabel = ttk.Label(UIFrame, text="10")
roomSizeLabel = ttk.Label(UIFrame, text="Max Room Size:")
roomSizeValueLabel = ttk.Label(UIFrame, text="10")
roomNumScale = ttk.Scale(UIFrame, from_=1, to=100, value=10, command= lambda event: valueLabel.configure(text='{:.0f}'.format(math.floor(roomNumScale.get()))))
maxRoomSizeScale = ttk.Scale(UIFrame, from_=5, to=20, value=10, command= lambda event: roomSizeValueLabel.configure(text='{:.0f}'.format(math.floor(maxRoomSizeScale.get()))))
genButton = ttk.Button(UIFrame, text='Generate', command= lambda: dr.ButtonCallback(math.floor(roomNumScale.get()), imgLabel, imageFrame, ppi, math.floor(maxRoomSizeScale.get())))

roomNumScale.grid(row=2, column=0, sticky='n')
valueLabel.grid(row=1,column=0)
scaleLabel.grid(row=0, column=0)
roomSizeLabel.grid(row=3,column=0)
roomSizeValueLabel.grid(row=4, column=0)
maxRoomSizeScale.grid(row=5, column=0)
genButton.grid(row=6, column=0)

image = dr.GenerateMap(numRooms, ppi) #generate initial image with default params
imgLabel.configure(image=image) #place initial image

imgLabel.grid(row=0, column=0)
imageFrame.grid(row=0,column=0)
UIFrame.grid(row=0,column=1)
window.mainloop()