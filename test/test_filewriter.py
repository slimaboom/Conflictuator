import sys, os


sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils.writter.AWritter import AWritter

# Découvre tous les writters dans le package utils.writter
AWritter.discover_writters('utils.writter')

# Test de création et d'utilisation d'un writter
writter = AWritter.create_writter(name='filewritter', container='writter_test.txt')
text = "Test écriture dans fichier"

if writter.write(text):
    print("Test écriture COMPLETED")
else:
    print("Test écriture FAILED")