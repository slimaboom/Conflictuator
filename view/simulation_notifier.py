from model.simulation import SimulationModel
from view.signal import SignalEmitter

from logging_config import setup_logging


class SimulationModelNotifier(SimulationModel):
    signal = SignalEmitter()

    def __init__(self):
        super().__init__()
        self.logger = setup_logging(__class__.__name__)
    
    def run(self) -> None:
        """Permet d'executer la methode run de la classe parente
        et de notifier par un signal l'IHM"""
        super().run()
        self.signal.aircrafts_moved.emit()