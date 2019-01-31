from mlogging import logger
from abc import ABC, abstractmethod
from typing import List, Type, Dict
from postgresql_init import engine
from sqlalchemy.sql import text


class Notification(ABC):
    @abstractmethod
    def __init__(self):
        self.notification_pk = None
        self.notify_on_which_alert = None

    @abstractmethod
    def notify(self):
        """Call this to fire off the notification.
        """
        pass

    @staticmethod
    @abstractmethod
    def get_all_from_db(alert_pk: int) -> List['Notification']:
        """Get all notifications from the database that are tied to the alert_pk.
        """
        pass
