from ctypes import resize
import tkinter
from turtle import onclick
import dungeonRoom as dr
import math
import random
import tkinter as tk
from tkinter import NW, ttk
from PIL import ImageTk, Image
def main():
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
    image = dr.GenerateMap(numRooms, ppi) #generate initial image with default params
    #image = image.resize((750, 750), Image.ANTIALIAS)
    imgtk = ImageTk.PhotoImage(image.resize((750,750), Image.ANTIALIAS))

    #Build UI elements
    def BuildUI(imageFrame, imgLabel, UIFrame, ppi):
        canvas = tk.Canvas(imageFrame, width=750, height=750)
        canvas.bind("<Button-1>", lambda event: dr.canvasOnClick(event, ppi, canvasImage, canvas))
        scaleLabel = ttk.Label(UIFrame, text='# of Rooms: ')
        valueLabel = ttk.Label(UIFrame, text="10")
        roomSizeLabel = ttk.Label(UIFrame, text="Max Room Size:")
        roomSizeValueLabel = ttk.Label(UIFrame, text="10")
        roomNumScale = ttk.Scale(UIFrame, from_=1, to=100, value=10, command= lambda event: valueLabel.configure(text='{:.0f}'.format(math.floor(roomNumScale.get()))))
        maxRoomSizeScale = ttk.Scale(UIFrame, from_=6, to=20, value=10, command= lambda event: roomSizeValueLabel.configure(text='{:.0f}'.format(math.floor(maxRoomSizeScale.get()))))
        genButton = ttk.Button(UIFrame, text='Generate', command= lambda: dr.ButtonCallback(math.floor(roomNumScale.get()), canvas, ppi, math.floor(maxRoomSizeScale.get()), canvasImage))
        return scaleLabel,valueLabel,roomSizeLabel,roomSizeValueLabel,roomNumScale,maxRoomSizeScale,genButton,canvas
    scaleLabel, valueLabel, roomSizeLabel, roomSizeValueLabel, roomNumScale, maxRoomSizeScale, genButton, canvas = BuildUI(imageFrame, imgLabel, UIFrame, ppi)
    canvasImage = canvas.create_image(0, 0, anchor=NW, image=imgtk)
    #imgLabel.configure(image=image) #place initial image
    
    def PlaceUI():
        roomNumScale.grid(row=2, column=0, sticky='n')
        valueLabel.grid(row=1,column=0)
        scaleLabel.grid(row=0, column=0)
        roomSizeLabel.grid(row=3,column=0)
        roomSizeValueLabel.grid(row=4, column=0)
        maxRoomSizeScale.grid(row=5, column=0)
        genButton.grid(row=6, column=0)
        canvas.grid(row=0, column=0)
        #imgLabel.grid(row=0, column=0)
        imageFrame.grid(row=0,column=0)
        UIFrame.grid(row=0,column=1)
    PlaceUI()
    window.mainloop()

if __name__ == "__main__":
    main()