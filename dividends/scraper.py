from bs4 import BeautifulSoup as soup
import json
import requests
from datetime import datetime


def scrapeTickers():
    DATE = datetime.now().strftime("%m/%d/%Y")[1:]
    URL = 'https://www.marketbeat.com/dividends/ex-dividend-date-list/'
    HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.76 Safari/537.36', "Upgrade-Insecure-Requests": "1","DNT": "1","Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8","Accept-Language": "en-US,en;q=0.5","Accept-Encoding": "gzip, deflate"}
    
    dailyTickers = []

    print(DATE)
    
    response = requests.get(URL, headers = HEADERS)
    page = soup(response.text, 'html.parser')
    table = page.find('table')
    rows = table.find_all('tr')
    for row in rows:
        ticker = row.find('div', {'class':'ticker-area'})
        if ticker != None:
            tickerExDate = row.find_all('td')[5].text
            if tickerExDate == DATE:
                dailyTickers.append(ticker.text)

    return dailyTickers


print(scrapeTickers())
