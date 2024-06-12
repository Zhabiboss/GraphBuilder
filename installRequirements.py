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
try:
    import tkinter.messagebox
    import tkinter.simpledialog
    import pygame
    import colorama
except:
    print("Error: missing modules. Unable to use pip.")
    sys.exit(1)

turtle.bye()