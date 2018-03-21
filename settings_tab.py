'''
settings_tab.py
'''

import os

from kivy.uix.boxlayout import BoxLayout

class SettingsTab(BoxLayout):

	def __init__(self, controller, **kwargs):

		super(SettingsTab, self).__init__(**kwargs)

		self.settings_dict = {}
		# Set the config data
		default_file_location = os.getcwd() + "/" + "config.ini"
		if os.path.isfile(default_file_location):
			file = open(default_file_location, "r")
			for line in file:
				config_data = line.split(":")
				print(config_data[0])
				if config_data[0] == "DefaultTemplateLocation":
					self.settings_dict['DTL'] = config_data[1].strip()
				if config_data[0] == "DefaultPDFLocation":
					self.settings_dict['DFL'] = config_data[1].strip()
			file.close()
		else: # config file is being created
			file = open(default_file_location, "w")
			user = getpass.getuser()
			self.settings_dict['DTL'] = "/home/{}/Documents/Templates".format(user)
			file.write("DefaultTemplateLocation:{}\n".format(self.settings_dict['DTL']))

			self.settings_dict['DFL'] = "/home/{}/Desktop".format(getpass.getuser())

			file.write("DefaultPDFLocation:{}\n".format(self.settings_dict['DFL']))

			file.close()

		# update the settings panel
		self.ids.dtl_text_input.text = self.settings_dict['DTL']
		self.ids.dfl_text_input.text = self.settings_dict['DFL']

	def update_settings(self):
		default_file_location = os.getcwd() + "/" + "config.ini"
		file = open(default_file_location, "w")
		self.settings_dict['DTL'] = self.ids.dtl_text_input.text
		file.write("DefaultTemplateLocation:{}\n".format(self.settings_dict['DTL']))
		self.settings_dict['DFL'] = self.ids.dfl_text_input.text
		file.write("DefaultPDFLocation:{}\n".format(self.settings_dict['DFL']))
		file.close()

	def get_setting(self, key):
		return self.settings_dict[key]