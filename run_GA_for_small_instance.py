# run_all_instances.py
import pandas as pd
import time
from population import generate_initial_population
from fitness import FitnessEvaluator
from ga_runner import run_ga
from utils import print_chromosome_assignments

# Charger les CSV (chemins relatifs)
'''
containers_df = pd.read_csv("containers_all.csv")
trucks_df = pd.read_csv("trucks_all.csv")
docks_df = pd.read_csv("docks_all.csv")
'''
# Récupérer toutes les instances existantes
#instances = sorted(containers_df["Instance"].unique())
data_container = {
    'ContainerID': [1, 2, 3],
    'Length': [2, 4, 2],
    'Position': [57, 63, 58],
    'Destination' : [2,2,2],
    'Instance': [1, 1, 1]
}

data_truck = {
    'TruckID': [1, 2],
    'Destination': [1,2],
    'Cost': [624 ,479],
    'Capacity':[6,6],
    'DockPosition':[1,2],
    'Instance': [1, 1]
}
data_docks={
'DockID':[1,2],
'Position':[1,2],'Instance': [1, 1]
}
instance_id = 1
containers_df = pd.DataFrame(data_container)
trucks_df = pd.DataFrame(data_truck)
docks_df = pd.DataFrame(data_docks)
results = []  # pour stocker les résultats
print("→ Avant génération de la population")

    # Génération population initiale
population = generate_initial_population(
pop_size=10,
containers_df=containers_df,
trucks_df=trucks_df,
docks_df=docks_df,
instance_id=instance_id,
ratio_binpacking=0.2
    )
print("→ Après génération de la population")

print("hi")
    # Évaluateur de fitness
fitness_eval = FitnessEvaluator(containers_df, trucks_df, C_E=0.5)

        # Exécution du GA
start_time = time.time()
best_chrom, best_fit,history = run_ga(
    population,
    fitness_eval,
    containers_df,
    trucks_df,
    instance_id,
    len(docks_df),
    num_generations=20
)  
print("hello") 
penalty_value, _ = fitness_eval.calculate_penalties(best_chrom, trucks_df, containers_df,instance_id)
cost = fitness_eval.calculate_truck_cost_f1(best_chrom)
energy = fitness_eval.calculate_energy_cost_f2(best_chrom)
true_fitness = cost + fitness_eval.C_E * energy  # "real" fitness (without penalties)

exec_time = time.time() - start_time
print(f"meuilleur chromomosome : {best_chrom}")


    # Résultats détaillés
print(f"⏱ Temps : {exec_time:.2f}s | Fitness = {true_fitness}")
results.append({
        "Instance": instance_id,
        "BestFitness": true_fitness,
        "ExecutionTime(s)": round(exec_time, 3),
        "PopulationSize": len(population),
        "Generations": 20
    })

# Sauvegarder le résumé global

print("salut")
results_df = pd.DataFrame(results)
results_df.to_csv("results_summary_GA_for_small_instance.csv", index=False)
print("\n✅ Tous les résultats enregistrés dans results_summary_GA_for_small_instance.csv")
