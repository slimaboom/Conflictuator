from threading import Thread
from queue import Queue
from typing import Any, List, Tuple
from algorithm.genetic.genetique import AlgorithmGenetic
from algorithm.genetic.genetique_intervalles import AlgorithmGeneticIntervalles
from algorithm.objective_function.conflict_exact import ObjectiveFunctionConflict
from algorithm.objective_function.function import ObjectiveFunctionMaxConflict, ObjectiveFunctionMaxConflictMinVariation
#from algorithm.objective_function.mix_objective import CombinedEvaluationStrategy

from algorithm.interface.IAlgorithm import AlgorithmState, AAlgorithm
from algorithm.type import AlgoType
from algorithm.recuit.recuit import AlgorithmRecuit
from algorithm.data import SimulatedAircraftImplemented

from logging_config import setup_logging

class AlgorithmManager:
    def __init__(self):
        self._algorithm = None  # Algorithme courant
        self._data = None
        self._thread = None
        self._instance = None
        self.__singleton_start = False
        self.logger = setup_logging(__class__.__name__)

    def set_algorithm(self, algorithm: AlgoType) -> None:
        """Définit l'algorithme à utiliser."""
        self._algorithm = algorithm

    def get_algorithm(self) -> AlgoType:
        """Renvoie l'algorithme actuellement configuré."""
        return self._algorithm

    def set_data(self, data: List[Any]) -> None:
        """Definit les donnees utilisees pour l'algorithme."""
        self._data = data
        self._create_instance_algo()

    def _create_instance_algo(self):
        if self._algorithm == AlgoType.RECUIT:
            # Transformer les avions en objets pour le recuit
            data_to_recuit = [SimulatedAircraftImplemented(aircraft) for aircraft in self._data]
            self._instance = AlgorithmRecuit(data_to_recuit, is_minimise=False) 

            # Creation de l'instance fonction objective
            function_objectif = ObjectiveFunctionMaxConflict()
            # Envoie de l'instance dans l'algorithme genetique
            self._instance.set_objective_function(function_objectif)

        elif self._algorithm == AlgoType.GENETIQUE:
            # Transformer les avions en objets pour l'algorithme génétique
            data_to_genetic = [SimulatedAircraftImplemented(aircraft) for aircraft in self._data]
            self.instance = AlgorithmGenetic(data_to_genetic, is_minimise=True, population_size=15, generations=30)

            # Creation de l'instance fonction objective
            function_objectif = ObjectiveFunctionConflict()
            function_objectif.set_nb_expected_conflict(4)
            # Envoie de l'instance dans l'algorithme genetique
            self.instance.set_objective_function(function_objectif)
        
        elif self._algorithm == AlgoType.GENETIQUEINT:
            # Transformer les avions en objets pour l'algorithme génétique
            data_to_genetic = [SimulatedAircraftImplemented(aircraft) for aircraft in self._data]
            self.instance = AlgorithmGeneticIntervalles(data_to_genetic, is_minimise=True, population_size=5, generations=5)

            # Creation de l'instance fonction objective
            function_objectif = ObjectiveFunctionConflict()
            #function_objectif.set_nb_expected_conflict(12)
            # Envoie de l'instance dans l'algorithme genetique
            self._instance.set_objective_function(function_objectif)

        else:
            pass

    def start_algorithm(self, queue: 'Queue') -> None:
        """
        Lance l'algorithme dans un thread séparé et retourne les résultats.
        """
        if not self._instance:
            raise ValueError("Aucun algorithme n'est défini.")


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