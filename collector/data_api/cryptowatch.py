from data_api import DataAPI, Pair, Exchange, DataSource
from typing import List
import requests
import json

class Cryptowatch(DataAPI):
    @staticmethod
    def get_last_price(pair: Pair, exchange: Exchange) -> float:
        r = requests.get('https://api.cryptowat.ch/markets/{}/{}/price'.format(exchange.name, pair.pair))
        json_data = json.loads(r.content)
        return float(json_data['result']['price'])

    @staticmethod
    def get_data_sources() -> List[DataSource]:
        r = requests.get('https://api.cryptowat.ch/markets')
        json_data = json.loads(r.content)

        ret: List[DataSource] = list()

        for exchange_and_market in json_data['result']:
            # The result has one more attribute called 'active' which is a boolean.
            # Take the result into account at a future date.
            pair = Pair(exchange_and_market['pair'])
            exchange = Exchange(exchange_and_market['exchange'])
            ret.append(DataSource(pair, exchange, Cryptowatch))

        return ret