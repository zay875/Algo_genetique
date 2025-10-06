
import random
import copy
import numpy as np
import matplotlib.pyplot as plt

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
           num_generations=100, num_elites=2, crossover_rate=0.8, mutation_rate=0.1):
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
        fitness_values = [fitness_evaluator.calculate_fitness(ch) for ch in population]

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

        # 5. Suivi du meilleur global
        current_best_fitness = min(fitness_values)
        current_best_chromosome = population[np.argmin(fitness_values)]

        if current_best_fitness < global_best_fitness:
            global_best_fitness = current_best_fitness
            global_best_chromosome = copy.deepcopy(current_best_chromosome)

        best_fitness_history.append(global_best_fitness)
        print(f"Gen {gen+1}: Best fitness = {global_best_fitness}")

    # 6. Résultat final
    plt.plot(best_fitness_history)
    plt.xlabel("Generation")
    plt.ylabel("Best Fitness")
    plt.title("GA Convergence")
    plt.show(block=False)
    plt.pause(10)
    plt.close()
    

    return global_best_chromosome, global_best_fitness, best_fitness_history
