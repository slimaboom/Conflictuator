from PyQt5.QtWidgets import (QDialog, QWidget,
                             QVBoxLayout, QHBoxLayout, QGridLayout,
                             QLabel, QComboBox, 
                             QPushButton, QLineEdit, QSpinBox, QDoubleSpinBox,
                             QSizePolicy
)

from datetime import time
from typing import Dict, Callable, List, Type
from types import MappingProxyType
from utils.controller.database_dynamique import MetaDynamiqueDatabase

import numpy as np
import inspect
import locale  # Avec locale.atof(), le programme prend en compte automatiquement le séparateur décimal (. ou ,) selon la configuration de l'utilisateur.

class AParamDialog(QDialog):
    """
    :param class_or_function_name (type: str): Nom de la class ou fonction
    :param getters_function_or_method (type: Callable[[str], MappingProxyType[str, inspect.Parameter]]): 
        fonction pour récupérer les paramètres de <class_or_function_name>
    :param Parent (QWidget)
    """

    TRUE_OR_FALSE_STR = ['True', 'False']

    def __init__(self, class_or_function_name: str, 
                 getters_function_or_method: Callable[[str], MappingProxyType[str, inspect.Parameter]], 
                parent: QWidget=None):
        super().__init__(parent=parent)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setWindowTitle(f"Configure hyper-parameters for {class_or_function_name}")
        self.adjustSize()
        
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

        self.str_bools = [self.true_str, self.false_str]

    def adjustSize(self):
        super().adjustSize()
        font_metrics = self.fontMetrics()
        title_width = font_metrics.width(self.windowTitle())  # Ajoute un peu d'espace
        self.setMinimumWidth(max(self.minimumWidth(), int(1.5*title_width)))

    def get_grid_layout(self) -> QGridLayout:
        return self.__grid_layout

    def get_main_layout(self) -> QVBoxLayout:
        return self.__main_layout

    def get_class_or_function_name(self) -> str:
        return self.__class_or_function_name

    def create_combox(self, items: List):
        input_field = QComboBox(self)
        input_field.setParent(self.parent().parent())
        input_field.addItems(items)
        return input_field

    def create_inputs(self, specific_inputs_types_dict: Dict[Type, List[str]] = {bool: TRUE_OR_FALSE_STR}) -> None:
        # Sauvegardes types particuliers bool/Enum, ou AFormat, AWriter, AAlgorithm, ATrafficGenerator[Dynamic|Recorded]
        self.specific_inputs_types_dict = specific_inputs_types_dict

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
            # Sélection de l'input approprié
            if specific_inputs_types_dict and expected_type in specific_inputs_types_dict:
                input_field = self.create_combox(items=specific_inputs_types_dict.get(expected_type))
                if param.default is not inspect.Parameter.empty:
                    input_field.setCurrentText(default_value)

            elif expected_type == time:
                input_field = self.add_time_input(param.default)  # Gestion du type `time`                

            elif expected_type == int or expected_type == float:
                if expected_type == int:
                    input_field = QSpinBox(self)
                    input_field.setMinimum(0)
                    input_field.setMaximum(2100500)
                    input_field.setSingleStep(1)

                elif expected_type == float:
                    input_field = QDoubleSpinBox(self)
                    input_field.setMaximum(float('inf'))
                    
                    # Calcul de l'ordre de grandeur du pas
                    if param.default != inspect.Parameter.empty and param.default != 0:
                        exponent = np.floor(np.log10(abs(param.default)))  # Exponent de la valeur
                        if exponent <0:
                            exponent = exponent - 2
                            step = 10**(exponent)  # Un ordre de grandeur plus bas
                        else:
                            exponent = -1
                            step = 0.1
                    else:
                        exponent = -3
                        step = 1e-3  # Valeur par défaut si 0

                    num_decimals = max(0, abs(int(exponent)))
                    input_field.setDecimals(num_decimals)  # Ajuster le nombre de décimales dynamiquement

                    # Ajuster la taille de la spinbox pour bien voir les valeurs
                    input_field.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
                    input_field.setSingleStep(step)

                else:
                    continue

                if param.default is not inspect.Parameter.empty:
                    input_field.setValue(param.default)

            else:
                input_field = QLineEdit()
                input_field.setText(default_value)

            self.__grid_layout.addWidget(input_field, row_placement, 3)
            input_field.setParent(self)
            self.param_inputs[param_name] = input_field  # Stockage de l'input


    def add_time_input(self, default_value):
        """ Ajoute une entrée sous forme de 3 spinboxes (HH:MM:SS) pour les paramètres de type `time`. """
        widget = QWidget()
        layout = QHBoxLayout(widget)
        widget.setLayout(layout)

        # Créer les trois SpinBoxes pour heures, minutes et secondes
        self.hours_spinbox = QSpinBox()
        self.hours_spinbox.setRange(0, 99)
        
        self.minutes_spinbox = QSpinBox()
        self.minutes_spinbox.setRange(0, 59)
        
        self.seconds_spinbox = QSpinBox()
        self.seconds_spinbox.setRange(0, 59)

        # Si une valeur par défaut existe, la convertir en HH:MM:SS
        if isinstance(default_value, time):
            h, m, s = default_value.hour, default_value.minute, default_value.second
            self.hours_spinbox.setValue(h)
            self.minutes_spinbox.setValue(m)
            self.seconds_spinbox.setValue(s)

        # Ajouter les widgets au layout
        layout.addWidget(self.hours_spinbox)
        layout.addWidget(self.minutes_spinbox)
        layout.addWidget(self.seconds_spinbox)
        return widget


    def get_parameters(self):
        """
        Retourne les paramètres convertis dans le bon type.
        """
        converted_params = {}
        for param_name, input_field in self.param_inputs.items():
            expected_type = self.param_types[param_name]

            if self.specific_inputs_types_dict and expected_type in self.specific_inputs_types_dict:
                value = input_field.currentText()  # Récupérer la valeur sélectionnée dans le QComboBox
                if bool in self.specific_inputs_types_dict:
                    converted_params[param_name] = value == self.TRUE_OR_FALSE_STR[0]
                else:
                    converted_params[param_name] = MetaDynamiqueDatabase.get_class(expected_type, value)
                    # Par exemple ca renvoie ca
                    # print(param_name, converted_params[param_name])
                    # reader <class 'utils.reader.FileReader.FileReader'>
                    # parser <class 'utils.formatter.format.JSONFormat'>
                    
            elif expected_type == time:  # Gérer le type `time`
                hours = self.hours_spinbox.value()
                minutes =self.minutes_spinbox.value()
                seconds = self.seconds_spinbox.value()
                converted_params[param_name] = time(hour=hours, minute=minutes, second=seconds)
                #print(param_name, converted_params[param_name])  # Convertir en secondes                
            else:

                value = input_field.text().strip()
                try:
                    if expected_type == int or expected_type == float:
                        value = locale.atof(value)
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
