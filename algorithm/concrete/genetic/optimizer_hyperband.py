from ray import tune
from ray.tune.schedulers import ASHAScheduler
from typing import Dict, Any, List

from typing_extensions import override

from algorithm.interface.IAlgorithm import AAlgorithm
from algorithm.concrete.genetic.genetique import AlgorithmGeneticBase
from algorithm.interface.ISimulatedObject import ASimulatedAircraft
import ray
import time
from ray.air import session

@AAlgorithm.register_algorithm
class HyperbandOptimizer(AAlgorithm):
    def __init__(self,
                 data: List['ASimulatedAircraft'],
                 is_minimise: bool = True,
                 verbose: bool = False,
                 num_samples: int = 20,
                 max_epochs: int = 100,
                 **kwargs):
        """
        Initialise l'optimiseur Hyperband.

        :param data: Données d'entrée pour l'algorithme.
        :param is_minimise: Booléen indiquant si l'on minimise ou maximise la fitness.
        :param verbose: Affiche les logs si True.
        :param timeout: Temps maximum d'exécution en secondes.
        :param num_samples: Nombre d'expériences à tester.
        :param max_epochs: Nombre max de générations pour l'optimisation.
        :param algorithm_class: Classe de l'algorithme génétique à optimiser.
        """
        super().__init__(data=data, is_minimise=is_minimise, verbose=verbose, **kwargs)
        
        self.num_samples = num_samples
        self.max_epochs = max_epochs
        self.search_space = {
            "population_size": tune.choice([10, 20, 30, 40]),
            "generations": tune.choice([10, 20, 30]),
            "mutation_rate": tune.uniform(0.01, 0.3),
            "crossover_rate": tune.uniform(0.5, 1.0),
        }
        
        ray.init(local_mode=True)  # Mode mono-thread
        self.progress = 0

    def evaluate(self, config: Dict[str, Any]):
        """
        Exécute l'algorithme génétique avec les hyperparamètres donnés et retourne sa performance.
        """
        self.progress += 1
        
        algo = AlgorithmGeneticBase(
            data=self.get_data(),
            population_size=config["population_size"],
            generations=config["generations"],
            mutation_rate=config["mutation_rate"],
            crossover_rate=config["crossover_rate"],
            is_minimise=True,
            verbose = True,
        )

        algo.set_objective_function(self.get_objective_function())
        algo.start()
        best_fitness = algo.get_best_fitness()
        print(best_fitness)
        
        session.report({"fitness": float(best_fitness)})

    def optimize(self):
        """
        Lance l'optimisation Hyperband sur les hyperparamètres de l'algorithme génétique.
        """
        scheduler = ASHAScheduler(
            metric="fitness",
            mode="min" if True else "max",
            max_t=self.max_epochs,
            grace_period=10,
            reduction_factor=3
        )
        
        analysis = tune.run(
            self.evaluate,
            config=self.search_space,
            num_samples=self.num_samples,
            scheduler=scheduler,
            max_concurrent_trials=1,
        )
        
        best_config = analysis.get_best_config(metric="fitness", mode="min" if self.is_minimise else "max")
        print("Meilleurs hyperparamètres trouvés :", best_config)
        return best_config
    
    @override
    def run(self):
        """
        Exécute l'optimisation et retourne les meilleurs hyperparamètres trouvés.
        """
        self.set_start_time(start=time.time())
        return self.optimize()
