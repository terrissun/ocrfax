'''
PDFPage class
'''
from . import word

from sortedcontainers import SortedDict

class PDFPage():

	def __init__(self, folder_location, number_of_pages):
		self.folder = folder_location
		self.number_of_pages = number_of_pages
		self.text_dict = {}
		self.id_dict = {}
		self.position_dict = SortedDict() # x, then y


	def add_word(self, word):
		# add word to multiple sortable dictionaries

		# by text - creates a list with every instance of the word
		if word.get_text() not in self.text_dict:
			self.text_dict[word.get_text()] = [word]
		else:
			self.text_dict[word.get_text()].append(word)

		# by id	
		self.id_dict[word.get_id()] = word

		# by position
		if word.get_x() not in self.position_dict:
			self.position_dict[word.get_x()] =  SortedDict()
			#print("Empty x value of {}: {}".format(word.get_x(), self.position_dict[word.get_x()]))
			(self.position_dict[word.get_x()])[word.get_y()] = word
			print("X: {} Y: {}".format(word.get_x(), word.get_y()))
		else:
			self.position_dict[word.get_x()][word.get_y()] = word
			print("X: {} Y: {}".format(word.get_x(), word.get_y()))

	def sort_dictionaries(self):
		return_value = SortedDict()
		for key1 in sorted(self.position_dict.keys()):
			x_return_value = SortedDict()
			for key2 in self.position_dict[key1]:
				x_return_value = sorted((self.position_dict[key1]).keys())



	# def print(self):
	# 	for word_id in self.id_dict:
	# 		print("{}: {}".format(word_id, self.id_dict[word_id].get_text()))

