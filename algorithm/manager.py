from threading import Thread
from queue import Queue
from typing import Any, Dict, List, Tuple

from algorithm.interface.IAlgorithm import AlgorithmState, AAlgorithm
from algorithm.interface.IObjective import AObjective
from algorithm.interface.ISimulatedObject import ASimulatedAircraft
from algorithm.data import SimulatedAircraftImplemented

from logging_config import setup_logging

class AlgorithmManager:
    def __init__(self):
        self._algorithm: 'AAlgorithm' = None
        self._data: List['ASimulatedAircraft'] = None
        self._thread: Thread = None
        self._instance: 'AAlgorithm' = None
        self.__singleton_start = False
        self.logger = setup_logging(__class__.__name__)

    def create_algorithm(self, aalgorithm: AAlgorithm, *args, **kwargs) -> None:
        """Définit l'algorithme à utiliser."""
        self._algorithm = aalgorithm
        self.logger.info(kwargs)
        # Parse les arguments
        aalgorithm_constructor_parameters = kwargs.pop(aalgorithm.__name__)
        aobjective_function_name = list(kwargs)[0] # Il ne doit rester qu'une seule clé + la clé AAlgorithm.NUMBER_OF_LAYERS_KEY
        aobjective_function_constructor_parameters = kwargs.pop(aobjective_function_name)

        # Creation de l'instance de AAlgorithm
        self._instance = AAlgorithm.create_algorithm(aalgorithm.__name__, self._data_to_algo, **aalgorithm_constructor_parameters)
        
        # Création de l'instance de AObjective
        aobjective_function = AObjective.create_objective_function(aobjective_function_name, **aobjective_function_constructor_parameters)
        self._instance.set_objective_function(aobjective_function)
 
        # Création des layers/couches pour self._instance
        number_of_layers = aalgorithm_constructor_parameters.get(AAlgorithm.NUMBER_OF_LAYERS_KEY)
        if number_of_layers:
            layers_dict = kwargs.pop(AAlgorithm.NUMBER_OF_LAYERS_KEY)
            # Exemple:
            #  {1: {'HyperbandOptimizer': 
            #         {'is_minimise': True, 'num_samples': 20, 'max_epochs': 99, 
            #           'verbose': False, 'timeout': datetime.time(0, 2)}, 
            #        'ObjectiveFunctionMaxConflict': {}}}}
            if layers_dict:
                layers = []
                available_algorithms = AAlgorithm.get_available_algorithms()
                available_objectives = AObjective.get_available_objective_functions()
                for layer_number, params in layers_dict.items():
                    layer = self.create_layer(layer_number,
                                              params,
                                              available_algorithms,
                                              available_objectives)
                    layers.append(layer)
                self._instance.set_layers(layers=layers)
        self._instance.display_layers()

    def create_layer(self, layer_number: int, layer_dictionnary: Dict[str, Dict], available_algorithms: List[str], available_functions: List[str]):
        """Create a layer for main algorithm"""
        algorithm_layer           = None
        objective_function_layer  = None
        for algo_name_or_objective_function_name, hyperparameters in layer_dictionnary.items():
            is_algorithm = algo_name_or_objective_function_name in available_algorithms
            is_function  = algo_name_or_objective_function_name in available_functions
            if (not is_algorithm) and (not is_function):
                error = f"Layer {layer_number} Error for main algorithm {self._algorithm.__name}"
                error += f"\n{algo_name_or_objective_function_name} not registed in AAlgorithm neither in AObjective"
                error += f"\n\nDepending on which kind of class it's, register in the corrected class, using"
                error += f"\n@AAlgorithm.register_algorithm above your class or @AObjective.register_objective_function"
                raise ValueError(error)
            
            # Instanciation
            if is_algorithm:
                algorithm_layer = AAlgorithm.create_algorithm(algo_name_or_objective_function_name, 
                                                              self._data_to_algo,
                                                              **hyperparameters)
                # Nom de l'algorithm de la layer
                name = f"{self._algorithm.__name__}: Layer {layer_number} - Algo: {algo_name_or_objective_function_name}"
                algorithm_layer.set_name(name)
            
            if is_function:
                objective_function_layer = AObjective.create_objective_function(algo_name_or_objective_function_name, **hyperparameters)
                # Nom de la fonction objective de la layer
                objective_name = f"{self._algorithm.__name__}: Layer {layer_number} - ObjectiveFunction: {algo_name_or_objective_function_name}"
                objective_function_layer.set_name(objective_name)

        # Sortir de la configuration de la layer
        if algorithm_layer == None:
            error = f"Main algorithm: {self._algorithm.__name__}\n"
            error += f"No algorithm found in layer {layer_number}"
            raise ValueError(error)

        if objective_function_layer == None:
            error = f"Main algorithm: {self._algorithm.__name__}\n"
            error += f"No objective found in layer {layer_number}\n"
            error += f"used for {algorithm_layer.__name}"
            raise ValueError(error)

        algorithm_layer.set_objective_function(objective_function_layer)
        msg = f"Created layer {layer_number} for {self._algorithm.__name__} using\n"
        msg += f"as internal algorithm: {algorithm_layer.get_name()}\n"
        msg += f"with objective function {algorithm_layer.get_objective_function().get_name()}"
        self.logger.info(msg)
        return algorithm_layer
    
    def get_algorithm(self) -> AAlgorithm:
        """Renvoie l'algorithme actuellement configuré."""
        return self._algorithm

    def set_data(self, data: List[Any]) -> None:
        """Definit les donnees utilisees pour l'algorithme."""
        # Transformer les avions en objets pour l'algorithme
        self._data_to_algo = [SimulatedAircraftImplemented(aircraft) for aircraft in data]


    def start_algorithm(self, queue: 'Queue') -> None:
        """
        Lance l'algorithme dans un thread séparé et retourne les résultats.
        """
        if not self._instance:
            raise ValueError("Aucun algorithme n'est défini ou instancié.")


        # Créer et démarrer un thread pour exécuter l'algorithme
        self._thread = Thread(target=self._run_algorithm_in_thread, args=(queue,), )
        self._thread.start()
        self.__singleton_start = True

    def _run_algorithm_in_thread(self, result_queue: Queue) -> None:
        """
        Méthode interne qui exécute l'algorithme dans un thread séparé.
        Elle place les résultats dans la Queue.
        """
        try:
            # Exécuter l'algorithme (par exemple recuit simulé)
            result = self._instance.start()
            #result = [DataStorage(speed=0.002, id=1), DataStorage(speed=0.003, id=2), DataStorage(speed=0.003, id=3), DataStorage(speed=0.003, id=4)]
            result_queue.put(result)  # Mettre le résultat dans la Queue
        except Exception as e:
            # En cas d'erreur, on met l'exception dans la Queue
            result_queue.put(e)
    
    def stop_algorithm(self) -> None:
        if self._thread and self._thread.is_alive():
            self._instance.stop()
            self.logger.info(f"Stopping {self._instance}")
    
    def progress_algorithm(self) -> float:
        return self._instance.get_progress()

    def process_time_algorithm(self) -> Tuple[float, float]:
        return self._instance.get_process_time(), self._instance.get_timeout_value()
    
    def get_algorithm_state(self) -> AlgorithmState:
        return self._instance.get_state()

    def has_been_lauch(self) -> bool:
        return self.__singleton_start
    
    def is_algorithm_error(self) -> bool:
        return self.get_algorithm_state() == AlgorithmState.ERROR
    
    def get_best_critere(self) -> float:
        if self._instance:
            return self._instance.get_best_critere()