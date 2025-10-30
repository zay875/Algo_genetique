import pandas as pd
import random
'''
def generate_docks(instance_id, K=5):
    """
    Generate dock data.
    Each dock has a unique position.
    """
    random.seed(200 + instance_id)

    dock_positions = random.sample(range(2, 7), min(K, 5))  # unique positions 1–5
    docks = []
    for k in range(1, K + 1):
        Rk = dock_positions[(k - 1) % len(dock_positions)]
        docks.append([instance_id, k, Rk])

    df = pd.DataFrame(docks, columns=["Instance", "DockID", "Position"])
    return df
'''

def generate_docks(instance_id, K=5):
    """
    Generate dock data.
    Each dock has a unique position.
    """
    random.seed(200 + instance_id)
    dock_positions = random.sample(range(1, K + 1), K)  # K positions uniques
    docks = []
    for k in range(1, K + 1):
        Rk = dock_positions[k - 1]
        docks.append([instance_id, k, Rk])
    return pd.DataFrame(docks, columns=["Instance", "DockID", "Position"])


