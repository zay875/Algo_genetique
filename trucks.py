import pandas as pd
import random

def generate_trucks(instance_id, D, H, df_docks, Q=6):
    """
    Generate truck data.
    Each truck has a destination, cost, capacity, and assigned dock position.
    """
    random.seed(300 + instance_id)

    CTd = {d: random.randint(200, 800) for d in range(1, D + 1)}  # cost per destination
    trucks = []

    for h in range(1, H + 1):
        dest = random.randint(1, D)
        chosen_dock = df_docks.sample(1).iloc[0]
        dock_pos = chosen_dock["Position"] #attention look for the dock is it the dock position we affect to trucks or the dockID
        added=False
        #capacity = random.randint(5, 12)
        trucks.append([instance_id, h, dest, CTd[dest], Q, dock_pos,added])
    #add a column name to distinguish the old and added trucks

    df = pd.DataFrame(trucks, columns=["Instance", "TruckID", "Destination", "Cost", "Capacity", "DockPosition","added"])
    return df

