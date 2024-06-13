import os
import turtle
import sys

turtle.setup(500, 200)
turtle.hideturtle()
turtle.bgcolor("black")
turtle.pencolor("green")
turtle.write("Installing requirements...", align = "center", font = ("Arial", 20, "normal"))

try: os.system("pip install pygame colorama tk-tools")
except: pass
try: os.system("pip3 install pygame colorama tk-tools")
except: pass
try: os.system("python -m pip install pygame colorama tk-tools")
except: pass
try: os.system("python3 -m pip install pygame colorama tk-tools")
except: pass
try: os.system("sudo apt install python3-pygame python3-colorama python3-tk")
except: pass
try:
    import tkinter.messagebox as messagebox
    import tkinter.simpledialog as simpledialog
    import tkinter.colorchooser as colorchooser
    import tkinter.filedialog as filedialog
    import pygame
    import colorama
except:
    print("Error: missing modules. Unable to use pip.")
    sys.exit(1)

turtle.bye()