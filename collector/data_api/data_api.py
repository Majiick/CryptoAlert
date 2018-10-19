from abc import ABC, abstractmethod

# Example structure
# pair btcusd:
#   exchange poloniex:
#     data source cryptowatch
#     data source poloniex
# This means that btcusd is traded on poloniex. To get the price data we can either use poloniex api or cryptowatch api.

class Pair:
    def __init__(self, pair: str):
        self.pair = pair


class Exchange:
    def __init__(self, name: str):
        self.name = name


class DataAPI(ABC):
    @staticmethod
    @abstractmethod
    def get_last_price(pair: Pair, exchange: Exchange) -> float:
        pass
