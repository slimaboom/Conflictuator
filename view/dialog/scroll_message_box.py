from PyQt5.QtWidgets import QMessageBox, QScrollArea, QLabel, QWidget, QVBoxLayout

class ScrollableMessageBox(QMessageBox):
    def __init__(self, parent=None):
        super().__init__(parent)
        # On retire le texte par défaut de la QMessageBox
        self.setText("")
        
        # Création du QScrollArea et configuration
        self.scroll_area = QScrollArea(self)
        self.scroll_area.setWidgetResizable(True)
        
        # Création d'un widget conteneur pour le contenu scrollable
        self.scroll_widget = QWidget()
        self.scroll_area.setWidget(self.scroll_widget)
        
        # Layout pour placer le texte dans le widget conteneur
        self.scroll_layout = QVBoxLayout(self.scroll_widget)
        self.message_label = QLabel(self)
        self.message_label.setWordWrap(True)
        self.scroll_layout.addWidget(self.message_label)
        
        # Ajout de la zone scrollable dans le layout de la QMessageBox
        layout = self.layout()
        # On l'ajoute sur une nouvelle ligne en fin de layout, en occupant toute la largeur
        layout.addWidget(self.scroll_area, layout.rowCount(), 0, 1, layout.columnCount())
    
    def setScrollableText(self, text):
        self.message_label.setText(text)
