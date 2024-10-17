import random
import math
from EVRP import *

class Herusitic:
    def __init__(self, EVRP, alpha=1.0, beta=2.0, evaporation_rate=0.5, pheromone_deposit=100.0):
        self.best_sol = None  # Najlepšie riešenie
        self.EVRP = EVRP  # EVRP objekt

        # Počet vozidiel načítame priamo z dát EVRP
        self.num_vehicles = self.EVRP.MIN_VEHICLES

        self.alpha = alpha  # Váha feromónov
        self.beta = beta  # Váha viditeľnosti
        self.evaporation_rate = evaporation_rate  # Rýchlosť odparovania feromónov
        self.pheromone_deposit = pheromone_deposit  # Množstvo feromónov na dobrej trase
        
        # Inicializácia feromónovej matice na základe veľkosti problému
        self.pheromone_matrix = [[1.0 for _ in range(EVRP.ACTUAL_PROBLEM_SIZE)] for _ in range(EVRP.ACTUAL_PROBLEM_SIZE)]
        self.visibility_matrix = [[0.0 for _ in range(EVRP.ACTUAL_PROBLEM_SIZE)] for _ in range(EVRP.ACTUAL_PROBLEM_SIZE)]

        # Vypočítanie viditeľnosti (inverzná vzdialenosť)
        for i in range(EVRP.ACTUAL_PROBLEM_SIZE):
            for j in range(EVRP.ACTUAL_PROBLEM_SIZE):
                if i != j:
                    self.visibility_matrix[i][j] = 1.0 / EVRP.get_distance(i, j)

    def initialize_heuristic(self):
        """Inicializácia štruktúry pre heuristiku."""
        self.best_sol = {
            'tour': [[0] * (self.EVRP.NUM_OF_CUSTOMERS + 1000) for _ in range(self.num_vehicles)], 
            'steps': [0] * self.num_vehicles, 
            'tour_length': math.inf
        }

    def run_heuristic(self):
        """Spustenie heuristiky s feromónovou maticou a viacerými vozidlami."""
        # Rozdelenie zákazníkov medzi vozidlá
        customers = list(range(1, self.EVRP.NUM_OF_CUSTOMERS + 1))
        random.shuffle(customers)
        customer_groups = [customers[i::self.num_vehicles] for i in range(self.num_vehicles)]
        
        for vehicle_id in range(self.num_vehicles):
            self.construct_solution(vehicle_id, customer_groups[vehicle_id])

        # Aktualizácia feromónov po zostavení riešenia
        self.update_pheromones()


    def construct_solution(self, vehicle_id, customer_group):
        """Konštrukcia riešenia pre konkrétne vozidlo."""
        r = customer_group  # Vozidlo obsluhuje len svoju skupinu zákazníkov
        random.shuffle(r)

        energy_temp = 0.0
        capacity_temp = 0.0

        self.best_sol['steps'][vehicle_id] = 1
        self.best_sol['tour'][vehicle_id][0] = self.EVRP.DEPOT  # Začiatok v depe

        i = 0
        while i < len(r):
            from_node = self.best_sol['tour'][vehicle_id][self.best_sol['steps'][vehicle_id] - 1]
            to_node = self.select_next_node(from_node, r)

            if (capacity_temp + self.EVRP.get_customer_demand(to_node) <= self.EVRP.MAX_CAPACITY and
                energy_temp + self.EVRP.get_energy_consumption(from_node, to_node) <= self.EVRP.BATTERY_CAPACITY):
                capacity_temp += self.EVRP.get_customer_demand(to_node)
                energy_temp += self.EVRP.get_energy_consumption(from_node, to_node)
                self.best_sol['tour'][vehicle_id][self.best_sol['steps'][vehicle_id]] = to_node
                self.best_sol['steps'][vehicle_id] += 1
                r.remove(to_node)
                i += 1
            else:
                if capacity_temp + self.EVRP.get_customer_demand(to_node) > self.EVRP.MAX_CAPACITY:
                    capacity_temp = 0.0  # Vozidlo ide späť do depa
                if energy_temp + self.EVRP.get_energy_consumption(from_node, to_node) > self.EVRP.BATTERY_CAPACITY:
                    charging_station = self.find_nearest_charging_station(from_node)
                    self.best_sol['tour'][vehicle_id][self.best_sol['steps'][vehicle_id]] = charging_station
                    energy_temp = 0.0
                self.best_sol['steps'][vehicle_id] += 1

        if self.best_sol['tour'][vehicle_id][self.best_sol['steps'][vehicle_id] - 1] != self.EVRP.DEPOT:
            self.best_sol['tour'][vehicle_id][self.best_sol['steps'][vehicle_id]] = self.EVRP.DEPOT
            self.best_sol['steps'][vehicle_id] += 1

        tour_length = self.EVRP.fitness_evaluation(self.best_sol['tour'][vehicle_id][:self.best_sol['steps'][vehicle_id]])
        if tour_length < self.best_sol['tour_length']:
            self.best_sol['tour_length'] = tour_length

    def select_next_node(self, from_node, candidate_list):
        """Výber ďalšieho uzla pre vozidlo na základe pravdepodobnosti vypočítanej z feromónov a viditeľnosti."""
        probabilities = []
        total_prob = 0.0

        for to_node in candidate_list:
            pheromone = self.pheromone_matrix[from_node][to_node] ** self.alpha
            visibility = self.visibility_matrix[from_node][to_node] ** self.beta
            prob = pheromone * visibility
            probabilities.append((to_node, prob))
            total_prob += prob

        rand_value = random.uniform(0, total_prob)
        cumulative_prob = 0.0
        for to_node, prob in probabilities:
            cumulative_prob += prob
            if rand_value <= cumulative_prob:
                return to_node

        return candidate_list[0]

    def find_nearest_charging_station(self, current_node):
        """Nájde najbližšiu nabíjaciu stanicu z aktuálnej polohy."""
        nearest_station = None
        min_distance = float('inf')
        for i in range(self.EVRP.NUM_OF_CUSTOMERS + 1, self.EVRP.ACTUAL_PROBLEM_SIZE):
            if self.EVRP.is_charging_station(i):
                distance = self.EVRP.get_distance(current_node, i)
                if distance < min_distance:
                    min_distance = distance
                    nearest_station = i
        return nearest_station

    def update_pheromones(self):
        """Aktualizácia feromónov na základe získaných riešení."""
        for i in range(self.EVRP.ACTUAL_PROBLEM_SIZE):
            for j in range(self.EVRP.ACTUAL_PROBLEM_SIZE):
                self.pheromone_matrix[i][j] *= (1 - self.evaporation_rate)

        for vehicle_id in range(self.num_vehicles):
            for step in range(self.best_sol['steps'][vehicle_id] - 1):
                from_node = self.best_sol['tour'][vehicle_id][step]
                to_node = self.best_sol['tour'][vehicle_id][step + 1]
                self.pheromone_matrix[from_node][to_node] += self.pheromone_deposit / self.best_sol['tour_length']
