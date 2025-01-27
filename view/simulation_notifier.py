from model.simulation import SimulationModel
from view.signal import SignalEmitter
from logging_config import setup_logging
from algorithm.type import AlgoType
from algorithm.interface.IAlgorithm import AlgorithmState

from queue import Queue
from PyQt5.QtCore import QTimer

from typing_extensions import override

class SimulationModelNotifier(SimulationModel):
    signal = SignalEmitter()

    def __init__(self):
        super().__init__()
        self.logger = setup_logging(__class__.__name__)
        
        self.qtimer = QTimer()
        self.qtimer.timeout.connect(self._watch_queue)

    @override
    def run(self) -> None:
        """Permet d'executer la methode run de la classe parente
        et de notifier par un signal l'IHM"""
        super().run()
        self.signal.aircrafts_moved.emit()

    @override
    def start_algorithm(self, algotype: 'AlgoType') -> 'Queue':
        """
        Démarre l'algorithme dans un thread séparé et connecte un signal pour notifier.
        """
        queue = Queue()
        super().set_algorithm(algotype)
        super().start_algorithm(queue)
    
        self._queue = queue
        interval = 100 if AlgoType.GENETIQUE else 1000
        self.qtimer.start(interval) # msec

    @override
    def stop_algorithm(self) -> None:
        super().stop_algorithm()
        if self.qtimer and self.qtimer.isActive():
            self.qtimer.stop()

    def _watch_queue(self) -> None:
        #self.logger.info("Watch queue launch")
        if self._queue.qsize() != 0:
            # Emission du signal pour signifier que l'algorithme a terminé
            # Le file d'attente est envoyee dans le signal
            self.signal.algorithm_terminated.emit(self._queue)
            self.qtimer.stop()
        
        progression = self.get_progress_algorithm()
        elasped, timeout = self.get_process_time_algorithm()
        
        self.signal.algorithm_progress.emit(progression)
        self.signal.algorithm_elapsed.emit(elasped)
        self.signal.algorithm_timeout_value.emit(timeout)
    
    def disconnect(self) -> None:
        self.signal.disconnect()