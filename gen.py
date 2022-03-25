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
numRooms = 10
ppi=40
scaleLabel = ttk.Label(UIFrame, text='# of Rooms: ')
valueLabel = ttk.Label(UIFrame, text="10")
roomNumScale = ttk.Scale(UIFrame, from_=1, to=50, value=10, command= lambda event: valueLabel.configure(text='{:.0f}'.format(math.floor(roomNumScale.get()))))
genButton = ttk.Button(UIFrame, text='Generate', command= lambda: dr.ButtonCallback(math.floor(roomNumScale.get()), imgLabel, imageFrame, ppi))
roomNumScale.grid(row=2, column=0, sticky='n')
valueLabel.grid(row=1,column=0)
scaleLabel.grid(row=0, column=0)
genButton.grid(row=3, column=0)
image = dr.GenerateMap(numRooms, ppi)
imgLabel.configure(image=image)
imgLabel.grid(row=0, column=0)
imageFrame.grid(row=0,column=0)
UIFrame.grid(row=0,column=1)
window.mainloop()