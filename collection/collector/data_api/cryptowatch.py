from data_api import DataAPI, Pair, Exchange, DataSource
from typing import List, Tuple
import requests
import json
from mlogging import logger


class Cryptowatch(DataAPI):
    @staticmethod
    def get_last_price(pair: Pair, exchange: Exchange) -> float:
        r = requests.get('https://api.cryptowat.ch/markets/{}/{}/price'.format(exchange.name, pair.pair))
        json_data = json.loads(r.content)
        return float(json_data['result']['price'])

    '''
    def get_trades...
        # Only gets very recent trades it seems like. Like the since param doesn't even work.
    '''


    @staticmethod
    def get_ohlc(pair: Pair, exchange: Exchange, start_time: int, end_time: int, periods: List[int]):
        '''
        Cryptowatch limits historical data.
        For the 60 tick you can't go back more than 30000 seconds or so.
        '''
        assert(end_time > start_time)
        assert(periods)
        supported_periods = [60, 180, 300, 900, 1800, 3600, 7200, 14400, 21600, 43200, 86400, 259200, 604800]
        for period in periods:
            assert(period in supported_periods)

        for cur_period in periods:
            earliest_time = end_time

            while earliest_time > start_time:
                logger.debug('Period: {}'.format(cur_period))
                logger.debug('Earliest time: {}'.format(earliest_time))
                params = {'before': earliest_time + 1, 'periods': cur_period}
                r = requests.get('https://api.cryptowat.ch/markets/{}/{}/ohlc'.format(exchange.name, pair.pair),
                                 params=params)
                json_data = json.loads(r.content)
                logger.debug(json_data['allowance'])

                if json_data['result'][str(cur_period)]:
                    logger.debug(len(json_data['result'][str(cur_period)]))

                    new_earliest_time = end_time
                    for ohlc in json_data['result'][str(cur_period)]:
                        new_earliest_time = min(new_earliest_time, int(ohlc[0]))

                    if earliest_time == new_earliest_time:
                        logger.debug('No more results')
                        break
                    else:
                        earliest_time = new_earliest_time
                else:
                    logger.debug('No result at earliest_time {}'.format(earliest_time))
                    break


    @staticmethod
    def get_data_sources() -> List[DataSource]:
        r = requests.get('https://api.cryptowat.ch/markets')
        json_data = json.loads(r.content)

        ret: List[DataSource] = list()

        for exchange_and_market in json_data['result']:
            # The result has one more attribute called 'active' which is a boolean.
            # Take the result into account at a future date.
            pair = Pair(exchange_and_market['pair'], structured_properly=False)
            exchange = Exchange(exchange_and_market['exchange'].upper())
            ret.append(DataSource(pair, exchange, Cryptowatch))

        return ret