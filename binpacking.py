
import pandas as pd
import csv
# Load dataframes as usual
'''
containers_df = pd.read_csv("C:/Users/Taieb/Algo_genetique/containers_all.csv")
trucks_df = pd.read_csv("C:/Users/Taieb/Algo_genetique/trucks_all.csv")
docks_df = pd.read_csv("C:/Users/Taieb/Algo_genetique/docks_all.csv")
INSTANCE_ID = 12
containers_df = containers_df[containers_df["Instance"] == INSTANCE_ID].copy()
trucks_df = trucks_df[trucks_df["Instance"] == INSTANCE_ID].copy()
docks_df = docks_df[docks_df["Instance"] == INSTANCE_ID].copy()
'''
'''
def process_instance(instance_id, containers_df, trucks_df, docks_df):
    # --- Filter data for this instance ---
    # --- Build truck list ---
    truck_list = []
    dock_ids = docks_df['DockID'].tolist()
    num_docks = len(dock_ids)
    #assignes docks with a round robin structure
    for i, row in trucks_df.iterrows():
        assigned_dock_id = dock_ids[i % num_docks]
        assigned_dock_position = docks_df[docks_df['DockID'] == assigned_dock_id]['Position'].iloc[0]

        truck_list.append({
            'TruckID': row['TruckID'],
            'Capacity': row['Capacity'],
            'InitialCapacity': row['Capacity'],
            'Destination': row['Destination'],
            'AssignedContainers': [],
            'AssignedDockID': assigned_dock_id,
            'AssignedDockPosition': assigned_dock_position
        })

    # --- Group containers by destination, sort by length desc ---
    grouped_containers = {}
    for dest_id, group in containers_df.groupby("Destination"):
        grouped_containers[dest_id] = (
            group.sort_values(by="Length", ascending=False)
            .to_dict("records")
        )
    unassigned_containers = []
    for dest_id, containers_in_dest in grouped_containers.items():
        for container in containers_in_dest:
            length = container["Length"]
            c_id = container["ContainerID"]

            # Chercher un camion compatible (même destination et capacité dispo)
            feasible_trucks = [
                t for t in truck_list
                if t["Destination"] == dest_id and t["Capacity"] >= length
            ]

            if feasible_trucks:
                # Choisir celui qui a la capacité la plus serrée (meilleur fit)
                best_truck = min(feasible_trucks, key=lambda x: x["Capacity"])
                best_truck["AssignedContainers"].append(c_id)
                best_truck["Capacity"] -= length
            else:
                # Aucun camion compatible
                unassigned_containers.append(c_id)

    max_truck_id = max([truck['TruckID'] for truck in truck_list])
    trucks_assigned_containers_list = [[] for _ in range(max_truck_id + 1)]

    for truck in truck_list:
        truck_id = truck['TruckID']
        truck_assigned_list = sorted([int(c) for c in truck['AssignedContainers']])
        trucks_assigned_containers_list[truck_id] = truck_assigned_list

    return trucks_assigned_containers_list
'''
def process_instance(instance_id, containers_df, trucks_df, docks_df):
    # --- Préparation des données ---
    truck_list = []
    dock_ids = docks_df['DockID'].tolist()
    num_docks = len(dock_ids)

    # --- Attribution des quais aux camions (round robin) ---
    for i, row in trucks_df.iterrows():
        assigned_dock_id = dock_ids[i % num_docks]
        assigned_dock_position = docks_df[docks_df['DockID'] == assigned_dock_id]['Position'].iloc[0]

        truck_list.append({
            'TruckID': row['TruckID'],
            'Capacity': row['Capacity'],
            'InitialCapacity': row['Capacity'],
            'Destination': row['Destination'],
            'AssignedContainers': [],
            'AssignedDockID': assigned_dock_id,
            'AssignedDockPosition': assigned_dock_position
        })

    # --- Regrouper les conteneurs par destination (tri décroissant par longueur) ---
    grouped_containers = {}
    for dest_id, group in containers_df.groupby("Destination"):
        grouped_containers[dest_id] = (
            group.sort_values(by="Length", ascending=False)
            .to_dict("records")
        )

    unassigned_containers = []

    # --- Affectation des conteneurs ---
    for dest_id, containers_in_dest in grouped_containers.items():
        for container in containers_in_dest:
            length = container["Length"]
            c_id = container["ContainerID"]

            # 1️⃣ Chercher un camion avec la même destination et assez de capacité
            feasible_trucks = [
                t for t in truck_list
                if t["Destination"] == dest_id and t["Capacity"] >= length
            ]

            if feasible_trucks:
                # Choisir le camion avec la capacité la plus serrée (best fit)
                best_truck = min(feasible_trucks, key=lambda x: x["Capacity"])
                best_truck["AssignedContainers"].append(c_id)
                best_truck["Capacity"] -= length

            else:
                # 2️⃣ Sinon, chercher un camion VIDE (aucun conteneur encore affecté)
                empty_trucks = [
                    t for t in truck_list
                    if len(t["AssignedContainers"]) == 0 and t["Capacity"] >= length
                ]

                if empty_trucks:
                    # On choisit le premier camion vide disponible
                    empty_truck = empty_trucks[0]
                    empty_truck["AssignedContainers"].append(c_id)
                    empty_truck["Capacity"] -= length
                    #print(f"⚠️ Conteneur {c_id} (dest {dest_id}) assigné à un camion VIDE (dest {empty_truck['Destination']})")

                else:
                    # 3️⃣ Aucun camion vide ou compatible disponible
                    unassigned_containers.append(c_id)

    # --- Construire la sortie sous forme de liste ---
    max_truck_id = max([truck['TruckID'] for truck in truck_list])
    trucks_assigned_containers_list = [[] for _ in range(max_truck_id + 1)]

    for truck in truck_list:
        truck_id = truck['TruckID']
        truck_assigned_list = sorted([int(c) for c in truck['AssignedContainers']])
        trucks_assigned_containers_list[truck_id] = truck_assigned_list

    # --- Affichage des conteneurs non assignés ---
    '''
    if unassigned_containers:
        print(f"Conteneurs non assignés : {unassigned_containers}")
    else:
        print(" Tous les conteneurs ont été assignés.")
    '''
    return trucks_assigned_containers_list


def binpacking_to_chromosome(trucks_assigned_containers_list, docks_df):
    chromosome = []
    dock_positions = docks_df['Position'].tolist()
    for truck_id, assigned in enumerate(trucks_assigned_containers_list):
        if truck_id == 0:
            continue
        dock_position = dock_positions[truck_id % len(dock_positions)]
        chromosome.extend([assigned, 0, dock_position, 0])
    return chromosome
