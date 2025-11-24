import pandas as pd
import ast
import re


def parse_benchmark_instance(path, instance_id="X"):
    """
    Convertit une instance du benchmark .txt en containers_df, trucks_df, docks_df
    """

    # Lire fichier
    with open(path, "r") as f:
        text = f.read()

    def extract_value(name):
        """
        Extrait un entier : N=4;
        """
        match = re.search(rf"{name}\s*=\s*(\d+)", text)
        return int(match.group(1)) if match else None

    def extract_list(name):
        """
        Extrait liste du style L = [3 5 2 3]
        """
        match = re.search(rf"{name}\s*=\s*\[([^\]]+)\]", text)
        if not match:
            return []
        raw = match.group(1)
        return list(map(int, re.findall(r"\d+", raw)))

    def extract_matrix(name):
        """
        Extrait une matrice style :
        R = [
            3 8 13 18 23
            28 33 38 43 48
        ];
        """
        pattern = rf"{name}\s*=\s*\[([\s\S]*?)\];"
        match = re.search(pattern, text)
        if not match:
            return []

        raw = match.group(1).strip().split("\n")
        matrix = []
        for row in raw:
            nums = list(map(int, re.findall(r"\d+", row)))
            matrix.append(nums)
        return matrix


    # Extraction
    N = extract_value("N")
    H = extract_value("H")
    Q = extract_value("Q")
    D = extract_value("D")
    K = extract_value("K")
    Ce = extract_value("C_e")

    L = extract_list("L")          # longueurs
    P = extract_list("P")          # positions conteneurs
    G = extract_matrix("G")        # destinations conteneurs (1 ligne)
    R = extract_matrix("R")        # positions quais

    Cd = extract_list("C_d")       # coût par destination
    cost_for_destination = Cd[0]   # 351 dans ton exemple


    # -------------------------
    # BUILD containers_df
    # -------------------------
    data_cont = []
    for i in range(N):
        data_cont.append({
            "Instance": instance_id,
            "ContainerID": i + 1,
            "Length": L[i],
            "Position": P[i],
            "Destination": G[0][i]   # unique ligne
        })

    containers_df = pd.DataFrame(data_cont)


    # -------------------------
    # BUILD docks_df
    # flatten R
    # -------------------------
    dock_positions = [pos for row in R for pos in row]

    docks_df = pd.DataFrame({
        "Instance": instance_id,
        "DockID": list(range(1, len(dock_positions) + 1)),
        "Position": dock_positions
    })


    # -------------------------
    # BUILD trucks_df
    # -------------------------
    # Assign dock positions in order
    dock_cycle = dock_positions[:H]

    data_trucks = []
    for t in range(H):
        data_trucks.append({
            "Instance": instance_id,
            "TruckID": t + 1,
            "Destination": D,               # unique destination
            "Cost": cost_for_destination,   # 351
            "Capacity": Q,                  # capacité
            "DockPosition": dock_cycle[t],
            "added": False
        })

    trucks_df = pd.DataFrame(data_trucks)

    return containers_df, trucks_df, docks_df



containers_df, trucks_df, docks_df = parse_benchmark_instance(
    "instance_chargui/Inst_4_1_4.txt", instance_id=1
)


print(containers_df.head())
print(trucks_df.head())
print(docks_df.head())
print(containers_df["Instance"].unique())

# ==== Save Outputs ====

containers_df.to_csv("instance_chargui/containers_Inst_4_1_4.csv", index=False)
trucks_df.to_csv("instance_chargui/trucks_Inst_4_1_4.csv", index=False)
docks_df.to_csv("instance_chargui/docks_Inst_4_1_4.csv", index=False)

print("CSV files saved successfully!")
