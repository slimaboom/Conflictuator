from algorithm.interface.IObjective import AObjective
from view.dialog.AParameterDialog import AParamDialog

class ObjectiveFunctionParamDialog(AParamDialog):
    def __init__(self, objective_function_name, parent=None):
        
        super().__init__(class_or_function_name=objective_function_name, 
                         getters_function_or_method=AObjective.get_class_constructor_params,
                         parent=parent)
        self.create_inputs()
        self.create_ok_button()
