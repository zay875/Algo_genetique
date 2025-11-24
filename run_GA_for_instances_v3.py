# run_all_instances.py
import pandas as pd
import time
from population import generate_initial_population
from fitness import FitnessEvaluator
from ga_runner import run_ga
from utils import print_chromosome_assignments
from utils import verify_solution_feasibility
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
'''
data_container = {
    'ContainerID': [1, 2, 3, 4, 5, 6, 7, 8],
    'Length': [2, 5, 3, 5, 5, 5, 4, 5],
    'Position': [46, 24, 55, 6, 70, 24, 57, 17],
    'Destination': [1, 2, 3, 3, 3, 3, 1, 1],
    'Instance': [2, 2, 2, 2, 2, 2, 2, 2]
}

data_truck = {
    'TruckID': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11,12],
    'Destination': [2, 2, 1, 1, 2, 2, 1, 3, 2, 3, 3,3],
    'Cost': [751, 751, 770, 770, 751, 751, 770, 766, 751, 766, 766,766],
    'Capacity': [6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6,6],
    'DockPosition': [2, 3, 2, 2, 1, 2, 3, 3, 5, 3, 5,1],
    'Instance': [2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2,2]
}


data_docks = {
    'DockID': [1, 2, 3, 4, 5],
    'Position': [4, 5, 2, 1, 3],
    'Instance': [2, 2, 2, 2, 2]
}


instance_id = 2
'''

#containers_df = pd.read_csv("petite_instances/coantainers.csv")
#trucks_df = pd.read_csv("petite_instances/trucks.csv")
#docks_df = pd.read_csv("petite_instances/docks.csv")
containers_df = pd.read_csv("instances_v3/containers_all.csv")
trucks_df = pd.read_csv("instances_v3/trucks_modifies.csv")
docks_df = pd.read_csv("instances_v3/docks_all.csv")

num_generations= 5
# Récupérer toutes les instances existantes
instances = sorted(containers_df["Instance"].unique())

results = []  # pour stocker les résultats

for instance_id in instances:
    if instance_id > 10:
        continue
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
        ratio_binpacking=0.8
    )
    print(f"→ Après génération de la population pour l'instance {instance_id}")
    print(f"the result of generating the population{population}")
    print("hi")
    print(f"Population initiale : {len(population)} individus")
    '''
        print("=== Vérification de faisabilité de la population initiale")
    for i, chrom in enumerate(population):
        feasible, errors = verify_solution_feasibility(chrom, trucks_df, containers_df, instance_id)
        print(f"Chromosome {i} : {'OK' if feasible else 'NON FAISABLE'}")
        if not feasible:
            print("  Erreurs :", errors)
    if not population:
        raise ValueError("❌ Population vide — vérifie process_instance ou generate_random_chromosome.")

    '''

    # Évaluateur de fitness (weights W1 and W2 explicit for clarity)
    fitness_eval = FitnessEvaluator(containers_df, trucks_df, C_E=0.5, W1=0.5, W2=0.5)
    num_docks = len(docks_df[docks_df["Instance"] == instance_id])
    # Exécution du GA
    start_time = time.time()
    best_chrom, best_fit,history,new_population= run_ga(
        population,
        fitness_eval,
        containers_df,
        trucks_df,
        instance_id,
        num_docks,
        num_generations=5
    )  
    #print(f"the result of crossover and mutation, la longeure {len(new_population)}{new_population}")

    '''
    
    print("=== Vérification de faisabilité de la population finale ===")
    for i, chrom in enumerate(new_population):
        feasible, errors = verify_solution_feasibility(chrom, trucks_df, containers_df, instance_id)
        print(f"Chromosome {i} : {'OK' if feasible else 'NON FAISABLE'}")
        if not feasible:
            print("  Erreurs :", errors)
    '''
    print(f"the result after GA{new_population}")
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
results_df.to_csv("results_summary_GA_instance_3.csv", index=False)
print("\n✅ Tous les résultats enregistrés dans results_summary_GA_instance_3.csv")
