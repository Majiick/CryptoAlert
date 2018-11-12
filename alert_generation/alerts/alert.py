from abc import ABC, abstractmethod
from typing import List, Type, Dict

class Alert(ABC):
    @abstractmethod
    def __init__(self):
        pass

    @abstractmethod
    def trigger(self) -> bool:
        pass
