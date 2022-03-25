from ctypes import resize
import dungeonRoom as dr
import random
import tkinter as tk
from tkinter import ttk
from PIL import ImageTk, Image
window = tk.Tk()
#window.geometry('1280x720')
window.resizable(False, False)
imageFrame = ttk.Frame(window)
UIFrame = ttk.Frame(window)
numRooms = tk.DoubleVar()
roomNumScale = ttk.Scale(UIFrame, from_=1, to=100, variable=numRooms)

random.seed()
rooms = [] #initial roomlist
placedRooms = [] #rooms already placed in map, this is used for collision checking

dr.GenRooms(rooms, numRooms)

maxDimension = dr.GetMaxDimension(rooms)

map = dr.Map(5+maxDimension) #generates map big enough for the rooms + a buffer

#place rooms on the map, random walk from center
dr.PlaceRooms(rooms, placedRooms, map)

image = dr.DrawPicture(map)
image = ImageTk.PhotoImage(image)
imgLabel = ttk.Label(imageFrame, image=image)
imgLabel.grid(row=0, column=0)
imgLabel = ttk.Label(UIFrame, image=image)
imgLabel.grid(row=0,column=0)
imageFrame.grid(row=0,column=0)
UIFrame.grid(row=0,column=1)
window.mainloop()