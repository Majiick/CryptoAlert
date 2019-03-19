from abc import ABC, abstractmethod
from typing import List, Type, Dict
from postgresql_init import engine
from sqlalchemy.sql import text
from mlogging import logger


class Alert(ABC):
    @abstractmethod
    def __init__(self):
        self.alert_pk = None
        self.created_by_user = None
        self.fulfilled = None
        self.repeat = None
        self.broadcast_interesting_event_on_trigger = None

    @abstractmethod
    def trigger(self, trade) -> bool:
        """ Call this to find out if the alert triggers or not on the passed in trade.
        """
        pass

    @abstractmethod
    def get_interesting_event_description(self):
        """ Call this to get the interesting event dictionary. Should contain all the fields as in the INTERESTING_EVENT table in the SQL schema.
        """
        pass

    def mark_fulfilled(self):
        self.fulfilled = True

        with engine.begin() as conn:
            conn.execute(text("UPDATE ALERT SET fulfilled=TRUE WHERE alert_pk=:alert_pk"), alert_pk=self.alert_pk)

    @staticmethod
    @abstractmethod
    def get_all_from_db() -> List['Alert']:
        pass
