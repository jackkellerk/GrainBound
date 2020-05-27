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
matarr = {} # This is a dictionary, the keys are the names of the windows, and the values are the images associated with them
windowarr = {} # This is a dictionary, the keys are the names of the windows, and the values are the window instances

# <summary>
# End of code before tkinter code
# </summary>

# <summary>
# Each material window class
# </summary>
class materialWindow:
    def __init__(self, name, windowInstance, tool='Imaging', brightness=0.5, contrast=0.5, gamma=0.5, madeChangeBeforeSaving=True):
        self.madeChangeBeforeSaving = madeChangeBeforeSaving
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
    if madeActionBeforeLastSave and tkMessageBox.askokcancel("Quit", "You have unsaved work, do you still wish to quit?"):
        shutil.rmtree('./temp', ignore_errors=True) # This removes the temp file
        root.quit()
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
        windowmenu.add_command(label=name, command=lambda: windowarr.get(name).windowInstance.focus_force())

# Create dm3 file window
def openMaterial():
    # File browser and creating window
    fileDir = tkFileDialog.askopenfilename(initialdir="/", title="Select a material", filetypes=(("dm3 files", "*.dm3"), ("all files", "*.*")))
    fileNameArr = fileDir.split('/')
    fileName = fileNameArr[len(fileNameArr)-1]
    window = Toplevel()
    window.attributes('-topmost', 'true')
    window.title(fileName)
    window.geometry("600x600+700+300")

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
                matarr[fileName + " (copy " + str(x+1) + ")"] = mat_img # python dictionary, inside [] is the key, the expression is equal to the value of the key
                mat = Label(window, image=matarr[fileName + " (copy " + str(x+1) + ")"], bg='white')
                mat.pack(side="top", fill="both", expand="yes")
                mat.place(relx=0, rely=0, anchor='nw')
                updateWindowMenu(fileName + " (copy " + str(x+1) + ")")
                windowObj = materialWindow(fileName + " (copy " + str(x+1) + ")", window) # Create window instance
                windowarr[fileName + " (copy " + str(x+1) + ")"] = windowObj
                break
    else:
        plt.savefig("./temp/" + fileName + ".jpg", bbox_inches='tight', pad_inches=-0.035)

        mat_img = ImageTk.PhotoImage(Image.open("./temp/" + fileName + ".jpg").resize((600,600), Image.ANTIALIAS))
        matarr[fileName] = mat_img # python dictionary, inside [] is the key, the expression is equal to the value of the key
        mat = Label(window, image=matarr[fileName], bg='white')
        mat.pack(side="top", fill="both", expand="yes")
        mat.place(relx=0, rely=0, anchor='nw')
        window.protocol("WM_DELETE_WINDOW", lambda name=fileName: matQuit(name))
        updateWindowMenu(fileName)
        windowObj = materialWindow(fileName, window)
        windowarr[fileName] = windowObj
    
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
filemenu.add_command(label="Open material", command=openMaterial)
filemenu.add_command(label="Save material", command=todo)
filemenu.add_command(label="Save material as", command=todo)
filemenu.add_separator()
filemenu.add_command(label="Exit", command=quit)

windowmenu = Menu(menubar, tearoff=0)

helpmenu = Menu(menubar, tearoff=0)
helpmenu.add_command(label="About", command=todo)
helpmenu.add_command(label="Contact us", command=updateWindowMenu)

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