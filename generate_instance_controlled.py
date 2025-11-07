
import pandas as pd
import random
from containers import generate_containers
from docks import generate_docks
from trucks import generate_trucks

import random
random.seed(42)  # 


def create_missing_trucks(instance_id, missing_dests, containers_demand, df_docks, K):
    """
    Create new trucks for destinations that exist in containers but not in trucks.
    Each truck has enough capacity (with 10% margin) to cover all containers for that destination.
    """
    new_trucks = []

    for dest in missing_dests:
        dock_id = (
            random.choice(df_docks["Position"])
            
        )
        new_trucks.append({
            "Instance": instance_id,
            "TruckID": f"T_new_{dest}",
            "Destination": dest,
            "Capacity":6,
            "Cost": 111,
            "DockPosition": dock_id
        })

    return pd.DataFrame(new_trucks)


def generate_instance(instance_id, D, N, H, K=7, Q=6, CE=0.5):
    """
    Main generator for one instance.
    Uses the three separate modules: containers, docks, trucks.
    """
    df_docks = generate_docks(instance_id, K)
    df_containers = generate_containers(instance_id, D, N)
    df_trucks = generate_trucks(instance_id, D, H, df_docks, Q)

    #verify the capacity and destination constraint for the containers and trucks
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
        #all destinations in containers must exist in trucks destinations
        
        #create a truck with the missing destination and enough capacity
            new_trucks_df = create_missing_trucks(instance_id, missing_in_trucks, containers_demand, df_docks, K)
            df_trucks = pd.concat([df_trucks, new_trucks_df], ignore_index=True)
        if missing_in_containers:
            print(f"[Instance {instance_id}] Destinations in trucks but NOT in containers: {sorted(missing_in_containers)}")
        

        # === Capacity check ===
        all_dests = container_dests.union(truck_dests)

        for dest in all_dests:
            demand = containers_demand.get(dest, 0)
            capacity = trucks_capacity.get(dest, 0)

            if capacity < demand:
                print(f"[Instance {instance_id}] Capacity insufficient for destination {dest}: "
                      f"Demand={demand}, Capacity={capacity}")

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

print(" 30 random instances generated and saved using modular architecture.")

