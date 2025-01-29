from model.simulation import SimulationModel
from view.signal import SignalEmitter
from logging_config import setup_logging
from algorithm.interface.IAlgorithm import AAlgorithm

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
        self.is_finished()

    @override
    def start_algorithm(self, aalgorithm: 'AAlgorithm', *args, **kwargs) -> 'Queue':
        """
        Démarre l'algorithme dans un thread séparé et connecte un signal pour notifier.
        """
        queue = Queue()
        super().set_algorithm(aalgorithm, *args, **kwargs)
        super().start_algorithm(queue)
    
        self._queue = queue
        interval = int(self.get_interval_timer() * 1000)
        interval = interval if interval else self.INTERVAL
        self.qtimer.start(int(interval)) # msec

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
            if self.get_algorithm_manager().is_algorithm_error():
                self.signal.algorithm_error.emit(self.get_algorithm_manager().get_algorithm_state(), 
                           self._queue.get_nowait())
            else:
                self.signal.algorithm_terminated.emit(self._queue)
                self.qtimer.stop()
        
        progression = self.get_progress_algorithm()
        elasped, timeout = self.get_process_time_algorithm()
        
        self.signal.algorithm_progress.emit(progression)
        self.signal.algorithm_elapsed.emit(elasped)
        self.signal.algorithm_timeout_value.emit(timeout)
    
    def disconnect(self) -> None:
        self.signal.disconnect()
    
    @override
    def is_finished(self) -> bool:
        """Emet un signal si la simulation est terminée"""
        is_finished = super().is_finished()
        if is_finished:
            self.signal.simulation_finished.emit(True)
        return is_finished