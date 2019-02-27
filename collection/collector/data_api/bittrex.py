import websockets
from signalr_aio import Connection
from base64 import b64decode
from zlib import decompress, MAX_WBITS
import json
import asyncio
import requests
from typing import List, Type, Dict, Any
import sys
from data_api import DataAPI, Pair, Exchange, DataSource, ContinuousDataSource, ContinuousDataAPI, TradeInfo
import math
import time
import mlogging
from mlogging import logger
import sys
import traceback


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

class BittrexWebsockets(ContinuousDataAPI):
    def __init__(self, pairs: List[Pair]):
        super().__init__(pairs)

        self.market_queryExchangeState_nonce: Dict[str, int] = {}
        self.market_nonce_numbers: Dict[str, int] = {}
        self.cached_received_exchange_deltas: Dict[str, List[str]] = {}  # The exchange deltas that were received before getting the market snapshot.

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
        return json.loads(deflated_msg.decode())

    # Create debug message handler.
    async def on_debug(self, **msg):
        # In case of 'queryExchangeState'
        # queryExchangeState example: {'M': 'BTC-NEO', 'N': 916508, 'Z': [{'Q': 1.48220452, 'R': 0.00235045}, {'Q': 51.44229504, 'R': 0.00235001}, {'Q': 4.96547649, 'R': 0.00235}, {'Q': 0.5, 'R': 0.00234982}, {'Q': 1234.31287009, 'R': 0.00234866}, {'Q': 771.41221481, 'R': 0.00234852}, ...
        # print(msg)
        if 'R' in msg and type(msg['R']) is not bool:
            decoded_msg = self.process_message(msg['R'])
            # self.market_nonce_numbers[decoded_msg['M'].replace('-', '_')] = int(decoded_msg['N'])
            self.market_queryExchangeState_nonce[decoded_msg['M'].replace('-', '_')] = int(decoded_msg['N'])
            # logger.debug(decoded_msg)
            # print(decoded_msg['N'])
            # print(int(decoded_msg['N']))
            logger.debug('Received queryExchangeState for market {}. Nonce: {}'.format(decoded_msg['M'].replace('-', '_'), int(decoded_msg['N'])))


    # Create error handler
    async def on_error(self, msg):
        logger.error('Bittrex continuous worker received error: ' + msg)
        assert(False)

    async def on_subscribe_to_exchange_deltas(self, msg):
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
        if market_name not in self.market_queryExchangeState_nonce:
            logger.debug('Nonce for market {} not set yet. This means the order book snapshot not yet received. Caching this trade.'.format(market_name))
            if market_name not in self.cached_received_exchange_deltas:
                self.cached_received_exchange_deltas[market_name] = []

            self.cached_received_exchange_deltas[market_name].append(json)
            return

        deltas_to_execute = []
        no_cached_entries = False
        if market_name not in self.market_nonce_numbers:
            # The market received first trade after acquiring the book snapshot. Execute cached trades with nonce greater than snapshot nonce.
            if market_name not in self.cached_received_exchange_deltas:
                # No cached entries.
                no_cached_entries = True
            else:
                # Add cached entries to deltas_to_execute
                last_cached_delta_nonce = None
                for cached_delta in self.cached_received_exchange_deltas[market_name]:  # Iterates in order received, so increasing nonce number.
                    if last_cached_delta_nonce is not None:
                        assert(int(cached_delta['N']) == last_cached_delta_nonce + 1)  # Cached deltas skipped a nonce
                    if int(cached_delta['N']) > self.market_queryExchangeState_nonce[market_name]:
                        deltas_to_execute.append(cached_delta)
                        print("Adding one delta to execute with nonce: {}. Snapshot nonce: {}".format(int(cached_delta['N']), self.market_queryExchangeState_nonce[market_name]))

        if no_cached_entries and market_name not in self.market_nonce_numbers:
            # If there were no cached entries but this is the first trade after acquiring book snapshot, then make sure trade lines up with snapshot nonce.
            assert(self.market_queryExchangeState_nonce[market_name] == int(json['N'])-1)
        else:
            if len(deltas_to_execute) > 0:
                assert(int(deltas_to_execute[-1]['N']) == int(json['N'])-1)  # Make sure that cached updates line up with the received update.
            else:
                assert(self.market_nonce_numbers[market_name] == int(json['N'])-1)  # Make sure that update nonce lines up with last update.


        ############


        # IF deltas_to_execute then execute them.


        ###########
        self.market_nonce_numbers[market_name] = int(json['N'])

        for fill in json['f']:  # In fills
            buy = None
            if fill['OT'] == 'SELL':
                buy = False
            elif fill['OT'] == 'BUY':
                buy = True

            # Since Bittrex returns with a resolution of one MILLISECOND, we need to convert to nanosecond resolution to avoid overwrites in influxdb.
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
            self.write_trade(trade)

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
            hub.server.invoke('queryExchangeState', pair.pair.replace('_', '-'))
            i += 1

            if i > 3:
                break


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
