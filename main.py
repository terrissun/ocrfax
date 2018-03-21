# -*- coding: utf-8 -*-
"""
Program: main.py
Author: MERS

The purpose of this module is to serve as the launching point for the entirety of the Faxxine
program. Currently, the program is run via the terminal, by entering::

        $ python3 main.py

This module serves as the central link between all of the other modules, and as the controller
in the Model-View-Controller (MVC) format.

Properties of this module has been defined in kivy language in MainApp.kv.

Todo:
    * Debug layout differences between OS X and Linux
    * Create notifications dynamically from PDFs instead of from text inputs.
    * Better HiDPI logic
"""
import platform
import os
import getpass
import datetime

# App Basics
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.core.window import Window

# Popups
from kivy.uix.modalview import ModalView


# Notifications Panel
from kivy.uix.recycleview import RecycleView
from kivy.uix.recyclegridlayout import RecycleGridLayout
from kivy.properties import BooleanProperty # pylint: disable=no-name-in-module
from kivy.uix.recycleview.layout import LayoutSelectionBehavior
from kivy.uix.recycleview.views import RecycleDataViewBehavior
from kivy.uix.behaviors import FocusBehavior

# Custom Modules
import status.status_tab as status_tab
import templates.templates_tab as templates_tab
import settings_tab
import watcher
import templates.pdfdisplay
import templates.template
import templates.pdftoimage
import ocr.ocrscan as ocrscan



# Resolution
os.environ['KIVY_METRICS_DENSITY'] = '1'
if platform.system() == "Darwin":  # PATCH CODE JUST TO LET RONGRONG RUN, NEED TO FIX
    Window.size = (512, 384)
else:
    Window.size = (1024, 768)


class Controller(BoxLayout):
    """The root object for the application, which links to all the other modules.

    As this application utilizes the MVC design pattern, this Controller class appropriately
    fills the role of controller in that pattern.

    Items prefixed by "self.ids" can be found in the main.kv file, under the Controller section.

    Attributes:
        default_template_location (str): The folder location where templates are stored
        default_file_location (str): The default location for the file chooser when loading a PDF
        notifications_panel (NotificationsPanel): The GUI element which displays notifications.
        notification_handler (NotificationHandler): Stores and handles Notification objects.
        watcher (Watcher): The watchfolder program.
        templates_page (TemplatesStartPage): The initial layout of the Templates tab in the GUI.
        pdf_display (PDFDisplay): The Templates tab layout which displays PDFs.
    """
    #TODO: Update this info section

    def __init__(self):
        """Initializes controller class."""
        super(Controller, self).__init__() # Must pass the super to properly set up window

        # create the settings tab
        self.settings_tab = settings_tab.SettingsTab(self)
        self.ids.settings_tab.add_widget(self.settings_tab)

        # create the status tab
        self.status_tab = status_tab.StatusTab(self)
        self.ids.status_tab.add_widget(self.status_tab)

        # create the templates tab
        self.templates_tab = templates_tab.TemplatesTab(self)
        self.ids.templates_tab.add_widget(self.templates_tab)


        # Set up watchfolder
        self.watcher = watcher.Watcher()

        # register this controller with the watchfolder so the watchfolder can contact it
        self.watcher.register_observer_program(self)
        self.watcher.run()

    def notify(self, notification_type, notification_message):
        """Allows the watchfolder to notify main."""
        if notification_type == "success":
            self.status_tab.add_notification(datetime.datetime
                                             .now()
                                             .strftime("%B %d, %Y at %I:%M%p"),
                                             "System", None, "Success",
                                             notification_message)
        elif notification_type == "failure":
            self.status_tab.add_notification(datetime.datetime
                                             .now()
                                             .strftime("%B %d, %Y at %I:%M%p"),
                                             "System", None, "Failure",
                                             notification_message)

    def estimateAffine(self, points1, points2):
        return ocrscan.estimateAffine(points1, points2)

    def check_setting(self, key):
        return self.settings_tab.get_setting(key)

'''
SelectableRecycleGridLayout
'''
class SelectableRecycleGridLayout(FocusBehavior, LayoutSelectionBehavior,
                                  RecycleGridLayout):
    ''' Adds selection and focus behaviour to the view. '''


'''
SelectableLabel
The basics for each individual label
'''
class SelectableLabel(RecycleDataViewBehavior, Label):
    ''' Add selection support to the Label '''
    index = None
    selected = BooleanProperty(False) # not selected by default
    selectable = BooleanProperty(True) # selectable by default

    def refresh_view_attrs(self, rv, index, data):
        ''' Catch and handle the view changes '''
        self.index = index
        return super(SelectableLabel, self).refresh_view_attrs(
            rv, index, data)

    def on_touch_down(self, touch):
        ''' Add selection on touch down '''
        if super(SelectableLabel, self).on_touch_down(touch):
            return True
        if self.collide_point(*touch.pos) and self.selectable:
            return self.parent.select_with_touch(self.index, touch)

    def apply_selection(self, rv, index, is_selected):
        ''' Respond to the selection of items in the view. '''
        self.selected = is_selected
        if is_selected:
            print("selection changed to {0}".format(rv.data[index]))
        else:
            print("selection removed for {0}".format(rv.data[index]))


"""
Main Application
 Attributes:
     build: will be invoked once when the app is started
"""
class MainApp(App):
    def build(self):
        #self.load_kv('./main.kv')
        self.title = "Faxxine 0.3 alpha edition"
        return Controller()

def main():
    app = MainApp()
    app.run()

if __name__ == "__main__":
    main()
