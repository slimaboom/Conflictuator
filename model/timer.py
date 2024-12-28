from threading import Lock, Thread, Event
from time import time, sleep

from logging_config import setup_logging
from typing import Callable

class Timer:
    def __init__(self):
        self.logger = setup_logging(__class__.__name__)

        self._interval = None
        self._running  = False
        self._callbacks = []
        self._thread = None
        self._stop_event = Event()  # Événement pour arrêter le thread
    
    def interval(self) -> int:
        """Retourne l'intervalle actuel en millisecondes."""
        return self._to_msec(self._interval)

    def _to_msec(self, sec: float) -> int:
        return int(self._interval * 1000)
 
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
        self.logger.info("Start running timer")
        while not self._stop_event.is_set():
            start_time = time()  # Garde le temps initial pour un interval précis
            for callback in self._callbacks:
                if self._stop_event.is_set(): return
                try:
                    start_callback = time()
                    callback()
                    duration = time() - start_callback
                    if duration > self.interval():  # Si un callback prend plus de 100 ms, avertir
                        self.logger.warning(f"Callback lent : {callback.__name__} a pris {duration:.2f}s.")
                except Exception as e:
                    self.logger.error(f"Erreur dans un callback : {e}")
            
            elapsed = time() - start_time
            sleep(max(0, self._interval - elapsed))  # Maintenir l'interval
        self.logger.info("Stop running timer")
        return

    
    def start(self, msec: int) -> None:
        """
        Démarre le timer si ce n'est pas déjà le cas.
        :param interval: Intervalle en millisecondes.
        """
        if not self._running:
            self._interval = msec/1000
            self._running = True
            self._stop_event.clear()  # Réinitialise l'événement (s'il a été déclenché)
            self._thread  = Thread(target=self._run)
            self._thread.start()

    def stop(self):
        """
        Arrêter le timer.
        """
        if self._running:
            self.logger.info(f"Le thread va être arrêté : {self._thread}")
            
                        # Signaler au thread qu'il doit s'arrêter
            self._stop_event.set()  # Déclenche l'événement pour signaler l'arrêt

            # Signaler au thread qu'il doit s'arrêter
            #self._running = False

            # Attendre que le thread termine proprement
            if self._thread:
                # Vérification finale
                self._thread.join(timeout=2)

                if self._thread.is_alive():
                    self.logger.warning("Le thread du timer n'a pas pu être arrêté correctement.")
                # Nettoyage
                self._thread = None
            self._running = False



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
