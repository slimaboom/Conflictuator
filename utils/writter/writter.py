from utils.writter.AWritter import AWritter
from typing_extensions import override

@AWritter.register_writter
class FileWritter(AWritter):
    """Classe concrète de AWritter pour écrire dans un fichier"""

    @override
    def __init__(self, filename: str):
        super().__init__(container=filename)

    def __repr__(self):
        return f"{self.__class__.__name__}(container='{self.get_container()}')"
    
    @override
    def write(self, text: str) -> bool:
        filename = self.get_container()
        if not filename: return False
        
        try:
            with open(filename, 'w') as f:
                f.write(text)
            return True
        except Exception as e:
            return False