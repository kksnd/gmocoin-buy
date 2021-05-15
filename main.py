import hashlib
import hmac
import json
import math
import os
import requests
import sys
import time
from datetime import datetime

# config
#  - setting
ENDPOINT_PUB = 'https://example.com'
ENDPOINT_PRV = 'https://example.com'
VALID_SYMBOLS = set()
MINIMUM_AMOUNT = {}
#  - order
TARGETCOIN = ''
BUDGET = 0

# environmental variable
API_KEY = ''
API_SECRET = ''

def load_config(filename: str = 'config.json') -> None:
    global ENDPOINT_PUB
    global ENDPOINT_PRV
    global VALID_SYMBOLS
    global MINIMUM_AMOUNT
    global TARGETCOIN
    global BUDGET
    try:
        with open(filename, 'r') as f:
            config = json.load(f)
    except:
        print('Error while loading the json config file')
        sys.exit()
    try:
        ENDPOINT_PUB = config['setting']['endpoint']['public']
        ENDPOINT_PRV = config['setting']['endpoint']['private']
        VALID_SYMBOLS = set((config['setting']['symbols']))
        MINIMUM_AMOUNT = {k: float(v) for k,v in config['setting']['minamount'].items()}
        TARGETCOIN = config['order']['targetcoin']
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
    path = '/v1/status'
    try:
        response  = requests.get(ENDPOINT_PUB + path)
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

def get_ticker(coin: str) -> Ticker:
    if coin not in VALID_SYMBOLS:
        print('invalid coin symbol')
        sys.exit()
    path = f'/v1/ticker?symbol={coin}'
    try:
        response = requests.get(ENDPOINT_PUB + path)
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
    path      = '/v1/account/assets'

    text = timestamp + method + path
    sign = hmac.new(bytes(API_SECRET.encode('ascii')), bytes(text.encode('ascii')), hashlib.sha256).hexdigest()

    headers = {
        "API-KEY": API_KEY,
        "API-TIMESTAMP": timestamp,
        "API-SIGN": sign
    }

    response = requests.get(ENDPOINT_PRV + path, headers=headers)
    resp_json = response.json()
    #print (json.dumps(resp_json, indent=2))
    
    balances = {}
    for data in resp_json['data']:
        s = data['symbol']
        if s == 'JPY' or s in VALID_SYMBOLS:
            balances[s] = data['available']
    return balances

def buy(coin: str, num: float) -> None:
    return

def main():
    load_config()
    load_env()
    if is_open():
        print('OPEN!')
        print('\n### get_ticker ###')
        ticker = get_ticker(TARGETCOIN)
        print(f'Current price {ticker.ask}')

        print('\n### get_balance ###')
        balance_dict = get_balance()
        print(balance_dict)

        print('\n### calculate amount ###')
        print(BUDGET)
        # 予算 (BUDGET) 以内、かつ最小注文単位のN倍となる、最大数量を求める
        min_amount = MINIMUM_AMOUNT[TARGETCOIN]
        amount = math.floor(BUDGET/ticker.ask/min_amount) * min_amount
        print(amount, ticker.ask * amount)
    else:
        print('Not OPEN...')

if __name__ == '__main__':
    main()
