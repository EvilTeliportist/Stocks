import asyncio, json, datetime, time
from aiohttp import ClientSession
from bs4 import BeautifulSoup as soup

tickers = ["AAPL", "MSFT", "AMZN", "FB", "GOOGL", "GOOG", "BRK-B", "JNJ", "PG", "V", "JPM", "NVDA", "HD", "MA", "UNH", "VZ", "DIS", "ADBE", "CRM", "PYPL", "MRK", "NFLX", "INTC", "T", "CMCSA", "PFE", "BAC", "KO", "WMT", "PEP", "ABT", "TMO", "CSCO", "MCD", "ABBV", "XOM", "COST", "ACN", "NKE", "CVX", "AVGO", "AMGN", "MDT", "NEE", "BMY", "UNP", "LIN", "DHR", "QCOM", "PM", "TXN", "LLY", "LOW", "ORCL", "HON", "UPS", "AMT", "IBM", "C", "SBUX", "LMT", "MMM", "CHTR", "WFC", "RTX", "FIS", "AMD", "BA", "NOW", "SPGI", "BLK", "CAT", "GILD", "MDLZ", "INTU", "ISRG", "MO", "ZTS", "CVS", "TGT", "PLD", "BKNG", "BDX", "AXP", "DE", "VRTX", "D", "EQIX", "CCI", "APD", "CL", "ANTM", "TMUS", "TJX", "SYK", "CI", "GS", "DUK", "MS", "ATVI", "MMC", "CSX", "CME", "BSX", "ADP", "SHW", "ITW", "NSC", "FDX", "PGR", "SO", "REGN", "CB", "ICE", "NEM", "NOC", "FISV", "GE", "HUM", "TFC", "MU", "ILMN", "DG", "EW", "KMB", "AMAT", "ECL", "USB", "ADSK", "GPN", "EL", "PNC", "AON", "MCO", "BIIB", "WM", "DD", "LRCX", "BAX", "ADI", "ROP", "ETN", "EMR", "SCHW", "LHX", "DLR", "AEP", "GM", "CTSH", "DOW", "EA", "XEL", "COP", "DXCM", "HCA", "ORLY", "GIS", "EBAY", "EXC", "SRE", "SBAC", "GD", "CMG", "PSA", "CNC", "TEL", "COF", "ROST", "SYY", "STZ", "IDXX", "JCI", "INFO", "APH", "CMI", "TWTR", "MNST", "A", "SNPS", "WEC", "PPG", "MET", "VRSK", "ALL", "BK", "AZO", "PCAR", "TRV", "MSCI", "IQV", "TROW", "ZBH", "CDNS", "TT", "YUM", "ES", "HPQ", "KR", "PRU", "F", "KLAC", "MAR", "ANSS", "CLX", "PH", "BLL", "CTAS", "WLTW", "PEG", "MSI", "AFL", "ADM", "WBA", "ROK", "AWK", "TDG", "FAST", "PSX", "KMI", "MCHP", "SLB", "WELL", "AIG", "SWK", "HLT", "GLW", "RMD", "BBY", "WMB", "OTIS", "MCK", "MKC", "ED", "XLNX", "DHI", "PAYX", "CARR", "MTD", "FCX", "ALXN", "STT", "FTV", "ALGN", "SWKS", "DTE", "CHD", "EOG", "AME", "VFC", "O", "LEN", "CTVA", "CERN", "APTV", "HSY", "DLTR", "PPL", "WY", "CPRT", "AVB", "LUV", "VRSN", "MPC", "RSG", "WST", "ARE", "KHC", "EFX", "FLT", "AJG", "EIX", "EQR", "LYB", "VLO", "ETR", "TSN", "AMP", "ODFL", "AEE", "DAL", "FRC", "MXIM", "KSU", "LH", "LVS", "AMCR", "CMS", "KEYS", "AKAM", "DFS", "TTWO", "TFX", "MKTX", "NTRS", "KMX", "CAG", "VMC", "DOV", "K", "TSCO", "VTR", "HOLX", "COO", "CDW", "FE", "VAR", "VIAC", "CBRE", "INCY", "FTNT", "GWW", "MAS", "EXPD", "BR", "IP", "PXD", "CTXS", "DPZ", "XYL", "PEAK", "FITB", "DGX", "GPC", "GRMN", "BF-B", "NDAQ", "EXR", "QRVO", "CAH", "ABC", "NVR", "FMC", "ESS", "HIG", "SYF", "NUE", "HRL", "STE", "DRE", "IEX", "ZBRA", "MTB", "CHRW", "MAA", "ULTA", "EXPE", "MLM", "PAYC", "TYL", "PKI", "IFF", "CE", "SIVB", "SJM", "WAT", "URI", "HAL", "LNT", "IR", "WAB", "TIF", "KEY", "J", "ABMD", "BXP", "HPE", "JKHY", "EVRG", "RCL", "ETFC", "CFG", "AES", "CINF", "LDOS", "JBHT", "FBHS", "TDY", "PHM", "NLOK", "OMC", "DRI", "MGM", "IT", "HES", "ATO", "RF", "ANET", "EMN", "WDC", "BIO", "OKE", "WHR", "STX", "AAP", "CNP", "PFG", "CTL", "ALB", "NTAP", "HBAN", "HAS", "AVY", "LKQ", "CBOE", "FOXA", "UDR", "PKG", "XRAY", "HSIC", "WU", "LW", "ALLE", "UAL", "OXY", "WRB", "RJF", "UHS", "BKR", "CXO", "TXT", "BWA", "L", "IRM", "CCL", "WRK", "RE", "DISH", "GL", "NI", "SNA", "LYV", "NRG", "HST", "PNW", "WYNN", "DVA", "MYL", "JNPR", "CPB", "ROL", "COG", "PNR", "PWR", "CF", "AIZ", "FFIV", "HWM", "LNC", "AOS", "IPG", "NWL", "PRGO", "DISCK", "TAP", "AAL", "REG", "MOS", "LB", "SEE", "RHI", "HII", "MHK", "LEG", "CMA", "BEN", "NWSA", "IPGP", "HBI", "FRT", "ZION", "VNO", "AIV", "NLSN", "DXC", "ALK", "PVH", "KIM", "FANG", "FLIR", "PBCT", "NCLH", "FOX", "TPR", "APA", "NBL", "NOV", "IVZ", "UNM", "RL", "SLG", "FLS", "MRO", "DISCA", "GPS", "XRX", "DVN", "KSS", "HFC", "HRB", "FTI", "UAA", "UA", "NWS", "COTY"]

with open('minute_data.json', 'r') as file:
    data = json.load(file)


async def fetch(url, session):
    async with session.get(url) as response:
        return await response.read()

def find_price_from_page(page, i):
    try:
        parsed = soup(page, 'html.parser')
        price = float(parsed.find_all('div', class_='D(ib) Mend(20px)')[0].findChildren("span")[0].text.replace(",", ""))
        return price
    except:
        print("error: " + tickers[i])

async def run():
    url = 'https://finance.yahoo.com/quote/'
    tasks = []

    # Fetch all responses within one Client session,
    # keep connection alive for all requests.
    async with ClientSession() as session:
        for ticker in tickers[:500]:
            #print(url + ticker)
            task = asyncio.ensure_future(fetch(url + ticker, session))
            tasks.append(task)
            print(ticker)

        responses = await asyncio.gather(*tasks)
        # you now have all response bodies in this variable

        for i in range(len(responses)):
            price = find_price_from_page(str(responses[i]), i)
            ticker = tickers[i]
            time = datetime.datetime.now().strftime("%m/%d/%Y, %H:%M")

            if ticker in data.keys():
                if time not in data[ticker].keys():
                    data[ticker][time] = price
            else:
                data[ticker] = {time: price}

        with open('minute_data.json', 'w') as file:
            json.dump(data, file)

loop = asyncio.get_event_loop()
future = asyncio.ensure_future(run())
loop.run_until_complete(future)
