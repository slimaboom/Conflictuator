from PyQt5.QtCore import QObject, pyqtSignal

class SignalEmitter(QObject):
    # Tout object est de type primitif <object> 
    # cela permet d'accepter n'importe quel objet (type)
    clicked = pyqtSignal(object)
    aircrafts_moved = pyqtSignal()
    simulation_finished = pyqtSignal(bool)
    simulation_conflicts = pyqtSignal(float)
    algorithm_terminated = pyqtSignal(object)
    algorithm_error = pyqtSignal(object, Exception)
    algorithm_progress = pyqtSignal(float)
    algorithm_elapsed = pyqtSignal(float)
    algorithm_timeout_value = pyqtSignal(float)
    algorithm_critere = pyqtSignal(float)