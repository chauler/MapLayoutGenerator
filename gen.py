import dungeonRoom as dr
import random
from PIL import ImageTk, Image

def main():
    random.seed()

    #Initialize app
    window = dr.App()
    window.img = Image.new("RGB", (10, 10))
    
    #generate initial window with example map
    window.map, window.img = dr.GenerateMap()
    print((window.canvas.winfo_width(), window.canvas.winfo_height()))
    window.imgtk = ImageTk.PhotoImage(window.img.resize((750,750)))
    window.canvas.itemconfig('image', image = window.imgtk)
    print((window.canvas.winfo_width(), window.canvas.winfo_height()))
    window.mainloop()

if __name__ == "__main__":
    main()