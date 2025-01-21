from threading import Thread
from queue import Queue
from typing import Any, List
from algorithm.algo_gen.genetique import GeneticAlgorithm

from algorithm.type import AlgoType
from algorithm.recuit.recuit import Recuit
from algorithm.recuit.data import SimulatedAircraftImplemented

from logging_config import setup_logging

class AlgorithmManager:
    def __init__(self):
        self._algorithm = None  # Algorithme courant
        self._data = None
        self._thread = None
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
            self.instance = Recuit(data_to_recuit, is_minimise=False) 

        elif self._algorithm == AlgoType.GENETIQUE:
            # Transformer les avions en objets pour l'algorithme génétique
            data_to_genetic = [SimulatedAircraftImplemented(aircraft) for aircraft in self._data]
            self.instance = GeneticAlgorithm(data_to_genetic, population_size=50, generations=30)

        else:
            pass

    def start_algorithm(self, queue: 'Queue') -> None:
        """
        Lance l'algorithme dans un thread séparé et retourne les résultats.
        """
        if not self.instance:
            raise ValueError("Aucun algorithme n'est défini.")


        # Créer et démarrer un thread pour exécuter l'algorithme
        self._thread = Thread(target=self._run_algorithm_in_thread, args=(queue,), )
        self._thread.start()

    def _run_algorithm_in_thread(self, result_queue: Queue) -> None:
        """
        Méthode interne qui exécute l'algorithme dans un thread séparé.
        Elle place les résultats dans la Queue.
        """
        try:
            # Exécuter l'algorithme (par exemple recuit simulé)
            result = self.instance.start().get()
            #result = [DataStorage(speed=0.002, id=1), DataStorage(speed=0.003, id=2), DataStorage(speed=0.003, id=3), DataStorage(speed=0.003, id=4)]
            result_queue.put(result)  # Mettre le résultat dans la Queue
        except Exception as e:
            # En cas d'erreur, on met l'exception dans la Queue
            result_queue.put(e)
    
    def stop_algorithm(self) -> None:
        if self._thread and self._thread.is_alive():
            self.instance.stop()
            self.logger.info(f"Stopping {self.instance}")
    
    def progress(self) -> float:
        return self.instance.get_progress()
