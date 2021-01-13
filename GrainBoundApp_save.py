# <summary>
# Dependencies
# </summary>
from tkinter import *
from tkinter import ttk, Tk, Canvas
import tkinter.messagebox
import tkinter.colorchooser
import os, shutil, time
import tkinter.filedialog
from PIL import ImageTk, Image
from ncempy.io import dm
import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
import matplotlib.animation as animation
import matplotlib.backends.backend_tkagg as tkagg
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, NavigationToolbar2Tk)
from matplotlib.backend_bases import key_press_handler
from matplotlib.ticker import (MultipleLocator, FormatStrFormatter, AutoMinorLocator)
from matplotlib import style
from matplotlib.widgets import TextBox
style.use('ggplot')
from matplotlib.backends.backend_tkagg import FigureCanvasAgg
import numpy as np
import imageio
import cv2
from subprocess import Popen
import webbrowser
import json
from SET import windowmenu, projectName, projectDir, madeActionBeforeLastSave, windowarr, old_mouse_x, old_mouse_y, zoomArr
# <summary>
# End of dependencies
# </summary>

# <summary>
# Code before tkinter code
# </summary>
np.set_printoptions(threshold=sys.maxsize)
# <summary>
# End of code before tkinter code
# </summary>

# <summary>
# Each material window class
# </summary>
class materialWindow:
    def __init__(self, name, parent, windowInstance, TkImage, position, zoomScale, scaleColor="#FFFFFF", lineArr=None, nextMaterialName=None, previousMaterialName=None, isActive=False, canvas=None, imageArr=None, tool="Move", brightness=0, contrast=float(1), gamma=float(1), madeChangeBeforeSaving=True):
        self.madeChangeBeforeSaving = madeChangeBeforeSaving
        self.TkImage = TkImage
        self.imageArr = imageArr
        self.name = name
        self.position = position
        self.zoomScale = zoomScale
        self.lineArr = lineArr
        self.parent = parent
        self.canvas = canvas
        self.scaleColor = scaleColor
        self.tool = tool
        self.brightness = brightness
        self.contrast = contrast
        self.gamma = gamma
        self.windowInstance = windowInstance
        self.nextMaterialName = nextMaterialName
        self.previousMaterialName = previousMaterialName
        self.isActive = isActive
# <summary>
# End of each material window class
# </summary>


# <summary>
# Each EDS window class
# </summary>
class edsWindow:
    def __init__(self, name, parent, windowInstance, position, zoomScale, scaleColor="#FFFFFF", isActive=False, canvas=None, energymain=None, energyleft=None, energyright=None, countmain=None, countleft=None, countright=None, madeChangeBeforeSaving=True):
        self.name = name
        self.parent = parent
        self.windowInstance = windowInstance
        self.position = position
        self.zoomScale = zoomScale
        self.scaleColor = scaleColor
        self.isActive = isActive
        self.canvas = canvas
        self.energymain = energymain # x-axis data
        self.energyleft = energyleft
        self.energyright = energyright
        self.countmain = countmain # y-axis data
        self.countleft = countleft
        self.countright = countright
        self.madeChangeBeforeSaving = madeChangeBeforeSaving
# <summary>
# End of each EDS window class
# </summary>

# <summary>
# Global variables
# </summary>
bokehProcess = {} # Dictionary of bokehProcess ports
# <summary>
# End of global variables
# </summary>

# <summary>
# Custom tkinter function code
# </summary>
def todo(debug=""):
    print("TODO " + str(debug))

def openBokeh():
    global bokehProcess

    for i in range(5006, 5100):
        if str(i) in bokehProcess:
            pass
        else:
            bokehProcess[str(i)] = Popen(['bokeh', 'serve', '--show', '--port', str(i), 'Bokeh_serve_v2.py'])
            break

# Helper function to draw the scale bar on the canvas; TODO: Actually finish this (add saving feature)
def drawScaleBar(name):
    txt = str(1 / int(windowarr[name].zoomScale))[:3] + " μm"
    windowarr[name].canvas.create_text(62,535,fill=windowarr[name].scaleColor,font="Times 20 bold", text=txt)
    windowarr[name].canvas.create_rectangle(25, 555, 120, 560, outline=windowarr[name].scaleColor, fill=windowarr[name].scaleColor)

# Function to change color of the scale
def scaleColor(name):
    color = tkinter.colorchooser.askcolor(title="Choose a color")

    # Loop through to find active window
    currentWindow = windowarr[name]
    while currentWindow.isActive == False and currentWindow.nextMaterialName != None:
        currentWindow = windowarr[currentWindow.nextMaterialName]
    
    if currentWindow.isActive == False:
        while currentWindow.isActive == False and currentWindow.previousMaterialName != None:
            currentWindow = windowarr[currentWindow.previousMaterialName]

    currentWindow.scaleColor = color[-1]
    updateContrast(windowarr[currentWindow.name].contrast, currentWindow.name)

# Helper function to find isActive for slider change; value is new value of slider and name is the name of the material
def helperEditSlider(value, name, sliderType):
    # Loop through to find active window
    currentWindow = windowarr[name]
    while currentWindow.isActive == False and currentWindow.nextMaterialName != None:
        currentWindow = windowarr[currentWindow.nextMaterialName]
    
    if currentWindow.isActive == False:
        while currentWindow.isActive == False and currentWindow.previousMaterialName != None:
            currentWindow = windowarr[currentWindow.previousMaterialName]

    if sliderType == "gamma":
        updateGamma(value, currentWindow.name)
    elif sliderType == "contrast":
        updateContrast(value, currentWindow.name)
    elif sliderType == "brightness":
        updateBrightness(value, currentWindow.name)

# Updates the contrast in each material window; value is an integer, window is a string of the name of the window
def updateContrast(value, window):
    percentage = float(int(value)) / float(100)

    alpha = (float(2) * percentage) + float(1) # Contrast control (1.0-3.0)
    windowarr[window].contrast = value
    adjusted = cv2.convertScaleAbs(windowarr[window].imageArr, alpha=alpha, beta=float(int(windowarr[window].brightness))) # Outputs an image array
    new_mat_img = ImageTk.PhotoImage(Image.fromarray(adjusted).resize((int(595 * windowarr[window].zoomScale), int(595 * windowarr[window].zoomScale)), Image.ANTIALIAS))

    windowarr[window].TkImage = new_mat_img

    currentWindow = windowarr[window]
    while currentWindow.parent != currentWindow.name and currentWindow.previousMaterialName != None:
        currentWindow = windowarr[currentWindow.previousMaterialName]
    if currentWindow.parent != currentWindow.name:
        while currentWindow.parent != currentWindow.name and currentWindow.nextMaterialName != None:
            currentWindow = windowarr[currentWindow.nextMaterialName]
    currentWindow.canvas.delete("all")
    currentWindow.canvas.create_image(windowarr[window].position[0], windowarr[window].position[1], image=windowarr[window].TkImage, anchor=NW)
    for i in range(len(windowarr[window].lineArr)):
        currentWindow.canvas.create_line(windowarr[window].lineArr[i][0], windowarr[window].lineArr[i][1], windowarr[window].lineArr[i][2], windowarr[window].lineArr[i][3], width=5, fill='red', capstyle=ROUND, smooth=TRUE, splinesteps=36)
    drawScaleBar(window)

    windowarr[window].madeChangeBeforeSaving = True
    projectTitle.config(text=("*" + projectName))

# Updates the brightness in each material window; value is an integer, window is a string of the name of the window
def updateBrightness(value, window):
    beta = float(int(value))

    percentage = float(int(windowarr[window].contrast)) / float(100)
    alpha = (float(2) * percentage) + float(1) # Contrast control (1.0-3.0)

    windowarr[window].brightness = value
    adjusted = cv2.convertScaleAbs(windowarr[window].imageArr, alpha=alpha, beta=beta)
    new_mat_img = ImageTk.PhotoImage(Image.fromarray(adjusted).resize((int(595 * windowarr[window].zoomScale), int(595 * windowarr[window].zoomScale)), Image.ANTIALIAS))

    windowarr[window].TkImage = new_mat_img

    currentWindow = windowarr[window]
    while currentWindow.parent != currentWindow.name and currentWindow.previousMaterialName != None:
        currentWindow = windowarr[currentWindow.previousMaterialName]
    if currentWindow.parent != currentWindow.name:
        while currentWindow.parent != currentWindow.name and currentWindow.nextMaterialName != None:
            currentWindow = windowarr[currentWindow.nextMaterialName]
    currentWindow.canvas.delete("all")
    currentWindow.canvas.create_image(windowarr[window].position[0], windowarr[window].position[1], image=windowarr[window].TkImage, anchor=NW)
    for i in range(len(windowarr[window].lineArr)):
        currentWindow.canvas.create_line(windowarr[window].lineArr[i][0], windowarr[window].lineArr[i][1], windowarr[window].lineArr[i][2], windowarr[window].lineArr[i][3], width=5, fill='red', capstyle=ROUND, smooth=TRUE, splinesteps=36)
    drawScaleBar(window)

    windowarr[window].madeChangeBeforeSaving = True
    projectTitle.config(text=("*" + projectName))

# Updates the brightness in each material window; value is an integer, window is a string of the name of the window
def updateGamma(value, window):
    if value == 0:
        value = 1
    gamma = 1.0 / float(int(value))
    windowarr[window].gamma = value
    table = np.array([((i / 255.0) ** gamma) * 255
		for i in np.arange(0, 256)]).astype("uint8")
    
    adjusted = cv2.LUT(windowarr[window].imageArr.astype("uint8"), table)
    new_mat_img = ImageTk.PhotoImage(Image.fromarray(adjusted).resize((int(595 * windowarr[window].zoomScale), int(595 * windowarr[window].zoomScale)), Image.ANTIALIAS))

    windowarr[window].TkImage = new_mat_img

    currentWindow = windowarr[window]
    while currentWindow.parent != currentWindow.name and currentWindow.previousMaterialName != None:
        currentWindow = windowarr[currentWindow.previousMaterialName]
    if currentWindow.parent != currentWindow.name:
        while currentWindow.parent != currentWindow.name and currentWindow.nextMaterialName != None:
            currentWindow = windowarr[currentWindow.nextMaterialName]
    currentWindow.canvas.delete("all")
    currentWindow.canvas.create_image(windowarr[window].position[0], windowarr[window].position[1], image=windowarr[window].TkImage, anchor=NW)
    for i in range(len(windowarr[window].lineArr)):
        currentWindow.canvas.create_line(windowarr[window].lineArr[i][0], windowarr[window].lineArr[i][1], windowarr[window].lineArr[i][2], windowarr[window].lineArr[i][3], width=5, fill='red', capstyle=ROUND, smooth=TRUE, splinesteps=36)

    drawScaleBar(window)
    windowarr[window].madeChangeBeforeSaving = True
    projectTitle.config(text=("*" + projectName))

# Called before root window quits
def quit():
    global madeActionBeforeLastSave, bokehProcess

    for i in bokehProcess.keys():
        bokehProcess[i].terminate()

    for mat in windowarr.keys():
        if windowarr[mat].madeChangeBeforeSaving == True:
            madeActionBeforeLastSave = True

    # quit dialog check
    if madeActionBeforeLastSave:
        if tkinter.messagebox.askokcancel("Quit", "You have unsaved work, do you still wish to quit?"):
            shutil.rmtree('./temp', ignore_errors=True) # This removes the temp file
            root.quit()
        else:
            return
    else:
        shutil.rmtree('./temp', ignore_errors=True) # This removes the temp file, just in case it still exists
        root.quit()

# Called before each material window quits
def matQuit(name, removeDialog=False):
    # Find the first material in the linked list
    currentWindow = windowarr[name]
    while currentWindow.previousMaterialName != None:
        currentWindow = windowarr[currentWindow.previousMaterialName]
    
    hasMadeChangesBeforeSaving = False
    while currentWindow.nextMaterialName != None:
        if currentWindow.madeChangeBeforeSaving == True:
            hasMadeChangesBeforeSaving = True
            break
        currentWindow = windowarr[currentWindow.nextMaterialName]
    if hasMadeChangesBeforeSaving == False and currentWindow.madeChangeBeforeSaving == True:
        hasMadeChangesBeforeSaving = True

    if hasMadeChangesBeforeSaving and removeDialog == False and tkinter.messagebox.askokcancel("Quit", "You didn't save this material, do you still wish to quit?", parent=windowarr.get(name).windowInstance):
        # Find the current active material in the linkedlist instance
        currentWindow = windowarr[name]
        while currentWindow.isActive == False and currentWindow.nextMaterialName != None:
            currentWindow = windowarr[currentWindow.nextMaterialName]
        if currentWindow.isActive == False:
            while currentWindow.isActive == False and currentWindow.previousMaterialName != None:
                currentWindow = windowarr[currentWindow.previousMaterialName]
        updateWindowMenu(currentWindow.name)

        # Destroy the window instance
        windowarr.get(name).windowInstance.destroy()

        # Find the first material in the linked list
        currentWindow = windowarr[name]
        while currentWindow.previousMaterialName != None:
            currentWindow = windowarr[currentWindow.previousMaterialName]

        # Remove all materials in the linked list
        nextWindow = None
        while currentWindow.nextMaterialName != None:
            nextWindow = windowarr[currentWindow.nextMaterialName]
            windowarr.pop(currentWindow.name, None)
            currentWindow = nextWindow

        # Lastly, remove the single node, currentWindow
        windowarr.pop(currentWindow.name, None)
    elif removeDialog:
        # Find the current active material in the linkedlist instance
        currentWindow = windowarr[name]
        while currentWindow.isActive == False and currentWindow.nextMaterialName != None:
            currentWindow = windowarr[currentWindow.nextMaterialName]
        if currentWindow.isActive == False:
            while currentWindow.isActive == False and currentWindow.previousMaterialName != None:
                currentWindow = windowarr[currentWindow.previousMaterialName]
        updateWindowMenu(currentWindow.name)

        # Destroy the window instance
        windowarr.get(name).windowInstance.destroy()

        # Find the first material in the linked list
        currentWindow = windowarr[name]
        while currentWindow.previousMaterialName != None:
            currentWindow = windowarr[currentWindow.previousMaterialName]

        # Remove all materials in the linked list
        nextWindow = None
        while currentWindow.nextMaterialName != None:
            nextWindow = windowarr[currentWindow.nextMaterialName]
            windowarr.pop(currentWindow.name, None)
            currentWindow = nextWindow

        # Lastly, remove the single node, currentWindow
        windowarr.pop(currentWindow.name, None)

# Under the Window menu tab, either add or remove a window. Variable name is a string that is the window name
def updateWindowMenu(name):
    if name in windowarr:
        if windowarr[name].isActive:
            windowmenu.delete(name)
        else:
            windowmenu.add_command(label=name, command=lambda: bringWindowToFront(name))
    else:
        windowmenu.add_command(label=name, command=lambda: bringWindowToFront(name))

# Helper function for updateWindowMenu (above)
def bringWindowToFront(name):
    windowarr.get(name).windowInstance.focus_force() 
    windowarr.get(name).windowInstance.lift()

# Switch window options to next window; name is the window name
def switchNextWindow(name):
    # Loop through to find active window
    currentWindow = windowarr[name]
    while currentWindow.isActive == False and currentWindow.nextMaterialName != None:
        currentWindow = windowarr[currentWindow.nextMaterialName]
    
    if currentWindow.isActive == False:
        while currentWindow.isActive == False and currentWindow.previousMaterialName != None:
            currentWindow = windowarr[currentWindow.previousMaterialName]

    # Check if nextMaterialName exists
    if currentWindow.nextMaterialName == None:
        return

    updateWindowMenu(currentWindow.name)
    updateWindowMenu(currentWindow.nextMaterialName)

    currentWindow.isActive = False
    windowarr[currentWindow.nextMaterialName].isActive = True
    
    windowarr[name].windowInstance.title(currentWindow.nextMaterialName)
    updateContrast(windowarr[currentWindow.nextMaterialName].contrast, currentWindow.nextMaterialName)

# Switch window options to previous window; name is the window name
def switchPreviousWindow(name):
    # Loop through to find active window
    currentWindow = windowarr[name]
    while currentWindow.isActive == False and currentWindow.nextMaterialName != None:
        currentWindow = windowarr[currentWindow.nextMaterialName]
    
    if currentWindow.isActive == False:
        while currentWindow.isActive == False and currentWindow.previousMaterialName != None:
            currentWindow = windowarr[currentWindow.previousMaterialName]

    # Check if previousMaterialName exists
    if currentWindow.previousMaterialName == None:
        return

    updateWindowMenu(currentWindow.name)
    updateWindowMenu(currentWindow.previousMaterialName)

    currentWindow.isActive = False
    windowarr[currentWindow.previousMaterialName].isActive = True
    
    windowarr[name].windowInstance.title(currentWindow.previousMaterialName)
    updateContrast(windowarr[currentWindow.previousMaterialName].contrast, currentWindow.previousMaterialName)

# create text function; TODO: actually implement this
def createText(name):
    todo("text")

# This is the helper function for tools
def changeTool(tool, name):
    if tool == "Move":
        windowarr[name].tool = "Move"
    elif tool == "Zoom":
        windowarr[name].tool = "Zoom"
    elif tool == "Draw":
        windowarr[name].tool = "Draw"

# This is the helper function to help choose what function to execute when clicking on the canvas; name is window name
def clickedCanvas(event, name):
    # Loop through to find active window
    currentWindow = windowarr[name]
    while currentWindow.isActive == False and currentWindow.nextMaterialName != None:
        currentWindow = windowarr[currentWindow.nextMaterialName]
    
    if currentWindow.isActive == False:
        while currentWindow.isActive == False and currentWindow.previousMaterialName != None:
            currentWindow = windowarr[currentWindow.previousMaterialName]

    if currentWindow.tool == "Zoom":
        zoom(event, currentWindow.name)
    elif currentWindow.tool == "Move":
        todo()
    elif currentWindow.tool == "Draw":
        paint(event, currentWindow.name)
    elif currentWindow.tool == "ZoomIn":
        todo()
    elif currentWindow.tool == "ZoomOut":
        todo()

# This is the helper function to reset the cursor position after clicking on the canvas
def stopClickedCanvas(event, name):
    global old_mouse_x, old_mouse_y

    if windowarr[name].tool == "Zoom" and event != None:
        # Remove the rectangle
        for i in range(len(zoomArr)):
            if zoomArr[i] != None:
                windowarr[name].canvas.delete(zoomArr[i])
                zoomArr[i] = None
        
        # Loop through to find active window
        currentWindow = windowarr[name]
        while currentWindow.isActive == False and currentWindow.nextMaterialName != None:
            currentWindow = windowarr[currentWindow.nextMaterialName]
        
        if currentWindow.isActive == False:
            while currentWindow.isActive == False and currentWindow.previousMaterialName != None:
                currentWindow = windowarr[currentWindow.previousMaterialName]
        
        # Find width and height of new crop zone
        width = (event.x - old_mouse_x) if (event.x - old_mouse_x) > 0 else (old_mouse_x - event.x)
        height = (old_mouse_y - event.y) if (old_mouse_y - event.y) > 0 else (event.y - old_mouse_y)

        # Scale
        scale = float(595) / float(width)

        # Set the position
        currentWindow.position = [0 - old_mouse_x * scale, 0 - old_mouse_y * scale]
        currentWindow.zoomScale = scale

        # Redraw canvas
        updateContrast(currentWindow.contrast, currentWindow.name)

    old_mouse_x = None
    old_mouse_y = None

# This is the function to zoom a material
def zoom(event, name):
    global old_mouse_x, old_mouse_y, zoomArr

    for i in range(len(zoomArr)):
        if zoomArr[i] != None:
            windowarr[name].canvas.delete(zoomArr[i])
            zoomArr[i] = None
    
    if old_mouse_x and old_mouse_y:
        zoomArr[0] = windowarr[name].canvas.create_line(old_mouse_x, old_mouse_y, event.x, old_mouse_y, width=2, fill='yellow', capstyle=ROUND, smooth=TRUE, splinesteps=36)
        zoomArr[1] = windowarr[name].canvas.create_line(event.x, old_mouse_y, event.x, event.y, width=2, fill='yellow', capstyle=ROUND, smooth=TRUE, splinesteps=36)
        zoomArr[2] = windowarr[name].canvas.create_line(old_mouse_x, old_mouse_y, old_mouse_x, event.y, width=2, fill='yellow', capstyle=ROUND, smooth=TRUE, splinesteps=36)
        zoomArr[3] = windowarr[name].canvas.create_line(old_mouse_x, event.y, event.x, event.y, width=2, fill='yellow', capstyle=ROUND, smooth=TRUE, splinesteps=36)
    else:
        old_mouse_x = event.x
        old_mouse_y = event.y
    
    windowarr[name].madeChangeBeforeSaving = True
    projectTitle.config(text=("*" + projectName))

# This is the function to draw on the canvas
def paint(event, name):
    global old_mouse_x, old_mouse_y

    if old_mouse_x and old_mouse_y:
        windowarr[name].canvas.create_line(old_mouse_x, old_mouse_y, event.x, event.y, width=5, fill='red', capstyle=ROUND, smooth=TRUE, splinesteps=36)
        windowarr[name].lineArr.append([old_mouse_x, old_mouse_y, event.x, event.y])

    old_mouse_x = event.x
    old_mouse_y = event.y
    windowarr[name].madeChangeBeforeSaving = True
    projectTitle.config(text=("*" + projectName))

# New project
def newProject():
    global madeActionBeforeLastSave
    for mat in windowarr.keys():
        if windowarr[mat].madeChangeBeforeSaving == True:
            madeActionBeforeLastSave = True

    # quit dialog check
    if madeActionBeforeLastSave:
        if not tkinter.messagebox.askokcancel("New project", "You have unsaved work. If you create a new project, you will lose it. Do you still wish to create a new project?"):
            return

    fileDir = tkinter.filedialog.asksaveasfilename(initialdir="/", title="Save new project as", defaultextension=".grainbound", filetypes=(("grainbound files", "*.grainbound"), ("all files", "*.*")))
    if len(fileDir) == 0:
        return
    fileNameArr = fileDir.split('/')
    fileName = fileNameArr[len(fileNameArr)-1]
    fileName = (fileName.split('.'))[0]
    projectTitle.config(text=fileName)

    #add readme to Grainbound file

    global projectDir
    projectDir = fileDir
    global projectName
    projectName = fileName

    # Remove all currently opened projects from the window dictionary
    for key, value in list(windowarr.items()):
        if value.isActive == True:
            matQuit(key, removeDialog=True)

    # Create the new file
    jsonData = {}
    jsonData['name'] = fileName
    jsonData['contributors'] = "Jack Kellerk, Chris Marvel, Anna Thomas"
    jsonData['materials'] = []
    newFile = open(fileDir, "w")
    json.dump(jsonData, newFile)
    newFile.close()

# Save all materials in the project
def save():
    global projectName
    global projectDir
    global madeActionBeforeLastSave

    if projectDir == "./temp/":
        saveAs()
    else:
        jsonData = {}
        jsonData['name'] = projectName
        jsonData['contributors'] = "Jack Kellerk, Chris Marvel"
        jsonData['materials'] = []

        # For each material, add it to the materials key for jsonData dictionary
        for key, value in windowarr.items():
            jsonData['materials'].append({
                'name': value.name,
                'tool': 'Imaging',
                'brightness': value.brightness,
                'contrast': value.contrast,
                'gamma': value.gamma,
                'imageArr': value.imageArr.tolist(),
                'previousMaterialName': value.previousMaterialName,
                'nextMaterialName': value.nextMaterialName,
                'isActive': value.isActive,
                'windowPosition': str(value.windowInstance.winfo_x()) + "," + str(value.windowInstance.winfo_y()),
                'lineArr': value.lineArr
            })

            if value.madeChangeBeforeSaving == True:
                value.madeChangeBeforeSaving = False

        newFile = open(projectDir, "w")
        json.dump(jsonData, newFile)
        newFile.close()

        for key in windowarr.keys():
            windowarr[key].madeChangeBeforeSaving = False
        madeActionBeforeLastSave = False

        projectTitle.config(text=("*" + projectName))

# Save the project
def saveAs():
    global madeActionBeforeLastSave

    fileDir = tkinter.filedialog.asksaveasfilename(initialdir="/", title="Save project as", defaultextension=".grainbound", filetypes=(("grainbound files", "*.grainbound"), ("all files", "*.*")))
    if len(fileDir) == 0:
        return
    fileNameArr = fileDir.split('/')
    fileName = fileNameArr[len(fileNameArr)-1]
    fileName = (fileName.split("."))[0]
    projectTitle.config(text=fileName)
    jsonData = {}
    jsonData['name'] = fileName
    jsonData['contributors'] = "Jack Kellerk, Chris Marvel"
    jsonData['materials'] = []

    # For each material, add it to the materials key for jsonData dictionary
    for key, value in windowarr.items():
        jsonData['materials'].append({
            'name': value.name,
            'tool': 'Imaging',
            'brightness': value.brightness,
            'contrast': value.contrast,
            'gamma': value.gamma,
            'imageArr': value.imageArr.tolist(),
            'previousMaterialName': value.previousMaterialName,
            'nextMaterialName': value.nextMaterialName,
            'isActive': value.isActive,
            'windowPosition': str(value.windowInstance.winfo_x()) + "," + str(value.windowInstance.winfo_y()),
            'lineArr': value.lineArr
        })
        
        if value.madeChangeBeforeSaving == True:
            value.madeChangeBeforeSaving = False
    
    if madeActionBeforeLastSave == True:
        madeActionBeforeLastSave = False

    newFile = open(fileDir, "w")
    json.dump(jsonData, newFile)
    newFile.close()

    global projectDir
    projectDir = fileDir
    global projectName
    projectName = fileName

# opens a project
def openProject():
    fileDir = tkinter.filedialog.askopenfilename(initialdir="/", title="Select a project", filetypes=(("grainbound files", "*.grainbound"), ("all files", "*.*")))
    if len(fileDir) == 0:
        return
    openFile = open(fileDir, "r")
    jsonData = json.loads(openFile.read())

    # Remove all currently opened projects from the window dictionary
    for key, value in list(windowarr.items()):
        if value.isActive == True:
            matQuit(key, removeDialog=True)

    # Replace project title with project name
    global projectName
    projectName = (jsonData['name'].split('.'))[0]
    global projectDir
    projectDir = fileDir
    projectTitle.config(text=projectName)

    # TODO: Under the About section, edit contributors

    # Open each project as a windowObj
    for mat in jsonData['materials']:
        if mat['isActive'] == True:
            window = Toplevel()
            window.title(mat['name'])
            window.resizable(0,0)
            windowPos = mat['windowPosition'].split(',')
            window.geometry("665x665+" + windowPos[0] + "+" + windowPos[1])
            updateWindowMenu(mat['name'])

            mat_img_arr = np.array(mat['imageArr']) if (mat['name'])[-1] == '3' else np.array(mat['imageArr'], dtype=np.uint8)
            mat_img = ImageTk.PhotoImage(Image.fromarray(mat_img_arr).resize((595,595), Image.ANTIALIAS))
            windowObj = materialWindow(mat['name'], mat['name'], window, mat_img, [0, 0], 1, lineArr=mat['lineArr'], imageArr=mat_img_arr, previousMaterialName=mat['previousMaterialName'], nextMaterialName=mat['nextMaterialName'], isActive=True, madeChangeBeforeSaving=False)
            windowarr[mat['name']] = windowObj

            canvas = Canvas(window, width=595, height=595, bd=0, highlightthickness=0)
            canvas.pack(side="top", fill="both", expand="yes")
            canvas.place(x=66, y=0, anchor='nw')
            canvas.create_image(0, 0, image=windowarr[mat['name']].TkImage, anchor=NW)
            canvas.bind('<B1-Motion>', lambda x, name=windowarr[mat['name']].name: clickedCanvas(x, name))
            canvas.bind('<ButtonRelease-1>', lambda x, name=windowarr[mat['name']].name: stopClickedCanvas(x, name))

            windowarr[mat['name']].windowInstance = window
            windowarr[mat['name']].canvas = canvas

            # Add widgets
            window.protocol("WM_DELETE_WINDOW", lambda name=windowarr[mat['name']].name: matQuit(name))
            moveButton = Button(window, width=4, height=3, text="Move", command=lambda name=windowarr[mat['name']].name: changeTool("Move", name))
            moveButton.pack()
            moveButton.place(x=2, y=2)

            zoomButton = Button(window, width=4, height=3, text="Zoom", command=lambda name=windowarr[mat['name']].name: changeTool("Zoom", name))
            zoomButton.pack()
            zoomButton.place(x=2, y=72)
            
            annotateButton = Button(window, width=4, height=3, text="Draw", command=lambda name=windowarr[mat['name']].name: changeTool("Draw", name))
            annotateButton.pack()
            annotateButton.place(x=2, y=142)

            metaDataButton = Button(window, width=4, height=3, text="Meta\nData", command=todo)
            metaDataButton.pack()
            metaDataButton.place(x=2, y=212)

            scaleColorButton = Button(window, width=4, height=3, text="Scale\nColor", command=lambda name=windowarr[mat['name']].name: scaleColor(name))
            scaleColorButton.pack()
            scaleColorButton.place(x=2, y=282)

            textButton = Button(window, width=4, height=3, text="Create\nText", command=lambda name=windowarr[mat['name']].name: createText(name))
            textButton.pack()
            textButton.place(x=2, y=352)

            changeMaterialLabel = Label(window, text="Change\nMaterial")
            changeMaterialLabel.pack()
            changeMaterialLabel.place(x=2, y=555)

            nextMaterialButton = Button(window, width=4, height=3, text=">", command=lambda name=windowarr[mat['name']].name: switchNextWindow(name))
            nextMaterialButton.pack()
            nextMaterialButton.place(x=60, y=600)

            previousMaterialButton = Button(window, width=4, height=3, text="<", command=lambda name=windowarr[mat['name']].name: switchPreviousWindow(name))
            previousMaterialButton.pack()
            previousMaterialButton.place(x=2, y=600)

            contrastScale = Scale(window, from_=-100, to=100, orient=HORIZONTAL, showvalue=50, label='Contrast', command=lambda x, name=windowarr[mat['name']].name: helperEditSlider(x, name, "contrast"))
            contrastScale.set(0)
            contrastScale.pack()
            contrastScale.place(x=170, y=600)

            brightnessScale = Scale(window, from_=-100, to=100, showvalue=50, orient=HORIZONTAL, label='Brightness', command=lambda x, name=windowarr[mat['name']].name: helperEditSlider(x, name, "brightness"))
            brightnessScale.set(0)
            brightnessScale.pack()
            brightnessScale.place(x=350, y=600)

            gammaScale = Scale(window, from_=-100, to=100, orient=HORIZONTAL, showvalue=50, label='Gamma', command=lambda x, name=windowarr[mat['name']].name: helperEditSlider(x, name, "gamma"))
            gammaScale.set(0)
            gammaScale.pack()
            gammaScale.place(x=530, y=600)

            # Set slider values
            gammaScale.set(float(mat['gamma']))
            contrastScale.set(float(mat['contrast']))
            brightnessScale.set(float(mat['brightness']))

            windowarr[mat['name']].madeChangeBeforeSaving = False
        else:
            mat_img_arr = np.array(mat['imageArr']) if (mat['name'])[-1] == '3' else np.array(mat['imageArr'], dtype=np.uint8)
            mat_img = ImageTk.PhotoImage(Image.fromarray(mat_img_arr).resize((595,595), Image.ANTIALIAS))
            windowObj = materialWindow(mat['name'], "", None, mat_img, [0, 0], 1, lineArr=mat['lineArr'], imageArr=mat_img_arr, brightness=mat['brightness'], contrast=mat['contrast'], gamma=mat['gamma'], nextMaterialName=mat['nextMaterialName'], previousMaterialName=mat['previousMaterialName'], tool="Imaging", isActive=False, madeChangeBeforeSaving=False)
            windowarr[mat['name']] = windowObj
            windowarr[mat['name']].madeChangeBeforeSaving = False

    # Assign parent and window instance to each windowObj
    for key in windowarr.keys():
        if windowarr[key].isActive == True:
            parent = key
            windowInstance = windowarr[key].windowInstance

            # Loop through to the end of the linked list
            currentWindow = windowarr[key]
            while currentWindow.nextMaterialName != None:
                currentWindow = windowarr[currentWindow.nextMaterialName]
                currentWindow.windowInstance = windowInstance
                currentWindow.parent = parent
            if currentWindow != windowarr[key]:
                currentWindow.parent = parent
                currentWindow.windowInstance = windowInstance

            # Loop through to the beginning of the linked list
            currentWindow = windowarr[key]
            while currentWindow.previousMaterialName != None:
                currentWindow = windowarr[currentWindow.previousMaterialName]
                currentWindow.windowInstance = windowInstance
                currentWindow.parent = parent
            if currentWindow != windowarr[key]:
                currentWindow.parent = parent
                currentWindow.windowInstance = windowInstance

# Create dm3 file window
def openNewMaterial():
    # File browser and creating window
    fileDir = tkinter.filedialog.askopenfilenames(initialdir="/", title="Select a material", filetypes=(("dm3 files", "*.dm3"), ("tif files", "*.tif"), ("tiff files", "*.tiff"), ("all files", "*.*")))
    if len(fileDir) == 0:
        return
    fileNameArr = fileDir[0].split('/')
    fileName = fileNameArr[len(fileNameArr)-1]
    window = Toplevel()
    window.title(fileName)
    window.resizable(0,0) #can't resize
    window.geometry("665x665+700+300")

    parentName = fileName

    # Create the dm3 image or else open up the tif image
    dm3f = dm.dmReader(fileDir[0]) if fileName[-1] == '3' else cv2.imread(fileDir[0], 0)
    if fileName[-1] == '3':
        dm3f['data'] = ((dm3f['data'] * 3) / 16000) # Transforming data
    else:
        nparr = dm3f

    # Check to see if current material is open yet; if it is, make a copy of it increasing a number at the end of the file name; if not, just save it as its file name
    if fileName in windowarr.keys():
        for x in range(100):
            if (fileName + " (copy " + str(x+1) + ")") in windowarr.keys():
                continue
            else:
                window.title(fileName + " (copy " + str(x+1) + ")")

                mat_img_arr = dm3f['data'] if fileName[-1] == '3' else nparr
                mat_img = ImageTk.PhotoImage(Image.fromarray(mat_img_arr).resize((595,595), Image.ANTIALIAS))
                windowObj = materialWindow(fileName + " (copy " + str(x+1) + ")", fileName + " (copy " + str(x+1) + ")", window, mat_img, [0,0], 1, imageArr=mat_img_arr, isActive=True) # Create window object
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

                # Add widgets
                newFileName = fileName + " (copy " + str(x+1) + ")"
                window.protocol("WM_DELETE_WINDOW", lambda name=newFileName: matQuit(name))
                parentName = newFileName
                moveButton = Button(window, width=4, height=3, text="Move", command=lambda name=newFileName: changeTool("Move", name))
                moveButton.pack()
                moveButton.place(x=2, y=2)

                zoomButton = Button(window, width=4, height=3, text="Zoom", command=lambda name=newFileName: changeTool("Zoom", name))
                zoomButton.pack()
                zoomButton.place(x=2, y=72)
                
                annotateButton = Button(window, width=4, height=3, text="Draw", command=lambda name=newFileName: changeTool("Draw", name))
                annotateButton.pack()
                annotateButton.place(x=2, y=142)

                metaDataButton = Button(window, width=4, height=3, text="Meta\nData", command=todo)
                metaDataButton.pack()
                metaDataButton.place(x=2, y=212)

                scaleColorButton = Button(window, width=4, height=3, text="Scale\nColor", command=lambda name=newFileName: scaleColor(name))
                scaleColorButton.pack()
                scaleColorButton.place(x=2, y=282)

                textButton = Button(window, width=4, height=3, text="Create\nText", command=lambda name=newFileName: createText(name))
                textButton.pack()
                textButton.place(x=2, y=352)

                changeMaterialLabel = Label(window, text="Change\nMaterial")
                changeMaterialLabel.pack()
                changeMaterialLabel.place(x=2, y=555)

                nextMaterialButton = Button(window, width=4, height=3, text=">", command=lambda: switchNextWindow(newFileName))
                nextMaterialButton.pack()
                nextMaterialButton.place(x=60, y=600)

                previousMaterialButton = Button(window, width=4, height=3, text="<", command=lambda: switchPreviousWindow(newFileName))
                previousMaterialButton.pack()
                previousMaterialButton.place(x=2, y=600)

                contrastScale = Scale(window, from_=-100, to=100, orient=HORIZONTAL, showvalue=50, label='Contrast', command=lambda x : helperEditSlider(x, newFileName, "contrast"))
                contrastScale.set(0)
                contrastScale.pack()
                contrastScale.place(x=170, y=600)

                brightnessScale = Scale(window, from_=-100, to=100, showvalue=50, orient=HORIZONTAL, label='Brightness', command=lambda x : helperEditSlider(x, newFileName, "brightness"))
                brightnessScale.set(0)
                brightnessScale.pack()
                brightnessScale.place(x=350, y=600)

                gammaScale = Scale(window, from_=-100, to=100, orient=HORIZONTAL, showvalue=50, label='Gamma', command=lambda x : helperEditSlider(x, newFileName, "gamma"))
                gammaScale.set(0)
                gammaScale.pack()
                gammaScale.place(x=530, y=600)

                # Set slider values
                gammaScale.set(float(1))
                contrastScale.set(float(1))
                brightnessScale.set(float(0))
                break
    else:
        mat_img_arr = dm3f['data'] if fileName[-1] == '3' else nparr
        mat_img = ImageTk.PhotoImage(Image.fromarray(mat_img_arr).resize((595,595), Image.ANTIALIAS))
        windowObj = materialWindow(fileName, fileName, window, mat_img, [0,0], 1, imageArr=mat_img_arr, isActive=True) # Create window object
        updateWindowMenu(fileName)
        windowarr[fileName] = windowObj
        windowarr[fileName].lineArr = []
        
        canvas = Canvas(window, width=595, height=595, bd=0, highlightthickness=0)
        canvas.pack(side="top", fill="both", expand="yes")
        canvas.place(x=66, y=0, anchor='nw')
        canvas.create_image(0, 0, image=windowarr[fileName].TkImage, anchor=NW)
        canvas.bind('<B1-Motion>', lambda x: clickedCanvas(x, fileName))
        canvas.bind('<ButtonRelease-1>', lambda x: stopClickedCanvas(x, fileName))
        
        window.protocol("WM_DELETE_WINDOW", lambda name=fileName: matQuit(name))
        windowarr[fileName].windowInstance = window
        windowarr[fileName].canvas = canvas

        # Add widgets
        moveButton = Button(window, width=4, height=3, text="Move", command=lambda: changeTool("Move", fileName))
        moveButton.pack()
        moveButton.place(x=2, y=2)

        zoomButton = Button(window, width=4, height=3, text="Zoom", command=lambda: changeTool("Zoom", fileName))
        zoomButton.pack()
        zoomButton.place(x=2, y=72)
        
        annotateButton = Button(window, width=4, height=3, text="Draw", command=lambda: changeTool("Draw", fileName))
        annotateButton.pack()
        annotateButton.place(x=2, y=142)

        metaDataButton = Button(window, width=4, height=3, text="Meta\nData", command=todo)
        metaDataButton.pack()
        metaDataButton.place(x=2, y=212)

        scaleColorButton = Button(window, width=4, height=3, text="Scale\nColor", command=lambda: scaleColor(fileName))
        scaleColorButton.pack()
        scaleColorButton.place(x=2, y=282)

        textButton = Button(window, width=4, height=3, text="Create\nText", command=lambda: createText(fileName))
        textButton.pack()
        textButton.place(x=2, y=352)

        changeMaterialLabel = Label(window, text="Change\nMaterial")
        changeMaterialLabel.pack()
        changeMaterialLabel.place(x=2, y=555)

        nextMaterialButton = Button(window, width=4, height=3, text=">", command=lambda: switchNextWindow(fileName))
        nextMaterialButton.pack()
        nextMaterialButton.place(x=60, y=600)

        previousMaterialButton = Button(window, width=4, height=3, text="<", command=lambda: switchPreviousWindow(fileName))
        previousMaterialButton.pack()
        previousMaterialButton.place(x=2, y=600)

        contrastScale = Scale(window, from_=-100, to=100, orient=HORIZONTAL, showvalue=50, label='Contrast', command=lambda x : helperEditSlider(x, fileName, "contrast"))
        contrastScale.set(0)
        contrastScale.pack()
        contrastScale.place(x=170, y=600)

        brightnessScale = Scale(window, from_=-100, to=100, showvalue=50, orient=HORIZONTAL, label='Brightness', command=lambda x : helperEditSlider(x, fileName, "brightness"))
        brightnessScale.set(0)
        brightnessScale.pack()
        brightnessScale.place(x=350, y=600)

        gammaScale = Scale(window, from_=-100, to=100, orient=HORIZONTAL, showvalue=50, label='Gamma', command=lambda x : helperEditSlider(x, fileName, "gamma"))
        gammaScale.set(0)
        gammaScale.pack()
        gammaScale.place(x=530, y=600)

        # Set slider values
        gammaScale.set(float(1))
        contrastScale.set(float(1))
        brightnessScale.set(float(0))
    
    # This is for the other files selected in the file dialog; open them not as windows, but as window objects
    for i in range(len(fileDir)):
        if i == 0:
            continue

        fileNameArrOthers = fileDir[i].split('/')
        fileNameOthers = fileNameArrOthers[len(fileNameArrOthers)-1]

        # Create the dm3 image
        dm3f = dm.dmReader(fileDir[i]) if fileDir[i][-1] == '3' else imageio.imread(fileDir[i])
        if fileDir[i][-1] == '3':
            dm3f['data'] = ((dm3f['data'] * 3) / 16000) # Transforming data
        else:
            nparr = np.array(dm3f)

        # Check to see if current material is open yet; if it is, make a copy of it increasing a number at the end of the file name; if not, just save it as its file name
        if fileNameOthers in windowarr.keys():
            for x in range(100):
                if (fileNameOthers + " (copy " + str(x+1) + ")") in windowarr.keys():
                    continue
                else:
                    mat_img_arr = dm3f['data'] if fileDir[i][-1] == '3' else nparr
                    mat_img = ImageTk.PhotoImage(Image.fromarray(mat_img_arr).resize((595,595), Image.ANTIALIAS))
                    windowObj = materialWindow(fileNameOthers + " (copy " + str(x+1) + ")", parentName, window, mat_img, [0,0], 1, imageArr=mat_img_arr) # Create window object
                    windowarr[fileNameOthers + " (copy " + str(x+1) + ")"] = windowObj
                    windowarr[fileNameOthers + " (copy " + str(x+1) + ")"].windowInstance = window
                    windowarr[fileNameOthers + " (copy " + str(x+1) + ")"].canvas = windowarr[parentName].canvas
                    windowarr[fileNameOthers + " (copy " + str(x+1) + ")"].lineArr = []
                    break
        else:
            mat_img_arr = dm3f['data'] if fileDir[i][-1] == '3' else nparr
            mat_img = ImageTk.PhotoImage(Image.fromarray(mat_img_arr).resize((595,595), Image.ANTIALIAS))
            windowObj = materialWindow(fileNameOthers, parentName, window, mat_img, [0,0], 1, imageArr=mat_img_arr) # Create window object
            windowarr[fileNameOthers] = windowObj
            windowarr[fileNameOthers].windowInstance = window
            windowarr[fileNameOthers].canvas = windowarr[parentName].canvas
            windowarr[fileNameOthers].lineArr = []
    
    # For each material before and after, connect them using previousMaterialName and nextMaterialName
    for i in range(len(fileDir)):
        fileNameArrOthers = fileDir[i].split('/')
        fileNameOthers = fileNameArrOthers[len(fileNameArrOthers)-1]
        for x in range(100):
            if (fileNameOthers + " (copy " + str(x+1) + ")") in windowarr.keys():
                continue
            elif x == 0:
                break
            else:
                fileNameOthers = (fileNameOthers + " (copy " + str(x) + ")")
                break
        if i-1 >= 0:
            fileNameArrBefore = fileDir[i-1].split('/')
            fileNameBefore = fileNameArrBefore[len(fileNameArrBefore)-1]
            for x in range(100):
                if (fileNameBefore + " (copy " + str(x+1) + ")") in windowarr.keys():
                    continue
                elif x == 0:
                    break
                else:
                    fileNameBefore = (fileNameBefore + " (copy " + str(x) + ")")
                    break
            windowarr[fileNameOthers].previousMaterialName = fileNameBefore
        if i+1 <= len(fileDir)-1:
            fileNameArrAfter = fileDir[i+1].split('/')
            fileNameAfter = fileNameArrAfter[len(fileNameArrAfter)-1]
            for x in range(100):
                if (fileNameAfter + " (copy " + str(x+1) + ")") in windowarr.keys():
                    continue
                elif x == 0:
                    break
                else:
                    fileNameAfter = (fileNameAfter + " (copy " + str(x) + ")")
                    break
            windowarr[fileNameOthers].nextMaterialName = fileNameAfter
            
    # Set this to true, so the user is prompted when attempting to close the program
    global madeActionBeforeLastSave
    madeActionBeforeLastSave = True
    projectTitle.config(text=("*" + projectName))

# <summary>
# End of custom tkinter function code
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
    window.resizable(0,0) #disables resizing
    window.geometry("1000x665+700+300")

    parentName = fileName

    # Extract the emsa spectrum data from file
    fileDateArr = []
    for i in range(2100): # potentially needs to be changed if file size varies
        fileDateArr.append([])
    isdata = False
    En = []
    Ct = []
    for r in range(3):
        En.append([])
        Ct.append([])

    for i in range(len(fileDir)):
        isdata = False
        f = open(fileDir[i], "r")
        for r in f:
            if "#DATE" in r:
                fileDateArr.append(r.replace('#DATE        : ',''))
            elif "#SPECTRUM" in r:
                isdata = True
            elif isdata and "#ENDOFDATA" not in r:
                txt = r.strip()
                txt = txt.split(',')
                En[i].append(float(txt[0]))
                Ct[i].append(float(txt[1]))
    
    # Check to see if current material is open yet; if it is, make a copy of it increasing a number at the end of the file name; if not, just save it as its file name
    if fileName in windowarr.keys():
        for x in range(len(windowarr)):
            if (fileName + " (copy " + str(x+1) + ")") in windowarr.keys():
                continue
            else:
                window.title(fileName + " (copy " + str(x+1) + ")")
                windowObj = edsWindow(fileName + " (copy " + str(x+1) + ")", fileName + " (copy " + str(x+1) + ")", windowInstance=window, position=[0,0], zoomScale=1, energymain=En[0], energyleft=En[1], energyright=En[2], countmain=Ct[0], countleft=Ct[1], countright=Ct[2], isActive=True) # Create window object
                updateWindowMenu(fileName + " (copy " + str(x+1) + ")")
                windowarr[fileName + " (copy " + str(x+1) + ")"] = windowObj
                
                canvas = Canvas(window, width=595, height=595, bd=0, highlightthickness=0)
                canvas.pack(side="top", fill="both", expand="yes")
                canvas.place(x=500, y=0, anchor='nw')
                canvas.bind('<B1-Motion>', lambda x: clickedCanvas(x, fileName))
                canvas.bind('<ButtonRelease-1>', lambda x: stopClickedCanvas(x, fileName))

                windowarr[fileName + " (copy " + str(x+1) + ")"].windowInstance = window
                windowarr[fileName + " (copy " + str(x+1) + ")"].canvas = canvas

                draw_figure(window, canvas, energy=En, count=Ct)     

                window.protocol("WM_DELETE_WINDOW", lambda name=fileName: matQuit(name))
                #eds quit function
                windowarr[fileName].windowInstance = window
                windowarr[fileName].canvas = canvas

                # checkbox to compute averaged left&right data (En[1], En[2])
                #var1 = tkinter.IntVar()
                #c1 = tkinter.Checkbutton(window, text='Python', variable=var1, onvalue=1, offvalue=0, command=compute_ave(window, canvas, En, Ct))
                #c1.pack()

    else:
        
        windowObj = edsWindow(fileName, fileName, windowInstance=window, position=[0,0], zoomScale=1, energymain=En[0], energyleft=En[1], energyright=En[2], countmain=Ct[0], countleft=Ct[1], countright=Ct[2], isActive=True) # Create window object
        updateWindowMenu(fileName)
        windowarr[fileName] = windowObj
        
        canvas = Canvas(window, width=595, height=595, bd=0, highlightthickness=0)
        canvas.pack(side="top", fill="both", expand="yes")
        canvas.place(x=500, y=0, anchor='nw')
        canvas.bind('<B1-Motion>', lambda x: clickedCanvas(x, fileName))
        canvas.bind('<ButtonRelease-1>', lambda x: stopClickedCanvas(x, fileName))
        
        draw_figure(window, canvas, energy=En, count=Ct)  

        # need to generalize this
        initial_x = 0, 22
        initial_y = 0, 180000

        # textboxes for users to input graph bounds. working on adding them to nav toolbar instead.
        '''axbox = plt.axes([0.1, 0.05, 0.8, 0.075])
        xlow_box = TextBox(axbox, 'x: from', initial=initial_x[0])
        xlow_box.on_submit(submit_xlow)  
        xhigh_box = TextBox(axbox, 'to', initial=initial_x[1])
        xhigh_box.on_submit(submit_xhigh)  
        ylow_box = TextBox(axbox, 'y: from', initial=initial_y[0])
        ylow_box.on_submit(submit_ylow)  
        yhigh_box = TextBox(axbox, 'to', initial=initial_[1]) 
        yhigh_box.on_submit(submit_yhigh)  '''

        window.protocol("WM_DELETE_WINDOW", lambda name=fileName: matQuit(name))
        #eds quit function
        windowarr[fileName].windowInstance = window
        windowarr[fileName].canvas = canvas

        # averaging graph checkbox
        #var1 = tkinter.IntVar()
        #c1 = tkinter.Checkbutton(canvas, text='Python', variable=var1, onvalue=1, offvalue=0, command=compute_ave(window, canvas, En, Ct))
        #c1.pack()

    # This is for the other files selected in the file dialog; open them not as windows, but as window objects
    for i in range(len(fileDir)):
        if i == 0:
            continue

        fileNameArrOthers = fileDir[i].split('/')
        fileNameOthers = fileNameArrOthers[len(fileNameArrOthers)-1]

        # do i need to draw figures here?

        # Check to see if current material is open yet; if it is, make a copy of it increasing a number at the end of the file name; if not, just save it as its file name
        if fileNameOthers in windowarr.keys():
            for x in range(100):
                if (fileNameOthers + " (copy " + str(x+1) + ")") in windowarr.keys():
                    continue
                else:
                    windowObj = edsWindow(fileName, fileName, Figure=fig, windowInstance=window, position=[0,0], zoomScale=1, energymain=En, countmain=Ct, isActive=True) # Create window object
                    windowarr[fileNameOthers + " (copy " + str(x+1) + ")"].windowInstance = window
                    windowarr[fileNameOthers + " (copy " + str(x+1) + ")"].canvas = windowarr[parentName].canvas
                    break
        else:
            windowObj = edsWindow(fileNameOthers, parentName, windowInstance=window, position=[0,0], zoomScale=1) # Create window object
            windowarr[fileNameOthers] = windowObj
            windowarr[fileNameOthers].windowInstance = window
            windowarr[fileNameOthers].canvas = windowarr[parentName].canvas
    
    # Set this to true, so the user is prompted when attempting to close the program
    global madeActionBeforeLastSave
    madeActionBeforeLastSave = True
    projectTitle.config(text=("*" + projectName))

# <summary>
# End of custom tkinter function code
# </summary>

# Draw a matplotlib figure onto a Tk canvas with original dimensions
def draw_figure(window, canvas, energy, count):
    fig = plt.figure()
    ax = fig.add_subplot(1,1,1)
    ax.set_xlim([0,22])
    ax.set_ylim([0,180000])
    p0, = ax.plot(energy[0], count[1], color='b', linewidth=1)
    p1, = ax.plot(energy[0], count[2], color='g', linewidth=1)
    p2, = ax.vlines(energy[0], ymin=[0], ymax=count[0])
    for v in range(1,len(count[0])-1):
        if count[0][v]-count[0][v-1]>50 and count[0][v]-count[0][v+1]>50:
            ax.annotate('(%s,%s)' % (energy[0][v],count[0][v]), xy=(energy[0][v],count[0][v]), textcoords='data')
    #ax.legend([p0, p1, p2], ["left", "right", "main"])
    ax.grid(True, linestyle='-.')
    ax.xaxis.set_minor_locator(AutoMinorLocator())
    ax.tick_params(which='minor', length=4)
    plt.xlabel('energy (keV)')
    plt.ylabel('intensity counts')
    plt.title('EDS Spectrum')

    canvas = FigureCanvasTkAgg(fig, master=window)  # A tk.DrawingArea.
    canvas.draw()

    # adds navigation toolbar to eds window
    frame1 = tkinter.Frame(window)
    toolbar = NavigationToolbar2Tk(canvas, frame1)
    frame1.pack(side=tkinter.TOP, fill=tkinter.X)
    toolbar.update()
    canvas.get_tk_widget().pack(side=tkinter.TOP, fill=tkinter.BOTH, expand=1)
    toolbar.pack(side=TOP, fill=X)


def compute_ave(window, canvas, energy, count):
    aves = []
    for i in range(len(count[0])):
        temp = (count[0][i] + count[1][i] + count[2][i])/3
        aves.append(temp)

    draw_figure(window, canvas, energy, aves)

# function for averaging checkbox / changing graph bounds
def submit(text):
    ydata = eval(text)
    l.set_ydata(ydata)
    ax.set_ylim(np.min(ydata), np.max(ydata))
    draw_figure()


# <summary>
# Tkinter layout code
# </summary>
root = Tk()
root.title('GrainBound')
root.geometry("1280x800")
root.configure(background='#F0F0F0')
root.protocol("WM_DELETE_WINDOW", quit)

# Creating the menubar
menubar = Menu(root)

filemenu = Menu(menubar, tearoff=0)
filemenu.add_command(label="New project", command=newProject)
filemenu.add_command(label="Open project...", command=openProject)
filemenu.add_command(label="Save project", command=save)
filemenu.add_command(label="Save project as...", command=saveAs)
filemenu.add_separator()
filemenu.add_command(label="Open material(s)", command=openNewMaterial)
filemenu.add_command(label="Open EDS material(s)", command=openNewEDS)
filemenu.add_command(label="Save materials", command=save)
filemenu.add_command(label="Save material as...", command=todo)
filemenu.add_separator()
filemenu.add_command(label="Exit", command=quit)

windowmenu = Menu(menubar, tearoff=0)

helpmenu = Menu(menubar, tearoff=0)
helpmenu.add_command(label="About", command=todo)
helpmenu.add_command(label="Contact us", command=todo)

menubar.add_cascade(label="File", menu=filemenu)
menubar.add_cascade(label="Edit")
menubar.add_cascade(label="Window", menu=windowmenu) # click on this with a dropdown of each window currently open, then when selected, brings the selected window to the front
menubar.add_cascade(label="Help", menu=helpmenu)

# Add logo
# logo_img = ImageTk.PhotoImage(Image.open('./Images/GrainBound_Logo.jpg').resize((320,180), Image.ANTIALIAS))
# logo = Label(root, image=logo_img, bg='white')
# logo.pack(side="top", fill="both", expand="yes")
# logo.place(relx=0.01, rely=0.01, anchor='nw')

canvasBig = Canvas(root, width=1280, height=800, bg='#F0F0F0')
canvasBig.pack()

# Left Panel
leftPanel = canvasBig.create_rectangle(0, 0, 325, 800, fill='#f48da9', outline='#f48da9')

projectLabel = Label(root, text="Projects", font=("Helvetica", 24, 'bold'), fg='#FFFFFF', bg='#f48da9')
projectLabel.pack()
projectLabel.place(relx=0.075, rely=0.07, anchor='nw')

sandwhich = ImageTk.PhotoImage(Image.open('./Images/sandwhich.png').resize((35,35), Image.ANTIALIAS))
sandwhichButton = Label(root, image=sandwhich, bg='#f48da9')
sandwhichButton.pack(side="top", fill="both", expand="yes")
sandwhichButton.place(x=20, y=58, anchor='nw')

newProjectButtonImage = ImageTk.PhotoImage(Image.open('./Images/project-button.png').resize((260,130), Image.ANTIALIAS))
newProjectButton = Label(root, image=newProjectButtonImage, bg='#f48da9')
newProjectButton.pack(side="top", fill="both", expand="yes")
newProjectButton.place(x=32.5, y=200, anchor='nw')
newProjectButton.bind("<Button-1>", lambda e: newProject())

openProjectButtonText = Label(root, text="Open Project", font=("Arial", 11, 'bold'), fg='#FFFFFF', bg='#9bd7d2')
openProjectButtonText.pack()
openProjectButtonText.place(x=118, y=372, anchor='nw')
openProjectButton = canvasBig.create_rectangle(32.5, 365, 292.5, 400, outline='#FFFFFF', fill='#9bd7d2')
openProjectButtonText.bind("<Button-1>", lambda e: openProject())
canvasBig.tag_bind(openProjectButton, '<ButtonPress-1>', lambda e: openProject())

saveProjectButtonText = Label(root, text="Save Project", font=("Arial", 11, 'bold'), fg='#FFFFFF', bg='#9bd7d2')
saveProjectButtonText.pack()
saveProjectButtonText.place(x=118, y=432, anchor='nw')
saveProjectButton = canvasBig.create_rectangle(32.5, 425, 292.5, 460, outline='#FFFFFF', fill='#9bd7d2')
saveProjectButtonText.bind("<Button-1>", lambda e: save())
canvasBig.tag_bind(saveProjectButton, '<ButtonPress-1>', lambda e: save())

saveProjectAsButtonText = Label(root, text="Save Project As", font=("Arial", 11, 'bold'), fg='#FFFFFF', bg='#9bd7d2')
saveProjectAsButtonText.pack()
saveProjectAsButtonText.place(x=108, y=492, anchor='nw')
saveProjectAsButton = canvasBig.create_rectangle(32.5, 485, 292.5, 520, outline='#FFFFFF', fill='#9bd7d2')
saveProjectAsButtonText.bind("<Button-1>", lambda e: saveAs())
canvasBig.tag_bind(saveProjectAsButton, '<ButtonPress-1>', lambda e: saveAs())

aboutButtonText = Label(root, text="About Us", font=("Arial", 11, 'bold'), fg='#FFFFFF', bg='#9bd7d2')
aboutButtonText.pack()
aboutButtonText.place(x=130, y=667, anchor='nw')
aboutButton = canvasBig.create_rectangle(32.5, 660, 292.5, 695, outline='#FFFFFF', fill='#9bd7d2')

settingsButtonText = Label(root, text="Settings", font=("Arial", 11, 'bold'), fg='#FFFFFF', bg='#9bd7d2')
settingsButtonText.pack()
settingsButtonText.place(x=135, y=727, anchor='nw')
settingsButton = canvasBig.create_rectangle(32.5, 720, 292.5, 755, outline='#FFFFFF', fill='#9bd7d2')

grainboundLabel = Label(root, text="© GrainBound LLC", font=("Helvetica", 8, 'bold'), fg='#FFFFFF', bg='#f48da9')
grainboundLabel.pack()
grainboundLabel.place(x=113, y=772, anchor='nw')

# Bottom panel
bottomPanel = canvasBig.create_rectangle(325, 737.5, 1280, 800, outline='#9bd7d2', fill='#9bd7d2')

websiteText = Label(root, text="W W W . G R A I N B O U N D . C O M", font=("Arial", 11, 'bold'), fg="#FFFFFF", bg="#9bd7d2")
websiteText.pack()
websiteText.place(x=355, y=760, anchor='nw')

phoneText = Label(root, text="1 - 8 5 5 - G R A I N B D", font=("Arial", 11, 'bold'), fg="#FFFFFF", bg="#9bd7d2")
phoneText.pack()
phoneText.place(x=1090, y=760, anchor='nw')

facebook = ImageTk.PhotoImage(Image.open('./Images/facebook.png').resize((20,20), Image.ANTIALIAS))
facebookButton = Label(root, image=facebook, bg='#9bd7d2')
facebookButton.pack(side="top", fill="both", expand="yes")
facebookButton.place(x=750, y=760, anchor='nw')

instagram = ImageTk.PhotoImage(Image.open('./Images/instagram.png').resize((20,20), Image.ANTIALIAS))
instagramButton = Label(root, image=instagram, bg='#9bd7d2')
instagramButton.pack(side="top", fill="both", expand="yes")
instagramButton.place(x=800, y=760, anchor='nw')

youtube = ImageTk.PhotoImage(Image.open('./Images/youtube.png').resize((20,20), Image.ANTIALIAS))
youtubeButton = Label(root, image=youtube, bg='#9bd7d2')
youtubeButton.pack(side="top", fill="both", expand="yes")
youtubeButton.place(x=850, y=760, anchor='nw')

linkedin = ImageTk.PhotoImage(Image.open('./Images/linkedin.png').resize((20,20), Image.ANTIALIAS))
linkedinButton = Label(root, image=linkedin, bg='#9bd7d2')
linkedinButton.pack(side="top", fill="both", expand="yes")
linkedinButton.place(x=900, y=760, anchor='nw')

# Border rectangles
vertRectangle = canvasBig.create_rectangle(323, 0, 327, 800, outline='#FFFFFF', fill='#FFFFFF')
horizRectangle = canvasBig.create_rectangle(325, 735.5, 1280, 739.5, outline='#FFFFFF', fill='#FFFFFF')

# Right panel
projectTitle = Label(root, text="Untitled Project", font=("Helvetica", 48, 'bold'), fg='#000000', bg='#F0F0F0')
projectTitle.pack()
projectTitle.place(x=357.5, y=41, anchor='nw')

logoImage = ImageTk.PhotoImage(Image.open('./Images/logo.png').resize((250,250), Image.ANTIALIAS))
logoImageButton = Label(root, image=logoImage, bg='#F0F0F0')
logoImageButton.pack(side="top", fill="both", expand="yes")
logoImageButton.place(x=1005, y=25, anchor='nw')

imageAnalysisImageButton = ImageTk.PhotoImage(Image.open('./Images/imaging-button.png').resize((260,130), Image.ANTIALIAS))
imageAnalysisButton = Label(root, image=imageAnalysisImageButton, bg='#F0F0F0')
imageAnalysisButton.pack(side="top", fill="both", expand="yes")
imageAnalysisButton.place(x=357.5, y=200, anchor='nw')
imageAnalysisButton.bind("<Button-1>", lambda e: openNewMaterial())

compositionAnalysisImageButton = ImageTk.PhotoImage(Image.open('./Images/composition-button.png').resize((260,130), Image.ANTIALIAS))
compositionAnalysisButton = Label(root, image=compositionAnalysisImageButton, bg='#F0F0F0')
compositionAnalysisButton.pack(side="top", fill="both", expand="yes")
compositionAnalysisButton.place(x=672.5, y=200, anchor='nw')
compositionAnalysisButton.bind("<Button-1>", lambda e: openNewEDS())

machineLearningImageButton = ImageTk.PhotoImage(Image.open('./Images/ml-button.png').resize((260,130), Image.ANTIALIAS))
machineLearningButton = Label(root, image=machineLearningImageButton, bg='#F0F0F0')
machineLearningButton.pack(side="top", fill="both", expand="yes")
machineLearningButton.place(x=987.5, y=200, anchor='nw')
machineLearningButton.bind("<Button-1>", lambda e: openBokeh())

imagingWindowsText = Label(root, text="Imaging Windows", font=("Arial", 11), fg='#000000', bg='#FFFFFF')
imagingWindowsText.pack()
imagingWindowsText.place(x=432, y=372, anchor='nw')
imagingWindowsButton = canvasBig.create_rectangle(357.5, 365, 617.5, 400, outline='#FFFFFF', fill='#FFFFFF')

compositionWindowsText = Label(root, text="Composition Windows", font=("Arial", 11), fg='#000000', bg='#FFFFFF')
compositionWindowsText.pack()
compositionWindowsText.place(x=732, y=372, anchor='nw')
compositionWindowsButton = canvasBig.create_rectangle(672.5, 365, 932.5, 400, outline='#FFFFFF', fill='#FFFFFF')

machineLearningWindowsText = Label(root, text="Machine Learning Windows", font=("Arial", 11), fg='#000000', bg='#FFFFFF')
machineLearningWindowsText.pack()
machineLearningWindowsText.place(x=1032, y=372, anchor='nw')
machineLearningWindowsButton = canvasBig.create_rectangle(987.5, 365, 1247.5, 400, outline='#FFFFFF', fill='#FFFFFF')

# Finishing the window
# root.config(menu=menubar)

root.mainloop()
# <summary>
# End of tkinter layout code
# </summary>

# customization of nav toolbar
#class NavigationToolbar(NavigationToolbar2GTKAgg):
    # only display the buttons we need
#    toolitems = [t for t in NavigationToolbar2GTKAgg.toolitems if
#                 t[0] in ('Home', 'Pan', 'Zoom', 'Save')]