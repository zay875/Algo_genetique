
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


def verify_solution_feasibility(chromosome, trucks_df, containers_df):
    """
    Vérifie si une solution (chromosome) est faisable.
    Retourne un dictionnaire contenant les erreurs et un booléen de faisabilité.
    """
    errors = []
    all_assigned_containers = []

    # 1️⃣ Vérifier la capacité de chaque camion
    for i in range(0, len(chromosome), 4):
        containers_assigned = chromosome[i]
        truck_id = i // 4 + 1

        truck_info = trucks_df.loc[trucks_df["TruckID"] == truck_id].iloc[0]
        truck_capacity = truck_info["Capacity"]
        truck_destination = truck_info["Destination"]

        total_length = 0
        for c_id in containers_assigned:
            cont_info = containers_df.loc[containers_df["ContainerID"] == c_id].iloc[0]
            total_length += cont_info["Length"]

            # Vérifier la destination
            if cont_info["Destination"] != truck_destination:
                errors.append(
                    f"❌ Conteneur {c_id} (dest {cont_info['Destination']}) "
                    f"assigné à camion {truck_id} (dest {truck_destination})"
                )

        if total_length > truck_capacity:
            errors.append(
                f"⚠️ Camion {truck_id} dépasse la capacité ({total_length}/{truck_capacity})"
            )

        all_assigned_containers.extend(containers_assigned)

    # 2️⃣ Vérifier les conteneurs dupliqués
    duplicates = [c for c in set(all_assigned_containers) if all_assigned_containers.count(c) > 1]
    if duplicates:
        errors.append(f"⚠️ Conteneurs assignés plusieurs fois : {duplicates}")

    feasible = len(errors) == 0
    return feasible, errors

