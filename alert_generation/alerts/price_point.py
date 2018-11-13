from alert import Alert
import sqlalchemy
import psycopg2
import time
from postgresql_init import engine
from sqlalchemy.sql import text
from typing import List, Type, Dict


class PricePoint(Alert):
    # TODO: These need to access Exchange, Pair etc. from the data_api folder.
    def __init__(self, exchange: str, pair: str, point: float, direction: str):
        assert(direction == 'up' or direction == 'down')

        self.exchange = exchange
        self.pair = pair
        self.point = point
        self.direction = direction

    # TODO: Have a common interface for passing in continuous data
    def trigger(self, trade) -> bool:
        if (trade['tags']['pair'] == self.pair or self.pair == '*') and (trade['tags']['exchange'] == self.exchange or self.exchange == '*'):
            if self.direction == 'up':
                if float(trade['fields']['price']) > self.point:
                    return True
            elif self.direction == 'down':
                if float(trade['fields']['price']) < self.point:
                    return True

        return False

    @staticmethod
    def get_all_from_db() -> List[Alert]:
        ret = []

        with engine.begin() as conn:
            result = conn.execute("select * from PRICE_POINT_ALERT WHERE fulfilled = FALSE")
            for row in result:
                alert = PricePoint(row['exchange'], row['pair'], row['point'], row['direction'])
                alert.alert_pk = row['alert_pk']
                alert.created_by_user = row['created_by_user']
                alert.fulfilled = row['fulfilled']
                alert.repeat = row['repeat']
                ret.append(alert)

        return ret

