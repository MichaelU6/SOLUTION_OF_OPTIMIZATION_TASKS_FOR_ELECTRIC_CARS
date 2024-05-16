import random
import math
from EVRP import *

class Herusitic():
    def __init__(self, EVRP):
        self.best_sol = None  # pozri heuristic.hpp pre štruktúru riešenia
        self.EVRP = EVRP

    def initialize_heuristic(self):
        """Inicializácia štruktúry pre heuristický algoritmus."""
        #global best_sol
        self.best_sol = {'tour': [0] * (self.EVRP.NUM_OF_CUSTOMERS + 1000), 'id': 1, 'steps': 0, 'tour_length': math.inf}

    def run_heuristic(self):
        """Implementácia heuristického algoritmu."""
        #global best_sol
        # v kazdom behu spustim mravvce pre vsetkych a najdem najlepsie riesenia 3 napr., v amtici hrany zaznacit. Ci vahujem hrany zistit. Ked hladam finalnu cestu tak idem cez fer maticu
        # vyrabam feromonovu maticu ako vysledok, pri kazdom behu ju nakonci zaktualizujem
        # vzdy vyberiem pre kazdeho mravca nejakym zvolenym spoobom kde je aj fer matica celu cestu a na konci vyberam najlepsich mravcov
        
        # Generovanie náhodného riešenia pre heuristiku
        r = list(range(0, self.EVRP.NUM_OF_CUSTOMERS + 1))
        random.shuffle(r)

        energy_temp = 0.0
        capacity_temp = 0.0
        charging_station = None

        self.best_sol['steps'] = 0
        self.best_sol['tour_length'] = math.inf

        self.best_sol['tour'][0] = self.EVRP.DEPOT
        self.best_sol['steps'] += 1

        i = 0
        while i < self.EVRP.NUM_OF_CUSTOMERS:
            from_node = self.best_sol['tour'][self.best_sol['steps'] - 1]
            to_node = r[i]

            if (capacity_temp + self.EVRP.get_customer_demand(to_node) <= self.EVRP.MAX_CAPACITY and
                    energy_temp + self.EVRP.get_energy_consumption(from_node, to_node) <= self.EVRP.BATTERY_CAPACITY):
                capacity_temp += self.EVRP.get_customer_demand(to_node)
                energy_temp += self.EVRP.get_energy_consumption(from_node, to_node)
                self.best_sol['tour'][self.best_sol['steps']] = to_node
                self.best_sol['steps'] += 1
                i += 1
            elif capacity_temp + self.EVRP.get_customer_demand(to_node) > self.EVRP.MAX_CAPACITY:
                capacity_temp = 0.0
                energy_temp = 0.0
                self.best_sol['tour'][self.best_sol['steps']] = self.EVRP.DEPOT
                self.best_sol['steps'] += 1
            elif energy_temp + self.EVRP.get_energy_consumption(from_node, to_node) > self.EVRP.BATTERY_CAPACITY:
                charging_station = random.randint(self.EVRP.NUM_OF_CUSTOMERS + 1, self.EVRP.ACTUAL_PROBLEM_SIZE - 1)
                if self.EVRP.is_charging_station(charging_station):
                    energy_temp = 0.0
                    self.best_sol['tour'][self.best_sol['steps']] = charging_station
                    self.best_sol['steps'] += 1
            else:
                capacity_temp = 0.0
                energy_temp = 0.0
                self.best_sol['tour'][self.best_sol['steps']] = self.EVRP.DEPOT
                self.best_sol['steps'] += 1

        # Uzavretie trasy návratu späť do depa
        if self.best_sol['tour'][self.best_sol['steps'] - 1] != self.EVRP.DEPOT:
            self.best_sol['tour'][self.best_sol['steps']] = self.EVRP.DEPOT
            self.best_sol['steps'] += 1

        self.best_sol['tour_length'] = self.EVRP.fitness_evaluation(self.best_sol['tour'][:self.best_sol['steps']])

    def free_heuristic(self):
        """Uvoľnenie pamäťových štruktúr."""
        del self.best_sol['tour']
