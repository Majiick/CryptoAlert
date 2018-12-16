from abc import ABC, abstractmethod
from typing import List, Type, Dict
import time
import zmq
from influxdb_init import db_client


class Pair:
    """
    A market pair in the form of <BaseCurrency>_<MarketCurrency> all capitalized
    """
    def __init__(self, pair: str, structured_properly=True):
        if structured_properly:
            assert('_' in pair)
            assert(pair.isupper())
        self.pair = pair


class Exchange:
    def __init__(self, name: str):
        assert(name.isupper() or name.isdigit())
        self.name = name


class TradeInfo:
    def __init__(self, exchange: Exchange, pair: Pair, buy: bool, size: float, price: float, timestamp=None):
        if timestamp is not None:
            assert(isinstance(timestamp, int))  # Nanosecond time
        self.timestamp = timestamp or time.time_ns()
        assert(self.timestamp > int(time.time() - 86400) * int(float('1e+9')))  # Check if timestamp is in nanoseconds and not more than one day old

        assert(isinstance(exchange, Exchange))
        assert(isinstance(pair, Pair))
        assert(isinstance(buy, bool))
        assert(isinstance(size, float) or isinstance(size, int))
        assert(isinstance(price, float) or isinstance(price, int))

        self.exchange = exchange
        self.pair = pair
        self.buy = buy
        self.size = size
        self.price = price

    def get_as_json_dict(self):
        """
        :return: Python dict object that can be interpreted as JSON and written to influxdb
        """
        return [
                {
                    "measurement": "trade",
                    "time": int(self.timestamp),
                    "tags": {
                        "exchange": self.exchange.name,
                        "pair": self.pair.pair,
                        "buy": self.buy
                    },
                    "fields": {
                        "size": self.size,
                        "price": self.price
                    }
                }
               ]


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
    async def run_blocking(self):
        pass

    @staticmethod
    def write_trade(trade: TradeInfo):
        assert(isinstance(trade, TradeInfo))

        time_started_send = time.time()
        zmq_context = zmq.Context()
        zmq_socket = zmq_context.socket(zmq.PUSH)
        zmq_socket.connect("tcp://localhost:27018")
        zmq_socket.send_json(trade.get_as_json_dict())
        assert(db_client.write_points(trade.get_as_json_dict(), time_precision='n'))
        print('It took {} to push trade to collector publisher and write to influxdb'.format(time.time() - time_started_send))

    @staticmethod
    @abstractmethod
    def get_all_pairs() -> List[Pair]:
        pass
