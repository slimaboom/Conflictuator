
from PyQt5.QtWidgets import (QComboBox, QLabel,
                            QDialog
)
from PyQt5.QtCore import Qt

from algorithm.interface.IAlgorithm import AAlgorithm
from algorithm.interface.IObjective import AObjective

from view.dialog.AParameterDialog import AParamDialog
from view.dialog.objectif_function_dialog import ObjectiveFunctionParamDialog

from typing_extensions import Dict, override

class AlgorithmParamDialog(AParamDialog):
    """
    :param algorithm_name (type: str): Nom de l'algorithme
    :param Parent (QWidget)
    """
    def __init__(self, algorithm_name, parent=None):

        super().__init__(class_or_function_name=algorithm_name, 
                    getters_function_or_method=AAlgorithm.get_class_constructor_params,
                    parent=parent)       
        
        self.create_inputs()
        self.creat_selection_objective_function()
        self.create_ok_button()
    
        self.__params_algorithm = None
        self.__params_objective = None

    def get_parameters(self):
        """
        Retourne un tuple contenant :
        - les paramètres de l'algorithme,
        - les paramètres de la fonction objective.
        """
        # Récupère les paramètres de l'algorithme
        self.__params_algorithm = super().get_parameters()

        # Récupère la fonction objective sélectionnée
        selected_function = self.objective_combo.currentText()
        
        # Ouvre la boîte de dialogue de la fonction objective
        if not selected_function:
            error = "\n\n\nNo objective function selected."
            error +="\nPlease register some objectif function by using"
            error += "\n@AObjectif.register_objective_function to register above derived class.\n\n"
            error += "The Objective Function must inheritance from AObjectif"
            raise ValueError(error)
        
        objective_dialog = ObjectiveFunctionParamDialog(objective_function_name=selected_function, parent=self.parent())

        if objective_dialog.exec_() == QDialog.Accepted:
            # Récupère les paramètres de la fonction objective
            self.__params_objective = objective_dialog.get_parameters()
            
            combined_parameters = {self.get_class_or_function_name(): self.__params_algorithm,
                                   selected_function: self.__params_objective}
            return combined_parameters
        

    def accept(self):
        """
        Déclenche la boîte de dialogue de la fonction objective après validation de l'algorithme.
        """
        super().accept()  # Ferme la boîte de dialogue actuelle (de l'algorithme)
        # Aucune action supplémentaire ici, car la fonction objective est déjà gérée dans get_parameters()
    
    def creat_selection_objective_function(self) -> None:
        # Lister les fonctions objectives
        self.objective_combo = QComboBox()
        objective_functions = AObjective.get_available_objective_functions()
        self.objective_combo.addItems(objective_functions)

        # Ajout de la liste déroulante à la mise en page
        row_index = self.get_grid_layout().rowCount()
        col_index =  self.get_grid_layout().columnCount()
        helf_left_col = col_index//2
        if col_index % 2 == 0:
            half_right_col  = helf_left_col
        else:
            half_right_col  = helf_left_col + 1        
        
        # Récupérer la prochaine ligne libre dans le grid layout

        # Ajouter le label sur les colonnes 0 et 1
        self.get_grid_layout().addWidget(QLabel("Select Objective Function:"), row_index, 0, 1, helf_left_col)

        # Ajouter le QComboBox sur les colonnes 2 et 3
        self.get_grid_layout().addWidget(self.objective_combo, row_index, 2, 1, half_right_col)
