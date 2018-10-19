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
        pass
