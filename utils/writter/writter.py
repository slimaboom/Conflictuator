from utils.writter.AWritter import AWritter
from typing_extensions import override

@AWritter.register_writter('filewritter')
class FileWritter(AWritter):
    """Classe concrète de AWritter pour écrire dans un fichier"""

    @override
    def __init__(self, filename: str):
        super().__init__(container=filename)

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