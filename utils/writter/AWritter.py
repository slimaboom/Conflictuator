from utils.writter.IWritter import IWritter
from typing_extensions import override
from abc import abstractmethod

class AWritter(IWritter):

    @abstractmethod
    def __init__(self, filename: str):
        self.__filename = filename

    def set_filename(self, filename: str) -> None:
        self.__filename = filename

    @override
    def writer(self, text: str) -> bool:
        if not self.__filename: return False
        
        try:
            with open(self.__filename) as f:
                f.write(text)

            return True
        
        except Exception as e:
            return False