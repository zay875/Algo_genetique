# run_all_instances.py
import pandas as pd
import time
from population import generate_initial_population
from fitness import FitnessEvaluator
from ga_runner import run_ga
from utils import print_chromosome_assignments
from binpacking import calculate_loading_times_df
import os
# Charger les CSV (chemins relatifs)
#utilisant les données génerer la deuxiéme fois avec les docks doublons corrigées
containers_df = pd.read_csv("instances_v3/containers_all.csv")
trucks_df = pd.read_csv("instances_v3/trucks_all.csv")
docks_df = pd.read_csv("instances_v3/docks_all.csv")

# Récupérer toutes les instances existantes
instances = sorted(containers_df["Instance"].unique())

results = []  # pour stocker les résultats

for instance_id in instances:
    # Filtrage des données (source "immuable" pour cette instance)
    cont_i_src  = containers_df[containers_df["Instance"] == instance_id].copy()
    trucks_i_src = trucks_df[trucks_df["Instance"] == instance_id].copy()
    docks_i_src  = docks_df[docks_df["Instance"] == instance_id].copy()

    # --- Génération population initiale (⚠️ NE PAS nommer le retour 'trucks_df') ---
    population= generate_initial_population(
        pop_size=50,
        containers_df=cont_i_src,
        trucks_df=trucks_i_src,
        docks_df=docks_i_src,
        instance_id=instance_id,
        ratio_binpacking=0.2
    )
    # Print initial population (first 5 individuals) to inspect reassignment/buffering
    print(f"Initial population size: {len(population)}")
    print("Initial population (first 5 chromosomes):")
    for i, indiv in enumerate(population[:5], start=1):
        print(f"  {i}: {indiv}")
    
    print(f"→ Après génération de la population pour l'instance {instance_id}")
    # Copies défensives pour le GA (évite toute mutation par référence)
    cont_i_ga  = cont_i_src.copy()
    trucks_i_ga = trucks_i_src.copy()
    docks_i_ga  = docks_i_src.copy()

    # --- Sanity checks avant GA ---
    assert not trucks_i_ga.empty, f"trucks_i_ga vide avant GA (instance {instance_id})"
    assert not cont_i_ga.empty, "containers vide"
    assert not docks_i_ga.empty, "docks vide"

    # Évaluateur de fitness
    fitness_eval = FitnessEvaluator(cont_i_ga, trucks_i_ga, C_E=0.5, W1=0.5, W2=0.5)

    # --- GA ---
    start_time = time.time()
    best_chrom, best_fit, history = run_ga(
        population,
        fitness_eval,
        cont_i_ga,
        trucks_i_ga,
        instance_id,
        len(docks_i_ga),
        num_generations=20
    )

    # Re-sanity après GA (le GA ne doit PAS vider tes DFs)
    if trucks_i_ga.empty:
        print(f"🚨 trucks_i_ga est vide après GA (instance {instance_id}) — on restaure depuis trucks_i_src pour la suite")
        trucks_i_ga = trucks_i_src.copy()

    # Coûts & fitness
    cost   = fitness_eval.calculate_truck_cost_f1(best_chrom)
    energy = fitness_eval.calculate_energy_cost_f2(best_chrom)
    final_fitness = fitness_eval.calculate_fitness(best_chrom, instance_id, include_penalty=False)

    # Loading times (utilise les DFs « sûrs »)
    Times_df = calculate_loading_times_df(best_chrom, trucks_df=trucks_i_ga, docks_df=docks_i_ga)
    os.makedirs("results_loading_times", exist_ok=True)
    # Try writing Excel; fall back to CSV if openpyxl is not installed
    try:
        Times_df.to_excel(f"results_loading_times/instance_{instance_id}_times.xlsx", index=False)
    except ModuleNotFoundError as e:
        # Most common missing dependency is openpyxl
        print("openpyxl not available, saving loading times as CSV instead.")
        Times_df.to_csv(f"results_loading_times/instance_{instance_id}_times.csv", index=False)

    exec_time = time.time() - start_time
    print(f"⏱ Temps : {exec_time:.2f}s | Fitness = {final_fitness}")

    results.append({
        "Instance": instance_id,
        "BestFitness": final_fitness,
        "ExecutionTime(s)": round(exec_time, 3),
        "PopulationSize": len(population),
        "Generations": 20,
        "best_chromosome": best_chrom
    })

# Sauvegarder le résumé global


results_df = pd.DataFrame(results)
results_df.to_csv("results_summary_with_reassignements.csv", index=False)
print("\n✅ Tous les résultats enregistrés dans results_summary_with_reassignements.csv")
