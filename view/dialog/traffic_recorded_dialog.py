from PyQt5.QtWidgets import (QLabel, QPushButton,
                             QHBoxLayout, QFileDialog
                             
)
from logging_config import setup_logging
from view.dialog.AParameterDialog import AParamDialog
from utils.formatter.AFormat import AFormat
from utils.reader.AReader import AReader
from model.traffic.abstract.ATrafficGeneratorRecorded import ATrafficGeneratorRecorded

import sys

class ATrafficGeneratorRecordedDialog(AParamDialog):
    def __init__(self, traffic_generator_recorded_name, parent=None):
        # Logger
        self.logger = setup_logging(self.__class__.__name__)
        
        # Parent
        super().__init__(class_or_function_name=traffic_generator_recorded_name, 
                         getters_function_or_method=ATrafficGeneratorRecorded.get_class_constructor_params,
                         parent=parent)

        specific_inputs_types_dict = {
            AFormat: AFormat.get_available_formats(),
            AReader: AReader.get_available_readers()
        }
        self.create_inputs(specific_inputs_types_dict)
        self.create_ok_button()

    def create_file_input(self):
        """Ajoute un bouton pour choisir un fichier (associé à AReader)."""
        file_layout = QHBoxLayout()

        self.file_label = QLabel("No file selected")
        self.file_button = QPushButton("Choose a file")
        self.file_button.clicked.connect(self.open_file_dialog)

        file_layout.addWidget(self.file_label)
        file_layout.addWidget(self.file_button)
        self.layout().addLayout(file_layout)

        self.file_name = None  # Stocke le nom du fichier sélectionné        

    def open_file_dialog(self) -> None:
        """Ouvre une boîte de dialogue pour choisir un fichier."""
        file_name, _ = QFileDialog.getOpenFileName(self, "Choose a file", "", "JSON File (*.json);;All Files (*)")
        if file_name:
            self.file_name = file_name
            self.file_label.setText(file_name)  # Met à jour le label

    def get_parameters(self):
        """Retourne les paramètres convertis avec les bonnes instances."""
        params = super().get_parameters()
        # Exemple des paramètres qui devrait arrivés.
        #[2025-02-01 15:30:33,006] - INFO - traffic_recorded_dialog.ATrafficGeneratorRecordedDialog@get_parameters: {'reader': 'FileReader', 'parser': 'JSONFormat'}
        # {'reader': 'FileReader', 'parser': 'JSONFormat'}

        self.create_file_input()
        self.open_file_dialog()
        if self.file_name == None:
            return None
        traffic_parameters = {}
        for param_name, param_class in params.items():
            if issubclass(param_class, AFormat):
                formatter_instance = param_class()
                traffic_parameters[param_name] = formatter_instance
            elif issubclass(param_class, AReader):
                reader_instance = param_class(source=self.file_name)
                traffic_parameters[param_name]  = reader_instance
        self.logger.info(traffic_parameters)
        return traffic_parameters