# <summary>
# Dependencies
# </summary>
from tkinter import *
import tkinter.messagebox
import os, shutil, time
import tkinter.filedialog
from PIL import ImageTk, Image
from ncempy.io import dm
import matplotlib.pyplot as plt
import numpy as np
import cv2
# <summary>
# End of dependencies
# </summary>

# <summary>
# Code before tkinter code
# </summary>
np.set_printoptions(threshold=sys.maxsize)

# Global variables
projectName = 'Untitled Project'
projectDir = "./temp/"
madeActionBeforeLastSave = False # This variable is used to determine whether closing the program should prompt the user to save
windowarr = {} # This is a dictionary, the keys are the names of the windows, and the values are the window classes

# <summary>
# End of code before tkinter code
# </summary>

# <summary>
# Each material window class
# </summary>
class materialWindow:
    def __init__(self, name, windowInstance, TkImage, nextMaterialName=None, previousMaterialName=None, isActive=False, imageLabel=None, imageArr=None, tool='Imaging', brightness=0, contrast=float(1), gamma=float(1), madeChangeBeforeSaving=True):
        self.madeChangeBeforeSaving = madeChangeBeforeSaving
        self.TkImage = TkImage
        self.imageArr = imageArr
        self.name = name
        self.imageLabel = imageLabel
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
# Custom tkinter function code
# </summary>
def todo(debug=""):
    print("TODO " + str(debug))

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
    new_mat_img = ImageTk.PhotoImage(Image.fromarray(adjusted).resize((595,595), Image.ANTIALIAS))

    windowarr[window].TkImage = new_mat_img

    currentWindow = windowarr[window]
    while currentWindow.previousMaterialName != None:
        currentWindow = windowarr[currentWindow.previousMaterialName]
    currentWindow.imageLabel.configure(image=windowarr[window].TkImage)

    windowarr[window].madeChangeBeforeSaving = True

# Updates the brightness in each material window; value is an integer, window is a string of the name of the window
def updateBrightness(value, window):
    beta = float(int(value))

    percentage = float(int(windowarr[window].contrast)) / float(100)
    alpha = (float(2) * percentage) + float(1) # Contrast control (1.0-3.0)

    windowarr[window].brightness = value
    adjusted = cv2.convertScaleAbs(windowarr[window].imageArr, alpha=alpha, beta=beta)
    new_mat_img = ImageTk.PhotoImage(Image.fromarray(adjusted).resize((595,595), Image.ANTIALIAS))

    windowarr[window].TkImage = new_mat_img

    currentWindow = windowarr[window]
    while currentWindow.previousMaterialName != None:
        currentWindow = windowarr[currentWindow.previousMaterialName]
    currentWindow.imageLabel.configure(image=windowarr[window].TkImage)

    windowarr[window].madeChangeBeforeSaving = True

# Updates the brightness in each material window; value is an integer, window is a string of the name of the window
def updateGamma(value, window):
    if value == 0:
        value = 1
    gamma = 1.0 / float(int(value))
    windowarr[window].gamma = value
    table = np.array([((i / 255.0) ** gamma) * 255
		for i in np.arange(0, 256)]).astype("uint8")
    
    adjusted = cv2.LUT(windowarr[window].imageArr.astype("uint8"), table)
    new_mat_img = ImageTk.PhotoImage(Image.fromarray(adjusted).resize((595,595), Image.ANTIALIAS))

    windowarr[window].TkImage = new_mat_img

    currentWindow = windowarr[window]
    while currentWindow.previousMaterialName != None:
        currentWindow = windowarr[currentWindow.previousMaterialName]
    currentWindow.imageLabel.configure(image=windowarr[window].TkImage)

    windowarr[window].madeChangeBeforeSaving = True

# Called before root window quits
def quit():
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
def matQuit(name):
    if windowarr.get(name).madeChangeBeforeSaving and tkinter.messagebox.askokcancel("Quit", "You didn't save this material, do you still wish to quit?", parent=windowarr.get(name).windowInstance):
        updateWindowMenu(name)
        windowarr.get(name).windowInstance.destroy()
        windowarr.pop(name, None)
        os.remove("./temp/" + name + ".jpg")

# Under the Window menu tab, either add or remove a window. Variable name is a string that is the window name
def updateWindowMenu(name):
    global windowmenu
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
    updateGamma(windowarr[currentWindow.nextMaterialName].gamma, currentWindow.nextMaterialName)
    updateContrast(windowarr[currentWindow.nextMaterialName].contrast, currentWindow.nextMaterialName)
    updateBrightness(windowarr[currentWindow.nextMaterialName].brightness, currentWindow.nextMaterialName)
    windowarr[name].imageLabel.configure(image=windowarr[currentWindow.nextMaterialName].TkImage)

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
    updateGamma(windowarr[currentWindow.previousMaterialName].gamma, currentWindow.previousMaterialName)
    updateContrast(windowarr[currentWindow.previousMaterialName].contrast, currentWindow.previousMaterialName)
    updateBrightness(windowarr[currentWindow.previousMaterialName].brightness, currentWindow.previousMaterialName)
    windowarr[name].imageLabel.configure(image=windowarr[currentWindow.previousMaterialName].TkImage)

# Create dm3 file window
def openNewMaterial():
    # File browser and creating window
    fileDir = tkinter.filedialog.askopenfilenames(initialdir="/", title="Select a material", filetypes=(("dm3 files", "*.dm3"), ("all files", "*.*")))
    fileNameArr = fileDir[0].split('/')
    fileName = fileNameArr[len(fileNameArr)-1]
    window = Toplevel()
    window.title(fileName)
    window.resizable(0,0)
    window.geometry("665x665+700+300")

    # Create the dm3 image
    dm3f = dm.dmReader(fileDir[0])
    dm3f['data'] = ((dm3f['data'] * 3) / 16000) # Transforming data

    # Check to see if current material is open yet; if it is, make a copy of it increasing a number at the end of the file name; if not, just save it as its file name
    if fileName in windowarr.keys():
        for x in range(100):
            if (fileName + " (copy " + str(x+1) + ")") in windowarr.keys():
                continue
            else:
                window.title(fileName + " (copy " + str(x+1) + ")")

                mat_img = ImageTk.PhotoImage(Image.fromarray(dm3f['data']).resize((595,595), Image.ANTIALIAS))
                mat_img_arr = dm3f['data']
                windowObj = materialWindow(fileName + " (copy " + str(x+1) + ")", window, mat_img, imageArr=mat_img_arr, isActive=True) # Create window object
                updateWindowMenu(fileName + " (copy " + str(x+1) + ")")
                windowarr[fileName + " (copy " + str(x+1) + ")"] = windowObj
                mat = Label(window, image=windowarr[fileName + " (copy " + str(x+1) + ")"].TkImage, bg='white')
                mat.pack(side="top", fill="both", expand="yes")
                mat.place(x=66, y=0, anchor='nw')
                windowarr[fileName + " (copy " + str(x+1) + ")"].windowInstance = window
                windowarr[fileName + " (copy " + str(x+1) + ")"].imageLabel = mat

                # Add widgets
                newFileName = fileName + " (copy " + str(x+1) + ")"
                moveButton = Button(window, width=4, height=3, text="Move", command=todo)
                moveButton.pack()
                moveButton.place(x=2, y=2)

                annotateButton = Button(window, width=4, height=3, text="Draw", command=todo)
                annotateButton.pack()
                annotateButton.place(x=2, y=72)
                
                toolButton = Button(window, width=4, height=3, text="Change\nTool", command=todo)
                toolButton.pack()
                toolButton.place(x=2, y=142)

                metaDataButton = Button(window, width=4, height=3, text="Meta\nData", command=todo)
                metaDataButton.pack()
                metaDataButton.place(x=2, y=212)

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
                break
    else:
        mat_img = ImageTk.PhotoImage(Image.fromarray(dm3f['data']).resize((595,595), Image.ANTIALIAS))
        mat_img_arr = dm3f['data']
        windowObj = materialWindow(fileName, window, mat_img, imageArr=mat_img_arr, isActive=True) # Create window object
        updateWindowMenu(fileName)
        windowarr[fileName] = windowObj
        mat = Label(window, image=windowarr[fileName].TkImage, bg='white')
        mat.pack(side="top", fill="both", expand="yes")
        mat.place(x=66, y=0, anchor='nw')
        window.protocol("WM_DELETE_WINDOW", lambda name=fileName: matQuit(name))
        windowarr[fileName].windowInstance = window
        windowarr[fileName].imageLabel = mat

        # Add widgets
        moveButton = Button(window, width=4, height=3, text="Move", command=todo)
        moveButton.pack()
        moveButton.place(x=2, y=2)

        annotateButton = Button(window, width=4, height=3, text="Draw", command=todo)
        annotateButton.pack()
        annotateButton.place(x=2, y=72)
        
        toolButton = Button(window, width=4, height=3, text="Change\nTool", command=todo)
        toolButton.pack()
        toolButton.place(x=2, y=142)

        metaDataButton = Button(window, width=4, height=3, text="Meta\nData", command=todo)
        metaDataButton.pack()
        metaDataButton.place(x=2, y=212)

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
    
    # This is for the other files selected in the file dialog; open them not as windows, but as window objects
    for i in range(len(fileDir)):
        if i == 0:
            continue

        fileNameArrOthers = fileDir[i].split('/')
        fileNameOthers = fileNameArrOthers[len(fileNameArrOthers)-1]

        # Create the dm3 image
        dm3f = dm.dmReader(fileDir[i])
        dm3f['data'] = ((dm3f['data'] * 3) / 16000) # Transforming data

        # Check to see if current material is open yet; if it is, make a copy of it increasing a number at the end of the file name; if not, just save it as its file name
        if fileNameOthers in windowarr.keys():
            for x in range(100):
                if (fileNameOthers + " (copy " + str(x+1) + ")") in windowarr.keys():
                    continue
                else:
                    mat_img = ImageTk.PhotoImage(Image.fromarray(dm3f['data']).resize((595,595), Image.ANTIALIAS))
                    mat_img_arr = dm3f['data']
                    windowObj = materialWindow(fileNameOthers + " (copy " + str(x+1) + ")", window, mat_img, imageArr=mat_img_arr) # Create window object
                    windowarr[fileNameOthers + " (copy " + str(x+1) + ")"] = windowObj
                    mat = Label(window, image=windowarr[fileNameOthers + " (copy " + str(x+1) + ")"].TkImage, bg='white')
                    windowarr[fileNameOthers + " (copy " + str(x+1) + ")"].windowInstance = window
                    windowarr[fileNameOthers + " (copy " + str(x+1) + ")"].imageLabel = mat
                    break
        else:
            mat_img = ImageTk.PhotoImage(Image.fromarray(dm3f['data']).resize((595,595), Image.ANTIALIAS))
            mat_img_arr = dm3f['data']
            windowObj = materialWindow(fileNameOthers, window, mat_img, imageArr=mat_img_arr) # Create window object
            windowarr[fileNameOthers] = windowObj
            mat = Label(window, image=windowarr[fileNameOthers].TkImage, bg='white')
            windowarr[fileNameOthers].windowInstance = window
            windowarr[fileNameOthers].imageLabel = mat
    
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

# <summary>
# End of custom tkinter function code
# </summary>

# <summary>
# Tkinter layout code
# </summary>
root = Tk()
root.title('GrainBound')
root.geometry("1280x800")
root.configure(background='#FFFFFF')
root.protocol("WM_DELETE_WINDOW", quit)

# Creating the menubar
menubar = Menu(root)

filemenu = Menu(menubar, tearoff=0)
filemenu.add_command(label="New project", command=todo)
filemenu.add_command(label="Open project", command=todo)
filemenu.add_command(label="Save project", command=todo)
filemenu.add_command(label="Save project as", command=todo)
filemenu.add_separator()
filemenu.add_command(label="Open material(s)", command=openNewMaterial)
filemenu.add_command(label="Save material", command=todo)
filemenu.add_command(label="Save material as", command=todo)
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
logo_img = ImageTk.PhotoImage(Image.open('./Images/GrainBound_Logo.jpg').resize((320,180), Image.ANTIALIAS))
logo = Label(root, image=logo_img, bg='white')
logo.pack(side="top", fill="both", expand="yes")
logo.place(relx=0.01, rely=0.01, anchor='nw')

# Finishing the window
root.config(menu=menubar)
root.mainloop()
# <summary>
# End of tkinter layout code
# </summary>