
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
    dock_ids = docks_df['Position'].tolist()
    num_docks = len(dock_ids)
    
    # --- Attribution des quais aux camions (round robin) ---
    for i, row in trucks_df.iterrows():
        assigned_dock_id = dock_ids[i % num_docks]
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
    grouped_containers = group_containers_by_destination(containers_df)
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
    print(f"DEBUG: first rows of trucks_df:\n{trucks_df.head()}")


    # --- Construire la sortie sous forme de liste ---
    max_truck_id = max([truck['TruckID'] for truck in truck_list])
   
    trucks_assigned_containers_list = [[] for _ in range(max_truck_id + 1)]

    for truck in truck_list:
        truck_id = truck['TruckID']
        truck_assigned_list = sorted([int(c) for c in truck['AssignedContainers']])
        trucks_assigned_containers_list[truck_id] = truck_assigned_list
    # --- Vérifier si la longueur totale des conteneurs <= somme des capacités des camions pour chaque destination ---
    # --- Vérifier si la longueur totale des conteneurs <= somme des capacités des camions pour chaque destination ---
    # --- Et si non, ajouter automatiquement des camions pour compenser la différence ---

    #grouped_trucks = {}
    '''
      for dest_id, group in trucks_df.groupby("Destination"):
        grouped_trucks[dest_id] = (
            group.sort_values(by="Capacity", ascending=False)
            .to_dict("records")
        )
    grouped_remaining_containers=group_containers_by_destination(unassigned_df)
    new_trucks = []  # Pour stocker les nouveaux camions ajoutés
    default_capacity = 6  # ✅ Capacité fixe de tous les camions

    for dest_id in grouped_remaining_containers.keys():
        total_container_length = sum(container["Length"] for container in grouped_remaining_containers[dest_id])
        avg_capacity = default_capacity  # ✅ Tous les camions ont une capacité de 6
        num_new_trucks = int(total_container_length // avg_capacity) + (1 if total_container_length % avg_capacity > 0 else 0)

        
    #check if trucks_df is empty
        if trucks_df is None or trucks_df.empty:
            print("⚠️ trucks_df vide — création impossible.")
            return [], pd.DataFrame(columns=["Instance","TruckID","Destination","Cost","Capacity","DockPosition"])

        if not truck_list:
            print("⚠️ Aucun camion trouvé — trucks_df vide.")
            return [], trucks_df
        max_truck_id = int(max([truck['TruckID'] for truck in truck_list]))


            # --- Trouver le prochain ID disponible ---
        #max_truck_id = trucks_df["TruckID"].max() + 1

        for i in range(num_new_trucks):
                new_trucks.append({
                    "TruckID": max_truck_id + i,
                    "Capacity": avg_capacity,
                    "Destination": dest_id,
                    "Instance": instance_id,
                    'Cost': 608,
                    'Capacity':6,
                    'DockPosition':7
                })
        for new_truck in new_trucks:
                truck_list.append({
                'TruckID': int(new_truck['TruckID']),
                'Capacity': new_truck['Capacity'],
                'InitialCapacity': new_truck['Capacity'],
                'Destination': new_truck['Destination'],
                'AssignedContainers': [],
                'AssignedDockID': 2,
                'AssignedDockPosition': new_truck.get('DockPosition', None),
                'start_loading_time': 0,
                'end_loading_time': 0
        
                                    })
        for truck in truck_list:
            truck_id = int(truck['TruckID'])
            truck_assigned_list = sorted([int(c) for c in truck['AssignedContainers']])

            # Si truck_id dépasse la taille actuelle, on agrandit la liste
        if truck_id >= len(trucks_assigned_containers_list):
            trucks_assigned_containers_list.extend([[] for _ in range(truck_id - len(trucks_assigned_containers_list) + 1)])

        trucks_assigned_containers_list[truck_id] = truck_assigned_list
        
        #affecter les conteneurs aux nouveaux trucks
        for dest_id_r, containers_in_dest_r in grouped_remaining_containers.items():
            for container in containers_in_dest_r:
                length = container["Length"]
                c_id = container["ContainerID"]

            # 1️⃣ Chercher un camion avec la même destination et assez de capacité
                feasible_trucks_r = [
                    t for t in truck_list
                    if t["Destination"] == dest_id_r and t["Capacity"] >= length
                ]

                if feasible_trucks_r:
                    # Choisir le camion avec la capacité la plus serrée (best fit)
                    best_truck = min(feasible_trucks_r, key=lambda x: x["Capacity"])
                    best_truck["AssignedContainers"].append(c_id)
                    best_truck["Capacity"] -= length
                    # Construire un DataFrame mis à jour avec les camions d’origine + les nouveaux
    updated_trucks_df = pd.concat(
        [trucks_df, pd.DataFrame(new_trucks)],
        ignore_index=True ) if new_trucks else trucks_df.copy()
    print(f"🚚 Nombre total de camions (après ajout éventuel) : {len(truck_list)}")
    print(f"📦 Conteneurs non assignés restants : {len(unassigned_containers)} -> {unassigned_containers}")


    '''
  
    # Assign by truck order (enumeration) to guarantee alignment with trucks_df order used elsewhere
    '''

    for idx, truck in enumerate(truck_list, start=1):
        truck_assigned_list = []
        for c in truck['AssignedContainers']:
            try:
                truck_assigned_list.append(int(c))
            except Exception:
                # keep original value if it cannot be converted to int
                truck_assigned_list.append(c)
        truck_assigned_list = sorted(truck_assigned_list, key=lambda x: int(x) if isinstance(x, (int, float)) or (isinstance(x, str) and x.isdigit()) else str(x))
        trucks_assigned_containers_list[idx] = truck_assigned_list
    '''
    # --- Affichage des conteneurs non assignés ---
    '''
    if unassigned_containers:
        print(f"Conteneurs non assignés : {unassigned_containers}")
    else:
        print(" Tous les conteneurs ont été assignés.")
    '''
    

    
    return trucks_assigned_containers_list




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