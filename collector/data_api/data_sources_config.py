from data_api import Pair, Exchange, DataAPI
from typing import List, Type
import cryptowatch


class DataSource:
    def __init__(self, pair : Pair, exchange : Exchange, data_api: Type[DataAPI]):
        assert(issubclass(data_api, DataAPI))
        self.pair = pair
        self.exchange = exchange
        self.data_api = data_api

    def get_last_price(self):
        return self.data_api.get_last_price(self.pair, self.exchange)



# All we need here is the data sources. We can build the pair and pairexchange sources deriving from datasources.
btcusd_bitfinex_datasource = DataSource(Pair('btcusd'), Exchange('bitfinex'), cryptowatch.Cryptowatch)

print(btcusd_bitfinex_datasource.get_last_price())
