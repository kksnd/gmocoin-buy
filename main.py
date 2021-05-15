import json
import math
import os
import requests
import sys

END_POINT = 'https://example.com'
VALID_SYMBOLS = ()
MINIMUM_AMOUNT = {}
BUDGET = 0
API_KEY = ''
API_SECRET = ''

def load_config(filename: str = 'config.json'):
    global END_POINT
    global VALID_SYMBOLS
    global MINIMUM_AMOUNT
    global BUDGET
    try:
        with open(filename, 'r') as f:
            config = json.load(f)
    except:
        print('Error while loading the json config file')
        sys.exit()
    try:
        END_POINT = config['endpoint']
        VALID_SYMBOLS = tuple(config['symbols'])
        MINIMUM_AMOUNT = {k: float(v) for k,v in config['minamount'].items()}
        BUDGET = int(config['budget'])
    except LookupError as e:
        print(f'{e} was not defined in the config file')
        sys.exit()

def load_env():
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
        response  = requests.get(END_POINT + path)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(e)
        sys.exit()
    resp_json = response.json()
    print(resp_json)
    return resp_json['status'] == 0 and resp_json['data']['status'] == 'OPEN'


class Ticker:
    elements = ('ask', 'bid', 'high', 'low', 'last')
    def __init__(self, ask: float, bid: float, high: float, low: float, last: float):
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
        response = requests.get(END_POINT + path)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(e)
        sys.exit()
    resp_json = response.json()
    print(resp_json)
    if resp_json['status'] == 0:
        data = {s: float(resp_json['data'][0][s]) for s in Ticker.elements}
        return Ticker(data['ask'], data['bid'], data['high'], data['low'], data['last'])

def buy(coin: str, num: float):
    return

def main():
    load_config()
    load_env()
    if is_open():
        print('OPEN!')
        ticker = get_ticker('BTC')
        print(ticker)
        print(BUDGET)
        # 予算 (BUDGET) 以内、かつ最小注文単位のN倍となる、最大数量を求める
        min_amount = MINIMUM_AMOUNT['BTC']
        amount = math.floor(BUDGET/ticker.ask/min_amount) * min_amount
        print(amount, ticker.ask * amount)
    else:
        print('Not OPEN...')

if __name__ == '__main__':
    main()
