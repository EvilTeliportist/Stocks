import requests
from bs4 import BeautifulSoup as soup


headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:50.0) Gecko/20100101 Firefox/50.0'}
page = requests.get('https://www.slickcharts.com/sp500', headers=headers)

parsed = soup(page.content, 'html.parser')

table = parsed.find_all('table', class_="table table-hover table-borderless table-sm")

for row in table[0].find_all('tbody')[0].find_all('tr'):
    print('"' + row.find_all('td')[2].text + '", ', end = "")
