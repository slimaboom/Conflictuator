from PyQt5.QtWidgets import (QDialog, QVBoxLayout, 
                             QHBoxLayout, QLabel, 
                             QComboBox, QPushButton, 
                             QFileDialog, QMessageBox
                            )
from typing import Tuple

from utils.formatter.AFormat import AFormat
from utils.writter.AWritter import AWritter

class RecordDialog(QDialog):
    def __init__(self, parent=None, available_formats=None, available_writers=None):
        super().__init__(parent)
        self.setWindowTitle("Choose which format types and writter types")

        # Initialisation des options
        self.available_formats = available_formats or AFormat.get_available_formats()
        self.available_writers = available_writers or AWritter.get_available_writters()

        # Layout principal
        layout = QVBoxLayout(self)

        # Section format
        format_layout = QHBoxLayout()
        format_label = QLabel("Format :")
        self.format_combobox = QComboBox()
        self.format_combobox.addItems(self.available_formats)
        format_layout.addWidget(format_label)
        format_layout.addWidget(self.format_combobox)
        layout.addLayout(format_layout)

        # Section type d'écriture
        writer_layout = QHBoxLayout()
        writer_label = QLabel("Writter :")
        self.writer_combobox = QComboBox()
        self.writer_combobox.addItems(self.available_writers)
        writer_layout.addWidget(writer_label)
        writer_layout.addWidget(self.writer_combobox)
        layout.addLayout(writer_layout)

        # Bouton pour ouvrir la boîte de dialogue de sélection de fichier
        file_button = QPushButton("Choose a file")
        file_button.clicked.connect(self.open_file_dialog)
        layout.addWidget(file_button)

        self.file_name = None  # Attribut pour stocker le nom de fichier choisi


    def open_file_dialog(self) -> None:
        """Ouvre une boîte de dialogue pour choisir un fichier avec une extension valide."""

        file_name, _ = QFileDialog.getSaveFileName(self, "Type a file", "", "JSON File (*.json);;All files (*)")
        
        if file_name:
            # Vérifie si le fichier choisi a une extension valide
            if '.' not in file_name:
                self.show_error_message("The name should include an extension (name.txt for exemple).")
                return  # Ne pas fermer la fenêtre si le fichier est invalide
                
            self.file_name = file_name  # Stocke le nom du fichier choisi
            self.accept()  # Ferme le RecordDialog lorsque le fichier est valide
            
    def get_selection(self) -> Tuple[AFormat, AWritter, str]:
        """
        Retourne les objets format et writter, ainsi que le nom du fichier saisi.
        """
        fmt_name = self.format_combobox.currentText()
        writter_name = self.writer_combobox.currentText()

        # Assure s que le nom du fichier est valide
        while not self.file_name or '.' not in self.file_name:
            return self.get_selection()  # Redemander l'entrée à l'utilisateur

        return AFormat.create_formatter(fmt_name), AWritter.create_writter(writter_name, container=self.file_name)


    def show_error_message(self, message: str) -> None:
        """ Affiche une boîte de dialogue d'erreur. """
        self.__show_message(message=message, title="No extension found.", icon=QMessageBox.Critical)

    def show_accepted_message(self, message: str) -> None:
        """ Affiche une boîte de dialogue d'erreur. """
        self.__show_message(message=message, title="Record", icon=QMessageBox.Information)


    def __show_message(self, message: str, title: str, icon: QMessageBox.Icon) -> None:
        parent = self.parent() or self  # Utilise le parent si défini, sinon utilise self
        msg_box = QMessageBox(parent)
        msg_box.setIcon(icon)
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        msg_box.exec_()