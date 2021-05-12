import json
import math
import requests

END_POINT = 'https://example.com'
VALID_SYMBOLS = ()
MINIMUM_AMOUNT = {}
BUDGET = 0

def load_config(filename: str = 'config.json'):
    global END_POINT
    global VALID_SYMBOLS
    global MINIMUM_AMOUNT
    global BUDGET
    with open(filename, 'r') as f:
        config = json.load(f)
    END_POINT = config['endpoint']
    VALID_SYMBOLS = tuple(config['symbols'])
    MINIMUM_AMOUNT = {k: float(v) for k,v in config['minamount'].items()}
    BUDGET = int(config['budget'])

def is_open() -> bool:
    path = '/v1/status'
    try:
        response  = requests.get(END_POINT + path)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(e)
        exit
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
        exit
    path = f'/v1/ticker?symbol={coin}'
    try:
        response = requests.get(END_POINT + path)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(e)
        exit
    resp_json = response.json()
    print(resp_json)
    if resp_json['status'] == 0:
        data = {s: float(resp_json['data'][0][s]) for s in Ticker.elements}
        return Ticker(data['ask'], data['bid'], data['high'], data['low'], data['last'])

def buy(coin: str, num: float):
    return

def main():
    load_config()
    print(MINIMUM_AMOUNT)
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
