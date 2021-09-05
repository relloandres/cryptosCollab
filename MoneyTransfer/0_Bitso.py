import pandas as pd
import numpy as np
import bitso
import json

mxn_to_convert = 500
xrp_address = 'rEb8TK3gBgk5auZkwc6sHnwrGVJH8DuaLh'
xrp_memo = '103636713'
min_xrp = 0.00000001 
dir_key = 'MoneyTransfer/Keys/BitsoKeysBW.json'


def connect_bitso_api(dir_key):
'''
Load keys from json file
Establish connection with Bitso API
'''
try:
        with open(dir_key) as f:
          cred = json.load(f)
        API_KEY = cred['api_key']
        API_SECRET = cred['api_secret']
        api = bitso.Api(API_KEY, API_SECRET)
        return api
except: 
        print('Connection failed')


def orderbook_asks(api, mxn_to_convert):
    '''
    Extracts open buy orders from orderbook and chooses the ones that match 
    available fiat ammount
    '''
    ob = api.order_book('xrp_mxn')
    str(ob.updated_at)
    # In order to cover order book we need to cover ask orders fullfiling amount until our supply of mxn is covered
    extract_info_orderbook = lambda x: [float(x.price), float(x.amount)]
    df = pd.DataFrame(map(extract_info_orderbook, ob.asks ),columns=['price','amount'])
    df['fill'] = df.price * df.amount
    df['fill_cumsum'] = df.fill.cumsum()
    # find which row is the one that covers our demand for buying mxn
    idxmax_mxn = df.fill_cumsum.gt( mxn_to_convert).idxmax()
    df_transactions = df.iloc[0:(idxmax_mxn+1)]    
    return df_transactions

def place_orders(api, mxn_to_convert, df_transactions):
    '''
    Places limit orders until mxn_to_convert is finished based on 
     prices extracted from orderbook
    '''
    # Place orders
    orders = []
    current_money = mxn_to_convert
    for i in range(len(df_transactions)):
        if current_money > df_transactions.fill[i]:
            minor_order = df_transactions.fill[i]
            current_money -= minor_order
            orders.append(  
                api.place_order(
                    book = 'xrp_mxn', 
                    side = 'buy', 
                    order_type = 'limit',              
                    price = df_transactions.price[i],
                    minor = minor_order) 
            )
        else:
            minor_order = current_money
            current_money -= minor_order
            orders.append(  
                api.place_order(
                    book = 'xrp_mxn', 
                    side = 'buy', 
                    order_type = 'limit',              
                    price = df_transactions.price[i],
                    minor = minor_order) 
            )
            return orders



def buy_orders_xrp_mxn(api, mxn_to_convert):
    if float(api.balances().mxn.available)>mxn_to_convert:
        # Get info from orderbook
        df_transactions = orderbook_asks(api, mxn_to_convert)
        orders = place_orders(api, mxn_to_convert, df_transactions)
        
        # check if order passed
        import time
        time.sleep(3)
        # Trades that have already been completed
        utx = api.user_trades()
        utx[0].__dict__
        # Check if order has order id and if it is in open order or in made trades
        for order in orders:
            # check if passed
            order.order_id
            oo = api.open_orders('xrp_mxn')
        # If order is not completed in timeframe then cancel order and place again with new orderbook prices


    else:
        print( 'Not enough MXN funds in account')
    return 



    # Check if orders have been met in a given time window
        # if it is not the case then repeat process with remaining mxn
    
    # Retrieve true fees of opperations

    # withdraw to xrp adress in binance, check that bought xrp are greater than min deposit into binance
        # we might need to modify source code of  package to  include destination tag in ripple_withdrawal
        # for example fork in github and add parameter
    api.ripple_withdrawal(currency='xrp', amount='1.10', address=xrp_address, destination_tag = xrp_memo)






