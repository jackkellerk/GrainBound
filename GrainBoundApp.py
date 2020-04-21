# <----Summary---->
# To go to python 2.7 'source C:/Python27/temp-python/Scripts/activate' then 'python GrainBoundApp.py'
# For clients, make an install bash file to install python 2.7 for them and all of the dependencies in my current python 2.7 version. Make sure about this because this took forever!
# <----End of Summary---->


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
from kivy.graphics import Color, Rectangle
# from kivy.garden.matplotlib.backend_kivyagg import FigureCanvasKivyAgg This breaks multiprocessing

import cv2
import numpy as np
import os
import multiprocessing
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
plt.savefig("material.png", bbox_inches='tight')

# Read the image in cv2
img = cv2.imread("./material.png", 0)

# This creates the plot for the historgram
#plt.matshow(dm3f)
plt.ylabel("Number of Pixels")
plt.xlabel('Grey Levels')
#<----End of code that runs when GBApp starts---->


# TODO: Remove Gamma (unless you can figure it out), and then for the metadata show dimension size and other data, and on the image show magnification

class rootwi(GridLayout):
    #def showData(self):
        #execfile('auxillaryWindow.py')

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
            plt.clf()
            plt.plot()
            for child in self.ids.histogram.children:
                self.ids.histogram.remove_widget(child)
            self.ids.histogram.add_widget(FigureCanvasKivyAgg(plt.gcf()))

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

class WinRoot(Widget):
    pass


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

class GBWinApp(App):
    def build(self):
        # Make the title become the file name
        self.title = "example.dm3"
        Builder.load_string("""""")
        return WinRoot()

def open_window():
    GBWinApp().run()

def open_app():
    GBApp().run()

if __name__ == "__main__":
    a = multiprocessing.Process(target=open_app)
    b = multiprocessing.Process(target=open_window)
    a.start()
    b.start()