# Dependencies for installation file: python 2.7

# <summary>
# Dependencies
# </summary>
from Tkinter import *
import tkMessageBox
import os, shutil, time
import tkFileDialog
from PIL import ImageTk, Image
import DM3lib as dm3
import matplotlib.pyplot as plt
import numpy as np
# <summary>
# End of dependencies
# </summary>

# <summary>
# Code before tkinter code
# </summary>

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
    def __init__(self, name, windowInstance, TkImage, imageURL=None, tool='Imaging', brightness=0.5, contrast=0.5, gamma=0.5, madeChangeBeforeSaving=True):
        self.madeChangeBeforeSaving = madeChangeBeforeSaving
        self.TkImage = TkImage
        self.imageURL = imageURL
        self.name = name
        self.tool = tool
        self.brightness = brightness
        self.contrast = contrast
        self.gamma = gamma
        self.windowInstance = windowInstance
# <summary>
# End of each material window class
# </summary>

# <summary>
# Custom tkinter function code
# </summary>
def todo():
    print "TODO"

# Called before root window quits
def quit():
    # quit dialog check
    if madeActionBeforeLastSave:
        if tkMessageBox.askokcancel("Quit", "You have unsaved work, do you still wish to quit?"):
            shutil.rmtree('./temp', ignore_errors=True) # This removes the temp file
            root.quit()
        else:
            return
    else:
        shutil.rmtree('./temp', ignore_errors=True) # This removes the temp file, just in case it still exists
        root.quit()

# Called before each material window quits
def matQuit(name):
    if windowarr.get(name).madeChangeBeforeSaving and tkMessageBox.askokcancel("Quit", "You didn't save this material, do you still wish to quit?", parent=windowarr.get(name).windowInstance):
        updateWindowMenu(name)
        windowarr.get(name).windowInstance.destroy()
        windowarr.pop(name, None)
        os.remove("./temp/" + name + ".jpg")

# Under the Window menu tab, either add or remove a window. Variable name is a string that is the window name
def updateWindowMenu(name):
    global windowmenu
    if name in windowarr:
        windowmenu.delete(name)
    else:
        windowmenu.add_command(label=name, command=lambda: bringWindowToFront(name))

# Helper function for updateWindowMenu (above)
def bringWindowToFront(name):
    windowarr.get(name).windowInstance.focus_force() 
    windowarr.get(name).windowInstance.lift()

# Create dm3 file window
def openNewMaterial():
    # File browser and creating window
    fileDir = tkFileDialog.askopenfilename(initialdir="/", title="Select a material", filetypes=(("dm3 files", "*.dm3"), ("all files", "*.*")))
    fileNameArr = fileDir.split('/')
    fileName = fileNameArr[len(fileNameArr)-1]
    window = Toplevel()
    window.title(fileName)
    window.resizable(0,0)
    window.geometry("665x665+700+300")

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

    # Create the dm3 image
    dm3f = dm3.DM3(fileDir)

    # Using matplotlib to save the numpy array image
    plt.figure(frameon=False)
    plt.imshow(dm3f.imagedata[0], cmap='gray')
    plt.axis('off')
    plt.gca().set_axis_off()
    plt.gca().xaxis.set_major_locator(plt.NullLocator())
    plt.gca().yaxis.set_major_locator(plt.NullLocator())
    plt.subplots_adjust(top = 1, bottom = 0, right = 1, left = 0, hspace = 0, wspace = 0)

    # Always save the jpg files in the temp folder, the actual image before closing is saved in the .grainbound file

    # Check to see if temp folder is created yet
    if os.path.isdir("./temp/") != True:
        os.mkdir('./temp/')

    # Check to see if current material is open yet; if it is, make a copy of it increasing a number at the end of the file name; if not, just save it as its file name
    if os.path.isfile("./temp/" + fileName + ".jpg"):
        for x in range(10):
            if(os.path.isfile("./temp/" + fileName + " (copy " + str(x+1) + ")" + ".jpg")):
                continue
            else:
                plt.savefig("./temp/" + fileName + " (copy " + str(x+1) + ")" + ".jpg", bbox_inches='tight', pad_inches=-0.035)

                window.title(fileName + " (copy " + str(x+1) + ")")

                mat_img = ImageTk.PhotoImage(Image.open("./temp/" + fileName + " (copy " + str(x+1) + ")" + ".jpg").resize((600,600), Image.ANTIALIAS))
                windowObj = materialWindow(fileName + " (copy " + str(x+1) + ")", window, mat_img) # Create window object
                updateWindowMenu(fileName + " (copy " + str(x+1) + ")")
                windowarr[fileName + " (copy " + str(x+1) + ")"] = windowObj
                mat = Label(window, image=windowarr[fileName + " (copy " + str(x+1) + ")"].TkImage, bg='white')
                mat.pack(side="top", fill="both", expand="yes")
                mat.place(x=65, y=0, anchor='nw')
                windowarr[fileName + " (copy " + str(x+1) + ")"].windowInstance = window
                break
    else:
        plt.savefig("./temp/" + fileName + ".jpg", bbox_inches='tight', pad_inches=-0.035)

        mat_img = ImageTk.PhotoImage(Image.open("./temp/" + fileName + ".jpg").resize((600,600), Image.ANTIALIAS))
        windowObj = materialWindow(fileName, window, mat_img) # Create window object
        updateWindowMenu(fileName)
        windowarr[fileName] = windowObj
        mat = Label(window, image=windowarr[fileName].TkImage, bg='white')
        mat.pack(side="top", fill="both", expand="yes")
        mat.place(x=65, y=0, anchor='nw')
        window.protocol("WM_DELETE_WINDOW", lambda name=fileName: matQuit(name))
        windowarr[fileName].windowInstance = window
    
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
filemenu.add_command(label="Open material", command=openNewMaterial)
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