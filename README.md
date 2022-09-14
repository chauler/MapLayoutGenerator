# Dungeon Layout Generator

By Alex Tomjack

Initially created for CSCE 3110 final project. Randomly generates a layout of rooms and doors using user-provided parameters. Also allows for pathfinding between two points selected by clicking on the image.

## Installation
The provided exe will run out of the box.
If you want to run the script itself, Python 3.10+ should first be installed, as well as the PIL library using pip:
```bash
pip install Pillow
```
Once this is finished, the program is run by running gen.py

The exe is created using pyinstaller (installed using pip) with
```bash
pyinstaller --onefile gen.py
```

## Usage
The program begins with a randomly generated map using default parameters. To generate your own map, adjust the parameters using the sliders, and press "Generate".

![image](https://user-images.githubusercontent.com/96323881/167211816-1f439c0d-697d-464a-8ec2-53afa37b2062.png)

The map consists of floors (the brown tiles), doors (the red tiles), and walls (the grey tiles). 

The pathfinding works by clicking clicking on two floor or door tiles. You can not select walls or empty tiles.

Once the second tile is clicked, a path will be displayed:

![image](https://user-images.githubusercontent.com/96323881/167212457-ef2eff7d-cb54-4853-9677-98e2ce72ddef.png)

You can pathfind again by clicking another set of points.
