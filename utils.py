
import random
import pandas as pd
import copy
def generate_random_chromosome(trucks_df, docks_df, containers_df):
    chromosome = []
    dock_positions = docks_df['DockID'].tolist()
    containers = containers_df[['ContainerID','Length']].to_dict("records")
    random.shuffle(containers)

    truck_ids = trucks_df['TruckID'].tolist()
    capacities = dict(zip(truck_ids, trucks_df['Capacity']))
    assignments = {t: [] for t in truck_ids}

    for c in containers:
        feasible = [t for t in truck_ids if capacities[t] >= c['Length']]
        if feasible:
            t = random.choice(feasible)
            assignments[t].append(c['ContainerID'])
            capacities[t] -= c['Length']

    for t in truck_ids:
        dock_pos = random.choice(dock_positions)
        chromosome.extend([assignments[t], 0, dock_pos, 0])

    return chromosome

def print_chromosome_assignments(chromosome, trucks_df):
    for i, t in enumerate(trucks_df['TruckID'].tolist()):
        idx = i * 4
        print(f"Truck {t}: Containers {chromosome[idx]} -> Dock {chromosome[idx+2]}")


