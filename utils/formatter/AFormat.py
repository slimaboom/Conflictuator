from abc import abstractmethod
from utils.formatter.IFormat import IFormat
from typing import List, TYPE_CHECKING

if TYPE_CHECKING:
    from model.aircraft import Aircraft

class AFormat(IFormat):
    @abstractmethod
    def export(self, obj: List['Aircraft']) -> str:
        pass