from abc import ABC, abstractmethod

class IWritter(ABC):
    @abstractmethod
    def writer(self, text: str) -> bool:
        pass