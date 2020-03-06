#To go to python 2.7 'source C:/Python27/temp-python/Scripts/activate' then 'python GrainBoundApp.py'
#For clients, make an install bash file to install python 2.7 for them and all of the dependencies in my current python 2.7 version. Make sure about this because this took forever!

import kivy
kivy.require('1.10.1') #current kivy version

# For Image contrast, brightness, gamma changing
import cv2
import numpy as np
import os

from kivy.app import App

from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.uix.image import AsyncImage
from kivy.uix.textinput import TextInput 

from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout

from kivy.lang import Builder
from kivy.base import Builder
from kivy.properties import StringProperty
from kivy.graphics import Color, Rectangle

#For DM3
import DM3lib as dm3

dm3f = dm3.DM3("example.dm3")
print dm3f.info

Builder.load_string("""
<rootwi>:
    orientation:'vertical'

    GridLayout:
        padding:5

        canvas:
            Rectangle:
                source:"/Users/nkt/Desktop/GrainBound/whitebg.png"
                pos: 0, 0
                size: root.width, root.height

        Image:
            size_hint_y: None
            source:"./GrainBound_Logo.png"
            width: 300
            allow_stretch: True
            pos: 50, root.height-150

        Image:
            size_hint_y: None
            source:"./logo_graphic.png"
            height: 225
            width: 225
            pos: 215, root.height-230

        Image:
            size_hint_y: None
            source:"./material.jpg"
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
            min: 0
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

        Label:
            id: gammaLabel
            text: "Gamma"
            pos: 90, root.height-570
            color: (0,0,0,1)

        Slider:
            id: gammaSlider
            min: 0
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
            min: 0
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

""")

class CustomLayout(GridLayout):
    def __init__(self, **kwargs):
        # make sure we aren't overriding any important functionality
        super(CustomLayout, self).__init__(**kwargs)

        with self.canvas.before:
            Color(1, 1, 1, 1)  # green; colors range from 0-1 instead of 0-255
            self.rect = Rectangle(size=self.size, pos=self.pos)

        self.bind(size=self._update_rect, pos=self._update_rect)

    def _update_rect(self, instance, value):
        self.rect.pos = instance.pos
        self.rect.size = instance.size


class rootwi(GridLayout):

    def adjust_gamma(image, gamma=1.0):

        invGamma = 1.0 / gamma
        table = np.array([((i / 255.0) ** invGamma) * 255
            for i in np.arange(0, 256)]).astype("uint8")

        return cv2.LUT(image, table)

    def contrastUpdate(self):
        try:
            # Make sure the input is a float
            self.ids.contrastSlider.value = float(self.ids.contrastTextInput.text)

            # Edit the image
            img = cv2.imread("material.jpg")
            alpha = (2.0 * (self.ids.contrastSlider.value / 100)) + 1.0 # Contrast control (1.0-3.0)
            adjusted = cv2.convertScaleAbs(img, alpha=alpha, beta=self.ids.brightnessSlider.value)
            cv2.imwrite("./out.png", adjusted)

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
            img = cv2.imread("material.jpg")
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
            img = cv2.imread("material.jpg")
            gamma = 0.2 #self.ids.gammaSlider.value / 100 # Contrast control (1.0-3.0)
            adjusted = adjust_gamma(img, gamma=gamma)
            cv2.imwrite("./out.png", adjusted)

            # Reassign the source of the image
            self.ids.material.source = "./out.png"
            self.ids.material.reload()
        except:
            # If input is not a float, reset text to original value
            self.ids.gammaTextInput.text = str(self.ids.gammaSlider.value)

class MyApp(App):
    def build(self):
        # Eventually make a method here to delete the temp directory
        return rootwi()

class GBApp(App):
    def build(self):
        return rootwi()

if __name__ == "__main__":
    GBApp().run()