from algorithm.interface.ISimulatedObject import ISimulatedObject, ASimulatedAircraft
from algorithm.interface.IObjective import IObjective, AObjective
from model.aircraft.storage import DataStorage

from utils.conversion import sec_to_time
from logging_config import setup_logging

from utils.controller.database_dynamique import MetaDynamiqueDatabase

from abc import ABC, abstractmethod
from typing import List, Type
from typing_extensions import override
from copy import deepcopy
from time import time
from enum import Enum

import numpy as np

class AlgorithmState(Enum):
    STARTED  = "STARTED"
    STOPPED  = "STOPPED"
    FINISHED = "FINISHED"
    TIMEOUT  = "TIMEOUT"
    ERROR    = "ERROR"
    NOT_STARTED = "NOT_STARTED"
    ALREADY_LAUNCH = "ALREADY_LAUNCH"
    

class IAlgorithm(ABC):
    """Interface pour un algorithme prenant une liste de ISimulatedObject"""

    @abstractmethod
    def __init__(self, data: List[ISimulatedObject], is_minimise: bool, timeout: float):
        """Constructeur abstrait obligeant à passer un paramètre de type List[ISimulatedObject] et un booleen pour minimisation ou non"""
        pass

    @abstractmethod
    def start(self) -> List[List[DataStorage]]:
        """Demarrer l'algorithme pour chercher une solution optimale"""
        pass

    @abstractmethod
    def stop(self) -> None:
        """Stopper l'algorithme. Ne renvoie pas de solution"""
        pass

    @abstractmethod
    def run(self) -> List[List[DataStorage]]:
        """Logique d'implementation de l'algorithme qui renvoie la solution optimale"""

    @abstractmethod
    def is_running(self) -> bool:
        """Vérifier si l'algorithme est en cours d'exécution."""
        pass

    @abstractmethod
    def get_progress(self) -> float:
        """Récupérer l'avancement de l'exécution, exprimée en %"""        
        pass

    @abstractmethod
    def get_process_time(self) -> float:
        """Récupérer le temps de calcul de l'execution, exprimée en secondes"""
        pass

    @abstractmethod
    def set_objective_function(self, function: IObjective) -> None:
        """Injection de dependance du calcul de la fonction objectif """
        pass
    
    @abstractmethod
    def get_objective_function(self) -> IObjective:
        """Renvoie la fonction objective utilisee"""
        pass

class AAlgorithm(IAlgorithm):
    """Classe abstraite pour un algorithme prenant une liste de ASimulatedAircraft"""
   
    @abstractmethod
    def __init__(self, data: List[ASimulatedAircraft], is_minimise: bool, verbose: bool = False, timeout: float = 120.):
        """Constructeur abstrait obligeant à passer:
            @param: data
                Liste de ASimulatedAircraft
            @param: is_minimise
                booléen pour minimisation ou non lorsque l'algorithme cherche une solution
            @param: verbose
                booléen pour afficher des logs ou non
        """
        self.__fobjective  = None
        self.__data        = data
        self.__is_minimise= is_minimise
        self.__recorded_datastorage = [deepcopy(d.get_data_storages()) for d in data]

        self.__pourcentage_process = 0.
        self.__process_time        = 0.
        self.__timeout_value       = timeout
        self.__startime            = None
        self.__state               = AlgorithmState.NOT_STARTED
        self.__generator = np.random.default_rng(seed=sum(d.get_object().get_id_aircraft() for d in data))
        self.__verbose   = verbose

        self.logger = setup_logging(self.__class__.__name__)

    def get_data(self) -> List[ASimulatedAircraft]:
        """Renvoie la liste de ASimulatedAircraft stocker dans la classe"""
        return self.__data

    @override
    def start(self) -> List[List[DataStorage]]:
        """
        Démarrer l'algorithme pour chercher une solution optimale.
        """
        self.set_state(AlgorithmState.STARTED)
        try:
            result = self.run()
            self.set_state(AlgorithmState.FINISHED)
            return result
        except Exception as e:
            self.set_state(AlgorithmState.ERROR)
            return e # Propager l'erreur avec le traceback

    @override
    def stop(self) -> None:
        """Stopper l'algorithme. Ne renvoie pas de solution"""
        if self.is_running():
            self.set_state(AlgorithmState.FINISHED)

    @override
    def is_running(self) -> bool:
        """Vérifier si l'algorithme est en cours d'exécution."""
        return self.get_state() == AlgorithmState.STARTED

    def is_minimisation(self) -> bool:
        """Retourne si l'objectif de l'algorithme est la minimisation du critere"""
        return self.__is_minimise
    
    @override
    def get_progress(self) -> float:
        """Récupérer l'avancement de l'exécution, exprimée en %"""        
        return self.__pourcentage_process

    def set_process(self, pourcentage: float) -> None:
        """Met à jour l'avancement de l'exécution, exprimée en %"""
        self.__pourcentage_process = pourcentage    

    @override
    def get_process_time(self) -> float:
        """Récupérer le temps de calcul de l'execution, exprimée en secondes"""
        return self.__process_time

    def set_process_time(self, process_time: float) -> float:
        """Met à jour le temps de calcul de l'execution, exprimée en secondes"""
        self.__process_time = process_time
    
    @override
    def set_objective_function(self, function: AObjective) -> None:
        """Injection de dependance du calcul de la fonction objectif de type AObjective """
        self.__fobjective = function
    
    @override
    def get_objective_function(self) -> AObjective:
        """Renvoie la fonction objective utilisee"""
        return self.__fobjective

    def evaluate(self, data: List[ASimulatedAircraft] = None) -> float:
        """Evaluation de l'algorithme avec la fonction objective"""
        if self.__fobjective == None:
            msg = f"Objective function not set in the algorithm, please use an instance of {AObjective} object\n"
            msg += f"and set the function by using {self.__class__.__name__}.set_objective_function(obj_func) to set objective function."
            raise ValueError(msg)
        return self.__fobjective.evaluate(data=self.__data if data == None else data)

    def get_timeout_value(self) -> float:
        """Renvoie la duree pour declencher le timeout"""
        return self.__timeout_value
    
    def set_timeout_value(self, timeout: float) -> None:
        """Met a jour la duree du timeout"""
        self.__timeout_value = timeout
    
    def get_start_time(self) -> float:
        """Renvoie le temps de demarrage de l'algorithme"""
        return self.__startime

    def set_start_time(self, start: float) -> None:
        """Met a jour le temps de demarrage de l'algorithme"""
        self.__startime = start

    def is_timeout(self) -> bool:
        """L'algorithme est-il en timeout (trop longue duree d'execution)"""
        if self.__startime != None:
            dt = time() - self.__startime
        else:
            dt = 0.

        _is_timeout = dt >= self.get_timeout_value()
        if _is_timeout:
            msgtimeout = f"Timeout: {sec_to_time(self.get_timeout_value())}, running for {sec_to_time(dt)}"
            self.logger.info(msgtimeout)
            self.set_state(AlgorithmState.TIMEOUT)
        return _is_timeout
    
    def get_generator(self) -> np.random.Generator:
        """Recupere le generator de nombre aleatoire de l'algorithme"""
        return self.__generator

    def reinitialize_data(self) -> None:
        """Re-initialise la liste de ASimulatedAircraft avec les valeurs initiales avant démarrage de l'algorithme"""
        init_datastorages = self.__recorded_datastorage
        for asimulatedobject, init_datastorage in zip(self.__data, init_datastorages):
            if self.is_verbose():
                self.logger.info(f"{asimulatedobject} --> init_ds: {init_datastorage}")
            asimulatedobject.update_commands(init_datastorage)
        
        # Apres avoir reinitialiser les commandes sur chaque object enrobé,
        # il faut recalculer correctement tous les conflits car certains restent lier avec les vitesses
        # de la solution optimale.
        # Donc quand tout le monde a ete reinitialise, ca recalcul avec les bon conflits.
        for asimulatedobject in self.__data:
            asimulatedobject.update_conflicts()
    
    def is_verbose(self) -> bool:
        """Renvoie vrai si la verbosite est mise en place"""
        return self.__verbose

    def set_state(self, state: AlgorithmState) -> None:
        """Mise à jour de l'état de l'algorithme."""
        self.__state = state
    
    def get_state(self) -> AlgorithmState:
        """Récupère l'état actuel de l'algorithme."""
        return self.__state

    @classmethod
    def register_algorithm(cls, algo_class: Type):
        """
        Enregistre un algorithme à partir de la classe.
        Exception: TypeError
        """
        return MetaDynamiqueDatabase.register(algo_class)

    @classmethod
    def get_available_algorithms(cls):
        """
        Retourne la liste des noms des algorithms disponibles.
        Exception: TypeError
        """
        return MetaDynamiqueDatabase.get_available(base_class=cls)

    @classmethod
    def discover_algorithms(cls, package: str):
        """
        Découvre et importe tous les modules dans un package donné ('algorithm.concrete')
        
        :param package: Le chemin du package où chercher les algorithms (ex. 'algorithm.concrete').
        """
        return MetaDynamiqueDatabase.discover_dynamic(package=package)
    
    @classmethod
    def get_algorithm_class(cls, name: str) -> 'AAlgorithm':
        """
        Renvoie une classe AAlgorithm à partir de son nom enregistré.
        L'instance n'est pas crée.
        Exception: TypeError ou ValueError
        """
        try:
            return MetaDynamiqueDatabase.get_class(base_class=cls, name=name)
        except Exception as e:
            error = f"Algorithm '{name}' non supporté car non enregistré dans la classe {cls.__name__}"
            error += f"\nUtiliser @{cls.__name__}.register_algorithm en décoration de la classe dérivée pour enregistrer l'algorithm."
            full_message = f"{str(e)}\n{error}"
            raise type(e)(full_message)
    
    @classmethod
    def create_algorithm(cls, name: str, *args, **kwargs) -> 'AAlgorithm':
        """
        Instancie une classe algorithm à partir de son nom enregistré.
        Exception: TypeError ou ValueError
        """
        return cls.get_algorithm_class(name)(*args, **kwargs)


    @classmethod
    def get_class_constructor_params(cls, class_name: str):
        """
        Retourne les paramètres du constructeur de l'algorithme spécifiée.
        Exception: TypeError
        """
        params = MetaDynamiqueDatabase.get_class_constructor_params(cls, class_name)
        ignored_param_names = ['data']
        # MappingProxyType[str, Parameter] est immutable donc on passe par un dictionnaire temporaire
        new_params = dict(params)
        for ignored_param_name in ignored_param_names:
            if new_params.get(ignored_param_name):
                del new_params[ignored_param_name]
        return type(params)(new_params)