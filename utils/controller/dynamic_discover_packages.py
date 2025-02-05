import os
import pkgutil
import importlib

def add_init_files(directory: str):
    """
    Ajoute un fichier __init__.py dans chaque répertoire contenant au moins un fichier .py.

    :param directory: Le répertoire de base du projet.
    """
    init_file = '__init__.py'
    for root, dirs, files in os.walk(directory):
        if any(file.endswith('.py') for file in files) and init_file not in files:
            init_path = os.path.join(root, "__init__.py")
            msg = f"Ajout de {init_path} pour faire de la découverte dynamique des nouvelles classes à enregister dans MetaDynamiqueDatabase"
            print(f"Ajout de {init_path}")
            with open(init_path, 'w') as f:
                pass

def dynamic_discovering(package: str):
    """
    Découvre et importe tous les modules dans un package donné, y compris ceux dans les sous-répertoires.
    Si les modules du package ne sont pas chargés c'est qu'il faut dans le répertoire le fichier
    __init__.py pour que le module <pkgutil.walk_packages> puisse reconnaitre le dossier comme "package"
    :param package: Le chemin du package où chercher les modules (ex. 'algorithm').
    """
    # Récupère le chemin du package (répertoire) en utilisant le nom du package
    package_path = package.replace('.', os.sep)
    
    if not os.path.isdir(package_path):
        raise ValueError(f"Le package '{package}' est introuvable.")

    # Ajout des fichiers __init__.py si nécessaire
    add_init_files(package_path)

    # Importer le package principal
    try:
        importlib.import_module(package)
    except ModuleNotFoundError:
        raise ValueError(f"Le package '{package}' ne peut pas être importé.")


    # Explore le répertoire et les sous-répertoires
    for importer, modname, ispkg in pkgutil.walk_packages(path=[package_path], prefix=package + '.', onerror=lambda x: None):
        # Tente d'importer chaque module découvert
        importlib.import_module(modname)
        #print(f"Module importé: {modname}")



def main_dynamic_discovering():
    from algorithm.interface.IAlgorithm import AAlgorithm
    from algorithm.interface.IObjective import AObjective
    from utils.formatter.AFormat import AFormat
    from utils.writer.AWriter import AWriter
    from utils.reader.AReader import AReader
    from model.traffic.abstract.ATrafficGenerator import ATrafficGenerator
    from model import configuration
    # Découverte dynamique des formats pour les enregistrés dans une méta base: MetaDynamiqueDatabase depuis AFormat
    AFormat.discover_formatters('utils.formatter')

    # Découverte dynamique des writers pour les enregistrés dans une méta base: MetaDynamiqueDatabase depuis AWriter
    AWriter.discover_writers('utils.writer')

    # Découverte dynamique des readers pour les enregistrés dans une méta base: MetaDynamiqueDatabase depuis AReader
    AReader.discover_readers('utils.reader')


    # Découverte dynamique des algorithms pour les enregistrés dans dans une méta base: MetaDynamiqueDatabase depuis AAlgorithm
    # Découverte dynamique des fonctions objectives pour les enregistrés dans une méta base: MetaDynamiqueDatabase depuis  Aobjective
    
    # Comme les deux classes abstraites sont dans algorithm.interface il suffit d'appeler une fois
    AAlgorithm.discover_algorithms('algorithm')
    #AObjective.discover_objective_functions('algorithm.objective_function')

    # Si AObjective est déplacé dans le répertoire objective_function
    #AObjective.discover_objective_functions('algorithm.objective_function')

    # Découverte dynamique des générateurs de traffic
    ATrafficGenerator.discover_traffic_generators('model.traffic')
