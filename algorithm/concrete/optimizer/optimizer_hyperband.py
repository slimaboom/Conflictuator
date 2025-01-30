#from ray import tune
#from ray.tune.schedulers import ASHAScheduler
from functools import partial
from typing import List

from typing_extensions import override

from algorithm.interface.IAlgorithm import AAlgorithm
from algorithm.concrete.genetic.genetique import AlgorithmGenetic
from algorithm.interface.ISimulatedObject import ASimulatedAircraft

#import ray
from time import time

@AAlgorithm.register_algorithm
class HyperbandOptimizer(AAlgorithm):
    def __init__(self, data: List['ASimulatedAircraft'],
                 is_minimise : bool = True, 
                 num_samples: int = 20, 
                 max_epochs: int =100):
        """
        Initialise l'optimiseur Hyperband.

        :param algorithm_class: Classe de l'algorithme à optimiser (ex: AlgorithmGenetic)
        :param search_space: Dictionnaire définissant l'espace de recherche des hyperparamètres
        :param num_samples: Nombre d'expériences à tester
        :param max_epochs: Nombre max de générations pour l'optimisation
        """
        # Attributs generaux
        super().__init__(data=data, is_minimise=is_minimise)

        self.algorithm_class = None
        self.num_samples = num_samples
        self.max_epochs = max_epochs
        self.data = data
        """self.search_space = {
                "population_size": tune.choice([5, 10, 15, 20, 30, 40]),
                "generations": tune.choice([10, 20, 30]),
                "mutation_rate": tune.uniform(0.01, 0.3),
                "crossover_rate": tune.uniform(0.5, 1.0),
            }"""

        #ray.init(local_mode=True)  # Force Ray Tune à fonctionner en mode mono-thread

        self.set_process(0)
        self.progress = 0

    def evaluate(self, config, data, is_minimise=True):
        """
        Exécute un algorithme avec des hyperparamètres donnés et retourne sa performance.
        """
        self.progress += 1
        self.set_process(round(self.progress * 100 / self.num_samples, 2 ))
        self.set_process_time(time())

        algo: 'AAlgorithm' = AlgorithmGenetic(data=data, is_minimise=is_minimise, verbose=False, **config) # convertir en int pas un dictionnaire 
        algo.set_objective_function(self.get_objective_function())

        best_solution, fitness = algo.startbis()
        #tune.report({"fitness": float(fitness)})

    def optimize(self, data, is_minimise=True):
        """
        Lance l'optimisation Hyperband sur les hyperparamètres de l'algorithme.
        """
        scheduler = ASHAScheduler(
            metric="fitness", 
            mode="min" if is_minimise else "max", 
            max_t=self.max_epochs,
            grace_period=10,
            reduction_factor=3
        )
        analysis = tune.run(
            partial(self.evaluate, data=data, is_minimise=is_minimise),
            config=self.search_space,
            num_samples=self.num_samples,
            scheduler=scheduler,
            max_concurrent_trials=1,
        )

        print("Meilleurs hyperparamètres trouvés :", analysis.get_best_config(metric="fitness", mode="min" if is_minimise else "max"))
        return analysis.get_best_config(metric="fitness", mode="min" if is_minimise else "max")
    
    @override
    def run(self) : 

        self.set_start_time(start=time())

        return self.optimize(self.data, is_minimise=True)
