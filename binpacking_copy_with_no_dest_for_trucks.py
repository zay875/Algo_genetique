
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
def group_trucks_by_destination(trucks_df):
    grouped_trucks = {}
    for dest_id, group in trucks_df.groupby("Destination"):
        grouped_trucks[dest_id] = (
            group.sort_values(by="Capacity", ascending=False)
            .to_dict("records")
        )
    return grouped_trucks
def process_instance(instance_id, containers_df, trucks_df, docks_df):
    """
    Prépare les données pour le binpacking.
    Règle : dans notre heuristique, tous les camions
    peuvent transporter n'importe quelle destination de conteneur.
    """

    print(f"the instance :{instance_id}")

    # ===============================
    # FILTRER LES CONTENEURS & CAMIONS DE L'INSTANCE
    # ===============================

    df_cont = containers_df[containers_df["Instance"] == instance_id].copy()
    df_trucks = trucks_df[trucks_df["Instance"] == instance_id].copy()
    df_docks = docks_df[docks_df["Instance"] == instance_id].copy()

    # ===============================
    # GROUPEMENT DES CONTENEURS PAR DESTINATION
    # (utile si ton heuristique trie selon G)
    # ===============================

    grouped_containers = {
        dest: rows.to_dict("records")
        for dest, rows in df_cont.groupby("Destination")
    }

    print("grouped containers", grouped_containers)

    # ===============================
    # PAS DE GROUPEMENT DES CAMIONS PAR DESTINATION
    # → RÈGLE : TOUS LES CAMIONS PEUVENT SERVIR TOUTES LES DESTINATIONS
    # ===============================

    trucks_for_all = df_trucks.to_dict("records")

    print("\n=== Vérification brute des destinations dans df_trucks ===")
    print(df_trucks["Destination"].unique())
    print(df_trucks)

    # Pour affichage
    grouped_trucks_display = {
        "ALL": trucks_for_all
    }
    print("grouped trucks", grouped_trucks_display)

    # ===============================
    # CONSTRUCTION DE LA LISTE DE CAMIONS
    # ===============================

    trucks_list = []
    for _, row in df_trucks.iterrows():
        trucks_list.append({
            "TruckID": row["TruckID"],
            "Destination": row["Destination"],   # même si la destination n’est plus filtrante
            "Capacity": row["Capacity"],
            "DockPosition": row["DockPosition"],
            "AssignedDockID": [],
            "AssignedDockPosition": []
        })
    trucks_assigned_containers_list = [[] for _ in range(len(trucks_list))]
    truck_index_map = {t["TruckID"]: idx for idx, t in enumerate(trucks_list)}
    print("\n=== TRUCK LIST BEFORE ASSIGNMENT ===")
    unassigned_containers = []
    for t in trucks_list:
        print(t["TruckID"], "dest=", t["Destination"], "cap=", t["Capacity"],
              "AssignedDockID", t["AssignedDockID"],
              "AssignedDockPosition", t["AssignedDockPosition"])

    # ===============================
    # BINPACKING : TU UTILISES TOUS LES CAMIONS POUR TOUTES DESTINATIONS
    # ===============================

    truck_container_assignments = []

    for dest_id, cont_list in grouped_containers.items():
        # Règle : tous les camions sont disponibles pour toutes destinations
        trucks_for_dest = trucks_for_all

        # Ton code d’affectation existant ici :
        # Index du camion qu'on va essayer en avançant
        i = 0  

        # Liste des camions déjà utilisés pour cette destination
        used_trucks = []  

        for container in cont_list:

            length = container["Length"]
            c_id = container["ContainerID"]

            # 1️⃣ Vérifier d'abord dans les camions déjà utilisés
            feasible_used = [
                t for t in used_trucks if t["Capacity"] >= length
            ]

            if feasible_used:
                # Meilleur camion = capacité minimale mais suffisante
                best_truck = min(feasible_used, key=lambda t: t["Capacity"])

            else:
                # 2️⃣ Sinon avancer dans les camions triés par capacité descendante
                assigned = False

                while i < len(trucks_for_dest):
                    candidate = trucks_for_dest[i]

                    if candidate["Capacity"] >= length:
                        best_truck = candidate
                        assigned = True
                        break
                    i += 1

                if not assigned:
                    # Aucun camion ne peut le prendre
                    unassigned_containers.append(c_id)
                    continue

                # Ajouter ce camion à la liste des camions utilisés
                used_trucks.append(best_truck)

            # 3️⃣ Mise à jour capacité du camion utilisé
            best_truck["Capacity"] -= length

            # 4️⃣ Affecter ce conteneur dans trucks_assigned_containers_list
            truck_id = best_truck["TruckID"]
            idx = truck_index_map[truck_id]
            #get only the container id to append in container_assigned_list
            assigned_container_id=container["ContainerID"]
            trucks_assigned_containers_list[idx].append(assigned_container_id)
        # Exemple générique :
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
#function to calculate the dockID like in Chargui
def dock_assignement(trucks_assigned_containers_list, containers_positions, docks_positions):
    truck_dock_assignments = []

    # docks_positions : {dockID -> position}
    dock_ids = list(docks_positions.keys())

    for truck in trucks_assigned_containers_list:

        if len(truck) == 0:
            avg_pos = 0
        else:
            avg_pos = sum(containers_positions[c] for c in truck) / len(truck)

        # choisir le dock dont la position est la plus proche
        best_dock = min(
            dock_ids,
            key=lambda d: abs(docks_positions[d] - avg_pos)
        )

        truck_dock_assignments.append(best_dock)

    return truck_dock_assignments

'''
def binpacking_to_chromosome(trucks_assigned_containers_list, docks_df):
    chromosome = []
    dock_positions = docks_df['Position'].tolist()
    for truck_id, assigned in enumerate(trucks_assigned_containers_list):
        dock_position = dock_positions[truck_id % len(dock_positions)]
        chromosome.extend([assigned, 0, dock_position, 0])
    return chromosome
'''
#calculating and assigning docks
def binpacking_to_chromosome(trucks_assigned_containers_list, docks_df, containers_df,instance_id):
    df_cont  = containers_df[containers_df["Instance"] == instance_id].copy()
    
    df_docks = docks_df[docks_df["Instance"] == instance_id].copy()
    chromosome = []

    # dict : containerID -> position
    containers_positions = dict(zip(df_cont["ContainerID"], containers_df["Position"]))

    # dict : dockID -> position
    docks_positions = dict(zip(df_docks["DockID"], df_docks["Position"]))
    print("docks_positions=", docks_positions)

    # dock IDs calculés par ton algorithme
    assigned_docks = dock_assignement(
        trucks_assigned_containers_list,
        containers_positions,
        docks_positions
    )
    print(f"the docks : {assigned_docks}")
    # construction du chromosome
    for i, assigned in enumerate(trucks_assigned_containers_list):

        dock_id = assigned_docks[i]         # un DockID valide (1..n)
        dock_position = docks_positions[dock_id]  # récupérer la Position

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