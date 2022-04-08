import PySimpleGUI as sg
import random
import numpy as np
import time
from scipy.spatial import Delaunay
from PIL import ImageGrab
import glob

def find_numbering():
    filtered_list = []
    filtered_list.extend(glob.glob('canvas*.png'))
    i = 1
    while True:
        if f"canvas{i}.png" not in filtered_list:
            return i
        i += 1

class GraphStateMachine():
    def __init__(self, window):
        self.N = 0
        self.points = np.empty((0,2))
        self.window = window
        self.graph = window["-GRAPH-"]
        self.graph_info = window["-SHOW-NUM-"]
        self.canvasSize = self.graph.CanvasSize
        
    
    def plot_random(self, n):
        for _ in range(n):
            # Generate a random point
            point = [random.randrange(20, self.canvasSize[0]-20), random.randrange(20, self.canvasSize[1]-20)]
            self.points = np.append(self.points, [point], axis=0)
            # Plot on the graph
            self.graph.draw_circle(point, 5, fill_color='orange')
            self.N += 1
            self.graph_info.Update(f"{self.N} points on screen", visible = True)
    
    def __len__(self):
        return self.points.shape[0]
        

    def plot_point(self, mouse):
        # mouse = np.array(mouse)
        self.points = np.append(self.points, [mouse], axis=0)
        # Plot on the graph
        self.graph.draw_circle(mouse, 5, fill_color='orange')
        self.N += 1
        self.graph_info.Update(f"{self.N} points on screen", visible = True)

    def clear_points(self):
        self.N = 0
        self.points = np.empty((0,2))
        self.graph.erase()
        self.graph_info.Update(visible = False)

    def delaunay(self):
        if self.points.shape[0] < 3:
            return 
        self.tris = Delaunay(self.points)
        for simplex in self.tris.simplices:
            tri = np.append(self.points[simplex], self.points[simplex[:1]], axis=0)
            self.graph.draw_lines(tri, color='black', width=1)

    def clear_mesh(self):
        # Erase entire graph then plot back the points
        self.graph.erase()
        for point in self.points:
            self.graph.draw_circle(list(point), 5, fill_color='orange')
    
    def export_graph(self):
        export_num = find_numbering()
        filename = f"canvas{export_num}.png"
        widget = self.graph.Widget
        box = (widget.winfo_rootx(), widget.winfo_rooty(), widget.winfo_rootx() + widget.winfo_width(), widget.winfo_rooty() + widget.winfo_height())
        grab = ImageGrab.grab(bbox=box)
        grab.save(filename)
        return filename

def front_page():
    sg.theme("DarkBlue12")
    layout = [
        [sg.Text("Delaunay Mesh Creation App", font=("Any 15"))],
        [sg.Button("Start", expand_x = True)]
    ]

    window = sg.Window("Delaunay Creation", layout)
    while True:
        event, values = window.read()
        if event == sg.WIN_CLOSED: # if user closes window or clicks cancel
            break
        elif event == "Start":
            window.close()
            Delaunay_creation()
            return 
    window.close()

def Delaunay_creation():
    sg.theme("Topanga")
    w, h = sg.Window.get_screen_size()
    layout = [
        [sg.Push(), sg.Text("Delaunay Mesh Creation Playground", font=("Any 20")), sg.Push()],
        [
            sg.Push(),
            sg.Graph(
                        canvas_size=(int(0.8*w), int(0.8*h)),
                        graph_bottom_left=(0, 0),
                        graph_top_right=(int(0.8*w), int(0.8*h)),
                        key="-GRAPH-",
                        change_submits=True,  # mouse click events
                        background_color='white'
        ),
            sg.Push()],
        [
            sg.Button("Generate Points", key="-GENERATE20-"),
            sg.Button("Clear All", key="-CLEAR-"),
            sg.Button("Export", key="-EXPORT-"),
            sg.Push(),
            sg.Button("Create Mesh", key="-DMC-"),
            sg.Push(),
            sg.Text("", visible = False, key = "-SHOW-NUM-"),
        ]
    ]
    window = sg.Window("Mesh Creation Playground", layout, resizable = True, finalize = True)
    window.maximize()
    # Initialize Graph State Machine
    GSM = GraphStateMachine(window)
    while True:
        event, values = window.read()
        if event == sg.WIN_CLOSED: # if user closes window or clicks cancel
            break
        elif event == '-GRAPH-':
            mouse = values['-GRAPH-']
            # If it is not mouse click
            if mouse == (None, None):
                continue
            # State Machine Plot the point, increase num_lm and save to table database. 
            GSM.plot_point(mouse)
        elif event == "-GENERATE20-":
            N = 20
            GSM.plot_random(N)
        elif event == "-CLEAR-":
            GSM.clear_points()
        elif event == "-DMC-":
            GSM.clear_mesh()
            GSM.delaunay()
        elif event == "-EXPORT-":
            filename = GSM.export_graph()
            sg.popup(f"Your exported image is {filename} . You're welcome!")
    window.close()

if __name__ == "__main__":
    front_page()