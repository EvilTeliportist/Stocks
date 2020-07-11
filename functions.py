import yfinance as yf
import matplotlib.pyplot as plt
import pandas as pd
import math, statistics

def divide_chunks(l, n):
    for i in range(0, len(l), n):
        yield l[i:i + n]

def ironCondorAvgReturn(t, percent, pd):

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
    low_call_premium = calls['ask'][lowest_dif_call[1]]
    high_call_premium = calls['ask'][lowest_dif_call[1] + 1]
    low_put_premium = puts['ask'][lowest_dif_put[1] - 1]
    high_put_premium = puts['ask'][lowest_dif_put[1]]

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
    weekly = []
    for chunk in chunks:
        weekly.append(abs(sum(chunk)))

    # Make Standard Deviation and Mean
    stdev = statistics.stdev(weekly)
    avg = sum(weekly) / len(weekly)

    # Create Normal Distribution
    dist = statistics.NormalDist(mu=avg, sigma=stdev)

    chance_of_lower = dist.cdf(lower_bound_percent)
    chance_of_higher = 1 - dist.cdf(upper_bound_percent)

    chance_of_loss = chance_of_lower + chance_of_higher

    average_loss = max_loss * chance_of_loss
    average_gain = (1 - chance_of_loss) * max_profit

    average_total = average_loss + average_gain

    print(t + ": $" + str(current_price) + "  ------- IRON CONDOR")
    print("     Spread Info")
    print("         Call Bought: Strike of $" + str(high_call_strike) + " for $" + str(high_call_premium))
    print("         Call Sold: Strike of $" + str(low_call_strike) + " for $" + str(low_call_premium))
    print("         Put Sold: Strike of $" + str(high_put_strike) + " for $" + str(high_put_premium))
    print("         Put Bought: Strike of $" + str(low_put_strike) + " for $" + str(low_put_premium))
    print("\n     Average Weekly Change (" + pd + "): " + str(round(avg * 100, 2)) + "%")
    print("     Percent Change to Lose: " + str(round(100 * lower_bound_percent, 2)) + "% or +" + str(round(100 * upper_bound_percent, 2)) + "%")
    print("     Chance to lose: " + str(round(chance_of_loss * 100, 2)) + "%")
    print("     Premium Recieved: $" + str(max_profit))
    print("     Max Loss: $" + str(abs(round(max_loss, 2))))
    print("     Average Return: $" + str(round(average_total, 2)))
    print("     Percentage Kept: " + str(round(average_total * 100 / max_profit, 2)) + "%")

    return average_total



ironCondorAvgReturn('TSLA', 20, '3mo')
