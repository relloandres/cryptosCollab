#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jul 14 12:23:47 2020

@author: bwilliams
"""

import os
from binance.client import Client
import pandas as pd
from datetime import datetime
import time
import numpy as np

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import seaborn as sns
sns.set(style='darkgrid', context='talk', palette='Dark2')



# 1. Load historical data for two currencies

def StablishConnectionBinance(directory_files):
    os.chdir(directory_files )
    from BinanceKeys import BinanceKey1
    api_key = BinanceKey1['api_key']
    api_secret = BinanceKey1['api_secret']
    client = Client(api_key, api_secret)
    return client


def GetHistoricalDataBinance_tocsv(client, symbol, start, end, interval, save_path):
    # Measure execution time
    start_time = time.time()
   
    klines = client.get_historical_klines(symbol, interval, start, end)
        
    df = pd.DataFrame(klines, columns = ['OpenTime','Open','High','Low','Close','Volume','CloseTime','QuoteAssetVolume','NumTrades','TakerBuyBaseAssetVolume','TakerBuyQuoteAssetVolume','Ignore'])
    
    df = df.assign(Open_Time = df['OpenTime'].apply(lambda x: datetime.fromtimestamp(x/1000)),
              Close_time = df['CloseTime'].apply(lambda x: datetime.fromtimestamp(x/1000)))

   
    os.chdir(save_path)
    name_file = "Binance_{}_{}_{}_{}".format(symbol,interval,start.replace( ' ','').replace(',',''),end.replace( ' ','').replace(',',''))
    df.to_csv(name_file + '.csv')
    print("--- %s seconds ---" % round(time.time() - start_time,2))
    return df




def exponential_moving_average(df, n_s, n_l, fee ):
    # 2. Moving averages on data 
    
    # Exponetial moving average on close price
    
     # Assume we can buy and sell on close price as well
     
     # Candlesticks are created on the rates of transactions (both buy and sell) in the period, 
     # we therfore do not know the true price for wich we can buy or sell, since 
     # we cannot tell if the order is buy or sell
     # this can be further improved by replicating historical trades, or better yet
     # by having historical orderbook data
     
     # returns: moving averages, trading signal and returns of buy-sell cycles
     
    
    # Only for 2019
    
    
    df = df.assign( 
                     mae_short = df['Close'].ewm(span=n_s, adjust=False).mean(),
                     mae_long = df['Close'].ewm(span=n_l, adjust=False).mean()
                     )
    
    # First buy when short moving average is over long moving average, this is the trigger
    
    
    '''
    my_year_month_fmt = mdates.DateFormatter('%m/%y')
    # Plot of last n rows
    
    # Exponential moving average
    temp = df.tail(1000)
    fig, ax = plt.subplots(figsize=(16,9))
    
    ax.plot(temp.Open_Time, temp.Close, label='Close')
    ax.plot(temp.Open_Time, temp.mae_short, label = str(n_s)+'-obs EMA')
    ax.plot(temp.Open_Time, temp.mae_long, label = str(n_l)+'-obs EMA')
    
    ax.legend(loc='best')
    ax.set_ylabel('Value')
    ax.xaxis.set_major_formatter(my_year_month_fmt)
    '''
    
    
    # Measure wins and loses
    # We only count proffit for USDT, nor for avoided losses of ETH
    # as we seek to increase USDT by exploiting changes in the currency 
    
    
    # suppose we have 1 USDT, strategy beggins with first purchase, 
     # this is, first purchase signal
     # Code is completely vectorized, adding transaction fees 
    
    
    # buy, sell, hold position
    
    df = df.assign( position_mae = np.sign(df.mae_short - df.mae_long ) )
    
    df = df.assign(position_mae_lag1 = df['position_mae'].shift(1))
    
    df['signal'] = 'hold'
    df.loc[(df['position_mae']==1) & (df['position_mae_lag1']==-1), 'signal'] = 'buy'
    df.loc[(df['position_mae']==-1) & (df['position_mae_lag1']==1), 'signal'] = 'sell'
    
    # df[df.index>=236][['Close','mae_short', 'mae_long', 'position_mae','position_mae_lag1', 'signal']]
    
    # Returns with comissions
    
    # 1. Find first buy signal
    # We consider that before first buy signal no transaction is put in place
    # We can improve code, by buying on first buy signal or if the position_mae == 1
    
    first_buy_index = df[df['signal'].isin( ['buy']) ].index.min()
    
    operations = df[df['signal'].isin( ['buy','sell']) & (df.index>= first_buy_index  ) ].copy()
    
    operations = operations[['Open_Time','Open', 'High', 'Low', 'Close','mae_short', 'mae_long', 'signal']]\
        .assign(
        Open_time_sell = operations['Open_Time'].shift(-1),
        Open_sell = operations['Open'].shift(-1),
        High_sell = operations['High'].shift(-1),
        Low_sell = operations['Low'].shift(-1),
        Close_sell = operations['Close'].shift(-1),
        mae_short_sell = operations['mae_short'].shift(-1),
        mae_long_sell = operations['mae_long'].shift(-1),
        Signal_sell = operations['signal'].shift(-1),
        )
    
    
    operations_buy = operations[(operations.signal == 'buy') & (operations.Signal_sell.notnull() )].copy()
    
    # Returns 
    # assuming both buying fee and selling fees are the same, and fee doesnt vary if its a maker or taker order
    
    
    operations_buy= operations_buy.assign( 
        r = operations_buy.Close_sell/operations_buy.Close - 1,
        r_fee =  ((1-fee)**2)  * operations_buy.Close_sell/operations_buy.Close  - 1
        )
        
    
    
    return  df[['Open_Time', 'Close','mae_short', 'mae_long','signal']]  , operations_buy[['Open_Time','r','r_fee']]


def total_return_sharpe(r):
    # sharpe ratio is adjusted for number of observations, we asume risk free rate of 0%
    n_buy = len(r)
    return r.sum(), n_buy*r.mean()/r.std()


