from threading import Lock, Thread
from time import time, sleep

from logging_config import setup_logging
from typing import Callable

class Timer:
    def __init__(self):
        self.logger = setup_logging(__class__.__name__)

        self._interval = None
        self._running  = False
        self._callbacks = []
        self._lock = Lock()
        self._thread = None
    
    def interval(self) -> int:
        """Retourne l'intervalle actuel en millisecondes."""
        return self._interval

    def connect(self, callback: Callable) -> None:
        """
        Ajouter une fonction à exécuter à chaque intervalle.
        :param callback: Fonction à exécuter (sans paramètres).
        """
        self._callbacks.append(callback)

    def _run(self) -> None:
        """
        Méthode interne pour exécuter les callbacks à interval régulier.
        """
        while self._running:
            start_time = time()  # Garde le temps initial pour un interval précis
            with self._lock:
                for callback in self._callbacks:
                    callback()  # Appeler chaque callback
            elapsed = time() - start_time
            sleep(max(0, self._interval - elapsed))  # Maintenir l'interval        
    
    def start(self, msec: int) -> None:
        """
        Démarre le timer si ce n'est pas déjà le cas.
        :param interval: Intervalle en millisecondes.
        """
        if not self._running:
            self._interval = msec
            self._running = True
            self._thread  = Thread(target=self._run, daemon=True)
            self._thread.start()

    def stop(self):
        """
        Arrêter le timer.
        """
        if self._running:
            self._running = False
            if self._thread:
                self._thread.join()
                self._thread = None

    def toggle(self):
        """
        Basculer entre démarrer/arrêter le timer.
        """
        if self._running:
            self.stop()
        else:
            self.start()

    def isActive(self) -> bool:
        """
        Vérifie si le timer est en cours d'exécution.
        :return: True si le timer est actif.
        """
        return self._running
