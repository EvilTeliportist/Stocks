from functions import *
import json, math


def daily():
    with open('stored_options.json') as file:
        data = json.load(file)

    exp = ''
    date = '2020-07-12'

    for stock in STOCKLIST:
        ticker = yf.Ticker(stock)
        options = ticker.option_chain()
        calls = format_options(options.calls.to_dict())
        puts = format_options(options.puts.to_dict())
        if exp == '':
            exp = options.calls.to_dict()['contractSymbol'][0].split('C')[0].split(stock)[1]
            exp = "20" + date[0:2] + "-" + date[2:4] + "-" + date[4:6]

        if date not in data.keys():
            data[date] = {}

        if stock not in data[date].keys():
            data[date][stock] = {}

        data[date][stock][exp] = {}

        data[date][stock][exp]['calls'] = calls
        data[date][stock][exp]['puts'] = puts

        print(stock + ": done...")

    with open('stored_options.json', 'w') as file:
        json.dump(data, file)

def format_options(options):
    temp = {}
    for i in range(len(options['strike'])):
        strike = options['strike'][i]
        bid = options['bid'][i]
        ask = options['ask'][i]
        lastPrice = options['lastPrice'][i]
        volume = options['volume'][i]

        if math.isnan(volume):
            volume = 0

        if math.isnan(bid):
            bid = 0

        if math.isnan(ask):
            ask = 0

        if math.isnan(lastPrice):
            lastPrice = 0


        temp.update({strike: {'bid': bid, 'ask': ask, 'lastPrice': lastPrice, 'volume':volume}})
    return temp

daily()
