import pandas as pd

# Charger le fichier CSV
df = pd.read_csv("trucks_all.csv")

def renumeroter_extra(group):
    # max des IDs normaux dans cette instance
    max_normal_id = group.loc[group["added"] == False, "TruckID"].astype(int).max()

    # Extra dans l'ordre d'apparition
    extras = group[group["added"] == True].copy()

    # Générer les nouveaux IDs continus après max_normal_id
    new_ids = list(range(max_normal_id + 1, max_normal_id + 1 + len(extras)))

    # Remplacer
    group.loc[group["added"] == True, "TruckID"] = new_ids

    return group

# Appliquer par instance
df_mod = df.groupby("Instance").apply(renumeroter_extra,include_groups=True).reset_index(drop=True)

# Sauvegarde
df_mod.to_csv("trucks_modifies.csv", index=False)

print("IDs extra mis à jour avec succès !")
 