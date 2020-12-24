import csv
import json
from websockets import BinanceSocketManager
from datetime import datetime


class messageHandler:

    def __init__(self, destination_path, file_prefix, save_every=60):
        self.destination_path = destination_path
        self.first_file = True
        self.file_prefix = file_prefix
        self.msg_counter = 0
        self.save_every = save_every
        self.current_period_data = []
        self.current_file_tag = ''

    def handle_msg(self, msg):
        self.current_period_data.append([msg['e'], msg['E'], msg['s'], msg['k']['i'], msg['k']['t'], msg['k']['T'], msg['k']['f'], msg['k']['L'], msg['k']['o'],
                                         msg['k']['c'], msg['k']['h'], msg['k']['l'], msg['k']['v'], msg['k']['q'], msg['k']['n'], msg['k']['x'], msg['k']['V'], msg['k']['Q'], msg['k']['B']])
        current_date = datetime.fromtimestamp(msg['k']['t'] // 1000)
        new_day = (current_date.hour == 0) and (
            current_date.minute == 0) and (current_date.second == 0)

        if self.first_file:
            self.first_file = False
            self.current_file_tag = msg['k']['t']
            print(f"First file tag: {self.current_file_tag}")

        if new_day:
            self.current_file_tag = msg['k']['t']
            print(f"New file tag: {self.current_file_tag}")

        if self.msg_counter == self.save_every-1:
            file_name = self.destination_path + '/' + \
                self.file_prefix + '-' + str(self.current_file_tag) + '.csv'

            with open(file_name, mode='a', newline='') as klines_file:
                klines_writer = csv.writer(klines_file, delimiter=',')
                print(f"Length: {len(self.current_period_data)}")
                for row in self.current_period_data:
                    klines_writer.writerow(row)

            self.current_period_data = []
            self.msg_counter = 0
        else:
            self.msg_counter += 1

        # print(self.msg_counter)


# Instantiate a BinanceSocketManager
klines_bm = BinanceSocketManager()
dest_dir = "/home/pi/andres/cryptos/data/binance/websockets"
prefix = "btcusdt"
msg_handler = messageHandler(dest_dir, prefix, save_every=300)

# Start trade socket with 'ETHBTC' and use handle_message to.. handle the message.
conn_key = klines_bm.start_kline_socket('BTCUSDT', msg_handler.handle_msg)

# then start the socket manager
klines_bm.start()

# # stop the socket manager
# klines_bm.stop_socket(conn_key)
