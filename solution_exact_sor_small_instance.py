from gurobipy import Model, GRB, quicksum
import gurobipy as gp
from gurobipy import GRB
import sys
import random
from gurobipy import max_ 
import pandas as pd
import sys
import time
# === Données ===
data_container = {
    'ContainerID': [1, 2, 3],
    'Length': [2, 4, 2],
    'Position': [57, 63, 58],
    'Destination' : [2,2,2],
    'Instance': [1, 1, 1]
}

data_truck = {
    'TruckID': [1, 2],
    'Destination': [1,2],
    'Cost': [624 ,479],
    'Capacity':[6,6],
    'DockPosition':[1,2],
    'Instance': [1, 1]
}
data_docks={
'DockID':[1,2],
'Position':[1,2],'Instance': [1, 1]
}
instance_id = 1
containers_df = pd.DataFrame(data_container)
trucks_df = pd.DataFrame(data_truck)
docks_df = pd.DataFrame(data_docks)

# Extraire les paramètres
H = trucks_df["TruckID"].tolist()
N = containers_df["ContainerID"].tolist()
K = docks_df["DockID"].tolist()
D = sorted(trucks_df["Destination"].unique())

    # Données de base
C_d = {int(row["Destination"]): int(row["Cost"]) for _, row in trucks_df.iterrows()}
C_E = 0.5
W1, W2 = 0.5, 0.5
M = 1000
Y = 10
V = 5
I = 5
Q = int(trucks_df["Capacity"].iloc[0]) if not trucks_df.empty else 6

P = containers_df["Position"].tolist()
L = containers_df["Length"].tolist()
R = docks_df["Position"].tolist()



results = []
random.seed(42)  # optional
#setting the containers destination 
# G doit être une matrice binaire : (d, i) -> {0,1}

    # Destination de chaque conteneur
Dest = dict(zip(containers_df["ContainerID"], containers_df["Destination"]))

    # Matrice G : conteneur i -> destination d
G = {}
for i in N:
    for d in D:
        G[d, i] = 1 if Dest[i] == d else 0


# === Modèle ===
m = Model("Transport_Energie")

# Variables

a = m.addVars(H, D, vtype=GRB.BINARY, name="a")# d is destination of the truck h
x = m.addVars(H, K, vtype=GRB.BINARY, name="x") #truck h is assigned to dock k
p = m.addVars(N, H, vtype=GRB.BINARY, name="p")# container n is assigned to truck h
z = m.addVars(N, H, vtype=GRB.CONTINUOUS, name="z") #area
d_abs = m.addVars(N, K, vtype=GRB.CONTINUOUS, name="d_abs")
v_used = m.addVars(H, vtype=GRB.BINARY, name="v")
n = m.addVars(H, H, vtype=GRB.BINARY, name="n") #same dock for two trucks
b = m.addVars(H, vtype=GRB.CONTINUOUS, name="b")
q = m.addVars(H, vtype=GRB.CONTINUOUS, name="q")

    # === Objectif ===
F1 = quicksum(C_d[d] * a[h, d] for h in H for d in D)
F2 = C_E * quicksum(z[i, h] for i in N for h in H)
m.setObjective(W1 * F1 + W2 * F2, GRB.MINIMIZE)



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
print(f"results of F1: {F1}")
print(f"results of F2: {F2}")
df_results = pd.DataFrame(results)
df_results.to_csv("results_exact_summary__small_instance.csv", index=False)

# do IIS
'''print("The model is infeasible; computing IIS")
m.computeIIS()
if m.IISMinimal:
    print("IIS is minimal\n")
else:
    print("IIS is not minimal\n")
print("\nThe following constraint(s) cannot be satisfied:")
for c in m.getConstrs():
    if c.IISConstr:
        print(c.ConstrName)

'''
