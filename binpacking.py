
import pandas as pd
import csv
# Load dataframes as usual
containers_df = pd.read_csv("C:/Users/Taieb/Algo_genetique/containers_all (1).csv")
trucks_df = pd.read_csv("C:/Users/Taieb/Algo_genetique/trucks_all (1).csv")
docks_df = pd.read_csv("C:/Users/Taieb/Algo_genetique/docks_all (1).csv")
def process_instance(instance_id, containers_df, trucks_df, docks_df):
    # --- Filter data for this instance ---
    df_containers = containers_df[containers_df["Instance"] == instance_id].copy()
    df_trucks = trucks_df[trucks_df["Instance"] == instance_id].copy()
    instance_docks_df = docks_df[docks_df["Instance"] == instance_id].copy()

    # --- Build truck list ---
    truck_list = []
    dock_ids = instance_docks_df['DockID'].tolist()
    num_docks = len(dock_ids)

    for i, row in df_trucks.iterrows():
        assigned_dock_id = dock_ids[i % num_docks]
        assigned_dock_position = instance_docks_df[instance_docks_df['DockID'] == assigned_dock_id]['Position'].iloc[0]

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
    for dest_id, group in df_containers.groupby("Destination"):
        containers_list = group.sort_values(by="Length", ascending=False).to_dict("records")
        grouped_containers[dest_id] = containers_list

    assigned_containers_count = 0
    unassigned_containers = []

    for dest_id, containers_in_dest in grouped_containers.items():
        for truck in truck_list:
            if truck['Destination'] == dest_id:
                containers_to_process = list(containers_in_dest)
                containers_in_dest[:] = []
                for container in containers_to_process:
                    is_assigned = any(container['ContainerID'] in tr['AssignedContainers'] for tr in truck_list)
                    if not is_assigned and truck['Capacity'] >= container['Length']:
                        truck['AssignedContainers'].append(container['ContainerID'])
                        truck['Capacity'] -= container['Length']
                        assigned_containers_count += 1
                    else:
                        containers_in_dest.append(container)

    for dest_id, containers_in_dest in grouped_containers.items():
        unassigned_containers.extend(containers_in_dest)

    max_truck_id = max([truck['TruckID'] for truck in truck_list])
    trucks_assigned_containers_list = [[] for _ in range(max_truck_id + 1)]

    for truck in truck_list:
        truck_id = truck['TruckID']
        truck_assigned_list = sorted([int(c) for c in truck['AssignedContainers']])
        trucks_assigned_containers_list[truck_id] = truck_assigned_list

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
