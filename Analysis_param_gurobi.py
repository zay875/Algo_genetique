import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv("results_exact_summary_with_chargui_instances_time_limit_30.csv")

df["Hard"] = (
    (df["Status"] == "TimeLimit") | 
    ((df["MipGap"] > 0.05) & (df["MipGap"].notna()))
)
df["unfeasible"] = (df["Status"] == "Infeasible")
print(df)
print(df.groupby("containers")["Hard"].mean())
print(df.groupby("Trucks")["Hard"].mean())
print(df.groupby(["Trucks", "containers"])["Hard"].mean())



# --- Instances normales ---
normal_df = df[df["unfeasible"] == False]

# --- Instances infeasible ---
infeas_df = df[df["unfeasible"] == True]


from mpl_toolkits.mplot3d import Axes3D

fig = plt.figure(figsize=(9,7))
ax = fig.add_subplot(111, projection='3d')

# Instances normales
ax.scatter(
    normal_df["Trucks"],
    normal_df["containers"],
    normal_df["Destinations"],
    c=normal_df["Hard"],
    cmap="viridis",
    label="Résoluble"
)

# Instances infeasible
ax.scatter(
    infeas_df["Trucks"],
    infeas_df["containers"],
    infeas_df["Destinations"],
    color="red",
    marker="X",
    s=120,
    label="Infeasible"
)
import matplotlib.patches as mpatches
feasible_color = plt.cm.viridis(0.0)  # violet foncé = Hard = 0
hard_color = plt.cm.viridis(1.0)  # couleur correspondant à Hard = 1 
hard_patch = mpatches.Patch(color=hard_color, label="Hard instances (Hard = 1)")
infe_patch = mpatches.Patch(color="red", label="Infeasible")
feasible_patch = mpatches.Patch(color=feasible_color, label="Feasible")



ax.set_xlabel("Trucks")
ax.set_ylabel("Containers")
ax.set_zlabel("Destinations")
ax.set_title("Difficulté du modèle (plot 3D)")

plt.legend(handles=[hard_patch, infe_patch,feasible_patch])
plt.show()


