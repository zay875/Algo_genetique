
import pandas as pd
import random
from containers import generate_containers
from docks import generate_docks
from trucks import generate_trucks

import random
random.seed(42)  # 

def generate_instance(instance_id, D, N, H, K=7, Q=6, CE=0.5):
    """
    Main generator for one instance.
    Uses the three separate modules: containers, docks, trucks.
    """
    df_docks = generate_docks(instance_id, K)
    df_containers = generate_containers(instance_id, D, N)
    df_trucks = generate_trucks(instance_id, D, H, df_docks, Q)

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
pd.concat(all_containers).to_csv("containers_all.csv", index=False)
pd.concat(all_trucks).to_csv("trucks_all.csv", index=False)
pd.concat(all_docks).to_csv("docks_all.csv", index=False)
pd.concat(all_params).to_csv("parameters_all.csv", index=False)

print(" 30 random instances generated and saved using modular architecture.")

