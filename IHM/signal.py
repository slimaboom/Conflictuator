from PyQt5.QtCore import QObject, pyqtSignal

class SignalEmitter(QObject):
    clicked = pyqtSignal(object)