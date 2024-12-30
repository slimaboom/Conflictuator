from model.simulation import SimulationModel
from view.signal import SignalEmitter
from logging_config import setup_logging
from algorithm.type import AlgoType
from algorithm.recuit.data import DataStorage

from queue import Queue, Empty
from PyQt5.QtCore import QTimer

from typing import List


class SimulationModelNotifier(SimulationModel):
    signal = SignalEmitter()

    def __init__(self):
        super().__init__()
        self.logger = setup_logging(__class__.__name__)
        
        self.qtimer = QTimer()
        self.qtimer.timeout.connect(self._watch_queue)

    def run(self) -> None:
        """Permet d'executer la methode run de la classe parente
        et de notifier par un signal l'IHM"""
        super().run()
        self.signal.aircrafts_moved.emit()

    def start_algorithm(self, algotype: 'AlgoType') -> 'Queue':
        """
        Démarre l'algorithme dans un thread séparé et connecte un signal pour notifier.
        """
        queue = Queue()
        super().set_algorithm(algotype)
        super().start_algorithm(queue)
    
        self._queue = queue
        self.qtimer.start(1000) # msec

    def stop_algorithm(self) -> None:
        super().stop_algorithm()
        self.qtimer.stop()

    def _watch_queue(self) -> None:
        self.logger.info("Watch queue launch")
        if self._queue.qsize() != 0:
            # Emission du signal pour signifier que l'algorithme a terminé
            # Le file d'attente est envoyee dans le signal
            self.logger.info("Watch queue launch")
            self.signal.algorithm_terminated.emit(self._queue)
            self.qtimer.stop()