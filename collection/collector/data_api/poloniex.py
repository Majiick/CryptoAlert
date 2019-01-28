from data_api import DataAPI, Pair, Exchange, DataSource, ContinuousDataSource, ContinuousDataAPI, TradeInfo
from typing import List, Tuple
import requests
import json
import websockets
import asyncio
import time
import zmq
from influxdb import InfluxDBClient
from influxdb_init import db_client
from mlogging import logger


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
        self.pairs = pairs
        assert(len(self.pairs) > 0)

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

    async def write_order_dump(self, order_dump, pair_id: int):
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
        pass

    async def write_order_update(self, order_updates, pair_id: int):
        assert(pair_id in WEBSOCKET_PAIRS_INVERTED)
        """
        :param order_updates: An array of   [
                                             ["o", <1 for buy 0 for sell>, "<price>", "<size>"],
                                             ["o", <1 for buy 0 for sell>, "<price>", "<size>"],
                                             ["t", "<trade id>", <1 for buy 0 for sell>, "<size>", "<price>", <timestamp>]
                                           ]
        :pair_id: Pair id described in WEBSOCKET_PAIRS
        :return:
        """

        for update in order_updates:
            if update[0] == 't':  # Trade
                buy = False
                if update[2] == 1:
                    buy = True
                else:
                    buy = False

                trade = TradeInfo(Exchange('POLONIEX'),
                                  Pair(WEBSOCKET_PAIRS_INVERTED[pair_id]),
                                  buy,
                                  float(update[4]),
                                  float(update[3]))

                ContinuousDataAPI.write_trade(trade)
            elif update[0] == 'o':  # New order
                pass
                # print('New Order')

    async def run_orders(self):
        websocket = await websockets.connect('wss://api2.poloniex.com')

        # Subscribe to all the order channels
        for pair in self.pairs:
            assert(pair.pair in WEBSOCKET_PAIRS)
            asyncio.ensure_future(websocket.send(json.dumps({'command': 'subscribe', 'channel': WEBSOCKET_PAIRS[pair.pair]})))

        while True:
            # Received data will look like: https://poloniex.com/support/api/#websockets_channels_aggregated
            data = await websocket.recv()
            data = json.loads(data)

            initial_dump = False
            try:
                if data[2][0][0] == 'i':
                    initial_dump = True
            except KeyError:
                pass

            if initial_dump:
                pass
                # print('Initial dump')
            else:
                await self.write_order_update(data[2], data[0])

    async def run(self):
        # asyncio.ensure_future(self.run_tickers())
        asyncio.ensure_future(self.run_orders())

    def run_blocking(self):
        loop = asyncio.get_event_loop()
        asyncio.ensure_future(self.run())
        loop.run_forever()
