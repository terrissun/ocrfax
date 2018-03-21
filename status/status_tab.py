'''
statustab
'''
from . import notificationhandler

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.recycleview import RecycleView
from kivy.uix.recyclegridlayout import RecycleGridLayout

class StatusTab(BoxLayout):

    def __init__(self, controller, **kwargs):

        super(StatusTab, self).__init__(**kwargs)

        self.controller = controller

        # create the notifications panel
        self.notifications_panel = NotificationsPanel()

        # add the notifications panel to the layout
        self.ids.notifications_display_box_layout.add_widget(self.notifications_panel)

        # Set up notifications
        self.notification_handler = notificationhandler.NotificationHandler()

    # Notification panel functions

    def add_notification(self, date, name, phone_number, message_type, message):

        """Adds a notification to notification_handler and updates the panel.

        Grabs data from the text input fields on the Status tab, then creates a Notificaition
        and adds it to the notification handler, after which it calls update_notifications.

        Args:
            date (str): The date of the notification
            name (str): The name of the sender of the notification. If a system message, this
            should be "System"
            phone_number (str): The phone_number of the sender. If a system message, this
            should be None
            message_type (str): The type of notification. Currently, only "Success".
            message (str): The actual message.
        """

        # Create the notification
        self.notification_handler.add_notification(date, name, phone_number, message_type, message)
        self.update_notifications()


    def add_notification_debug(self):
        """Adds a notification to notification_handler and updates the panel.

        Grabs data from the text input fields on the Status tab, then creates a Notificaition
        and adds it to the notification handler, after which it calls update_notifications.
        """
        date = self.ids.date_text_input.text
        name = self.ids.name_text_input.text
        phone_number = self.ids.phone_number_text_input.text
        message_type = self.ids.message_type_text_input.text
        message = self.ids.message_text_input.text

        # Create the notification
        self.notification_handler.add_notification(date, name, phone_number, message_type, message)
        self.update_notifications()

    def update_notifications(self):
        """Updates the notifications panel with which notifications are currently stored.

        Gather the notifications from notification_handler into a flattened array, which is
        necessary for accurate display of the RecycleGridLayout. After, tells the GUI element
        notifications_panel to update itself.
        """
        grid_update_array = []
        for i in range(0, self.notification_handler.size()):
            notification = self.notification_handler.get_notification_at_index(i)
            grid_update_array.append(notification.get_date())
            grid_update_array.append(notification.get_name())
            grid_update_array.append(notification.get_phone_number())
            grid_update_array.append(notification.get_message_type())
            grid_update_array.append(notification.get_message())

        # refresh the list
        self.notifications_panel.update_data(grid_update_array)

    def clear_notifications(self):
        """Clears the notification panel of all notifications.

        Deletes all Notification objects in notification_handler, then passes an empty array
        to the GUI element notifications_panel, and tells it to update itself.
        """
        self.notification_handler.delete_all_notifications()
        grid_update_array = []
        self.notifications_panel.update_data(grid_update_array)

    def search_notifications(self):
        message = self.ids.search_input.text
        grid_update_array = []
        for i in range(0, self.notification_handler.size()):
            notification = self.notification_handler.get_notification_at_index(i)
            if notification.notification_contains(message):
                grid_update_array.append(notification.get_date())
                grid_update_array.append(notification.get_name())
                grid_update_array.append(notification.get_phone_number())
                grid_update_array.append(notification.get_message_type())
                grid_update_array.append(notification.get_message())

        self.notifications_panel.update_data(grid_update_array)


'''
NotificationsPanel
This is the notifications panel that appears on the Status tab.
This panel uses a recycle view, a more efficient, up-to-date form of ListView
'''
class NotificationsPanel(RecycleView):
    def __init__(self, **kwargs):
        super(NotificationsPanel, self).__init__(**kwargs)

    def update_data(self, values):
        # parses the data provided in values into an appropriate value for self.data
        self.data = [{'text': str(x)} for x in values]
