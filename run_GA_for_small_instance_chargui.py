# run_all_instances.py
import pandas as pd
import time
from population_copy import generate_initial_population
from fitness import FitnessEvaluator
from ga_runner import run_ga
from utils import print_chromosome_assignments
from utils import verify_solution_feasibility
import re

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
        Extrait une matrice style :
        R = [
            3 8 13 18 23
            28 33 38 43 48
        ];
        """
        pattern = rf"{name}\s*=\s*\[([\s\S]*?)\];"
        match = re.search(pattern, text)
        if not match:
            return []

        raw = match.group(1).strip().split("\n")
        matrix = []
        for row in raw:
            nums = list(map(int, re.findall(r"\d+", row)))
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
    G = extract_matrix("G")        # destinations conteneurs (1 ligne)
    R = extract_matrix("R")        # positions quais

    Cd = extract_list("C_d")       # coût par destination
    


    # -------------------------
    # BUILD containers_df
    # -------------------------
    data_cont = []
    for i in range(N):
        data_cont.append({
            "Instance" : instance_id,
            "ContainerID": i + 1,
            "Length": L[i],
            "Position": P[i],
            "Destination": G[0][i]   # unique ligne
        })

    containers_df = pd.DataFrame(data_cont)


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
    dock_cycle = dock_positions[:H]

    data_trucks = []
    for t in range(H):
        data_trucks.append({
            
            "Instance" : instance_id,
            "TruckID": t + 1,
            "Destination": -1,
              
            "Cost": 0,   # 351
            "Capacity": Q,                  # capacité
            "DockPosition": dock_cycle[t],
            "added": False
        })

    trucks_df = pd.DataFrame(data_trucks)

    return containers_df, trucks_df, docks_df,Cd
import os
import pandas as pd

INPUT_FOLDER = "Benchmark_instances_set_for_Sustainability_2019/instances/"


# Parcourir tous les fichiers .txt
instance_files = [f for f in os.listdir(INPUT_FOLDER) if f.endswith(".txt")]

print(f"{len(instance_files)} fichiers trouvés.")

for idx, filename in enumerate(instance_files, start=1):
    instance_path = os.path.join(INPUT_FOLDER, filename)

    try:
        print(f"\n🔄 Conversion de : {filename}")
        # Identifiant unique basé sur l'ordre ou sur le nom
        #instance_id = os.path.splitext(filename)[0]
        
        instance_name = os.path.splitext(filename)[0]
        instance_id = int(re.findall(r"\d+", instance_name)[0])   

        print(f"the instances numbers: {instance_id}")


        # Un SEUL appel pour tout extraire
        containers_df, trucks_df, docks_df, destinations = parse_benchmark_instance(instance_path,instance_id=instance_id)

    except Exception as e:
        print(f" ERREUR lors de la conversion de {filename} : {e}")

    num_generations= 5
    # Récupérer toutes les instances existantes
    #instances = sorted(containers_df["Instance"].unique())
    #print(containers_df["Instance"].dtype)


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
results_df.to_csv("results_summary_GA_ALL_instances_chargui.csv", index=False)
print("\n✅ Tous les résultats enregistrés dans results_summary_GA_ALL_instances_chargui.csv")
