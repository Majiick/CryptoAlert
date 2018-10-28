from abc import ABC, abstractmethod
from typing import List, Type, Dict


class Pair:
    def __init__(self, pair: str):
        self.pair = pair


class Exchange:
    def __init__(self, name: str):
        self.name = name


class DataSource:
    def __init__(self, pair: Pair, exchange: Exchange, data_api: Type['DataAPI']):  # Type['DataAPI'] is a forward declaration
        assert(issubclass(data_api, DataAPI))
        self.pair = pair
        self.exchange = exchange
        self.data_api = data_api

    def get_last_price(self):
        return self.data_api.get_last_price(self.pair, self.exchange)

    def get_ohlc(self, start_time: int, end_time: int, periods: List[int]):
        return self.data_api.get_ohlc(self.pair, self.exchange, start_time, end_time, periods)


class DataAPI(ABC):
    @staticmethod
    @abstractmethod
    def get_last_price(pair: Pair, exchange: Exchange) -> float:
        pass

    @staticmethod
    @abstractmethod
    def get_ohlc(pair: Pair, exchange: Exchange, start_time: int, end_time: int, periods: List[int]):
        '''
        :param start_time: UNIX timespamp, inclusive
        :param end_time: UNIX timespamp, inclusive
        :param periods: The type of periods to get in seconds. e.g. 60 = 1m
        :return:
        '''
        pass

    @staticmethod
    @abstractmethod
    def get_data_sources() -> List[DataSource]:
        pass


class ContinuousDataSource:
    def __init__(self, pair: Pair, exchange: Exchange, data_api: Type['ContinuousDataAPI']):  # Type['ContinuousDataAPI'] is a forward declaration
        assert(issubclass(data_api, ContinuousDataAPI))
        self.pair = pair
        self.exchange = exchange
        self.data_api = data_api


class ContinuousDataAPI(ABC):
    @abstractmethod
    def __init__(self, pairs: List[Pair]):
        self.pairs = pairs

    @abstractmethod
    async def run(self):
        pass

    @staticmethod
    @abstractmethod
    def get_all_pairs() -> List[Pair]:
        pass