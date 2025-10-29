import pandas as pd

# Chemin du fichier CSV à convertir
csv_file = "results_exact_summary_before_adingdock_constraint.csv"

# Nom du fichier Excel de sortie
excel_file = "results_exact_summary_before_ading_dock_constraint.xlsx"

# Lecture du fichier CSV
df = pd.read_csv(csv_file) 

# Conversion en fichier Excel
df.to_excel(excel_file, index=False)

print(f"Conversion terminée ! Le fichier '{excel_file}' a été créé avec succès.")
