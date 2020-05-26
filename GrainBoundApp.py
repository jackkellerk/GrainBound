# Dependencies for installation file: python 2.7,

# <summary>
# Dependencies
# </summary>
from Tkinter import *
import tkFileDialog
from PIL import ImageTk, Image
# <summary>
# End of dependencies
# </summary>

# <summary>
# Code before tkinter code
# </summary>

# <summary>
# End of code before tkinter code
# </summary>

# <summary>
# Custom tkinter function code
# </summary>
def todo():
    print "TODO"

# Create dm3 file window
def openMaterial():
    fileDir = tkFileDialog.askopenfilename(initialdir="/", title="Select a material", filetypes=(("dm3 files", "*.dm3"), ("all files", "*.*")))
    fileName = fileDir.split('/')
    window = Toplevel()
    window.attributes('-topmost', 'true')
    window.title(fileName[len(fileName)-1])
    window.geometry("500x500")
# <summary>
# End of custom tkinter function code
# </summary>

# <summary>
# Tkinter layout code
# </summary>
# Creating the window
root = Tk()
root.title('GrainBound')
root.geometry("1280x800")
root.configure(background='#FFFFFF')

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
filemenu.add_command(label="Exit", command=root.quit)

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