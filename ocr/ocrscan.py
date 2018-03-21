from PIL import Image, ImageDraw
import sys
import os
import io
import tesserocr
from tesserocr import PyTessBaseAPI, RIL, PSM, iterate_level
import ocr.pdfpage as pdfpage
import ocr.word as word
import numpy as np
import re

def get_text(img):
	images = Image.open(img)
	text = tesserocr.image_to_text(images)
	print(text)


def get_word_data(img):
	image = Image.open(img, mode='r')
	pdf = pdfpage.PDFPage('folder location', 1)
	with PyTessBaseAPI() as api:
		api.SetImage(image)
		boxes = api.GetComponentImages(RIL.WORD,True) # option for TEXTLINE or SYMBOL (character) as well
		for i,(im,box,_,_)in enumerate(boxes):
			api.SetRectangle(box['x'],box['y'],box['w'],box['h'])
			ocrResult = api.GetUTF8Text()
			conf = api.MeanTextConf()
			doc_word = word.Word(i, box['x'], box['y'], box['w'], box['h'], conf, ocrResult)
			# print ((u"Box[{0}]: x={x}, y={y}, w={w}, h={h}, ""confidence: {1}, text: {2}").format(i, conf, ocrResult, **box))
			pdf.add_word(doc_word)
	pdf.sort_dictionaries()
	return pdf

def get_components_test(img):
	image = Image.open(img)
	with PyTessBaseAPI() as api:
		api.SetImage(image)
		boxes = api.GetComponentImages(RIL.TEXTLINE,True)
		for i,(im,box,_,_)in enumerate(boxes):
			api.SetRectangle(box['x'],box['y'],box['w'],box['h'])
			ocrResult = api.GetUTF8Text()
			conf = api.MeanTextConf()
			print ((u"Box[{0}]: x={x}, y={y}, w={w}, h={h}, ""confidence: {1}, text: {2}").format(i, conf, ocrResult, **box))

def get_text_from_box(fn, x, y, w, h):
        """
        Functionality: given the bounding box, find the word(s) within; assumes the box is good enough
        For debugging purpose, this function will draw the bounding box where Tesseract sees the word 
        and save to debug_output.png

        Args: 
            image: PIL image object
            x: x coordinate of the upper left corner of the bounding box 
            y: y coordinate of the upper left corner of the bounding vox
            w: width of the bounding box
            h: height of the bounding box

        Returns:
            a list of word objects (but did not set id)
        """
        # print (fn)
        image = Image.open(fn)
        Arr = np.array(image)
        boxes = []
        words = []
        with PyTessBaseAPI() as api:
                api.SetImage(image)
                api.SetVariable("save_blob_choices", "T")
                api.SetRectangle(x, y, w, h)
                api.Recognize()
                
                ri = api.GetIterator()
                level = RIL.WORD
                counter = 0
                for r in iterate_level(ri, level):
                        try: 
                                symbol = r.GetUTF8Text(level)
                                conf = r.Confidence(level)
                                bbox = r.BoundingBox(level)
                                w = word.Word(None, None, None, None, None, None, None)
                                w.confidence = conf
                                w.text = symbol
                                w.x = bbox[0]
                                w.y = bbox[1]
                                w.width = bbox[2] - bbox[0]
                                w.height = bbox[3] - bbox[1]
                                words.append(w)
                                # print (w.text)
                                outim = Image.fromarray(Arr[bbox[1]:bbox[3], bbox[0]:bbox[2]])
                                #debugging purpose only...
                                if symbol:
                                        print (symbol + " " + str(conf))
                                        # print (bbox)
                                        outim.save(str(counter) + ' debug.png')
                                        counter += 1
                        except RuntimeError:
                                print ('No text returned')
                                continue

        return words

def getXMat(points):
        """
        converts points to computable form of X in Y = AX
        Returns:
            2D numpy array, shape = 2 by n
        """
        mat = []
        for pair in points: # for each pair of points
                row1 = np.array([pair[0], pair[1], 1, 0, 0, 0])  # x, y, 1, 0, 0, 0
                row2 = np.array([0, 0, 0, pair[0], pair[1], 1])  # 0, 0, 0, x, y, 1
                mat.append(row1) # append the two rows
                mat.append(row2)
        mat = np.vstack((mat)) # stack them horizontally
        print("Vstack:")
        print(mat.shape)
        return mat
        
def getYMat(points):
        """
        converts points to computable form of Y in Y = AX
        Returns:
            An numpy array that represents a vector, shape = n
        """
        mat = []
        for pair in points:
                mat.append(np.array([pair[0], pair[1]]))  # x1 x2
        mat = np.hstack((mat))                            # y1 y2
        print("Hstack:")
        print(mat.shape)
        return mat

def estimateAffine(points1, points2):
        """
        Estimate an affine transformation based on two sets of points
        Args:
            points1: A set of points in image 1, represented as a list of tuples
            points2: A set of points in image 2, represented as a list of tuples
        Returns:
            matrix form of the transformation
        """
        X = getXMat(points1)
        Y = getYMat(points2)
        a = np.dot(np.linalg.pinv(X), Y)
        T = np.zeros((3,3)) # create a 3 x 3 matrix of zeroes
        A = np.reshape(a, (2, 3)) # turns a into a 2 x 3 matrix
        T[0:2, :] = A[:, :] # for each column in the first and second row of T, set it to the equivalent in A
        T[-1, :] = np.array([0, 0, 1]) # for the last row in T,     
        return T

def testRecognize(fn, origRec, T):
        """
        Used for keyword recognition
        Args:
            fn: filename
            origRec: original box, represented as a 4-element tuple (x0, y0, x1, y1)
            T: the transformation matrix
        Returns: a string for the recognized keyword, the tightest bounding box
        """
        orig_ul = np.array([origRec[0], origRec[1], 1])
        orig_lr = np.array([origRec[2], origRec[3], 1])
        new_ul = np.dot(T, orig_ul)
        new_lr = np.dot(T, orig_lr)
        # allow for error margin and make a bigger box...
        words = get_text_from_box(fn, int(new_ul[0])- 10, int(new_ul[1]) - 10, int(new_lr[0]) - int(new_ul[0]) + 15, int(new_lr[1]) -
                                  int (new_ul[1]) + 10)
        recognized = ""
        for word in words:
                word.text = re.sub(r'[^\w\s]','',word.text)
                if len(word.text) > 0:
                        recognized += word.text
        recognized = recognized.strip()
        return recognized, (int(new_ul[0]), int(new_ul[1]), int(new_lr[0]), int(new_lr[1]))


def blobRecognize(fn, origRec, T):
        """
        Used for blob recognition
        Args:
            fn: filename
            origRec: original box, represented as a 4-element tuple (x0, y0, x1, y1)
            T: the transformation matrix
        Returns: a list representing the blob
        """
        orig_ul = np.array([origRec[0], origRec[1], 1])
        orig_lr = np.array([origRec[2], origRec[3], 1])
        new_ul = np.dot(T, orig_ul)
        new_lr = np.dot(T, orig_lr)
        width =  int(new_lr[0]) - int(new_ul[0])
        height = int(new_lr[1]) - int (new_ul[1])
        # print (x0, y0, x0 + width, y0 + height)
        words = get_text_from_box(fn, int(new_ul[0]), int(new_ul[1]), width, height + 12)
        blobs = []# each word in blobs should be separated by a space
        for word in words:
                if len(word.text) > 0:
                        blobs.append(word.text)
        return blobs

def get_ratio(fn, wp, hp):
        image = Image.open(fn)
        w, h = image.size[0], image.size[1]
        print (w, h)
        vec = np.array([w/wp, h/hp])
        image.close()
        return vec

        
if __name__ == "__main__":
        pass

