from tkinter import *
from tkinter import ttk, Tk, Canvas
import tkinter.messagebox
import tkinter.colorchooser
import tkinter.filedialog
import os, shutil, time
from PIL import ImageTk, Image
from ncempy.io import dm
import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
import matplotlib.animation as animation
from matplotlib import style
style.use('ggplot')
from matplotlib.backends.backend_tkagg import FigureCanvasAgg
import numpy as np
import imageio
import cv2
import json
from SET import projectName, projectDir, madeActionBeforeLastSave, windowarr, old_mouse_x, old_mouse_y, zoomArr
# <summary>
# Each EDS window class
# </summary>
class edsWindow:
    def __init__(self, name, parent, windowInstance, TkImage, position, zoomScale, scaleColor="#FFFFFF", previousMaterialName=None, nextMaterialName=None, isActive=False, canvas=None, energyArr=None, countArry=None, tool="Move", madeChangeBeforeSaving=True):
        self.name = name
        self.parent = parent
        self.windowInstance = windowInstance
        self.TkImage = TkImage
        self.position = position
        self.zoomScale = zoomScale
        self.scaleColor = scaleColor
        self.previousMaterialName = previousMaterialName
        self.nextMaterialName = nextMaterialName
        self.isActive = isActive
        self.canvas = canvas
        self.tool = tool
        self.energyArr = energyArr # x-axis data
        self.countArr = countArr # y-axis data
        self.madeChangeBeforeSaving = madeChangeBeforeSaving
# <summary>
# End of each EDS window class
# </summary>

# Create eds file window
def openNewEDS():
    # File browser and creating window
    fileDir = tkinter.filedialog.askopenfilenames(initialdir="/", title="Select a material", filetypes=(("emsa files", "*.emsa"),))
    if len(fileDir) == 0:
        return
    fileNameArr = fileDir[0].split('/')
    fileName = fileNameArr[len(fileNameArr)-1]
    window = Toplevel()
    window.title(fileName)
    window.resizable(0,0)
    window.geometry("1000x665+700+300")

    parentName = fileName

    # Plot the emsa spectrum data
    fileDateArr = []
    for i in range(2100):
        fileDateArr.append([])
    isdata = False
    data = []
    f = open(fileDir[0], "r")
    for r in f:
        if "#DATE" in r:
            fileDateArr.append(r.replace('#DATE        : ',''))
        elif "#SPECTRUM" in r:
            isdata = True
        elif isdata and "#ENDOFDATA" not in r:
            txt = r.strip()
            txt = txt.split(',')
            data.append([float(txt[0]), float(txt[1])])

    root = tkinter.Toplevel()
    cv = Canvas(root, width=450, height=300, bd=0)
    cv.pack()
    eds_img = ImageTk.PhotoImage(file="testgraph1.png")
    canvasImage = cv.create_image(0, 0, image=eds_img, anchor="nw")
    root.mainloop()

    
    # Check to see if current material is open yet; if it is, make a copy of it increasing a number at the end of the file name; if not, just save it as its file name
    if fileName in windowarr.keys():
        for x in range(len(windowarr)):
            if (fileName + " (copy " + str(x+1) + ")") in windowarr.keys():
                continue
            else:
                window.title(fileName + " (copy " + str(x+1) + ")")
                '''
                windowObj = edsWindow(fileName + " (copy " + str(x+1) + ")", fileName + " (copy " + str(x+1) + ")", windowInstance=window, position=[0,0], zoomScale=1, energyArr=data[:,0], countArr=data[:,1] isActive=True) # Create window object
                updateWindowMenu(fileName + " (copy " + str(x+1) + ")")
                windowarr[fileName + " (copy " + str(x+1) + ")"] = windowObj
                windowarr[fileName + " (copy " + str(x+1) + ")"].lineArr = []
                
                canvas = Canvas(window, width=595, height=595, bd=0, highlightthickness=0)
                canvas.pack(side="top", fill="both", expand="yes")
                canvas.place(x=66, y=0, anchor='nw')
                canvas.create_image(0, 0, image=windowarr[fileName].TkImage, anchor=NW)
                canvas.bind('<B1-Motion>', lambda x: clickedCanvas(x, newFileName))
                canvas.bind('<ButtonRelease-1>', lambda x: stopClickedCanvas(x, newFileName))

                windowarr[fileName + " (copy " + str(x+1) + ")"].windowInstance = window
                windowarr[fileName + " (copy " + str(x+1) + ")"].canvas = canvas
                '''
    else:
        En=np.array(data)[:,0]
        Ct=np.array(data)[:,1]
        print(Ct)

        windowObj = edsWindow(fileName, fileName, TkImage=eds_img, windowInstance=window, position=[0,0], zoomScale=1, energyArr=En, countArr=Ct, isActive=True) # Create window object
        updateWindowMenu(fileName)
        windowarr[fileName] = windowObj

        root = tkinter.Toplevel()
        
        # Create a canvas
        w, h = 300, 200
        canvas = Canvas(window, width=w, height=h, bd=0, highlightthickness=0)
        canvas.pack(side="top", fill="both", expand="yes")
        canvas.place(x=66, y=0, anchor='nw')
        canvas.create_image(0, 0, image="testgraph1.png", anchor=NW)
        canvas.bind('<B1-Motion>', lambda x: clickedCanvas(x, fileName))
        canvas.bind('<ButtonRelease-1>', lambda x: stopClickedCanvas(x, fileName))
        
        window.protocol("WM_DELETE_WINDOW", lambda name=fileName: matQuit(name))
        windowarr[fileName].windowInstance = window
        windowarr[fileName].canvas = canvas

        root.mainloop()



""" Draw a matplotlib figure onto a Tk canvas
    loc: location of top-left corner of figure on canvas in pixels.
    Inspired by matplotlib source: lib/matplotlib/backends/backend_tkagg.py
    """
def draw_figure(canvas, figure, loc=(0, 0)):
    '''
    figure_canvas_agg = FigureCanvasAgg(figure)
    figure_canvas_agg.draw()
    figure_x, figure_y, figure_w, figure_h = figure.bbox.bounds
    figure_w, figure_h = int(figure_w), int(figure_h)
    photo = tkinter.PhotoImage(master=canvas, width=figure_w, height=figure_h)

    # Position: convert from top-left anchor to center anchor
    canvas.create_image(loc[0] + figure_w/2, loc[1] + figure_h/2, image=photo)

    # Unfortunately, there's no accessor for the pointer to the native renderer
    tkagg.blit(photo, figure_canvas_agg.get_renderer()._renderer, colormode=2)

    # Return a handle which contains a reference to the photo object
    # which must be kept live or else the picture disappears
    return photo
    '''