#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jun  8 18:08:24 2020

@author: bwilliams
"""



import json
with open("/Users/bwilliams/Documents/GitHub/cryptosCollab/dataAcquisition/coinAPI/symbols/symbols_list.json") as f:
    symbols = json.load(f)
    
exchange = "BITMEX"
trade_type = "SPOT"

for symbol in symbols:
    if symbol['exchange_id'] == exchange:
         if symbol['symbol_type'] == trade_type:
             print(symbol['symbol_id'])
             
import pandas as pd
df_s = pd.read_json(r"/Users/bwilliams/Documents/GitHub/cryptosCollab/dataAcquisition/coinAPI/symbols/symbols_list.json")

df_s['symbol_type'].unique()

temp = df_s[(df_s['exchange_id'] == exchange) ]
trade_type = "FUTURES"
# & (df_s['symbol_type'] == trade_type)


temp2 = temp[temp['symbol_type']=='FUTURES']
