import yfinance as yf
import matplotlib.pyplot as plt
import pandas as pd
import math, datetime, statistics
from bar import ProgressBar
from scipy.stats import *

STOCKLIST = ['MSFT', 'BAC', 'SPY', 'DIS', 'AMD', 'T', 'WMT', 'AMZN',
             'NFLX', 'PFE', 'JPM', 'GOOGL', 'XOM', 'PEP', 'BA', 'WFC',
             'NVDA', 'GDX', 'XLF', 'UAL', 'XLE', 'BABA', 'INTC', 'KO',
             'HAL', 'GOLD', 'CVS', 'UNH', 'MCD', 'GS', 'C', 'AAL', 'TSLA',
             'SPCE', 'AAPL', 'NKLA', 'DAL', 'TWTR', 'FB', 'SNAP', 'MU', 'UBER',
             'DKNG', 'F', 'GM', 'NOK', 'SLV', 'AZN', 'V', 'JNJ', 'HD', 'CRM',
             'NKE', 'BP', 'PLUG']

EARNINGS_WEEK = ['MSFT', 'AMD', 'INTC', 'GOOGL', 'KO', 'SNAP', 'T', 'TWTR',
                'AZN', 'AMZN', 'UNH']

def divide_chunks(l, n):
    for i in range(0, len(l), n):
        yield l[i:i + n]

def ironCondorAvgReturn(t, expdate, width = 5, pd = '3mo', can_print = True, days_until_exp = 5, pricetype = ''):

    ticker = yf.Ticker(t)
    hist = [i[3] for i in ticker.history(period=pd).to_numpy()]
    current_price = [i[3] for i in ticker.history(period='1d').to_numpy()][0]

    chain = ticker.option_chain(expdate)
    calls = chain.calls.to_dict()
    puts = chain.puts.to_dict()

    width = (width / 100)

    upper_bound_price = current_price * (1 + width)
    lower_bound_price = current_price * (1 - width)


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
    if pricetype == 'bid/ask':
        low_call_premium = calls['bid'][lowest_dif_call[1]]
        high_call_premium = calls['ask'][lowest_dif_call[1] + 1]
        low_put_premium = puts['ask'][lowest_dif_put[1] - 1]
        high_put_premium = puts['bid'][lowest_dif_put[1]]

    else:
        low_call_premium = calls['lastPrice'][lowest_dif_call[1]]
        high_call_premium = calls['lastPrice'][lowest_dif_call[1] + 1]
        low_put_premium = puts['lastPrice'][lowest_dif_put[1] - 1]
        high_put_premium = puts['lastPrice'][lowest_dif_put[1]]

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
        print("     Return on investment: " + str(round(average_total * -100 / max_loss, 2)) + "%")

    return {'Ticker': t, 'average_total': average_total, 'max_loss': max_loss, 'chance_of_loss': chance_of_loss}

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

def runList(stocks_to_screen, expdate, days_until_exp = 5,  widths = [5, 7]):
    profits = []

    counter = 0
    m = len(stocks_to_screen) * len(widths)
    bar = ProgressBar(0, m)

    for ticker in stocks_to_screen:
        if ticker not in EARNINGS_WEEK:
            for i in widths:
                try:
                    k = ironCondorAvgReturn(ticker, expdate, width = i, can_print = False, days_until_exp = days_until_exp)
                    profits.append([ticker, round(k['average_total'] * -100 / k['max_loss'], 2), i, k['chance_of_loss']])
                    counter += 1
                    bar.update(counter, message = ticker)
                except:
                    counter += 1;
        else:
            counter += 1 * len(widths)

    profits = sorted(profits, key=lambda x: x[1])

    for p in profits:
        if p[1] > 5 and p[3] < .25:
            print(p[0] + "--------")
            print("     ExpRet: " + str(p[1]) + "%")
            print("     Chance of Loss: " + str(round(p[3] * 100, 2)) + "%")
            print("     Width: " + str(p[2]) + "%")

def isMarketOpen():
    d = datetime.datetime.now()
    weekday = d.isoweekday() in range(1, 6)
    hour = ((d.hour * 100) + d.minute) > 930 and d.hour < 16
    return weekday and hour
