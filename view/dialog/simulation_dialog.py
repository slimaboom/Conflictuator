from PyQt5.QtWidgets import (QDialog, QVBoxLayout, 
                             QLabel, QComboBox, 
                             QPushButton
)
from PyQt5.QtCore import QSize

from model.traffic.abstract.ATrafficGenerator import ATrafficGenerator
from model.traffic.abstract.ATrafficGeneratorDynamic import ATrafficGeneratorDynamic

from view.dialog.AParameterDialog import AParamDialog
from view.dialog.traffic_recorded_dialog import ATrafficGeneratorRecordedDialog

import sys

class SimulationDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Choose Traffic Generator")

        self.resize(self.width(), self.height())  # Définit une taille plus grande (largeur x hauteur)
        self.setMinimumSize(QSize(400, 200))  # Taille minimale pour éviter le rétrécissement

        # Initialisation des options principales
        self.available_traffic_generator_kind = ATrafficGenerator.get_available_traffic_generators()

        # Layout principal
        layout = QVBoxLayout(self)

        # 1. Sélection du type de trafic (première ComboBox)
        self.label_type = QLabel("Select Traffic Type:")
        self.combobox_type = QComboBox(self)
        self.combobox_type.addItems(self.available_traffic_generator_kind)
        self.combobox_type.currentIndexChanged.connect(self.update_subclasses)  # Mise à jour dynamique

        # 2. Sélection de la sous-classe de trafic (deuxième ComboBox)
        self.label_subtype = QLabel("Select Specific Generator:")
        self.combobox_subtype = QComboBox(self)  # Vide au début

        # 3. Bouton pour valider la sélection
        self.btn_validate = QPushButton("Validate")
        self.btn_validate.clicked.connect(self.validate_selection)

        # Ajout des widgets au layout
        layout.addWidget(self.label_type)
        layout.addWidget(self.combobox_type)
        layout.addWidget(self.label_subtype)
        layout.addWidget(self.combobox_subtype)
        layout.addWidget(self.btn_validate)

        # Mise à jour initiale des sous-classes
        self.update_subclasses()

    def update_subclasses(self):
        """ Met à jour la liste des sous-classes disponibles en fonction du choix de l'utilisateur. """
        selected_type = self.combobox_type.currentText() # Renvoie le nom de la classe stocker dans comme ['ATrafficGeneratorDynamic', 'ATrafficGeneratorRecorded']
        available_classes = ATrafficGenerator.get_traffic_generator_class(selected_type).get_available_traffic_generators()

        self.combobox_subtype.clear()
        self.combobox_subtype.addItems(available_classes)

    def get_parameters(self):
        """ Affiche le dialogue et retourne la classe sélectionnée par l'utilisateur. """
        selected_type = self.combobox_type.currentText()
        selected_subtype = self.combobox_subtype.currentText()

        # Récupération de la classe spécifique ATrafficGeneratorDynamic ou ATrafficGeneratorRecorded
        abstract_traffic_generator_class_type = ATrafficGenerator.get_traffic_generator_class(selected_type)
            

        # Récupération des paramètres pour final_class: 
        # container, reader, parser si de type ATrafficGeneratorRecorded
        # temps de simulation, autres hyper-paramètres ATrafficGeneratorDynamic
        
        # Utilisation de la classe "AParamDialog" pour rechercher les paramètres
        # Il faut aller chercher les hyper paramètres du constructeurs de la classe pour <selected_subtype> generator
        # #concrete_traffic_generator = abstract_traffic_generator_class_type.get_traffic_generator_class(selected_subtype)

        if abstract_traffic_generator_class_type == ATrafficGeneratorDynamic:
            traffic_generator_dialog = AParamDialog(class_or_function_name     = selected_subtype,
                                                    getters_function_or_method = abstract_traffic_generator_class_type.get_class_constructor_params,
                                                    parent=self)
            traffic_generator_dialog.create_inputs()
            traffic_generator_dialog.create_ok_button()
        else: #ATrafficGeneratorRecorded
            traffic_generator_dialog = ATrafficGeneratorRecordedDialog(traffic_generator_recorded_name=selected_subtype,
                                                                       parent=self)

        if traffic_generator_dialog.exec_() == QDialog.Accepted:
            # Récupération des paramètres du traffic générator
            hyperparameters_traffic_generator = traffic_generator_dialog.get_parameters()
            if hyperparameters_traffic_generator == None:
                self.close()
                sys.exit(0)
            return abstract_traffic_generator_class_type.create_traffic_generator(selected_subtype, **hyperparameters_traffic_generator) # Retourne la classe sélectionnée

        else:
            self.close()
            sys.exit(0)
    

    def validate_selection(self):
        """ Récupère la sélection finale et affiche un message. """
        self.accept()
