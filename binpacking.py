
import pandas as pd
import csv
# Load dataframes as usual

def group_containers_by_destination(containers_df):
    grouped_containers = {}
    for dest_id, group in containers_df.groupby("Destination"):
        grouped_containers[dest_id] = (
            group.sort_values(by="Length", ascending=False)
            .to_dict("records")
        )
    return grouped_containers

def process_instance(instance_id, containers_df, trucks_df, docks_df,verbose=True):
    # --- Préparation des données ---
    truck_list = []
    df_cont  = containers_df[containers_df["Instance"] == instance_id].copy()
    df_trucks = trucks_df[trucks_df["Instance"] == instance_id].copy()
    df_docks = docks_df[docks_df["Instance"] == instance_id].copy()

    if df_docks.empty:
        raise ValueError(f"❌ Aucun dock trouvé pour l’instance {instance_id}")

    df_trucks = df_trucks.sort_values("TruckID").reset_index(drop=True)

    dock_positions = df_docks["Position"].tolist()
    num_docks = len(dock_positions)
    # --- Attribution des quais aux camions (round robin) ---
    for i, row in df_trucks.iterrows():
        assigned_dock_id = dock_positions[i % num_docks]
        assigned_dock_position = docks_df[docks_df['DockID'] == assigned_dock_id]['Position'].iloc[0]
        assigned_dock_position = int(assigned_dock_position)
        truck_list.append({
            'TruckID': row['TruckID'],
            'Capacity': row['Capacity'],
            'InitialCapacity': row['Capacity'],
            'Destination': row['Destination'],
            'AssignedContainers': [],
            'AssignedDockID': assigned_dock_id,
            'AssignedDockPosition': assigned_dock_position,
            'start_loading_time': 0,
            'end_loading_time': 0
        })

    # --- Regrouper les conteneurs par destination (tri décroissant par longueur) ---
    grouped_containers = group_containers_by_destination(df_cont)
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
                unassigned_containers.append(c_id)
                
    # --- Build DataFrame of unassigned containers ---
    if unassigned_containers:
        unassigned_df = containers_df[containers_df["ContainerID"].isin(unassigned_containers)].copy()
        print(f"⚠️ {len(unassigned_df)} unassigned containers found.")
    else:
        unassigned_df = pd.DataFrame(columns=containers_df.columns)
        if verbose:

            print("✅ All containers were successfully assigned.")

    # --- Construire la sortie sous forme de liste ---
    # We'll build a dense list indexed by truck order (1..n) rather than relying on numeric TruckID values
    print(f"DEBUG: len(truck_list) = {len(truck_list)}")
    print(f"DEBUG: len(trucks_df) = {len(trucks_df)}")


    # --- Construire la sortie sous forme de liste ---
# --- Construire la sortie sous forme de liste compactée ---
    trucks_assigned_containers_list = []

    for truck in sorted(truck_list, key=lambda x: int(x["TruckID"])):
        assigned = sorted([int(c) for c in truck["AssignedContainers"]])
        trucks_assigned_containers_list.append(assigned)

    return trucks_assigned_containers_list


    '''# --- Construire la sortie sous forme de liste ---
    df_trucks = trucks_df[trucks_df["Instance"] == instance_id].copy()
    df_trucks = df_trucks.sort_values("TruckID").reset_index(drop=True)

    num_trucks = len(df_trucks)
    trucks_assigned_containers_list = [[] for _ in range(num_trucks)]

    # Mapping TruckID → correct list index
    truck_to_index = { int(row["TruckID"]): idx for idx, row in df_trucks.iterrows() }

    for truck in truck_list:
        tid = truck["TruckID"]
        if tid not in truck_to_index:
            continue  # skip ghost trucks

        idx = truck_to_index[tid]
        trucks_assigned_containers_list[idx] = sorted(int(c) for c in truck["AssignedContainers"])

    return trucks_assigned_containers_list
'''
'''
def binpacking_to_chromosome(trucks_assigned_containers_list,trucks_df,docks_df):
    chromosome = []
    dock_positions = docks_df['Position'].tolist()
  # On parcourt les camions dans l'ordre du DataFrame pour garder la cohérence
    for _, truck in trucks_df.iterrows():
        truck_id = int(truck["TruckID"])
        assigned = []

        # Vérifier si le TruckID existe dans la liste (pour éviter les index out of range)
        if truck_id < len(trucks_assigned_containers_list):
            assigned = trucks_assigned_containers_list[truck_id]
        else:
            assigned = []

        dock_position = truck.get("DockPosition", dock_positions[truck_id % len(dock_positions)])

        
        chromosome.extend([assigned, 0, dock_position, 0])

    return chromosome
'''
'''def binpacking_to_chromosome(trucks_assigned_containers_list, trucks_df, docks_df, instance_id):
    chromosome = []

    # Garder uniquement les trucks de l'instance
    df_trucks = trucks_df[trucks_df["Instance"] == instance_id].copy()
    df_trucks = df_trucks.sort_values("TruckID").reset_index(drop=True)

    num_trucks = len(trucks_assigned_containers_list)

    # Vérification de cohérence
    if num_trucks != len(df_trucks):
        print("⚠️ WARNING: mismatch between binpacking trucks and trucks_df!")
        print("  → len(binpacking) =", num_trucks)
        print("  → len(df_trucks)  =", len(df_trucks))
        print("  On aligne sur binpacking uniquement.")

    for i in range(1,num_trucks +1):
        assigned = trucks_assigned_containers_list[i]
        dock_position = int(df_trucks.loc[i, "DockPosition"])

        chromosome.extend([assigned, 0, dock_position, 0])

    return chromosome
'''

def binpacking_to_chromosome(trucks_assigned_containers_list, docks_df):
    chromosome = []
    dock_positions = docks_df['Position'].tolist()
    for truck_id, assigned in enumerate(trucks_assigned_containers_list):
        dock_position = dock_positions[truck_id % len(dock_positions)]
        chromosome.extend([assigned, 0, dock_position, 0])
    return chromosome
# --- Functions from binpacking.ipynb ---
def calculate_loading_times_df(chromosome, trucks_df, docks_df):
    """
    Calculates loading times for each truck based on the chromosome and returns a DataFrame.
    """
    truck_ids = trucks_df['TruckID'].tolist()
    dock_posi = docks_df['Position'].tolist()  # ✅ DockID au lieu de Position
    service_time_per_container = 1 # Assuming 1 unit of time per container
    changeover_time = 5 #

    # Extract truck information from the chromosome and create a temporary truck list
    truck_list = []
    for i in range(0, len(chromosome), 4):
        truck_index = i // 4
        if truck_index < len(truck_ids):
            truck_id = truck_ids[truck_index]
            assigned_containers = chromosome[i]
            assigned_dock_position = chromosome[i+2]
            truck_list.append({
                'TruckID': truck_id,
                'AssignedContainers': assigned_containers,
                'AssignedDockPosition': assigned_dock_position,
                'start_loading_time': 0,
                'end_loading_time': 0
            })

    # Sort trucks by assigned dock position and then by TruckID to ensure consistent ordering
    truck_list.sort(key=lambda x: (x['AssignedDockPosition'], x['TruckID']))

    dock_completion_times = {dock_pos: 0 for dock_pos in dock_posi}

    
    loading_times_data = []
    for truck in truck_list:
        assigned_dock_position = truck['AssignedDockPosition']
        if assigned_dock_position not in dock_completion_times:
            print(f"⚠️ Dock {assigned_dock_position} non trouvé dans cette instance.")
            print("→ Docks disponibles :", list(dock_completion_times.keys()))
            continue

        truck['start_loading_time'] = dock_completion_times[assigned_dock_position] + changeover_time
        truck['end_loading_time'] = truck['start_loading_time'] + service_time_per_container * len(truck['AssignedContainers'])
        dock_completion_times[assigned_dock_position] = truck['end_loading_time']

        loading_times_data.append({
            'TruckID': truck['TruckID'],
            # 'AssignedDockID': truck['AssignedDockID'], # Dock ID is not in chromosome
            'AssignedDockPosition': truck['AssignedDockPosition'],
            'start_loading_time': truck['start_loading_time'],
            'end_loading_time': truck['end_loading_time']
        })
    loading_times_df = pd.DataFrame(loading_times_data)
    return loading_times_df