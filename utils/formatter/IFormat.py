from abc import ABC, abstractmethod
from typing import Any, TYPE_CHECKING

class IFormat(ABC):
    @abstractmethod
    def export(self, obj: Any) -> str:
        pass