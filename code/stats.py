import math
from EVRP import *

class Stats():
    def __init__(self, EVRP):     
        # Použité na výstup offline výkonu a diverzitu populácie
        self.log_performance = None
        self.perf_filename = None
        self.perf_of_trials = None
        self.MAX_TRIALS	= 20 
        self.EVRP = EVRP									

    def open_stats(self):
        """Inicializácia a otvorenie výstupných súborov."""
        #global perf_of_trials, log_performance, perf_filename

        self.perf_of_trials = [0.0] * self.MAX_TRIALS

        # Pre výkon
        self.perf_filename = f"stats.{self.EVRP.problem_instance}.txt"
        self.log_performance = open(self.perf_filename, "a")

    def get_mean(self, r, value):
        """Nastavenie priemerných hodnôt."""
        #global perf_of_trials
        self.perf_of_trials[r] = value

    def mean(self, values):
        """Výpočet priemeru."""
        return sum(values) / len(values)

    def stdev(self, values, average):
        """Výpočet štandardnej odchýlky."""
        if len(values) <= 1:
            return 0.0
        dev = sum((x - average) ** 2 for x in values)
        return math.sqrt(dev / (len(values) - 1))

    def best_of_vector(self, values):
        """Nájdenie najlepšej hodnoty v poli."""
        return min(values)

    def worst_of_vector(self, values):
        """Nájdenie najhoršej hodnoty v poli."""
        return max(values)

    def close_stats(self):
        """Uzatvorenie a výpis štatistík."""
        #global perf_of_trials, log_performance

        for value in self.perf_of_trials:
            self.log_performance.write(f"{value:.2f}\n")

        perf_mean_value = self.mean(self.perf_of_trials)
        perf_stdev_value = self.stdev(self.perf_of_trials, perf_mean_value)

        self.log_performance.write(f"Mean {perf_mean_value}\t ")
        self.log_performance.write(f"\tStd Dev {perf_stdev_value}\t \n")
        self.log_performance.write(f"Min: {self.best_of_vector(self.perf_of_trials)}\t \n")
        self.log_performance.write(f"Max: {self.worst_of_vector(self.perf_of_trials)}\t \n")

        self.log_performance.close()

    def free_stats(self):
        """Uvoľnenie pamäťových štruktúr."""
        #global perf_of_trials
        del self.perf_of_trials
