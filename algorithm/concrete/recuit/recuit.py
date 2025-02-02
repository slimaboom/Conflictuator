from algorithm.interface.ISimulatedObject import ASimulatedAircraft
from algorithm.interface.IAlgorithm import AAlgorithm
from algorithm.concrete.recuit.etat import Etat
from model.aircraft.storage import DataStorage

from utils.controller.argument import method_control_type

from logging_config import setup_logging

from typing import List
from typing_extensions import override

import numpy as np
from datetime import time, datetime

@AAlgorithm.register_algorithm
class AlgorithmRecuit(AAlgorithm):
    @method_control_type(List[ASimulatedAircraft])
    def __init__(self, data: List[ASimulatedAircraft], is_minimise: bool = False, 
                 verbose           : bool = False,
                 timeout           : time = time(hour=0, minute=2, second=0),
                 number_transitions: int = 2000,
                 heat_up_rate      : float = 1.5,
                 heat_up_acceptance: float = 0.8,
                 cooling_rate      : float = 0.995,
                 **kwargs):
    
        # Attributs generaux
        super().__init__(data=data, is_minimise=is_minimise, verbose=verbose, timeout=timeout, **kwargs)
        self.__generator   = self.get_generator()

        self.logger = setup_logging(self.__class__.__name__)

        # Parametres de l'algorithme Recuit Simule
        self.__nb_transitions = number_transitions
        self.__heat_up_rate   = heat_up_rate
        self.__heat_up_accept = heat_up_acceptance
        self.__cooling_rate   = cooling_rate

        # Timeout
        self.set_timeout_value(self.get_timeout_value())

    def __accept(self, yi: float, yj: float, temperature: float) -> bool:
        """Principle of Acceptation in Maximisation or Minimisation"""
        delta = yj - yi
        accept_pourentage = 1. if delta == 0 else 1 # si delta vaut 0 on accepte a 70%
        if self.is_minimisation(): # Minimisation
            if yj < yi: return True
            else:
                probability = self.__generator.random()
                boltzmann   = np.exp(-delta/temperature) # detla > 0
                return probability < boltzmann * accept_pourentage
        else: # Maximisation
            if yj > yi: return True
            else:
                probability = self.__generator.random()
                boltzmann   = np.exp(delta/temperature) # delta < 0
                #self.logger.info(f"yi={yi}, yj={yj} --> delta={delta}, prob:{probability}, boltzmann:{boltzmann} -> {probability < boltzmann}")
                return probability < boltzmann * accept_pourentage

    def __heat_up_loop(self) -> float:
        """Determine the initial temperature"""
        start_time = datetime.now().timestamp()

        self.set_start_time(start=start_time)

        accept_counter = 0
        temperature    = 0.01
        accept_rate    = 0.0

        # Etat
        xi = Etat(self.get_data())
        xj = Etat(self.get_data())

        while accept_rate < self.__heat_up_accept and self.is_running(): # 80% of transifition must be accepted
            accept_counter    = 0
            for k in range(self.__nb_transitions):
                self.set_process_time(process_time=datetime.now().timestamp() - self.get_start_time())

                # Generation of state point
                xi.initialize_random()
                yi = xi.calcul_critere(self.get_objective_function().evaluate)

                # Generation of neighborhood of xi
                xj.copy(xi)
                xj.generate_neighborhood()
                yj = xj.calcul_critere(self.get_objective_function().evaluate)

                # Is neighborhood accepted ?
                #self.logger.info(f"At T={temperature}, yi={yi}, yj={yj}")
                if self.__accept(yi, yj, temperature):
                    accept_counter += 1
                    # Maj du critiere
                    self.set_best_critere(yj)
                #    self.logger.info(f"At T={temperature}, yi={yi}, yj={yj} ({accept_counter}/{self._nb_transitions})")

            # Count rate of accepted transitions
            accept_rate = accept_counter/self.__nb_transitions
            temperature *= self.__heat_up_rate # Increase temperature

            msg = f"Accept rate: {accept_rate} ({accept_counter}/{self.__nb_transitions}) at temperature={temperature}"
            self.logger.info(msg)
        return temperature

    def __cooling_loop(self, initial_temperature: float) -> Etat:
        """Coolling loop of temperature"""
        self.set_start_time(start=datetime.now().timestamp())
        self.logger.info(f"Start colling at temperature: {initial_temperature}")

        xi = Etat(self.get_data())
        xi.initialize_random()
        yi = xi.calcul_critere(self.get_objective_function().evaluate)
        xi.critere = yi

        xj = Etat(self.get_data())
        best_state = Etat(self.get_data())

        temperatures = self.__get_all_temperatures(initial_temperature)
        for i, temperature in enumerate(temperatures):
            pourcentage = round(100*(i+1)/len(temperatures), 1)
            self.set_process(pourcentage=pourcentage)

            if not self.is_running() or self.is_timeout():
                break
            
            else:
                for k in range(self.__nb_transitions):
                    self.set_process_time(process_time=datetime.now().timestamp()-self.get_start_time())

                    xj.copy(xi)
                    xj.generate_neighborhood()
                    yj = xj.calcul_critere(self.get_objective_function().evaluate)

                    if self.__accept(yi, yj, temperature):
                        best_state.save_state(xj)

                        xj = xi
                        yi = yj
                        # Maj du critiere
                        self.set_best_critere(yj)

                        if self.is_verbose():
                            msg = f"Iteration {k}/{self.__nb_transitions} - Temperature: {temperature} - critere: {yi}"
                            self.logger.info(msg)
                            self.logger.info(f"Etat: {best_state.display()}")


        self.logger.info(f"End of colling - Before restoring: Best {best_state}")
        best_state.restore_state(best_state)                    # Maj du critiere
        self.set_best_critere(best_state.get_critere())

        self.logger.info(f"End of colling - After restoring: Best {best_state}")
        self.stop()
        return best_state

    @override
    def run(self) -> List[List[DataStorage]]:
        # Initial Temperature
        initial_temperature = self.__heat_up_loop()
        # Cooling Temperature
        best = self.__cooling_loop(initial_temperature)
        
        self.logger.info(f"Before setting initial value {best}")
        self.reinitialize_data()
        self.logger.info(f"After setting initial value {best}")
        self.stop()
        return best.get_vector()
    

    def __get_all_temperatures(self, initial: float) -> List[float]:
        # Tf=self._cooling_rate**n * T0 = 0.1*T0
        n = int(np.ceil(np.log(0.1)/np.log(self.__cooling_rate)))
        temperatures = [initial*self.__cooling_rate**i for i in range(n)]
        return temperatures