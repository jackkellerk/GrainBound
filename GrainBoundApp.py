# Dependencies for installation file: python 2.7,

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
projectDir = "./"
matarr = []

# <summary>
# End of code before tkinter code
# </summary>

# <summary>
# Custom tkinter function code
# </summary>
def todo():
    print "TODO"

def quit():
    if tkMessageBox.askokcancel("Quit", "Do you really wish to quit?"):
        shutil.rmtree('./temp', ignore_errors=True) # This removes the temp file
        root.quit()

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

    plt.figure(frameon=False)
    plt.imshow(dm3f.imagedata[0], cmap='gray')
    plt.axis('off')
    plt.gca().set_axis_off()
    plt.gca().xaxis.set_major_locator(plt.NullLocator())
    plt.gca().yaxis.set_major_locator(plt.NullLocator())
    plt.subplots_adjust(top = 1, bottom = 0, right = 1, left = 0, hspace = 0, wspace = 0)

    if projectName == 'Untitled Project':
        if os.path.isdir("./temp/") != True:
            os.mkdir('./temp/')

        plt.savefig("./temp/" + fileName + ".jpg", bbox_inches='tight', pad_inches=-0.035)

        mat_img = ImageTk.PhotoImage(Image.open("./temp/" + fileName + ".jpg").resize((600,600), Image.ANTIALIAS))
        matarr.append(mat_img)
        mat = Label(window, image=matarr[len(matarr)-1], bg='white')
        mat.pack(side="top", fill="both", expand="yes")
        mat.place(relx=0, rely=0, anchor='nw')

    else:
        plt.savefig(projectDir + "/" + fileName, bbox_inches='tight', pad_inches=-0.035)
    
    #window.mainloop()

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

helpmenu = Menu(menubar, tearoff=0)
helpmenu.add_command(label="About", command=todo)
helpmenu.add_command(label="Contact us", command=todo)

menubar.add_cascade(label="File", menu=filemenu)
menubar.add_cascade(label="Edit")
menubar.add_cascade(label="Display")
menubar.add_cascade(label="Process")
menubar.add_cascade(label="Analysis")
menubar.add_cascade(label="Window")
menubar.add_cascade(label="Microscope")
menubar.add_cascade(label="PASAD")
menubar.add_cascade(label="IPU")
menubar.add_cascade(label="MSA")
menubar.add_cascade(label="SISpectrum")
menubar.add_cascade(label="SITools")
menubar.add_cascade(label="Custom")
menubar.add_cascade(label="GPA")
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