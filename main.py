
from population import generate_initial_population
from fitness import FitnessEvaluator
from ga_runner import run_ga
import pandas as pd
import time
import numpy as np
import matplotlib.pyplot as plt
from utils import verify_solution_feasibility , print_chromosome_assignments
'''
data = {
    'Container': [1, 2, 3, 4, 5, 6],
    'Length': [2, 4, 2, 5, 10, 4],
    'Position': [57, 63, 58, 49, 26, 71],
    'Destination' : [2,2,2,1,1,2]
}

data_2 = {
    'Truck': [1, 2,3,4,5],
    'Destination': [1, 1,2,2,2],
    'Cost': [624,624, 479,479,479]
}
Truck_cost_df = pd.DataFrame(data_2)
data_containers = {
    'Instance': [12, 12, 12, 12, 12, 12],
    'ContainerID': [1, 2, 3, 4, 5, 6],
    'Length': [2, 4, 2, 5, 5, 4],
    'Position': [57, 63, 58, 49, 26, 71],
    'Destination': [2, 2, 2, 1, 1, 2]
}

data_trucks = {
    'Instance': [12, 12, 12, 12, 12],
    'TruckID': [1, 2, 3, 4, 5],
    'Destination': [1, 1, 2, 2, 2],
    'Cost': [624, 624, 479, 479, 479],
    'Capacity': [6, 6, 6, 6, 6],
    'DockPosition': [1, 1, 4, 4, 2]
}

data_dock = {
    'Instance': [12, 12, 12, 12, 12],
    'DockID': [1, 2, 3, 4, 5],
    'Position': [5, 1, 3, 2, 4]
}
containers_df = pd.DataFrame(data_containers)
trucks_df = pd.DataFrame(data_trucks)
docks_df = pd.DataFrame(data_dock)
#containers_df = pd.DataFrame(data)
'''
#Charger les données
containers_df = pd.read_csv("C:/Users/Taieb/Algo_genetique/containers_all.csv")
trucks_df = pd.read_csv("C:/Users/Taieb/Algo_genetique/trucks_all.csv")
docks_df = pd.read_csv("C:/Users/Taieb/Algo_genetique/docks_all.csv")
#truck_cost_df = pd.read_csv("truck_cost.csv")
# Choisir une instance spécifique
INSTANCE_ID = 12

# Filtrer les DataFrames pour cette instance
containers_df_instance = containers_df[containers_df["Instance"] == INSTANCE_ID].copy()
trucks_df_instance = trucks_df[trucks_df["Instance"] == INSTANCE_ID].copy()
docks_df_instance = docks_df[docks_df["Instance"] == INSTANCE_ID].copy()

# Générer population
initial_population_10 = generate_initial_population(10, containers_df_instance, trucks_df_instance, docks_df_instance, instance_id=12)
#initial_population_50 = generate_initial_population(50, containers_df, trucks_df, docks_df, instance_id=12)
#initial_population_100 = generate_initial_population(100, containers_df, trucks_df, docks_df, instance_id=12)
#initial_population_30 = generate_initial_population(20, containers_df, trucks_df, docks_df, instance_id=12)
# Fitness
fitness_eval = FitnessEvaluator(containers_df_instance, trucks_df_instance, C_E=0.5)

# Lancer GA
'''best_chrom, best_fit, history = run_ga(
    initial_population_50,
    fitness_eval,
    num_docks=len(docks_df),
    num_generations=100
)'''
'''best_chrom, best_fit, history = run_ga(
    initial_population_100,
    fitness_eval,
    num_docks=len(docks_df),
    num_generations=100
)'''


start_time = time.time()  # ⏱️ Début du chronométrage
best_chrom, best_fit, history = run_ga(
    initial_population_10,
    fitness_eval,
    num_docks=len(docks_df),
    num_generations=50
)

end_time = time.time()  # ⏱️ Fin du chronométrage
diversity=len(set(map(str, initial_population_10)))
diversity_ratio = diversity / len(initial_population_10)
import sys
sys.stdout.flush()

execution_time = end_time - start_time
print(f"Temps d'exécution : {execution_time:.3f} secondes")

print("\nMeilleur Chromosome trouvé :", best_chrom)
print("Fitness du meilleur :", best_fit)
#print chromozome
'''for idx, chromosome in enumerate(initial_population_10):
    print(f"Chromosome {idx+1}: longueur = {len(chromosome)}")
    if len(chromosome) <= 10:
        print(chromosome)'''
for idx, chromosome in enumerate(initial_population_10):
    print_chromosome_assignments(chromosome, trucks_df_instance)

for i, chrom in enumerate(initial_population_10):
    print(f"Chromosome {i+1}:")
    for j in range(0, len(chrom), 4):
        print(f"  Truck {j//4 + 1}: {chrom[j]}")

penalty, _ = fitness_eval.calculate_penalties(best_chrom, trucks_df_instance, containers_df_instance, 12)
f1 = fitness_eval.calculate_truck_cost_f1(best_chrom)
f2 = fitness_eval.calculate_energy_cost_f2(best_chrom)
fitness_no_penalty = fitness_eval.W1 * f1 + fitness_eval.W2 * f2

print("\n=== Final Best Chromosome ===")
print(f"Truck cost (F1): {f1}")
print(f"Energy cost (F2): {f2}")
print(f"Penalty: {penalty}")
print(f"Total fitness (with penalty): {fitness_no_penalty + penalty}")
print(f"Fitness without penalty: {fitness_no_penalty}")

#verify faisable solutions in initial population
'''for idx, chromosome in enumerate(initial_population_10):
    feasible, errors = verify_solution_feasibility(chromosome, trucks_df, containers_df, instance_id=12)
    print(f"\nChromosome {idx+1} : {' Faisable' if feasible else ' Non faisable'}")
    if not feasible:
        for err in errors:
            print("   ", err)'''


