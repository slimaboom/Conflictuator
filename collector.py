from abc import ABC
from collections import defaultdict
from typing import List, Dict, TypeVar, Generic, Union

T= TypeVar('T')

class Collector(ABC, Generic[T]):
    def __init__(self, key: str = None, values: Union[List[T], T] = None):
        self._database = defaultdict(dict)
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

            print(f"Sector with name:' '{key}' is not defined ! Skipped")
    
    def get_all(self) -> Dict[str, Union[List[T], T]]:
        return self._database
    
    def get_from_key(self, key: str) -> Union[List[T], T]:
        return self._database.get(key)

    def __repr__(self) -> str:
        attr = ", ".join([f"'{key}'" for key in self.get_all()])
        return f"Sector({attr})"
