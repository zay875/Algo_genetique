
import pandas as pd
import matplotlib.pyplot as plt

# Charger les fichiers
ga = pd.read_csv("results_summary.csv")
exact = pd.read_csv("results_exact_summary.csv")
random = pd.read_csv("results_summary_ramdom_pop.csv")

# Normaliser la colonne Instance en int (si présente)
for df in (ga, exact, random):
    if "Instance" in df.columns:
        try:
            df["Instance"] = df["Instance"].astype(int)
        except Exception:
            # leave as-is if conversion fails
            pass

# Renommer les colonnes pour garder des noms explicites après merge
if "BestFitness" in ga.columns and "BestFitness_GA" not in ga.columns:
    ga = ga.rename(columns={"BestFitness": "BestFitness_GA"})
if "ExecutionTime(s)" in ga.columns and "ExecutionTime(s)_GA" not in ga.columns:
    ga = ga.rename(columns={"ExecutionTime(s)": "ExecutionTime(s)_GA"})

# Filtrer les résultats optimaux et renommer colonnes pour exact
if "Status" in exact.columns:
    exact_opt = exact[exact["Status"] == "Optimal"].copy()
else:
    exact_opt = exact.copy()
if "ExecutionTime(s)" in exact_opt.columns and "ExecutionTime(s)_Exact" not in exact_opt.columns:
    exact_opt = exact_opt.rename(columns={"ExecutionTime(s)": "ExecutionTime(s)_Exact"})

# Normaliser random
if "BestFitness" in random.columns and "BestFitness_random" not in random.columns:
    random = random.rename(columns={"BestFitness": "BestFitness_random"})
if "ExecutionTime(s)" in random.columns and "ExecutionTime(s)_random" not in random.columns:
    random = random.rename(columns={"ExecutionTime(s)": "ExecutionTime(s)_random"})

# Fusionner (GA + Exact) puis Random
merged = pd.merge(ga, exact_opt, on="Instance", how="inner")
merged = pd.merge(merged, random, on="Instance", how="left")

# Calculer le pourcentage d'écart en utilisant BestFitness_GA vs Objective
import numpy as np

def compute_gap(row):
    bf = row.get("BestFitness_GA") or row.get("BestFitness")
    obj = row.get("Objective")
    if pd.isna(bf) or pd.isna(obj) or obj == 0:
        return "nan"
    try:
        bf_val = float(bf)
        obj_val = float(obj)
    except Exception:
        return "nan" 
    return 100.0 * (bf_val - obj_val) / obj_val if bf_val > obj_val else 0

merged["Gap(%)"] = merged.apply(compute_gap, axis=1)

print("\n=== Comparaison GA vs Exact ===")
# Safe column names for display
cols_to_show = [
    "Instance",
    "BestFitness_GA" if "BestFitness_GA" in merged.columns else ("BestFitness" if "BestFitness" in merged.columns else None),
    "BestFitness_random" if "BestFitness_random" in merged.columns else None,
    "Objective" if "Objective" in merged.columns else None,
    "Gap(%)",
    "ExecutionTime(s)_GA" if "ExecutionTime(s)_GA" in merged.columns else None,
    "ExecutionTime(s)_Exact" if "ExecutionTime(s)_Exact" in merged.columns else None,
]
cols_to_show = [c for c in cols_to_show if c]
print(merged[cols_to_show])

print("\n📊 Moyenne de l'écart (%) :", merged["Gap(%)"].mean())

# === Sauvegarder le récapitulatif ===
output_file = "comparison_summary_after_ading_dock_condtraint.csv"
save_cols = ["Instance"]
if "BestFitness_GA" in merged.columns:
    save_cols.append("BestFitness_GA")
elif "BestFitness" in merged.columns:
    save_cols.append("BestFitness")
if "BestFitness_random" in merged.columns:
    save_cols.append("BestFitness_random")
if "Objective" in merged.columns:
    save_cols.append("Objective")
save_cols += ["Gap(%)"]
if "ExecutionTime(s)_GA" in merged.columns:
    save_cols.append("ExecutionTime(s)_GA")
if "ExecutionTime(s)_random" in merged.columns:
    save_cols.append("ExecutionTime(s)_random")
if "ExecutionTime(s)_Exact" in merged.columns:
    save_cols.append("ExecutionTime(s)_Exact")

merged[save_cols].to_csv(output_file, index=False)
print(f"\n💾 Résumé sauvegardé dans {output_file}")

# Graphique de comparaison
plt.figure(figsize=(10,6))
if "Objective" in merged.columns:
    plt.plot(merged["Instance"], merged["Objective"], label="Exact (Optimal)", marker="o")
if "BestFitness_GA" in merged.columns:
    plt.plot(merged["Instance"], merged["BestFitness_GA"], label="GA (Best Fitness)", marker="s")
elif "BestFitness" in merged.columns:
    plt.plot(merged["Instance"], merged["BestFitness"], label="GA (Best Fitness)", marker="s")
if "BestFitness_random" in merged.columns:
    plt.plot(merged["Instance"], merged["BestFitness_random"], label="GA (Best Fitness_random)", marker="^")
plt.xlabel("Instance")
plt.ylabel("Objective Value")
plt.title("Comparaison : GA vs Modèle Exact (Gurobi)")
plt.legend()
plt.grid(True)
plt.show()

# Graphique du pourcentage d'écart
plt.figure(figsize=(10,5))
plt.bar(merged["Instance"], merged["Gap(%)"], color='orange')
plt.xlabel("Instance")
plt.ylabel("Ecart (%)")
plt.title("Ecart entre GA et solution exacte (%)")
plt.grid(True)
plt.show()
