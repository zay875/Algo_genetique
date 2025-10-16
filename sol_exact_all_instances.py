
# run_exact_all_instances.py
from gurobipy import Model, GRB, quicksum
import pandas as pd
import sys
import time

# === Charger les fichiers CSV générés ===
containers_df = pd.read_csv("containers_all.csv")
trucks_df = pd.read_csv("trucks_all.csv")
docks_df = pd.read_csv("docks_all.csv")

instances = sorted(containers_df["Instance"].unique())
results = []

for instance_id in instances:
    print(f"\n🚛 === Résolution exacte pour l'instance {instance_id} ===")

    # Extraire les données de l’instance
    cont_i = containers_df[containers_df["Instance"] == instance_id].copy()
    trucks_i = trucks_df[trucks_df["Instance"] == instance_id].copy()
    docks_i = docks_df[docks_df["Instance"] == instance_id].copy()

    # Extraire les paramètres
    H = trucks_i["TruckID"].tolist()
    N = cont_i["ContainerID"].tolist()
    K = docks_i["DockID"].tolist()
    D = sorted(trucks_i["Destination"].unique())

    # Données de base
    C_d = {int(row["Destination"]): int(row["Cost"]) for _, row in trucks_i.iterrows()}
    C_E = 0.5
    W1, W2 = 0.5, 0.5
    M = 1000
    Y = 10
    V = 5
    I = 5
    Q = int(trucks_i["Capacity"].iloc[0]) if not trucks_i.empty else 6

    P = cont_i["Position"].tolist()
    L = cont_i["Length"].tolist()
    R = docks_i["Position"].tolist()

    # Destination de chaque conteneur
    Dest = dict(zip(cont_i["ContainerID"], cont_i["Destination"]))

    # Matrice G : conteneur i -> destination d
    G = {}
    for i in N:
        for d in D:
            G[d, i] = 1 if Dest[i] == d else 0

    # === Modèle ===
    m = Model(f"Instance_{instance_id}_Transport_Energie")

    # Variables
    a = m.addVars(H, D, vtype=GRB.BINARY, name="a")
    x = m.addVars(H, K, vtype=GRB.BINARY, name="x")
    p = m.addVars(N, H, vtype=GRB.BINARY, name="p")
    z = m.addVars(N, H, vtype=GRB.CONTINUOUS, name="z")
    d_abs = m.addVars(N, K, vtype=GRB.CONTINUOUS, name="d_abs")
    v_used = m.addVars(H, vtype=GRB.BINARY, name="v")
    n = m.addVars(H, H, vtype=GRB.BINARY, name="n")
    b = m.addVars(H, vtype=GRB.CONTINUOUS, name="b")
    q = m.addVars(H, vtype=GRB.CONTINUOUS, name="q")

    # === Objectif ===
    F1 = quicksum(C_d[d] * a[h, d] for h in H for d in D)
    F2 = C_E * quicksum(z[i, h] for i in N for h in H)
    m.setObjective(W1 * F1 + W2 * F2 + 1e-4 * quicksum(k * x[h, k] for h in H for k in K), GRB.MINIMIZE)

    # === Contraintes principales ===
    # (1) Chaque conteneur assigné à un camion
    for i in N:
        m.addConstr(quicksum(p[i, h] for h in H) == 1)

    # (2) Capacité
    for h in H:
        m.addConstr(quicksum(L[i-1] * p[i, h] for i in N) <= Q)

    # (3) Valeur absolue pour la distance
    for i in N:
        for k in K:
            m.addConstr(d_abs[i, k] >= P[i-1] - R[k-1])
            m.addConstr(d_abs[i, k] >= R[k-1] - P[i-1])

    # (4) Définition de z[i,h]
    for i in N:
        for h in H:
            for k in K:
                m.addConstr(z[i, h] >= 2 * d_abs[i, k] + Y * L[i-1] - M * (2 - (p[i, h] + x[h, k])))

    # (5) Contrainte de destination
    m.addConstrs((
        p[i, h] + p[j, h] <= quicksum(G[d, i] * G[d, j] for d in D) + 1
        for i in N for j in N if i != j for h in H
    ))

    # (6) Camion utilisé
    m.addConstrs((p[i, h] <= v_used[h] for h in H for i in N))

    # (7) Destination du camion
    m.addConstrs((a[h, d] <= G[d, i] + 1 - p[i, h] for i in N for h in H for d in D))
    m.addConstrs((v_used[h] == quicksum(a[h, d] for d in D) for h in H))

    # (8) Assignation au quai
    m.addConstrs((quicksum(x[h, k] for k in K) == v_used[h] for h in H))

    # (9) Contraintes d’ordre sur les quais
    m.addConstrs((x[h, k] + x[g, k] - 1 <= n[h, g] + n[g, h] for h in H for g in H if h != g for k in K))
    m.addConstrs((n[h, g] + n[g, h] <= 1 for h in H for g in H))

    # (10) Timing
    m.addConstrs((b[g] >= 0 for g in H))
    m.addConstrs((b[g] >= q[h] + V - M * (1 - n[g, h]) for h in H for g in H))
    m.addConstrs((q[h] == b[h] + I * quicksum(p[i, h] for i in N) for h in H))

    # === Résolution ===
   # === Résolution ===
# --- Gurobi parameters to encourage feasible solutions ---
    #m.Params.OutputFlag = 1       # show progress
    #m.Params.TimeLimit = 120      # stop after 2 minutes
    #m.Params.MIPFocus = 1         # focus on finding *any* feasible solution
    #m.Params.MIPGap = 0.05        # accept solution within 5% of optimum
    #m.Params.PoolSolutions = 10   # store multiple feasible solutions (optional)
    #m.Params.PoolSearchMode = 2   # explore more feasible solutions

    # --- Solve ---
    start_time = time.time()
    m.optimize()
    exec_time = round(time.time() - start_time, 3)


    # === Résultats ===
    if m.Status == GRB.OPTIMAL:
        for v in m.getVars():
            print('%s %g' % (v.VarName, v.X))
        print(f"✅ Instance {instance_id} résolue : objectif = {m.ObjVal:.2f} | Temps = {exec_time}s")
        results.append({
            "Instance": instance_id,
            "Objective": m.ObjVal,
            "Status": "Optimal",
            "UsedTrucks": sum(v_used[h].X > 0.5 for h in H),
            "ExecutionTime(s)": exec_time
        })
    else:
        print(f"⚠️ Instance {instance_id} non résolue (status {m.Status}) | Temps = {exec_time}s")
        results.append({
            "Instance": instance_id,
            "Objective": None,
            "Status": m.Status,
            "UsedTrucks": None,
            "ExecutionTime(s)": exec_time
        })
# === Sauvegarde des résultats ===
df_results = pd.DataFrame(results)
df_results.to_csv("results_exact_summary.csv", index=False)
