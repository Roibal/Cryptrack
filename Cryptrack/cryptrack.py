import requests
import random
import datetime
import time
from configparser import ConfigParser
import string
import json
import sys

####################################################
# Cryptrack
# Author: Henry Wrightman
# Version: 1.0.1
# 12/10/17
# Modified 4/21/2018 by Joaquin Roibal @ BlockchainEng
# Changes: 	-Fixed True/False (capitalization)
#			-Added Date/Time Context with Buy & Sell
###################################################


# INI Functions ###################################
###################################################
###################################################
###################################################
def iniRead(section):
	
	try:
	    from configparser import ConfigParser
	except ImportError:
	    from ConfigParser import ConfigParser  # ver. < 3.0

	# instantiate
	config = ConfigParser()

	# parse existing file
	config.read('portfolio.ini')

	# read values from a section
	entry_val = config.getfloat(section, 'entry')
	amount_val = config.getfloat(section, 'amount')
	#print(entry_val, amount_val)
	return (entry_val, amount_val)

def iniAddEntry(sectionName, amount, entry):

	# instantiate
	config = ConfigParser()

	# add
	config.add_section(sectionName)
	config.set(sectionName, 'entry', entry)
	config.set(sectionName, 'amount', amount)
	# save to a file
	with open('portfolio.ini', 'a') as configfile:
		config.write(configfile)

def iniUpdateEntry(sectionName, amount, entry):

	# instantiate
	config = ConfigParser()

	# parse existing file
	config.read('portfolio.ini')
	if (not config.has_section(sectionName)):
		print ("error: portfolio doesn't contain this symbol yet. Consider calling 'add' first.")
		return

	# add
	config.set(sectionName, 'entry', entry)
	config.set(sectionName, 'amount', amount)

	# save to a file
	with open('portfolio.ini', 'w') as configfile:
		config.write(configfile)

def iniDeleteEntry(sectionName):

	# instantiate
	config = ConfigParser()

	# remove section
	config.read('portfolio.ini')
	if (not config.has_section(sectionName)):
		print ("error: portfolio doesn't contain this symbol yet. Deletion not needed.")
		return

	config.remove_section(sectionName)

	# save to a file
	with open('portfolio.ini', 'w') as configfile:
	    config.write(configfile)

def iniSections():

	# instantiate
	config = ConfigParser()

	# parse existing file
	config.read('portfolio.ini')

	return config.sections()

# coinmarketcap API ###############################
###################################################
###################################################
###################################################

class currency(object):
	# init conversion map from json to object
	def __init__(self, j):
		self.__dict__ = j
		# override unix with converted timestamp
		self.__dict__["last_updated"] = currency.unixConvert(self.__dict__["last_updated"])

	# request method to pull from API by requested currency name
	def request(req_name):
		s = requests.Session()
		r = s.get('https://api.coinmarketcap.com/v1/ticker/')
		full_data = json.loads(r.text)

		# json mingling
		if (req_name is not ""):	
			for item in full_data:
				name = item.get("symbol")
				if (name == req_name):
					return item
		else:
			return full_data

		return full_data

	# unix conversion bc it's annoying
	def unixConvert(unix):
		return datetime.datetime.fromtimestamp(
			int(unix)
			).strftime('%H:%M:%S')

	# JSON Notes #
	# the key (e.g id, name, rank) can be referenced for their values; see line ~252
	'''
	"id": "ethereum", 
	        "name": "Ethereum", 
	        "symbol": "ETH", 
	        "rank": "2", 
	        "price_usd": "323.14", 
	        "price_btc": "0.0761602", 
	        "24h_volume_usd": "733002000.0", 
	        "market_cap_usd": "30445631290.0", 
	        "available_supply": "94218083.0", 
	        "total_supply": "94218083.0", 
	        "percent_change_1h": "-0.31", 
	        "percent_change_24h": "1.15", 
	        "percent_change_7d": "5.68", 
	        "last_updated": "1503590065"
	'''

# Main ############################################
###################################################
###################################################
###################################################
if __name__ == '__main__':
	list_of_commands = ['help', 'add', 'remove', 'update', 'buy', 'sell', 'list', 'show', 'quit', 'create_portfolio']
	command = "help"
	while 1:

		if (str(command.lower()) == list_of_commands[0]):
			print ("""\n \n > supported commands: \n
				add <symbol> <entry_amount> <entry_price> ; e.g add XLM 2500 0.16 \n
				remove <symbol>; e.g remove XLM \n
				buy/sell <symbol> <amount> <price>; will update portfolio amounts \n
				create_portfolio <initial deposit in USD>; will create a portfolio \n
				list; will list portfolio symbols \n
				show; will output portfolio statistics \n
				quit; exit\n
				""")
		command = input("Enter command: ")
		comm = command.split(' ')
		if (str(comm[0].lower()) == list_of_commands[1]):
            #Add functionality
			s = str(command).split(' ')

			if (len(s) == 4):
				acr = s[1]

				if (acr in iniSections()):
					print ("entry already exists. Consider the update command.")
				else:
					amount = s[2]	
					entry = s[3]

					iniAddEntry(acr, amount, entry)
			else:
				print ("invalid parameters for:" + str(command[0:3]))

		if (str(comm[0].lower()) == list_of_commands[9]):
            #Create Portfolio Function
			s = str(command).split(' ')

			if (len(s) == 2):
				acr = 'USDT'

				if (acr in iniSections()):
					print ("entry already exists. Consider the update command.")
				else:
					amount = s[1]
					entry = '1'
					iniAddEntry(acr, amount, entry)
			else:
				print ("invalid parameters for:" + str(command[0:3]))

		if (str(comm[0].lower()) == list_of_commands[2]):
			s = str(command).split(' ')

			if (len(s) == 2):
				acr = s[1]
				iniDeleteEntry(acr)
			else:
				print ("invalid parameters for:" + str(command[0:6]))

		if (str(comm[0].lower()) == list_of_commands[3]):
			s = str(command).split(' ')

			if (len(s) == 4):
				acr = s[1]
				amount = s[2]	
				entry = s[3]

				iniUpdateEntry(acr, amount, entry)
			else:
				print ("invalid parameters for:" + str(command[0:6]))

		if (str(comm[0].lower()) == list_of_commands[6]):
            #Functionality from List
			currList = iniSections()
			portfolio_start= 0
			portfolio_curr_total = 0
			for i in currList:
				data = currency.request(i)
				c = currency(data)

				read = iniRead(i)
				val = read[0]
				ent = read[1]

				start_price = val*ent
				portfolio_start += start_price
				current_price = float(c.price_usd)*ent
				portfolio_curr_total += current_price
				delta = round((float(c.price_usd)*ent) - (val*ent), 3)

				print (c.name + " $" + c.price_usd + " " + 
					"[" + c.percent_change_1h  + "% h]" +
					"[" + c.percent_change_24h + "% d]" +
					"[" + c.percent_change_7d + "% w] |" +
					" Delta: $" + str(delta))
			print("\n Portfolio Statistics (USDT): \nPortfolio Start: $", portfolio_start, "\nPortfolio Current: $", portfolio_curr_total)

		if (str(comm[0].lower()) == list_of_commands[7]):
            #Show
			print (iniSections())
		
		if (str(comm[0].lower()) == list_of_commands[8]):
            #Quit
			sys.exit(0)

		elif comm[0] not in list_of_commands:
			print ("unsupported command. Please Try Again!\n\n")
