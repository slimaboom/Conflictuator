from configuration import MAIN_SECTOR, SECONDARY_SECTOR, BALISES, ROUTES

import matplotlib.pyplot as plt

def main():
    
    # Affichage du background
    fig, ax = plt.subplots(figsize=(15,10))
    limit_xy = 0.05

    # Affichage du secteur principale
    ax = MAIN_SECTOR.plot(ax, color="#D9EAD3")

    # Affichage des secteurs secondaires
    ax = SECONDARY_SECTOR.plot(ax, color="#F3F3D9")

    # Affichage des balises
    ax = BALISES.plot(ax, color='#BBBBBB')

    # Affichage des routes aeriennes
    ax = ROUTES.plot(ax, BALISES, color='grey')

    # Limit de la figure
    ax.set_xlim(-limit_xy, 1+limit_xy)
    ax.set_ylim(-limit_xy, 1+limit_xy)
    ax.set_aspect('equal', adjustable='box')
    
    fig.tight_layout()
    plt.show()
    return 0


if __name__ == '__main__':
    main()