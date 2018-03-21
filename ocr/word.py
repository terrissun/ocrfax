'''
word.py
'''

class Word():

	def __init__(self, id, x, y, w, h, confidence, text):
		self.id = id
		self.x = x
		self.y = y
		self.width = w
		self.height = h
		self.confidence = confidence
		self.text = text

	def get_id(self):
		return self.id

	def get_x(self):
		return self.x

	def get_y(self):
		return self.y

	def get_width(self):
		return self.width

	def get_height(self):
		return self.height

	def get_confidence(self):
		return self.confidence

	def get_text(self):
		return self.text
