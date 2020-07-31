from backtesting import Backtest, Strategy
from backtesting.lib import crossover

from backtesting.test import SMA, GOOG

import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
from datetime import timedelta 
import pandas
import pandas as pd
import copy
import numpy


class SmaCross(Strategy):
	def SAR(self, arr):
		return arr

	def init(self):
		price = self.data.Close
		macd_signal = self.data.MACD
		ema_12 = self.data.ema_12
		ema_9 = self.data.ema_9
		#price = self.symbol_df['Close']
		self.signal = self.I(self.SAR, ema_9, color='red')
		self.macd = self.I(self.SAR, macd_signal, color='black')
		# self.ma1 = self.I(SMA, price, 10, color='black')
		# self.ma2 = self.I(SMA, price, 12, color='red')

	def next(self):
		if crossover(self.macd, self.signal):
			self.buy()
		elif crossover(self.macd, self.signal):
			self.sell()

scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name('Happy Stock-6d54ea58d0fa.json', scope)
client = gspread.authorize(creds)
symbol_sheet = client.open("VEDL").sheet1
nifty50_sheet = client.open("NIFTY 50").sheet1
symbol_dict = symbol_sheet.get_all_records()
nifty50_dict = nifty50_sheet.get_all_records()

mydata= []
symbol_df = pd.DataFrame(symbol_dict)
symbol_df['Date'] = pd.to_datetime(symbol_df['Date'])
mydata.append(symbol_df)
TechIndicator = copy.deepcopy(mydata)

for stock in range(len(TechIndicator)):
	TechIndicator[stock]['ema_9'] = TechIndicator[stock]['Close'].ewm(span=9,min_periods=0,adjust=True,ignore_na=False).mean()
	TechIndicator[stock]['ema_26'] = TechIndicator[stock]['Close'].ewm(span=26,min_periods=0,adjust=True,ignore_na=False).mean()
	TechIndicator[stock]['ema_12'] = TechIndicator[stock]['Close'].ewm(span=12,min_periods=0,adjust=True,ignore_na=False).mean()
	TechIndicator[stock]['MACD'] = TechIndicator[stock]['ema_12'] - TechIndicator[stock]['ema_26']
	TechIndicator[stock] = TechIndicator[stock].fillna(0)
	TechIndicator[0].tail()
print(TechIndicator[0]['MACD'])
bt = Backtest(pd.DataFrame(TechIndicator[0]), SmaCross)
print(bt.run())
bt.plot()