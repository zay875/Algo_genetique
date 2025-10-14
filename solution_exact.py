from gurobipy import Model, GRB, quicksum

# === Données ===
H, D, N, K = range(1,4), range(1,5), range(1,6), range(1,3)

C_d = {1:10, 2:12, 3:15, 4:9}     # coût par destination
C_E = 0.8
W1, W2 = 0.5, 0.5
M = 1000                  # grande constante (Big M)

# Paramètres physiques
P = [3, 6, 8, 10, 13]     # position de chaque container (en m)
R = [4, 9]                # position possible pour chaque camion
L = [2, 3, 3, 4, 2]       # longueur de chaque container
Y = 10                    # longueur verticale du quai (constante)
Q= 6 
# === Modèle ===
m = Model("Transport_Energie")

# Variables
a = m.addVars(H, D, vtype=GRB.BINARY, name="a")   # camion -> destination
x = m.addVars(H, K, vtype=GRB.BINARY, name="x")   # camion -> position
p = m.addVars(N, H, vtype=GRB.BINARY, name="p")   # container -> camion
z = m.addVars(N, H, lb=0.0, name="z")             # coût énergétique
d = m.addVars(N, K, lb=0.0, name="d")             # |P_i - R_k|

# === Fonctions objectifs ===
F1 = quicksum(C_d[d_] * a[h, d_] for h in H for d_ in D)
F2 = C_E * quicksum(z[i, h] for i in N for h in H)

m.setObjective(W1 * F1 + W2 * F2, GRB.MINIMIZE)


# === Contraintes ===

# (1) Chaque container i assigné à un seul camion h
for i in N:
    m.addConstr(quicksum(p[i, h] for h in H) == 1, name=f"assign_container[{i}]")
#capacity constarint
for h in H:
    m.addConstr(quicksum(L[i] * p[i, h] for i in N) <= Q,
                name=f"capacity[{h}]")

#(2) Linéarisation du terme absolu : d[i,k] = |P_i - R_k|
for i in N:
    for k in K:
        m.addConstr(d[i, k] >= P[i] - R[k], name=f"abs_pos1[{i},{k}]")
        m.addConstr(d[i, k] >= R[k] - P[i], name=f"abs_pos2[{i},{k}]")

# (3) Définition de z[i,h]
# z[i,h] >= 2*|P_i - R_k| + Y*L_i - M*(2 - (p[i,h] + x[h,k]))
for i in N:
    for h in H:
        for k in K:
            m.addConstr(
                z[i, h] >= 2 * d[i, k] + Y * L[i] - M * (2 - (p[i, h] + x[h, k])),
                name=f"z_def[{i},{h},{k}]"
            )

# === Optimisation ===
m.optimize()
for v in m.getVars():
        print(f"{v.VarName} {v.X:g}")

print(f"Obj: {m.ObjVal:g}")

