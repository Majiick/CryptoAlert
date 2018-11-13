from abc import ABC, abstractmethod
from typing import List, Type, Dict

class Alert(ABC):
    @abstractmethod
    def __init__(self):
        self.alert_pk = None
        self.created_by_user = None
        self.fulfilled = None
        self.repeat = None

    @abstractmethod
    def trigger(self) -> bool:
        pass

    @staticmethod
    @abstractmethod
    def get_all_from_db() -> List['Alert']:
        pass
