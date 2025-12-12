import pandas as pd
import time
import os
import re

from population_copy import generate_initial_population
from fitness import FitnessEvaluator
from ga_runner import run_ga

INPUT_FOLDER = "Benchmark_instances_set_for_Sustainability_2019/instances/"

# Paramètres pour la Grid Search
population_sizes = [30, 40, 50, 60]
crossover_rates = [0.4, 0.6, 0.8, 0.9]
mutation_rates = [0.01, 0.05, 0.08, 0.1]

N_RUNS = 10
MAX_GENERATIONS = 50


# ---------------------------------------------------------------------
#  Utilitaire pour parser une instance
# ---------------------------------------------------------------------

def parse_benchmark_instance(path, instance_id="X"):
    """
    Convertit une instance du benchmark .txt en containers_df, trucks_df, docks_df
    """

    # Lire fichier
    with open(path, "r") as f:
        text = f.read()

    def extract_value(name):
        """
        Extrait un entier : N=4;
        """
        match = re.search(rf"{name}\s*=\s*(\d+)", text)
        return int(match.group(1)) if match else None

    def extract_list(name):
        """
        Extrait liste du style L = [3 5 2 3]
        """
        match = re.search(rf"{name}\s*=\s*\[([^\]]+)\]", text)
        if not match:
            return []
        raw = match.group(1)
        return list(map(int, re.findall(r"\d+", raw)))

    def extract_matrix(name):
        """
        Extrait correctement les matrices multilignes du style :

        G = [
            0 1 0 ...
            0 0 1 ...
            ...
        ];

        Fonction robuste qui gère :
        ✔ lignes vides
        ✔ tabulations
        ✔ espaces irréguliers
        ✔ matrices étalées sur plusieurs lignes
        """
        pattern = rf"{name}\s*=\s*\[([\s\S]*?)\];"
        match = re.search(pattern, text, re.MULTILINE)

        if not match:
            return []

        block = match.group(1)

        matrix = []
        for line in block.splitlines():
            # ignore lignes vides ou blanches
            if not line.strip():
                continue

            # extraire tous les entiers de la ligne
            nums = list(map(int, re.findall(r"-?\d+", line)))

            if nums:
                matrix.append(nums)

        return matrix




    # Extraction
    N = extract_value("N")
    H = extract_value("H")
    Q = extract_value("Q")
    D = extract_value("D")
    K = extract_value("K")
    Ce = extract_value("C_e")

    L = extract_list("L")          # longueurs
    P = extract_list("P")          # positions conteneurs
    G = extract_matrix("G")
    if len(G) != D:
        print(f"⚠️ WARNING: G contient {len(G)} lignes mais D = {D} (instance {instance_id})")

    for row in G:
        if len(row) != N:
            print(f"⚠️ Ligne de G de longueur {len(row)} au lieu de N = {N}")
        # destinations conteneurs (1 ligne)
    R = extract_matrix("R")        # positions quais
    print("DEBUG R rows:", len(R))
    print("DEBUG R row lengths:", [len(r) for r in R])
    print("DEBUG dock_positions length:", len([pos for row in R for pos in row]))
    print("Expected H =", H)
    Cd = extract_list("C_d")       # coût par destination
    
    print("DEBUG :: N =", N)
    print("DEBUG :: len(L) =", len(L))
    print("DEBUG :: len(P) =", len(P))
    print("DEBUG :: G rows =", len(G))
    print("DEBUG :: G row lengths =", [len(r) for r in G])
    print("DEBUG :: len(Cd) =", len(Cd))


    # -------------------------
    # BUILD containers_df
    # -------------------------
    data_cont = []

    nb_dest = len(G)   # normalement = D, une ligne par destination

    for i in range(N):   # i = 0..N-1
        dest_idx = None

        for d in range(nb_dest):   # d = 0..D-1
            row = G[d]
            # sécurité si une ligne G est plus courte que N
            if i < len(row) and row[i] == 1:
                dest_idx = d+1       # ou d+1 si tu veux 1..D
                break

        if dest_idx is None:
            # aucun 1 trouvé pour ce conteneur → cas anormal
            print(f"⚠️ Aucun 1 trouvé dans G pour le conteneur {i+1} (instance {instance_id})")
            dest_idx = -1  # ou 0, comme tu veux

        data_cont.append({
            "Instance": instance_id,
            "ContainerID": i + 1,
            "Length": L[i],
            "Position": P[i],
            "Destination": dest_idx
        })

    containers_df = pd.DataFrame(data_cont)

    

    # Ajout du coût par conteneur en fonction de sa destination
    def get_cost_for_dest(dest):
        if dest <= 0:
            return 0  # ou np.nan si tu préfères
        if dest > len(Cd):
            print(f"⚠️ Destination {dest} hors limites pour l'instance {instance_id}")
            return 0
        return Cd[dest - 1]

    containers_df["Cost_destination"] = containers_df["Destination"].apply(get_cost_for_dest)


    # -------------------------
    # BUILD docks_df
    # flatten R
    # -------------------------
    dock_positions = [pos for row in R for pos in row]

    docks_df = pd.DataFrame({
    
        "Instance" : instance_id,
        "DockID": list(range(1, len(dock_positions) + 1)),
        "Position": dock_positions
    })


    # -------------------------
    # BUILD trucks_df
    # -------------------------
    # Assign dock positions in order
    

    data_trucks = []
    for t in range(H):
        assigned_position = dock_positions[t % len(dock_positions)]
        data_trucks.append({
            
            "Instance" : instance_id,
            "TruckID": t + 1,
            "Destination": -1,
              
            "Cost": 0,   # 351
            "Capacity": Q,                  # capacité
            "DockPosition": assigned_position,
            "added": False
        })

    trucks_df = pd.DataFrame(data_trucks)

    return containers_df, trucks_df, docks_df,Cd
 


# ---------------------------------------------------------------------
#   GRID SEARCH : test toutes les combinaisons
# ---------------------------------------------------------------------
def run_grid_search_for_instance(instance_id, containers_df, trucks_df, docks_df, Cd):

    results = []

    num_docks = len(docks_df[docks_df["Instance"] == instance_id])
    fitness_eval = FitnessEvaluator(containers_df, trucks_df, Cd, C_E=0.5, W1=0.5, W2=0.5)

    for pop in population_sizes:
        for pc in crossover_rates:
            for pm in mutation_rates:

                print(f"\n🔍 Testing configuration: pop={pop}, pc={pc}, pm={pm}")

                fitness_list = []
                time_list = []
                truck_cost_list = []
                energy_cost_list = []

                for run_id in range(N_RUNS):

                    # --------------------------------------------------------
                    # GENERATE POPULATION
                    # --------------------------------------------------------
                    population = generate_initial_population(
                        pop_size=pop,
                        containers_df=containers_df,
                        trucks_df=trucks_df,
                        docks_df=docks_df,
                        instance_id=instance_id,
                        ratio_binpacking=0.8
                    )

                    # --------------------------------------------------------
                    # RUN GA
                    # --------------------------------------------------------
                    t0 = time.time()
                    best_chrom, best_fit, history, new_pop = run_ga(
                        population,
                        fitness_eval,
                        containers_df,
                        trucks_df,
                        instance_id,
                        num_docks,
                        num_generations=MAX_GENERATIONS,       
                        crossover_rate=pc,
                        mutation_rate=pm
                    )
                    exec_time = time.time() - t0

                    # --------------------------------------------------------
                    # COLLECT PERFORMANCE
                    # --------------------------------------------------------
                    truck_cost = fitness_eval.calculate_truck_cost_f1_from_chrom(best_chrom, instance_id)
                    energy_cost = fitness_eval.calculate_energy_cost_f2(best_chrom)

                    fitness_list.append(best_fit)
                    time_list.append(exec_time)
                    truck_cost_list.append(truck_cost)
                    energy_cost_list.append(energy_cost)

                # ------------------------------------------------------------
                # STORE MEAN RESULTS FOR THIS PARAMETER CONFIGURATION
                # ------------------------------------------------------------
                results.append({
                    "Instance": instance_id,
                    "PopulationSize": pop,
                    "CrossoverRate": pc,
                    "MutationRate": pm,
                    "AvgFitness": sum(fitness_list) / N_RUNS,
                    "AvgTruckCost": sum(truck_cost_list) / N_RUNS,
                    "AvgEnergyCost": sum(energy_cost_list) / N_RUNS,
                    "AvgTime": sum(time_list) / N_RUNS
                })

    return pd.DataFrame(results)



# ---------------------------------------------------------------------
#   MAIN SCRIPT : PARCOURT TOUTES LES INSTANCES
# ---------------------------------------------------------------------
def main():

    instance_files = [f for f in os.listdir(INPUT_FOLDER) if f.endswith(".txt")]
    print(f"📁 {len(instance_files)} fichiers trouvés.")

    all_results = []

    for filename in instance_files:

        path = os.path.join(INPUT_FOLDER, filename)
        instance_name = os.path.splitext(filename)[0]
        instance_id = int(re.findall(r"\d+", instance_name)[0])

        print(f"\n==========================================")
        print(f"➡️ Running Grid Search on instance {instance_id}")
        print(f"==========================================")

        containers_df, trucks_df, docks_df, Cd = parse_benchmark_instance(path, instance_id)

        df_instance = run_grid_search_for_instance(instance_id, containers_df, trucks_df, docks_df, Cd)
        all_results.append(df_instance)

    # Fusion des résultats et sauvegarde CSV final
    final_df = pd.concat(all_results, ignore_index=True)
    final_df.to_csv("GA_grid_search_results.csv", index=False)

    print("\n🎉 FINI ! Résultats enregistrés dans GA_grid_search_results.csv")



if __name__ == "__main__":
    main()
