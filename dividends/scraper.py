import logging
import azure.functions as func

from bs4 import BeautifulSoup as soup
import json
import requests
from datetime import datetime, timedelta
import yfinance


def scrapeTickers():
    logging.info("TEST")
    DATE = datetime.now().strftime("%d-%b-%Y")
    URL_DATE = datetime.now().strftime("%Y-%m-%d")
    URL = 'https://api.nasdaq.com/api/calendar/dividends?date=' + URL_DATE
    HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.76 Safari/537.36', "Upgrade-Insecure-Requests": "1","DNT": "1","Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8","Accept-Language": "en-US,en;q=0.5","Accept-Encoding": "gzip, deflate"}
    API_URL = 'https://rtstockdata.azurewebsites.net/dividend_update'

    dailyDataset = []

    response = requests.get(URL, headers = HEADERS).json()
    
    rows = response['data']['calendar']['rows']
    count = 0
    for row in rows:
        try:
            # logging.info(row)
            yf = yfinance.Ticker(row['symbol'])
            hist = yf.history(period='2d')
            boughtAt = hist.iloc[0]['Close']
            soldAt = hist.iloc[-1]['Open']
            profit = round(soldAt - boughtAt + row['dividend_Rate'], 2)
            volume = hist.iloc[-1]['Volume']
            dailyDataset.append({'ticker': row['symbol'], 'exdate': DATE.replace("-", ""), 'boughtAt': boughtAt, 'soldAt': soldAt, 'profit': profit, 'volume': volume, 'amount': row['dividend_Rate']})
            count += 1
        except:
            pass

    
    headers = {'Content-Type': "application/json", 'Accept': "application/json"}
    APIResponse = requests.post(API_URL, headers = headers, json = {'hash':'7A6ECCDB792062797AA4F6BEE12199219EC8749641BA50B3138DD4857A65173D', 'data': dailyDataset})
    # logging.info(APIResponse)

def main(mytimer: func.TimerRequest) -> None:
    if mytimer.past_due:
        logging.info('The timer is past due!')

    scrapeTickers()
    # logging.info('Python timer trigger function ran')
