from kivy.app import App
from kivy.garden.matplotlib.backend_kivyagg import FigureCanvas
from matplotlib import pyplot as plt
import matplotlib.image as mpimg
import matplotlib.patches as patches
import numpy as np
import sys
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout

'''
give (x,y) coordinate in display coordinate system. lower left = (0,0)
draw a bounding box
return a rectangle patch
'''
'''
assume (x1, y1) lower left and (x2, y2) upper right
'''
boxes = []
def drawbox(x1, y1, x2, y2):
    print ('drawing rectangle')
    width = abs(x2 - x1)
    height = abs(y2 - y1)
    rect = patches.Rectangle((x1,y1),width,height,linewidth=1,edgecolor='r',facecolor='none')
    return rect

'''
print mouse position in display coordinate
'''
def onclick(event):
    print ("add to queue: x: %.2f, y: %.2f" % (event.x, event.y))   

'''
debugging purpose...
'''
def on_enter(instance):
    print ('the widget has value',instance.text)

'''
draw a rectangle after button click
based on text inputs. assume user enters (x1, y1)--> lower left
(x2, y2) --> upper right
'''
def updateGraph(instance):
    global boxes
    rect = drawbox(int(textinput1.text),int(textinput2.text),int(textinput3.text),int(textinput4.text))
    ax.add_patch(rect)
    boxes.append(rect)
    canvas.draw()

'''
remove all boxes drawn on the canvas
'''
def recoverGraph(instance):
    for box in boxes:
        box.remove()
    canvas.draw()
    
class TestApp(App):
    def build(self):
        global fig, ax, textinput1, textinput2, textinput3, textinput4, canvas
        fig,ax = plt.subplots(1)
        plt.imshow(img)
        box = BoxLayout()
        canvas = FigureCanvas(figure = fig)
        box.add_widget(canvas)
        fig.canvas.mpl_connect('button_press_event', onclick)
        # some widgets
        textinput1 = TextInput(text = "x1", multiline = False, size_hint = (0.7, None), height = 60)
        textinput1.bind(on_text_validate = on_enter)
        textinput2 = TextInput(text = "y1", multiline = False, size_hint = (0.7, None), height = 60)
        textinput2.bind(on_text_validate = on_enter)
        textinput3 = TextInput(text = "x2", multiline = False, size_hint = (0.7, None), height = 60)
        textinput3.bind(on_text_validate = on_enter)
        textinput4 = TextInput(text = "y2", multiline = False, size_hint = (0.7, None), height = 60)
        textinput4.bind(on_text_validate = on_enter)
        box.add_widget(textinput1)
        box.add_widget(textinput2)
        box.add_widget(textinput3)
        box.add_widget(textinput4)
        button1 = Button(text = 'update', size_hint = (0.7, None), height = 60)
        box.add_widget(button1)
        button1.bind(on_press = updateGraph)
        button2 = Button(text = 'recover', size_hint = (0.7, None), height = 60)
        box.add_widget(button2)
        button2.bind(on_press = recoverGraph)
        canvas.draw()
        return box

if __name__ == "__main__":
    # read image from command line
    img = mpimg.imread(sys.argv[1])
    app = TestApp()
    app.run()
