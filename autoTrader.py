

import oandapy
import json
import requests
from sendEmail import sendEmail
import time
from numpy import exp, array, random, dot
#from data.predict import predictNext
import os
import math
import datetime
from data import updatePrediction
from dateutil.parser import parse




currentPrediction = 0.0


class MyStreamer(oandapy.Streamer):
	def __init__(self, count = 10, *args, **kwargs):
		print "connecting..."
		super(MyStreamer, self).__init__(*args, **kwargs)


	def on_success(self, data):

		global currentUnits, STARTING_UNITS, currentPrediction
		if 'heartbeat' in data:
			pass
		elif 'tick' in data:
			cls()
			#print environment+" Trading"
			print "\n"
			print data['tick']['instrument']
			print 'bid:',data['tick']['bid']
			print 'ask:',data['tick']['ask']
			print 'time:',data['tick']['time']
			time = parse(data['tick']['time']) #converts to datetime object


			try:
				trades = oanda.get_trades(account, instrument = instrument)
			except:
				time.sleep(1)
				#handle rate limit
				trades = oanda.get_trades(account, instrument = instrument)		

			#print(trades)
			print "\n"
			if len(trades['trades']) > 0:
				print "Current Position"
				print 'id:', trades['trades'][0]['id']
				print "Position:", trades['trades'][0]['instrument']
				print trades['trades'][0]['side']
				print "Units:", trades['trades'][0]['units']
				last_trade_id = trades['trades'][0]['id']

			elif 0 <= time.minute <= 1: #change to datetime from tick
				print "no trades open"
				print "attempting to trade"
				#if spread < 3 pips
				#os.system('python ./data/getData2.py')
				#os.system('python ./data/updatePrediction')
				updatePrediction.update()
				with open("./data/USD_JPY_H1_predictions.csv") as f:
					prediction = list(f)[-1]
					currentPrediction = prediction
				response = oanda.get_prices(instruments="USD_JPY")
				prices = response.get("prices")
				ask = prices[0].get("ask")
				bid = prices[0].get("bid")
				spread = abs(ask-bid) * .0001
				if float(prediction) > ask and spread < 4:
					direction = 1
				elif float(prediction) < bid and spread < 4:
					direction = 0

				try:
					transactions = oanda.get_transaction_history(account, instrument = instrument)
				except Exception as e:
					time.sleep(1)
					transactions = oanda.get_transaction_history(account, instrument = instrument)

				last_trade_pl = 0		
				for t in transactions['transactions']:
					if 'type' in t:
						if t['type'] == "TRADE_CLOSE" or t['type'] == "STOP_LOSS_FILLED" or t['type'] == "TAKE_PROFIT_FILLED":
							last_trade_pl = t['pl']
							break

				factor = .0001
				if instrument == "USD_JPY":
					factor = .01
				if direction == 1:
					print "Sending buy order..."
					try:
						response = oanda.create_order(account, instrument = instrument, units = currentUnits, side='buy', type = 'market', stopLoss = ask - SL * factor, takeProfit = ask + TP*factor)
					except Exception as e:
						response = oanda.create_order(account, instrument = instrument, units = currentUnits, side='buy', type = 'market', stopLoss = ask - SL * factor, takeProfit = ask + TP*factor)

					try:
						print "sending email"
						sendEmail(email, recipient, "Position closed\nP/L: "+str(last_trade_pl)+"\nBuy: "+ str(currentUnits) +"\nPrediction: "+prediction)
					except Exception as e:
						print "email failed to send"
						print e
				else:
					print "Sending sell order..."
					try:
						response = oanda.create_order(account, instrument = instrument, units = currentUnits, side='sell', type = 'market', stopLoss = bid + SL*factor, takeProfit = bid - TP*factor)
					except Exception as e:
						response = oanda.create_order(account, instrument = instrument, units = currentUnits, side='sell', type = 'market', stopLoss = bid + SL*factor, takeProfit = bid - TP*factor)
					try:
						print "sending email"
						sendEmail(email, recipient, "Position closed\nP/L: " + str(last_trade_pl) + "\nSell: " +str(currentUnits)+"\nPrediction: "+prediction)
					except Exception as e:
						print "email failed to send"
						print e

			print "Prediction: "+str(currentPrediction)

	def on_error(self, data):
		self.disconnect()
		print "error"
#clears the console output
def cls():
	os.system('cls' if os.name=='nt' else 'clear')
		



with open('config.json', 'r') as f:
	config = json.load(f)
#oanda account to be traded on
account = ""
#oanda API access token 
access_token = "" 
#username of notication sender (tested on gmail)
email = config['emailUser']
#an email address of the notification recipient 
recipient = config['emailRecipient']

environment = raw_input("Live or practice: ")
if (environment == "live"):
	account = config['liveAccount']
	access_token = config['liveToken']
elif (environment == "practice"):
	account = config['practiceAccount']
	access_token = config['practiceToken']

instrument = raw_input("Enter a pair to trade (EUR_USD, USD_JPY, etc): ")
STARTING_UNITS = int(raw_input("Enter the base number of units to trade: ")) 

currentUnits = STARTING_UNITS
TP = int(raw_input("Enter number of pips for TP: "))
SL = int(raw_input("Enter number of pips for SL: "))

timeframe = raw_input("Enter a timeframe (S1, M1, H1): ") 

oanda = oandapy.API(environment=environment, access_token=access_token)
stream = MyStreamer(environment=environment, access_token=access_token)
stream.rates(account, instruments=instrument)

