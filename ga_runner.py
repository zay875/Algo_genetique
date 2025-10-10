
import random
import copy
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from utils import  verify_solution_feasibility
data = {
    'Container': [1, 2, 3, 4, 5, 6],
    'Length': [2, 4, 2, 5, 10, 4],
    'Position': [57, 63, 58, 49, 26, 71],
    'Destination' : [2,2,2,1,1,2]
}

data_2 = {
    'Truck': [1, 2,3,4,5],
    'Destination': [1, 1,2,2,2],
    'Cost': [624,624, 479,479,479]
}
Truck_cost_df = pd.DataFrame(data_2)
data_containers = {
    'Instance': [12, 12, 12, 12, 12, 12],
    'ContainerID': [1, 2, 3, 4, 5, 6],
    'Length': [2, 4, 2, 5, 5, 4],# changed the container length from 10 to 5 because it will never fit in the truck sincr the truck capacity is 6
    'Position': [57, 63, 58, 49, 26, 71],
    'Destination': [2, 2, 2, 1, 1, 2]
}

data_trucks = {
    'Instance': [12, 12, 12, 12, 12],
    'TruckID': [1, 2, 3, 4, 5],
    'Destination': [1, 1, 2, 2, 2],
    'Cost': [624, 624, 479, 479, 479],
    'Capacity': [6, 6, 6, 6, 6],
    'DockPosition': [1, 1, 4, 4, 2]
}

data_dock = {
    'Instance': [12, 12, 12, 12, 12],
    'DockID': [1, 2, 3, 4, 5],
    'Position': [5, 1, 3, 2, 4]
}
containers_df = pd.DataFrame(data_containers)
trucks_df = pd.DataFrame(data_trucks)
docks_df = pd.DataFrame(data_dock)
penalties = []  #define this before the for-loop
# --- SELECTION ---
def tournament_selection(population, fitness_values, k=3):
    """Sélection par tournoi (choisit le meilleur parmi k individus aléatoires)."""
    selected = random.sample(list(zip(population, fitness_values)), k)
    selected.sort(key=lambda x: x[1])  # tri par fitness (minimisation)
    return copy.deepcopy(selected[0][0])

# --- ELITISM ---
def elitism_selection(population, fitness_values, num_elites):
    """Retourne les meilleurs individus (élites)."""
    ranked = sorted(zip(population, fitness_values), key=lambda x: x[1])
    return [copy.deepcopy(ind) for ind, fit in ranked[:num_elites]]

# --- CROSSOVER ---
def truck_aligned_crossover(parent1, parent2):
    """
    Croisement à un point aligné sur les blocs [containers, _, dock, _].
    """
    block_size = 4
    num_blocks = len(parent1) // block_size
    point = random.randint(1, num_blocks - 1)

    child1 = parent1[:point * block_size] + parent2[point * block_size:]
    child2 = parent2[:point * block_size] + parent1[point * block_size:]

    return child1, child2

'''def truck_aligned_crossover(parent1, parent2):
    child1, child2 = [], []
    for i in range(0, len(parent1), 4):  # iterate trucks
        block1 = parent1[i:i+4]
        block2 = parent2[i:i+4]

        if random.random() < 0.5:
            child1 += block1
            child2 += block2
        else:
            child1 += block2
            child2 += block1

   return child1, child2'''
# --- MUTATION ---
def mutate(chromosome, num_docks, mutation_rate=0.2):
    """
    Mutation aléatoire : échange de containers ou changement de dock.
    """
    chromosome = copy.deepcopy(chromosome)
    for i in range(0, len(chromosome), 4):
        if random.random() < mutation_rate:
            # mutation dock
            chromosome[i+2] = random.randint(1, num_docks)
        if random.random() < mutation_rate and chromosome[i]:
            # mutation container swap
            containers = chromosome[i]
            if len(containers) > 1:
                idx1, idx2 = random.sample(range(len(containers)), 2)
                containers[idx1], containers[idx2] = containers[idx2], containers[idx1]
                chromosome[i] = containers
    return chromosome

# --- MAIN GA LOOP ---

def run_ga(initial_population, fitness_evaluator, num_docks,
           num_generations=100, num_elites=1, crossover_rate=0.9, mutation_rate=0.03):
    """
    Exécute l’algorithme génétique avec suivi du meilleur global.
    """
    population = copy.deepcopy(initial_population)
    best_fitness_history = []

    # 🔹 Variables pour suivre le meilleur global
    global_best_fitness = float('inf')
    global_best_chromosome = None

    for gen in range(num_generations):
        # 1. Évaluer fitness
        fitness_values = [
        fitness_evaluator.calculate_fitness(ch, trucks_df, containers_df, instance_id=12)
        for ch in population
]


        # 2. Garder élites
        elites = elitism_selection(population, fitness_values, num_elites)

        # 3. Générer enfants
        offspring = []
        while len(offspring) < len(population) - num_elites:
            parent1 = tournament_selection(population, fitness_values)
            parent2 = tournament_selection(population, fitness_values)

            if random.random() < crossover_rate:
                child1, child2 = truck_aligned_crossover(parent1, parent2)
            else:
                child1, child2 = copy.deepcopy(parent1), copy.deepcopy(parent2)

            offspring.append(mutate(child1, num_docks, mutation_rate))
            if len(offspring) < len(population) - num_elites:
                offspring.append(mutate(child2, num_docks, mutation_rate))

        # 4. Nouvelle population
        population = elites + offspring
        #afficher la nouvelle generation
        print(f"\n=== Génération {gen+1} : Nouvelle population ===")
        for i, chrom in enumerate(population):
         print(f"Chromosome {i+1}:")
         print(chrom)
         #verify faisability in new population
         feasible, errors = verify_solution_feasibility(chrom, trucks_df, containers_df, instance_id=12)
         print(f"\nChromosome {i+1} : {' Faisable' if feasible else ' Non faisable'}")
         if not feasible:
            for err in errors:
             print("   ", err)
        
        
          
        # 5. Suivi du meilleur global
        current_best_fitness = min(fitness_values)
        current_best_chromosome = population[np.argmin(fitness_values)]

        if current_best_fitness < global_best_fitness:
            global_best_fitness = current_best_fitness
            global_best_chromosome = copy.deepcopy(current_best_chromosome)

        best_fitness_history.append(global_best_fitness)
        print(f"Gen {gen+1}: Best fitness = {global_best_fitness}")
        penalty_value, _ = fitness_evaluator.calculate_penalties(global_best_chromosome, trucks_df, containers_df, instance_id=12)
        penalties.append(penalty_value)
    # 6. Résultat final
    '''plt.plot(best_fitness_history)
    plt.xlabel("Generation")
    plt.ylabel("Best Fitness")
    plt.title("GA Convergence")
    plt.show(block=False)
    plt.pause(50)
    plt.close()'''
    '''
    plt.figure()
    plt.plot(penalties, label="Penalty")
    plt.xlabel("Generation")
    plt.ylabel("Total Penalty")
    plt.title("Penalty Evolution")
    plt.legend()
    plt.show()'''

    
    fig, axes = plt.subplots(2, 1, figsize=(8, 6))

    # Fitness
    axes[0].plot(best_fitness_history, color='blue')
    axes[0].set_title("GA Convergence (Best Fitness)")
    axes[0].set_xlabel("Generation")
    axes[0].set_ylabel("Fitness")
    axes[0].grid(True)

    # Penalty
    axes[1].plot(penalties, color='orange', linestyle="--")
    axes[1].set_title("Penalty Evolution")
    axes[1].set_xlabel("Generation")
    axes[1].set_ylabel("Penalty")
    axes[1].grid(True)

    plt.tight_layout()
    plt.show(block=False)
    plt.pause(50)
    plt.close()

    return global_best_chromosome, global_best_fitness, best_fitness_history
