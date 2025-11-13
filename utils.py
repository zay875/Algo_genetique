
import random
import pandas as pd
import copy
'''
data_containers = {
    'Instance': [12, 12, 12, 12, 12, 12],
    'ContainerID': [1, 2, 3, 4, 5, 6],
    'Length': [2, 4, 2, 5, 10, 4],
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
'''

# Load dataframes as usual
'''
containers_df = pd.read_csv("C:/Users/Taieb/Algo_genetique/containers_all.csv")
trucks_df = pd.read_csv("C:/Users/Taieb/Algo_genetique/trucks_all.csv")
docks_df = pd.read_csv("C:/Users/Taieb/Algo_genetique/docks_all.csv")
INSTANCE_ID = 12
containers_df = containers_df[containers_df["Instance"] == INSTANCE_ID].copy()
trucks_df = trucks_df[trucks_df["Instance"] == INSTANCE_ID].copy()
docks_df = docks_df[docks_df["Instance"] == INSTANCE_ID].copy()
#truck_cost_df = pd.read_csv("truck_cost.csv")
'''
def generate_random_chromosome(trucks_df, docks_df, containers_df):
    chromosome = []
    dock_positions = docks_df['Position'].tolist()
    
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


def verify_solution_feasibility(chromosome, trucks_df, containers_df,instance_id):
    """
    Vérifie si une solution (chromosome) est faisable.
    Retourne un dictionnaire contenant les erreurs et un booléen de faisabilité.
    """
   
    df_containers = containers_df[containers_df["Instance"] == instance_id].copy()
    df_trucks = trucks_df[trucks_df["Instance"] == instance_id].copy()
    errors = []
    all_assigned_containers = []
   
    # ...existing code...
    df_trucks = df_trucks.sort_values("TruckID").reset_index(drop=True)
    truck_ids = df_trucks['TruckID'].tolist()
    num_trucks = len(truck_ids)
    num_blocks = len(chromosome) // 4
     
    for i in range(num_blocks):
        if i >= num_trucks:
            errors.append(f"⚠️ Bloc chromosome {i} sans camion correspondant (instance {instance_id})")
            continue

        containers_assigned = chromosome[i * 4]
        truck_id = truck_ids[i]

        truck_info = df_trucks.loc[df_trucks["TruckID"] == truck_id].iloc[0]
        truck_capacity = truck_info["Capacity"]
        truck_destination = truck_info["Destination"]

        total_length = 0
        for c_id in containers_assigned:
            cont_rows = df_containers.loc[df_containers["ContainerID"] == c_id]
            if cont_rows.empty:
                errors.append(
                    f"⚠️ Conteneur {c_id} n'existe pas dans l'instance {instance_id}"
                )
                continue  # Passe au suivant

            cont_info = cont_rows.iloc[0]
            total_length += cont_info["Length"]

            #La destination du camion doit correspondre à celle du conteneur qui lui est assigné.
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
    # 3️⃣ Check unassigned containers
    #tout les contenerus doivent etre assigné 
    all_containers = df_containers["ContainerID"].tolist()
    unassigned = [c for c in all_containers if c not in all_assigned_containers]
    if unassigned:
     errors.append(f"⚠️ Conteneurs non assignés : {unassigned}")   

# ...existing code...

    # 2️⃣ Vérifier les conteneurs dupliqués
    #chaque conteneur doit être assigné à un seul camion.
    duplicates = [c for c in set(all_assigned_containers) if all_assigned_containers.count(c) > 1]
    if duplicates:
        errors.append(f"⚠️ Conteneurs assignés plusieurs fois : {duplicates}")

    feasible = len(errors) == 0
    return feasible, errors

