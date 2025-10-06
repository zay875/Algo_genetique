
from population import generate_initial_population
from fitness import FitnessEvaluator
from ga_runner import run_ga
import pandas as pd
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
#containers_df = pd.DataFrame(data)

# Charger les données
containers_df = pd.read_csv("C:/Users/Taieb/Algo_genetique/containers_all (1).csv")
trucks_df = pd.read_csv("C:/Users/Taieb/Algo_genetique/trucks_all (1).csv")
docks_df = pd.read_csv("C:/Users/Taieb/Algo_genetique/docks_all (1).csv")
#truck_cost_df = pd.read_csv("truck_cost.csv")

# Générer population
initial_population_10 = generate_initial_population(10, containers_df, trucks_df, docks_df, instance_id=12)
#initial_population_50 = generate_initial_population(50, containers_df, trucks_df, docks_df, instance_id=12)
#initial_population_100 = generate_initial_population(100, containers_df, trucks_df, docks_df, instance_id=12)
#initial_population_200 = generate_initial_population(200, containers_df, trucks_df, docks_df, instance_id=12)
# Fitness
fitness_eval = FitnessEvaluator(containers_df, Truck_cost_df, C_E=1)

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
best_chrom, best_fit, history = run_ga(
    initial_population_10,
    fitness_eval,
    num_docks=len(docks_df),
    num_generations=50
)
import sys
sys.stdout.flush()


print("Diversité initiale :", len(set(map(str, initial_population_10))))

print("\nMeilleur Chromosome trouvé :", best_chrom)
print("Fitness du meilleur :", best_fit)
