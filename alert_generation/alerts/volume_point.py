from alert import Alert
import sqlalchemy
import psycopg2
import time
from postgresql_init import engine
from sqlalchemy.sql import text
from typing import List, Type, Dict
from mlogging import logger


class VolumePoint(Alert):
    # TODO: These need to access Exchange, Pair etc. from the data_api folder.
    def __init__(self, exchange: str, pair: str, point: float):
        self.exchange = exchange
        self.pair = pair
        self.point = point

    def trigger(self, trade) -> bool:
        if (trade['tags']['pair'].lower() == self.pair.lower() or self.pair == '*') and (trade['tags']['exchange'].lower() == self.exchange.lower() or self.exchange == '*'):
            if float(trade['fields']['size']) > self.point:
                return True

        return False

    def get_interesting_event_description(self):
        return 'Not Implemented'

    @staticmethod
    def get_all_from_db() -> List[Alert]:
        ret: List[Alert] = []

        with engine.begin() as conn:
            result = conn.execute("select * from VOLUME_POINT_ALERT WHERE fulfilled = FALSE")
            for row in result:
                alert = VolumePoint(row['exchange'], row['pair'], row['point'])
                alert.alert_pk = row['alert_pk']
                alert.created_by_user = row['created_by_user']
                alert.fulfilled = row['fulfilled']
                alert.repeat = row['repeat']
                alert.broadcast_interesting_event_on_trigger = row['broadcast_interesting_event_on_trigger']
                alert.alert_type = row['alert_type']
                ret.append(alert)

        return ret