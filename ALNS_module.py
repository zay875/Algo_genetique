# run_all_instances.py
import pandas as pd
import time
from population import generate_initial_population
from fitness import FitnessEvaluator
from ga_runner import run_ga
from utils import print_chromosome_assignments



import matplotlib.pyplot as plt
import numpy as np
from mabwiser.mab import LearningPolicy

from alns import ALNS
from alns.accept import *
from alns.select import *
from alns.stop import *
SEED = 42
#
np.random.seed(SEED)
n = 100
p = np.random.randint(1, 100, size=n)
w = np.random.randint(10, 50, size=n)
W = 1_000




# Récupérer toutes les instances existantes
#instances = sorted(containers_df["Instance"].unique())
data_container = {
    'ContainerID': [1, 2, 3,4],
    'Length': [5,4,5,4],
    'Position': [25, 7, 29, 28],
    'Destination' : [2,1, 2,2],
    'Instance': [1,1,1,1]
}

data_truck = {
    'TruckID': [1, 2,3,4,5,6 ,7,8,9,10],
    'Destination': [2,1,2,1,1,1,1,2,2,1],
    'Cost': [705,608,705,608,608,608,608,705,705,608],
    'Capacity':[6,6,6,6,6,6,6,6,6,6],
    'DockPosition':[2,4,3,3,2,4,5,2,2,4],
    'Instance': [1,1,1,1,1,1,1,1,1,1]
}
data_docks={ 
'DockID':[1,2,3,4],
'Position':[4,7,6,2],'Instance': [1,1,1,1]
}
instance_id = 2
containers_df = pd.DataFrame(data_container)
trucks_df = pd.DataFrame(data_truck)
docks_df = pd.DataFrame(data_docks)
results = []  # pour stocker les résultats
print("→ Avant génération de la population")
#grouped_containers = group_containers_by_destination(containers_df)
#check the trucks instances for capacity
#trucks_df = ensure_capacity(trucks_df, grouped_containers, instance_id)
# Génération population initiale
population = generate_initial_population(
    pop_size=10,
    containers_df=containers_df,
    trucks_df=trucks_df,
    docks_df=docks_df,
    instance_id=instance_id,
    ratio_binpacking=0.2
)

if not population:
    raise ValueError("❌ Population vide — vérifie process_instance ou generate_random_chromosome.")

# Évaluateur de fitness (weights W1 and W2 explicit for clarity)
fitness_eval = FitnessEvaluator(containers_df, trucks_df, C_E=0.5, W1=0.5, W2=0.5)

# Exécution du GA
start_time = time.time()
best_chrom, best_fit,history,new_population,fitness_values= run_ga(
    population,
    fitness_eval,
    containers_df,
    trucks_df,
    instance_id,
    len(docks_df),
    num_generations=5
)  
print(f"the result of crossover and mutation{new_population}")
print(f"fitness values for each population{fitness_values}")
print("hello") 
#penalty_value, _ = fitness_eval.calculate_penalties(best_chrom, trucks_df, containers_df, instance_id)
cost = fitness_eval.calculate_truck_cost_f1(best_chrom)
energy = fitness_eval.calculate_energy_cost_f2(best_chrom)

# Final fitness using configured weights and including penalties
final_fitness = fitness_eval.calculate_fitness(best_chrom, instance_id, include_penalty=False)
'''
exec_time = time.time() - start_time
print(f"meuilleur chromomosome : {best_chrom}")

# Résultats détaillés
print(f"⏱ Temps : {exec_time:.2f}s | Fitness = {final_fitness}")
results.append({
        "Instance": instance_id,
        "BestFitness": final_fitness,
        "ExecutionTime(s)": round(exec_time, 3),
        "PopulationSize": len(population),
        "Generations": 20,
        "best_chromosome": best_chrom    })

# Sauvegarder le résumé global

print("salut")
results_df = pd.DataFrame(results)
results_df.to_csv("results_summary_GA_for_small_instance_2.csv", index=False)
print("\n✅ Tous les résultats enregistrés dans results_summary_GA_for_small_instance_2.csv")



'''
import copy
import math

class LogisticsState:
    """
    Represents one solution (state) in the cross-dock logistics problem.
    Each state assigns containers to trucks and tracks total cost.
    """

    def __init__(self, assignments, truck_capacities, container_weights, energy_matrix):
        """
        Parameters
        ----------
        assignments : dict[int, int]
            Mapping container_id -> truck_id.
        truck_capacities : dict[int, float]
            Truck capacities {truck_id: max_capacity}.
        container_weights : dict[int, float]
            Container weights {container_id: weight}.
        energy_matrix : dict[(container_id, truck_id), float]
            Energy cost of loading a container into a given truck.
        """
        self.assignments = assignments
        self.truck_capacities = truck_capacities
        self.container_weights = container_weights
        self.energy_matrix = energy_matrix

        # Derived values
        self.truck_loads = self._compute_truck_loads()
        self.energy_cost = self._compute_energy_cost()
        self.num_trucks_used = len(set(assignments.values()))

    # -------------- cost and feasibility -----------------

    def _compute_truck_loads(self):
        """Compute how much load is currently assigned to each truck."""
        loads = {t: 0.0 for t in self.truck_capacities}
        for c, t in self.assignments.items():
            loads[t] += self.container_weights[c]
        return loads

    def _compute_energy_cost(self):
        """Compute total energy cost of all current assignments."""
        return sum(self.energy_matrix[(c, t)] for c, t in self.assignments.items())

    def is_feasible(self):
        """Return True if all trucks respect capacity constraints."""
        return all(
            self.truck_loads[t] <= self.truck_capacities[t] + 1e-6
            for t in self.truck_capacities
        )

    # -------------- ALNS interface methods -----------------

    def objective(self):
        """
        Return a scalar cost for ALNS to minimize.
        You can tune alpha/beta weights to emphasize one objective more.
        """
        alpha = 0.6  # weight for trucks used
        beta = 0.4   # weight for energy cost
        return alpha * self.num_trucks_used + beta * self.energy_cost

    def copy(self):
        """Return a deep copy of this state (used by ALNS)."""
        return copy.deepcopy(self)

    def __repr__(self):
        return (f"<LogisticsState cost={self.objective():.2f}, "
                f"trucks={self.num_trucks_used}, "
                f"energy={self.energy_cost:.2f}>")



# Percentage of items to remove in each iteration
destroy_rate = 0.25
class KnapsackState:
    """
    Solution class for the 0/1 knapsack problem. It stores the current
    solution as a vector of binary variables, one for each item.
    """

    def __init__(self, x: np.ndarray):
        self.x = x

    def objective(self) -> int:
        # Negative p since ALNS expects a minimisation problem.
        return -p @ self.x

    def weight(self) -> int:
        return w @ self.x
    
def to_destroy(state: KnapsackState) -> int:
    return int(destroy_rate * state.x.sum())

#first a simple distroy function (random)
def random_remove(state: KnapsackState, rng):
    probs = state.x / state.x.sum()
    #choose the rank in the solution and remove from range
    to_remove = rng.choice(np.arange(n), size=to_destroy(state), p=probs)

    assignments = state.x.copy()
    assignments[to_remove] = 0

    return KnapsackState(x=assignments)