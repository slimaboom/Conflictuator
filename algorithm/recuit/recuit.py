from algorithm.recuit.etat import Etat
from algorithm.recuit.data import ISimulatedObject
from logging_config import setup_logging

import numpy as np

from typing import List

class Recuit:
    def __init__(self, data: List[ISimulatedObject], is_minimise: bool = True):
        self.data = data
        self.is_minimise = is_minimise
        self.generator   = np.random.default_rng(seed=len(data))

        self.logger = setup_logging(self.__class__.__name__)

        # Parametre du Recuit
        self._nb_transitions: int = 2000
        self._cooling_rate: float = 0.995
        self._heat_up_rate: float = 1.5
        self._heat_up_accept: float = 0.8

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

        while accept_rate < self._heat_up_accept: # 80% of transifition must be accepted
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
        self.logger.info(f"Start colling at temperature: {initial_temperature}")

        temperature = initial_temperature
        xi = Etat(self.data)
        xi.initialize_random()
        yi = xi.calcul_critere()

        xj = Etat(self.data)
        best_state = Etat(self.data)
        while temperature > 0.1 * initial_temperature:
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

                    msg = f"Iteration {k}/{self._nb_transitions} - Temperature: {temperature} - critere: {yi}"
                    self.logger.info(msg)
                    self.logger.info(f"Etat: {best_state.display()}")            

            temperature *= self._cooling_rate

        self.logger.info(f"End of colling - Before restoring: Best {best_state}")
        best_state.restore_state(best_state)
        self.logger.info(f"End of colling - After restoring: Best {best_state}")
        return best_state
    
    def run(self) -> Etat:
        # Heat up
        initial_temperature = self.heat_up_loop()
        return self.cooling_loop(initial_temperature) # Cooling

