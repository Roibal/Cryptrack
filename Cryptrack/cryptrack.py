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
#
# 4/21/2018 Modified by Joaquin Roibal @BlockchainEng
# Changes: 	-Fixed True/False (capitalization) [removed functionality]
#			-Added Date/Time Context with Buy & Sell [will need further development]
#           -Buy-Sell Functionality (future development)
#           -Add Cryptocurrency 'Basket' (completed)
#           -Added Portfolio Functionality [and $250k index starting April 21, 2018]
#           -Added Instructional Youtube Video: https://youtu.be/DFCDVrAmyR4
#           -Will Incorporate with Algo Trading Bot
###################################################


# INI Functions ###################################
###################################################
###################################################
###################################################
def iniRead(section, portfolio='portfolio.ini'):
	
	try:
	    from configparser import ConfigParser
	except ImportError:
	    from ConfigParser import ConfigParser  # ver. < 3.0

	# instantiate
	config = ConfigParser()

	# parse existing file
	config.read(portfolio)

	# read values from a section
	entry_val = config.getfloat(section, 'entry')
	amount_val = config.getfloat(section, 'amount')
	#print(entry_val, amount_val)
	return (entry_val, amount_val)

def iniAddEntry(sectionName, amount, entry, port_file='portfolio.ini'):

	# instantiate
	config = ConfigParser()

	# add
	config.add_section(sectionName)
	config.set(sectionName, 'entry', entry)
	config.set(sectionName, 'amount', amount)
	# save to a file
	with open(port_file, 'a') as configfile:
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

def iniSections(portfolio_file='portfolio.ini'):

	# instantiate
	config = ConfigParser()

	# parse existing file
	config.read(portfolio_file)

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

def track_index(num_coins='25', denom='USD'):
    #This Function Will Track an Index of Top-25 coins, if $10K Purchased
    #Get Top 25 coins by Market Cap from Coin Market Cap
    r = requests.get('https://api.coinmarketcap.com/v1/ticker/?convert={}&limit={}'.format(denom, num_coins))
    print(r.status_code)
    coin_list = r.json()
    print(coin_list)
    #for crypto in coin_list:
        #print(crypto['id'])
    #Create CSV (.txt) file with: [symbol], [name], [price], [quantity in circulation], [total market cap], [1 hour change], [1 day change], [1 week change]
    #Save To .txt file
    workfile = 'Top{}Coins_MarketCap_{}'.format(num_coins, time.strftime("%d_%b_%Y_H%H-M%M-S%S", time.localtime()))+'{}.txt'.format(denom)
    with open(workfile, 'a+') as f:
        i=0
        read_data = f.readline()
        for crypto in coin_list:
            #print(crypto['id'])
            if read_data=='' and i==0:
                f.write('symbol, name, price, quantity, market_cap, 1_hr_change, 1_day_change, 1_week_change, 24h_volume\n')
                i=1
            f.write('{}, {}, {}, {}, {}, {}, {}, {}, {}\n'.format(crypto['symbol'], crypto['name'], crypto['price_usd'], crypto['total_supply'],
                                                            crypto['market_cap_usd'], crypto['percent_change_1h'], crypto['percent_change_24h'],
                                                            crypto['percent_change_7d'], crypto['24h_volume_usd']))
    return workfile
    #Determine Price on January 1, 2018

    #Calculate Quantity of Coin Able to be Purchased with $10k on that date
def buy_coin(coin, amount, entry, index):
    iniAddEntry(str(coin), str(amount), str(entry), str(index))

def create_index(portfolio_amount = '250000', num_coins = '25'):
    position_size = float(portfolio_amount)/float(num_coins)
    #Calculate Quantity of Coin Able to be Purchased with $10k on that date
    wrk_file = track_index()
    with open(wrk_file, 'r') as f:
        for line in f:
            coin = line.split(',')
            if coin[0]=='symbol':
                pass
            else:
                amount = position_size/float(coin[2])
                #create new Date_index_portfolio.ini (blank) to use
                buy_coin(coin[0], amount, coin[2], 'DATE_index_portfolio.ini')
    print("Create Index Completed")
    #Calculate Current Statistics (ROR, Price, Volume) for Total at current date & time
        #incorporated with 'show' functionality
    #Visualize Data with MatPlotLib

# Main ############################################
###################################################
###################################################
###################################################

def run():
	list_of_commands = ['help', 'add', 'remove', 'update', 'buy', 'sell', 'list', 'show', 'quit', 'create_portfolio', 'index']
	command = "help"
	while 1:

		if (str(command.lower()) == list_of_commands[0]):
			print ("""\n \n > supported commands: \n
				add <symbol> <entry_amount> <entry_price> ; e.g add XLM 2500 0.16 (default)\n
				* add <symbol> <purchase amount> <index> ; adds purchase amount of symbol to index
				* remove <symbol>; e.g remove XLM \n
				* buy/sell <symbol> <amount> <price>; will update portfolio amounts \n
				create_portfolio <initial deposit in USD>; will create a portfolio \n
				list; will list portfolio symbols \n
				show portfolio.ini; will output portfolio statistics \n
				show April_21_index_portfolio.ini ; will output index statistics \n
				index example ; display example of index with top 25 coins in USD\n
				index <num_coins> <denomination> ; display index of top <number> of coins in <USD> or <EUR>\n
				quit; exit\n
				""")
		command = input("Enter command: ")
		comm = command.split(' ')

		if comm[0]=='index':
            #if Index is chosen, print either example or user-entered input
			if comm[1].lower()=='example':
				create_index()
			else:
				track_index(int(comm[1]), str(comm[2]))

		if (str(comm[0].lower()) == list_of_commands[1]):
            #Add functionality
			s = str(command).split(' ')

			if (len(s) == 4):
				#default add
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
			#Remove Functionality
			s = str(command).split(' ')

			if (len(s) == 2):
				acr = s[1]
				iniDeleteEntry(acr)
			else:
				print ("invalid parameters for:" + str(command[0:6]))

		if (str(comm[0].lower()) == list_of_commands[3]):
			#Update Functionality
			s = str(command).split(' ')

			if (len(s) == 4):
				acr = s[1]
				amount = s[2]	
				entry = s[3]

				iniUpdateEntry(acr, amount, entry)
			else:
				print ("invalid parameters for:" + str(command[0:6]))

		if (str(comm[0].lower()) == list_of_commands[7]):
            #Functionality from Show
			currList = iniSections(comm[1])
			portfolio_start= 0
			portfolio_curr_total = 0
			for i in currList:
				data = currency.request(i)
				c = currency(data)

				read = iniRead(i, comm[1])
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
			print("\nPortfolio Statistics (USD): \nPortfolio Start: $", portfolio_start, "\nPortfolio Current: $", round(portfolio_curr_total,3))
			profit_loss = portfolio_curr_total-portfolio_start
			print("Profit/Loss: $", round(profit_loss, 2))
			port_perc_change = (profit_loss)/portfolio_start
			print("Percent Change: ", round(port_perc_change*100,3), "%")

		if (str(comm[0].lower()) == list_of_commands[6]):
            #List
			print (iniSections())
		
		if (str(comm[0].lower()) == list_of_commands[8]):
            #Quit
			sys.exit(0)

		elif comm[0] not in list_of_commands:
			print ("unsupported command. Please Try Again!\n\n")

if __name__ == '__main__':
	run()