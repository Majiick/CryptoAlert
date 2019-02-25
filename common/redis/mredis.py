"""
Redis is used to store the latest snapshot of order books.
The schema is a bunch of lists containing the full JSON object of the order book.
Schema:
    list 'POLONIEX_BTC_USD' [LatestOrderBook, SecondLastOrderBook...]
    list 'BITTREX_ETH_BTC' [LatestOrderBook, SecondLastOrderBook...]

You can use LPUSH together with LTRIM to create a list that never exceeds a given number of elements, but just remembers the latest N elements.
e.g. LPUSH mylist someelement
     LTRIM mylist 0 99


"""

import redis
import json
from typing import List, Type, Dict
from mlogging import logger

MAX_ORDER_BOOK_HISTORY = 100

r = redis.Redis(host='redis', port=6379, db=0)


def save_order_book(order_book):
    r.lpush(order_book.exchange.name + order_book.pair.pair, json.dumps(order_book.get_as_json_dict()))
    r.ltrim(order_book.exchange.name + order_book.pair.pair, MAX_ORDER_BOOK_HISTORY)
