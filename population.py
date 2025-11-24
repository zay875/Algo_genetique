
#from binpacking import process_instance, binpacking_to_chromosome
from binpacking_copy import process_instance, binpacking_to_chromosome 
from utils import generate_random_chromosome
import pandas as pd

def generate_initial_population(pop_size, containers_df, trucks_df, docks_df, instance_id, ratio_binpacking=0.8):
    population, seen = [], set()
    num_bp = int(pop_size * ratio_binpacking)
    for i in range(num_bp):
        verbose_flag = (i == 0)
        trucks_assigned= process_instance(instance_id, containers_df, trucks_df, docks_df)

        print(f"the truck container assignement list is : {trucks_assigned}")
        chrom = binpacking_to_chromosome(trucks_assigned, docks_df,containers_df,instance_id)
        print(f"chromosome: {chrom}")
        '''
        key = str(chrom)
        
        if key not in seen:
        '''
        #; seen.add(key)
        population.append(chrom)
        
    while len(population) < pop_size:
        chrom = generate_random_chromosome(trucks_df , docks_df, containers_df,instance_id)
        key = str(chrom)
        if key not in seen:
        
            population.append(chrom); seen.add(key)
        
    return population
