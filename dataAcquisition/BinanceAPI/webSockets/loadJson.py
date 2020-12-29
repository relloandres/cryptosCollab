# import json

# with open("./myStreams.json") as json_file:
#     a = json.load(json_file)

# print(a[0]['name'])

from datetime import datetime

current_date = datetime.fromtimestamp(1608842640000 // 1000)

print(current_date)