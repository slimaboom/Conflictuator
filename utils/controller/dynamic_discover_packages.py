import os
import pkgutil
import importlib

def dynamic_discovering(package: str):
    """
    Découvre et importe tous les modules dans un package donné, y compris ceux dans les sous-répertoires.
    
    :param package: Le chemin du package où chercher les modules (ex. 'algorithm').
    """
    # Récupère le chemin du package (répertoire) en utilisant le nom du package
    package_path = package.replace('.', os.sep)
    if not os.path.isdir(package_path):
        error  = f"Le chemin {package_path} n'existe pas ou n'est pas un dossier."
        error += f"\nArgument: package: {package}"
        raise ValueError(error)

    # Explore le répertoire et les sous-répertoires
    for importer, modname, ispkg in pkgutil.walk_packages(path=[package_path], prefix=package + '.', onerror=lambda x: None):
        # Tente d'importer chaque module découvert
        importlib.import_module(modname)
        #print(f"Module importé: {modname}")



def main_dynamic_discovering():
    from algorithm.interface.IAlgorithm import AAlgorithm
    from algorithm.interface.IObjective import AObjective
    from utils.formatter.AFormat import AFormat
    from utils.writter.AWritter import AWritter

    # Découverte dynamique des formats pour les enregistrés dans une méta base: MetaDynamiqueDatabase depuis AFormat
    AFormat.discover_formatters('utils.formatter')

    # Découverte dynamique des writters pour les enregistrés dans une méta base: MetaDynamiqueDatabase depuis AWritter
    AWritter.discover_writters('utils.writter')

    # Découverte dynamique des algorithms pour les enregistrés dans dans une méta base: MetaDynamiqueDatabase depuis AAlgorithm
    # Découverte dynamique des fonctions objectives pour les enregistrés dans une méta base: MetaDynamiqueDatabase depuis  Aobjective
    # Comme les deux classes abstraites sont dans algorithm.interface il suffit d'appeler une fois
    AAlgorithm.discover_algorithms('algorithm.concrete')
    AObjective.discover_objective_functions('algorithm.objective_function')

    # Si AObjective est déplacé dans le répertoire objective_function
    #AObjective.discover_objective_functions('algorithm.objective_function')

