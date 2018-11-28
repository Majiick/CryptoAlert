"""
from data_api import DataAPI, Pair, Exchange, DataSource, ContinuousDataSource, ContinuousDataAPI
from typing import List, Tuple
import requests
import json
import websockets
import asyncio
import time
import zmq
from influxdb import InfluxDBClient
from influxdb_init import db_client
import websockets
from signalr_aio import Connection
from base64 import b64decode
from zlib import decompress, MAX_WBITS
import json


class BittrexWebsockets(ContinuousDataAPI):
    def __init__(self, pairs: List[Pair]):
        self.pairs = pairs

    @staticmethod
    def get_all_pairs() -> List[Pair]:
        r = requests.get('https://api.bittrex.com/api/v1.1/public/getmarkets')
        r = r.json()

        assert(r['success'])

        ret = []
        for market in r['result']:
            if market['IsActive'] and not market['IsRestricted']:
                ret.append(Pair(market['MarketName'].replace('-', '_')))

        return ret

    @staticmethod
    def get_all_pairs() -> List[Pair]:
        r = requests.get('https://api.bittrex.com/api/v1.1/public/getmarkets')
        r = r.json()

        assert (r['success'])

        ret = []
        for market in r['result']:
            if market['IsActive'] and not market['IsRestricted']:
                ret.append(Pair(market['MarketName'].replace('-', '_')))

        return ret

    @staticmethod
    def process_message(message):
        deflated_msg = decompress(b64decode(message), -MAX_WBITS)
        return json.loads(deflated_msg.decode())

    @staticmethod
    async def on_message(msg):
        decoded_msg = process_message(msg[0])
        print(decoded_msg)

    # Create debug message handler.
    async def on_debug(**msg):
        # In case of 'queryExchangeState'
        if 'R' in msg and type(msg['R']) is not bool:
            decoded_msg = self.process_message(msg['R'])
            print(decoded_msg)

    # Create error handler
    async def on_error(msg):
        print(msg, flush=True)

    # Create hub message handler


    async def on_SubscribeToExchangeDeltas(msg):
        pass

    def run(self):
        connection = Connection('https://socket.bittrex.com/signalr', session=None)
        hub = connection.register_hub('c2')

        # connection.received += on_debug

        # # Assign error handler
        # connection.error += on_error

        # Assign hub message handler
        hub.client.on('uE', BittrexWebsockets.on_message)

        # Send a message
        hub.server.invoke('SubscribeToExchangeDeltas', 'BTC-ETH')

        # Start the client
        connection.start()
        print(';P')

    def run_blocking(self):
        self.run()
"""