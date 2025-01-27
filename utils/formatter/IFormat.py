from abc import ABC, abstractmethod
from typing import Any

class IFormat(ABC):
    @abstractmethod
    def export(self, obj: Any) -> str:
        pass