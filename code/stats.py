import math
import random
import matplotlib.pyplot as plt
from EVRP import *

class Stats():
    def __init__(self, EVRP):     
        self.log_performance = None
        self.perf_filename = None
        self.perf_of_trials = None
        self.MAX_TRIALS = 20 
        self.EVRP = EVRP									

    def open_stats(self):
        self.perf_of_trials = [0.0] * self.MAX_TRIALS
        self.perf_filename = f"stats.{self.EVRP.problem_instance}.txt"
        self.log_performance = open(self.perf_filename, "a")

    def get_mean(self, r, value):
        self.perf_of_trials[r] = value

    def mean(self, values):
        return sum(values) / len(values)

    def stdev(self, values, average):
        if len(values) <= 1:
            return 0.0
        dev = sum((x - average) ** 2 for x in values)
        return math.sqrt(dev / (len(values) - 1))

    def best_of_vector(self, values):
        return min(values)

    def worst_of_vector(self, values):
        return max(values)

    def close_stats(self):
        for value in self.perf_of_trials:
            self.log_performance.write(f"{value:.2f}\n")

        perf_mean_value = self.mean(self.perf_of_trials)
        perf_stdev_value = self.stdev(self.perf_of_trials, perf_mean_value)

        self.log_performance.write(f"Mean {perf_mean_value:.2f}\t ")
        self.log_performance.write(f"\tStd Dev {perf_stdev_value:.2f}\t \n")
        self.log_performance.write(f"Min: {self.best_of_vector(self.perf_of_trials)}\t \n")
        self.log_performance.write(f"Max: {self.worst_of_vector(self.perf_of_trials)}\t \n")

        self.log_performance.close()
        self.plot_stats()

    def plot_stats(self):
        """Vytvorenie grafu výkonu."""
        plt.figure(figsize=(10, 6))
        plt.plot(range(self.MAX_TRIALS), self.perf_of_trials, marker='o', linestyle='-', color='b', label='Performance')
        plt.title('ACO Performance over Trials')
        plt.xlabel('Trial Number')
        plt.ylabel('Performance Value')
        plt.axhline(self.mean(self.perf_of_trials), color='r', linestyle='--', label='Mean Performance')
        plt.legend()
        plt.grid()
        plt.savefig(f"performance_plot.{self.EVRP.problem_instance}.png")
        plt.close()

    def free_stats(self):
        del self.perf_of_trials