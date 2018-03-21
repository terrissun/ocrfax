import datetime

class Notification:
	# the data type for the notification
	
	# Constructor
	def __init__(self, date, name, phone_number, message_type, message):
		self.date = date
		self.name = name
		self.phone_number = phone_number
		self.type = message_type
		self.message = message


	# Accessors

	def get_date(self):
		return self.date

	def get_name(self):
		return self.name

	def get_phone_number(self):
		return self.phone_number

	def get_message_type(self):
		return self.type

	def get_message(self):
		return self.message

	# see if a given text message is in the notification
	def notification_contains(self,text):
		if (self.date.find(text) !=-1) or (self.name.find(text) !=-1) or (self.phone_number.find(text) !=-1) or (self.type.find(text) !=-1) or (self.message.find(text) !=-1):
			return True
		else: 
			return False
		

	# Debug functionaliity

	def print(self):
		print("{} - {}:{} Type:{}  Message:{}".format(self.date, self.name, self.phone_number, self.type, self.message))


	@staticmethod
	def testMethod():
		print("hey")