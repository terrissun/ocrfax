'''
pdfdisplay.py
'''
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.widget import Widget
# from kivy.graphics import *
from kivy.graphics import Color, Ellipse, Line
import matplotlib
matplotlib.use("module://kivy.garden.matplotlib.backend_kivyagg")
from kivy.garden.matplotlib import FigureCanvasKivyAgg
from matplotlib import pyplot as plt
import matplotlib.image as mpimg
# from matplotlib.patches import Rectangle
import matplotlib.patches as patches

from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
import sys
import numpy as np
import os
from kivy.core.window import Window
from PIL import Image
import copy


# Custom Modules
import status.notificationhandler
import ocr.ocrscan as ocrscan

# Notifications Panel
from kivy.uix.recycleview import RecycleView
from kivy.uix.recyclegridlayout import RecycleGridLayout
from kivy.properties import BooleanProperty
from kivy.uix.recycleview.layout import LayoutSelectionBehavior
from kivy.uix.recycleview.views import RecycleDataViewBehavior
from kivy.uix.behaviors import FocusBehavior
from kivy.uix.recycleview.layout import LayoutSelectionBehavior


# import kivy image
from kivy.uix.image import Image as KivyImage
from kivy.graphics.instructions import InstructionGroup
    
       
class PDFDisplay(BoxLayout):
    """
    PDFDisplay class handles displaying PDF as images functionalities on GUI
    Attributes:
        boxes: a list of rectangles objects drawn
        controller: the overall layout 
        fig, ax: matplotlib object
        pdf_canvas: kivy backend Figure Canvas object 
        templates_text_input: see main.kv; a boxlayout that has all text boxes
        pages: read all images in a folder and store them to a list of numpy array
        pageNum: current page number
    """

    def __init__(self, controller, template, display_type, **kwargs):
        """
        Args:
            param1: controller (obj). Need to pass in a controller object 
        """
        super(PDFDisplay, self).__init__(**kwargs)
        self.controller = controller
        self.template = template
        self.pdf_canvas = PDFCanvas(controller, display_type)
        self.ids.pdf_canvas_area.add_widget(self.pdf_canvas)


    def load_pdf(self, directory):
        # load the first page
        self.pdf_canvas.load_pdf(directory)

    def next_page(self):
        """
        go to the next page when the next page button is pressed
        if the last page is reached, nothing will happen
        """
        self.pdf_canvas.next_page()

    def prev_page(self):
        """
        go to the previous page when the previous page button is pressed
        if the first page is reached, nothing will happen
        """
        self.pdf_canvas.prev_page()

    def get_canvas(self):
        return self.pdf_canvas

    def update_canvas(self, transformation, boxes):
        return self.pdf_canvas.update_canvas(transformation, boxes)

    def clear_page(self):
        self.pdf_canvas.clear_page()

    def get_boxes(self):
        return self.pdf_canvas.get_boxes()

    def get_image_boundaries(self):
        return self.pdf_canvas.get_image_boundaries()

    def add_to_box_list(self, boxes):
        self.pdf_canvas.add_to_box_list(boxes)

class PDFCanvas(Widget):
    def __init__(self, controller, display_type, **kwargs):
        """Initializes controller class."""
        super(PDFCanvas, self).__init__(**kwargs) # Must pass the super to properly set up window
        self.controller = controller
        self.display_type = display_type
        if display_type == "preview":
            self.drawable = False
        elif display_type == "position_dependent_keywords":
            self.drawable = True


    def load_pdf(self, directory):
        # set up the page images of the pdf
        self.pages = []
        self.page_num = 0

        # get the files from the directory
        files = os.listdir(directory)
        self.pages = [os.path.join(directory, x) for x in files if x.endswith('.png')]

        # will sort by 1.png, 2.png, 3.png etc...for each page in the pdf
        self.pages.sort()

        # get the image dimensions
        self.page_dimensions = []
        for page in self.pages:
            image_sample = Image.open(page)
            self.page_dimensions.append(image_sample.size)
        
        # set the background image
        color = (1, 1, 0)
        with self.canvas:
            self.bg = KivyImage(source=(self.pages[self.page_num]), pos=self.pos, size=self.size)
            Color(*color, mode='hsv')

        # bind self.update_bg to changes in position or size, to automatically update the bg image
        self.bind(pos=self.update_bg)
        self.bind(size=self.update_bg)

        # values used for drawing rectangles
        self.x1 = 0
        self.y1 = 0
        self.x3 = 0
        self.y3 = 0

        self.hold = False
        self.move = False

        # set the corners
        self.bottom_left = (self.pos[0], self.pos[1])
        self.bottom_right = (self.pos[0] + self.size[0], self.pos[1])
        self.top_left = (self.pos[0], self.pos[1] + self.size[1])
        self.top_right = (self.pos[0] + self.size[0], self.pos[1] + self.size[1])

        # stores the rectangles that are drawn
        self.rectangles = []

    def update_canvas(self, transformation, boxes):
        with self.canvas:
            if boxes is not None:
                # deep copy the original position dependent keyword boxes
                new_boxes = []
                for rectangle in boxes:
                    new_boxes.append(rectangle.clone()) # cloned lines are added to the canvas

                for rectangle in boxes:
                    rectangle.remove_from_canvas(self.canvas) # remove the original lines from the canvas

                # do the transformation
                for rectangle in new_boxes:
                    rectangle.transform(transformation)

                return new_boxes
            else:
                return None

    def update_canvas_modify_rects(self, transformation, boxes):
        with self.canvas:
            if boxes is not None:
                # do the transformation on the boxes
                for rectangle in boxes:
                    rectangle.transform(transformation)

                return boxes
            else:
                return None

    def add_to_box_list(self, boxes):
        if boxes is not None:
            self.rectangles.extend(boxes)

    def next_page(self):
        """
        go to the next page when the next page button is pressed
        if the last page is reached, nothing will happen
        """
        if self.page_num < len(self.pages) - 1:
            self.page_num += 1
            self.bg.source = self.pages[self.page_num]

    def prev_page(self):
        """
        go to the previous page when the previous page button is pressed
        if the first page is reached, nothing will happen
        """
        if self.page_num > 0:
            self.page_num -= 1
            self.bg.source = self.pages[self.page_num]

    def update_bg(self, *args):
        print("Updating background position from {}, {} to {}, {}".format(self.bg.pos[0], self.bg.pos[1], self.pos[0], self.pos[1]))
        print("Updating background size from {}, {} to {}, {}".format(self.bg.size[0], self.bg.size[1], self.size[0], self.size[1]))
        old_top_left = self.top_left
        old_top_right = self.top_right
        old_bottom_left = self.bottom_left
        old_bottom_right = self.bottom_right
        
        self.bg.pos = self.pos
        self.bg.size = self.size
        self.bottom_left = (self.bg.pos[0] + ((self.size[0] - self.bg.norm_image_size[0]) / 2), self.bg.pos[1])
        self.bottom_right = (self.bottom_left[0] + self.bg.norm_image_size[0], self.bg.pos[1])
        self.top_left = (self.bottom_left[0], self.bottom_left[1] + self.bg.size[1])
        self.top_right = (self.bottom_right[0], self.top_left[1])

        old_coordinates = [old_top_left, old_top_right, old_bottom_left, old_bottom_right]
        new_coordinates = [self.top_left, self.top_right, self.bottom_left, self.bottom_right]

        # get the transformation
        transformation = ocrscan.estimateAffine(old_coordinates, new_coordinates)

        # remove the old rectangles from the canvas or they will appear along with the new ones!
        print("Canvas children before:")
        print(len(self.canvas.children))

        for rectangle in self.rectangles:
            rectangle.remove_from_canvas(self.canvas)

        print("Canvas children after:")
        print(len(self.canvas.children))
        self.rectangles = self.update_canvas_modify_rects(transformation, self.rectangles)
        print("The new rectangles are {}".format(self.rectangles))


        x_pos = self.pos[0] + ((self.size[0]  - self.bg.norm_image_size[0])/ 2)
        y_pos = self.bg.pos[1]

        print("Image position is {}, {}".format(x_pos, y_pos))


    def on_touch_down(self, touch):
        if self.drawable:
            with self.canvas:
                if self.is_inside_image(touch.x, touch.y):
                    self.hold = True
                    print("{}, {}".format(touch.x, touch.y))
                    xp, yp = self.toPixelCoordinates(touch.x, touch.y)
                    print ('pixel coordinates of current touch-down point are {}, {}'.format(xp, yp))
                    Color(0, 0, 0)
                    d = 30.
                    self.x1 = touch.x
                    self.y1 = touch.y

                    touch.ud['line1'] = Line() # left
                    touch.ud['line2'] = Line() # bottom
                    touch.ud['line3'] = Line() # right
                    touch.ud['line4'] = Line() # top

    def on_touch_move(self, touch):
        if self.drawable:
            if self.is_inside_image(touch.x, touch.y):
                if self.hold == True:
                    self.move = True
                    self.x3 = touch.x
                    self.y3 = touch.y
                    x2 = self.x1
                    y2 = self.y3
                    x4 = self.x3
                    y4 = self.y1

                    touch.ud['line1'].points = [self.x1, self.y1, x2, y2] # left side of box
                    touch.ud['line2'].points = [x2, y2, self.x3, self.y3] # bottom side of box
                    touch.ud['line3'].points = [self.x3, self.y3, x4, y4] # right side of box
                    touch.ud['line4'].points = [x4, y4, self.x1, self.y1] # top side of box



    def on_touch_up(self, touch):
        if self.drawable:
            if self.hold == True and self.move == True:
                print("BG image position should be {}".format(self.bottom_left))
                print("BG image size should be {}".format(self.bg.norm_image_size))
                print("Bottom right is {}".format(self.bottom_right))
                print("Top right is {}".format(self.top_right))
                print("Bottom left is {}".format(self.bottom_left))
                print("Top left is {}".format(self.top_left))

                # determine the direction the rectangle was drawn - down-left, down-right, up-left, up-right
                direction = self.determine_rectangle_draw_direction(touch.ud['line1'], touch.ud['line2'], touch.ud['line3'], touch.ud['line4'])

                # if the rectangle is usable
                if direction != "bad_rect":

                    # convert the lines so that it is as if the user drew the rectangle down-right
                    self.convert_lines_to_down_right(direction, touch.ud['line1'], touch.ud['line2'], touch.ud['line3'], touch.ud['line4'])

                    # maintain a direct reference to these lines and their instances on the canvas to make them easy to remove
                    rect_lines = InstructionGroup()
                    rect_lines.add(touch.ud['line1'])
                    rect_lines.add(touch.ud['line2'])
                    rect_lines.add(touch.ud['line3'])
                    rect_lines.add(touch.ud['line4'])
                    new_rect = Rectangle(touch.ud['line1'], touch.ud['line2'], touch.ud['line3'], touch.ud['line4'], rect_lines)
                    new_rect.debug_print()
                    self.rectangles.append(new_rect)
                
                    '''
                    some tests to ensure I've calculated the pixel coordinates correctly
                    uncomment to try out..
                    topLeft -> 0, 0
                    topRight -> 512, 0
                    bottomLeft -> 0, 613
                    bottomRight -> 512, 613
                    
                    topLeftX = self.top_left[0]
                    topLeftY = self.top_left[1]
                    topLeftXp, topLeftYp = self.toPixelCoordinates(topLeftX, topLeftY)
                    print (topLeftXp, topLeftYp)

                    topRightX = self.top_right[0]
                    topRightY = self.top_right[1]
                    topRightXp, topRightYp = self.toPixelCoordinates(topRightX, topRightY)
                    print (topRightXp, topRightYp)

                    bottomLeftX = self.bottom_left[0]
                    bottomLeftY = self.bottom_left[1]
                    bottomLeftXp, bottomLeftYp = self.toPixelCoordinates(bottomLeftX, bottomLeftY)
                    print (bottomLeftXp, bottomLeftYp)

                    bottomRightX = self.bottom_right[0]
                    bottomRightY = self.bottom_left[1]
                    bottomRightXp, bottomRightYp = self.toPixelCoordinates(bottomRightX, bottomRightY)
                    print (bottomRightXp, bottomRightYp)
                    '''
                    
                    # convert to pixel
                    uLx, uLy = self.toPixelCoordinates(new_rect.get_upper_left()[0], new_rect.get_upper_left()[1])
                    lRx, lRy = self.toPixelCoordinates(new_rect.get_lower_right()[0], new_rect.get_lower_right()[1])
                    
                    print ('current rectangles at pixel coordinates')
                    print (uLx, uLy, lRx, lRy)

                    # # need to get the actual image name tho..
                    # # compute shrink ratio
                    vec = ocrscan.get_ratio(self.pages[self.page_num], self.bg.norm_image_size[0], self.bg.norm_image_size[1])
                    print ('shrink ratio')
                    print (vec)
                    adjCoordUL = np.array([uLx, uLy]) * vec
                    adjCoordLR = np.array([lRx, lRy]) * vec
                    startX = adjCoordUL[0]
                    startY = adjCoordUL[1]
                    width = (adjCoordLR - adjCoordUL)[0]
                    height = (adjCoordLR - adjCoordUL)[1]
                    words = ocrscan.get_text_from_box(self.pages[self.page_num], startX, startY - 10, width, height+10)
                    new_rect.set_text(words)
                    new_rect.print()

            self.hold = False
            self.move = False

    def clear_page(self):
        for rectangle in self.rectangles:
            rectangle.clear()
        self.rectangles = []

    def toPixelCoordinates(self, x, y):
        '''
        convert canvas coordinate to pixel coordinates
        where the origin is the uppler left of the canvas
        '''
        a = self.top_left[0]
        b = self.top_left[1]
        width, height = Window.size[0], Window.size[1]
        bp = height - b
        xp = x - a
        yp = height - y - bp
        return int(xp), int(yp)
        

    def toCanvasCoordinates(self, xp, yp):
        '''
        convert pixel coordinates to canvas coordinate
        where the origin is the lower left of the canvas (window)
        '''
        a = self.top_left[0]
        b = self.top_left[1]
        _, height = Window.size[0], Window.size[1]
        bp = height - b
        x = xp + a
        y = height - up - bp
        return int(x), int(y)

    def get_boxes(self):
        return self.rectangles

    def draw_canvas_from_rectangles(self, rectangles):
        with self.canvas:
            for rectangle in rectangles:
                rectangle.redraw(self.canvas)

    def get_image_boundaries(self):
        return [self.top_left, self.top_right, self.bottom_left, self.bottom_right]

    def determine_rectangle_draw_direction(self, line1, line2, line3, line4):
        # the point where the rectangle starts from is (line1.points[0], line1.points[1])
        # the direction is simply the direction the user moves the mouse after clicking
        # down to draw the rectangle
        up_down = None
        left_right = None
        if line1.points[3] > line1.points[1]: # user drew upwards
            up_down = "up"
        elif line1.points[3] < line1.points[1]: # user drew downwards
            up_down = "down"
        else: # user drew completely horizontally, no area
            return "bad_rect"

        if line3.points[0] > line1.points[0]: # user drew right
            left_right = "right"
        elif line3.points[0] < line1.points[0]: # user drew left
            left_right = "left"
        else: # user drew completely vertically, no area
            return "bad_rect"

        return "{}-{}".format(up_down, left_right)

    def convert_lines_to_down_right(self, direction, line1, line2, line3, line4):
        # if the rectangle is drawn down right, it should go from origin to end of line1 (left side) downwards,
        # then to line2 (bottom side) left to right, then to line3 (right side) bottom to top, then to line4
        # (top side) right to left

        # down-right is already ok
        if direction == "down-left":
            # swap left and right lines
            self.swap_lines(line1, line3)

            # flip all lines
            self.flip_line(line1)
            self.flip_line(line2)
            self.flip_line(line3)
            self.flip_line(line4)

        elif direction == "up-left":
            # swap left and right lines
            self.swap_lines(line1, line3)

            # flip bottom and top
            self.flip_line(line2)
            self.flip_line(line4)


        elif direction == "up-right":
            # swap top and bottom lines, no need to flip
            self.swap_lines(line2, line4)

            # flip left and right lines
            self.flip_line(line1)
            self.flip_line(line3)

    def swap_lines(self, line1, line2):
        temp_line_points = [line1.points[0], line1.points[1], line1.points[2], line1.points[3]]
        line1.points = [line2.points[0], line2.points[1], line2.points[2], line2.points[3]]
        line2.points = [temp_line_points[0], temp_line_points[1], temp_line_points[2], temp_line_points[3]]

    def flip_line(self, line):
        line.points = [line.points[2], line.points[3], line.points[0], line.points[1]]

    def is_inside_image(self, x, y):
        if x > self.top_right[0] or x < self.top_left[0]:
            return False
        if y > self.top_left[1] or y < self.bottom_left[1]:
            return False
        return True

class Rectangle():

    def __init__(self, left_line, bottom_line, right_line, top_line, rect_lines):
        self.left_line = left_line
        self.right_line = right_line
        self.top_line = top_line
        self.bottom_line = bottom_line
        self.group = rect_lines
        self.text = ""

    def get_position(self):
        return [self.left_line.points[0], self.left_line.points[3]]

    def get_upper_left(self):
        return [self.left_line.points[0], self.left_line.points[1]]

    def get_lower_right(self):
        return [self.right_line.points[0], self.right_line.points[1]]

    def get_width(self):
        return self.bottom_line.points[2] - self.bottom_line.points[0]

    def get_height(self):
        return self.left_line.points[0] - self.left_line.points[2]

    def get_left_line(self):
        return self.left_line

    def set_text(self, word_array):
        for word in word_array:
            self.text = self.text + word.get_text() + " "

        self.text.strip()

    def set_string(self, string):
        self.text = string

    def get_text(self):
        return self.text

    def print(self):
        print(self.text)

    def redraw(self, canvas_ref):
        print("redrawing lines for rect")
        with canvas_ref:
            Color(0, 0, 0)
            canvas_ref.add(self.left_line)
            canvas_ref.add(self.right_line)
            canvas_ref.add(self.top_line)
            canvas_ref.add(self.bottom_line)
            self.debug_print()
            # canvas_ref.add(Line(points=[100, 100, 500, 500], width=10))

    def clear(self):
        self.left_line.points = []
        self.right_line.points = []
        self.top_line.points = []
        self.bottom_line.points = []

    def transform(self, T):
        print("Starting transform")
        # transform left line
        print("Upper left started as {}, {}".format(self.left_line.points[0], self.left_line.points[1]))
        line_points_1 = self.transform_coordinate_point(T, self.left_line.points[0], self.left_line.points[1])
        line_points_2 = self.transform_coordinate_point(T, self.left_line.points[2], self.left_line.points[3])
        self.left_line.points = [line_points_1[0][0], line_points_1[1][0], line_points_2[0][0], line_points_2[1][0]]
        print("Upper left is now {}, {}".format(self.left_line.points[0], self.left_line.points[1]))
        print("Transformed left line")

        # transform right line
        line_points_1 = self.transform_coordinate_point(T, self.right_line.points[0], self.right_line.points[1])
        line_points_2 = self.transform_coordinate_point(T, self.right_line.points[2], self.right_line.points[3])
        self.right_line.points = [line_points_1[0][0], line_points_1[1][0], line_points_2[0][0], line_points_2[1][0]]
        print("Transformed right line")

        # transform top line
        line_points_1 = self.transform_coordinate_point(T, self.top_line.points[0], self.top_line.points[1])
        line_points_2 = self.transform_coordinate_point(T, self.top_line.points[2], self.top_line.points[3])
        self.top_line.points = [line_points_1[0][0], line_points_1[1][0], line_points_2[0][0], line_points_2[1][0]]
        print("Transformed top line")

        # transform bottom line
        line_points_1 = self.transform_coordinate_point(T, self.bottom_line.points[0], self.bottom_line.points[1])
        line_points_2 = self.transform_coordinate_point(T, self.bottom_line.points[2], self.bottom_line.points[3])
        self.bottom_line.points = [line_points_1[0][0], line_points_1[1][0], line_points_2[0][0], line_points_2[1][0]]
        print("Transformed bottom line")

    # def transform_line(self, T, line):
    #     line_points_1 = self.transform_coordinate_point(T, line.points[0], line.points[1])
    #     line_points_2 = self.transform_coordinate_point(T, line.points[2], line.points[3])
    #     line.points = 

    def transform_coordinate_point(self, T, x, y):
        line_points = [x, y, 1]
        line_points = np.vstack(line_points)
        return np.dot(T, line_points)

    def debug_print(self):
        print("Upper left coordinate is {}, {}".format(self.left_line.points[0], self.left_line.points[1]))
        print("Lower right coordinate is {}, {}".format(self.right_line.points[0], self.right_line.points[1]))

    def clone(self):
        new_left_line = Line()
        new_left_line.points = [self.left_line.points[0], self.left_line.points[1], self.left_line.points[2], self.left_line.points[3]]
        new_right_line = Line()
        new_right_line.points = [self.right_line.points[0], self.right_line.points[1], self.right_line.points[2], self.right_line.points[3]]
        new_top_line = Line()
        new_top_line.points = [self.top_line.points[0], self.top_line.points[1], self.top_line.points[2], self.top_line.points[3]]
        new_bottom_line = Line()
        new_bottom_line.points = [self.bottom_line.points[0], self.bottom_line.points[1], self.bottom_line.points[2], self.bottom_line.points[3]]
        
        rect_lines = InstructionGroup()
        rect_lines.add(new_left_line)
        rect_lines.add(new_right_line)
        rect_lines.add(new_top_line)
        rect_lines.add(new_bottom_line)
        new_rect = Rectangle(new_left_line, new_bottom_line, new_right_line, new_top_line, rect_lines)
        new_rect.set_string(self.get_text())
        return new_rect

    def remove_from_canvas(self, canvas_ref):
        canvas_ref.remove(self.group)