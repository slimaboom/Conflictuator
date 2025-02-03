import inspect
from algorithm.interface.ISimulatedObject import ISimulatedObject, ASimulatedAircraft
from algorithm.interface.IObjective import IObjective, AObjective
from model.aircraft.storage import DataStorage

from utils.conversion import sec_to_time, time_to_sec
from logging_config import setup_logging

from utils.controller.database_dynamique import MetaDynamiqueDatabase

from abc import ABC, abstractmethod
from typing import List, Type, Any
from typing_extensions import override
from copy import deepcopy
from datetime import time, datetime
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
        """Récupérer l'avancement de l'exécution, exprimée en % [0-100]"""        
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
   
    NUMBER_OF_LAYERS_KEY: str = "number_of_layers"

    @abstractmethod
    def __init__(self, data: List[ASimulatedAircraft], 
                 is_minimise: bool, 
                 verbose: bool = False, 
                 timeout: time = time(hour=0, minute=2, second=0),
                 number_of_layers: int = 0,
                 **kwargs):
        """
        Constructeur abstrait imposant 4 paramètres obligatoires.

        :param data: Liste de ASimulatedAircraft.
        :param is_minimise: Booléen indiquant si l'algorithme doit minimiser.
        :param verbose: Active ou non les logs (facultatif, par défaut False).
        :param timeout: Temps maximum d'exécution en secondes (facultatif, par défaut 120s).
        :param number_of_layers: Nombre de couches récursive que l'algorithme peut avoir
            Par exemple AlgorithmGenetic pourrait avoir 2 couches c'est à dire qu'il pourrait 
                lancer dans la premiere couche 1 algorithme différent de lui (ou pas)
                et dans la seconde couche un autre algorithme différent possiblement des deux
                Chacune des deux couches aurait donc son propre algorithme avec
                    ses hyper-paramètres
                    sa fonction objective
        :param kwargs: Hyperparamètres supplémentaires que les classes dérivées peuvent utiliser.
        """
        super().__init__(data, is_minimise, timeout)  # Passe les hyperparamètres aux éventuelles classes parentes

        self.__fobjective  = None
        self.__data        = data
        self.__is_minimise= is_minimise
        self.__recorded_datastorage = [deepcopy(d.get_data_storages()) for d in data]

        self.__pourcentage_process = 0.
        self.__process_time        = 0.
        self.__timeout_value       = time_to_sec(timeout.isoformat())
        self.__startime            = None
        self.__state               = AlgorithmState.NOT_STARTED
        self.__generator = np.random.default_rng(seed=sum(d.get_object().get_id_aircraft() for d in data))
        self.__verbose   = verbose
        self.__layers: List[AAlgorithm]    = []
        self.__number_of_layers = number_of_layers
        self.extra_params = kwargs  # Stocke les hyperparamètres supplémentaires
        self.__name = self.__class__.__name__       
        self.__best_critere = float('inf') if is_minimise else -float('inf')
        self.__simulation_duration : float= None
        self.logger = setup_logging(self.__class__.__name__)

    def get_param(self, param_name: str, default=None) -> Any:
        """Retourne un paramètre stocké ou la valeur par défaut"""
        return self.extra_params.get(param_name, default)
    
    def set_simulation_duration(self, simulation_duration:float) -> None:
        """Modifie l'attribut de temps totale de la simulation"""
        self.__simulation_duration = simulation_duration

    def get_simulation_duration(self) -> float:
        """ Renvoie la durée totale de simulation """
        return self.__simulation_duration

    def get_name(self) -> str:
        """Renvoie le nom de l'algorithme"""
        return self.__name
    
    def set_name(self, name: str) -> None:
        """Modifie le nom de l'algorithme stocké dans l'attribut"""
        self.__name = name
        self.logger.info(name)

    def get_best_critere(self) -> float:
        """Retourne le meilleur crietre obtenu"""
        return self.__best_critere

    def set_best_critere(self, critere: float) -> None:
        """Modifie la valeur du meilleure critere"""
        self.__best_critere = critere

    def display_layers(self) -> None:
        for i, layer in enumerate(self.__layers):
            self.logger.info(f"{self.get_name()}: layer {i+1} --> {layer.get_name()}")

    def get_data(self) -> List[ASimulatedAircraft]:
        """Renvoie la liste de ASimulatedAircraft stocker dans la classe"""
        return self.__data

    def set_data(self, data: List[ASimulatedAircraft]) -> None:
        """Modifie l'attribut data (List[ASimulatedAircraft]) en enoyant l'argument dans l'attribut"""
        self.__data = data

    def get_layers(self) -> List['AAlgorithm']:
        """Récupération de la liste des différentes couches de AAlgorithm"""
        return self.__layers
    
    def set_layers(self, layers: List['AAlgorithm']) -> None:
        """Mise à jour de la liste des différentes couches de AAlgorithm
        Exception: ValueError si la la taille en entrée est différente du nombre de layers demandés dans le constructeur (number_of_layers)
        """
        if len(layers) != self.__number_of_layers:
            error = f"layers arugment is not the same size as expected in the construction of the instance (number_of_layers)"
            error += f"\nExpected size {self.__number_of_layers}, got {len(layers)}"
            raise ValueError(error)
        
        self.__layers = layers

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
            #import traceback
            #tb = traceback.format_exc()
            #self.set_state(AlgorithmState.ERROR)
            #raise type(e)(f"{e}\nTraceback:\n{tb}") from e # Propager l'erreur avec le traceback
            raise e
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
        """Récupérer l'avancement de l'exécution, exprimée en % [0-100]"""        
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
            dt = datetime.now().timestamp() - self.__startime
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
        params        = MetaDynamiqueDatabase.get_class_constructor_params(cls, class_name)
        params_parent = inspect.signature(cls.__init__).parameters
        ignored_param_names = ['data', 'self', 'args', 'kwargs'] # self, kwargs, args, pour le parent


        # Création d'une copie mutable du dictionnaire
        new_params = dict(params)

        # Fusionner sans écraser les clés existantes
        # Privilégier les clés de la classe dérivée par rapport à la parente
        for key, value in params_parent.items():
            if key not in new_params and key not in ignored_param_names:
                new_params[key] = value

        # MappingProxyType[str, Parameter] est immutable donc on passe par un dictionnaire temporaire
        for ignored_param_name in ignored_param_names:
            if new_params.get(ignored_param_name):
                del new_params[ignored_param_name]
        return type(params)(new_params)