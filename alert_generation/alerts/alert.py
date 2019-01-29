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

    @abstractmethod
    def trigger(self, trade) -> bool:
        pass

    def mark_fulfilled(self):
        self.fulfilled = True

        with engine.begin() as conn:
            conn.execute(text("UPDATE ALERT SET fulfilled=TRUE WHERE alert_pk=:alert_pk"), alert_pk=self.alert_pk)

    @staticmethod
    @abstractmethod
    def get_all_from_db() -> List['Alert']:
        pass
