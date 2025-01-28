from collections import defaultdict
from typing import List, Dict, TypeVar, Generic

T= TypeVar('T')

class Collector(Generic[T]):
    def __init__(self, key: str = None, values: T = None):
        self._database = {}
        if key: self.add(key, values)
    
    def add(self, key: str, value: T) -> None:
        if not key in self._database:
            self._database[key] = value
        else:
            msg = f"{self.__class__.__name__} with key: '{key} is already defined ! Skipped"
            print(msg)
    
    def delete(self, key) -> None:
        if key in self._database:
            del self._database[key]
        else:
            msg = f"{self.__class__.__name__} with key: '{key} is not defined ! Skipped"
            print(msg)
    
    def get_all(self) -> Dict[str, T]:
        return self._database
    
    def get_from_key(self, key: str) -> T:
        return self._database.get(key)

    def __repr__(self) -> str:
        attr = ", ".join([f"'{key}'" for key in self.get_all()])
        return f"Collector({attr})"
    
    def is_empty(self): return len(self._database) == 0

    def __contains__(self, key: str) -> bool:
        return key in self._database
    
    def __iter__(self):
        return iter(self._database)
    
    def clear(self) -> None:
        self._database.clear()
    
    def __len__(self):
        return len(self._database)