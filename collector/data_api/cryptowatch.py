from data_api import DataAPI, Pair, Exchange, DataSource
from typing import List, Tuple
import requests
import json

class Cryptowatch(DataAPI):
    @staticmethod
    def get_last_price(pair: Pair, exchange: Exchange) -> float:
        r = requests.get('https://api.cryptowat.ch/markets/{}/{}/price'.format(exchange.name, pair.pair))
        json_data = json.loads(r.content)
        return float(json_data['result']['price'])


    @staticmethod
    def get_ohlc(pair: Pair, exchange: Exchange, start_time: int, end_time: int, periods: List[int]):
        assert(end_time > start_time)
        assert(periods)
        supported_periods = [60, 180, 300, 900, 1800, 3600, 7200, 14400, 21600, 43200, 86400, 259200, 604800]
        for period in periods:
            assert(period in supported_periods)

        for cur_period in periods:
            earliest_time = end_time

            while earliest_time > start_time:
                print('Period: {}'.format(cur_period))
                print('Earliest time: {}'.format(earliest_time))
                params = {'before': earliest_time + 1, 'periods': cur_period}
                r = requests.get('https://api.cryptowat.ch/markets/{}/{}/ohlc'.format(exchange.name, pair.pair),
                                 params=params)
                json_data = json.loads(r.content)
                # print(json_data['allowance'])

                if json_data['result'][str(cur_period)]:
                    print(len(json_data['result'][str(cur_period)]))

                    new_earliest_time = end_time
                    for ohlc in json_data['result'][str(cur_period)]:
                        new_earliest_time = min(new_earliest_time, int(ohlc[0]))

                    if earliest_time == new_earliest_time:
                        print('No more results')
                        break
                    else:
                        earliest_time = new_earliest_time
                else:
                    print('No result at earliest_time {}'.format(earliest_time))
                    break

        '''
        max_limit_per_period = 497
        for cur_period in periods:
            max_time_frame = max_limit_per_period * cur_period
            time_frames_to_queury: List[Tuple[int, int]] = []  # Stores time frames which are (start, end).
            cur_time = end_time
            while cur_time > start_time:
                time_frames_to_queury.append((cur_time - max_time_frame, cur_time))
                cur_time = cur_time - max_time_frame

            for time_frame in time_frames_to_queury:
                print('\n')
                print('cur_period: {}'.format(cur_period))
                print('time_frame: {}'.format(time_frame))
                params = {'after': time_frame[0] - 1, 'before': time_frame[1] + 1}
                r = requests.get('https://api.cryptowat.ch/markets/{}/{}/ohlc'.format(exchange.name, pair.pair),
                                 params=params)
                json_data = json.loads(r.content)
                print(json_data['allowance'])

                for period in periods:
                    if json_data['result'][str(period)]:
                        print(len(json_data['result'][str(period)]))
                    else:
                        print('Missed period {} for timeframe {}'.format(period, time_frame))
        '''


    @staticmethod
    def get_data_sources() -> List[DataSource]:
        r = requests.get('https://api.cryptowat.ch/markets')
        json_data = json.loads(r.content)

        ret: List[DataSource] = list()

        for exchange_and_market in json_data['result']:
            # The result has one more attribute called 'active' which is a boolean.
            # Take the result into account at a future date.
            pair = Pair(exchange_and_market['pair'])
            exchange = Exchange(exchange_and_market['exchange'])
            ret.append(DataSource(pair, exchange, Cryptowatch))

        return ret