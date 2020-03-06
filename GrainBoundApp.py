#To go to python 2.7 'source C:/Python27/temp-python/Scripts/activate' then 'python GrainBoundApp.py'
#For clients, make an install bash file to install python 2.7 for them and all of the dependencies in my current python 2.7 version. Make sure about this because this took forever!

import kivy
kivy.require('1.10.1') #current kivy version

from kivy.app import App

from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.uix.image import AsyncImage

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

#TODO fix the graphics because I ruined it :(
#https://kivy.org/doc/stable/api-kivy.uix.slider.html

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

        Button:
            text: "Imaging"
            pos: root.width-160, root.height-85
            width: 150
            height: 75
            background_color: (0.96, 0.55, 0.66, 1.0)
            background_normal: ''

        Label:
            text: "Data Menu"
            font_size: 30
            color: (0,0,0,1)
            pos: 100, root.height-300
        
        Button:
            text: "Type 1"
            pos: 80, root.height-400
        Button:
            text: "Type 2"
            pos: 200, root.height-400
        Button:
            text: "Type 3"
            pos: 320, root.height-400

        Label:
            text: "Which questions would you like to ask about the data?"
            font_size: 30
            color: (0,0,0,1)
            pos: 350, root.height-550
        
        Button:
            text: "Question 1 about data..."
            width: 400
            height: 100
            pos: 80, root.height-650
        Button:
            text: "Question 2 about data..."
            width: 400
            pos: 80, root.height-750
        Button:
            text: "Question 3 about data..."
            width: 400
            pos: 80, root.height-850

        Button:
            text: "Run!"
            width: 150
            height: 75
            background_color: (0.96, 0.55, 0.66, 1.0)
            background_normal: ''
            pos: root.width-160, 10

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
    pass

class MyApp(App):
    def build(self):
        return rootwi()


class GBApp(App):
    def build(self):
        return rootwi()

    #def build(self):   
        #return Image(source='/Users/nkt/Desktop/GrainBound/GrainBound_Logo.png')
        #Label(text="GrainBound", font_size=50)
        #return Button(text="Welcome to GrainBound!", font_size=50, background_color=(175,238,238))


if __name__ == "__main__":
    GBApp().run()