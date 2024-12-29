from threading import Thread
from queue import Queue
from typing import Any, List

from algorithm.type import AlgoType
from algorithm.recuit.recuit import Recuit
from algorithm.recuit.data import SimulatedAircraftImplemented, DataStorage

class AlgorithmManager:
    def __init__(self):
        self._algorithm = None  # Algorithme courant
        self._data = None

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
            pass

        else:
            pass

    def start_algorithm(self, queue: 'Queue') -> None:
        """
        Lance l'algorithme dans un thread séparé et retourne les résultats.
        """
        if not self.instance:
            raise ValueError("Aucun algorithme n'est défini.")


        # Créer et démarrer un thread pour exécuter l'algorithme
        thread = Thread(target=self._run_algorithm_in_thread, args=(queue,))
        thread.start()

    def _run_algorithm_in_thread(self, result_queue: Queue) -> None:
        """
        Méthode interne qui exécute l'algorithme dans un thread séparé.
        Elle place les résultats dans la Queue.
        """
        try:
            # Exécuter l'algorithme (par exemple recuit simulé)
            #result = self.instance.run().get()
            result = [DataStorage(speed=0.002, id=1), DataStorage(speed=0.003, id=2), DataStorage(speed=0.003, id=3), DataStorage(speed=0.003, id=4)]
            result_queue.put(result)  # Mettre le résultat dans la Queue
        except Exception as e:
            # En cas d'erreur, on met l'exception dans la Queue
            result_queue.put(e)