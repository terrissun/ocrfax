'''
starter code for 
drawing interactive 
rectangle
'''
import matplotlib
from matplotlib import pyplot as plt
import matplotlib.image as mpimg
import sys
from kivy.app import App
from kivy.garden.matplotlib import FigureCanvasKivyAgg
from kivy.uix.boxlayout import BoxLayout
import numpy as np
from matplotlib.patches import Rectangle

        
class MainApp(App):
    def build(self):
        """
        some initialization
        Args:
            rect: a dummy rectangle, whose width and height will be reset trigger by user event
            x0, y0: mouse click location
            x1, y1: mouse release location
            canvas: FigureCanvasKivyAgg object. Note that I'm using this back end right now 
            as the FigureCanvas backend has bug with plt.show()
            selectors: store user-drawn rectangle data
            offsetx: translation of origin on x direction
            offsety: translation of origin on y direction
        """
        self.selectors = []
        img = mpimg.imread(sys.argv[1])
        self.fig, self.ax = plt.subplots(1)
        plt.imshow(img)
        width, height = self.fig.canvas.get_width_height()
        pxorigin = self.ax.transData.transform([(0,0)])
        self.offsetx = pxorigin[0][0]
        self.offsety = height - pxorigin[0][1]
        print ('offsetx, offsety', self.offsetx, self.offsety)
        self.rect = Rectangle((0,0),1,1)
        self.rect.set_fill(False)
        self.rect.set_edgecolor('b')
        self.x0 = None
        self.y0 = None
        self.x1 = None
        self.y1 = None
        self.canvas = FigureCanvasKivyAgg(plt.gcf()) # get the current reference of plt
        box = BoxLayout()
        self.ax.add_patch(self.rect) # attach our rectangle to axis
        self.canvas.mpl_connect("button_press_event", self.on_press)
        self.canvas.mpl_connect("button_release_event", self.on_release)
        box.add_widget(self.canvas)
        return box

    def on_press(self, event):
        """
        record user click location
        """
        self.x0 = event.xdata
        self.y0 = event.ydata
        print ('x0, y0', self.x0, self.y0)

    def on_release(self, event):
        """
        record user mouse release location
        """
        self.x1 = event.xdata
        self.y1 = event.ydata
        self.rect.set_width(self.x1 - self.x0)
        self.rect.set_height(self.y1 - self.y0)
        self.rect.set_xy((self.x0, self.y0))
        xy_pixels = self.ax.transData.transform(np.vstack([self.x0, self.y0]).T)
        px, py = xy_pixels.T
        width, height = self.fig.canvas.get_width_height()
        # transform from origin on lower left to orgin on upper right
        py = height - py
        # account for translation factor
        px -= self.offsetx
        py -= self.offsety
        self.selectors.append([px, py, abs(self.x1 - self.x0), abs(self.y1 - self.y0)])
        print ('your rectangle', px, py, abs(self.x1 - self.x0), abs(self.y1 - self.y0))
        self.canvas.draw()
    
if __name__ == "__main__":
    app = MainApp()
    app.run()
  
