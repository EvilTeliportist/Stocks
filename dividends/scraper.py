from bs4 import BeautifulSoup as soup
import json
import requests
from datetime import datetime, timedelta
import yfinance


with open('dividends/dividends.json', 'r') as file:
    dataset = json.load(file)

def scrapeTickers():
    
    DATE = datetime.now().strftime("%d-%b-%Y")
    URL = 'https://api.nasdaq.com/api/calendar/dividends?date=2020-09-30'
    HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.76 Safari/537.36', "Upgrade-Insecure-Requests": "1","DNT": "1","Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8","Accept-Language": "en-US,en;q=0.5","Accept-Encoding": "gzip, deflate"}
    
    dailyDataset = []

    response = requests.get(URL, headers = HEADERS).json()
    
    rows = response['data']['calendar']['rows']
    count = 0
    for row in rows:
        yf = yfinance.Ticker(row['symbol'])
        hist = yf.history(period='2d')
        boughtAt = hist.iloc[0]['Close']
        soldAt = hist.iloc[-1]['Open']
        profit = round(soldAt - boughtAt + row['dividend_Rate'], 2)
        volume = hist.iloc[-1]['Volume']
        dataset.append({'ticker': row['symbol'], 'exdate': DATE, 'boughtAt': boughtAt, 'soldAt': soldAt, 'profit': profit, 'volume': volume, 'amount': row['dividend_Rate']})
        count += 1
    
scrapeTickers()

with open('dividends/dividends.json', 'w') as file:
    json.dump(dataset, file)