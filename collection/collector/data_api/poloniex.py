from data_api import DataAPI, Pair, Exchange, DataSource, ContinuousDataSource, ContinuousDataAPI, TradeInfo, OrderBook
from typing import List, Type, Dict, Tuple
import requests
import json
import websockets
import asyncio
import time
import zmq
import mlogging
from mlogging import logger
import sys
import traceback
import collections
from decimal import *


WEBSOCKET_PAIRS = {'BTC_BCN': 7, 'BTC_BTS': 14, 'BTC_BURST': 15, 'BTC_CLAM': 20,
                   'BTC_DGB': 25, 'BTC_DOGE': 27, 'BTC_DASH': 24, 'BTC_GAME': 38,
                   'BTC_HUC': 43, 'BTC_LTC': 50, 'BTC_MAID': 51, 'BTC_OMNI': 58,
                   'BTC_NAV': 61, 'BTC_NMC': 64, 'BTC_NXT': 69, 'BTC_PPC': 75,
                   'BTC_STR': 89, 'BTC_SYS': 92, 'BTC_VIA': 97, 'BTC_VTC': 100,
                   'BTC_XCP': 108, 'BTC_XMR': 114, 'BTC_XPM': 116, 'BTC_XRP': 117,
                   'BTC_XEM': 112, 'BTC_ETH': 148, 'BTC_SC': 150, 'BTC_FCT': 155,
                   'BTC_DCR': 162, 'BTC_LSK': 163, 'BTC_LBC': 167, 'BTC_STEEM': 168,
                   'BTC_SBD': 170, 'BTC_ETC': 171, 'BTC_REP': 174, 'BTC_ARDR': 177,
                   'BTC_ZEC': 178, 'BTC_STRAT': 182, 'BTC_PASC': 184, 'BTC_GNT': 185,
                   'BTC_BCH': 189, 'BTC_ZRX': 192, 'BTC_CVC': 194, 'BTC_OMG': 196,
                   'BTC_GAS': 198, 'BTC_STORJ': 200, 'BTC_EOS': 201, 'BTC_SNT': 204,
                   'BTC_KNC': 207, 'BTC_BAT': 210, 'BTC_LOOM': 213, 'BTC_QTUM': 221,
                   'BTC_BNT': 232, 'BTC_MANA': 229, 'USDT_BTC': 121, 'USDT_DOGE': 216,
                   'USDT_DASH': 122, 'USDT_LTC': 123, 'USDT_NXT': 124, 'USDT_STR': 125,
                   'USDT_XMR': 126, 'USDT_XRP': 127, 'USDT_ETH': 149, 'USDT_SC': 219,
                   'USDT_LSK': 218, 'USDT_ETC': 173, 'USDT_REP': 175, 'USDT_ZEC': 180,
                   'USDT_GNT': 217, 'USDT_BCH': 191, 'USDT_ZRX': 220, 'USDT_EOS': 203,
                   'USDT_SNT': 206, 'USDT_KNC': 209, 'USDT_BAT': 212, 'USDT_LOOM': 215,
                   'USDT_QTUM': 223, 'USDT_BNT': 234, 'USDT_MANA': 231, 'XMR_BCN': 129,
                   'XMR_DASH': 132, 'XMR_LTC': 137, 'XMR_MAID': 138, 'XMR_NXT': 140,
                   'XMR_ZEC': 181, 'ETH_LSK': 166, 'ETH_STEEM': 169, 'ETH_ETC': 172,
                   'ETH_REP': 176, 'ETH_ZEC': 179, 'ETH_GNT': 186, 'ETH_BCH': 190, 'ETH_ZRX': 193,
                   'ETH_CVC': 195, 'ETH_OMG': 197, 'ETH_GAS': 199, 'ETH_EOS': 202, 'ETH_SNT': 205,
                   'ETH_KNC': 208, 'ETH_BAT': 211, 'ETH_LOOM': 214, 'ETH_QTUM': 222, 'ETH_BNT': 233,
                   'ETH_MANA': 230, 'USDC_BTC': 224, 'USDC_USDT': 226, 'USDC_ETH': 225}

WEBSOCKET_PAIRS_INVERTED = {v: k for k, v in WEBSOCKET_PAIRS.items()}


class PoloniexWebsocket(ContinuousDataAPI):
    def __init__(self, pairs: List[Pair]):
        super().__init__(pairs)
        self.order_books: Dict[str, OrderBook] = {}
        for pair in pairs:
            self.order_books[pair.pair] = OrderBook(Exchange('POLONIEX'), pair)

    @staticmethod
    def get_all_pairs() -> List[Pair]:
        ret = []

        for k, v in WEBSOCKET_PAIRS.items():
            ret.append(Pair(k))

        return ret

    async def write_ticker(self, ticker_update):
        """
        :param ticker_update: Array of
              [
                <currency pair id>,
                "<last trade price>",
                "<lowest ask>",
                "<highest bid>",
                "<percent change in last 24 hours>",
                "<base currency volume in last 24 hours>",
                "<quote currency volume in last 24 hours>",
                <is frozen>,
                "<highest trade price in last 24 hours>",
                "<lowest trade price in last 24 hours>"
              ]
        """

        json_body = [
            {
                "measurement": "ticker",
                "tags": {
                    "exchange": "poloniex",
                    "pair": WEBSOCKET_PAIRS_INVERTED[ticker_update[0]]
                },
                "time": time.time_ns(),
                "fields": {
                    "price": ticker_update[1],
                }
            }
        ]

        db_client.create_retention_policy('retention_policy', '3d', 3, default=True)
        db_client.write_points(json_body)
        logger.debug("Written ticker update")

    async def run_tickers(self):
        websocket = await websockets.connect('wss://api2.poloniex.com')
        await websocket.send(json.dumps({'command': 'subscribe', 'channel': '1002'}))  # 1002 is Ticker channel
        ack = await websocket.recv()  # Wait and discard acknowledgement
        assert (json.loads(ack)[0] == 1002 and json.loads(ack)[1] == 1)  # Check if acknowledgement is successful.

        while True:
            data = await websocket.recv()
            data = json.loads(data)

            if data[0] == 1002:  # 1002 is Ticker channel
                currency_update = data[2]
                await self.write_ticker(currency_update)

    async def write_order_dump(self, order_dump):
        """
        :param order_dump: [
                            [
                              "i",
                              {
                                "currencyPair": "<currency pair name>",
                                "orderBook": [
                                  {
                                    "<lowest ask price>": "<lowest ask size>",
                                    "<next ask price>": "<next ask size>",
                                    …
                                  },
                                  {
                                    "<highest bid price>": "<highest bid size>",
                                    "<next bid price>": "<next bid size>",
                                    …
                                  }
                                ]
                              }
                            ]
                          ]
        :param pair_id: Pair id described in WEBSOCKET_PAIRS
        :return:
        """

        pair_name = order_dump[0][1]['currencyPair']
        write_time = int(time.time_ns())
        writes = []

        sell_orders = collections.OrderedDict()
        buy_orders = collections.OrderedDict()
        print(pair_name)
        rank = 0
        for price, size in order_dump[0][1]['orderBook'][0].items():  # Sell orders
            sell_orders[Decimal(price)] = Decimal(size)
            # writes.append({
            #     "measurement": "order_book",
            #     "time": write_time,
            #     "tags": {
            #         "exchange": 'POLONIEX',
            #         "pair": pair_name,
            #         "buy": False,
            #         "rank": rank
            #     },
            #     "fields": {
            #         "size": size,
            #         "price": price
            #     }
            # })
            # rank += 1

        rank = 0
        for price, size in order_dump[0][1]['orderBook'][1].items():  # Buy orders
            buy_orders[Decimal(price)] = Decimal(size)
            # writes.append({
            #     "measurement": "order_book",
            #     "time": write_time,
            #     "tags": {
            #         "exchange": 'POLONIEX',
            #         "pair": pair_name,
            #         "buy": True,
            #         "rank": rank
            #     },
            #     "fields": {
            #         "size": size,
            #         "price": price
            #     }
            # })
            # rank += 1

        self.order_books[pair_name].set_initial_orders(sell_orders, buy_orders)
        self.order_books[pair_name].save_order_book()
        # db_client.write_points(writes, time_precision='n')

    async def write_order_updates(self, order_updates, pair_id: int, jsonraw=None):
        assert(pair_id in WEBSOCKET_PAIRS_INVERTED)
        pair_name = WEBSOCKET_PAIRS_INVERTED[pair_id]
        """
        :param order_updates: An array of   [
                                             ["o", <1 for buy 0 for sell>, "<price>", "<size>"],
                                             ["o", <1 for buy 0 for sell>, "<price>", "<size>"],
                                             ["t", "<trade id>", <1 for buy 0 for sell>, "<size>", "<price>", <timestamp>]
                                           ]
        :pair_id: Pair id described in WEBSOCKET_PAIRS
        :return:
        """



        # Do removal_updates last.
        # Price level removal if quantity is 0 https://docs.poloniex.com/#price-aggregated-book
        removal_updates = []
        for update in order_updates:
            if update[0] == 'o':
                if Decimal(update[3]) == Decimal(0):
                    removal_updates.append(update)

        order_updates = [x for x in order_updates if not (x[0] == 'o' and Decimal(x[3]) == Decimal(0))]

        for update in order_updates:
            if update[0] == 't':  # Trade
                buy = False
                if int(update[2]) == 1:
                    buy = True
                else:
                    buy = False

                trade = TradeInfo(Exchange('POLONIEX'),
                                  Pair(WEBSOCKET_PAIRS_INVERTED[pair_id]),
                                  buy,
                                  float(update[4]),
                                  float(update[3]))
                logger.debug(trade.get_as_json_dict())
                self.order_books[pair_name].update_using_trade(buy, Decimal(update[3]), Decimal(update[4]))
                self.write_trade(trade)
            elif update[0] == 'o':  # Order Book modification
                buy = False
                if int(update[1]) == 1:
                    buy = True
                else:
                    buy = False

                if Decimal(update[3]) == Decimal(0):  # Price level removal if quantity is 0 https://docs.poloniex.com/#price-aggregated-book
                    assert(False)  # This should be in removal_updates
                    self.order_books[pair_name].remove_order(buy, Decimal(update[2]))
                else:
                    self.order_books[pair_name].add_order(buy, Decimal(update[2]), Decimal(update[3]))

        # Execute removal modifications
        for removal_update in removal_updates:
            buy = False
            if int(update[1]) == 1:
                buy = True
            else:
                buy = False

            self.order_books[pair_name].remove_order(buy, Decimal(removal_update[2]))

        self.order_books[pair_name].save_order_book()



    async def run_orders(self):
        websocket = await websockets.connect('wss://api2.poloniex.com')

        # Subscribe to all the order channels
        for pair in self.pairs:
            assert(pair.pair in WEBSOCKET_PAIRS)
            asyncio.ensure_future(websocket.send(json.dumps({'command': 'subscribe', 'channel': WEBSOCKET_PAIRS[pair.pair]})))

        while True:
            # Received data will look like: https://docs.poloniex.com/#price-aggregated-book

            # The first response is an order book dump like:
            # [ <channel id>, <sequence number>, [ [ "i", { "currencyPair": "<currency pair name>", "orderBook": [ { "<lowest ask price>": "<lowest ask size>", "<next ask price>": "<next ask size>", ... }, { "<highest bid price>": "<highest bid size>", "<next bid price>": "<next bid size>", ... } ] } ] ] ]
            # [ 14, 8767, [ [ "i", { "currencyPair": "BTC_BTS", "orderBook": [ { "0.00001853": "2537.5637", "0.00001854": "1567238.172367" }, { "0.00001841": "3645.3647", "0.00001840": "1637.3647" } ] } ] ] ]

            # Subsequent responses:
            # ["o", <1 for buy 0 for sell>, "<price>", "<size>"], ["t", "<trade id>", <1 for buy 0 for sell>, "<price>", "<size>", <timestamp>] ] ... ]
            # [ 14, 8768, [ ["o", 1, "0.00001823", "5534.6474"], ["o", 0, "0.00001824", "6575.464"], ["t", "42706057", 1, "0.05567134", "0.00181421", 1522877119] ] ]


            raw_json = await websocket.recv()
            data = json.loads(raw_json, parse_float=Decimal)

            if data[0] == 1010:
                logger.debug("Heartbeat from Poloniex, continuing.")
                continue

            initial_dump = False
            try:
                if data[2][0][0] == 'i':
                    initial_dump = True
            except (KeyError, IndexError):
                logger.warning('Received data malformed, skipping, data is: {}.'.format(str(data)))
                continue

            if initial_dump:
                await self.write_order_dump(data[2])
                # print('Initial dump')
            else:
                await self.write_order_updates(data[2], data[0], jsonraw=raw_json)

    async def run(self):
        # asyncio.ensure_future(self.run_tickers())
        while True:
            try:
                logger.info('Running continuous worker {}'.format(str(type(self).__name__)))
                task = asyncio.ensure_future(self.run_orders())
                await task
            except Exception as e:
                logger.critical(traceback.format_exc())
                logger.critical("Continuous worker failed: {}".format(str(e)))
                self.record_trade_interruption('POLONIEX')

            logger.debug('here9999')

    def run_blocking(self):
        loop = asyncio.get_event_loop()
        asyncio.ensure_future(self.run())
        loop.run_forever()
