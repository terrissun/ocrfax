import datetime
from . import notification

class NotificationHandler:
	# Handles the functionality for notifications. Main program creates a NotificationHandler object and modifies/accesses the notifications themselves via the functions.

	# constructor
	def __init__(self):
		self.notification_list = [] # create the list to store notifications

	# add notification
	def add_notification(self, date, name, phone_number, message_type, message):
		self.notification_list.append(notification.Notification(date, name, phone_number, message_type, message))

	# delete notification
	def delete_notification(self, notification):
		self.notification_list.remove(notification)

	# delete all notifications
	def delete_all_notifications(self):
		self.notification_list = []

	# sort notifications by date, name, phone number, and type, in ascending or descending order
	def sort_notifications(self, sort_style="date", descending=True):
		if (sort_style == "date"):
			self.notification_list.sort(key=lambda x: (x.get_date()), reverse=descending)
		elif (sort_style == "name"):
			self.notification_list.sort(key=lambda x: (x.get_name() == None, x.get_name()), reverse=descending)
		elif (sort_style == "phone_number"):
			self.notification_list.sort(key=lambda x: (x.get_phone_number() == None, x.get_phone_number()), reverse=descending)
		elif (sort_style == "type"):
			self.notification_list.sort(key=lambda x: (x.get_message_type()), reverse=descending)

	# return the notification at a specific index
	def get_notification_at_index(self, index):
		return self.notification_list[index]

	# return how many notifications are in the handler
	def size(self):
		return len(self.notification_list)


if __name__ == "__main__":

	#TEST CODE

	# Create a new notification handler
	handler = NotificationHandler()

	# Create a date, and a notification, then add it
	current_datetime = datetime.datetime.now()
	handler.add_notification(current_datetime, "Paul Johnson", 5843947711, "Abnormal Lab", "Paul Johnson has an abnormal lipid panel - cholesterol is 120.")

	# Repeat
	current_datetime = datetime.datetime.now()
	handler.add_notification(current_datetime, "John Smith", 9281739912, "Abnormal Lab", "John Smith has an abnormal lipid panel - cholesterol is 120.")

	# Repeat - for "Processing Error" notifications, name is None
	current_datetime = datetime.datetime.now()
	handler.add_notification(current_datetime, None, None, "Processing Error", "Unable to match template.")

	# Sort
	handler.sort_notifications("name", True)


	# Print
	test_notification = handler.get_notification_at_index(0)
	test_notification.print()
	test_notification = handler.get_notification_at_index(1)
	test_notification.print()
	test_notification = handler.get_notification_at_index(2)
	test_notification.print()	


