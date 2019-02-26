from abc import ABC, abstractmethod
from typing import List, Type, Dict, Tuple
import time
import zmq
import influxdb
from influxdb_init import db_client
from mlogging import logger
import collections
import mredis
from decimal import *
import json
import simplejson


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
        assert(name.isupper() or name.isdigit())  # Exchange name needs to be all capitals or digits.
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


class OrderBook:
    def __init__(self, exchange: Exchange, pair: Pair):
        self.exchange = exchange
        self.pair = pair
        self.sell_orders: Dict[Decimal, Decimal] = collections.OrderedDict()  # Sell and buy orders are a dict: price -> volume
        self.buy_orders: Dict[Decimal, Decimal] = collections.OrderedDict()
        self.initial_orders_set = False

    def set_initial_orders(self, sell_orders, buy_orders):
        # assert(len(sell_orders) > 0)
        # assert(len(buy_orders) > 0)
        self.sell_orders = sell_orders
        self.buy_orders = buy_orders
        self.initial_orders_set = True

    def add_order(self, buy: bool, price: Decimal, size: Decimal):
        assert(self.initial_orders_set)
        assert(price > 0)
        assert(size > 0)

        if buy:
            if price not in self.buy_orders:
                self.buy_orders[price] = Decimal(0)
            self.buy_orders[price] += size
            print(self.pair.pair + " Adding buy order at price " + str(price))
        else:
            if price not in self.sell_orders:
                self.sell_orders[price] = Decimal(0)
            self.sell_orders[price] += size
            print(self.pair.pair + "Adding sell order at price " + str(price))

        self.save_order_book()


    def remove_order(self, buy: bool, price: Decimal):
        """
        Removes order at price. Removes fully.
        """
        assert(self.initial_orders_set)
        if buy:
            if price in self.buy_orders:
                del self.buy_orders[price]
            else:
                assert('Price not in buy orders')
        else:
            if price in self.sell_orders:
                del self.sell_orders[price]
            else:
                assert('Price not in sell orders')

        self.save_order_book()

    def update_using_trade(self, buy: bool, price: Decimal, size: Decimal):
        assert(self.initial_orders_set)

        print('xD: ' + self.pair.pair + str(buy))
        if buy:  # If bought then sell order (or a part of it) is fulfilled and vice versa.
            # print(self.sell_orders)
            try:
                self.sell_orders[price] -= size
                assert(self.sell_orders[price] >= 0)
            except KeyError:
                logger.error(self.sell_orders)
                logger.error(price)
                logger.error(list(self.sell_orders.keys())[0])
                logger.error(price == list(self.sell_orders.keys())[0])
                logger.error(price in self.buy_orders)
        else:
            try:
                # print(self.buy_orders)
                self.buy_orders[price] -= size
                assert(self.buy_orders[price] >= 0)
            except KeyError:
                logger.error(self.buy_orders)
                logger.error(price)
                logger.error(list(self.buy_orders.keys())[0])
                logger.error(price == list(self.buy_orders.keys())[0])
                logger.error(price in self.sell_orders)

        self.save_order_book()

    def get_as_json_dict(self):
        assert(self.initial_orders_set)
        json_dict = {}
        json_dict['sell'] = self.sell_orders
        json_dict['buy'] = self.buy_orders

        return json_dict

    def save_order_book(self):
        """
        Saves order book to Redis
        """
        assert(self.initial_orders_set)
        mredis.save_order_book(self)


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
        assert (len(pairs) > 0)

        self.pairs = pairs
        self.time_last_written_trade = time.time()  # Last write that happened to InfluxDB in epoch seconds. Used when service interruption happens inside to record it.

    @abstractmethod
    async def run_blocking(self):
        pass

    def record_trade_interruption(self, exchange: str):
        logger.error('Last successful write at {}, recording interruption of {} sec for exchange {}.'.format(self.time_last_written_trade, int(time.time()) - int(self.time_last_written_trade), exchange))
        zmq_context = zmq.Context()
        zmq_socket = zmq_context.socket(zmq.PUSH)
        zmq_socket.connect("tcp://collector-orchestrator:99991")

        info = {'exchange': exchange, 'start_time': int(self.time_last_written_trade), 'end_time': int(time.time())}
        logger.debug('About to transmit interruption to collector orchestrator, the collector orchestrator needs to confirm.')
        zmq_socket.send_json(info)

    def write_trade(self, trade: TradeInfo):
        assert(isinstance(trade, TradeInfo))

        time_started_send = int(time.time())
        zmq_context = zmq.Context()
        zmq_socket_collector_publisher = zmq_context.socket(zmq.PUSH)
        zmq_socket_collector_publisher.connect("tcp://localhost:27018")
        zmq_socket_collector_publisher.send_json(trade.get_as_json_dict())
        # logger.info(trade.get_as_json_dict())
        # assert(db_client.write_points(trade.get_as_json_dict(), time_precision='n'))  # I have benchmarked what takes the longest here, and this line is the culprit where we write to influxdb.
        ######################################################################## TEMPORARY
        try:
            db_client.write_points(trade.get_as_json_dict(), time_precision='n')
            self.time_last_written_trade = int(time.time())
        except influxdb.exceptions.InfluxDBClientError as e:
            logger.error('InfluxDB error: ' + str(e) + ' data: ' + str(trade.get_as_json_dict()))

        time_to_write = time.time() - time_started_send
        if time_to_write > 0.1:
            logger.warning('It took {} to push trade to collector publisher and write to influxdb'.format(time_to_write))
        else:
            logger.debug('It took {} to push trade to collector publisher and write to influxdb'.format(time_to_write))

    @staticmethod
    @abstractmethod
    def get_all_pairs() -> List[Pair]:
        pass
