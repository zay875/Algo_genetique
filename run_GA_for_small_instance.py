# run_all_instances.py
import pandas as pd
import time
from population import generate_initial_population
from fitness import FitnessEvaluator
from ga_runner import run_ga
from utils import print_chromosome_assignments
#from binpacking import ensure_capacity
#from binpacking import group_containers_by_destination

# Charger les CSV (chemins relatifs)
'''
containers_df = pd.read_csv("containers_all.csv")
trucks_df = pd.read_csv("trucks_all.csv")
docks_df = pd.read_csv("docks_all.csv")
'''
# Récupérer toutes les instances existantes
#instances = sorted(containers_df["Instance"].unique())
data_container = {
    'ContainerID': [1, 2, 3,4],
    'Length': [2, 5, 3 ,5],
    'Position': [38, 17, 48,28],
    'Destination' : [1,2,2,2],
    'Instance': [2,2 ,2,2]
}

data_truck = {
    'TruckID': [1, 2,3,4],
    'Destination': [1,1,2,3],
    'Cost': [608 ,608,705,504],
    'Capacity':[6,6,6,6],
    'DockPosition':[4,6,6,2],
    'Instance': [2,2,2,2]
}
data_docks={ 
'DockID':[1,2,3,4],
'Position':[4,7,6,2],'Instance': [2,2,2,2]
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
print("→ Après génération de la population")

print("hi")
print(f"Population initiale : {len(population)} individus")
if not population:
    raise ValueError("❌ Population vide — vérifie process_instance ou generate_random_chromosome.")

# Évaluateur de fitness (weights W1 and W2 explicit for clarity)
fitness_eval = FitnessEvaluator(containers_df, trucks_df, C_E=0.5, W1=0.5, W2=0.5)

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
#penalty_value, _ = fitness_eval.calculate_penalties(best_chrom, trucks_df, containers_df, instance_id)
cost = fitness_eval.calculate_truck_cost_f1(best_chrom)
energy = fitness_eval.calculate_energy_cost_f2(best_chrom)

# Final fitness using configured weights and including penalties
final_fitness = fitness_eval.calculate_fitness(best_chrom, instance_id, include_penalty=False)

# Print a clear breakdown to avoid confusion
print(f"cost of trucks (sum)           : {cost}")
print(f"cost of energy (sum)           : {energy}")
print(f"W1 (weight for cost)           : {fitness_eval.W1}")
print(f"W2 (weight for energy)         : {fitness_eval.W2}")
print(f"W1 * cost                      : {fitness_eval.W1 * cost}")
print(f"W2 * energy                    : {fitness_eval.W2 * energy}")
#print(f"penalty (if any)               : {penalty_value}")
print(f"Final fitness (W1*cost+W2*energy): {final_fitness}")

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
