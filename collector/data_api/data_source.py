from typing import List, Dict
from data_api import DataSource, Pair, Exchange
from poloniex import PoloniexWebsocket

# Example structure
# pair btcusd:
#   exchange poloniex:
#     data source cryptowatch
#     data source poloniex
# This means that btcusd is traded on poloniex. To get the price data we can either use poloniex api or cryptowatch api.
import cryptowatch


data_sources: Dict[str, Dict[str, List[DataSource]]] = dict()  # data_sources['btcusd']['poloniex'] = [DataSource1, DataSource2]


def add_data_source(data_source: DataSource):
    if not data_source.pair.pair in data_sources:
        data_sources[data_source.pair.pair] = dict()

    if not data_source.exchange.name in data_sources[data_source.pair.pair]:
        data_sources[data_source.pair.pair][data_source.exchange.name] = list()

    data_sources[data_source.pair.pair][data_source.exchange.name].append(data_source)


for data_source in cryptowatch.Cryptowatch.get_data_sources():
    add_data_source(data_source)

# add_data_source(DataSource(Pair('btcusd'), Exchange('bitfinex'), cryptowatch.Cryptowatch))
# print(data_sources['btcusd']['bitfinex'][0].get_ohlc(1540052198 - 2592000, 1540052198, [60, 180, 300, 900, 1800, 3600, 7200, 14400, 21600, 43200, 86400, 259200, 604800]))

p = PoloniexWebsocket(PoloniexWebsocket.get_all_pairs())
p.run_test()