from algorithm.recuit.etat import Etat
from algorithm.recuit.data import ISimulatedObject
from logging_config import setup_logging
from model.utils import sec_to_time

from copy import deepcopy
import time
import numpy as np

from typing import List

class Recuit:
    def __init__(self, data: List[ISimulatedObject], is_minimise: bool = True, verbose: bool = False):
        self.data = data
        self.is_minimise = is_minimise
        self.generator   = np.random.default_rng(seed=len(data))
        self.verbose = verbose

        self.logger = setup_logging(self.__class__.__name__)

        # Parametre du Recuit
        self._nb_transitions: int = 2000
        self._cooling_rate: float = 0.995
        self._heat_up_rate: float = 1.5
        self._heat_up_accept: float = 0.8

        # Sauvegarde des datas
        self._data_saved = [deepcopy(d) for d in data]
        self._isrunning = False

        # Timeout
        self._timeout = 120
        self._starttime = None

        # Progression
        self._progress = 0.

    def get_initial_data(self) -> List[ISimulatedObject]:
        return self._data_saved

    def _accept(self, yi: float, yj: float, temperature: float) -> bool:
        """Principle of Acceptation in Maximisation or Minimisation"""
        delta = yj - yi
        if self.is_minimise: # Minimisation
            if yj < yi: return True
            else:
                probability = self.generator.random()
                boltzmann   = np.exp(-delta/temperature) # detla > 0
                return probability < boltzmann
        else: # Maximisation
            if yj > yi: return True
            else:
                probability = self.generator.random()
                boltzmann   = np.exp(delta/temperature) # delta < 0
                return probability < boltzmann

    def heat_up_loop(self) -> float:
        """Determine the initial temperature"""
        accept_counter = 0
        temperature    = 0.01
        accept_rate    = 0.0

        # Etat
        xi = Etat(self.data)
        xj = Etat(self.data)

        while accept_rate < self._heat_up_accept and self.is_running(): # 80% of transifition must be accepted
            accept_counter    = 0
            for k in range(self._nb_transitions):

                # Generation of state point
                xi.initialize_random()
                yi = xi.calcul_critere()

                # Generation of neighborhood of xi
                xj.copy(xi)
                xj.generate_neighborhood()
                yj = xj.calcul_critere()

                # Is neighborhood accepted ?
                if self._accept(yi, yj, temperature):
                    accept_counter += 1
            # Count rate of accepted transitions
            accept_rate = accept_counter/self._nb_transitions
            temperature *= self._heat_up_rate # Increase temperature

            msg = f"Accept rate: {accept_rate} ({accept_counter}/{self._nb_transitions}) at temperature={temperature}"
            self.logger.info(msg)
        return temperature

    def cooling_loop(self, initial_temperature: float) -> Etat:
        """Coolling loop of temperature"""
        self._starttime = time.time()
        self.logger.info(f"Start colling at temperature: {initial_temperature}")

        xi = Etat(self.data)
        xi.initialize_random()
        yi = xi.calcul_critere()

        xj = Etat(self.data)
        best_state = Etat(self.data)

        temperatures = self._get_all_temperatures(initial_temperature)
        for i, temperature in enumerate(temperatures):
            self._progress = round(100*(i+1)/len(temperatures), 4)

            if not self.is_running() or self.is_timeout():
                break
            
            else:
                for k in range(self._nb_transitions):
                    xj.copy(xi)
                    xj.generate_neighborhood()
                    yj = xj.calcul_critere()

                    if self._accept(yi, yj, temperature):
                        _buffer = xi
                        xi.copy(xj)
                        best_state.save_state(xi)

                        xj = _buffer
                        yi = yj

                        if self.verbose:
                            msg = f"Iteration {k}/{self._nb_transitions} - Temperature: {temperature} - critere: {yi}"
                            self.logger.info(msg)
                            self.logger.info(f"Etat: {best_state.display()}")


        self.logger.info(f"End of colling - Before restoring: Best {best_state}")
        best_state.restore_state(best_state)
        self.logger.info(f"End of colling - After restoring: Best {best_state}")
        self._isrunning = False
        return best_state
    
    def _reinitialize_data(self) -> None:
        for isimulatedobject, initial_isimulatedobject in zip(self.data, self.get_initial_data()):
            isimulatedobject.update(initial_isimulatedobject.get_data_storage().speed)

    def _run(self) -> Etat:
        self._isrunning = True
        # Heat up
        initial_temperature = self.heat_up_loop()
        best = self.cooling_loop(initial_temperature) # Cooling
        
        self.logger.info(f"Before setting initial value {best}")
        self._reinitialize_data()
        self.logger.info(f"After setting initial value {best}")
        self._isrunning = False
        return best

    def start(self) -> Etat:
        return self._run()
    
    def stop(self) -> None:
        if self.is_running():
            self._isrunning = False
            self._reinitialize_data()
    
    def is_running(self) -> bool: return self._isrunning

    def get_timeout(self) -> float: return self._timeout
    def set_timeout(self, timeout: float) -> None: 
        self._timeout = timeout
    
    def is_timeout(self) -> bool:
        _is_timeout = self._starttime == None or (time.time() - self._starttime) >= self._timeout
        if _is_timeout:
            msgtimeout = f"Timeout: {sec_to_time(self.get_timeout())}, running for {sec_to_time(time.time() - self._starttime)}"
            self.logger.info(msgtimeout)
        return _is_timeout

    def _get_all_temperatures(self, initial: float) -> List[float]:
        # Tf=self._cooling_rate**n * T0 = 0.1*T0
        n = int(np.ceil(np.log(0.1)/np.log(self._cooling_rate)))
        temperatures = [initial*self._cooling_rate**i for i in range(n)]
        return temperatures

    def get_progress(self) -> float:
        return self._progress