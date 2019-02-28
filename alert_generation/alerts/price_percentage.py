from alert import Alert
import sqlalchemy
import psycopg2
import time
from postgresql_init import engine
from sqlalchemy.sql import text
from typing import List, Type, Dict
from mlogging import logger
from influxdb_init import db_client
import influxdb
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

    def trigger(self, trade) -> bool:
        try:
            time_started_query = time.time()
            """
            WARNING THIS IS SQL INJECTABLE









            """
            if (trade['tags']['pair'].lower() == self.pair.lower() or self.pair == '*') and (trade['tags']['exchange'].lower() == self.exchange.lower() or self.exchange == '*'):
                # Result: ResultSet({'('trade', None)': [{'time': '2019-02-28T10:58:08.306845796Z', 'max': 1.67000003, 'min': 1.67000003}]})
                # After list(result): [[{'time': '2019-02-28T11:01:11.533978751Z', 'max': 0.00042362, 'min': 0.00042362}]]
                result = db_client.query("SELECT max(price), min(price) FROM trade WHERE time > now() - {}s and exchange='{}' and pair='{}';".format(int(self.time_frame), trade['tags']['exchange'], trade['tags']['pair']))
                result = list(result)
                if not result:
                    logger.warning('No result for query {}'.format("SELECT max(price), min(price) FROM trade WHERE time > now() - {}s and exchange='{}' and pair='{}';".format(int(self.time_frame), trade['tags']['exchange'], trade['tags']['pair'])))
                    return False
                logger.debug(result)
                max_price = float(result[0][0]['max'])
                min_price = float(result[0][0]['min'])

                ret = False
                if self.direction == 'up':
                    percentage_diff = 100 * (trade['fields']['price'] - min_price) / min_price
                    logger.debug(trade['fields']['price'])
                    logger.debug(min_price)
                    logger.debug(percentage_diff)
                    logger.debug(trade)
                    logger.debug('up')
                    if percentage_diff > self.point:
                        ret = True
                elif self.direction == 'down':
                    percentage_diff = 100 * (trade['fields']['price'] - max_price) / max_price
                    logger.debug(trade['fields']['price'])
                    logger.debug(max_price)
                    logger.debug(percentage_diff)
                    logger.debug(trade)
                    logger.debug('down')
                    if abs(percentage_diff) > self.point:
                        ret = True


            time_to_query = time.time() - time_started_query
            logger.debug('Took {} to query'.format(time_to_query))
            if ret:
                for x in range(20):
                    logger.debug('truyu')
            return ret
        except influxdb.exceptions.InfluxDBClientError as e:
            logger.error('InfluxDB error: ' + str(e) + ' data: ' + str(trade.get_as_json_dict()))

        return False

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
                ret.append(alert)

        return ret

