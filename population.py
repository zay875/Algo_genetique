
from binpacking import process_instance, binpacking_to_chromosome
from utils import generate_random_chromosome
import pandas as pd

def generate_initial_population(pop_size, containers_df, trucks_df, docks_df, instance_id, ratio_binpacking=0.2):
    population, seen = [], set()
    num_bp = int(pop_size * ratio_binpacking)
    print("  [POP] Début de generate_initial_population")
    for _ in range(num_bp):
        print(f"  [POP] Génération de l'individu {_+1}/{pop_size}")
        trucks_assigned = process_instance(instance_id, containers_df, trucks_df, docks_df)
       
        chrom = binpacking_to_chromosome(trucks_assigned, docks_df)
        key = str(chrom)
        if key not in seen:
            population.append(chrom); seen.add(key)
    
    print("  [POP] Population complète ✅")  
    print(f"  [POP] Fin de la phase binpacking ({len(population)} individus)")  
    while len(population) < pop_size:
        print(f"  [POP] (aléatoire) Génération de l'individu {len(population)+1}/{pop_size}")
        chrom = generate_random_chromosome(trucks_df , docks_df, containers_df)
        key = str(chrom)
        if key not in seen:
            population.append(chrom); seen.add(key)
    print(f"  [POP] Population complète ✅ ({len(population)} individus)")
    return population
