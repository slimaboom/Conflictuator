from collections.abc import Iterable
from typing import Union, Type
from functools import wraps
import typing

def method_control_type(expected_type: Union[Type, Type[Iterable]]):
    """
    Un décorateur pour vérifier que le premier paramètre (après `self`) d'une méthode 
    est soit d'un type donné, soit un itérable contenant uniquement ce type.
    
    :param expected_type: Le type attendu, ou un itérable de ce type.
    """
    def decorator(func):
        @wraps(func)  # Conserve les métadonnées de la méthode originale (comme __name__)
        def wrapper(self, obj, *args, **kwargs):
            # Vérifie si expected_type est un itérable (ex: List[Aircraft])
            if hasattr(expected_type, '__origin__') and expected_type.__origin__ in [list, typing.List]:
                inner_type = expected_type.__args__[0]  # Récupère le type interne (ex: Aircraft)
                if not isinstance(obj, Iterable) or not all(isinstance(item, inner_type) for item in obj):
                    raise TypeError(
                        f"\n\nErreur dans {self.__class__.__name__}.{func.__name__}:\n"
                        f"Expected an iterable of {inner_type.__name__} objects, but got {type(obj).__name__}."
                    )
            else:
                # Sinon, vérifie que `obj` est du type attendu (ex: Aircraft)
                if not isinstance(obj, expected_type):
                    raise TypeError(
                        f"\n\nErreur dans {self.__class__.__name__}.{func.__name__}:\n"
                        f"Expected an object of type {expected_type.__name__}, but got {type(obj).__name__}."
                    )
            
            # Appelle la méthode originale
            return func(self, obj, *args, **kwargs)
        return wrapper
    return decorator
