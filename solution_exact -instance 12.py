from gurobipy import Model, GRB, quicksum
import gurobipy as gp
from gurobipy import GRB
import sys
import random
# === Données ===
H, D, N = range(1,7), range(1,5), range(1,6)
#D destinations, H trucks, N containers, K docks

C_d = {1:348, 2:591, 3:233, 4:351}     # coût par destination
C_E = 0.5
W1, W2 = 0.5, 0.5
M = 1000                  # grande constante (Big M)

# Paramètres physiques
P = [75, 54, 29, 50, 60]     # position de chaque container (en m)
R = [5, 2, 3, 4]       # positions réelles
K = list(range(len(R))) # indices des quais               # position possible pour chaque camion
L = [4, 4, 3, 1, 4]       # longueur de chaque container
Y = 10                    # longueur verticale du quai (constante)
Q= 6 


random.seed(42)  # optional
#setting the containers destination 
# G doit être une matrice binaire : (d, i) -> {0,1}
G = {}
Dest = {1:3, 2:2, 3:4, 4:2, 5:3}  # conteneur -> destination

for i in N:
    for d in D:
        G[d, i] = 1 if Dest[i] == d else 0


# === Modèle ===
m = Model("Transport_Energie")

# Variables
a = m.addVars(H, D, vtype=GRB.BINARY, name="a")   # camion -> destination
x = m.addVars(H, K, vtype=GRB.BINARY, name="x")   # camion -> position
p = m.addVars(N, H, vtype=GRB.BINARY, name="p")   # container -> camion
z = m.addVars(N, H,vtype=GRB.CONTINUOUS, name="z")             # coût énergétique
d = m.addVars(N, K, vtype=GRB.CONTINUOUS,name="d")             # |P_i - R_k|
v = m.addVars(H,vtype=GRB.BINARY, name="v")       # vh if truck h is used
n = m.addVars(H, H, vtype=GRB.BINARY, name="n")       # nh, ng if truck h and g are assigned to same dock and h is predecessuer of g
# === Fonctions objectifs ===
F1 = quicksum(C_d[d_] * a[h, d_] for h in H for d_ in D)
F2 = C_E * quicksum(z[i, h] for i in N for h in H)


#adding a penalty to avoid using the same dock for all trucks, instead of adding a constraint because in the report de reference it does'nt say so, its better to penalize that
m.setObjective(W1*F1 + W2*F2 + 1e-4*quicksum(k * x[h,k] for h in H for k in K), GRB.MINIMIZE)



# === Contraintes ===

# (1) Chaque container i est assigné à un seul camion h #2
for i in N:
    m.addConstr(quicksum(p[i, h] for h in H) == 1, name=f"assign_container[{i}]")
#capacity constarint #3
for h in H:
    m.addConstr(quicksum(L[i-1] * p[i, h] for i in N) <= Q,
                name=f"capacity[{h}]")

#(2) Linéarisation du terme absolu : d[i,k] = |P_i - R_k| #8
for i in N:
    for k in K:
        m.addConstr(d[i, k] >= P[i-1] - R[k], name=f"abs_pos1[{i},{R[k]}]")
        m.addConstr(d[i, k] >= R[k] - P[i-1], name=f"abs_pos2[{i},{R[k]}]")
# (3) Définition de z[i,h]
# z[i,h] >= 2*|P_i - R_k| + Y*L_i - M*(2 - (p[i,h] + x[h,k]))
for i in N:
    for h in H:
        for k in K:
            m.addConstr(
                z[i, h] >= 2 * d[i, k] + Y * L[i-1] - M * (2 - (p[i, h] + x[h, k])),
                name=f"z_def[{i},{h},{k}]"
            )

#trucks can only load containers with same destination #4
m.addConstrs((
    p[i,h] + p[j,h] <= quicksum(G[d,i]*G[d,j] for d in D) + 1
    for i in N for j in N if i != j for h in H
), name="same_dest")

#a truck is used if at least one container is assigne dto it #5
m.addConstrs((p[i,h] <= v[h] for h in H for i in N), name="truck_used_id_container_is_assigned_to_it")
#truck_destination=container_destination assigned to it #6

m.addConstrs((a[h,d] <= G[d,i] + 1 - p[i,h] for i in N for h in H for d in D), name="dest_constraint")
#if truck h is used, it has one destination #7
m.addConstrs((v[h] == quicksum(a[h,d] for d in D) for h in H), name="truck_use")

#aech truck is asigned to one dock #9
m.addConstrs((quicksum(x[h,k] for k in K)==v[h] for h in H), name="truck_dock")
# constraint 10
m.addConstrs((x[h,k] + x[g,k]-1 <= n[h,g] + n[g,h] for h in H for g in H if h != g for k in K ) , name="two_trucks_samedock_")
# constraint 11
m.addConstrs((n[h,g] + n[g,h] <=1 for h in H for g in H ) , name="only_one_predecesseur")


# === Optimisation ===
m.optimize()
for v in m.getVars():
        print(f"{v.VarName} {v.X:g}")
print("Contenu complet de G :")
print(G)
print("\n--- Résumé affectation ---")
for h in H:
    assigned = [i for i in N if p[i,h].X > 0.5]
    docks = [R[k] for k in K if x[h,k].X > 0.5]   # <<- ici
    dests = [d for d in D if a[h,d].X > 0.5]
    print(f"Camion {h}: dest {dests} | containers {assigned} | quai {docks}")

print(f"Obj: {m.ObjVal:g}")
status = m.Status
if status == GRB.UNBOUNDED:
    print("The model cannot be solved because it is unbounded")
    sys.exit(0)
if status == GRB.OPTIMAL:
    print(f"The optimal objective is {m.ObjVal:g}")
    sys.exit(0)
if status != GRB.INF_OR_UNBD and status != GRB.INFEASIBLE:
    print(f"Optimization was stopped with status {status}")
    sys.exit(0)

# do IIS
print("The model is infeasible; computing IIS")
m.computeIIS()
if m.IISMinimal:
    print("IIS is minimal\n")
else:
    print("IIS is not minimal\n")
print("\nThe following constraint(s) cannot be satisfied:")
for c in m.getConstrs():
    if c.IISConstr:
        print(c.ConstrName)


