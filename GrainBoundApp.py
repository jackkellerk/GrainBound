#To run the Kivy application: 

import kivy
kivy.require('1.11.1') #current kivy version

from kivy.app import App
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from functools import partial
from kivy.uix.textinput import TextInput


class GBApp(App):
    def build(self):
        return Button(text="Welcome to GrainBound!", background_color=(176,224,230))

if __name__ == "__main__":
    GBApp().run()