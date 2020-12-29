import csv
import json
from websockets import BinanceSocketManager
from datetime import datetime
import time


STREAMS_PERIODS = {
    "_1m": 60000,
    "_3m": 180000,
    "_5m": 300000,
    "_15m": 900000,
    "_30m": 1800000,
    "_1h": 3600000,
    "_2h": 7200000,
    "_4h": 14400000,
    "_6h": 21600000,
    "_8h": 28800000,
    "_12h": 43200000,
    "_1d": 86400000,
    "_3d": 259200000,
    "_1w": 604800000
}


class streamListener:

    def __init__(self, streams_info):
        # self.mocked_file_tag = 0

        # Instantiate a BinanceSocketManager
        self.binance_client = BinanceSocketManager()
        self.current_connection = ''

        self.streams_info = streams_info

        self.streams_names = []
        self.streams_destination_path = {}
        self.streams_periods = {}
        self.streams_save_frecuency = {}

        self.streams_last_checkpoint = {}
        self.first_file = {}
        self.current_period_data = {}
        self.current_file_tag = {}

        for stream_info in streams_info:
            current_stream_name = stream_info['name']

            self.streams_names.append(current_stream_name)
            self.streams_destination_path[current_stream_name] = stream_info['destinationPath']
            self.streams_periods[current_stream_name] = STREAMS_PERIODS[stream_info['periodLength']]
            self.streams_save_frecuency[current_stream_name] = stream_info['saveFrecuency']

            self.first_file[current_stream_name] = True
            self.current_period_data[current_stream_name] = []
            self.current_file_tag[current_stream_name] = ''

    def create_socket_connections(self):
        self.current_connection = self.binance_client.start_multiplex_socket(
            self.streams_names, self.handle_msg)

    def stop_socket_connection(self):
        self.binance_client.stop_socket(self.current_connection)

    def start_listening(self):
        self.create_socket_connections()
        # then start the socket manager
        self.binance_client.start()

    def restart_connection(self):
        print("RESTARTING CONNECTION:")
        self.stop_socket_connection()
        print(" - Connections stopped")
        time.sleep(3)
        self.create_socket_connections()
        print(" - Connections created")

    def new_day_checkpoint(self, millis_time):
        for stream_name in self.streams_names:
            self.streams_last_checkpoint[stream_name] = millis_time

    def handle_msg(self, msg):
        current_stream_name = msg['stream']
        current_stream_data = msg['data']

        if current_stream_name not in self.streams_names:
            print(f"Unknown stream name: {current_stream_name}")

        current_date = datetime.fromtimestamp(
            current_stream_data['k']['t'] // 1000)
        new_day = (current_date.hour == 0) and (
            current_date.minute == 0) and (current_date.second == 0)
        # new_day = current_date.minute % 2 == 0

        if self.first_file[current_stream_name]:
            self.first_file[current_stream_name] = False
            self.current_file_tag[current_stream_name] = current_stream_data['k']['t']
            self.streams_last_checkpoint[current_stream_name] = current_stream_data['k']['t']
            print(
                f"Stream: {current_stream_name}, First file tag: {self.current_file_tag[current_stream_name]}, At: {current_date}")

        if new_day:
            if (current_stream_data['k']['t'] != self.streams_last_checkpoint[current_stream_name]):
                self._save_data(current_stream_name)
                self.new_day_checkpoint(current_stream_data['k']['t'])
                self.current_period_data[current_stream_name].append([current_stream_data['e'], current_stream_data['E'], current_stream_data['s'], current_stream_data['k']['i'], current_stream_data['k']['t'], current_stream_data['k']['T'], current_stream_data['k']['f'], current_stream_data['k']['L'], current_stream_data['k']['o'],
                                                                      current_stream_data['k']['c'], current_stream_data['k']['h'], current_stream_data['k']['l'], current_stream_data['k']['v'], current_stream_data['k']['q'], current_stream_data['k']['n'], current_stream_data['k']['x'], current_stream_data['k']['V'], current_stream_data['k']['Q'], current_stream_data['k']['B']])
                self.current_file_tag[current_stream_name] = current_stream_data['k']['t']
                print(
                    f"Stream: {current_stream_name}, New file tag: {self.current_file_tag[current_stream_name]}, At: {current_date}")
                self.restart_connection()
                # self.mocked_file_tag += 1
        else:
            trigger_save_process = (current_stream_data['k']['t']-self.streams_last_checkpoint[current_stream_name]
                                    ) // self.streams_periods[current_stream_name] == self.streams_save_frecuency[current_stream_name]
            if trigger_save_process:
                self._save_data(current_stream_name)
                self.streams_last_checkpoint[current_stream_name] = current_stream_data['k']['t']
                print(
                    f"Stream: {current_stream_name}, File tag: {self.current_file_tag[current_stream_name]}, At: {current_date}")

            self.current_period_data[current_stream_name].append([current_stream_data['e'], current_stream_data['E'], current_stream_data['s'], current_stream_data['k']['i'], current_stream_data['k']['t'], current_stream_data['k']['T'], current_stream_data['k']['f'], current_stream_data['k']['L'], current_stream_data['k']['o'],
                                                                  current_stream_data['k']['c'], current_stream_data['k']['h'], current_stream_data['k']['l'], current_stream_data['k']['v'], current_stream_data['k']['q'], current_stream_data['k']['n'], current_stream_data['k']['x'], current_stream_data['k']['V'], current_stream_data['k']['Q'], current_stream_data['k']['B']])

    def _save_data(self, stream_name):
        file_name = self.streams_destination_path[stream_name] + '/' + \
            stream_name + '-' + \
            str(self.current_file_tag[stream_name]) + '.csv'
        # file_name = self.streams_destination_path[stream_name] + \
        #     '/' + stream_name + '-' + str(self.mocked_file_tag) + '.csv'

        with open(file_name, mode='a', newline='') as klines_file:
            klines_writer = csv.writer(klines_file, delimiter=',')
            print(f"{len(self.current_period_data[stream_name])} rows saved")
            for row in self.current_period_data[stream_name]:
                klines_writer.writerow(row)

        self.current_period_data[stream_name] = []


# Load streams info
with open("/Users/Innomius/Andres/personal/myGithub/cryptosCollab/dataAcquisition/BinanceAPI/webSockets/myStreams.json") as json_file:
    my_streams_info = json.load(json_file)

# Instantiate a client
klines_bm = streamListener(my_streams_info)

# Satrt listening
klines_bm.start_listening()

# print("Stopping connection")
# klines_bm.binance_client.stop_socket(klines_bm.current_connection)
# print(" - Connections ended")
# klines_bm.binance_client.reactor.callFromThread(
#     klines_bm.binance_client.reactor.stop)
# klines_bm.binance_client.join()
# print(" - Thread ended")

# # stop the socket manager
# klines_bm.stop_socket(conn_key)
