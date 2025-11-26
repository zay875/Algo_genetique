
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
        
        '''
        
        if random.random() < mutation_rate and chromosome[i]:
        # --- vraie mutation : déplacer 1 conteneur vers un autre camion ---

            containers = chromosome[i]

            # choisir un conteneur au hasard dans ce camion
            container_to_move = random.choice(containers)

            # retirer du camion actuel
            containers.remove(container_to_move)

            # choisir un autre camion comme destination
            # (dire : les indices des camions sont : 0, 4, 8, 12, ... dans ton chromosome)
            num_trucks = len(chromosome) // 4
            current_truck_index = i // 4

            # choisir un autre camion
            new_truck_index = random.choice([t for t in range(num_trucks) if t != current_truck_index])

            # ajouter au nouveau camion
            new_position = new_truck_index * 4
            chromosome[new_position].append(container_to_move)
            '''
    return chromosome
#diploid crossover inspired by the paper "A Diploid Evolutionary Algorithm for Sustainable Truck Scheduling at a Cross-Docking Facility by Maxim A. Dulebenets"
'''

def diploid_crossover(parent1, parent2):
    """
    Diploid crossover: combine two parents to create two children,
    each child inherits genes from both parents.
    """
    # Block-wise two-point crossover (operates on blocks of 4 genes = one truck)
    block_size = 4
    num_blocks = len(parent1) // block_size

    # safety: if parents are too short or identical blocks, fallback to copying
    if num_blocks < 2:
        return copy.deepcopy(parent1), copy.deepcopy(parent2)

    # choose two crossover points (block indices) with 0 <= start < end <= num_blocks
    start, end = sorted(random.sample(range(1, num_blocks), 2))

    # split parents into block lists
    blocks1 = [parent1[i*block_size:(i+1)*block_size] for i in range(num_blocks)]
    blocks2 = [parent2[i*block_size:(i+1)*block_size] for i in range(num_blocks)]

    child_blocks1 = []
    child_blocks2 = []
    for i in range(num_blocks):
        if start <= i < end:
            # inherit middle segment from respective parents
            child_blocks1.append(copy.deepcopy(blocks1[i]))
            child_blocks2.append(copy.deepcopy(blocks2[i]))
        
            # inherit outer segments from the opposite parent if the element is not already in the child block
            # Source - https://stackoverflow.com/a
            # Posted by aaronasterling, modified by community. See post 'Timeline' for change history
            # Retrieved 2025-11-17, License - CC BY-SA 4.0
        for elm1 in [item for item in blocks2 if item not in child_blocks1]:
            child_blocks1.insert(i,copy.deepcopy(elm1))
        for elm2 in [item for item in blocks1 if item not in child_blocks2]:
            child_blocks2.insert(i,copy.deepcopy(elm2))
    # flatten blocks back to chromosomes
    child1 = [gene for block in child_blocks1 for gene in block]
    child2 = [gene for block in child_blocks2 for gene in block]

    return child1, child2
'''
def diploid_crossover(parent1, parent2):
    """
    Diploid crossover: combine two parents to create two children,
    each child inherits genes from both parents.
    """
    # Block-wise two-point crossover (operates on blocks of 4 genes = one truck)
    block_size = 4
    num_blocks = len(parent1) // block_size

    # safety: if parents are too short or identical blocks, fallback to copying
    if num_blocks < 2:
        return copy.deepcopy(parent1), copy.deepcopy(parent2)

    # choose two crossover points (block indices) with 0 <= start < end <= num_blocks
    start, end = sorted(random.sample(range(1, num_blocks), 2))

    # split parents into block lists
    blocks1 = [parent1[i*block_size:(i+1)*block_size] for i in range(num_blocks)]
    blocks2 = [parent2[i*block_size:(i+1)*block_size] for i in range(num_blocks)]

    child_blocks1 = []
    child_blocks2 = []
    for i in range(num_blocks):
        if start <= i < end:
            # inherit middle segment from respective parents
            child_blocks1.append(copy.deepcopy(blocks1[i]))
            child_blocks2.append(copy.deepcopy(blocks2[i]))
        else:
            # inherit outer segments from the opposite parent
            child_blocks1.append(copy.deepcopy(blocks2[i]))
            child_blocks2.append(copy.deepcopy(blocks1[i]))

    # flatten blocks back to chromosomes
    child1 = [gene for block in child_blocks1 for gene in block]
    child2 = [gene for block in child_blocks2 for gene in block]

    return child1, child2


def make_hashable_block(block):
    # Convert block to a fully hashable tuple
    return (tuple(block[0]), block[1], block[2], block[3])


def pmx_block(parent1, parent2):
    block_size = 4
    num_blocks = len(parent1) // block_size

    # Convert parents to list-of-blocks
    p1 = [parent1[i*block_size:(i+1)*block_size] for i in range(num_blocks)]
    p2 = [parent2[i*block_size:(i+1)*block_size] for i in range(num_blocks)]

    # Choose PMX slice
    start, end = sorted(random.sample(range(num_blocks), 2))

    # Prepare empty child
    child = [None] * num_blocks

    # Copy segment from p1
    child[start:end] = copy.deepcopy(p1[start:end])

    # Mapping for conflict resolution
    mapping = {}
    for i in range(start, end):
        b1 = make_hashable_block(p1[i])
        b2 = make_hashable_block(p2[i])
        mapping[b2] = b1
        mapping[b1] = b2

    # Fill remaining blocks
    for i in range(num_blocks):
        if child[i] is not None:
            continue

        candidate = p2[i]

        # Resolve conflicts using mapping
        while True:
            h = make_hashable_block(candidate)
            if h in mapping and list(mapping[h]) in child:
                candidate = list(mapping[h])
            else:
                break

        child[i] = copy.deepcopy(candidate)

    # Flatten the child
    flat_child = [gene for block in child for gene in block]
    return flat_child


def PMX_crossover(parent1, parent2):
    child1 = pmx_block(parent1, parent2)
    child2 = pmx_block(parent2, parent1)
    return child1, child2


#------------Correction des chromosomes-----------


def correct_chrom(errors, chrom, trucks_df, containers_df, instance_id):
        
    # Préparation
    df_containers = containers_df[containers_df["Instance"] == instance_id].copy()
    df_trucks = trucks_df[trucks_df["Instance"] == instance_id].copy()
    df_trucks = df_trucks.sort_values("TruckID").reset_index(drop=True)

    truck_ids = df_trucks["TruckID"].tolist()
    num_trucks = len(truck_ids)
    num_blocks = len(chrom) // 4

    unassigned = []
    wrong_assignment = []
    duplicates = []
    capacity_errors = []
    for e in errors:
        
        if "assigné à camion" in e:
            # Exemple: ❌ Conteneur 7 (dest 1) assigné à camion 5 (dest 2)
            parts = e.split()
            cid = int(parts[2])
            wrong_assignment.append(cid)
        
        if "non assignés" in e:
            # Exemple: ⚠️ Conteneurs non assignés : [3]
            ids = eval(e.split(":")[1].strip())
            unassigned.extend(ids)

        if "assignés plusieurs fois" in e:
            ids = eval(e.split(":")[1].strip())
            duplicates.extend(ids)

        if "dépasse la capacité" in e:
            # Exemple: ⚠️ Camion 3 dépasse la capacité (14/6)
            tid = int(e.split()[2])
            capacity_errors.append(tid)

        if "n'existe pas" in e:
            cid = int(e.split()[2])
            wrong_assignment.append(cid)

        if "sans camion correspondant" in e:
            # Exemple: Bloc chromosome 10 sans camion correspondant
            block_idx = int(e.split()[3])
            # On vide ce block
            chrom[block_idx*4] = []
    #enlever les conteneurs duppliqué
 
    for cid in duplicates:
        for i in range(num_blocks):
            block_containers = chrom[i*4]
            if cid in block_containers:
                block_containers.remove(cid)
                
    
    # enlever les conteneurs assigné au mauvais camion
    removed = set()

    for cid in wrong_assignment:
        for i in range(num_blocks):
            block_containers = chrom[i*4]
            if cid in block_containers:
                block_containers.remove(cid)
                removed.add(cid)
    

        
    #assigner les contenerus enlevé et non assigné

    valid_ids = set(df_containers["ContainerID"].tolist())

    # On garde les IDs pour debug / logs
    all_removed = list(removed)  
    all_unassigned = list(unassigned)

    # Mais on ne réassigne que les conteneurs valables
    removed = [cid for cid in removed if cid in valid_ids]
    unassigned = [cid for cid in unassigned if cid in valid_ids]

    to_assign = list(set(unassigned) | set(removed))
    #print (f"the containers to assign{to_assign}")
    for cid in to_assign:
        
        cont_dest = df_containers.loc[df_containers["ContainerID"] == cid, "Destination"].iloc[0]
        cont_len  = df_containers.loc[df_containers["ContainerID"] == cid, "Length"].iloc[0]
        assigned= False
        # Chercher camion compatible
        for i in range(num_trucks):
            tid = truck_ids[i]
            if df_trucks.loc[df_trucks["TruckID"] == tid, "Destination"].iloc[0] != cont_dest:
                continue

            block_containers = chrom[i*4]
            current_len = sum(df_containers[df_containers["ContainerID"] == c]["Length"].iloc[0]
                              for c in block_containers)

            truck_cap = df_trucks.loc[df_trucks["TruckID"] == tid, "Capacity"].iloc[0]

            if current_len + cont_len <= truck_cap:
                block_containers.append(cid)
                assigned = True
                break
        #chercher un camion vide 
        if not assigned:
            for i in range(num_trucks):
                block = chrom[i*4]
                if len(block) == 0:      # 
                #Modifier la destination du camion dans df_trucks
                    tid = truck_ids[i]
                    df_trucks.loc[df_trucks["TruckID"] == tid, "Destination"] = cont_dest
                    block.append(cid)
                    assigned = True
                    break

    return chrom        

    #corriger le conteneurs enlevé et non assingeé

# --- MAIN GA LOOP ---

def run_ga(initial_population, fitness_evaluator, containers_df, trucks_df, instance_id,
           num_docks, num_generations=10, num_elites=1, crossover_rate=0.9, mutation_rate=0.03,num_points=3):

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
        #correct the elits
        corrected_elites = []
        for elite in elites:
            feasible, errors = verify_solution_feasibility(elite, trucks_df, containers_df, instance_id)
            print(f"the error:  {errors}, {feasible}")
            if not feasible:
                elite = correct_chrom(errors, elite, trucks_df, containers_df, instance_id)
            corrected_elites.append(elite)

        elites = corrected_elites
        print(f"the elits are : {elites}")
        # 3. Générer enfants
        max_attempts = 5  # pour éviter une boucle infinie
        offspring = []
        while len(offspring) < len(population) - num_elites:
            parent1 = tournament_selection(population, fitness_values)
            parent2 = tournament_selection(population, fitness_values)
            attempts_parent = 0
            while parent2 == parent1 and attempts_parent < 5:
                parent2 = tournament_selection(population, fitness_values)
                attempts_parent += 1

                # Si toujours identiques → forcer une mutation forte pour créer de la diversité
                '''
                if parent1 == parent2:
                    parent2 = mutate(copy.deepcopy(parent2), num_docks, mutation_rate=0.5)  # mutation plus forte
                '''
            valid_children=[]
            for _ in range(max_attempts):

                if random.random() < crossover_rate:
                    #child1, child2 = PMX_crossover(parent1, parent2)
                    child1, child2 = truck_aligned_crossover(parent1, parent2)
                else:
                    child1, child2 = copy.deepcopy(parent1), copy.deepcopy(parent2)
                child1=mutate(child1, num_docks, mutation_rate)
                child2=mutate(child2, num_docks, mutation_rate)

                 # Vérification de faisabilité
                feasible1, errors1 = verify_solution_feasibility(child1, trucks_df, containers_df, instance_id)
                print(f"errors after ga operations for child 1{errors1}")
                feasible2, errors2 = verify_solution_feasibility(child2, trucks_df, containers_df, instance_id)
                print(f"errors after ga operations for child 2{errors2}")
                if feasible1:
                    valid_children.append(child1)
                else:
                    #corriger le chromosome
                    child1 = correct_chrom(errors1, child1, trucks_df, containers_df, instance_id)
                    
                    valid_children.append(child1)
                if feasible2:
                    valid_children.append(child2)
                else:
                    child2 = correct_chrom(errors2, child2, trucks_df, containers_df, instance_id)
                    valid_children.append(child2)

        # Si on a trouvé des enfants valides, on sort de la boucle
                if len(valid_children) >= 2:
                    break
            # Si après toutes les tentatives, aucun enfant valide → on garde les parents (fallback)
            '''if not valid_children:
                valid_children = [copy.deepcopy(parent1), copy.deepcopy(parent2)]
            '''
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
