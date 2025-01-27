from PyQt5.QtCore import QObject, pyqtSignal

class SignalEmitter(QObject):
    # Tout object est de type primitif <object> 
    # cela permet d'accepter n'importe quel objet (type)
    clicked = pyqtSignal(object)
    aircrafts_moved = pyqtSignal()
    algorithm_terminated = pyqtSignal(object)
    algorithm_progress = pyqtSignal(float)
    algorithm_elapsed = pyqtSignal(float)
    algorithm_timeout_value = pyqtSignal(float)
    algorithm_error = pyqtSignal(object, object)