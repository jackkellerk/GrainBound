# <----Summary---->
# To go to python 2.7 'source C:/Python27/temp-python/Scripts/activate' then 'python GrainBoundApp.py'
# For clients, make an install bash file to install python 2.7 for them and all of the dependencies in my current python 2.7 version. Make sure about this because this took forever!
# <----End of Summary---->

# !/usr/bin/python
# coding=utf-8

#<----Dependencies---->
import kivy
kivy.require('1.10.1')
from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.widget import Widget
from kivy.uix.button import Button
from kivy.lang import Builder
from kivy.graphics.texture import Texture
from kivy.uix.popup import Popup
from kivy.uix.image import Image
from kivy.uix.image import AsyncImage
from kivy.uix.textinput import TextInput
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.base import Builder
from kivy.properties import StringProperty
from kivy.graphics import *
from kivy.config import Config
from kivy.clock import Clock

import cv2
import numpy as np
import os
import psutil
import time
from multiprocessing import Process
import DM3lib as dm3
import matplotlib.pyplot as plt
#<----End of Dependencies---->


#<----Code that runs when GBApp starts---->
# This loads all of the data from the dm3 file; Make this dynamic later
dm3f = dm3.DM3("./Data/example.dm3")

# Plot the imagedata using plt and save it
plt.figure(frameon=False)
plt.imshow(dm3f.imagedata[0], cmap='gray')
plt.axis('off')
plt.gca().set_axis_off()
plt.gca().xaxis.set_major_locator(plt.NullLocator())
plt.gca().yaxis.set_major_locator(plt.NullLocator())
plt.subplots_adjust(top = 1, bottom = 0, right = 1, left = 0, 
            hspace = 0, wspace = 0)
plt.savefig("material.png", bbox_inches='tight', pad_inches=-0.035)

# Read the image in cv2
img = cv2.imread("./material.png", 0)
#<----End of code that runs when GBApp starts---->


# TODO: Remove Gamma (unless you can figure it out), and then for the metadata show dimension size and other data, and on the image show magnification
# TODO: Make second window always on top. Thinking I can do this once we port it to Windows.
# TODO: Make small window update as you make changes in the big window. See if it is possible to make small windows ad hoc. Also, if there is time, make a zoom feature for the small window.

class rootwi(GridLayout):
    def showData(self):   
        print "Show Metadata"

    def adjust_gamma(self, image, gamma=1.0):
        invGamma = 1.0 / gamma
        table = np.array([((i / 255.0) ** invGamma) * 255
            for i in np.arange(0, 256)]).astype("uint8")

        return cv2.LUT(image, table)

    def contrastUpdate(self):
        try:
            # Make sure the input is a float
            self.ids.contrastSlider.value = float(self.ids.contrastTextInput.text)

            # Edit the image
            alpha = (1.0 * (self.ids.contrastSlider.value / 100)) + 1.0 # Contrast control (1.0-3.0)
            adjusted = cv2.convertScaleAbs(img, alpha=alpha, beta=self.ids.brightnessSlider.value)
            cv2.imwrite("./out.png", adjusted)

            # Update the historgram
            #lst =[]
            #plt.clf()
            #plt.plot()
            #for child in self.ids.histogram.children:
                #self.ids.histogram.remove_widget(child)
            #self.ids.histogram.add_widget(FigureCanvasKivyAgg(plt.gcf()))

            # Reassign the source of the image
            self.ids.material.source = "./out.png"
            self.ids.material.reload()
        except:
            # If input is not a float, reset text to original value
            self.ids.contrastTextInput.text = str(self.ids.contrastSlider.value)

    def brightnessUpdate(self):
        try:
            # Make sure the input is a float
            self.ids.brightnessSlider.value = float(self.ids.brightnessTextInput.text)

            # Edit the image
            beta = self.ids.brightnessSlider.value # Contrast control (1.0-3.0)
            adjusted = cv2.convertScaleAbs(img, alpha=((2.0 * (self.ids.contrastSlider.value / 100)) + 1.0), beta=beta)
            cv2.imwrite("./out.png", adjusted)

            # Reassign the source of the image
            self.ids.material.source = "./out.png"
            self.ids.material.reload()
        except:
            # If input is not a float, reset text to original value
            self.ids.brightnessTextInput.text = str(self.ids.brightnessSlider.value)

    def gammaUpdate(self):
        try:
            # Make sure the input is a float
            self.ids.gammaSlider.value = float(self.ids.gammaTextInput.text) 

            # Edit the image
            gamma = 0.2 #self.ids.gammaSlider.value / 100 # Contrast control (1.0-3.0)
            adjusted = adjust_gamma(img, gamma=gamma)
            cv2.imwrite("./out.png", adjusted)

            # Reassign the source of the image
            self.ids.material.source = "./out.png"
            self.ids.material.reload()
        except:
            # If input is not a float, reset text to original value
            self.ids.gammaTextInput.text = str(self.ids.gammaSlider.value)

class GBApp(App):
    def build(self):
        self.title = "GrainBound Application"
        Builder.load_string("""
<rootwi>:
    orientation:'vertical'

    GridLayout:
        padding:5

        canvas:
            Rectangle:
                source:"/Users/nkt/Desktop/GrainBound/Images/whitebg.png"
                pos: 0, 0
                size: root.width, root.height

        Image:
            size_hint_y: None
            source:"./Images/GrainBound_Logo.png"
            width: 300
            allow_stretch: True
            pos: 50, root.height-150

        Image:
            size_hint_y: None
            source:"./Images/logo_graphic.png"
            height: 225
            width: 225
            pos: 215, root.height-230

        Image:
            size_hint_y: None
            source:"./material.png"
            id: material
            height: 600
            width: 600
            pos: 600, root.height-800

        Button:
            text: "Tool: Imaging"
            pos: root.width-160, root.height-85
            width: 150
            height: 75
            background_color: (0.96, 0.55, 0.66, 1.0)
            background_normal: ''

        Label:
            id: brightnessLabel
            text: " Brightness"
            pos: 90, root.height-670
            color: (0,0,0,1)

        Slider:
            id: brightnessSlider
            min: -100
            max: 100
            step: 1
            value: 0.0
            width: 200
            orientation: 'horizontal'
            pos: 100, root.height-700
            on_value: root.brightnessUpdate()

        TextInput:
            text: str(brightnessSlider.value)
            id: brightnessTextInput
            width: 50
            multiline: False
            height: 30
            pos: 310, root.height-667.5
            background_color: (0.73,0.96,1.0,1) if self.focus else (0.93,0.93,0.93,1)
            background_normal: ''
            on_text_validate: root.brightnessUpdate()

        BoxLayout:
            id: histogram
            pos: 95, root.height-470
            width: 280
            height: 180

        Label:
            id: gammaLabel
            text: "Gamma"
            pos: 90, root.height-570
            color: (0,0,0,1)

        Slider:
            id: gammaSlider
            min: -100
            max: 100
            step: 1
            value: 0.0
            width: 200
            orientation: 'horizontal'
            pos: 100, root.height-600
            on_value: root.gammaUpdate()

        TextInput:
            text: str(gammaSlider.value)
            width: 50
            height: 30
            id: gammaTextInput
            multiline: False
            pos: 310, root.height-567.5
            background_color: (0.73,0.96,1.0,1) if self.focus else (0.93,0.93,0.93,1)
            background_normal: ''
            on_text_validate: root.gammaUpdate()

        Label:
            id: contrastLabel
            text: "Contrast"
            pos: 90, root.height-770
            color: (0,0,0,1)

        Slider:
            id: contrastSlider
            min: -100
            max: 100
            step: 1
            value: 0.0
            width: 200
            orientation: 'horizontal'
            pos: 100, root.height-800
            on_value: root.contrastUpdate()

        TextInput:
            text: str(contrastSlider.value)
            width: 50
            height: 30
            id: contrastTextInput
            multiline: False
            pos: 310, root.height-767.5
            background_color: (0.73,0.96,1.0,1) if self.focus else (0.93,0.93,0.93,1)
            background_normal: ''
            on_text_validate: root.contrastUpdate()

        Button:
            text: "Import Data"
            width: 265
            height: 35
            background_color: (0.96, 0.55, 0.66, 1.0)
            background_normal: ''
            pos: 100, root.height-835

        Button:
            text: "Show Metadata"
            width: 265
            height: 35
            background_color: (0.96, 0.55, 0.66, 1.0)
            background_normal: ''
            pos: 100, root.height-885
            on_press: root.showData()

""")
        return rootwi()

    # When the current window closes, close the other window
    def on_stop(self):
        try:
            p = psutil.Process(os.getpid()+1)
            p.terminate()
        except:
            print os.getpid()

class WinRoot(GridLayout):
    def start(self):
        print "Start"
        Clock.schedule_interval(self.updateImage, 2)

    def updateImage(self):
        # Reassign the source of the image
        print "Hello World"
        self.ids.material.source = "./out.png"
        self.ids.material.reload()

class GBWinApp(App):
    def build(self):
        # Make the title become the file name
        self.title = "example.dm3"
        Builder.load_string("""
<WinRoot>:
    orientation:'vertical'

    GridLayout:
        padding:0

        Image:
            size_hint_y: None
            source:"./material.png"
            id: material
            height: 627
            width: 665
            keep_ratio: False
            allow_stretch: True

        Image:
            size_hint_y: None
            source:"./Images/rectangle.jpg"
            id: material
            height: 7
            width: 70
            pos: 25, 15
            keep_ratio: False
            allow_stretch: True

        Label:
            id: relativeSize
            text: "1 " + u'\u03BC' + "m"
            font_size: 20
            pos: 0, -15
            color: (1,1,1,1)
            
""")
        return WinRoot()

    def on_start(self):
        #WinRoot().start()
        pass
    
    # When the current window closes, close the other window
    def on_stop(self):
        try:
            p = psutil.Process(os.getpid()-1)
            p.terminate()
        except:
            print os.getpid()

    

def open_window():
    GBWinApp().run()

def open_app():
    GBApp().run()

if __name__ == "__main__":
    a = Process(target=open_app)
    b = Process(target=open_window)
    Config.set('graphics', 'position', 'custom')
    Config.set('graphics', 'left', 0)
    Config.set('graphics', 'top',  0)
    Config.set('graphics', 'width', '1280')
    Config.set('graphics', 'height', '960')
    a.start()
    time.sleep(0.04) # This ensures that the second window appears on top
    Config.set('graphics', 'left', 500)
    Config.set('graphics', 'top',  300)
    Config.set('graphics', 'width', '665')
    Config.set('graphics', 'height', '627')
    Config.set('graphics', 'window_state', 'maximized')
    Config.set('graphics','resizable', 0)
    b.start()