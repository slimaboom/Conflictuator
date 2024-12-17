from PyQt5.QtCore import QObject, pyqtSignal

class SignalEmitter(QObject):
    # Tout object est de type primitif <object> 
    # cela permet d'accepter n'importe quel objet (type)
    clicked = pyqtSignal(object)
    aircrafts_moved = pyqtSignal()