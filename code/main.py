import sys
from EVRP import *
from stats import *
from heuristic import *

def start_run(r, EVRP):
    """Inicializuje beh heuristického algoritmu."""
    random_seed = r
    EVRP.init_evals()
    EVRP.init_current_best()
    print(f"Run: {r} with random seed {random_seed}")

def end_run(r, EVRP, Stats, Heu):
    """Získava pozorovanie behu heuristického algoritmu."""
    current_best = EVRP.get_current_best()
    #evaluations = EVRP.get_evals()
    Stats.get_mean(r - 1, current_best)
    print(f"End of run {r} with best solution quality {current_best}\n")
    #print(f"bets:{Heu.best_sol}")

#def termination_condition(EVRP):
#    """Nastavuje ukončovaciu podmienku heuristického algoritmu."""
#    return EVRP.get_evals() >= EVRP.TERMINATION

def main():
    """Hlavná funkcia."""
    global problem_instance
    # Krok 1
    problem_instance = sys.argv[1]  # predať názov súboru .evrp ako argument
    evrp = EVRP()
    evrp.read_problem(problem_instance)

    # Krok 2
    stats = Stats(evrp)
    stats.open_stats()
    start_run(1, evrp)
    heuristic = Herusitic(evrp,4)
    heuristic.initialize_heuristic()
    
    for run in range(1, stats.MAX_TRIALS + 1):
        # Krok 3
        heuristic.run_aco(stats)
        
        # Krok 4
        #while not termination_condition(evrp):
        #    heuristic.run_heuristic()

        # Krok 5
        end_run(run, evrp, stats, heuristic)
    #print(heuristic.best_sol)
    # Krok 6
    stats.close_stats()

    # Uvoľnenie pamäte
    stats.free_stats()
    #heuristic.free_heuristic()
    evrp.free_EVRP()

if __name__ == "__main__":
    main()
