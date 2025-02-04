from typing import Dict, Type
from types import MappingProxyType
from utils.controller.dynamic_discover_packages import dynamic_discovering

import inspect


class MetaDynamiqueDatabase:
    """Métaclasse pour centraliser l'enregistrement des classes dérivées par rapport à leur classe parente abstraite
        Utiliser pour enregistrer les classes de types:
            - AAlgorithm
            - AObjective
            - AWritter
            - AFormat
            - AReader
            - ATrafficGenerator

        Cette méta classe permet d'enregistrer une dictionnaire donc la clé est le type abstrait de la sous classe,
        par exemple AlgorithmRecuit est de type AAlgorithm donc dans le dictionnaire il y aura
        {'AAlgorithm':
            {'AlgorithmRecuit': AlgorithmRecuit (Objet) subclass non instancé}
        }

        Si il y a des fonctions objectifs on aura alors une clé 'AObjective' si la classe dérivée est bien dérivée de AObjective
        avec par exemple MyFunctionObject(AObjective) alors on aura  
        
        {'AAlgorithm':
            {'AlgorithmRecuit': AlgorithmRecuit (Objet) subclass non instancé},

        'AObjective':
            {'MyFunctionObject': MyFunctionObject (Objet) subclass non instancé}
        }

        De même pour les AWritter et AFormat et autre si évolution...
    Développé au 29/01/2025 16:20:00 par F.NOUALHAGUET
    """
    
    __DYNAMIC_DATABASE: Dict[str, Dict[str, Type]] = {}

    @classmethod
    def register(cls, subclass: Type, base_class_name: str = None):
        """Enregistre une classe dérivée dans le bon dictionnaire.
        Exception: TypeError
        """
        if not isinstance(subclass, Type):  # Vérifie si subclass est bien une classe
            raise TypeError(f"Expected a class (Type), got {type(subclass)} instead.")

        if base_class_name == None:
            base_class_name = subclass.__bases__[0].__name__  # Ex: "AAlgorithm" si heritage directe
        else:
            # Ex: "AAlgorithm" si pas heritage directe et qu'on force la classe de base
            # comme dans IAlgorithm.py dans AAlgorithm.register_algorithm on force l'appelle a MetaDynamiqueDatabase.register avec la bonne cle
            base_class_name = base_class_name.__name__ 

        if base_class_name not in cls.__DYNAMIC_DATABASE:
            cls.__DYNAMIC_DATABASE[base_class_name] = {}

        cls.__DYNAMIC_DATABASE[base_class_name][subclass.__name__] = subclass

        return subclass  # Permet d'utiliser comme décorateur

    @classmethod
    def get_available(cls, base_class: Type) -> list:
        """Retourne toutes les classes dérivées enregistrées d'une classe de base donnée.
        Exception: TypeError
        """
        if not isinstance(base_class, Type):  # Vérifie si subclass est bien une classe
            raise TypeError(f"Expected a class (Type), got {type(base_class)} instead.")
        
        base_class_name = base_class.__name__
        return list(cls.__DYNAMIC_DATABASE.get(base_class_name, {}).keys())

    @classmethod
    def get_class(cls, base_class: Type, name: str) -> Type:
        """Retourne la classe dérivée enregistrée sous un nom donné. Non instanciee
        Exception: TypeError ou ValueError
        """
        if not isinstance(base_class, Type):  # Vérifie si subclass est bien une classe
            raise TypeError(f"Expected a class (Type), got {type(base_class)} instead.")
        
        base_class_name = base_class.__name__
        if name not in cls.__DYNAMIC_DATABASE.get(base_class_name, {}):
            raise ValueError(f"Class '{name}' not registered in {base_class_name}")
        return cls.__DYNAMIC_DATABASE[base_class_name][name]

    @classmethod
    def create_instance(cls, base_class: Type, name: str, *args, **kwargs):
        """Instancie une classe dérivée en fonction de son nom enregistré.
        
        Exception: TypeError ou ValueError
        """
        return cls.get_class(base_class, name)(*args, **kwargs)

    @classmethod
    def get_class_constructor_params(cls, base_class: Type, class_name: str) -> MappingProxyType[str, inspect.Parameter]:
        """Retourne les paramètres du constructeur d'une classe spécifique.
        Exception: TypeError
        """
        class_object = cls.get_class(base_class, class_name)
        signature = inspect.signature(class_object)
        
        params = {}
        params_without_annotations = {}
        for i, (name, param) in enumerate(signature.parameters.items()):
            if not (param.name.lower() in ["self", "args", "kwargs"]): # Exclure self, *args et **kwargs pour l'IHM...
                if param.annotation != inspect.Parameter.empty:
                    params[name] = param
                else:
                    params_without_annotations[name] =  param

        if not params_without_annotations:
            return MappingProxyType(params)
        error = f"Annotations on parameters error, Please annotate the type of the parameters:\n{params_without_annotations}"
        raise TypeError(error)
    
    @classmethod
    def discover_dynamic(cls, package: str):
        """
        Découvre et importe tous les modules dans un package donné.
        
        :param package: Le chemin du package où chercher les writters (ex. 'utils.writter').
        """
        return dynamic_discovering(package=package)