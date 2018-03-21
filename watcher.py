# -*- coding: utf-8 -*-
"""
Program: watcher.py
Author: MERS

The purpose of this module is to control the logic for the watchdog folder,
which monitors a specific folder on the computer for the addition of a PDF.
watcher then converts the PDF to images, scans them using Tesseract,
and provides that informaton back to the main program, which is registered
as an observer.


Todo:
    * Allow ability for user to set watchfolder location in config file
    * Separate out imagemagick functionality into its own module
    * Consider an alternate approach to importing PyPDF2
"""
import sys
import os

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import templates.template
import ocr.ocrscan
import ocr.parser
import shutil
import PyPDF2
import templates.pdftoimage

class Watcher:
    """The outer class to which the functionality in the Handler class is applied..

    Currently, the main purpose of this class is to simply register the main program
    as an observer, then to run the event handler.

    Attributes:
        DIRECTORY_TO_WATCH (str): the directory which is watched for changes
        observer (Observer):
        event_handler (Handler):
    """

    DIRECTORY_TO_WATCH = "watchfolders/watch"

    def __init__(self):
        """Initializes the Watcher program."""
        self.observer = Observer()

    def register_observer_program(self, observer_program):
        """Registers the main program as an observer and creates the event handler."""
        self.event_handler = Handler(observer_program)

    def run(self):
        self.observer.schedule(self.event_handler, self.DIRECTORY_TO_WATCH, recursive=False)
        self.observer.start()


class Handler(FileSystemEventHandler):

    def __init__(self, observer_program):
        self.observer_program = observer_program

    def on_any_event(self, event):
        # Do nothing if a directory is created in the watchfolder
        if event.is_directory:
            return None

        elif event.event_type == 'created':
            fileext = event.src_path[-4:] # check the file extension

            if fileext == '.pdf': # only care if it's a PDF

                backup = self.observer_program.ids.backup_pdfs_checkbox.active


                # if the backup option is checked
                if backup:
                    print("Creating backup")
                    shutil.copy(event.src_path, "watchfolders/backup")


                imgFolder = pdftoimage.convert_pdf(event.src_path)


                # Process the images

                # send the PDF to the parser for processing
                print("Preparing to scan image...")
                pdf = ocrscan.get_word_data('{}/1.png'.format(imgFolder))

                print("Image scanned.")

                # Delete the images - no longer needed
                os.system("rm -r '%s'" %(imgFolder))
                print("Deleted %s" %(imgFolder))


                print(parser.Parser.is_word_at_location('Hudson', 1187, 300, pdf, 10))

                match = parser.Parser.identify_document(pdf, self.observer_program.default_template_location)
                #print("Template Match: {}".format(rc))

                # check if PDF object is valid and what rules apply to it

                        # if so, upload etc.

                        # if not, send to error bin

                if match is not None:
                    print("Match to template: {}.template".format(match.get_name()))
                    shutil.copy(event.src_path, "upload")

                    # Notify the main program with the info it needs
                    self.observer_program.notify("success", "{}".format(match.get_name()))


                else:
                    print("Error: no template match")
                    shutil.copy(event.src_path, "error")
                    # Notify the main program with the info it needs
                    self.observer_program.notify("failure", "No match found.")

                

if __name__ == '__main__':
    w = Watcher()
    w.run()
