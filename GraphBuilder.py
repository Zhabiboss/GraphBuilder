# Author: Zhabiboss

import os
import math
import json
import sys
try:
    import tkinter.messagebox as messagebox
    import tkinter.simpledialog as simpledialog
    import tkinter.colorchooser as colorchooser
    import tkinter
    import pygame
    import colorama
except:
    import installRequirements

colorama.init()

bg = colorama.Back
fg = colorama.Fore

print(f"{fg.GREEN} Initializing pygame... {fg.RESET}")
pygame.init()

print(f"{fg.GREEN} Initializing Graph Builder... {fg.RESET}")

general = json.load(open("Resources/general.json"))

fullscreen = general["fullscreen"]
if fullscreen:
    res = width, height = pygame.display.Info().current_w, pygame.display.Info().current_h
else:
    res = width, height = general["resolution"]["width"], general["resolution"]["height"]
screen = pygame.display.set_mode(res, pygame.FULLSCREEN if fullscreen else 0)

version = general["version"]
print(f"{fg.GREEN} Graph Builder version: {version} {fg.RESET}")
pygame.display.set_caption(f"Graph Builder {version}  |  unnamed graph")

clock = pygame.time.Clock()
fps = general["fps"]

fontFamily = general["font"]
if not os.path.isfile(f"Resources/{fontFamily}"):
    messagebox.showerror("Error", f"Font file not found: {fontFamily}")
    print(f"{fg.RED} Error: font file not found in /Resources/: {fontFamily} {fg.RESET}")
    sys.exit(1)

class font:
    small = pygame.font.Font(f"Resources/{fontFamily}", 14)
    medium = pygame.font.Font(f"Resources/{fontFamily}", 24)
    large = pygame.font.Font(f"Resources/{fontFamily}", 36)

vertexSelectionRange = general["vertexSelectionRange"]

drawBackgroundGrid = general["drawBackgroundGrid"]
backgroundGridColor = general["backgroundGridColor"]
backgroundGridSize = general["backgroundGridSize"]

class PopUpButton:
    def __init__(self, x, y, width, height, text, font, action):
        self.x, self.y = x, y
        self.width, self.height = width, height
        self.text = text
        self.font = font
        self.action = action

    @property
    def rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)
    
    def draw(self):
        if self.rect.collidepoint(pygame.mouse.get_pos()):
            pygame.draw.rect(screen, (200, 200, 200), self.rect)
        else:
            pygame.draw.rect(screen, (255, 255, 255), self.rect)
        text = self.font.render(self.text, True, (0, 0, 0))
        screen.blit(text, (self.x + self.width // 2 - text.get_width() // 2, self.y + self.height // 2 - text.get_height() // 2))

    def onClick(self):
        if self.rect.collidepoint(pygame.mouse.get_pos()):
            self.action()
            return True
        return False
    
class Button:
    def __init__(self, x, y, width, height, text, font, action):
        self.x, self.y = x, y
        self.width, self.height = width, height
        self.text = text
        self.font = font
        self.action = action

    @property
    def rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)
    
    def draw(self):
        if self.rect.collidepoint(pygame.mouse.get_pos()):
            pygame.draw.rect(screen, (200, 200, 200), self.rect)
        else:
            pygame.draw.rect(screen, (255, 255, 255), self.rect)
        text = self.font.render(self.text, True, (0, 0, 0))
        screen.blit(text, (self.x + self.width // 2 - text.get_width() // 2, self.y + self.height // 2 - text.get_height() // 2))

    def onClick(self):
        if self.rect.collidepoint(pygame.mouse.get_pos()):
            self.action()
            return True
        return False

def distance(x1, y1, x2, y2):
    return ((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5

def distanceToLine(x, y, lx1, ly1, lx2, ly2):
    # Calculate the line segment vector (lx2-lx1, ly2-ly1) and the point vector (x-lx1, y-ly1)
    line_vec_x = lx2 - lx1
    line_vec_y = ly2 - ly1
    point_vec_x = x - lx1
    point_vec_y = y - ly1
    
    # Calculate the length of the line segment
    line_length = distance(lx1, ly1, lx2, ly2)
    
    # If the segment's length is zero, it is a point, return distance to this point
    if line_length == 0:
        return distance(x, y, lx1, ly1)
    
    # Calculate the projection scalar of the point vector onto the line vector
    projection = (point_vec_x * line_vec_x + point_vec_y * line_vec_y) / (line_length ** 2)
    
    # Calculate the closest point on the segment
    if projection < 0:
        closest_x = lx1
        closest_y = ly1
    elif projection > 1:
        closest_x = lx2
        closest_y = ly2
    else:
        closest_x = lx1 + projection * line_vec_x
        closest_y = ly1 + projection * line_vec_y
    
    # Return the distance from the point to the closest point on the segment
    return distance(x, y, closest_x, closest_y)

vertices = []
edges = []
isWeighted = False
PopUpButtons: list[PopUpButton] = []
selected = None
buttons: list[Button] = []

location = None

content = ""
with open("Storage/latestRestart.json", "r") as latest:
    content = latest.read()
    if content != "":
        data = json.loads(content)
        vertices = data["vertices"]
        edges = data["edges"]
        isWeighted = data["isWeighted"]
        location = data["location"]
        pygame.display.set_caption(f"Graph Builder {version}  |  {os.path.basename(location)[:-5]}" if location != None \
                                   else f"Graph Builder {version}  |  unnamed graph")
    latest.close()

if content != "":
    with open("Storage/latestRestart.json", "w") as latest:
        latest.write("")
        latest.close()

contentF11 = ""
with open("Storage/latestRestartF11.json", "r") as latestF11:
    contentF11 = latestF11.read()
    if contentF11 != "":
        data = json.loads(contentF11)
        vertices = data["vertices"]
        edges = data["edges"]
        isWeighted = data["isWeighted"]
        location = data["location"]
        pygame.display.set_caption(f"Graph Builder {version}  |  {os.path.basename(location)[:-5]}" if location != None \
                                   else f"Graph Builder {version}  |  unnamed graph")
    latestF11.close()

if contentF11 != "":
    with open("Storage/latestRestartF11.json", "w") as latestF11:
        latestF11.write("")
        latestF11.close()

def save():
    global location
    location = simpledialog.askstring('Save graph', 'Graph name: ', initialvalue = 'Graph')
    if location == None: return
    pygame.display.set_caption(f"Graph Builder {version}  |  {location}")
    location += ".json"
    json.dump({
        "vertices": vertices, "edges": edges, "isWeighted": isWeighted
    }, open(location, "w"))

def load():
    global vertices, edges, isWeighted, location
    location = simpledialog.askstring('Load graph', 'Path to graph json: ', initialvalue = 'Graph.json')
    if location == None: return
    elif not os.path.isfile(location):
        messagebox.showerror("Error", f"File not found: {location}")
        print(f"{fg.RED} Error: file not found: {location} {fg.RESET}")
        return
    pygame.display.set_caption(f"Graph Builder {version}  |  {os.path.basename(location)[:-5]}")
    data = json.load(open(location, "r"))
    vertices = data["vertices"]
    edges = data["edges"]
    isWeighted = data["isWeighted"]

controlsInfo = general["controlsInfo"]

def properExit():
    if vertices == [] and edges == []: pygame.quit(); sys.exit()
    if not location: save()
    else:
        if not os.path.isfile(location): save()
        else:
            if json.load(open(location, "r")) != {"vertices": vertices, "edges": edges, "isWeighted": isWeighted}: save()
    pygame.quit()
    sys.exit(0)

def dijkstra(vertices, edges, start, end):
    start = tuple(start)
    end = tuple(end)
    vertices = [tuple(vertex) for vertex in vertices]
    edges = [[tuple(edge[0]), tuple(edge[1]), edge[2], edge[3]] for edge in edges]
    distances = {tuple(vertex): float("infinity") for vertex in vertices}
    previous = {tuple(vertex): None for vertex in vertices}
    distances[start] = 0
    unvisited = set(vertices)

    while unvisited:
        current = min(unvisited, key = lambda vertex: distances[vertex])
        unvisited.remove(current)

        if current == end:
            break

        for neighbor in vertices:
            if neighbor in unvisited:
                for edge in edges:
                    if edge[3] == "ds":
                        if edge[0] == current and edge[1] == neighbor:
                            alt = distances[current] + edge[2]
                            if alt < distances[neighbor]:
                                distances[neighbor] = alt
                                previous[neighbor] = current

                    elif edge[3] == "db":
                        if (edge[0] == current and edge[1] == neighbor) or (edge[1] == current and edge[0] == neighbor):
                            alt = distances[current] + edge[2]
                            if alt < distances[neighbor]:
                                distances[neighbor] = alt
                                previous[neighbor] = current

    path = []
    while end:
        path.append(end)
        end = previous[end]
    path.reverse()

    return path

def leastExpensivePath():
    start = simpledialog.askstring("Least expensive path", "Start vertex: ")
    if not start: return
    end = simpledialog.askstring("Least expensive path", "End vertex: ")
    if not end: return
    for vertex in vertices:
        if start == vertex[2]: start = vertex; break
    for vertex in vertices:
        if end == vertex[2]: end = vertex; break
    path = dijkstra(vertices, edges, start, end)
    messagebox.showinfo("Least expensive path", f"Path: {', '.join(vertex[2] for vertex in path)}")

def clear():
    global vertices, edges
    vertices.clear()
    edges.clear()

def settings():
    settings_ = general

    root = tkinter.Tk()
    root.title("Settings")
    root["bg"] = "#101010"
    root.geometry("450x200")
    root.resizable(False, False)
    
    """warningLabel = tkinter.Label(root, text = "After all changes restart is required.", fg = "yellow", bg = "#101010", font = ("Consolas", 14))
    warningLabel.grid(row = 0, column = 0, columnspan = 2, rowspan = 2)"""

    vertexSelectionRangeLabel = tkinter.Label(root, text = "Vertex selection range:", bg = "#101010", fg = "white", font = ("Consolas", 14))
    vertexSelectionRangeLabel.grid(row = 2, column = 0)
    vertexSelectionRangeEntry = tkinter.Entry(root, bg = "#202020", fg = "white")
    vertexSelectionRangeEntry.grid(row = 2, column = 1)
    vertexSelectionRangeEntry.insert(0, settings_["vertexSelectionRange"])

    def drawBackgroundGridChecked():
        if DBGCVar.get() == 1:
            settings_["drawBackgroundGrid"] = True
        else:
            settings_["drawBackgroundGrid"] = False
    
    DBGCVar = tkinter.IntVar(root)
    drawBackgroundGridCheckbox = tkinter.Checkbutton(root, text = "Draw background grid: ", bg = "#101010", fg = "white", font = ("Consolas", 14), 
                                             activebackground = "#101010", activeforeground = "white", offvalue = 0, onvalue = 1, selectcolor = "black",
                                             command = drawBackgroundGridChecked, variable = DBGCVar)
    drawBackgroundGridCheckbox.grid(row = 3, column = 0)
    if drawBackgroundGrid: drawBackgroundGridCheckbox.select()

    def fullscreenChecked():
        if fullscreenVar.get() == 1:
            settings_["fullscreen"] = True
        else:
            settings_["fullscreen"] = False
    
    fullscreenVar = tkinter.IntVar(root)
    fullscreenCheckbox = tkinter.Checkbutton(root, text = "Fullscreen: ", bg = "#101010", fg = "white", font = ("Consolas", 14), 
                                             activebackground = "#101010", activeforeground = "white", offvalue = 0, onvalue = 1, selectcolor = "black",
                                             command = fullscreenChecked, variable = fullscreenVar)
    fullscreenCheckbox.grid(row = 4, column = 0)
    if fullscreen: fullscreenCheckbox.select()

    backgroundGridColorLabel = tkinter.Label(root, text = "Background grid color: ", bg = "#101010", fg = "white", font = ("Consolas", 14))
    backgroundGridColorLabel.grid(row = 5, column = 0)

    def backgroundGridColorColorpicker_():
        color = colorchooser.askcolor(initialcolor = general["backgroundGridColor"])
        if color[1] != None:
            settings_["backgroundGridColor"] = color[1]

    backgroundGridColorColorpicker = tkinter.Button(root, text = "Choose color", bg = "#202020", fg = "white", font = ("Consolas", 14), command = backgroundGridColorColorpicker_)
    backgroundGridColorColorpicker.grid(row = 5, column = 1)
    backgroundGridSizeLabel = tkinter.Label(root, text = "Background grid size: ", bg = "#101010", fg = "white", font = ("Consolas", 14))
    backgroundGridSizeLabel.grid(row = 6, column = 0)
    backgroundGridSizeEntry = tkinter.Entry(root, bg = "#202020", fg = "white")
    backgroundGridSizeEntry.grid(row = 6, column = 1)
    backgroundGridSizeEntry.insert(0, settings_["backgroundGridSize"])
    
    def apply():
        try: 
            settings_["backgroundGridSize"] = int(backgroundGridSizeEntry.get())
            settings_["vertexSelectionRange"] = int(vertexSelectionRangeEntry.get())
        except: pass
        json.dump(settings_, open("Resources/general.json", "w"), indent = 4)

        json.dump({
            "vertices": vertices, "edges": edges, "isWeighted": isWeighted, "location": location
        }, open("Storage/latestRestart.json", "w"))

        python = sys.executable
        os.execl(python, python, * sys.argv)

    applyButton = tkinter.Button(root, text = "Apply", bg = "#fafafa", fg = "black", font = ("Consolas", 14), command = apply)
    applyButton.grid(row = 7, column = 0)

    root.mainloop()

buttons.append(Button(10, 10, 100, 40, "Save", font.medium, save))
buttons.append(Button(10, 60, 100, 40, "Load", font.medium, load))
buttons.append(Button(10, 110, 140, 40, "Controls", font.medium, lambda: messagebox.showinfo("Controls", "\n".join(controlsInfo))))
buttons.append(Button(10, 160, 110, 40, "Settings", font.medium, settings))
buttons.append(Button(10, 210, 100, 40, "Quit", font.medium, properExit))
buttons.append(Button(10, 310, 100, 40, "Clear", font.medium, clear))
buttons.append(Button(10, 360, 110, 40, "Dijkstra", font.medium, leastExpensivePath))

buttonPanelRect = pygame.Rect(0, 0, 160, height)
buttonPanelBG = pygame.Surface((buttonPanelRect.width, buttonPanelRect.height))
s = pygame.Surface((2, 5))
pygame.draw.line(s, (50, 50, 50), (0, 0), (0, 2))
pygame.draw.line(s, (50, 50, 50), (1, 2), (1, 5))
s.set_at((1, 0), (50, 50, 50))
buttonPanelBG.blit(pygame.transform.smoothscale(s, (buttonPanelRect.width, buttonPanelRect.height)), (0, 0))
del s

viewOffset = [0, 0]
prevMousePos = [0, 0]

while True:
    screen.fill((0, 0, 0))

    for event in pygame.event.get():
        if event.type == pygame.QUIT: properExit()

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_F11:
                general["fullscreen"] = not general["fullscreen"]
                json.dump(general, open("Resources/general.json", "w"), indent = 4)
                json.dump({
                    "vertices": vertices, "edges": edges, "isWeighted": isWeighted, "location": location
                }, open("Storage/latestRestartF11.json", "w"))
                python = sys.executable
                os.execl(python, python, * sys.argv)

        if event.type == pygame.MOUSEBUTTONDOWN:
            wasPopUpButtonPressed = False
            for button in PopUpButtons:
                if button.onClick(): wasPopUpButtonPressed = True; break
            if not wasPopUpButtonPressed:
                for button in buttons:
                    if button.onClick(): wasPopUpButtonPressed = True; break
                    
            if len(PopUpButtons) == 0 and not wasPopUpButtonPressed and not buttonPanelRect.collidepoint(*pygame.mouse.get_pos()):
                for button in buttons:
                    if button.rect.collidepoint(*pygame.mouse.get_pos()):
                        continue
                if pygame.mouse.get_pressed()[0]:
                    position = pygame.mouse.get_pos()
                    adjusted_pos = [position[0] + viewOffset[0], position[1] + viewOffset[1]]
                    selectedVertex = None
                    selectedEdge = None
                    for vertex in vertices:
                        if distance(adjusted_pos[0], adjusted_pos[1], vertex[0], vertex[1]) <= vertexSelectionRange: 
                            selectedVertex = vertex
                            break
                    if selectedVertex == None: 
                        for edge in edges:
                            if distanceToLine(adjusted_pos[0], adjusted_pos[1], edge[0][0], edge[0][1], edge[1][0], edge[1][1]) <= vertexSelectionRange:
                                selectedEdge = edge
                                break
                        if selectedEdge == None:
                            vertices.append([adjusted_pos[0], adjusted_pos[1], str(len(vertices) + 1)])

                    elif selectedVertex != None:
                        if selected != None:
                            vertex = selectedVertex
                            for edge in edges:
                                if edge[0] == vertex and edge[1] == selected: edges[edges.index(edge)][3] = "db"
                            if selected != vertex: edges.append([selected, vertex, 1, "ds"])
                            clickedOnVertex = True
                            selected = None
                        else:
                            selected = selectedVertex
                
                elif pygame.mouse.get_pressed()[2]:
                    position = pygame.mouse.get_pos()
                    adjusted_pos = [position[0] + viewOffset[0], position[1] + viewOffset[1]]
                    selectedVertex = None
                    selectedEdge = None
                    for vertex in vertices:
                        if distance(adjusted_pos[0], adjusted_pos[1], vertex[0], vertex[1]) <= vertexSelectionRange: 
                            selectedVertex = vertex
                            break
                    if selectedVertex == None: 
                        for edge in edges:
                            if distanceToLine(adjusted_pos[0], adjusted_pos[1], edge[0][0], edge[0][1], edge[1][0], edge[1][1]) <= vertexSelectionRange:
                                selectedEdge = edge
                                break
                        if selectedEdge == None:
                            vertices.append([adjusted_pos[0], adjusted_pos[1], str(len(vertices) + 1)])

                    if selectedEdge != None:
                        def clearPopUpButtons(): PopUpButtons.clear()
                        def remove():
                            if selectedEdge in edges:
                                edges.remove(selectedEdge)
                            clearPopUpButtons()
                        def changeWeight():
                            global isWeighted
                            try: edges[edges.index(selectedEdge)][2] = int(simpledialog.askstring("Change weight", "Weight: "))
                            except: 
                                messagebox.showerror("Error", "Invalid input")
                                print(f"{fg.RED} Error: invalid input {fg.RESET}")
                                edges[edges.index(selectedEdge)][2] = 1
                            isWeighted = True
                            clearPopUpButtons()

                        x, y = position[0], position[1]
                        width_, height_ = 200, 90
                        if x + width_ > width: x = width - width_
                        if y + height_ > height: y = height - height_
                        PopUpButtons.append(PopUpButton(x, y, 200, 40, "Change weight", font.medium, changeWeight))
                        PopUpButtons.append(PopUpButton(x, y + 50, 100, 40, "Remove", font.medium, remove))

                    elif selectedVertex != None:
                        def clearPopUpButtons(): PopUpButtons.clear()
                        def remove():
                            edges[:] = [edge for edge in edges if edge[0] != selectedVertex and edge[1] != selectedVertex]
                            vertices.remove(selectedVertex)
                            clearPopUpButtons()
                        def rename():
                            vertices[vertices.index(selectedVertex)][2] = simpledialog.askstring("Rename vertex", "New name: ")
                            clearPopUpButtons()

                        x, y = position[0], position[1]
                        width_, height_ = 100, 90
                        if x + width_ > width: x = width - width_
                        if y + height_ > height: y = height - height_
                        PopUpButtons.append(PopUpButton(x, y, 100, 40, "Rename", font.medium, rename))
                        PopUpButtons.append(PopUpButton(x, y + 50, 100, 40, "Remove", font.medium, remove))
            
            else:
                if not wasPopUpButtonPressed: PopUpButtons.clear()


    if len(PopUpButtons) == 0 and not buttonPanelRect.collidepoint(*pygame.mouse.get_pos()) and pygame.mouse.get_pressed()[1]:
        position = pygame.mouse.get_pos()
        movement = [position[0] - prevMousePos[0], position[1] - prevMousePos[1]]
        viewOffset[0] -= movement[0]
        viewOffset[1] -= movement[1]

    if drawBackgroundGrid:
        for x in range(0, width, backgroundGridSize):
            pygame.draw.line(screen, backgroundGridColor, (x - viewOffset[0] % backgroundGridSize, 0), (x - viewOffset[0] % backgroundGridSize, height))
        for y in range(0, height, backgroundGridSize):
            pygame.draw.line(screen, backgroundGridColor, (0, y - viewOffset[1] % backgroundGridSize), (width, y - viewOffset[1] % backgroundGridSize))
                
    for vertex in vertices:
        color = (50, 255, 50) if distance(pygame.mouse.get_pos()[0] + viewOffset[0], pygame.mouse.get_pos()[1] + viewOffset[1], vertex[0], vertex[1]) <= vertexSelectionRange else (255, 255, 255)
        if vertex == selected: color = (0, 200, 0)
        pygame.draw.circle(screen, color, (vertex[0] - viewOffset[0], vertex[1] - viewOffset[1]), 10)
        text = font.small.render(vertex[2], True, (255, 255, 255))
        screen.blit(text, (vertex[0] - text.get_width() // 2 - viewOffset[0], vertex[1] - 15 - text.get_height() - viewOffset[1]))

    for edge in edges:
        color = (255, 255, 255) if not distanceToLine(pygame.mouse.get_pos()[0] + viewOffset[0], pygame.mouse.get_pos()[1] + viewOffset[1], edge[0][0], edge[0][1], edge[1][0], edge[1][1]) <= vertexSelectionRange else (50, 255, 50)
        angle = math.atan2(edge[0][1] - edge[1][1], edge[0][0] - edge[1][0])
        pygame.draw.line(screen, color, (edge[0][0] - math.cos(angle) * 10 - viewOffset[0], edge[0][1] - math.sin(angle) * 10 - viewOffset[1]), 
                         (edge[1][0] + math.cos(angle) * 10 - viewOffset[0], edge[1][1] + math.sin(angle) * 10 - viewOffset[1]), 2)
        if isWeighted:
            text = font.small.render(str(edge[2]), True, (255, 255, 255), (0, 0, 0))
            screen.blit(text, ((edge[0][0] + edge[1][0]) // 2 - text.get_width() // 2 - viewOffset[0], (edge[0][1] + edge[1][1]) // 2 - text.get_height() // 2 - viewOffset[1]))
        
        if edge[3] == "ds":
            angle = math.atan2(edge[0][1] - edge[1][1], edge[0][0] - edge[1][0])
            pygame.draw.line(screen, color, (edge[1][0] + math.cos(angle) * 10 - viewOffset[0], edge[1][1] + math.sin(angle) * 10 - viewOffset[1]), 
                             (edge[1][0] + math.cos(angle - 2 * math.pi - math.pi / 8) * 20 - viewOffset[0], edge[1][1] + math.sin(angle - 2 * math.pi - math.pi / 8) * 20 - viewOffset[1]), 2)
            pygame.draw.line(screen, color, (edge[1][0] + math.cos(angle) * 10 - viewOffset[0], edge[1][1] + math.sin(angle) * 10 - viewOffset[1]), 
                             (edge[1][0] + math.cos(angle + 2 * math.pi + math.pi / 8) * 20 - viewOffset[0], edge[1][1] + math.sin(angle + 2 * math.pi + math.pi / 8) * 20 - viewOffset[1]), 2)
        elif edge[3] == "db":
            angle = math.atan2(edge[0][1] - edge[1][1], edge[0][0] - edge[1][0])
            pygame.draw.line(screen, color, (edge[1][0] + math.cos(angle) * 10 - viewOffset[0], edge[1][1] + math.sin(angle) * 10 - viewOffset[1]), 
                             (edge[1][0] + math.cos(angle - 2 * math.pi - math.pi / 8) * 20 - viewOffset[0], edge[1][1] + math.sin(angle - 2 * math.pi - math.pi / 8) * 20 - viewOffset[1]), 2)
            pygame.draw.line(screen, color, (edge[1][0] + math.cos(angle) * 10 - viewOffset[0], edge[1][1] + math.sin(angle) * 10 - viewOffset[1]), 
                             (edge[1][0] + math.cos(angle + 2 * math.pi + math.pi / 8) * 20 - viewOffset[0], edge[1][1] + math.sin(angle + 2 * math.pi + math.pi / 8) * 20 - viewOffset[1]), 2)
            angle = math.atan2(edge[1][1] - edge[0][1], edge[1][0] - edge[0][0])
            pygame.draw.line(screen, color, (edge[0][0] + math.cos(angle) * 10 - viewOffset[0], edge[0][1] + math.sin(angle) * 10 - viewOffset[1]), 
                             (edge[0][0] + math.cos(angle - 2 * math.pi - math.pi / 8) * 20 - viewOffset[0], edge[0][1] + math.sin(angle - 2 * math.pi - math.pi / 8) * 20 - viewOffset[1]), 2)
            pygame.draw.line(screen, color, (edge[0][0] + math.cos(angle) * 10 - viewOffset[0], edge[0][1] + math.sin(angle) * 10 - viewOffset[1]),
                             (edge[0][0] + math.cos(angle + 2 * math.pi + math.pi / 8) * 20 - viewOffset[0], edge[0][1] + math.sin(angle + 2 * math.pi + math.pi / 8) * 20 - viewOffset[1]), 2)
            
    for button in PopUpButtons:
        button.draw()

    screen.blit(buttonPanelBG, (buttonPanelRect.x, buttonPanelRect.y))
    for button in buttons:
        button.draw()

    screen.blit(font.small.render(f"Vertices: {len(vertices)}", True, "black", "white"), (10, height - 60))
    screen.blit(font.small.render(f"Edges: {len(edges)}", True, "black", "white"), (10, height - 40))
    screen.blit(font.small.render(f"Total weight: {sum([int(edge[2]) for edge in edges])}", True, "black", "white"), (10, height - 20))
    
    prevMousePos = list(pygame.mouse.get_pos())

    pygame.display.update()
    clock.tick(fps)

    if content != "":
        settings()
        content = ""
