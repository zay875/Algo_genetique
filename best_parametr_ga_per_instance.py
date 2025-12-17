import pandas as pd


df=pd.read_csv("GA_grid_search_results.csv")
# =========================
# 2. Select best row per instance
#    (lowest AvgFitness)
# =========================
best_per_instance = (
    df.loc[df.groupby("Instance")["AvgFitness"].idxmin()]
      .sort_values("Instance")
      .reset_index(drop=True)
)

columns_to_keep = [
    "Instance",
    "PopulationSize",
    "CrossoverRate",
    "MutationRate",
    "AvgFitness",
    "AvgTruckCost",
    "AvgEnergyCost",
    "AvgTime"
]

best_per_instance = best_per_instance[columns_to_keep]

output_file = "best_parameters_GA_per_instance.csv"
best_per_instance.to_csv(output_file, index=False)

print("Best parameters for GA per instance saved to:", output_file)
print(best_per_instance)