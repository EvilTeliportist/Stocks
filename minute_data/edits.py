import json

times = ["09/10/2020, 16:01",
"09/10/2020, 16:02",
"09/10/2020, 16:03",
"09/10/2020, 16:04",
"09/10/2020, 16:05"]

temp = {}

with open('minute_data/minute_data.json', 'r') as file:
    data = json.load(file)

for ticker in data:
    t = {}
    for time in data[ticker]:
        if time not in times:
            t.update({time: data[ticker][time]})
    temp.update({ticker: t})

print(temp)

with open("minute_data/minute_data2.json", 'w') as file:
    json.dump(temp, file)
