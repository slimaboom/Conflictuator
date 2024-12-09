import numpy as np

def rad_to_deg_aero(radians: float) -> float:
    deg = np.rad2deg(radians)
    # Convertir le système mathématique (0° = Est, 90° = Nord) au système aéronautique 
    deg_aero = (450 - deg) % 360
    return deg_aero if deg_aero != 0 else 360.


def sec_to_time(seconds: float) -> str:
    """Convertit un temps en secondes avec précision en un format HH:MM:SS.sss."""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = seconds % 60  # Inclure les fractions
    return f"{hours:02}:{minutes:02}:{secs:06.3f}"  # Ajoute 3 décimales pour les secondes


def time_to_sec(time_str: str) -> float:
    """
    Convertit un temps au format HH:MM:SS ou HH:MM:SS.ss en secondes.
    
    Args:
        time_str (str): Une chaîne de caractères représentant le temps (HH:MM:SS ou HH:MM:SS.ss).
    
    Returns:
        float: Le temps en secondes.
    
    Raises:
        ValueError: Si le format n'est pas valide.
    """
    try:
        # Séparation entre la partie "HH:MM:SS" et la partie millisecondes éventuelle
        if "." in time_str:
            main_time, millis = time_str.split(".")
            millis = int(millis) / 100  # Convertir les centièmes en fractions de seconde
        else:
            main_time = time_str
            millis = 0

        # Découpage de la partie principale en heures, minutes et secondes
        hours, minutes, secs = map(int, main_time.split(":"))
        return hours * 3600 + minutes * 60 + secs + millis/10
    except ValueError:
        raise ValueError("Le format du temps doit être HH:MM:SS ou HH:MM:SS.ss.")



if __name__ == "__main__":
    # Test rad_to_deg_aero
    for angle in [0, np.pi/2, np.pi, 3*np.pi/2, 5*np.pi/6]:
        msg = f"""Radians: {angle}
MathsDeg: {np.rad2deg(angle)}
AeroAngle: {rad_to_deg_aero(angle)}
"""
        print(msg)
    
    # Test sec_to_time
    print(sec_to_time(803.76))
    print(time_to_sec(sec_to_time(803.760)))

    