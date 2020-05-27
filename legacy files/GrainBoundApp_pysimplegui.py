# Dependencies to install for installation file: PySimpleGUI27, typing, future

# <summary> 
# Dependencies
# </summary>
import os, sys
import PySimpleGUI27 as sg
from PIL import Image
# <summary> 
# End of dependencies
# </summary>

# <summary> 
# Code executed before PySimpleGUI
# </summary>
img = Image.open('./Images/GrainBound_Logo.png')
nw = 320
nh = 180
img = img.resize((nw, nh), Image.ANTIALIAS)
img.save('./Images/logonew.png')
# <summary> 
# End of code executed before PySimpleGUI
# </summary>

# <summary> 
# PySimpleGUI program code
# </summary>

# This is the toolbar layout
menu_layout = [['File', ['New project', 'Open project', 'Open material', 'Save', 'Save as', 'Exit']],
                ['Edit', ['Option 1', 'Option 2']],
                ['Process', ['Option 3', 'Option 4']],
                ['Analysis', ['Option 5', 'Option 6']],
                ['Window', ['Option 7', 'Option 8']],
                ['Microscope', ['Option 9', 'Option 10']],
                ['PASAD', ['Option 11', 'Option 12']],
                ['IPU', ['Option 13', 'Option 14']],
                ['MSA', ['Option 15', 'Option 16']],
                ['SISpectrum', ['Option 17', 'Option 18']],
                ['SITools', ['Option 19', 'Option 20']],
                ['Custom', ['Option 21', 'Option 22']],
                ['GPA', ['Option 23', 'Option 24']],
                ['Help', ['About']]]

# This is the actual gui layout
layout = [[sg.Menu(menu_layout)],
            [sg.Image('./Images/logonew.png', background_color='#FFFFFF')]]

# Creates the main window
window = sg.Window('GrainBound', layout, background_color='#FFFFFF', location=(0,0), size=(1280,800)).Finalize()

# This is the event loop. Every button click is handled here.
while True:
    event, values = window.read()

    # If 'Exit' is called, break out of the loop, thus closing the program
    if event == None or event == 'Exit':
        break

    # If 'Open material' is called, open a new window
    elif event == 'Open material':
        newWindow()

# After breaking from the loop, close the window
window.close()
# <summary> 
# End of PySimpleGUI program code
# </summary>

# <summary>
# This is the class for the dm3 window
# </summary>
def newWindow():
    layout = [sg.Ok()]
    window = sg.Window("dm3", layout)
    while True:
        event, values = window.read(timeout=200)
        if not event:
            break
# <summary>
# End of class
# </summary>