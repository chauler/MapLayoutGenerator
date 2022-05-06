# Dungeon Layout Generator

By Alex Tomjack

Created for CSCE 3110 final project. Randomly generates a layout of rooms and doors using user-provided parameters. Also allows for pathfinding between two points selected by clicking on the image.

## Installation
The provided exe will run out of the box.
If you want to run the script itself, Python 3.10 should first be installed, as well as the PIL library using pip:
```bash
pip install Pillow
```
Once this is finished, the program is run by running gen.py

The exe is created using pyinstaller (installed using pip) with
```bash
pyinstaller --onefile gen.py
```

## Usage
