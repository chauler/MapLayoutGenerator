import generation as dr
import UIHandling as UI
import random
from PIL import Image

def main():
    random.seed()

    #Initialize app
    window = UI.App()
    
    #generate initial window with example map
    #window.map, window.img = dr.GenerateMap()
    #window.DisplayImage((750,750))
    window.mainloop()

if __name__ == "__main__":
    main()