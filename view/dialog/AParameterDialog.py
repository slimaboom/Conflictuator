from PyQt5.QtWidgets import (QDialog, QLayout, QWidget,
                             QVBoxLayout, QGridLayout,
                             QLabel, QComboBox, 
                             QPushButton, QLineEdit, 
)

from typing import Callable
from types import MappingProxyType
import inspect

class AParamDialog(QDialog):
    """
    :param class_or_function_name (type: str): Nom de la class ou fonction
    :param getters_function_or_method (type: Callable[[str], MappingProxyType[str, inspect.Parameter]]): 
        fonction pour récupérer les paramètres de <class_or_function_name>
    :param Parent (QWidget)
    """

    def __init__(self, class_or_function_name: str, getters_function_or_method: Callable[[str], MappingProxyType[str, inspect.Parameter]], parent: QWidget=None):
        super().__init__(parent=parent)
        self.setWindowTitle(f"Configure hyper-parameters for {class_or_function_name}")

        self.__main_layout = QVBoxLayout()
        self.__main_layout.addWidget(QLabel(f"Enter parameter value for {class_or_function_name}:"))

        self.__class_or_function_name = class_or_function_name
        self.__getters_function_or_method = getters_function_or_method
        self.true_str = str(True)
        self.false_str = str(False)

        self.__grid_layout = QGridLayout()
        self.param_inputs = {}
        self.param_types = {}

        self.__main_layout.addLayout(self.__grid_layout)

        # Définir le layout principal
        self.setLayout(self.__main_layout)
        
    def get_grid_layout(self) -> QGridLayout:
        return self.__grid_layout

    def get_main_layout(self) -> QVBoxLayout:
        return self.__main_layout

    def get_class_or_function_name(self) -> str:
        return self.__class_or_function_name

    def create_inputs(self) -> None:
        # Définition des titres de colonnes
        headers = ["Name", "Type", "Default", "Value"]
        row = self.__grid_layout.rowCount()
        for col, header in enumerate(headers):
            header_label = QLabel(header)
            self.__grid_layout.addWidget(header_label, row, col)

        # Récupération des paramètres du constructeur
        for row, (param_name, param) in enumerate(self.__getters_function_or_method(self.__class_or_function_name).items()):
            # AAlgorithm.get_function_constructor_params verifie deja que l'annotation n'est pas vide normalement
            if param.annotation == inspect.Parameter.empty:
                raise TypeError(f"Parameter'{param_name}' without annotations. Please annotate this parameter to use AAlgorithm derived class")
            
            row_placement = self.__grid_layout.rowCount() + 1
            
            expected_type = param.annotation  # Récupérer l'annotation
            self.param_types[param_name] = expected_type  # Stocker le type
            
            # Création des colonnes
            name_label = QLabel(param_name)
            self.__grid_layout.addWidget(name_label, row_placement, 0)

            type_label = QLabel(str(expected_type.__name__))
            self.__grid_layout.addWidget(type_label, row_placement, 1)

            default_value = str(param.default) if param.default != inspect.Parameter.empty else ""
            default_label = QLabel(default_value)
            self.__grid_layout.addWidget(default_label, row_placement, 2)

            # Si le type est `bool`, on utilise un menu déroulant (QComboBox)
            if expected_type == bool:
                input_field = QComboBox()
                input_field.addItems([self.true_str, self.false_str])
                # Sélectionner la valeur par défaut si elle est définie
                if param.default is not inspect.Parameter.empty:
                    input_field.setCurrentText(default_value)
            else:
                input_field = QLineEdit()
                input_field.setText(default_value)

            self.__grid_layout.addWidget(input_field, row_placement, 3)
            self.param_inputs[param_name] = input_field

    def get_parameters(self):
        """
        Retourne les paramètres convertis dans le bon type.
        """
        converted_params = {}
        for param_name, input_field in self.param_inputs.items():
            expected_type = self.param_types[param_name]

            if expected_type == bool:
                value = input_field.currentText()  # Récupérer la valeur sélectionnée dans le QComboBox
                converted_params[param_name] = value == self.true_str # Convertir en booléen
            else:
                value = input_field.text().strip()
                try:
                    converted_params[param_name] = expected_type(value)  # Conversion directe
                except ValueError as e:
                    raise ValueError(f"\n\nConversion error for '{param_name}': impossible to convert '{value}' in {expected_type}") from e
        return converted_params

    def create_ok_button(self):
        # Bouton OK
        self.ok_button = QPushButton("OK")
        self.ok_button.clicked.connect(self.accept)
        self.__main_layout.addWidget(self.ok_button)

        self.setLayout(self.__main_layout)