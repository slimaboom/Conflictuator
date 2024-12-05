from configuration import MAIN_SECTOR, SECONDARY_SECTOR, BALISES, ROUTES
from route import Airway
from aircraft import Aircraft
from animation import update

import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

def main():
    # Création de la figure et des axes
    fig, ax = plt.subplots(figsize=(15, 10))

    # Création des avions avec un plan de vol
    aircrafts = [Aircraft(speed=0.02, 
                          flight_plan=Airway.transform(ROUTES.get_from_key("NO-SE1"), BALISES))]
    
    # Initialiser l'animation
    timestep = 0.05  # Intervalle de temps pour chaque mise à jour

    # Passer les secteurs et les routes en tant que paramètres dans la fonction update
    ani = FuncAnimation(
        fig,
        update,  # La fonction à appeler à chaque frame
        frames=200,  # Nombre total de frames
        fargs=(aircrafts, timestep, ax, MAIN_SECTOR, SECONDARY_SECTOR, BALISES, ROUTES),  # Arguments supplémentaires
        interval=100,  # Intervalle en millisecondes
        blit=False  # On ne fait pas du "blit" ici car il y a trop d'éléments à redessiner
    )

    # Afficher la figure
    plt.show()
    return 0


if __name__ == '__main__':
    main()