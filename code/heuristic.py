import sys
import math
import random
from EVRP import *
from stats import *

class Herusitic:
    def __init__(self, EVRP, alpha=0.5, beta=3.0, evaporation_rate=0.5, pheromone_deposit=100.0, iterations=20):
        self.best_sol = None  # Najlepšie riešenie
        self.solution = None  # Najlepšie riešenie
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

    def initialize(self):
        self.best_sol = {
            'tour': [[] for _ in range(self.num_vehicles)], 
            'steps': [0] * self.num_vehicles, 
            'tour_length': math.inf
        }
        
    def initialize_heuristic(self):
        """Inicializácia štruktúry pre heuristiku."""
        self.solution = {
            'tour': [[] for _ in range(self.num_vehicles)], 
            'steps': [0] * self.num_vehicles, 
            'tour_length': math.inf
        }
        
    # Toto je spustenie iteracie pre mravce v jednej iteracii od ktorych chcem vytiahnut najlepsiu cestu
    def run_aco(self, stats):
        self.writeParameter()
     
        for iteration in range(self.iterations):
            self.run_heuristic()  # Pošlem jedného mravca obsluzit vsetky auta so vsetkymi zakaznikmy

            # ak
            if self.solution['tour_length'] < self.best_sol['tour_length']:
                self.best_sol['tour'] = [list(route) for route in self.solution['tour']]
                self.best_sol['steps'] = list(self.solution['steps'])
                self.best_sol['tour_length'] = self.solution['tour_length']
            
            # do štatistík zapíšem riešenie tejto iterácií, jeho dĺžku
            #stats.get_mean(iteration, self.best_sol['tour_length'])

            #print(f"Iteration {iteration + 1}, Best Tour Length: {global_best['tour_length']}")
            
        # Ked dobehnu vsetky mravce konkretne 10, podla toho kto mal najkratsiu cestu updatnem feromonovu maticu
        self.update_pheromones()
        
        return self.best_sol

    # Toto je len pre jedneho mravca
    def run_heuristic(self):
        """Spustenie jedneho mravca a viacerými vozidlami."""
        self.initialize_heuristic()
        
        """Zoznam kde su id vsetkych zakaznikov tak ako v datach, 0 je depo, preto zacinam od 1"""
        customersListIds = list(range(1, self.EVRP.NUM_OF_CUSTOMERS + 1))
        # Vsetci zakaznici idu
        for vehicle_id in range(self.num_vehicles):
            newCustomerCopy = self.construct_solution(vehicle_id, customersListIds)
            if newCustomerCopy is False:
                break
            customersListIds = newCustomerCopy
        # Ked vygenerujem pre vsetky auta jedno riesenie porovnam ho ci nieje najlepsie. Vlastne je to riesenie jedneho mravca
        if len(customersListIds) == 0:
            flattened_list = [item for sublist in self.solution['tour'] for item in sublist[:-1]]
            flattened_list.append(0)
            tour_length = self.EVRP.fitness_evaluation(flattened_list)
            self.solution['tour_length'] = tour_length

    def construct_solution(self, vehicle_id, customersListIdsDontService):
        """Konštrukcia riešenia pre konkrétne vozidlo."""
        
        energy_temp = 0.0
        capacity_temp = 0.0

        self.solution['steps'][vehicle_id] = 0
        self.solution['tour'][vehicle_id].append(self.EVRP.DEPOT)  # Začiatok v depe = 0
        
        nodeForCheckLoop = -1
        
        i = 1
        # Ked skoncim som v depe zarucene
        while i == 1:
            # Vyberiem podla toho ktory krok som urobil kde som. Id vrcholu kde som.
            #from_node_for_capacity = self.select_actual_node(self.solution['tour'][vehicle_id], self.solution['steps'][vehicle_id])
            from_node = self.solution['tour'][vehicle_id][self.solution['steps'][vehicle_id]]
            # Pozriem ci som nemal ten isty vrchol naposledy ak ano tak som sa dostal do nekonecneho cyklu takze to zavriem
            if from_node == nodeForCheckLoop:
                return False
            else:
                nodeForCheckLoop = from_node
            # Ak som uz obsluzil vsetkych zakaznikov tak chcem ist do depa a skoncit
            if len(customersListIdsDontService) == 0:
                self.find_path_in_depo(from_node, energy_temp, vehicle_id)
                i = 0
                break
            # Vyberiem ku ktoremu ZAKZANIKOVI chcem ist
            to_node = self.select_next_node(from_node, customersListIdsDontService)
            # Zistim kolko od zakaznika kotreho LEN planujejm obsluzit treba baterie k najblizsej nabijacke
            min_Battery = self.EVRP.get_energy_consumption(to_node, self.find_nearest_charging_station(to_node)) 
            # Ak ma vozidlo dost kapacity pre planovaneho zakaznika a dost baterii aby prisiel k zakaznikovi a k naajblizsej nabijacke
            # tak obsluzim zakaznika (miniem kapacitu, bateriu). Zapisem do cesty zakaznika a pridam krok a odstranim zakaznika z neobsluzenych zakaznikov.
            if (capacity_temp + self.EVRP.get_customer_demand(to_node) <= self.EVRP.MAX_CAPACITY and
                energy_temp + self.EVRP.get_energy_consumption(from_node, to_node) + min_Battery <= self.EVRP.BATTERY_CAPACITY):
                capacity_temp += self.EVRP.get_customer_demand(to_node)
                energy_temp += self.EVRP.get_energy_consumption(from_node, to_node)
                self.solution['tour'][vehicle_id].append(to_node)
                self.solution['steps'][vehicle_id] += 1
                customersListIdsDontService.remove(to_node)
            else:
                """Ked vozidlo nema dostatok miesta na obsluzenie vybreneho zakaznika alebo dost baterie poslem ho do depa/najblizsej stanice"""
                # Ak ide o kapacitu vozidla
                if capacity_temp + self.EVRP.get_customer_demand(to_node) > self.EVRP.MAX_CAPACITY:
                    # Ak mam dost baterie na navrat do depa
                    if energy_temp + self.EVRP.get_energy_consumption(from_node, self.EVRP.DEPOT) <= self.EVRP.BATTERY_CAPACITY:
                        self.solution['tour'][vehicle_id].append(self.EVRP.DEPOT)
                        self.solution['steps'][vehicle_id] += 1
                        i = 0
                    # Nema dost baterie na navrat do depa.
                    else:
                        # Dostanem sa do depa aj spotrebnymi zaznamami o krokoch a ceste
                        self.find_path_in_depo(from_node, energy_temp, vehicle_id)
                        i = 0
                # Ak nejde o kapacitu vozidla musi ist o malo baterie. Najdem nabijcaku. Prejdem na nabijacku a ulozim ze som na nabijacke.
                # a pridam jeden krok a nabijem vozidlo
                else:
                    charging_station = self.find_nearest_charging_station(from_node)
                    self.solution['tour'][vehicle_id].append(charging_station)
                    energy_temp = 0.0
                    self.solution['steps'][vehicle_id] += 1
                    
 
        #skontrolujem riesenie pre vozidlo ci je dokoncene a ci obsluzil vsektych zakaznikov (toto reba dokoncit aby neviplo apku)
        self.EVRP.check_solution(self.solution['tour'][vehicle_id][:self.solution['steps'][vehicle_id]+1])
        
        return customersListIdsDontService
    
    def select_actual_node(self, actualPath, steps):
        if actualPath[steps] > self.EVRP.NUM_OF_CUSTOMERS:
            return self.select_actual_node(actualPath, steps-1)
        else:
            return actualPath[steps]
        
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
        # Zistim kolko baterie je treba z vrhcolu kde som do depa
        distance_to_depo = self.EVRP.get_energy_consumption(current_node, self.EVRP.DEPOT)

        # Ak momentalna bateria vozidla staci do depa nastav dalsi bod mojej cesty depo a pridaj krok
        if self.EVRP.BATTERY_CAPACITY - energyCapacity >= distance_to_depo:
            self.solution['tour'][vehicleId].append(self.EVRP.DEPOT)
            self.solution['steps'][vehicleId] += 1
        else:
            # Ak nie je dosť energie, nájdi najbližšiu nabíjaciu stanicu. Presun sa nanu a pridaj krok
            nearest_station = self.find_nearest_charging_station(current_node)
            self.solution['tour'][vehicleId].append(nearest_station)
            self.solution['steps'][vehicleId] += 1
            # Pridam dalsi vrchol depo a pridam krok
            self.solution['tour'][vehicleId].append(self.EVRP.DEPOT)
            self.solution['steps'][vehicleId] += 1
     
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
                
    def writeParameter(self): 
        with open("parametre.txt", 'w') as file:
            file.write(f"Zoznam uzlov s id a súradnicami x a y: {self.EVRP.node_list}\n")
            file.write(f"Zoznam s id a požiadavkami zákazníkov: {self.EVRP.cust_demand}\n")
            file.write(f"Nabijacie stanice: {self.EVRP.charging_station}\n")
            file.write(f"Matica vzdialenosti: {self.EVRP.distances}\n")
            file.write(f"Problem size: {self.EVRP.problem_size}\n")
            file.write(f"Energy consuption: {self.EVRP.energy_consumption}\n")
            file.write(f"Depo: {self.EVRP.DEPOT}\n")
            file.write(f"Počet zákazníkov (bez depa): {self.EVRP.NUM_OF_CUSTOMERS}\n")
            file.write(f"Celkový počet zákazníkov, dobíjacích staníc a depa: {self.EVRP.ACTUAL_PROBLEM_SIZE}\n")
            file.write(f"Optimum: {self.EVRP.OPTIMUM}\n")
            file.write(f"NUM_OF_STATIONS: {self.EVRP.NUM_OF_STATIONS}\n")
            file.write(f"Maximálna energia vozidiel: {self.EVRP.BATTERY_CAPACITY}\n")
            file.write(f"Kapacita vozidiel: {self.EVRP.MAX_CAPACITY}\n")
            file.write(f"MIN_VEHICLES: {self.EVRP.MIN_VEHICLES}\n")
            file.write(f"evals: {self.EVRP.evals}\n")
            file.write(f"current_best: {self.EVRP.current_best}\n")

