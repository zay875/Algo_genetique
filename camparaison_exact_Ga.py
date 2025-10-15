
import pandas as pd
import matplotlib.pyplot as plt

# Charger les fichiers
ga = pd.read_csv("results_summary.csv")
exact = pd.read_csv("results_exact_summary.csv")

# Nettoyer / normaliser les colonnes
ga["Instance"] = ga["Instance"].astype(int)
exact["Instance"] = exact["Instance"].astype(int)

# Garder uniquement les instances résolues par Gurobi (Status = Optimal)
exact_opt = exact[exact["Status"] == "Optimal"].copy()

# Fusion sur la colonne Instance
merged = pd.merge(ga, exact_opt, on="Instance", suffixes=("_GA", "_Exact"))

# Calculer le pourcentage d'écart
merged["Gap(%)"] = merged.apply(
    lambda row: 100 * (row["BestFitness"] - row["Objective"]) / row["Objective"]
    if row["BestFitness"] > row["Objective"] else 0,
    axis=1
)


print("\n=== 🔍 Comparaison GA vs Exact ===")
print(merged[["Instance", "BestFitness", "Objective", "Gap(%)", "ExecutionTime(s)_GA", "ExecutionTime(s)_Exact"]])


print("\n📊 Moyenne de l'écart (%) :", merged["Gap(%)"].mean())
# === Sauvegarder le récapitulatif ===
output_file = "comparison_summary.csv"
merged.to_csv(output_file, index=False)
print(f"\n💾 Résumé sauvegardé dans {output_file}")
# Graphique de comparaison
plt.figure(figsize=(10,6))
plt.plot(merged["Instance"], merged["Objective"], label="Exact (Optimal)", marker="o")
plt.plot(merged["Instance"], merged["BestFitness"], label="GA (Best Fitness)", marker="s")
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
