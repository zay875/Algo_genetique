import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv("results_exact_summary_with_chargui_instances.csv")

df["Hard"] = (
    (df["Status"] == "TimeLimit") | 
    ((df["MipGap"] > 0.05) & (df["MipGap"].notna()))
)
print(df.groupby("containers")["Hard"].mean())
print(df.groupby("Trucks")["Hard"].mean())
print(df.groupby(["Trucks", "containers"])["Hard"].mean())


plt.scatter(df["Trucks"], df["containers"], c=df["Hard"])
plt.xlabel("Trucks")
plt.ylabel("Containers")
plt.title("Difficulté du modèle en fonction de la taille de l’instance")
plt.colorbar(label="Hard (1=Bloqué)")
plt.show()
