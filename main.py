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
                          flight_plan=Airway.transform(ROUTES.get_from_key("NO-SE1"), BALISES)),
                 Aircraft(speed=0.04, 
                          flight_plan=Airway.transform(ROUTES.get_from_key("NO-SO1"), BALISES, reverse=True))]
    
    # Initialiser l'animation
    # Calcul du timestep basé sur l'intervalle et le facteur d'échelle
    timestep = 0.1

    # Passer les secteurs et les routes en tant que paramètres dans la fonction update
    ani = FuncAnimation(
        fig,
        update,  # La fonction à appeler à chaque frame
        frames=500,  # Nombre total de frames
        fargs=(aircrafts, timestep, ax, MAIN_SECTOR, SECONDARY_SECTOR, BALISES, ROUTES),  # Arguments supplémentaires
        interval=50,  # Intervalle en millisecondes
        blit=False  # On ne fait pas du "blit" ici car il y a trop d'éléments à redessiner
    )

    # Afficher la figure
    plt.show()
    return 0


if __name__ == '__main__':
    main()