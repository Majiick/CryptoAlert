from data_api import DataAPI, Pair, Exchange
import requests
import json

class Cryptowatch(DataAPI):
    @staticmethod
    def get_last_price(pair: Pair, exchange: Exchange) -> float:
        r = requests.get('https://api.cryptowat.ch/markets/{}/{}/price'.format(exchange.name, pair.pair))
        json_data = json.loads(r.content)
        return float(json_data['result']['price'])
