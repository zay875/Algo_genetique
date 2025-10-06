
from binpacking import process_instance, binpacking_to_chromosome
from utils import generate_random_chromosome

def generate_initial_population(pop_size, containers_df, trucks_df, docks_df, instance_id, ratio_binpacking=0.2):
    population, seen = [], set()
    num_bp = int(pop_size * ratio_binpacking)

    for _ in range(num_bp):
        trucks_assigned = process_instance(instance_id, containers_df, trucks_df, docks_df)
        chrom = binpacking_to_chromosome(trucks_assigned, docks_df)
        key = str(chrom)
        if key not in seen:
            population.append(chrom); seen.add(key)

    while len(population) < pop_size:
        chrom = generate_random_chromosome(trucks_df, docks_df, containers_df)
        key = str(chrom)
        if key not in seen:
            population.append(chrom); seen.add(key)

    return population
