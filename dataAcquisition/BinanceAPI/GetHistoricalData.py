#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat May 23 13:53:58 2020

@author: bwilliams
"""

from binance.client import Client
import pandas as pd
from datetime import datetime

api_key = 'Uzdbb6H9SSTijdzyTCyrvCqJqZnugShZhGRB5ykCinfxXEAM57q0SkHCONilOKEn'
api_secret = ''
client = Client(api_key, api_secret)

symbol = "ETHUSDT"
start = "1 Jan, 2020"
end = "23 May, 2020"
interval = Client.KLINE_INTERVAL_1MINUTE
klines = client.get_historical_klines(symbol, interval, start, end)



'''
# Returns OHLCV
Open time, 
Open, 
high, 
low, 
close, 
volume
close time 
quote asset volume
number of trades 
taker buy base asset volume
taker buy quote asset volume
ignore
'''

df = pd.DataFrame(klines, columns = ['OpenTime','Open','High','Low','Close','Volume','CloseTime','QuoteAssetVolume','NumTrades','TakerBuyBaseAssetVolume','TakerBuyQuoteAssetVolume','Ignore'])

df = df.assign(Open_Time = df['OpenTime'].apply(lambda x: datetime.fromtimestamp(x/1000)),
          Close_time = df['CloseTime'].apply(lambda x: datetime.fromtimestamp(x/1000)))

import os
os.chdir('/Users/bwilliams/Documents/GitHub/cryptosCollab/dataAcquisition/BinanceAPI')
name_file = "Binance_{}_{}_{}_{}".format(symbol,interval,start.replace( ' ','').replace(',',''),end.replace( ' ','').replace(',',''))
df.to_csv(name_file + '.csv')




