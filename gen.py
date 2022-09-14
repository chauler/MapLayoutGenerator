import dungeonRoom as dr
import random
from PIL import ImageTk, Image

def main():
    random.seed()

    #Initialize app
    window = dr.App()
    window.resizable(False, False)
    window.img = Image.new("RGB", (10, 10))
    
    #generate initial window with example map
    window.map, window.img = dr.GenerateMap()
    window.imgtk = ImageTk.PhotoImage(window.img.resize((750,750), Image.ANTIALIAS))
    window.canvas.itemconfig('image', image = window.imgtk)
    window.mainloop()

if __name__ == "__main__":
    main()