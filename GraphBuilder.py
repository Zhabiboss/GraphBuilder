import os
import math
import json
import sys
try:
    import tkinter.messagebox
    import tkinter.simpledialog
    import tkinter
    import pygame
    import colorama
except:
    import os
    import turtle

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

colorama.init()

bg = colorama.Back
fg = colorama.Fore

print(f"{fg.GREEN} Initializing pygame... {fg.RESET}")
pygame.init()

print(f"{fg.GREEN} Initalizing Graph Builder... {fg.RESET}")

general = json.load(open("Resources/general.json"))

fullscreen = general["fullscreen"]
if fullscreen: res = width, height = pygame.display.Info().current_w, pygame.display.Info().current_h
else: res = width, height = general["resolution"]["width"], general["resolution"]["height"]
screen = pygame.display.set_mode(res, pygame.FULLSCREEN if fullscreen else 0)

version = general["version"]
print(f"{fg.GREEN} Graph Builder version: {version} {fg.RESET}")
pygame.display.set_caption(f"Graph Builder {version}  |  unnamed graph")

clock = pygame.time.Clock()
fps = general["fps"]

fontFamily = general["font"]
if not os.path.isfile(f"Resources/{fontFamily}"):
    tkinter.messagebox.showerror("Error", f"Font file not found: {fontFamily}")
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

def save():
    global location
    location = tkinter.simpledialog.askstring('Save graph', 'Graph name: ', initialvalue = 'Graph')
    if location == None: return
    pygame.display.set_caption(f"Graph Builder {version}  |  {location}")
    location += ".json"
    json.dump({
        "vertices": vertices, "edges": edges, "isWeighted": isWeighted
    }, open(location, "w"))
buttons.append(Button(10, 10, 100, 40, "Save", font.medium, save))

def load():
    global vertices, edges, isWeighted, location
    location = tkinter.simpledialog.askstring('Load graph', 'Path to graph json: ', initialvalue = 'Graph.json')
    if location == None: return
    elif not os.path.isfile(location):
        tkinter.messagebox.showerror("Error", f"File not found: {location}")
        print(f"{fg.RED} Error: file not found: {location} {fg.RESET}")
        return
    pygame.display.set_caption(f"Graph Builder {version}  |  {os.path.basename(location)[:-5]}")
    data = json.load(open(location, "r"))
    vertices = data["vertices"]
    edges = data["edges"]
    isWeighted = data["isWeighted"]
buttons.append(Button(10, 60, 100, 40, "Load", font.medium, load))

controlsInfo = general["controlsInfo"]
buttons.append(Button(10, 110, 140, 40, "Controls", font.medium, lambda: tkinter.messagebox.showinfo("Controls", "\n".join(controlsInfo))))

def properExit():
    if vertices == [] and edges == []: pygame.quit(); sys.exit()
    if not location: save()
    else:
        if not os.path.isfile(location): save()
        else:
            if json.load(open(location, "r")) != {"vertices": vertices, "edges": edges, "isWeighted": isWeighted}: save()
    pygame.quit()
    sys.exit(0)

buttons.append(Button(10, 160, 100, 40, "Quit", font.medium, properExit))

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
    start = tkinter.simpledialog.askstring("Least expensive path", "Start vertex: ")
    if not start: return
    end = tkinter.simpledialog.askstring("Least expensive path", "End vertex: ")
    if not end: return
    for vertex in vertices:
        if start == vertex[2]: start = vertex; break
    for vertex in vertices:
        if end == vertex[2]: end = vertex; break
    path = dijkstra(vertices, edges, start, end)
    tkinter.messagebox.showinfo("Least expensive path", f"Path: {', '.join(vertex[2] for vertex in path)}")

buttons.append(Button(10, 210, 120, 40, "Dijkstra", font.medium, leastExpensivePath))

def clear():
    global vertices, edges
    vertices.clear()
    edges.clear()
buttons.append(Button(10, 260, 100, 40, "Clear", font.medium, clear))

def settings():
    settings_ = general

    root = tkinter.Tk()
    root.title("Settings")
    root["bg"] = "#101010"
    root.geometry("600x600")
    root.resizable(False, False)
    
    warningLabel = tkinter.Label(root, text = "After all changes restart is required.", fg = "yellow", bg = "#101010", font = ("Consolas", 14))
    warningLabel.grid(row = 0, column = 0, columnspan = 2, rowspan = 2)

    vertexSelectionRangeLabel = tkinter.Label(root, text = "Vertex selection range:", bg = "#101010", fg = "white", font = ("Consolas", 14))
    vertexSelectionRangeLabel.grid(row = 2, column = 0)
    vertexSelectionRangeEntry = tkinter.Entry(root, bg = "#202020", fg = "white")
    vertexSelectionRangeEntry.grid(row = 2, column = 1)

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

    backgroundGridColorLabel = tkinter.Label(root, text = "Background grid color: ", bg = "#101010", fg = "white", font = ("Consolas", 14))
    backgroundGridColorLabel.grid(row = 5, column = 0)
    backgroundGridColorEntry = tkinter.Entry(root, bg = "#202020", fg = "white")
    backgroundGridColorEntry.grid(row = 5, column = 1)

    backgroundGridSizeLabel = tkinter.Label(root, text = "Background grid size: ", bg = "#101010", fg = "white", font = ("Consolas", 14))
    backgroundGridSizeLabel.grid(row = 6, column = 0)
    backgroundGridSizeEntry = tkinter.Entry(root, bg = "#202020", fg = "white")
    backgroundGridSizeEntry.grid(row = 6, column = 1)
    
    def apply():
        try: 
            pygame.Color(backgroundGridColorEntry.get())
            settings_["backgroundGridColor"] = backgroundGridColorEntry.get()
        except: pass
        try: 
            settings_["backgroundGridSize"] = int(backgroundGridSizeEntry.get())
            settings_["vertexSelectionRange"] = int(vertexSelectionRangeEntry.get())
        except: pass
        json.dump(settings_, open("Resources/general.json", "w"), indent = 4)

    applyButton = tkinter.Button(root, text = "Apply", bg = "#fafafa", fg = "black", font = ("Consolas", 14), command = apply)
    applyButton.grid(row = 7, column = 0, columnspan = 2)

    root.mainloop()
buttons.append(Button(10, 310, 110, 40, "Settings", font.medium, settings))

buttonPanelRect = pygame.Rect(0, 0, 150, height)
buttonPanelBG = pygame.Surface((buttonPanelRect.width, buttonPanelRect.height))
s = pygame.Surface((2, 2))
s.set_at((0, 0), (50, 50, 50))
s.set_at((1, 1), (50, 50, 50))
s.set_at((0, 1), (0, 0, 0))
s.set_at((1, 0), (0, 0, 0))
buttonPanelBG.blit(pygame.transform.smoothscale(s, (buttonPanelRect.width, buttonPanelRect.height)), (0, 0))
del s

while True:
    screen.fill((0, 0, 0))

    for event in pygame.event.get():
        if event.type == pygame.QUIT: properExit()

        """if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_F11:
                fullscreen = not fullscreen
                if fullscreen: res = width, height = pygame.display.Info().current_w, pygame.display.Info().current_h
                else: res = width, height = general["resolution"]["width"], general["resolution"]["height"]
                screen = pygame.display.set_mode(res, pygame.FULLSCREEN if fullscreen else 0)
                class font:
                    small = pygame.font.Font(f"Resources/{fontFamily}", 14)
                    medium = pygame.font.Font(f"Resources/{fontFamily}", 24)
                    large = pygame.font.Font(f"Resources/{fontFamily}", 36)"""

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
                    selectedVertex = None
                    selectedEdge = None
                    for vertex in vertices:
                        if distance(position[0], position[1], vertex[0], vertex[1]) <= vertexSelectionRange: 
                            selectedVertex = vertex
                            break
                    if selectedVertex == None: 
                        for edge in edges:
                            if distanceToLine(position[0], position[1], edge[0][0], edge[0][1], edge[1][0], edge[1][1]) <= vertexSelectionRange:
                                selectedEdge = edge
                                break
                        if selectedEdge == None:
                            vertices.append([position[0], position[1], str(len(vertices) + 1)])

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
                    selectedVertex = None
                    selectedEdge = None
                    for vertex in vertices:
                        if distance(position[0], position[1], vertex[0], vertex[1]) <= vertexSelectionRange: 
                            selectedVertex = vertex
                            break
                    if selectedVertex == None: 
                        for edge in edges:
                            if distanceToLine(position[0], position[1], edge[0][0], edge[0][1], edge[1][0], edge[1][1]) <= vertexSelectionRange:
                                selectedEdge = edge
                                break
                        if selectedEdge == None:
                            vertices.append([position[0], position[1], str(len(vertices) + 1)])

                    if selectedEdge != None:
                        def clearPopUpButtons(): PopUpButtons.clear()
                        def remove():
                            edges.remove(edges[edges.index(edge)])
                            clearPopUpButtons()
                        def changeWeight():
                            global isWeighted
                            try: edges[edges.index(selectedEdge)][2] = int(tkinter.simpledialog.askstring("Change weight", "Weight: "))
                            except: 
                                tkinter.messagebox.showerror("Error", "Invalid input")
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
                            index = vertices.index(selectedVertex)
                            for edge in edges:
                                for i in edge[:1]:
                                    if i == index:
                                        edges.remove(edge)
                                        break
                                    elif i > index:
                                        edge[edge.index(i)] -= 1
                            vertices.remove(selectedVertex)
                            clearPopUpButtons()
                        def rename():
                            vertices[vertices.index(selectedVertex)][2] = tkinter.simpledialog.askstring("Rename vertex", "New name: ")
                            clearPopUpButtons()

                        x, y = position[0], position[1]
                        width_, height_ = 100, 90
                        if x + width_ > width: x = width - width_
                        if y + height_ > height: y = height - height_
                        PopUpButtons.append(PopUpButton(x, y, 100, 40, "Rename", font.medium, rename))
                        PopUpButtons.append(PopUpButton(x, y + 50, 100, 40, "Remove", font.medium, remove))
            
            else:
                if not wasPopUpButtonPressed: PopUpButtons.clear()

    if drawBackgroundGrid:
        for x in range(0, width, backgroundGridSize):
            pygame.draw.line(screen, backgroundGridColor, (x, 0), (x, height))
        for y in range(0, height, backgroundGridSize):
            pygame.draw.line(screen, backgroundGridColor, (0, y), (width, y))
                
    for vertex in vertices:
        color = (255, 255, 255) if not distance(pygame.mouse.get_pos()[0], pygame.mouse.get_pos()[1], vertex[0], vertex[1]) <= vertexSelectionRange else (50, 255, 50)
        pygame.draw.circle(screen, color, (vertex[0], vertex[1]), 10)
        text = font.small.render(vertex[2], True, (255, 255, 255))
        screen.blit(text, (vertex[0] - text.get_width() // 2, vertex[1] - 15 - text.get_height()))

    for edge in edges:
        color = (255, 255, 255) if not distanceToLine(pygame.mouse.get_pos()[0], pygame.mouse.get_pos()[1], edge[0][0], edge[0][1], edge[1][0], edge[1][1]) <= vertexSelectionRange else (50, 255, 50)
        pygame.draw.line(screen, color, (edge[0][0], edge[0][1]), (edge[1][0], edge[1][1]), 2)
        if isWeighted:
            text = font.small.render(str(edge[2]), True, (255, 255, 255))
            pygame.draw.rect(screen, (0, 0, 0), text.get_rect(center = ((edge[0][0] + edge[1][0]) // 2, (edge[0][1] + edge[1][1]) // 2)))
            screen.blit(text, ((edge[0][0] + edge[1][0]) // 2 - text.get_width() // 2, (edge[0][1] + edge[1][1]) // 2 - text.get_height() // 2))
        
        if edge[3] == "ds":
            angle = math.atan2(edge[0][1] - edge[1][1], edge[0][0] - edge[1][0])
            pygame.draw.line(screen, color, (edge[1][0] + math.cos(angle) * 10, edge[1][1] + math.sin(angle) * 10), 
                             (edge[1][0] + math.cos(angle - 2 * math.pi - math.pi / 8) * 20, edge[1][1] + math.sin(angle - 2 * math.pi - math.pi / 8) * 20), 2)
            pygame.draw.line(screen, color, (edge[1][0] + math.cos(angle) * 10, edge[1][1] + math.sin(angle) * 10), 
                             (edge[1][0] + math.cos(angle + 2 * math.pi + math.pi / 8) * 20, edge[1][1] + math.sin(angle + 2 * math.pi + math.pi / 8) * 20), 2)
        elif edge[3] == "db":
            angle = math.atan2(edge[0][1] - edge[1][1], edge[0][0] - edge[1][0])
            pygame.draw.line(screen, color, (edge[1][0] + math.cos(angle) * 10, edge[1][1] + math.sin(angle) * 10), 
                             (edge[1][0] + math.cos(angle - 2 * math.pi - math.pi / 8) * 20, edge[1][1] + math.sin(angle - 2 * math.pi - math.pi / 8) * 20), 2)
            pygame.draw.line(screen, color, (edge[1][0] + math.cos(angle) * 10, edge[1][1] + math.sin(angle) * 10), 
                             (edge[1][0] + math.cos(angle + 2 * math.pi + math.pi / 8) * 20, edge[1][1] + math.sin(angle + 2 * math.pi + math.pi / 8) * 20), 2)
            angle = math.atan2(edge[1][1] - edge[0][1], edge[1][0] - edge[0][0])
            pygame.draw.line(screen, color, (edge[0][0] + math.cos(angle) * 10, edge[0][1] + math.sin(angle) * 10), 
                             (edge[0][0] + math.cos(angle - 2 * math.pi - math.pi / 8) * 20, edge[0][1] + math.sin(angle - 2 * math.pi - math.pi / 8) * 20), 2)
            pygame.draw.line(screen, color, (edge[0][0] + math.cos(angle) * 10, edge[0][1] + math.sin(angle) * 10),
                             (edge[0][0] + math.cos(angle + 2 * math.pi + math.pi / 8) * 20, edge[0][1] + math.sin(angle + 2 * math.pi + math.pi / 8) * 20), 2)
            
    for button in PopUpButtons:
        button.draw()

    screen.blit(buttonPanelBG, (buttonPanelRect.x, buttonPanelRect.y))
    for button in buttons:
        button.draw()

    screen.blit(font.small.render(f"Vertices: {len(vertices)}", True, "black", "white"), (10, height - 20))
    screen.blit(font.small.render(f"Edges: {len(edges)}", True, "black", "white"), (10, height - 40))
    screen.blit(font.small.render(f"Total weight: {sum([int(edge[2]) for edge in edges])}", True, "black", "white"), (10, height - 60))

    pygame.display.flip()
    clock.tick(fps)