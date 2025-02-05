import sys, os


sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils.writer.AWriter import AWriter

# Découvre tous les writers dans le package utils.writer
AWriter.discover_writers('utils.writer')

# Test de création et d'utilisation d'un writer
writer = AWriter.create_writer(name='FileWriter', container='writer_test.txt')
text = "Test écriture dans fichier"

if writer.write(text):
    print("Test écriture COMPLETED")
else:
    print("Test écriture FAILED")
