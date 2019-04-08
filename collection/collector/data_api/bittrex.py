import websockets
from signalr_aio import Connection
from base64 import b64decode
from zlib import decompress, MAX_WBITS
import json
import asyncio
import requests
from typing import List, Type, Dict, Any
import sys
from data_api import DataAPI, Pair, Exchange, DataSource, ContinuousDataSource, ContinuousDataAPI, TradeInfo, OrderBook
import math
import time
import mlogging
from mlogging import logger
import sys
from decimal import *
import traceback
import collections
import threading


"""
https://bittrex.github.io/api/v1-1

Socket Connections
Websocket connections may occasionally need to be recycled. If, for example, you're maintinaing local order book state, and you stop receiving updates even though you know trade activity is occurring, it may be time to resynchronize.

Because v1.1 websocket nonces are server-specific, it's crucial to maintain state on a per-connection basis. For example, to resychronize the BTC-ETH market order book:

Drop existing websocket connections and flush accumulated data and state (e.g. market nonces).
Re-establish websocket connection.
Subscribe to BTC-ETH market deltas, cache received data keyed by nonce.
Query BTC-ETH market state.
Apply cached deltas sequentially, starting with nonces greater than that received in step 4.
"""

class QLock:
    def __init__(self):
        self.lock = threading.Lock()
        self.waiters = collections.deque()
        self.count = 0

    def acquire(self):
        self.lock.acquire()
        if self.count:
            new_lock = threading.Lock()
            new_lock.acquire()
            self.waiters.append(new_lock)
            self.lock.release()
            new_lock.acquire()
            self.lock.acquire()
        self.count += 1
        self.lock.release()

    def release(self):
        with self.lock:
            if not self.count:
                raise ValueError("lock not acquired")
            self.count -= 1
            if self.waiters:
                self.waiters.popleft().release()

    def locked(self):
        return self.count > 0

class BittrexWebsockets(ContinuousDataAPI):
    def __init__(self, pairs: List[Pair]):
        super().__init__(pairs)

        self.market_queryExchangeState_nonce: Dict[str, int] = {}
        self.market_nonce_numbers: Dict[str, int] = {}
        self.cached_received_exchange_deltas: Dict[str, List[str]] = {}  # The exchange deltas that were received before getting the market snapshot.
        self.order_books: Dict[str, OrderBook] = {}
        self.received_deltas: Dict[str, Any] = {}
        self.mutexes: Dict[str, Any] = {}

    @staticmethod
    def get_all_pairs() -> List[Pair]:
        r = requests.get('https://api.bittrex.com/api/v1.1/public/getmarkets')
        r = r.json()

        assert(r['success'])  # type: ignore

        ret = []
        for market in r['result']:  # type: ignore
            if market['IsActive'] and not market['IsRestricted']:
                ret.append(Pair(market['MarketName'].replace('-', '_')))

        return ret

    def process_message(self, message):
        deflated_msg = decompress(b64decode(message), -MAX_WBITS)
        return json.loads(deflated_msg.decode(), parse_float=Decimal)

    # Create debug message handler.
    async def on_debug(self, **msg):
        # In case of 'queryExchangeState'
        # queryExchangeState example: {'M': 'BTC-NEO', 'N': 916508, 'Z': [{'Q': 1.48220452, 'R': 0.00235045}, {'Q': 51.44229504, 'R': 0.00235001}, {'Q': 4.96547649, 'R': 0.00235}, {'Q': 0.5, 'R': 0.00234982}, {'Q': 1234.31287009, 'R': 0.00234866}, {'Q': 771.41221481, 'R': 0.00234852}, ...
        # print(msg)
        if 'R' in msg and type(msg['R']) is not bool:
            decoded_msg = self.process_message(msg['R'])
            market_name = decoded_msg['M'].replace('-', '_')
            # self.market_nonce_numbers[decoded_msg['M'].replace('-', '_')] = int(decoded_msg['N'])
            self.market_queryExchangeState_nonce[market_name] = int(decoded_msg['N'])
            # logger.debug(decoded_msg)
            # print(decoded_msg['N'])
            # print(int(decoded_msg['N']))
            logger.debug('Received queryExchangeState for market {}. Nonce: {}'.format(market_name, int(decoded_msg['N'])))

            buy_orders = collections.OrderedDict()
            sell_orders = collections.OrderedDict()
            for buy_order in decoded_msg['Z']:
                assert(Decimal(buy_order['R']) not in buy_orders)
                buy_orders[Decimal(buy_order['R'])] = Decimal(buy_order['Q'])

            for sell_order in decoded_msg['S']:
                assert(Decimal(sell_order['R']) not in sell_orders)
                sell_orders[Decimal(sell_order['R'])] = Decimal(sell_order['Q'])

            self.order_books[market_name] = OrderBook(Exchange('BITTREX'), Pair(market_name))
            self.order_books[market_name].set_initial_orders(sell_orders, buy_orders)
            self.order_books[market_name].save_order_book()


    # Create error handler
    async def on_error(self, msg):
        logger.error('Bittrex continuous worker received error: ' + msg)
        assert(False)

    # def process_market_deltas(self):
    #     while True:
    #         pass

    async def on_subscribe_to_exchange_deltas(self, msg):
        sys.stdout.flush()
        sys.stderr.flush()
        # market_name = json['M'].replace('-', '_')
        # json = self.process_message(msg[0])
        # if market_name not in self.received_deltas:
        #     self.received_deltas[market_name] = []
        # self.received_deltas[market_name].append(json)
        # return
        """
        msg example: {'M': 'BTC-XEM', 'N': 782391, 'Z': [{'TY': 2, 'R': 1.892e-05, 'Q': 3687.0}, {'TY': 2, 'R': 1.89e-05, 'Q': 5555.84218246}, {'TY': 2, 'R': 1.86e-05, 'Q': 4216.29131711}], 'S': [], 'f': [{'FI': 64912354, 'OT': 'SELL', 'R': 1.925e-05, 'Q': 156.903765, 'T': 1543424515903}]}

        Msg format: {
                      "MarketName": "string",
                      "Nonce": "int",
                      "Buys": [
                        {
                          "Type": "int",
                          "Balance": "decimal",
                          "Available": "decimal"
                        }
                      ],
                      "Sells": [
                        {
                          "Type": "int",
                          "Balance": "decimal",
                          "Available": "decimal"
                        }
                      ],
                      "Fills": [
                        {
                          "FillId": "int",
                          "OrderType": "string",
                          "Rate": "decimal",
                          "Quantity": "decimal",
                          "TimeStamp": "date"
                        }
                      ]
                    }
        """
        DELTA_TYPES = {0: 'ADD', 1: 'REMOVE', 2: 'UPDATE'}

        json = self.process_message(msg[0])

        market_name = json['M'].replace('-', '_')
        if market_name not in self.mutexes:
            self.mutexes[market_name] = QLock()
        self.mutexes[market_name].acquire()
        # logger.debug('Lock acquired for market {}'.format(market_name))
        # logger.debug(json)

        if market_name not in self.market_queryExchangeState_nonce:
            logger.debug('Nonce for market {} not set yet. This means the order book snapshot not yet received. Caching this update {}.'.format(market_name, json))
            if market_name not in self.cached_received_exchange_deltas:
                self.cached_received_exchange_deltas[market_name] = []

            self.cached_received_exchange_deltas[market_name].append(json)
            self.mutexes[market_name].release()
            logger.debug('Lock released for market {}'.format(market_name))
            return

        if market_name in self.market_queryExchangeState_nonce and market_name not in self.market_nonce_numbers:
            # If there was a queryExchangeState received and this is the first trade then check that this trade + cached trades line up with the queryExchangeState
            # This assert is in place to check if the queryExchangeState was received first before any trades which may cause trades to be missing.
            # For example if queryExchangeState nonce is 9002 but the first trade received nonce is 9005 then there are 3 trades missing, this should not happen.
            if market_name in self.cached_received_exchange_deltas:
                assert(int(self.cached_received_exchange_deltas[market_name][-1]['N']) == int(json['N'])-1)  # Check that the last nonce received is lined up with this trade
                assert(self.market_queryExchangeState_nonce[market_name]+1 >= int(self.cached_received_exchange_deltas[market_name][0]['N'])) # See that the first received trade is the next nonce from queryExchangeState or lower.+1 To account for when nonce of trade is one bigger than snapshot.
            else:
                assert(self.market_queryExchangeState_nonce[market_name]+1 >= int(json['N']))  # +1 To account for when nonce of trade is one bigger than snapshot.

        deltas_to_execute = []
        if market_name in self.cached_received_exchange_deltas:
            if (market_name in self.market_nonce_numbers):
                logger.debug(market_name)
                logger.debug(self.market_nonce_numbers)
            assert(market_name not in self.market_nonce_numbers)  # Nonce should not be in nonce numbers yet because cached deltas should only be executed on the first received trade after receiving the order book.
            last_cached_delta_nonce = None
            checked_if_first_lines_up_with_queryExchange_nonce = False
            for cached_delta in self.cached_received_exchange_deltas[market_name]:  # Iterates in order received, so increasing nonce number.
                if last_cached_delta_nonce is not None:
                    assert (int(cached_delta['N']) == last_cached_delta_nonce + 1)  # Cached deltas skipped a nonce
                if int(cached_delta['N']) > self.market_queryExchangeState_nonce[market_name]:
                    if not checked_if_first_lines_up_with_queryExchange_nonce:
                        checked_if_first_lines_up_with_queryExchange_nonce = True
                        assert(int(cached_delta['N']) == self.market_queryExchangeState_nonce[market_name] + 1)

                    deltas_to_execute.append(cached_delta)
                    last_cached_delta_nonce = int(cached_delta['N'])
                    logger.debug("Adding one delta to execute with nonce: {} for {}. Snapshot nonce: {}".format(int(cached_delta['N']), market_name, self.market_queryExchangeState_nonce[market_name]))

            del self.cached_received_exchange_deltas[market_name]

        if market_name in self.market_nonce_numbers:
            assert(not deltas_to_execute)
            if not self.market_nonce_numbers[market_name] == int(json['N']) - 1:
                if market_name in self.cached_received_exchange_deltas:
                    dlts = self.cached_received_exchange_deltas[market_name]
                else:
                    dlts = None
                logger.error('Trade nonce doesnt line up for market {}, last nonce number is {} and nonce right now is {}. QueryExchangeNonce is {} and cached deltas is {} '
                             .format(market_name, self.market_nonce_numbers[market_name], json['N'], self.market_queryExchangeState_nonce[market_name], dlts))
                assert(self.market_nonce_numbers[market_name] == int(json['N']) - 1)  # Make sure that update nonce lines up with last update.
            assert (self.market_nonce_numbers[market_name] == int(json['N']) - 1)  # Make sure that update nonce lines up with last update.
        else:
            # First trade after receiving queryExchange
            if deltas_to_execute:
                logger.debug('Making sure cached updates line up with received updated')
                assert (int(deltas_to_execute[-1]['N']) == int(json['N']) - 1)  # Make sure that cached updates line up with the received update
            else:
                if not (self.market_queryExchangeState_nonce[market_name] == int(json['N']) - 1):
                    logger.error(
                        'Trade nonce doesnt line up for market {}, last nonce number is {} and nonce right now is {}. QueryExchangeNonce is {} and cached deltas is {} '
                        .format(market_name, self.market_nonce_numbers[market_name], json['N'],
                                self.market_queryExchangeState_nonce[market_name], dlts))
                assert(self.market_queryExchangeState_nonce[market_name] == int(json['N']) - 1)

        if len(deltas_to_execute) > 0:
            logger.debug('Making sure cached updates line up with received updated')
            assert (int(deltas_to_execute[-1]['N']) == int(json['N']) - 1)  # Make sure that cached updates line up with the received update.


        # IF deltas_to_execute then execute them.
        if len(deltas_to_execute) > 0:
            logger.debug('Having deltas_to_execute for {}.'.format(market_name))

        self.market_nonce_numbers[market_name] = int(json['N'])

        for queryExchangeState in deltas_to_execute + [json]:
            # Adds come before everything.
            # Then fills need to come first because if an order is fulfilled fully then it will be removed in the same update.
            # Then removes and updates
            for buy_order in queryExchangeState['Z']:
                if int(buy_order['TY']) == 0: # Add
                    self.order_books[market_name].add_order(True, Decimal(buy_order['R']), Decimal(buy_order['Q']))

            for sell_order in queryExchangeState['S']:
                if int(sell_order['TY']) == 0: # Add
                    self.order_books[market_name].add_order(False, Decimal(sell_order['R']), Decimal(sell_order['Q']))

            for fill in queryExchangeState['f']:  # In fills
                buy = None
                if fill['OT'] == 'SELL':
                    buy = False
                elif fill['OT'] == 'BUY':
                    buy = True

                # Since Bittrex returns with a resolution of one MILLISECOND, we need to convert to nanosecond resolution to avoid overwrites in postgres.
                # To prevent the overwrites we need to keep the second that bittrex return to us but write our own nanosecond time
                # float('1e+6') is how many nanoseconds is in one millisecond since Bittrex returns seconds
                frac, whole = math.modf(time.time_ns() / float('1e+6'))  # Convert time nanoseconds to seconds and get the fraction part
                timestamp = int((fill['T'] + frac) * float('1e+6'))  # Take bittrex timestamp add the fraction of nanoseconds onto it and convert to nanoseconds.

                trade = TradeInfo(Exchange('BITTREX'),
                                  Pair(json['M'].replace('-', '_')),
                                  buy,
                                  float(fill['Q']),
                                  float(fill['R']),
                                  timestamp=timestamp)
                self.order_books[market_name].update_using_trade(buy, Decimal(fill['R']), Decimal(fill['Q']))
                self.write_trade(trade)

            for buy_order in queryExchangeState['Z']:
                if int(buy_order['TY']) == 1: # Remove
                    self.order_books[market_name].remove_order(True, Decimal(buy_order['R']))
                if int(buy_order['TY']) == 2: # Update
                    self.order_books[market_name].set_order(True, Decimal(buy_order['R']), Decimal(buy_order['Q']))

            for sell_order in queryExchangeState['S']:
                if int(sell_order['TY']) == 1: # Remove
                    self.order_books[market_name].remove_order(False, Decimal(sell_order['R']))
                if int(sell_order['TY']) == 2: # Update
                    self.order_books[market_name].set_order(False, Decimal(sell_order['R']), Decimal(sell_order['Q']))

        self.order_books[market_name].save_order_book()
        self.mutexes[market_name].release()
        # logger.debug('Lock released for market {}'.format(market_name))


    def run(self):
        """
        Need to QueryExchangeState for every market first
        :return:
        """
        logger.info('Running continuous worker {}'.format(str(type(self).__name__)))
        connection = Connection('https://socket.bittrex.com/signalr', session=None)
        hub = connection.register_hub('c2')

        connection.received += self.on_debug

        # Assign error handler
        connection.error += self.on_error

        # Assign hub message handler
        hub.client.on('uE', self.on_subscribe_to_exchange_deltas)

        # Subscribe to all assigned pairs
        i = 0
        for pair in self.pairs:
            logger.info(pair.pair)
            hub.server.invoke('SubscribeToExchangeDeltas', pair.pair.replace('_', '-'))
            i += 1
            # break
            #
            # if i > 5:
            #     break
        time.sleep(3)
        for pair in self.pairs:
            logger.info(pair.pair)
            hub.server.invoke('queryExchangeState', pair.pair.replace('_', '-'))


        # Start the client
        connection.start()

    def run_blocking(self):
        while True:
            try:
                self.run()
            except Exception as e:
                logger.critical(traceback.format_exc())
                logger.critical("Continuous worker failed: {}".format(str(e)))
                self.record_trade_interruption('BITTREX')
