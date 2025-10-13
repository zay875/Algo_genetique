import pandas as pd
import random

def generate_containers(instance_id, D, N, Li_choices=None):
    """
    Generate container data (Chargui et al. 2019 style).
    Each container has a length, position, and destination dock.
    """
    if Li_choices is None:
        Li_choices = [1, 2, 3, 4, 5]  # allowed lengths (units)
        
    random.seed(100 + instance_id)

    containers = []
    for i in range(1, N + 1):
        Li = random.choice(Li_choices)
        Pi = random.randint(1, 75)  # position in dock area
        d = random.randint(1, D)    # random destination
        containers.append([instance_id, i, Li, Pi, d])

    df = pd.DataFrame(containers, columns=["Instance", "ContainerID", "Length", "Position", "Destination"])
    return df

