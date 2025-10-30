import pandas as pd
from binpacking import calculate_loading_times_df

# --- Données de test simplifiées ---
# (tu peux copier celles d'une instance que tu veux vérifier)
trucks_df = pd.DataFrame({
    "TruckID": [1, 2, 3],
    "AssignedDockPosition": [1, 2, 3],
    "LoadingDuration": [1, 1, 2]  # ex. durée en heures ou unités
})

docks_df = pd.DataFrame({
    "DockID": [1, 2, 3],
    "Position": [1, 2, 3]
})

# Simule un chromosome (même format que celui du GA)
best_chrom = [[1], 0, 1, 0, [2], 0, 2, 0, [3], 0, 3, 0]

# --- Test du calcul ---
try:
    times_df = calculate_loading_times_df(best_chrom, trucks_df=trucks_df, docks_df=docks_df)
    print("✅ Calcul réussi :")
    print(times_df)
except KeyError as e:
    print(f"⚠️ Erreur de clé : {e}")
    print("→ Vérifie que le dock existe dans docks_df.")
