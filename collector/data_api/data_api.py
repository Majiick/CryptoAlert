from abc import ABC, abstractmethod
from typing import List, Type, Dict


class Pair:
    def __init__(self, pair: str):
        self.pair = pair


class Exchange:
    def __init__(self, name: str):
        self.name = name


class DataSource:
    def __init__(self, pair : Pair, exchange : Exchange, data_api: Type['DataAPI']):  # Type['DataAPI'] is a forward declaration
        assert(issubclass(data_api, DataAPI))
        self.pair = pair
        self.exchange = exchange
        self.data_api = data_api

    def get_last_price(self):
        return self.data_api.get_last_price(self.pair, self.exchange)


class DataAPI(ABC):
    @staticmethod
    @abstractmethod
    def get_last_price(pair: Pair, exchange: Exchange) -> float:
        pass

    @staticmethod
    @abstractmethod
    def get_data_sources() -> List[DataSource]:
        pass

