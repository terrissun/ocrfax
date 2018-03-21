'''
templates_tab.py
'''
import os

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.recycleview import RecycleView

# Filechooser
from kivy.uix.filechooser import FileChooserIconView

# Popups
from kivy.uix.modalview import ModalView

import templates.template as template
from . import pdftoimage
from . import pdfdisplay

class TemplatesTab(BoxLayout):

    def __init__(self, controller, **kwargs):

        super(TemplatesTab, self).__init__(**kwargs)
        self.controller = controller
        self.templates_page = TemplatesStartPage(self.controller, self)  # create the initial dynamic layout
        self.ids.templates_tab.add_widget(self.templates_page) # add to the templates tab
        self.pdf_display = None
        self.position_dependent_keywords = None


    # Templates functions

    def launch_load_file_chooser(self, load_type):
        """Launches the file chooser GUI element.

        The default folder location of the file chooser is dependent upon the load_type argument,
        and is parsed within the LoadFileChooserPopup class itself.

        Args:
            load_type (str): What type of file you are trying to load. There are two types:

                "pdf_loader": For choosing a PDF.
                "template_loader": For choosing a Template.
        """
        self.load_file_chooser = LoadFileChooserPopup(self.controller, self, load_type)
        self.load_file_chooser.open()

    def load_template_creator(self, path, load_type):
        print("Path is {}".format(path))
        if load_type == "pdf_loader":
            # loads the PDF display with the appropriate converted PDF images
            self.templates_page.load_pdf(path)
            self.templates_page.ids.mark_keywords_for_identification_button.disabled = False
        elif load_type == "template_loader":
            self.ids.templates_tab.content.clear_widgets() # clear the tab
            loaded_template = template.load_from_file(path)
            self.templates_page = TemplateCreationPage(self.controller, loaded_template) # create PDF display
            self.ids.templates_tab.add_widget(self.templates_page) # add the PDF display

    def close_template_creation_panel(self):
        self.ids.templates_tab.clear_widgets() # clear the tab
        self.templates_page = TemplatesStartPage(self.controller, self)  # create the initial dynamic layout
        self.ids.templates_tab.add_widget(self.templates_page) # add to the templates tab


    def add_to_identification_keywords(self, boxes, popup_img_boundaries):
        self.templates_page.position_dependent_keyword_panel.update_data(boxes)
        # get the transformation from the popup panel to the template preview window
        preview_page = self.templates_page.pdf_display
        preview_img_boundaries = preview_page.get_image_boundaries()
        affine_transformation = self.controller.estimateAffine(popup_img_boundaries, preview_img_boundaries)
        self.position_dependent_keywords = preview_page.update_canvas(affine_transformation,
                                                                      boxes)


class TemplatesStartPage(BoxLayout):
    '''Controls the functionality of the templates tab.

    Because the templates tab has a number of different views/layouts, it requires
    additional functionality to save/load them and rearrange the tab. This is one of
    the possible views for the templates tab: the Start Page. This allows the user
    to choose whether to create a new template or to work on an existing one.

    Attributes:
        controller (Controller): A reference to the controller.
    '''

    def __init__(self, controller, templates_tab, **kwargs):
        # initialization of start page on program load
        super(TemplatesStartPage, self).__init__(**kwargs)
        self.controller = controller
        self.templates_tab = templates_tab

    def new_template_popup(self):
        # create the dialog box which allows you to name the template you are creating
        NewTemplatesPopup(self.controller, self.templates_tab).open()

    def load_template_popup(self):
        # brings up a file chooser to choose the template to load
        LoadFileChooserPopup(self.controller, self.templates_tab, "template_loader").open()


'''
NewTemplatesPopup
The popup window which allows you to name your template. If you choose to name the template and click OK, it
will load the template creation view panel.
'''
class NewTemplatesPopup(ModalView):
    def __init__(self, controller, templates_tab, **kwargs):
        super(NewTemplatesPopup, self).__init__(**kwargs)
        self.ids.new_templates_input_name_box.focus = True
        self.controller = controller
        self.templates_tab = templates_tab

    def prepare_new_template_panel(self):
        # create the PDF display
        input_text = self.ids.new_templates_input_name_box.text
        if input_text == "":
            # don't allow blank template names
            self.ids.new_templates_error_text.text = ("Error: you must enter a valid filename "
                                                      "to continue.")
            self.ids.new_templates_input_name_box.focus = True
        elif os.path.isfile(self.controller.check_setting('DTL') + "/"
                            + input_text + ".template"):
            # check if there is a file with that name already
            self.ids.new_templates_error_text.text = ("Error: there is already a file named "
                                                      "{}.template.".format(input_text))
            self.ids.new_templates_input_name_box.focus = True
        else:
            new_template = template.Template(input_text,
                                                       self.controller.check_setting('DTL')
                                                       + "/" + input_text + ".template")
            # create the PDF display
            self.templates_tab.templates_page = TemplateCreationPage(self.controller, self.templates_tab, new_template)

            # clear the tab
            self.templates_tab.ids.templates_tab.clear_widgets()

            # # add the Template Creation Page
            self.templates_tab.ids.templates_tab.add_widget(self.templates_tab.templates_page)

            # close the popup
            self.dismiss()

class TemplateCreationPage(BoxLayout):

    def __init__(self, controller, templates_tab, template, **kwargs):
        super(TemplateCreationPage, self).__init__(**kwargs)
        self.controller = controller
        self.templates_tab = templates_tab
        self.pdf_display = None
        self.template = template
        self.ids.template_title.text = template.get_name() + ".template"
        self.test = None
        self.directory = None
        self.position_dependent_keyword_panel = PositionDependentKeywordPanel()
        self.ids.position_dependent_panel.add_widget(self.position_dependent_keyword_panel)

    def launch_file_chooser(self):
        self.templates_tab.launch_load_file_chooser("pdf_loader")

        # if loaded tempalte
        # self.pdf_display.update_templates_tab_from_loaded_template()

    def load_pdf(self, directory):
        self.ids.templates_box.clear_widgets()
        self.pdf_display = pdfdisplay.PDFDisplay(self.controller,
                                                           self.template, "preview")
        self.pdf_display.load_pdf(directory)
        self.directory = directory
        self.ids.templates_box.add_widget(self.pdf_display)

    #TODO: popup warning if panel hasn't been saved
    def close_template_creation_panel(self):
        self.ids.mark_keywords_for_identification_button.disabled = True
        self.templates_tab.close_template_creation_panel()

    def save_template(self):
        self.template.save()
        self.template_saved = True

    def update_templates_tab_from_loaded_template(self):
        for i in range(0, self.template.keyword_list_length("id")):
            self.ids.identification_keywords_title.text += (" {},"
                                                            .format(self.template
                                                                    .keyword_at_index("id", i)
                                                                    .get_text()))
        self.ids.identification_keywords_title.text = (self.ids
                                                       .identification_keywords_title
                                                       .text)[:-1]

        for i in range(0, self.template.keyword_list_length("field_keyword")):
            self.ids.field_keywords_title.text += (" {},"
                                                   .format(self.template
                                                           .keyword_at_index("field_keyword", i)
                                                           .get_text()))

        self.ids.field_keywords_title.text = (self.ids.field_keywords_title.text)[:-1]

        for i in range(0, self.template.keyword_list_length("extraction_field")):
            self.ids.extraction_fields_title.text += (" {},"
                                                      .format(self.template
                                                              .keyword_at_index("extraction_field",
                                                                                i)
                                                              .get_text()))
        self.ids.extraction_fields_title.text = (self.ids.extraction_fields_title.text)[:-1]

    # Position-Independent Keywords
    def add_position_independent_keyword(self):
        pass
        # Grab the word, the page number, and how many are on that page from the text fields.

        # Go to the data parsed from Tesseract of that page, and check that for the
        # given PAGE_COUNT, WORD appears COUNT number of times.

        # If it does, add the position independent keyword to the scrollview

        # If it does not, create a dialog window informing the user of the error.

    def add_position_dependent_keyword(self):
        if self.directory is None:
            AlertPopup("You must first load a PDF before you can add keywords.").open()
        else:
            # open modal window which full-screens the PDF
            PDFPopup(self.controller, self.templates_tab, self.directory).open()
            # - allows bounding boxes to be drawn/saved

    def get_preview_image_boundaries(self):
        return self.pdf_display.get_image_boundaries()


class PositionDependentKeywordPanel(RecycleView):
    def __init__(self, **kwargs):
        # self.size = 0
        super(PositionDependentKeywordPanel, self).__init__(**kwargs)

    # def on_scroll_start(self, touch):
        # super(PositionDependentKeywordPanel, self).on_scroll_start(touch)

    # def on_scroll_move(self, touch):
    #     if self.size != 0:
    #         super(PositionDependentKeywordPanel, self).on_scroll_move(touch)

    # def on_scroll_end(self, touch):
    #     if self.size != 0:
    #         super(PositionDependentKeywordPanel, self).on_scroll_end(touch)

    def update_data(self, boxes):
        # parses the data provided in values into an appropriate value for self.data
        box_data_list = []
        for box in boxes:
            box_data_list.append({'text':box.get_text()})
            print(box.get_text())
        self.data = box_data_list



'''
LoadFileChooserPopup
The popup window which displays a file chooser system, implemented through Kivy
'''
class LoadFileChooserPopup(ModalView):
    def __init__(self, controller, templates_tab, load_type, **kwargs):
        super(ModalView, self).__init__(**kwargs)
        self.controller = controller
        self.templates_tab = templates_tab
        self.load_type = load_type
        if load_type == "pdf_loader":
            self.filechooser = FileChooserClass(
                self,
                filters=[lambda folder, filename: filename.endswith('.pdf')])
        elif load_type == "template_loader":
            self.filechooser = FileChooserClass(
                self,
                filters=[lambda folder, filename: filename.endswith('.template')])
        self.ids.filechooser_box.add_widget(self.filechooser)
        if load_type == "pdf_loader":
            self.filechooser.path = self.controller.check_setting('DFL')
        elif load_type == "template_loader":
            self.filechooser.path = self.controller.check_setting('DTL')



    def load(self):
        # sends the file to the right location/calls the appropriate module
        # with open(os.path.join(path, filename[0])) as stream:
        #     self.text_input.text = stream.read()
        print(self.filechooser.selection[0])
        if self.load_type == "pdf_loader":
            # code should call here imagemagick module to convert the pdf to images,
            # then save the PDF to a temp folder
            imgFolder = pdftoimage.convert_pdf(self.filechooser.selection[0])

            self.templates_tab.load_template_creator(imgFolder, self.load_type)

        elif self.load_type == "template_loader":
            # send the template file location
            self.templates_tab.load_template_creator(self.filechooser.selection[0], self.load_type)

        self.dismiss()


    def go_up(self):
        # goes up a directory
        if self.filechooser.path != "/": # don't try to go up past root
            path_split = self.filechooser.path.split("/")
            new_path = ""
            if len(path_split) is 2:
                new_path = "/"
            else:
                for i in range(1, len(path_split)-1):
                    new_path = new_path + "/" + path_split[i]
            self.filechooser.path = new_path # set the new path


'''
FileChooserClass
A customized file chooser class, which utilizes the File Chooser Icon View (pictures of folders)
Necessary because there is no other way to update the title every time the directory changes
(to update the "Current Directory:" title)
This is the actual file chooser; LoadFileChooserPopup is the modal view window that contains this.
'''
class FileChooserClass(FileChooserIconView):
    def __init__(self, dialog, **kwargs):
        super(FileChooserIconView, self).__init__(**kwargs)
        self.dialog = dialog # the popup window itself

    def _update_files(self, *args, **kwargs):
        super(FileChooserIconView, self)._update_files(*args, **kwargs)
        # update the title with the current working directory
        self.dialog.ids.load_dialog_title.text = "  Current Directory: " + self.path

class PDFPopup(ModalView):

    def __init__(self, controller, templates_tab, directory, **kwargs):
        super(PDFPopup, self).__init__(**kwargs)
        self.controller = controller
        self.templates_tab = templates_tab
        self.directory = directory
        self.pdf_display = pdfdisplay.PDFDisplay(self.controller,
                                                           None,
                                                           "position_dependent_keywords")
        self.ids.popup_pdf_location.add_widget(self.pdf_display)
        self.pdf_display.load_pdf(self.directory)

        # get the transformation from template preview panel to popup window
        affine_transformation = self.controller.estimateAffine((self.templates_tab.templates_page.pdf_display
                                                        .get_image_boundaries()),
                                                       self.pdf_display.get_image_boundaries())

        # transform the position dependent keyword boxes
        pd_keywords = self.pdf_display.update_canvas(affine_transformation,
                                                     self.templates_tab.position_dependent_keywords)

        # add it to the list of boxes
        self.pdf_display.add_to_box_list(pd_keywords)


    def add_boxes(self):
        boxes = self.pdf_display.get_boxes()
        print("Boxes are {}".format(boxes))
        self.templates_tab.add_to_identification_keywords(boxes,
                                                       self.pdf_display.get_image_boundaries())
        self.dismiss()



class AlertPopup(ModalView):

    def __init__(self, message, **kwargs):
        super(AlertPopup, self).__init__(**kwargs)
        self.ids.message_box.text = message
