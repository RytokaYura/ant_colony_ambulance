import random as rn
import numpy as np
from numpy.random import choice


class AntColony:
    def __init__(self, distances, n_ants, n_best, n_iterations, decay, alpha=0.5, beta=2):
        self.distances = distances
        self.pheromone = np.ones(self.distances.shape) / len(distances)
        self.all_loc = list(range(len(distances)))
        self.n_ants = n_ants
        self.n_best = n_best
        self.n_iterations = n_iterations
        self.decay = decay
        self.alpha = alpha
        self.beta = beta
        self.route_history = []

    def run(self, start, end):
        best_route = (None, np.inf)
        self.route_history = []

        for i in range(self.n_iterations):
            all_routes = self.generate_all_routes(start, end)
            all_routes = [p for p in all_routes if p[0] is not None]

            if not all_routes:
                continue

            self.route_history.extend([p[0] for p in all_routes])
            print(f"Iterasi {i + 1}:")
            for route, dist in all_routes:
                print(f"  Rute: {route}, Jarak: {dist:.2f}")

            self.spread_pheromone(all_routes, self.n_best)
            shortest_route = min(all_routes, key=lambda x: x[1])
            if shortest_route[1] < best_route[1]:
                best_route = shortest_route

            self.pheromone = self.pheromone * self.decay
            print(f"Iterasi {i + 1}/{self.n_iterations} - Terbaik: {shortest_route[1]:.2f}")

        return best_route

    def spread_pheromone(self, all_routes, n_best):
        sorted_routes = sorted(all_routes, key=lambda x: x[1])
        for route, dist in sorted_routes[:n_best]:
            for move in route:
                i, j = move
                self.pheromone[i][j] += 1.0 / (self.distances[i][j] + 1e-10)  

    def generate_all_routes(self, start, end):
        all_routes = []
        for _ in range(self.n_ants):
            route = self.gen_route(start, end)
            dist = self.gen_route_dist(route) if route is not None else np.inf
            all_routes.append((route, dist))
        return all_routes

    def gen_route(self, start, end):
        route = []
        visited = set()
        visited.add(start)
        current = start

        while current != end:
            move = self.pick_move(self.pheromone[current], self.distances[current], visited)
            if move is None:
                return None  
            route.append((current, move))
            current = move
            visited.add(current)

        return route

    def gen_route_dist(self, route):
        return sum(self.distances[i][j] for i, j in route)

    def pick_move(self, pheromone_row, dist_row, visited):
        pheromone = np.copy(pheromone_row)
        pheromone[list(visited)] = 0 

        inv_dist = np.array([1.0 / (d + 1e-10) if d > 0 else 0 for d in dist_row])
        inv_dist[list(visited)] = 0

        prob = (pheromone ** self.alpha) * (inv_dist ** self.beta)

        if prob.sum() == 0:
            allowed = [loc for loc in self.all_loc if loc not in visited]
            if not allowed:
                return None
            return np.random.choice(allowed)

        prob = prob / prob.sum()
        move = np.random.choice(self.all_loc, 1, p=prob)[0]
        return move