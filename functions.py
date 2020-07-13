import yfinance as yf
import matplotlib.pyplot as plt
import pandas as pd
import math, datetime, statistics
from scipy.stats import *

STOCKLIST = ['MSFT', 'BAC', 'SPY', 'DIS', 'AMD', 'T', 'WMT', 'AMZN',
                    'NFLX', 'PFE', 'JPM', 'GOOGL', 'XOM', 'PEP', 'BA', 'WFC',
                     'NVDA', 'GDX', 'XLF', 'UAL', 'XLE', 'BABA', 'INTC', 'KO',
                      'HAL', 'GOLD', 'CVS', 'UNH', 'MCD', 'GS', 'C']

def divide_chunks(l, n):
    for i in range(0, len(l), n):
        yield l[i:i + n]

def ironCondorAvgReturn(t, percent, pd, can_print, days_until_exp):

    ticker = yf.Ticker(t)
    hist = [i[3] for i in ticker.history(period=pd).to_numpy()]
    current_price = [i[3] for i in ticker.history(period='1d').to_numpy()][0]

    calls = ticker.option_chain('2020-07-16').calls.to_dict()
    puts = ticker.option_chain('2020-07-16').puts.to_dict()

    percent = (percent / 100)

    upper_bound_price = current_price * (1 + percent)
    lower_bound_price = current_price * (1 - percent)


    # Find CLosest Strike Prices to Percent Given
    lowest_dif_call = [1000, -1]
    lowest_dif_put = [1000, -1]
    for i in range(len(calls['strike'])):
        dif = abs(calls['strike'][i] - upper_bound_price)
        if dif < lowest_dif_call[0]:
            lowest_dif_call = [dif, i]

    for i in range(len(puts['strike'])):
        dif = abs(puts['strike'][i] - lower_bound_price)
        if dif < lowest_dif_put[0]:
            lowest_dif_put = [dif, i]

    # Get Strike Prices
    low_call_strike = calls['strike'][lowest_dif_call[1]]
    high_call_strike = calls['strike'][lowest_dif_call[1] + 1]
    high_put_strike = puts['strike'][lowest_dif_put[1]]
    low_put_strike = puts['strike'][lowest_dif_put[1] - 1]

    # Get Premiums
    low_call_premium = calls['bid'][lowest_dif_call[1]]
    high_call_premium = calls['ask'][lowest_dif_call[1] + 1]
    low_put_premium = puts['ask'][lowest_dif_put[1] - 1]
    high_put_premium = puts['bid'][lowest_dif_put[1]]

    # Get Volumes
    low_call_vol = calls['volume'][lowest_dif_call[1]]
    high_call_vol = calls['volume'][lowest_dif_call[1] + 1]
    low_put_vol = puts['volume'][lowest_dif_put[1] - 1]
    high_put_vol = puts['volume'][lowest_dif_put[1]]

    # Calculate Profits and Loss
    cost_to_open = low_call_premium + high_put_premium - low_put_premium - high_call_premium
    max_profit = round(cost_to_open * 100, 2)
    max_loss = cost_to_open - max((high_put_strike - low_put_strike), (high_call_strike - low_call_strike))
    max_loss *= 100

    upper_break = low_call_strike + cost_to_open
    lower_break = high_put_strike - cost_to_open

    upper_bound_percent = (upper_break - current_price) / current_price
    lower_bound_percent = (lower_break - current_price) / current_price

    # Get Weekly Changes
    changes = []
    for i in range(len(hist) - 1):
        change = (hist[i+1] - hist[i]) / hist[i]
        changes.append(change)

    chunks = list(divide_chunks(changes, 5))
    if len(chunks[-1]) != 5:
        chunks = chunks[:-1]
    weekly = []
    for chunk in chunks:
        weekly.append(sum(chunk) * (days_until_exp / 5))

    # Make Standard Deviation and Mean
    stdev = statistics.stdev(weekly)
    avg = sum(weekly) / len(weekly)

    # Create Normal Distribution
    dist = norm(avg, stdev)

    chance_of_lower = dist.cdf(lower_bound_percent)
    chance_of_higher = 1 - dist.cdf(upper_bound_percent)

    chance_of_loss = chance_of_lower + chance_of_higher

    average_loss = max_loss * chance_of_loss
    average_gain = (1 - chance_of_loss) * max_profit

    average_total = average_loss + average_gain

    if can_print:
        print(t + ": $" + str(round(current_price, 2)) + "  ------- IRON CONDOR")
        print("     Spread Info")
        print("         Call Bought: Strike of $" + str(high_call_strike) + " for $" + str(high_call_premium) + ", VOL: " + str(high_call_vol))
        print("         Call Sold: Strike of $" + str(low_call_strike) + " for $" + str(low_call_premium) + ", VOL: " + str(low_call_vol))
        print("         Put Sold: Strike of $" + str(high_put_strike) + " for $" + str(high_put_premium) + ", VOL: " + str(high_put_vol))
        print("         Put Bought: Strike of $" + str(low_put_strike) + " for $" + str(low_put_premium) + ", VOL: " + str(low_put_vol))
        print("\n     Average Weekly Change (" + pd + "): " + str(round(avg * 100, 2)) + "%")
        print("     Standard Deviation: " + str(round(stdev * 100, 2)) + "%")
        print("     Percent Change to Lose: " + str(round(100 * lower_bound_percent, 2)) + "% or +" + str(round(100 * upper_bound_percent, 2)) + "%")
        print("     Chance to lose: " + str(round(chance_of_loss * 100, 3)) + "%")
        print("     Premium Recieved: $" + str(max_profit))
        print("     Max Loss: $" + str(abs(round(max_loss, 2))))
        print("     Average Return: $" + str(round(average_total, 5)))
        print("     Percentage Kept: " + str(round(average_total * 100 / max_profit, 2)) + "%")
        print("     Return on $1000 investment: " + str(round(math.floor(-1000 / max_loss) * average_total / 10, 2)) + "%")

    return [average_total, max_loss]

def showPlot(t, r, pd):

    profits = []
    percent = []
    for i in range(r):
        try:
            profits.append(ironCondorAvgReturn(t, i + 1, pd))
            percent.append(i + 1)
        except:
            print('error')
    plt.plot(percent, profits)
    plt.show()

def runList(stocks_to_screen, days_until_exp):
    profits = []

    for ticker in stocks_to_screen:
        print(ticker)
        for i in [5, 7]:
            k = ironCondorAvgReturn(ticker, i, '3mo', False, days_until_exp)
            num_pos = math.floor(-1000 / k[1])
            ret = num_pos * k[0]
            profits.append([round(ret / 10, 3), i, ticker])

    print(sorted(profits, key=lambda x: x[0]))

def isMarketOpen():
    d = datetime.datetime.now()
    weekday = d.isoweekday() in range(1, 6)
    hour = ((d.hour * 100) + d.minute) > 930 and d.hour < 16
    return weekday and hour
