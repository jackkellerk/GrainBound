# Global variables

projectName = 'Untitled Project'
projectDir = "./temp/"
madeActionBeforeLastSave = False # This variable is used to determine whether closing the program should prompt the user to save
windowarr = {} # This is a dictionary, the keys are the names of the windows, and the values are the window classes
old_mouse_x = None # These two variables are to keep track of the previous mouse position for the tools
old_mouse_y = None
zoomArr = [None] * 4 # This is used to hold the temp lines for the box for the zoom tool
