from utils.reader.AReader import AReader
from typing_extensions import override

@AReader.register_reader
class FileReader(AReader):
    """Lit des données depuis un fichier."""

    def __init__(self, source: str):
        super().__init__(source)

    def __repr__(self):
        return f"{self.__class__.__name__}(source='{self.source}')" 

    @override
    def read(self) -> str:
        """Lit le contenu d'un fichier et le retourne sous forme de chaîne."""
        with open(self.get_source(), 'r', encoding='utf-8') as f:
            return f.read()
