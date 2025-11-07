
from binpacking import process_instance, binpacking_to_chromosome
from utils import generate_random_chromosome
import pandas as pd

def generate_initial_population(pop_size, containers_df, trucks_df, docks_df, instance_id, ratio_binpacking=0.2):
    population, seen = [], set()
    num_bp = int(pop_size * ratio_binpacking)
    for i in range(num_bp):
        verbose_flag = (i == 0)
        trucks_assigned, updated_trucks_df = process_instance(instance_id, containers_df, trucks_df, docks_df)

        if updated_trucks_df is not None and not updated_trucks_df.empty:
            trucks_df = updated_trucks_df
        else:
            print(f"⚠️ updated_trucks_df vide à l’itération {i}, on garde la version précédente")

        print(f"the tuck container assignement list is : {trucks_assigned}")
        chrom = binpacking_to_chromosome(trucks_assigned, docks_df)
        key = str(chrom)
        if key not in seen:
            population.append(chrom); seen.add(key)
    
    while len(population) < pop_size:
        chrom = generate_random_chromosome(trucks_df , docks_df, containers_df)
        key = str(chrom)
        if key not in seen:
            population.append(chrom); seen.add(key)
    return population, trucks_df
