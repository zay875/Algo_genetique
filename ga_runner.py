
import random
import copy
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from utils import  verify_solution_feasibility

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

import random

def multipoint_crossover(parent1, parent2, num_points=3):
    """
    Crossover à plusieurs points, mais respectant les blocs de 4 gènes.
    Chaque bloc correspond à un camion.
    """
    block_size = 4
    num_blocks = len(parent1) // block_size
    crossover_points = sorted(random.sample(range(1, num_blocks), num_points))

    child1, child2 = [], []
    start = 0
    swap = False

    for point in crossover_points + [num_blocks]:
        if not swap:
            child1.extend(parent1[start*block_size : point*block_size])
            child2.extend(parent2[start*block_size : point*block_size])
        else:
            child1.extend(parent2[start*block_size : point*block_size])
            child2.extend(parent1[start*block_size : point*block_size])
        swap = not swap
        start = point

    return child1, child2

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

def run_ga(initial_population, fitness_evaluator, containers_df, trucks_df, instance_id,
           num_docks, num_generations=10, num_elites=1, crossover_rate=0.9, mutation_rate=0.03,num_points=5):

    """
    Exécute l’algorithme génétique avec suivi du meilleur global.
    """
    population = copy.deepcopy(initial_population)
    best_fitness_history = []
    penalties = []


    # 🔹 Variables pour suivre le meilleur global
    global_best_fitness = float('inf')
    global_best_chromosome = None
    fitness_cache = {}

    for gen in range(num_generations):
        # --- Calcul du fitness avec cache ---
        fitness_cache = {}
        fitness_values = []

        for chrom in population:
            key = str(chrom)
            #appelle verify feasibility
            if key not in fitness_cache:
                fitness_cache[key] = fitness_evaluator.calculate_fitness(chrom, instance_id, include_penalty=True)
            


            fitness_values.append(fitness_cache[key])

        # 2. Garder élites
        elites = elitism_selection(population, fitness_values, num_elites)

        # 3. Générer enfants
        max_attempts = 5  # pour éviter une boucle infinie
        offspring = []
        while len(offspring) < len(population) - num_elites:
            parent1 = tournament_selection(population, fitness_values)
            parent2 = tournament_selection(population, fitness_values)
            valid_children=[]
            for _ in range(max_attempts):

                if random.random() < crossover_rate:
                    child1, child2 = multipoint_crossover(parent1, parent2,num_points)
                else:
                    child1, child2 = copy.deepcopy(parent1), copy.deepcopy(parent2)
                child1=mutate(child1, num_docks, mutation_rate)
                child2=(mutate(child2, num_docks, mutation_rate))

                 # Vérification de faisabilité
                feasible1, errors1 = verify_solution_feasibility(child1, trucks_df, containers_df, instance_id)
                feasible2, errors2 = verify_solution_feasibility(child2, trucks_df, containers_df, instance_id)

                if feasible1:
                    valid_children.append(child1)
                if feasible2:
                    valid_children.append(child2)

        # Si on a trouvé des enfants valides, on sort de la boucle
                if len(valid_children) >= 2:
                    break
            # Si après toutes les tentatives, aucun enfant valide → on garde les parents (fallback)
            if not valid_children:
                valid_children = [copy.deepcopy(parent1), copy.deepcopy(parent2)]

            offspring.extend(valid_children[:len(population) - len(elites) - len(offspring)])

        # 4. Nouvelle population
        population = elites + offspring
        #afficher la nouvelle generation
        
        #print(f"\n=== Génération {gen+1} : Nouvelle population ===")
        #for i, chrom in enumerate(population):
         #print(f"Chromosome {i+1}:")
         #print(chrom)
         #verify faisability in new population
         #feasible, errors = verify_solution_feasibility(chrom, trucks_df, containers_df, instance_id)
         #print(f"\nChromosome {i+1} : {' Faisable' if feasible else ' Non faisable'}")
         #if not feasible:
            #for err in errors:
             #print("   ", err)
        
        
             
        # 5. Suivi du meilleur global
        current_best_fitness = min(fitness_values)
        current_best_chromosome = population[np.argmin(fitness_values)]
      
        if current_best_fitness < global_best_fitness:
            global_best_fitness = current_best_fitness
            global_best_chromosome = copy.deepcopy(current_best_chromosome)
        
      
        best_fitness_history.append(global_best_fitness)
        #print(f"Gen {gen+1}: Best fitness = {global_best_fitness}")
        #penalty_value, _ = fitness_evaluator.calculate_penalties(global_best_chromosome, trucks_df, containers_df, instance_id)
        #penalties.append(penalty_value)
    
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

    
    #fig, axes = plt.subplots(2, 1, figsize=(8, 6))
    #plt.close(fig)
    # Fitness
    '''axes[0].plot(best_fitness_history, color='blue')
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
    '''
    return global_best_chromosome, global_best_fitness,best_fitness_history, population
