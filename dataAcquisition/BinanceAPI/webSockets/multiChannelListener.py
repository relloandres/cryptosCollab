import csv
import json
from websockets import BinanceSocketManager


def handle_msg(msg):
    print(msg['data']['k']['t'])


# Instantiate a BinanceSocketManager
klines_bm = BinanceSocketManager()

# Start trade socket with 'ETHBTC' and use handle_message to.. handle the message.
# conn_key1 = klines_bm.start_kline_socket('ETHBTC', handle_msg)
# conn_key2 = klines_bm.start_kline_socket('BTCUSDT', handle_msg)
conn_key3 = klines_bm.start_multiplex_socket(
    ['btcusdt@kline_1m', 'ethbtc@kline_1m'], handle_msg)

# then start the socket manager
klines_bm.start()

# # stop the socket manager
# klines_bm.stop_socket(conn_key)
