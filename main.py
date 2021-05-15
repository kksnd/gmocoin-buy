import hashlib
import hmac
import json
import math
import os
import requests
import sys
import time
from datetime import datetime
from decimal import Decimal, ROUND_HALF_UP

# config
#  - setting
ENDPOINT = 'https://example.com'
VALID_SYMBOLS = set()
MINIMUM_AMOUNT = {}
#  - order
TARGETSYMBOL = ''
BUDGET = 0

# environmental variable
API_KEY = ''
API_SECRET = ''

def load_config(filename: str = 'config.json') -> None:
    global ENDPOINT
    global VALID_SYMBOLS
    global MINIMUM_AMOUNT
    global TARGETSYMBOL
    global BUDGET
    try:
        with open(filename, 'r') as f:
            config = json.load(f)
    except:
        print('Error while loading the json config file')
        sys.exit()
    try:
        ENDPOINT = config['setting']['endpoint']
        VALID_SYMBOLS = set((config['setting']['symbols']))
        MINIMUM_AMOUNT = config['setting']['minamount']
        TARGETSYMBOL = config['order']['targetsymbol']
        BUDGET = int(config['order']['budget'])
    except LookupError as e:
        print(f'{e} was not defined in the config file')
        sys.exit()

def load_env() -> None:
    global API_KEY
    global API_SECRET
    try:
        API_KEY = os.environ['GMOCOIN_API_KEY']
        API_SECRET = os.environ['GMOCOIN_API_SECRET']
    except LookupError as e:
        print(f'Environmental variable {e} was not defined')
        sys.exit()

def is_open() -> bool:
    endpoint = f'{ENDPOINT}/public'
    path = '/v1/status'
    try:
        response  = requests.get(endpoint + path)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(e)
        sys.exit()
    resp_json = response.json()
    print(resp_json)
    return resp_json['status'] == 0 and resp_json['data']['status'] == 'OPEN'


class Ticker:
    elements = ('ask', 'bid', 'high', 'low', 'last')
    def __init__(self, ask: float, bid: float, high: float, low: float, last: float) -> None:
        self.ask  = ask
        self.bid  = bid
        self.high = high
        self.low  = low
        self.last = last

    def mid_price(self) -> float:
        return (self.ask + self.bid) / 2

    def __str__(self) -> str:
        return str({'ask': self.ask, 'bid': self.bid, 'high': self.high, 'low': self.low, 'last': self.last})

def get_ticker(symbol: str) -> Ticker:
    if symbol not in VALID_SYMBOLS:
        print('invalid coin symbol')
        sys.exit()
    endpoint = f'{ENDPOINT}/public'
    path     = f'/v1/ticker?symbol={symbol}'
    try:
        response = requests.get(endpoint + path)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(e)
        sys.exit()
    resp_json = response.json()
    print(resp_json)
    if resp_json['status'] == 0:
        data = {s: float(resp_json['data'][0][s]) for s in Ticker.elements}
        return Ticker(data['ask'], data['bid'], data['high'], data['low'], data['last'])

def get_balance() -> dict:
    timestamp = '{0}000'.format(int(time.mktime(datetime.now().timetuple())))
    method    = 'GET'
    endpoint = f'{ENDPOINT}/private'
    path      = '/v1/account/assets'

    text = timestamp + method + path
    sign = hmac.new(bytes(API_SECRET.encode('ascii')), bytes(text.encode('ascii')), hashlib.sha256).hexdigest()

    headers = {
        "API-KEY": API_KEY,
        "API-TIMESTAMP": timestamp,
        "API-SIGN": sign
    }

    response = requests.get(endpoint + path, headers=headers)
    resp_json = response.json()
    
    balances = {}
    for data in resp_json['data']:
        s = data['symbol']
        if s == 'JPY' or s in VALID_SYMBOLS:
            balances[s] = data['available']
    return balances

def buy_market(symbol: str, amount: str) -> None:
    timestamp = '{0}000'.format(int(time.mktime(datetime.now().timetuple())))
    method    = 'POST'
    endpoint  = f'{ENDPOINT}/private'
    path      = '/v1/order'
    reqBody = {
        "symbol": symbol,
        "side": "BUY",
        "executionType": "MARKET",
        "size": amount
    }

    text = timestamp + method + path + json.dumps(reqBody)
    sign = hmac.new(bytes(API_SECRET.encode('ascii')), bytes(text.encode('ascii')), hashlib.sha256).hexdigest()

    headers = {
        "API-KEY": API_KEY,
        "API-TIMESTAMP": timestamp,
        "API-SIGN": sign
    }

    print('buy request!!!!!!!!!!!')
    #response = requests.post(endpoint + path, headers=headers, data=json.dumps(reqBody))
    #resp_json = response.json()
    #print (json.dumps(resp_json, indent=2))

def main():
    load_config()
    load_env()
    if is_open():
        print('OPEN!')
        print('\n### Get ticker ###')
        ticker = get_ticker(TARGETSYMBOL)
        print(f'  => Current ask price = {ticker.ask}')

        print('\n### Get balance ###')
        balance_dict = get_balance()
        print(balance_dict)
        print(f'  => You have {balance_dict["JPY"]} JPY')

        print('\n### Calculate amount ###')
        print(f'Budget: {BUDGET}')
        # 予算 (BUDGET) 以内、かつ最小注文単位のN倍となる、最大数量を求める
        min_amount = MINIMUM_AMOUNT[TARGETSYMBOL]
        amount = str(math.floor(BUDGET/ticker.ask/float(min_amount)) * float(min_amount))
        str_amount = str(Decimal(amount).quantize(Decimal(min_amount), rounding=ROUND_HALF_UP))
        print(f'  => You will buy {str_amount} {TARGETSYMBOL} (= {int(ticker.ask * float(amount))} JPY)')

        print('\n### Buy ###')
        buy_market(TARGETSYMBOL, str_amount)
    else:
        print('Not OPEN...')

if __name__ == '__main__':
    main()
