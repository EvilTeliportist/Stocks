from bs4 import BeautifulSoup as soup
import json
import requests
from datetime import datetime, timedelta
import yfinance


with open('dividends/dividends.json', 'r') as file:
    dataset = json.load(file)

def scrapeTickers():
    
    DATE = datetime.now().strftime("%d-%b-%Y")
    URL = 'https://www.dogsofthedow.com/ex-dividend-date-calendar.htm'
    HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.76 Safari/537.36', "Upgrade-Insecure-Requests": "1","DNT": "1","Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8","Accept-Language": "en-US,en;q=0.5","Accept-Encoding": "gzip, deflate"}
    
    response = requests.get(URL, headers = HEADERS)
    page = soup(response.text, 'html.parser')
    table = page.find('tbody')
    rows = table.find_all('tr')

    for row in rows:
        date = row.find('td', {'class': 'column-3'}).text
        if date == DATE:
            ticker = row.find('td', {'class': 'column-1'}).text
            dividendAmount = row.find('td', {'class': 'column-4'}).text
            dataset.append({'ticker': ticker, 'amount': dividendAmount, 'date': date})
        else:
            print(date)
            print(DATE)

    count = 0
    for ticker in dataset:
        yf = yfinance.Ticker(ticker['ticker'])
        hist = yf.history(period='2d')
        boughtAt = hist.iloc[0]['Close']
        soldAt = hist.iloc[-1]['Open']
        profit = round(soldAt - boughtAt, 2)
        dataset[count].update({'boughtAt': boughtAt, 'soldAt': soldAt, 'profit': profit})
        count += 1
    
scrapeTickers()

with open('dividends/dividends.json', 'w') as file:
    json.dump(dataset, file)