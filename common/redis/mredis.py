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
import simplejson

MAX_ORDER_BOOK_HISTORY = 100

r = redis.Redis(host='redis', port=6379, db=0)


def save_order_book(order_book):
    print('Saving order book')
    json_dict = order_book.get_as_json_dict()
    assert['sell' in json_dict]
    assert['buy' in json_dict]
    json_string = simplejson.dumps(json_dict, use_decimal=True)
    r.lpush(order_book.exchange.name + order_book.pair.pair, json_string)
    r.ltrim(order_book.exchange.name + order_book.pair.pair, 0, MAX_ORDER_BOOK_HISTORY)
