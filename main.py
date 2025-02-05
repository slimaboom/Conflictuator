from platform import system
from enum import Enum
import os
import sys

from PyQt5.QtWidgets import QApplication

from utils.controller.dynamic_discover_packages import main_dynamic_discovering
from view.main_window import MainWindow

class PlatformName(Enum):
    WINDOWS = "Windows"
    LINUX   = "Linux"
    MACOS   = "Darwin"


#----------------------------------------------------------------------------
#---------------------   MAIN PART  -----------------------------------------
#----------------------------------------------------------------------------

def main():

    # platforme_name: Linux | Darwin | Windows
    platform_name = system()
    if platform_name == PlatformName.LINUX.value:
        os.environ["QT_QPA_PLATFORM"] = "xcb" 
    elif platform_name == PlatformName.MACOS.value:
        os.environ["QT_QPA_PLATFORM"] = "cocoa"
    else: # Windows
        pass

    # Découverte dynamique des algorithms, fonctions objectifs, writers, formatters, traffic generator
    main_dynamic_discovering()

    # Apres gestion de la variable d'environnement: lancement de la fenetre
    app = QApplication(sys.argv)
    window = MainWindow()
    sys.exit(app.exec_())

# Application PyQt5
if __name__ == "__main__":
    main()