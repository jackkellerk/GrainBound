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
from subprocess import Popen
import webbrowser
import json
from SET import windowmenu, projectName, projectDir, madeActionBeforeLastSave, windowarr, old_mouse_x, old_mouse_y, zoomArr
from functools import partial
from bokeh.layouts import column, gridplot
from bokeh.models import ColumnDataSource, Slider, BoxSelectTool, LassoSelectTool, Button
from bokeh.plotting import figure, curdoc
from bokeh.server.server import Server
import numpy as np
import pandas as pd
from bokeh.events import Reset
from bokeh.io.export import get_screenshot_as_png
from jinja2 import Template
from multiprocessing import Process
# <summary>
# End of dependencies
# </summary>

# <summary>
# Code before tkinter code
# </summary>

# <summary>
# End of code before tkinter code
# </summary>
nbins_ = 200
nbins = nbins_

# initialize the selected dictionary
selected_dict = {}

# reads the files
df = pd.read_pickle('./Bokeh_serve_v2/Data_out')

# Corrections for products made

# This removes extra spaces
df['Product Goal'] = df['Product Goal'].replace({'B ':'B', 'A ':'A', 'C ':'C', np.nan:'N', 0:'Za', 1:'Zb', -100:'nan'})

# This removes extra spaces
df['Product Made'] = df['Product Made'].replace({'B ':'B', 'A ':'A', 'C ':'C', np.nan:'N',  -100:'nan'})

#Builds dicts for the products
Product_goal_dict = dict(enumerate(df['Product Goal'].astype('category').cat.categories))
Product_made_dict = dict(enumerate(df['Product Made'].astype('category').cat.categories))

# Corrections for products made

# This removes extra spaces
df['Product Goal'] = df['Product Goal'].replace({'B ':'B', 'A ':'A', 'C ':'C', np.nan:'z_nan', 0:'z_a', 1:'z_b', -100:'znan'})

# This removes extra spaces
df['Product Made'] = df['Product Made'].replace({'B ':'B', 'A ':'A', 'C ':'C', np.nan:'z_nan',  -100:'z_nan'})

# Sets this up as a catagorical value
df['Product Goal Catagorical'] = df['Product Goal'].astype('category').cat.codes

# Sets this up as a catagorical value
df['Product Made Catagorical'] = df['Product Made'].astype('category').cat.codes

# sets the tools that are available
TOOLS = "pan,wheel_zoom,box_select,lasso_select,reset,save"

# defines the line style
LINE_ARGS = dict(color="#3A5785", line_color=None)

# selects only the columns we want to plot based on the names
ind = df.columns.str.contains('_update') + df.columns.str.contains('Catagorical')

main = []
vh1_list = []
vh2_list = []
vhist = []
vedges = []
sources = []

# function that creates the histogram
def create_histogram(df, y_label=None, plot_width=150, nbins=nbins, selected_dict = selected_dict):

    # extracts data from the y_label extracted
    data = df[y_label]

    if 'Catagorical' in y_label:
        nbins = len(np.unique(data))
    else:
        nbins = 200

    vhist, vedges = np.histogram(data, bins=nbins)

    # builds a zero vector
    vzeros = np.zeros(len(vedges) - 1)
    vmax = max(vhist) * 1.1

    # builds the figures
    pv = figure(toolbar_location='above', plot_width=plot_width, plot_height=300, x_range=(-vmax, vmax),
                min_border=10, y_axis_location="right", tools=TOOLS)

    # sets the gridline
    pv.ygrid.grid_line_color = None

    # tilts the label orientation
    pv.xaxis.major_label_orientation = np.pi / 4

    # sets the graph background fill color
    pv.background_fill_color = "#fafafa"

    # constructs the data for plotting histograms with quad
    data = {'top': vedges[1:], 'bottom': vedges[:-1], 'left': vzeros, 'right': vhist}

    # builds the data source from the data
    source = ColumnDataSource(data)

    # Plots the original graph
    pv.quad(top="top", bottom="bottom", left="left", right="right", source=source, color="#f48da9", line_color="#f48da9",line_width = .1)

    # plots the negative and positive of the results
    vh1 = pv.quad(left=0, bottom=vedges[:-1], top=vedges[1:], right=vzeros, alpha=0.5, **LINE_ARGS)
    vh2 = pv.quad(left=0, bottom=vedges[:-1], top=vedges[1:], right=vzeros, alpha=0.1, **LINE_ARGS)

    # adds the axis and removes my label from the data
    pv.yaxis.axis_label = y_label.split('_')[0]

    if 'Catagorical' in y_label:
        name = y_label.split(' Catagorical')[0]
        y_tick = np.arange(len(np.unique(df[name]))) + .5

        cat = df[name].astype('category').cat.categories
        string = []

        for cat_ in cat:
            new_string = cat_.replace('z_', '').replace('a', '0').replace('b', '1').replace('n0n', 'nan')

            string.append(new_string)
        pv.yaxis.ticker = y_tick
        pv.yaxis.major_label_overrides = dict(zip(y_tick, string))



    # callback for when we select some data
    source.selected.on_change('indices', partial(callback, y_label=y_label,
                                                main=main, df=df, sources=sources,
                                                selected_dict=selected_dict,
                                                vh1_list=vh1_list, vh2_list=vh2_list,
                                                nbins=nbins))
    # callback for the reset operation
    selected_dict = pv.on_event('reset', partial(reset, selected_dict=selected_dict, df =df , vh1_list = vh1_list,
                                                vh2_list = vh2_list, nbins=nbins))

    return pv, vh1, vh2, vhist, vedges, source


# function that resets the dictionary to the default
def reset(selected_dict, df, vh1_list, vh2_list, nbins):
    # resets the dictionary
    selected_dict = {}
    update_graphs(df, selected_dict, vh1_list, vh2_list, nbins=nbins)
    return selected_dict

def update_graphs(df, selected_dict, vh1_list, vh2_list, nbins=nbins):
    # intializes the array so that all index are selected
    ind_selected = np.linspace(0, df.shape[0] - 1, df.shape[0]).astype(int)

    # loops around the selection dictionary
    for selected in selected_dict:

        if 'Product' in selected:
            nbins_ = len(np.unique(df[selected]))
        else:
            nbins_ = 200

        # computes the histogram
        #vhist, vedges = np.histogram(df[selected], bins=nbins_)
        # vzeros = np.zeros(len(vedges) - 1)
        # vmax = max(vhist) * 1.1

        # builds a temporary index vector for index
        temp_ind = []

        # loops around all of the selections for a single parameter
        for index_value in selected_dict[selected]:
            vhist, vedges = np.histogram(df[selected], bins=nbins_)
            lower_bound = vedges[index_value]
            upper_bound = vedges[index_value + 1]

            # Appends all the selections to a dictionary
            temp_ind = np.append(temp_ind,
                                np.where(
                                    np.logical_and(
                                        df[selected] >= lower_bound,
                                        df[selected] <= upper_bound))).astype(int)

        # computes the index that remain in selected
        ind_selected = np.intersect1d(ind_selected, temp_ind)

    # this calls a function that plots the secondary graphs
    add_secondary_plots(df, ind_selected, vh1_list, vh2_list, nbins_)

def add_secondary_plots(df, ind_selected, vh1_list, vh2_list, nbins):

    # finds the columns that we want to plot
    cols = df.columns.str.contains('_update') + df.columns.str.contains('Catagorical')

    # loops around the selected parameters
    for i, selected in enumerate(df.columns[cols]):

        if 'Product' in selected:
            nbins = len(np.unique(df[selected]))
        else:
            nbins = 200

        #computes the original hisogram
        vhist, vedges = np.histogram(df[selected], bins=nbins)

        # Checks if the number of selected values are 0 or all
        if len(ind_selected) == 0 or df.shape[0] == len(ind_selected):

            # builds a 0 axis
            vzeros = np.zeros(len(vedges) - 1)

            # applies the 0 values as the histogram values
            vhist1, vhist2 = vzeros, vzeros
        else:
            # builds a ones array of the same shape as the raw data
            neg_inds = np.ones_like(df[selected], dtype=np.bool)
            # sets the selected values equal to false
            neg_inds[ind_selected] = False
            # computes the histogram for the negative and positive values based on the selection and the original histogram
            vhist1, _ = np.histogram(df[selected][ind_selected], bins=vedges)
            vhist2, _ = np.histogram(df[selected][neg_inds], bins=vedges)

        # updates the data in the histograms
        vh1_list[i].data_source.data["right"] = vhist1
        vh2_list[i].data_source.data["right"] = -vhist2


def callback(attr, old, new, y_label, main, df, sources, selected_dict, vh1_list, vh2_list, nbins=nbins):
    # finds the columns we are interested in
    ind = df.columns.str.contains('_update') + df.columns.str.contains('Catagorical')

    # finds the index of the catagories we just changed
    selected_cat = np.argwhere(df.columns[ind] == y_label).squeeze()

    assert (y_label == df.columns[ind][selected_cat])

    # function that builds a dictionary of the selected values
    selected_dict[y_label] = new

    # This checks to see if there are selected values saved
    if len(selected_dict.keys()) != 0:
        update_graphs(df, selected_dict, vh1_list, vh2_list, nbins=nbins)

def bkapp(doc):
    # builds arrays of all the information we want to save
    for columns in df.columns[ind]:
        main_, vh1_, vh2_, vhist_, vedges_, source_ = create_histogram(df, columns, plot_width=int(1920/6.5), nbins=nbins, selected_dict=selected_dict)
        main.append(main_)
        vh1_list.append(vh1_)
        vh2_list.append(vh2_)
        vhist.append(vhist_)
        vedges.append(vedges_)
        sources.append(source_)

    # This adds a blank value at the end to flatten
    # main.append(div)
    vh1_list.append(None)
    vh2_list.append(None)
    vhist.append(None)
    vedges.append(None)

    # sets the graph layout
    layout = gridplot([main[0:6], main[6:12], main[12:18], main[18:24], main[24:30]])

    with open('./Bokeh_serve_v2/templates/index.html') as f:
        index_template = Template(f.read())

    doc.add_root(layout)
    doc.template = index_template
    doc.title = "GrainBound Machine Learning"

###############################################
###############################################
###############################################

# Setting num_procs here means we can't touch the IOLoop before now, we must
# let Server handle that. If you need to explicitly handle IOLoops then you
# will need to use the lower level BaseServer class.

# <summary>
# Global variables
# </summary>
bokehProcess = {} # Dictionary of bokehProcess ports
# <summary>
# End of global variables
# </summary>

# TODO FOR NEXT WEEK: Move the settings button below the save project as button, where the settings button is make it a contact us button,
# spruce up the about us screen, in the contact us screen -- copy the map from GrainBound's website, add contact info (from Deanne's email footer) and info@grainbound.com,
# for Josh's Bokeh applicaiton, update the layout (extend each box horizontally to fit the web browser), add the logo to the top of the website, and for the boxes -- make the contrast more visible

# <summary>
# Custom tkinter function code
# </summary>
def todo(debug=""):
    print("TODO " + str(debug))

def contactUs():
    # Create the window
    windowContactUs = Toplevel()
    windowContactUs.title("Contact Us")
    windowContactUs.resizable(0,0) # can't resize
    windowContactUs.geometry("500x500+700+300")

    # Create the canvas
    contactUsCanvas = Canvas(windowContactUs, width=500, height=500, bg='#f48da9')
    contactUsCanvas.pack()
    
    # Create the map
    mapImage = ImageTk.PhotoImage(Image.open('./Images/map.png').resize((750,355), Image.ANTIALIAS))
    mapButton = Label(windowContactUs, image=mapImage, bg='#F0F0F0')
    mapButton.pack(side="top", fill="both", expand="yes")
    mapButton.place(x=-115, y=0, anchor='nw')
    mapButton.bind("<Button-1>", lambda e: openURL(r"https://www.google.com/maps/dir/?api=1&destination=301%20Broadway%20#500,%20Bethlehem,%20PA%2018015,%20USA"))
    mapButton.image = mapImage

    # Add the text
    phoneAndEmailLabel = Label(windowContactUs, text="PHONE & EMAIL", font=("Helvetica", 11, 'bold'), fg='#FFFFFF', bg='#f48da9')
    phoneAndEmailLabel.pack()
    phoneAndEmailLabel.place(x=25, y=370, anchor='nw')

    addressHeaderLabel = Label(windowContactUs, text="ADDRESS", font=("Helvetica", 11, 'bold'), fg='#FFFFFF', bg='#f48da9')
    addressHeaderLabel.pack()
    addressHeaderLabel.place(x=320, y=370, anchor='nw')

    address1Label = Label(windowContactUs, text="301 Broadway, Suite 500", font=("Helvetica", 9), fg='#FFFFFF', bg='#f48da9')
    address1Label.pack()
    address1Label.place(x=320, y=415, anchor='nw')

    address2Label = Label(windowContactUs, text="Bethlehem, PA 18015", font=("Helvetica", 9), fg='#FFFFFF', bg='#f48da9')
    address2Label.pack()
    address2Label.place(x=320, y=435, anchor='nw')

    phoneLabel = Label(windowContactUs, text="1-855-GRAINBD (472-4623)", font=("Helvetica", 9), fg='#FFFFFF', bg='#f48da9')
    phoneLabel.pack()
    phoneLabel.place(x=25,y=415)

    emailLabel = Label(windowContactUs, text="info@grainbound.com", font=("Helvetica", 9), fg='#FFFFFF', bg='#f48da9')
    emailLabel.pack()
    emailLabel.place(x=25,y=435)

    # Create boxes
    whiteBox = contactUsCanvas.create_rectangle(30, 395, 80, 397, outline='#FFFFFF', fill='#FFFFFF')

    whiteBox2 = contactUsCanvas.create_rectangle(325, 395, 385, 397, outline='#FFFFFF', fill='#FFFFFF')

def aboutUs():
    # Create the window
    window = Toplevel()
    window.title("About Us")
    window.resizable(0,0) # can't resize
    window.geometry("500x500+700+300")

    # Create the canvas
    aboutUsCanvas = Canvas(window, width=500, height=500, bg='#F0F0F0')
    aboutUsCanvas.pack()

    # Create the layout
    titleLabel = Label(window, text="What is GrainBound?", font=("Helvetica", 24, 'bold'), fg='#000000', bg='#F0F0F0')
    titleLabel.pack()
    titleLabel.place(x=30, y=25, anchor='nw')

    answerLabel = aboutUsCanvas.create_text(230, 230, fill="#000000", width=400, font=("Helvetica", 12), text="GrainBound solves the critical problems that control material behaviors. As a result, your materials become more predictable than ever before.\n\nWe partner with manufacturers of ceramics, metals, and composites to achieve targeted performance goals with applications spanning many industries worldwide.\n\nWith our services, your materials develop enhanced mechanical strength, dielectric breakdown strength, electrical impedance, among many other attributes, all to be realized in new and prolific discoveries.\n\nMost important to us is that we build long-lasting partnerships, ensuring that you always have certainty in your material and its applications.")

def not_finished():
    # Create the window
    window = Toplevel()
    window.title("Notice")
    window.resizable(0,0) # can't resize
    window.geometry("300x100+750+350")

    # Create the canvas
    aboutUsCanvas = Canvas(window, width=500, height=500, bg='#F0F0F0')
    aboutUsCanvas.pack()

    # Create the layout
    titleLabel = Label(window, text="This feature is\nnot ready yet!", font=("Helvetica", 24, 'bold'), fg='#000000', bg='#F0F0F0')
    titleLabel.pack()
    titleLabel.place(x=35, y=5, anchor='nw')

def openURL(url):
    webbrowser.open(url)

def hoverOverButton(button, buttonText, name):
    global canvasBig

    if name == "openProjectButton" or name == "saveProjectButton" or name == "saveAsProjectButton" or name == "aboutButton" or name == "settingsButton" or name == "contactUsButton":
        buttonText.config(bg="#86bdb8")
        canvasBig.itemconfig(button, fill="#86bdb8")
    elif name == "newProjectButton":
        button.config(image=buttonText)
        button.place(x=27.5,y=195)
    elif name == "imageAnalysis":
        button.config(image=buttonText)
        button.place(x=352.5, y=195)
    elif name == "compositionButton":
        button.config(image=buttonText)
        button.place(x=667.5, y=195)
    elif name == "mlButton":
        button.config(image=buttonText)
        button.place(x=982.5, y=195)

def leaveHoverOverButton(button, buttonText, name):
    global canvasBig

    if name == "openProjectButton" or name == "saveProjectButton" or name == "saveAsProjectButton" or name == "aboutButton" or name == "settingsButton" or name == "contactUsButton":
        buttonText.config(bg="#9bd7d2")
        canvasBig.itemconfig(button, fill="#9bd7d2")
    elif name == "newProjectButton":
        button.config(image=buttonText)
        button.place(x=32.5,y=200)
    elif name == "imageAnalysis":
        button.config(image=buttonText)
        button.place(x=357.5, y=200)
    elif name == "compositionButton":
        button.config(image=buttonText)
        button.place(x=672.5, y=200)
    elif name == "mlButton":
        button.config(image=buttonText)
        button.place(x=987.5, y=200)

def openBokehProcess(i):
    server = Server({'/': bkapp}, num_procs=1, port=i)
    server.start()
    server.io_loop.add_callback(server.show, "/")
    server.io_loop.start()

def openBokeh():
    global bokehProcess

    for i in range(5006, 5100):
        if str(i) in bokehProcess:
            pass
        else:
            p = Process(target=openBokehProcess, args=(i,))
            p.start()
            bokehProcess[str(i)] = p
            break

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

# <summary>
# Tkinter layout code
# </summary>
root = Tk()
root.title('GrainBound')
root.geometry("1280x800")
root.resizable(0,0) # can't resize
root.configure(background='#F0F0F0')
root.protocol("WM_DELETE_WINDOW", quit)

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
newProjectButtonImageEnlarged = ImageTk.PhotoImage(Image.open('./Images/project-button.png').resize((270,140), Image.ANTIALIAS))
newProjectButton = Label(root, image=newProjectButtonImage, bg='#f48da9')
newProjectButton.pack(side="top", fill="both", expand="yes")
newProjectButton.place(x=32.5, y=200, anchor='nw')
newProjectButton.bind("<Button-1>", lambda e: newProject())
newProjectButton.bind("<Enter>", lambda e: hoverOverButton(newProjectButton, newProjectButtonImageEnlarged, "newProjectButton"))
newProjectButton.bind("<Leave>", lambda e: leaveHoverOverButton(newProjectButton, newProjectButtonImage, "newProjectButton"))

openProjectButtonText = Label(root, text="Open Project", font=("Arial", 11, 'bold'), fg='#FFFFFF', bg='#9bd7d2')
openProjectButtonText.pack()
openProjectButtonText.place(x=118, y=372, anchor='nw')
openProjectButton = canvasBig.create_rectangle(32.5, 365, 292.5, 400, outline='#FFFFFF', fill='#9bd7d2')
openProjectButtonText.bind("<Button-1>", lambda e: openProject())
canvasBig.tag_bind(openProjectButton, '<ButtonPress-1>', lambda e: openProject())
openProjectButtonText.bind("<Enter>", lambda e: hoverOverButton(openProjectButton, openProjectButtonText, "openProjectButton"))
canvasBig.tag_bind(openProjectButton, "<Enter>", lambda e: hoverOverButton(openProjectButton, openProjectButtonText, "openProjectButton"))
canvasBig.tag_bind(openProjectButton, "<Leave>", lambda e: leaveHoverOverButton(openProjectButton, openProjectButtonText, "openProjectButton"))

saveProjectButtonText = Label(root, text="Save Project", font=("Arial", 11, 'bold'), fg='#FFFFFF', bg='#9bd7d2')
saveProjectButtonText.pack()
saveProjectButtonText.place(x=118, y=432, anchor='nw')
saveProjectButton = canvasBig.create_rectangle(32.5, 425, 292.5, 460, outline='#FFFFFF', fill='#9bd7d2')
saveProjectButtonText.bind("<Button-1>", lambda e: save())
canvasBig.tag_bind(saveProjectButton, '<ButtonPress-1>', lambda e: save())
saveProjectButtonText.bind("<Enter>", lambda e: hoverOverButton(saveProjectButton, saveProjectButtonText, "saveProjectButton"))
canvasBig.tag_bind(saveProjectButton, "<Enter>", lambda e: hoverOverButton(saveProjectButton, saveProjectButtonText, "saveProjectButton"))
canvasBig.tag_bind(saveProjectButton, "<Leave>", lambda e: leaveHoverOverButton(saveProjectButton, saveProjectButtonText, "saveProjectButton"))

saveProjectAsButtonText = Label(root, text="Save Project As", font=("Arial", 11, 'bold'), fg='#FFFFFF', bg='#9bd7d2')
saveProjectAsButtonText.pack()
saveProjectAsButtonText.place(x=108, y=492, anchor='nw')
saveProjectAsButton = canvasBig.create_rectangle(32.5, 485, 292.5, 520, outline='#FFFFFF', fill='#9bd7d2')
saveProjectAsButtonText.bind("<Button-1>", lambda e: saveAs())
canvasBig.tag_bind(saveProjectAsButton, '<ButtonPress-1>', lambda e: saveAs())
saveProjectAsButtonText.bind("<Enter>", lambda e: hoverOverButton(saveProjectAsButton, saveProjectAsButtonText, "saveAsProjectButton"))
canvasBig.tag_bind(saveProjectAsButton, "<Enter>", lambda e: hoverOverButton(saveProjectAsButton, saveProjectAsButtonText, "saveAsProjectButton"))
canvasBig.tag_bind(saveProjectAsButton, "<Leave>", lambda e: leaveHoverOverButton(saveProjectAsButton, saveProjectAsButtonText, "saveAsProjectButton"))

settingsButtonText = Label(root, text="Settings", font=("Arial", 11, 'bold'), fg='#FFFFFF', bg='#9bd7d2')
settingsButtonText.pack()
settingsButtonText.place(x=135, y=552, anchor='nw')
settingsButton = canvasBig.create_rectangle(32.5, 545, 292.5, 580, outline='#FFFFFF', fill='#9bd7d2')
settingsButtonText.bind("<Enter>", lambda e: hoverOverButton(settingsButton, settingsButtonText, "settingsButton"))
canvasBig.tag_bind(settingsButton, "<Enter>", lambda e: hoverOverButton(settingsButton, settingsButtonText, "settingsButton"))
canvasBig.tag_bind(settingsButton, "<Leave>", lambda e: leaveHoverOverButton(settingsButton, settingsButtonText, "settingsButton"))

aboutButtonText = Label(root, text="About Us", font=("Arial", 11, 'bold'), fg='#FFFFFF', bg='#9bd7d2')
aboutButtonText.pack()
aboutButtonText.place(x=130, y=667, anchor='nw')
aboutButton = canvasBig.create_rectangle(32.5, 660, 292.5, 695, outline='#FFFFFF', fill='#9bd7d2')
aboutButtonText.bind("<Enter>", lambda e: hoverOverButton(aboutButton, aboutButtonText, "aboutButton"))
aboutButtonText.bind("<Button-1>", lambda e: aboutUs())
canvasBig.tag_bind(aboutButton, '<ButtonPress-1>', lambda e: aboutUs())
canvasBig.tag_bind(aboutButton, "<Enter>", lambda e: hoverOverButton(aboutButton, aboutButtonText, "aboutButton"))
canvasBig.tag_bind(aboutButton, "<Leave>", lambda e: leaveHoverOverButton(aboutButton, aboutButtonText, "aboutButton"))

contactUsButtonText = Label(root, text="Contact Us", font=("Arial", 11, 'bold'), fg='#FFFFFF', bg='#9bd7d2')
contactUsButtonText.pack()
contactUsButtonText.place(x=125, y=727, anchor='nw')
contactUsButton = canvasBig.create_rectangle(32.5, 720, 292.5, 755, outline='#FFFFFF', fill='#9bd7d2')
contactUsButtonText.bind("<Enter>", lambda e: hoverOverButton(contactUsButton, contactUsButtonText, "contactUsButton"))
contactUsButtonText.bind("<Button-1>", lambda e: contactUs())
canvasBig.tag_bind(contactUsButton, '<ButtonPress-1>', lambda e: contactUs())
canvasBig.tag_bind(contactUsButton, "<Enter>", lambda e: hoverOverButton(contactUsButton, contactUsButtonText, "contactUsButton"))
canvasBig.tag_bind(contactUsButton, "<Leave>", lambda e: leaveHoverOverButton(contactUsButton, contactUsButtonText, "contactUsButton"))

grainboundLabel = Label(root, text="© GrainBound LLC", font=("Helvetica", 8, 'bold'), fg='#FFFFFF', bg='#f48da9')
grainboundLabel.pack()
grainboundLabel.place(x=113, y=772, anchor='nw')

# Bottom panel
bottomPanel = canvasBig.create_rectangle(325, 737.5, 1280, 800, outline='#9bd7d2', fill='#9bd7d2')

websiteText = Label(root, text="W W W . G R A I N B O U N D . C O M", font=("Arial", 11, 'bold'), fg="#FFFFFF", bg="#9bd7d2")
websiteText.pack()
websiteText.place(x=355, y=760, anchor='nw')
websiteText.bind("<Button-1>", lambda e: openURL("https://www.grainbound.com/"))

phoneText = Label(root, text="1 - 8 5 5 - G R A I N B D", font=("Arial", 11, 'bold'), fg="#FFFFFF", bg="#9bd7d2")
phoneText.pack()
phoneText.place(x=1090, y=760, anchor='nw')

facebook = ImageTk.PhotoImage(Image.open('./Images/facebook.png').resize((20,20), Image.ANTIALIAS))
facebookButton = Label(root, image=facebook, bg='#9bd7d2')
facebookButton.pack(side="top", fill="both", expand="yes")
facebookButton.place(x=750, y=760, anchor='nw')
facebookButton.bind("<Button-1>", lambda e: openURL("https://www.facebook.com/"))

instagram = ImageTk.PhotoImage(Image.open('./Images/instagram.png').resize((20,20), Image.ANTIALIAS))
instagramButton = Label(root, image=instagram, bg='#9bd7d2')
instagramButton.pack(side="top", fill="both", expand="yes")
instagramButton.place(x=800, y=760, anchor='nw')
instagramButton.bind("<Button-1>", lambda e: openURL("https://www.instagram.com/"))

youtube = ImageTk.PhotoImage(Image.open('./Images/youtube.png').resize((20,20), Image.ANTIALIAS))
youtubeButton = Label(root, image=youtube, bg='#9bd7d2')
youtubeButton.pack(side="top", fill="both", expand="yes")
youtubeButton.place(x=850, y=760, anchor='nw')
youtubeButton.bind("<Button-1>", lambda e: openURL("https://www.youtube.com/channel/UCDWuVpxY-8_TfXlONNLEe1Q"))

linkedin = ImageTk.PhotoImage(Image.open('./Images/linkedin.png').resize((20,20), Image.ANTIALIAS))
linkedinButton = Label(root, image=linkedin, bg='#9bd7d2')
linkedinButton.pack(side="top", fill="both", expand="yes")
linkedinButton.place(x=900, y=760, anchor='nw')
linkedinButton.bind("<Button-1>", lambda e: openURL("https://www.linkedin.com/company/grainboundllc/"))

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
imageAnalysisImageEnlarged = ImageTk.PhotoImage(Image.open('./Images/imaging-button.png').resize((270,140), Image.ANTIALIAS))
imageAnalysisButton = Label(root, image=imageAnalysisImageButton, bg='#F0F0F0')
imageAnalysisButton.pack(side="top", fill="both", expand="yes")
imageAnalysisButton.place(x=357.5, y=200, anchor='nw')
imageAnalysisButton.bind("<Button-1>", lambda e: not_finished())
imageAnalysisButton.bind("<Enter>", lambda e: hoverOverButton(imageAnalysisButton, imageAnalysisImageEnlarged, "imageAnalysis"))
imageAnalysisButton.bind("<Leave>", lambda e: leaveHoverOverButton(imageAnalysisButton, imageAnalysisImageButton, "imageAnalysis"))

compositionAnalysisImageButton = ImageTk.PhotoImage(Image.open('./Images/composition-button.png').resize((260,130), Image.ANTIALIAS))
compositionAnalysisImageEnlarged = ImageTk.PhotoImage(Image.open('./Images/composition-button.png').resize((270,140), Image.ANTIALIAS))
compositionAnalysisButton = Label(root, image=compositionAnalysisImageButton, bg='#F0F0F0')
compositionAnalysisButton.pack(side="top", fill="both", expand="yes")
compositionAnalysisButton.place(x=672.5, y=200, anchor='nw')
compositionAnalysisButton.bind("<Button-1>", lambda e: not_finished())
compositionAnalysisButton.bind("<Enter>", lambda e: hoverOverButton(compositionAnalysisButton, compositionAnalysisImageEnlarged, "compositionButton"))
compositionAnalysisButton.bind("<Leave>", lambda e: leaveHoverOverButton(compositionAnalysisButton, compositionAnalysisImageButton, "compositionButton"))

machineLearningImageButton = ImageTk.PhotoImage(Image.open('./Images/ml-button.png').resize((260,130), Image.ANTIALIAS))
machineLearningImageEnlarged = ImageTk.PhotoImage(Image.open('./Images/ml-button.png').resize((270,140), Image.ANTIALIAS))
machineLearningButton = Label(root, image=machineLearningImageButton, bg='#F0F0F0')
machineLearningButton.pack(side="top", fill="both", expand="yes")
machineLearningButton.place(x=987.5, y=200, anchor='nw')
machineLearningButton.bind("<Button-1>", lambda e: openBokeh())
machineLearningButton.bind("<Enter>", lambda e: hoverOverButton(machineLearningButton, machineLearningImageEnlarged, "mlButton"))
machineLearningButton.bind("<Leave>", lambda e: leaveHoverOverButton(machineLearningButton, machineLearningImageButton, "mlButton"))

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