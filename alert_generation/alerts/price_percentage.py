from alert import Alert
import sqlalchemy
import psycopg2
import time
from postgresql_init import engine
from sqlalchemy.sql import text
from typing import List, Type, Dict, Any
from mlogging import logger
import time


class PricePercentage(Alert):
    # TODO: These need to access Exchange, Pair etc. from the data_api folder.
    def __init__(self, exchange: str, pair: str, point: float, direction: str, time_frame: float):
        """

        :param exchange:
        :param pair:
        :param point:
        :param direction:
        :param time_frame: Seconds back in time.
        """
        assert(direction == 'up' or direction == 'down')

        self.exchange = exchange
        self.pair = pair
        self.point = point
        self.direction = direction
        self.time_frame = time_frame

        # The 3 variables below are to be used when constructing the get interesting event description.
        self.price_percentage_diff = 0.0
        self.min_price = 0.0
        self.max_price = 0.0

    def trigger(self, trade) -> bool:
        time_started_query = time.time()
        if (trade['tags']['pair'].lower() == self.pair.lower() or self.pair == '*') and (trade['tags']['exchange'].lower() == self.exchange.lower() or self.exchange == '*'):
            # Result: ResultSet({'('trade', None)': [{'time': '2019-02-28T10:58:08.306845796Z', 'max': 1.67000003, 'min': 1.67000003}]})
            # After list(result): [[{'time': '2019-02-28T11:01:11.533978751Z', 'max': 0.00042362, 'min': 0.00042362}]]
            with engine.begin() as conn:
                # Assuming both epoch and time frame are in seconds and trade_time is in nano seconds.
                print(int(self.time_frame))
                result = conn.execute(text("SELECT max(price), min(price) FROM TRADE WHERE trade_time > (extract(epoch from now()) * 1000000000) - cast(1 as bigint)*:time_frame*1000000000 AND market=:market AND exchange=:exchange;"),
                             time_frame=int(self.time_frame),
                             market=trade['tags']['pair'],
                             exchange=trade['tags']['exchange'])
                result = result.fetchone()

            print(result)
            if result[0] is None:
                logger.warning('No result for price percentage query. {}'.format(self.__dict__))
                return False
            max_price = float(result[0])
            min_price = float(result[1])
            # result = db_client.query("SELECT max(price), min(price) FROM trade WHERE time > now() - {}s and exchange='{}' and pair='{}';".format(int(self.time_frame), trade['tags']['exchange'], trade['tags']['pair']))
            # result = list(result)
            # if not result:
            #     logger.warning('No result for query {}'.format("SELECT max(price), min(price) FROM trade WHERE time > now() - {}s and exchange='{}' and pair='{}';".format(int(self.time_frame), trade['tags']['exchange'], trade['tags']['pair'])))
            #     return False
            # logger.debug(result)
            # max_price = float(result[0][0]['max'])
            # min_price = float(result[0][0]['min'])

            ret = False
            if self.direction == 'up':
                percentage_diff = 100.0 * (trade['fields']['price'] - min_price) / min_price
                # logger.debug(trade['fields']['price'])
                # logger.debug(min_price)
                # logger.debug(percentage_diff)
                # logger.debug(trade)
                # logger.debug('up')
                if percentage_diff > self.point:
                    ret = True
            elif self.direction == 'down':
                percentage_diff = 100.0 * (trade['fields']['price'] - max_price) / max_price
                # logger.debug(trade['fields']['price'])
                # logger.debug(max_price)
                # logger.debug(percentage_diff)
                # logger.debug(trade)
                # logger.debug('down')
                if abs(percentage_diff) > self.point:
                    ret = True

            if ret:
                self.min_price = min_price
                self.max_price = max_price
                self.price_percentage_diff = percentage_diff


        time_to_query = time.time() - time_started_query
        logger.debug('Took {} to query'.format(time_to_query))
        if ret:
            for x in range(20):
                logger.debug('truyu')
        return ret

    def get_interesting_event_description(self):
        '''
        CREATE TABLE IF NOT EXISTS INTERESTING_EVENT(
        id SERIAL PRIMARY KEY,
        event_time BIGINT NOT NULL,
        exchange TEXT NOT NULL,
        market TEXT NOT NULL,
        message TEXT NOT NULL,
        event_type TEXT NOT NULL
        );
        '''
        assert(self.min_price is not None)
        assert(self.max_price is not None)
        assert(self.price_percentage_diff is not None)
        return {'event_time': -1, 'exchange': self.exchange, 'market': self.pair, 'event_type': 'pricepercentage',
                'message': 'Price spiked by {} from {} to {} in the last {} seconds.'.format(self.price_percentage_diff, self.min_price, self.max_price, self.time_frame)}

    @staticmethod
    def get_all_from_db() -> List[Alert]:
        ret: List[Alert] = []

        with engine.begin() as conn:
            result = conn.execute("select * from PRICE_PERCENTAGE_ALERT WHERE fulfilled = FALSE")
            for row in result:
                alert = PricePercentage(row['exchange'], row['pair'], row['point'], row['direction'], row['time_frame'])
                alert.alert_pk = row['alert_pk']
                alert.created_by_user = row['created_by_user']
                alert.fulfilled = row['fulfilled']
                alert.repeat = row['repeat']
                alert.broadcast_interesting_event_on_trigger = row['broadcast_interesting_event_on_trigger']
                ret.append(alert)

        return ret

