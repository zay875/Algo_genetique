
import pandas as pd
import random
from containers import generate_containers
from docks import generate_docks
from trucks import generate_trucks

import random
random.seed(42)  # 


def create_missing_trucks(instance_id, missing_dests, containers_demand, df_docks, K, cost_map=None, default_cost=111):
    """
    Create new trucks for destinations that exist in containers but not in trucks.
    Each truck has enough capacity (with 10% margin) to cover all containers for that destination.
    """
    new_trucks = []

    for dest in missing_dests:
        dock_id = (
            random.choice(df_docks["Position"])
            
        )
        cost = cost_map.get(dest, default_cost) if cost_map else default_cost
        new_trucks.append({
            "Instance": instance_id,
            "TruckID": f"T_new_{dest}",
            "Destination": dest,
            "Capacity":6,
            "Cost": cost,
            "DockPosition": dock_id,
            "added":True
        })

    return pd.DataFrame(new_trucks)


def compute_additional_trucks_needed(instance_id, containers_demand, trucks_capacity, df_docks, per_truck_capacity, cost_map=None, default_cost=111):
    """
    Compute and return a DataFrame of additional trucks needed so that capacity meets demand.

    - containers_demand: Series mapping Destination -> total length demand
    - trucks_capacity: Series mapping Destination -> total capacity available
    - df_docks: dataframe of docks (used to pick DockPosition)
    - per_truck_capacity: capacity assigned to each created truck (Q in generator)

    Returns: DataFrame of new truck rows (may be empty)
    """
    new_trucks = []
    for dest in sorted(set(containers_demand.index).union(trucks_capacity.index)):
        demand = containers_demand.get(dest, 0)
        capacity = trucks_capacity.get(dest, 0)
        if capacity < demand:
            additional_capacity_needed = int(demand - capacity)
            # number of trucks required (ceiling division)
            num_additional_trucks = (additional_capacity_needed // per_truck_capacity) + (
                1 if additional_capacity_needed % per_truck_capacity > 0 else 0
            )
            for _ in range(num_additional_trucks):
                dock_id = random.choice(df_docks["DockID"].tolist())
                new_truck_id = f"T_extra_{dest}_{random.randint(1000,9999)}"
                cost = cost_map.get(dest, default_cost) if cost_map else default_cost
                new_trucks.append({
                    "Instance": instance_id,
                    "TruckID": new_truck_id,
                    "Destination": dest,
                    "Capacity": per_truck_capacity,
                    "Cost": cost,
                    "DockPosition": dock_id,
                    "added": True,
                })

    if new_trucks:
        return pd.DataFrame(new_trucks)
    return pd.DataFrame(columns=["Instance","TruckID","Destination","Capacity","Cost","DockPosition","added"])


def generate_instance(instance_id, D, N, H, K=7, Q=6, CE=0.5):
    """
    Main generator for one instance.
    Uses the three separate modules: containers, docks, trucks.
    """
    df_docks = generate_docks(instance_id, K)
    df_containers = generate_containers(instance_id, D, N)
    df_trucks = generate_trucks(instance_id, D, H, df_docks, Q)

    # Build cost map per destination from existing trucks (if any)
    cost_map = None
    if 'Destination' in df_trucks.columns and 'Cost' in df_trucks.columns:
        # prefer the most common/first cost seen for a destination
        cost_map = df_trucks.groupby('Destination')['Cost'].first().to_dict()

    # verify the capacity and destination constraint for the containers and trucks
    #for each destination in the coantainers instance that there are enough trucks with enough capacity for that destination
    if 'Destination' in df_containers.columns and 'Destination' in df_trucks:
       # Group by destination
        containers_demand = df_containers.groupby("Destination")["Length"].sum()
        trucks_capacity = df_trucks.groupby("Destination")["Capacity"].sum()

        # Get sets of destinations
        container_dests = set(containers_demand.index)
        truck_dests = set(trucks_capacity.index)

        # === Diagnostic test: destination mismatches ===
        missing_in_trucks = container_dests - truck_dests
        missing_in_containers = truck_dests - container_dests

        if missing_in_trucks:
            print(f"[Instance {instance_id}] Destinations in containers but NOT in trucks: {sorted(missing_in_trucks)}")
            # create a truck with the missing destination and enough capacity
            new_trucks_df = create_missing_trucks(instance_id, missing_in_trucks, containers_demand, df_docks, K, cost_map=cost_map)
            df_trucks = pd.concat([df_trucks, new_trucks_df], ignore_index=True)
        if missing_in_containers:
            print(f"[Instance {instance_id}] Destinations in trucks but NOT in containers: {sorted(missing_in_containers)}")
        

        # === Capacity check ===
        all_dests = container_dests.union(truck_dests)

        # Use helper to compute additional trucks needed and append them
        additional_trucks_df = compute_additional_trucks_needed(instance_id, containers_demand, trucks_capacity, df_docks, per_truck_capacity=Q, cost_map=cost_map)
        if not additional_trucks_df.empty:
            for _, row in additional_trucks_df.iterrows():
                print(f"[Instance {instance_id}] Capacity insufficient for destination {row['Destination']}: adding truck {row['TruckID']} (Capacity={row['Capacity']})")
            df_trucks = pd.concat([df_trucks, additional_trucks_df], ignore_index=True)

    else:
        print(f"[Instance {instance_id}] Missing 'Destination' column in containers or trucks dataset.")
    params = pd.DataFrame({
        "Instance": [instance_id]*10,
        "Parameter": ["N", "K", "D", "H", "Q", "CE", "Y", "I", "V", "M"],
        "Value": [N, K, D, H, Q, CE, 10, 2, 5, 10000]
    })


    return df_containers, df_trucks, df_docks, params


# ==== Generate 30 Random Instances ====
num_instances = 30
all_containers, all_trucks, all_docks, all_params = [], [], [], []

for idx in range(1, num_instances + 1):
    # Randomized parameters for each instance
    D = random.randint(2, 5)    # number of destinations
    N = random.randint(4, 13)   # number of containers
    H = random.randint(5, 10)    # number of trucks
    K = random.randint(3, 7)    # number of docks

    c, t, d, p = generate_instance(instance_id=idx, D=D, N=N, H=H, K=K, Q=6, CE=0.5)

    
    all_containers.append(c)
    all_trucks.append(t)
    all_docks.append(d)
    all_params.append(p)




# ==== Save Outputs ====
pd.concat(all_containers).to_csv("instances_v3/containers_all.csv", index=False)
pd.concat(all_trucks).to_csv("instances_v3/trucks_all.csv", index=False)
pd.concat(all_docks).to_csv("instances_v3/docks_all.csv", index=False)
pd.concat(all_params).to_csv("instances_v3/parameters_all.csv", index=False)

print("30 random instances generated and saved using modular architecture.")

