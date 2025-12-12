
# run_exact_all_instances.py
from gurobipy import Model, GRB, quicksum
import pandas as pd
import sys
import time
import re
import os


INPUT_FOLDER = "Benchmark_instances_set_for_Sustainability_2019/instances/"
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
        pattern = rf"{name}\s*=\s*\[([\s\S]*?)\];"
        match = re.search(pattern, text)
        if not match:
            return []

        raw_lines = match.group(1).strip().splitlines()
        matrix = []
        for row in raw_lines:
            # On récupère tous les entiers de la ligne
            nums = list(map(int, re.findall(r"\d+", row)))
            if not nums:
                # ligne vide → on l'ignore
                continue
            matrix.append(nums)
        return matrix



    # Extraction
    N = extract_value("N")
    H = extract_value("H")
    Q = extract_value("Q")
    D = extract_value("D")
    K = extract_value("K")


    L = extract_list("L")          # longueurs
    P = extract_list("P")          # positions conteneurs
    G = extract_matrix("G")        # destinations conteneurs ()
    R_raw = extract_matrix("R")   # 3 lignes * 5 colonnes
    R = [val for row in R_raw for val in row]  # aplatissement
        # positions quais

    C_d = extract_list("C_d")       # coût par destination
    



    return N,H,Q,D,K,L,P,G,R,C_d

# Parcourir tous les fichiers .txt
instance_files = [f for f in os.listdir(INPUT_FOLDER) if f.endswith(".txt")]

print(f"{len(instance_files)} fichiers trouvés.")
results = []

for idx, filename in enumerate(instance_files, start=1):
    instance_path = os.path.join(INPUT_FOLDER, filename)
    try:
        print(f"\n🔄 Conversion de : {filename}")
        # Identifiant unique basé sur l'ordre ou sur le nom
        #instance_id = os.path.splitext(filename)[0]
        
        instance_name = os.path.splitext(filename)[0]
        instance_id = int(re.findall(r"\d+", instance_name)[0])   

        print(f"the instances numbers: {instance_id}")


        # Extraire les paramètres
        N,H,Q,D,K,L,P,G,R,C_d= parse_benchmark_instance(instance_path,instance_id=instance_id)
        C_E = 0.5
    except Exception as e:
        print(f" ERREUR lors de la conversion de {filename} : {e}")
    print(f"\n === Résolution exacte pour l'instance {instance_id} ===")
    print(f"N,H,Q,D,K,C_E,L,P,G,R,C_d: {N,H,Q,D,K,C_E,L,P,G,R,C_d}")
    
    N_list = list(range(1, N + 1))  # les conteneurs commencent à 1
    H_list = list(range(1, H + 1))  # camions
    K_list = list(range(1, K + 1))  # quais
    D_list = list(range(D))         # destinations 0…D-1
    
    # Données de base
    W1, W2 = 0.5, 0.5
    M = 1000
    Y = 12
    V = 5
    I = 10
    

    # === Modèle ===
    m = Model(f"Instance_{instance_id}_Transport_Energie")
    # Limite de temps : 2 hours
    m.setParam("TimeLimit", 7200)

    # Variables
    a = m.addVars(H_list, D_list, vtype=GRB.BINARY, name="a")# d is destination of the truck h
    x = m.addVars(H_list, K_list, vtype=GRB.BINARY, name="x") #truck h is assigned to dock k
    p = m.addVars(N_list, H_list, vtype=GRB.BINARY, name="p")# container n is assigned to truck h
    z = m.addVars(N_list, H_list, vtype=GRB.CONTINUOUS, name="z") #area
    d_abs = m.addVars(N_list, K_list, vtype=GRB.CONTINUOUS, name="d_abs")
    v_used = m.addVars(H_list, vtype=GRB.BINARY, name="v")
    n = m.addVars(H_list, H_list, vtype=GRB.BINARY, name="n") #same dock for two trucks
    b = m.addVars(H_list, vtype=GRB.CONTINUOUS, name="b")
    q = m.addVars(H_list, vtype=GRB.CONTINUOUS, name="q")

    # === Objectif ===
    F1 = quicksum(C_d[d] * a[h, d] for h in H_list for d in D_list)
    F2 = C_E * quicksum(z[i, h] for i in N_list for h in H_list)
    m.setObjective(W1 * F1 + W2 * F2, GRB.MINIMIZE)

    # === Contraintes principales ===
    # (1) Chaque conteneur assigné à un camion
    for i in N_list:
        m.addConstr(quicksum(p[i, h] for h in H_list) == 1)

    # (2) Capacité
    for h in H_list:
        m.addConstr(quicksum(L[i-1] * p[i, h] for i in N_list) <= Q)

    # (3) Valeur absolue pour la distance
    for i in N_list:
        for k in K_list:
            m.addConstr(d_abs[i, k] >= P[i-1] - R[k-1])
            m.addConstr(d_abs[i, k] >= R[k-1] - P[i-1])

    # (4) Définition de z[i,h]
    for i in N_list:
        for h in H_list:
            for k in K_list:
                m.addConstr(z[i, h] >= 2 * d_abs[i, k] + Y * L[i-1] - M * (2 - (p[i, h] + x[h, k])))

    # (5) Contrainte de destination
    '''m.addConstrs((
        p[i, h] + p[j, h] <= quicksum(G[d, i] * G[d, j] for d in D) + 1
        for i in N for j in N if i != j for h in H
    ))
    '''
    m.addConstrs((
    p[i, h] + p[j, h] <= quicksum(G[d][i-1] * G[d][j-1] for d in D_list) + 1
    for i in N_list for j in N_list if i != j for h in H_list
))

    # (6) Camion utilisé
    m.addConstrs((p[i, h] <= v_used[h] for h in H_list for i in N_list))

    # (7) Destination du camion
    '''
    m.addConstrs((a[h, d] <= G[d, i] + 1 - p[i, h] for i in N for h in H for d in D))
    m.addConstrs((v_used[h] == quicksum(a[h, d] for d in D) for h in H))
    '''
    m.addConstrs((a[h, d] >= p[i, h] * G[d][i-1]for h in H_list for d in D_list for i in N_list))
    m.addConstrs((quicksum(a[h, d] for d in D_list) == v_used[h]for h in H_list))

    # (8) Assignation au quai
    m.addConstrs((quicksum(x[h, k] for k in K_list) == v_used[h] for h in H_list))
      
    #ajouter une limite pour les quai utilisé, max 2 camions sur le quai
    #m.addConstrs((quicksum(x[h, k] for h in H) <= 2 for k in K),
             #name="DockCapacityConstraint")

    # (9) Contraintes d’ordre sur les quais
    m.addConstrs((x[h, k] + x[g, k] - 1 <= n[h, g] + n[g, h] for h in H_list for g in H_list if h != g for k in K_list))
    m.addConstrs((n[h, g] + n[g, h] <= 1 for h in H_list for g in H_list))

    # (10) Timing
    m.addConstrs((b[g] >= 0 for g in H_list))
    m.addConstrs((b[g] >= q[h] + V - M * (1 - n[g, h]) for h in H_list for g in H_list))
    m.addConstrs((q[h] == b[h] + I * quicksum(p[i, h] for i in N_list) for h in H_list))

    # === Résolution ===

    # --- Solve ---
    start_time = time.time()
    m.optimize()
    exec_time = round(time.time() - start_time, 3)

    # === Résultats ===
    status = m.Status
    mipgap = m.MIPGap if status in [GRB.OPTIMAL, GRB.TIME_LIMIT] and m.SolCount > 0 else None
    nodes = m.NodeCount

    # --- TIME LIMIT ---
    if status == GRB.TIME_LIMIT:
        print(f"⚠️ Instance {instance_id} stoppée par la limite de temps ({exec_time}s)")
        results.append({
            "Instance": instance_id,
            "file name": filename,
            "containers": N,
            "Destinations": D,
            "Trucks": H,
            "Docks": K,
            "Objective": m.ObjVal if m.SolCount > 0 else None,
            "F1": F1.getValue() if m.SolCount > 0 else None,
            "F2": F2.getValue() if m.SolCount > 0 else None,
            "Status": "TimeLimit",
            "MipGap": mipgap,
            "Nodes": nodes,
            "UsedTrucks": sum(v_used[h].X > 0.5 for h in H_list) if m.SolCount > 0 else None,
            "ExecutionTime(s)": exec_time
        })

    # --- OPTIMAL ---
    elif status == GRB.OPTIMAL:
        print(f"Instance {instance_id} résolue : objectif = {m.ObjVal:.2f} | Temps = {exec_time}s")
        results.append({
            "Instance": instance_id,
            "file name": filename,
            "containers": N,
            "Destinations": D,
            "Trucks": H,
            "Docks": K,
            "Objective": m.ObjVal,
            "F1": F1.getValue(),
            "F2": F2.getValue(),
            "Status": "Optimal",
            "MipGap": mipgap,
            "Nodes": nodes,
            "UsedTrucks": sum(v_used[h].X > 0.5 for h in H_list),
            "ExecutionTime(s)": exec_time
        })

    # --- INFEASIBLE ---
    elif status == GRB.INFEASIBLE:
        print(f"Instance {instance_id} INFÉASIBLE | Temps = {exec_time}s")

        m.computeIIS()
        m.write(f"IIS_{instance_id}.ilp")

        results.append({
            "Instance": instance_id,
            "file name": filename,
            "containers": N,
            "Destinations": D,
            "Trucks": H,
            "Docks": K,
            "Objective": None,
            "F1": None,
            "F2": None,
            "Status": "Infeasible",
            "MipGap": None,
            "Nodes": nodes,
            "UsedTrucks": None,
            "ExecutionTime(s)": exec_time
        })

    # --- UNBOUNDED ---
    elif status == GRB.UNBOUNDED:
        print(f" Instance {instance_id} UNBOUNDED")
        results.append({
            "Instance": instance_id,
            "file name": filename,
            "containers": N,
            "Destinations": D,
            "Trucks": H,
            "Docks": K,
            "Objective": None,
            "F1": None,
            "F2": None,
            "Status": "Unbounded",
            "MipGap": None,
            "Nodes": nodes,
            "UsedTrucks": None,
            "ExecutionTime(s)": exec_time
        })

    # --- AUTRE STATUT ---
    else:
        print(f"Instance {instance_id} arrêtée avec statut : {status}")
        results.append({
            "Instance": instance_id,
            "file name": filename,
            "containers": N,
            "Destinations": D,
            "Trucks": H,
            "Docks": K,
            "Objective": None,
            "F1": None,
            "F2": None,
            "Status": status,
            "MipGap": None,
            "Nodes": nodes,
            "UsedTrucks": None,
            "ExecutionTime(s)": exec_time
        })


# === Sauvegarde des résultats ===
df_results = pd.DataFrame(results)
df_results.to_csv("results_exact_summary_with_chargui_instances_time_limit_2_h.csv", index=False)
