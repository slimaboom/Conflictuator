import heapq
import random
from typing import Dict, Tuple, List
from model.balise import Balise, DatabaseBalise
from model.configuration import BALISES

class AirwaysGenerator:
    def __init__(self, database_balise: 'DatabaseBalise', sector_margin=0.1):
        self.database_balise = database_balise
        self.sector_margin = sector_margin 
        self.graph = self.build_graph() 

    def build_graph(self) -> Dict[str, List[Tuple[str, float]]]:
        # Liste des connexions valides extraites de l'image
        valid_connections = {
            "GAI": ["GWENA", "LOBOS", "ONGHI"],
            "GWENA": ["DIRMO", "VULCA"],
            "LOBOS": ["MEN"],
            "ETORI": ["MEN", "SPIDY", "ONGHI"],
            "VULCA": ["CFA", "BURGO", "GWENA"],
            "CFA": ["ETAMO", "MINDI"],
            "LANZA": ["MINDI", "MEN"],
            "MINDI": ["CFA", "LANZA", "MTL", "LSE"],
            "GRENA": ["MTL", "SANTO", "LTP", "BOSUA"],
            "MTL": ["MAJOR", "MINDI", "GRENA", "LTP"],
            "SPIDY": ["MTL", "ETORI"],
            "LSE": ["LTP", "BOJOL", "MINDI", "LIMAN"],
            "LTP": ["LSE", "MTL", "GRENA", "MOZAO"],
            "LIMAN": ["PAS", "LSE"],
            "MOZAO": ["LTP", "SEVET"],
            "BOJOL": ["LSE", "BURGO"],
            "BURGO": ["ATN", "BOJOL", "VULCA", "VEYRI"],
            "ATN": ["BURGO"],
            "VEYRI": ["MELKA", "BURGO"],
            "MELKA": ["FRI", "PAS", "VEYRI", "SEVET"],
            "SEVET": ["MOZAO", "RAPID", "MELKA", "JUVEN"],
            "FRI": ["MELKA"],
            "BOSUA": ["JUVEN", "GRENA"],
            "JUVEN": ["BOSUA", "BIELA", "SEVET"],
            "SAMOS": ["SANTO"],
            "JAMBI": ["MTL", "SANTO", "SICIL"],
            "SANTO": ["JAMBI", "SAMOS", "GRENA"],
            "MAJOR": ["MTL"],
            "DIRMO": ["ETAMO", "GWENA"],
            "ETAMO": ["DIRMO", "CFA"],
            "LANZA": ["MINDI", "MEN"], 
            "PAS": ["MELKA", "LIMAN"],
            "BIELA": ["JUVEN"],
            "RAPID": ["SEVET"],
            "MEN" : ["CFA", "ETORI", "LANZA", "LOBOS"],
            "ONGHI": ["ETORI", "GAI"],
            "SICIL": ["JAMBI", "SODRI"],
            "SODRI" : ["SICIL"]
        
        }

        graph = {}
        for balise_name, neighbors in valid_connections.items():
            balise = self.database_balise.get_from_key(balise_name)
            if balise is None:
                print(f"Balise {balise_name} introuvable dans la base de données.")
                continue
            graph[balise_name] = []
            for neighbor in neighbors:
                other_balise = self.database_balise.get_from_key(neighbor)
                if other_balise is None:
                    print(f"Balise {neighbor} introuvable dans la base de données.")
                    continue
                distance = balise.distance_horizontale(other_balise)
                graph[balise_name].append((neighbor, distance))

        return graph

    def dijkstra(self, start: Balise, end: Balise) -> List[Balise]:
        start_name = start.get_name()
        end_name = end.get_name()

        if start_name not in self.graph or end_name not in self.graph:
            raise ValueError(f"Start or end balise not found in the graph: {start_name}, {end_name}")

        print(f"Recherche du chemin de {start_name} à {end_name}")

        queue = [(0, start_name, [])]
        visited = set()

        distances = {balise: float('inf') for balise in self.graph}
        distances[start_name] = 0

        # Parcourir le graphe
        while queue:
            cumulative_distance, current_balise_name, path = heapq.heappop(queue)

            if current_balise_name in visited:
                continue

            # Ajouter la balise actuelle au chemin
            path = path + [current_balise_name]
            visited.add(current_balise_name)

            # Vérifier si la balise actuelle est la destination
            if current_balise_name == end_name:
                print(f"Chemin trouvé : {path}")
                return [self.database_balise.get_from_key(name) for name in path]

            # Ajouter les voisins à la file de priorité
            for neighbor_name, distance in self.graph[current_balise_name]:
                if neighbor_name not in visited:
                    new_distance = cumulative_distance + distance
                    if new_distance < distances[neighbor_name]:
                        distances[neighbor_name] = new_distance
                        heapq.heappush(queue, (new_distance, neighbor_name, path))

        print("Aucun chemin trouvé")
        return []

    def get_directional_balises(self) -> Dict[str, List[Balise]]:
        """
        Divise les balises en directions (N, NE, E, SE, S, SW, W, NW).
        Exclut les balises générées au milieu du secteur.
        """
        min_x = min(balise.getX() for balise in self.database_balise.get_all().values())
        max_x = max(balise.getX() for balise in self.database_balise.get_all().values())
        min_y = min(balise.getY() for balise in self.database_balise.get_all().values())
        max_y = max(balise.getY() for balise in self.database_balise.get_all().values())

        mid_x = (min_x + max_x) / 2
        mid_y = (min_y + max_y) / 2

        directions = {dir_: [] for dir_ in ["N", "NE", "E", "SE", "S", "SW", "W", "NW"]}

        for balise in self.database_balise.get_all().values():
            x, y = balise.getX(), balise.getY()
            distance_from_center = ((x - mid_x)**2 + (y - mid_y)**2)**0.5
            if distance_from_center < 0.4: # Favoriser les balises éloignées du centre
                continue

            if y >= mid_y:  # Nord
                if x >= mid_x:
                    directions["NE"].append(balise)
                else:
                    directions["NW"].append(balise)
            else:  # Sud
                if x >= mid_x:
                    directions["SE"].append(balise)
                else:
                    directions["SW"].append(balise)

            if y >= mid_y and abs(x - mid_x) < self.sector_margin:
                directions["N"].append(balise)
            elif y <= mid_y and abs(x - mid_x) < self.sector_margin:
                directions["S"].append(balise)
            elif x >= mid_x and abs(y - mid_y) < self.sector_margin:
                directions["E"].append(balise)
            elif x <= mid_x and abs(y - mid_y) < self.sector_margin:
                directions["W"].append(balise)

        return directions

    def generate_route_between_different_quadrants(self, min_balises: int = random.randint(5,10)) -> List[Balise]:
        """
        Génère une route entre deux balises dans des directions différentes,
        avec un nombre minimum de balises.
        """
        directions = self.get_directional_balises()

        start_direction = random.choice(list(directions.keys()))
        while not directions[start_direction]:
            start_direction = random.choice(list(directions.keys()))

        allowed_directions = [dir_ for dir_ in directions.keys() if dir_ != start_direction and not self.is_same_quadrant(start_direction, dir_)]

        end_direction = random.choice(allowed_directions)
        while not directions[end_direction]:
            end_direction = random.choice(allowed_directions)

        start_balise = random.choice(directions[start_direction])
        end_balise = random.choice(directions[end_direction])

        # Dijkstra 
        path = self.dijkstra(start_balise, end_balise)

        """# Vérifier si chemin respecte le nombre minimum de balises
        if len(path) < min_balises:
            print(f"Chemin trop court ({len(path)} balises). Ajout de balises intermédiaires.")
            path = self.add_intermediate_balises(path, min_balises)"""

        return path

    """def add_intermediate_balises(self, path: List[Balise], min_balises: int) -> List[Balise]:
        remaining_balises = [balise for balise in self.database_balise.get_all().values() if balise not in path]
        new_path = []

        # Ajouter les balises existantes tout en insérant des balises intermédiaires si nécessaire
        for i in range(len(path) - 1):
            new_path.append(path[i])
            if len(new_path) < min_balises - 1 and remaining_balises:
                intermediate_balise = random.choice(remaining_balises)
                new_path.append(intermediate_balise)
                remaining_balises.remove(intermediate_balise)

        # Ajouter la dernière balise
        new_path.append(path[-1])

        # Si toujours insuffisant, insérer encore plus de balises
        while len(new_path) < min_balises and remaining_balises:
            new_path.insert(-1, random.choice(remaining_balises))

        return new_path"""



    @staticmethod
    def is_same_quadrant(direction1: str, direction2: str) -> bool:
        """
        Vérifie si deux directions appartiennent au même quadrant.
        """
        quadrant_groups = [
            {"N", "NE", "NW"},
            {"S", "SE", "SW"},
            {"E", "NE", "SE"},
            {"W", "NW", "SW"}
        ]
        for group in quadrant_groups:
            if direction1 in group and direction2 in group:
                return True
        return False
