from data_api import Pair, Exchange, DataAPI
from typing import List, Type
import cryptowatch


class DataSource:
    def __init__(self, pair : Pair, exchange : Exchange, data_api: DataAPI):
        assert(issubclass(data_api, DataAPI))
        self.pair = pair
        self.exchange = exchange
        self.data_api = data_api

    def get_last_price(self):
        return self.data_api.get_last_price(self.pair, self.exchange)


class PairExchangeSource:
    def __init__(self, pair: Pair, exchange: Exchange):
        self.exchange = exchange
        self.data_sources: List[DataSource] = []


class PairSource:
    def __init__(self, pair: Pair):
        self.pair = pair
        self.exchanges: List[PairExchangeSource] = []

# All we need here is the data sources. We can build the pair and pairexchange sources deriving from datasources.
btcusd = PairSource(Pair('btcusd'))
btcusd_bitfinex = PairExchangeSource(Pair('btcusd'), Exchange('bitfinex'))
btcusd_bitfinex_datasource = DataSource(btcusd.pair, btcusd_bitfinex.exchange, cryptowatch.Cryptowatch)
btcusd_bitfinex.data_sources.append(btcusd_bitfinex_datasource)
btcusd.exchanges.append(btcusd_bitfinex)

print(btcusd_bitfinex_datasource.get_last_price())
