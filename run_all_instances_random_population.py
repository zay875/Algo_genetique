
# run_all_instances.py
import pandas as pd
import time
from population import generate_initial_population
from fitness import FitnessEvaluator
from ga_runner import run_ga
from utils import print_chromosome_assignments

# Charger les CSV (chemins relatifs)
containers_df = pd.read_csv("containers_all.csv")
trucks_df = pd.read_csv("trucks_all.csv")
docks_df = pd.read_csv("docks_all.csv")

# Récupérer toutes les instances existantes
instances = sorted(containers_df["Instance"].unique())

results = []  # pour stocker les résultats

for instance_id in instances:
    print(f"\n🚀=== Instance {instance_id} ===")

    # Filtrage des données
    cont_i = containers_df[containers_df["Instance"] == instance_id].copy()
    trucks_i = trucks_df[trucks_df["Instance"] == instance_id].copy()
    docks_i = docks_df[docks_df["Instance"] == instance_id].copy()

    # Génération population initiale
    population = generate_initial_population(
        pop_size=10,
        containers_df=cont_i,
        trucks_df=trucks_i,
        docks_df=docks_i,
        instance_id=instance_id,ratio_binpacking=0.0
    )

    # Évaluateur de fitness
    fitness_eval = FitnessEvaluator(cont_i, trucks_i, C_E=0.5)

        # Exécution du GA
    start_time = time.time()
    best_chrom, best_fit, history = run_ga(
        population,
        fitness_eval,
        cont_i,
        trucks_i,
        instance_id,
        len(docks_i),
        num_generations=20
)


    exec_time = time.time() - start_time


    # Résultats détaillés
    print(f"⏱ Temps : {exec_time:.2f}s | Fitness = {best_fit}")
    results.append({
        "Instance": instance_id,
        "BestFitness": best_fit,
        "ExecutionTime(s)": round(exec_time, 3),
        "PopulationSize": len(population),
        "Generations": 20
    })

# Sauvegarder le résumé global


results_df = pd.DataFrame(results)
results_df.to_csv("results_summary_ramdom_pop.csv", index=False)
print("\n✅ Tous les résultats enregistrés dans results_summary_random_pop.csv")
