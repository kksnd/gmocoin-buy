import requests
import json

END_POINT = 'https://api.coin.z.com/public'

def is_open():
    path      = '/v1/status'
    response  = requests.get(END_POINT + path)
    resp_json = response.json()
    print(resp_json)
    return resp_json['status'] == 0 and resp_json['data']['status'] == 'OPEN'

def main():
    if is_open():
        print('OPEN!')
    else:
        print('Not OPEN...')

if __name__ == '__main__':
    main()
