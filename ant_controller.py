import numpy as np
from ant_colony import AntColony

class AntController:
    def __init__(self, distances, n_ants=50, n_best=10, n_iterations=100, decay=0.8, alpha=1, beta=1):
        np.random.seed(123)
        self.ant_colony = AntColony(
            distances=distances,
            n_ants=n_ants,
            n_best=n_best,
            n_iterations=n_iterations,
            decay=decay,
            alpha=alpha,
            beta=beta
        )

    def find_best_route(self, start, end):
        return self.ant_colony.run(start, end)

    @staticmethod
    def translate_route(route, node_names):
         return [(node_names[i], node_names[j]) for i, j in route]
