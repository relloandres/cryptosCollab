import csv
import json
from websockets import BinanceSocketManager
from datetime import datetime


class messageHandler:

    def __init__(self, destination_path, streams_names, save_every=60):
        self.destination_path = destination_path
        self.save_every = save_every
        self.streams_names = streams_names
        self.first_file = {}
        self.msg_counter = {}
        self.current_period_data = {}
        self.current_file_tag = {}

        for stream_name in streams_names:
            self.first_file[stream_name] = True
            self.msg_counter[stream_name] = 0
            self.current_period_data[stream_name] = []
            self.current_file_tag[stream_name] = ''

    def handle_msg(self, msg):
        current_stream_name = msg['stream']
        current_stream_data = msg['data']
        self.current_period_data[current_stream_name].append([current_stream_data['e'], current_stream_data['E'], current_stream_data['s'], current_stream_data['k']['i'], current_stream_data['k']['t'], current_stream_data['k']['T'], current_stream_data['k']['f'], current_stream_data['k']['L'], current_stream_data['k']['o'],
                                         current_stream_data['k']['c'], current_stream_data['k']['h'], current_stream_data['k']['l'], current_stream_data['k']['v'], current_stream_data['k']['q'], current_stream_data['k']['n'], current_stream_data['k']['x'], current_stream_data['k']['V'], current_stream_data['k']['Q'], current_stream_data['k']['B']])
        current_date = datetime.fromtimestamp(current_stream_data['k']['t'] // 1000)
        new_day = (current_date.hour == 0) and (
            current_date.minute == 0) and (current_date.second == 0)

        if self.first_file[current_stream_name]:
            self.first_file[current_stream_name] = False
            self.current_file_tag[current_stream_name] = current_stream_data['k']['t']
            print(f"Stream: {current_stream_name}, first file tag: {self.current_file_tag[current_stream_name]}")

        if new_day:
            self.current_file_tag[current_stream_name] = current_stream_data['k']['t']
            print(f"Stream: {current_stream_name}, new file tag: {self.current_file_tag[current_stream_name]}")

        # TODO: Add functionality to save data when a day ends even if the row limit to save is not reached  
        if self.msg_counter[current_stream_name] == self.save_every-1:
            file_name = self.destination_path + '/' + current_stream_name + '-' + str(self.current_file_tag[current_stream_name]) + '.csv'

            with open(file_name, mode='a', newline='') as klines_file:
                klines_writer = csv.writer(klines_file, delimiter=',')
                print(f"Length: {len(self.current_period_data[current_stream_name])}")
                for row in self.current_period_data[current_stream_name]:
                    klines_writer.writerow(row)

            self.current_period_data[current_stream_name] = []
            self.msg_counter[current_stream_name] = 0
        else:
            self.msg_counter[current_stream_name] += 1


# Instantiate a BinanceSocketManager
klines_bm = BinanceSocketManager()

# Define streams to listen
streams_to_listen = ['btcusdt@kline_1m', 'ethbtc@kline_1m']

# Build message handler
dest_dir = "/home/pi/andres/cryptos/data/binance/websockets/multistreams"
msg_handler = messageHandler(dest_dir, streams_to_listen, save_every=300)

# Start multistream socket
conn = klines_bm.start_multiplex_socket(
    streams_to_listen, msg_handler.handle_msg)

# then start the socket manager
klines_bm.start()

# # stop the socket manager
# klines_bm.stop_socket(conn_key)
