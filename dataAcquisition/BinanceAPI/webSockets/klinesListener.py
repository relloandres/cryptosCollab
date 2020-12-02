import csv
import json
from websockets import BinanceSocketManager

class messageHandler:

    def __init__(self, save_to_file, save_every=60):
        self.save_to_file = save_to_file
        self.msg_counter = 0
        self.save_evry = save_every
        self.current_period_data = []

    def handle_msg(self, msg):
        self.current_period_data.append([msg['e'], msg['E'], msg['s'], msg['k']['i'], msg['k']['t'], msg['k']['T'], msg['k']['f'], msg['k']['L'],msg['k']['o'],msg['k']['c'],msg['k']['h'],msg['k']['l'],msg['k']['v'],msg['k']['q'],msg['k']['n'],msg['k']['x'],msg['k']['V'],msg['k']['Q'],msg['k']['B']])

        if self.msg_counter==self.save_evry-1:

            with open(self.save_to_file, mode='a', newline='') as klines_file:
                klines_writer = csv.writer(klines_file, delimiter=',')
                print(f"Length: {len(self.current_period_data)}")
                for row in self.current_period_data:
                    klines_writer.writerow(row)

            self.current_period_data = []
            self.msg_counter=0
        else:
            self.msg_counter += 1

        # print(self.msg_counter)


# Instantiate a BinanceSocketManager
klines_bm = BinanceSocketManager()
klines_file_path = "/Users/Innomius/Andres/personal/crypto/python-binance/pruebas/develop/klines.csv"
msg_handler = messageHandler(klines_file_path, save_every=5)

# Start trade socket with 'ETHBTC' and use handle_message to.. handle the message.
conn_key = klines_bm.start_kline_socket('ETHBTC', msg_handler.handle_msg)

# then start the socket manager
klines_bm.start()

# # stop the socket manager
# klines_bm.stop_socket(conn_key)