'''
template.py
'''
import ocr.word

def load_from_file(filepath):
	file = open(filepath, "r")
	line = file.readline()
	name = (line.split(":")[1])
	new_template = Template(name.strip(), filepath)
	file.readline()
	
	line_count = 0
	word_text = ""
	x = 0
	y = 0
	w = 0
	h = 0

	# Load identification keywords
	for line in file:
		if "End of Faxxine Template Identification Keywords" in line:
			break
		else:
			if line_count == 0:
				word_text = line.strip()
				line_count = 1
			else:
				data = line.split(",")
				x = int(data[0].strip())
				y = int(data[1].strip())
				w = int(data[2].strip())
				h = int(data[3].strip())
				new_template.add_id_keyword(word_text, x, y, w, h)
				line_count = 0
	
	# Load field keywords
	file.readline()
	for line in file:
		if "End of Faxxine Template Field Keywords" in line:
			break
		else:
			if line_count == 0:
				word_text = line.strip()
				line_count = 1
			else:
				data = line.split(",")
				x = int(data[0].strip())
				y = int(data[1].strip())
				w = int(data[2].strip())
				h = int(data[3].strip())
				new_template.add_field_keyword(word_text, x, y, w, h)
				line_count = 0

	# Load field keywords
	file.readline()
	for line in file:
		if "End of Faxxine Template Extraction Fields" in line:
			break
		else:
			data = line.split(",")
			word_text = data[0].strip()
			x = int(data[1].strip())
			y = int(data[2].strip())
			w = int(data[3].strip())
			h = int(data[4].strip())
			new_template.add_field(word_text, x, y, w, h)
			line_count = 0

	file.close()
	return new_template




class Template():

	# Temporary test init method, needs to save and load to file
	def __init__(self, name, filepath):
		self.name = name
		self.filepath = filepath
		self.id_keyword_list = []
		self.field_keyword_list = []
		self.field_list = []


	def add_id_keyword(self, keyword, x, y, w, h):
		new_word = word.Word(len(self.id_keyword_list), x, y, w, h, 100, keyword)
		self.id_keyword_list.append(new_word)

	def add_field_keyword(self, keyword, x, y, w, h):
		new_word = word.Word(len(self.field_keyword_list), x, y, w, h, 100, keyword)
		self.field_keyword_list.append(new_word)

	def add_field(self, keyword, x, y, w, h):
		new_word = word.Word(len(self.field_list), x, y, w, h, 100, keyword)
		self.field_list.append(new_word)

	def get_name(self):
		return self.name

	def save(self):
		file = open(self.filepath, "w")
		file.write("Name:{}\n".format(self.name))

		file.write("Beginning of Faxxine Template Identification Keywords\n")
		for i in range(0, len(self.id_keyword_list)):
			temp_word = self.id_keyword_list[i]
			file.write("{}\n".format(temp_word.get_text()))
			file.write("{},{},{},{}\n".format(temp_word.get_x(), temp_word.get_y(), temp_word.get_width(), temp_word.get_height()))
		file.write("End of Faxxine Template Identification Keywords\n")

		file.write("Beginning of Faxxine Template Field Keywords\n")
		for i in range(0, len(self.field_keyword_list)):
			temp_word = self.field_keyword_list[i]
			file.write("{}\n".format(temp_word.get_text()))
			file.write("{},{},{},{}\n".format(temp_word.get_x(), temp_word.get_y(), temp_word.get_width(), temp_word.get_height()))
		file.write("End of Faxxine Template Field Keywords\n")

		file.write("Beginning of Faxxine Template Extraction Fields\n")
		for i in range(0, len(self.field_list)):
			temp_word = self.field_list[i]
			file.write("{},{},{},{},{}\n".format(temp_word.get_text(), temp_word.get_x(), temp_word.get_y(), temp_word.get_width(), temp_word.get_height()))
		file.write("End of Faxxine Template Extraction Fields\n")

		file.close()

	def keyword_list_length(self, field_type):
		if field_type == "id":
			return len(self.id_keyword_list)
		elif field_type == "field_keyword":
			return len(self.field_keyword_list)
		elif field_type == "extraction_field":
			return len(self.field_list)

	def keyword_at_index(self, field_type, index):
		if field_type == "id":
			return self.id_keyword_list[index]
		elif field_type == "field_keyword":
			return self.field_keyword_list[index]
		elif field_type == "extraction_field":
			return self.field_list[index]

if __name__ == "__main__":
	template = load_from_file("/home/matthew/Documents/Templates/test.template")
	template.save()