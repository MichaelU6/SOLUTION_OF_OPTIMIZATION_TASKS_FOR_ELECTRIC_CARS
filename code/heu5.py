import sys
import math
import random
from EVRP import *
from stats import *

class Herusitic:
    def __init__(self, EVRP, alpha=0.5, beta=3.0, evaporation_rate=0.5, pheromone_deposit=100.0, iterations=20):
        self.best_sol = None  # Najlepšie riešenie
        self.EVRP = EVRP  # EVRP objekt
        self.num_vehicles = self.EVRP.MIN_VEHICLES

        self.alpha = alpha  # Váha feromónov
        self.beta = beta  # Váha viditeľnosti
        self.evaporation_rate = evaporation_rate  # Rýchlosť odparovania feromónov
        self.pheromone_deposit = pheromone_deposit  # Množstvo feromónov na dobrej trase
        self.iterations = iterations  # Počet iterácií pre zlepšenie riešení

        # Inicializácia feromónovej matice
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
            'tour': [[0] * (self.EVRP.NUM_OF_CUSTOMERS + 100) for _ in range(self.num_vehicles)], 
            'steps': [0] * self.num_vehicles, 
            'tour_length': math.inf
        }

    def run_aco(self, stats):
        global_best = {
            'tour': None,
            'steps': None,
            'tour_length': math.inf
        }

        for iteration in range(self.iterations):
            self.run_heuristic()  # Pošlem jedného mravca obsluzit vsetky auta so vsetkymi zakaznikmy

            

            # ak
            if self.best_sol['tour_length'] < global_best['tour_length']:
                global_best['tour'] = [list(route) for route in self.best_sol['tour']]
                global_best['steps'] = list(self.best_sol['steps'])
                global_best['tour_length'] = self.best_sol['tour_length']
            
            # do štatistík zapíšem riešenie tejto iterácií, jeho dĺžku
            stats.get_mean(iteration, self.best_sol['tour_length'])

            #print(f"Iteration {iteration + 1}, Best Tour Length: {global_best['tour_length']}")
            
        # Ked dobehnu vsetky mravce konkretne 10, podla toho kto mal najkratsiu cestu updatnem feromonovu maticu
        self.update_pheromones()
        
        return global_best

    def run_heuristic(self):
        """Spustenie heuristiky s feromónovou maticou a viacerými vozidlami."""
        #self.initialize_heuristic()
        # Rozdelenie zákazníkov medzi vozidlá
        customers = list(range(1, self.EVRP.NUM_OF_CUSTOMERS + 1))
        random.shuffle(customers)
        customer_groups = [customers[i::self.num_vehicles] for i in range(self.num_vehicles)]
        for vehicle_id in range(self.num_vehicles):
            self.construct_solution(vehicle_id, customer_groups[vehicle_id])
        
        # Ked vygenerujem pre vsetky auta jedno riesenie porovnam ho ci nieje najlepsie. Vlastne je to riesenie jedneho mravca
        tour_length = self.EVRP.fitness_evaluation(self.best_sol)
        #if tour_length < self.best_sol['tour_length']:
        #    self.best_sol['tour_length'] = tour_length

    def construct_solution(self, vehicle_id, customer_group):
        """Konštrukcia riešenia pre konkrétne vozidlo."""
        r = customer_group
        random.shuffle(r)

        energy_temp = 0.0
        capacity_temp = 0.0

        self.best_sol['steps'][vehicle_id] = 1
        self.best_sol['tour'][vehicle_id][0] = self.EVRP.DEPOT  # Začiatok v depe

        #print(r)
        i = 0
        while i < len(r):
            from_node = self.best_sol['tour'][vehicle_id][self.best_sol['steps'][vehicle_id] - 1]
            to_node = self.select_next_node(from_node, r)
            min_Battery = self.EVRP.get_energy_consumption(to_node, self.find_nearest_charging_station(to_node)) 

            if (capacity_temp + self.EVRP.get_customer_demand(to_node) <= self.EVRP.MAX_CAPACITY and
                energy_temp + self.EVRP.get_energy_consumption(from_node, to_node) + min_Battery <= self.EVRP.BATTERY_CAPACITY):
                capacity_temp += self.EVRP.get_customer_demand(to_node)
                energy_temp += self.EVRP.get_energy_consumption(from_node, to_node)
                self.best_sol['tour'][vehicle_id][self.best_sol['steps'][vehicle_id]] = to_node
                self.best_sol['steps'][vehicle_id] += 1
                #print(to_node, energy_temp)
                r.remove(to_node)
            else:
                """Ked vozidlo nema dostatok miesta na obsluzenie vybreneho zakaznika alebo dost baterie poslem ho do depa/najblizsej stanice"""
                if capacity_temp + self.EVRP.get_customer_demand(to_node) > self.EVRP.MAX_CAPACITY:
                    if energy_temp + self.EVRP.get_energy_consumption(from_node, 0) <= self.EVRP.BATTERY_CAPACITY:
                        capacity_temp = 0.0  # Vozidlo ide späť do depa
                        energy_temp = 0.0
                        self.best_sol['tour'][vehicle_id][self.best_sol['steps'][vehicle_id]] = self.EVRP.DEPOT
                        self.best_sol['steps'][vehicle_id] += 1
                    else:
                        self.find_path_in_depo(from_node, energy_temp, vehicle_id)
                        energy_temp = 0.0
                        capacity_temp = 0.0  # Vozidlo ide späť do depa
                    #print(self.EVRP.DEPOT, energy_temp)
                if energy_temp + self.EVRP.get_energy_consumption(from_node, to_node) > self.EVRP.BATTERY_CAPACITY:
                    charging_station = self.find_nearest_charging_station(from_node)
                    self.best_sol['tour'][vehicle_id][self.best_sol['steps'][vehicle_id]] = charging_station
                    energy_temp = 0.0
                    #print(charging_station, energy_temp)
                    self.best_sol['steps'][vehicle_id] += 1
                

        if self.best_sol['tour'][vehicle_id][self.best_sol['steps'][vehicle_id] - 1] != self.EVRP.DEPOT:
        #    self.best_sol['tour'][vehicle_id][self.best_sol['steps'][vehicle_id]] = self.EVRP.DEPOT
        #    self.best_sol['steps'][vehicle_id] += 1
            #print("bater = " + str(energy_temp))
            self.find_path_in_depo(self.best_sol['tour'][vehicle_id][self.best_sol['steps'][vehicle_id] - 1], energy_temp, vehicle_id)    
        #print(self.EVRP.MAX_CAPACITY)
        #skontrolujem riesenie pre vozidlo ci je dokoncene a ci obsluzil vsektych zakaznikov
        #self.EVRP.check_solution(self.best_sol['tour'][vehicle_id][:self.best_sol['steps'][vehicle_id]])
        
        
        #tour_length = self.EVRP.fitness_evaluation(self.best_sol['tour'][vehicle_id][:self.best_sol['steps'][vehicle_id]])
        #if tour_length < self.best_sol['tour_length']:
        #    self.best_sol['tour_length'] = tour_length

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
    
    def find_path_in_depo(self, current_node, energyCapacity, vehicleId):
        """Nájdi cestu do depa ked vozidlo ma uz nejaku energiu minutu"""
        # Ak je dosť energie na návrat do depa, vráť depo ako ďalší uzol
        distance_to_depo = self.EVRP.get_energy_consumption(current_node, self.EVRP.DEPOT)
        #print("A")
        #print(distance_to_depo)
        #print(energyCapacity)
        if self.EVRP.BATTERY_CAPACITY - energyCapacity >= distance_to_depo:
            #print("JJ")
            self.best_sol['tour'][vehicleId][self.best_sol['steps'][vehicleId]] = self.EVRP.DEPOT
            self.best_sol['steps'][vehicleId] += 1
            #return self.EVRP.DEPOT
        else:
            # Ak nie je dosť energie, nájdi najbližšiu nabíjaciu stanicu
            #while current_node != 0:
            #    distance_to_depo = self.EVRP.get_energy_consumption(current_node, self.EVRP.DEPOT)
            #    if self.EVRP.BATTERY_CAPACITY - energyCapacity >= distance_to_depo:
            #        self.best_sol['tour'][vehicleId][self.best_sol['steps'][vehicleId]] = self.EVRP.DEPOT
             #       self.best_sol['steps'][vehicleId] += 1
            #        current_node = self.EVRP.DEPOT
            #    else:
            #        nearest_station = self.find_nearest_charging_station(current_node)
            #        self.best_sol['tour'][vehicleId][self.best_sol['steps'][vehicleId]] = nearest_station
            ##        self.best_sol['steps'][vehicleId] += 1
             #       current_node = nearest_station
             #       energyCapacity = 0
            nearest_station = self.find_nearest_charging_station(current_node)
            self.best_sol['tour'][vehicleId][self.best_sol['steps'][vehicleId]] = nearest_station
            self.best_sol['steps'][vehicleId] += 1
            current_node = nearest_station
            energyCapacity = 0
                #return nearest_station`
     
    
    def update_pheromones(self):
        """Aktualizácia feromónov na základe získaných riešení."""
        # Odparovanie feromónov
        for i in range(self.EVRP.ACTUAL_PROBLEM_SIZE):
            for j in range(self.EVRP.ACTUAL_PROBLEM_SIZE):
                self.pheromone_matrix[i][j] *= (1 - self.evaporation_rate)

        # Ukladanie nového feromónu pre aktuálne najlepšiu trasu
        for vehicle_id in range(self.num_vehicles):
            for step in range(self.best_sol['steps'][vehicle_id] - 1):
                from_node = self.best_sol['tour'][vehicle_id][step]
                to_node = self.best_sol['tour'][vehicle_id][step + 1]
                self.pheromone_matrix[from_node][to_node] += self.pheromone_deposit / self.best_sol['tour_length']

