import os
import pkgutil
import importlib

def dynamic_discovering(package: str, filename: str):
    """
    Découvre et importe tous les modules dans un package donné.
    
    :param package: Le chemin du package où chercher les writters (ex. 'utils.formatter').
    :param filename: Le chemin du fichier depuis où chercher le module (ex. 'exemple.py').

    """
    # Résout le chemin absolu vers le package
    package_path = os.path.join(os.path.dirname(filename))

    if not os.path.isdir(package_path):
        error  = f"Le chemin {package_path} n'existe pas ou n'est pas un dossier."
        error += f"\nArgument: package: {package}, filename: {filename}"
        raise ValueError(error)

    # Découvre et importe chaque module
    for a, module_name, b in pkgutil.iter_modules([package_path]):
        full_module_name = f"{package}.{module_name}"
        importlib.import_module(full_module_name)