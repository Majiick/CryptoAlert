from data_api import DataAPI, Pair, Exchange, DataSource
from typing import List, Tuple, Dict
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
    def get_ohlc(pair: Pair, exchange: Exchange, start_time: int, end_time: int, periods: List[int]) -> Dict[int, List[Tuple[int, float, float, float, float, float]]]:
        # Return: Dict[period, List[[ CloseTime, OpenPrice, HighPrice, LowPrice, ClosePrice, Volume ]]
        '''
        Cryptowatch limits historical data.
        For the 60 tick you can't go back more than 30000 seconds or so.

        {
            "result": {
            "60": [
                [1481634360, 782.14, 782.14, 781.13, 781.13, 1.92525],
                [1481634420, 782.02, 782.06, 781.94, 781.98, 2.37578],
                [1481634480, 781.39, 781.94, 781.15, 781.94, 1.68882],
                ...
            ],
            "180": [...],
            "300": [...],
            ...
            "604800": [...]
            }
        }

        '''
        assert (end_time > start_time)
        assert (periods)
        supported_periods = [60, 180, 300, 900, 1800, 3600, 7200, 14400, 21600, 43200, 86400, 259200, 604800]
        for period in periods:
            assert (period in supported_periods)

        ret: Dict[int, List[Tuple[int, float, float, float, float, float]]] = {}
        for period in periods:
            ret[period] = []

        for cur_period in periods:
            earliest_time = end_time + 600

            while earliest_time > start_time:
                # logger.debug('Period: {}'.format(cur_period))
                # logger.debug('Earliest time: {}'.format(earliest_time))
                params = {'before': earliest_time + 1, 'periods': cur_period, 'after': start_time-(cur_period*2)-1}
                # logger.debug('https://api.cryptowat.ch/markets/{}/{}/ohlc'.format(exchange.name, pair.pair.replace('_', '')))
                r = requests.get(
                    'https://api.cryptowat.ch/markets/{}/{}/ohlc'.format(exchange.name, pair.pair.replace('_', '')),
                    params=params)
                json_data = json.loads(r.content)
                logger.debug(json_data)
                if 'error' in json_data:
                    logger.error('Error: {}'.format(json_data['error']))
                    return ret
                if int(json_data['allowance']['remaining']) <= 0:
                    logger.error('Ran out of allowance.')

                if 'result' in json_data:
                    if json_data['result'][str(cur_period)]:
                        ret[cur_period].extend(json_data['result'][str(cur_period)])

                        new_earliest_time = end_time
                        for ohlc in json_data['result'][str(cur_period)]:
                            new_earliest_time = min(new_earliest_time, int(ohlc[0]))

                        if earliest_time == new_earliest_time:
                            # logger.debug('No more results')
                            break
                        else:
                            earliest_time = new_earliest_time
                    else:
                        logger.debug('No result at earliest_time {}'.format(earliest_time))
                        break
                else:
                    logger.warning('No ohlc result for request https://api.cryptowat.ch/markets/{}/{}/ohlc before time {}'.format(exchange.name, pair.pair.replace('_', ''), earliest_time))
                    break

        return ret


    @staticmethod
    def get_data_sources() -> List[DataSource]:
        r = requests.get('https://api.cryptowat.ch/markets')
        json_data = json.loads(r.content)
        if 'error' in json_data:
            logger.critical('Error: {}'.format(json_data['error']))
            return []
            # assert(False)

        ret: List[DataSource] = list()

        for exchange_and_market in json_data['result']:
            # The result has one more attribute called 'active' which is a boolean.
            # Take the result into account at a future date.
            pair = Pair(exchange_and_market['pair'], structured_properly=False)
            exchange = Exchange(exchange_and_market['exchange'].upper())
            ret.append(DataSource(pair, exchange, Cryptowatch))

        return ret