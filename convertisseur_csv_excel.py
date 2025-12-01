import pandas as pd

# Chemin du fichier CSV à convertir
csv_file = "results_exact_summary_with_chargui_instances.csv"

# Nom du fichier Excel de sortie
excel_file = "fichiers excel/results_exact_summary_with_chargui_instances.xlsx"

# Lecture du fichier CSV
df = pd.read_csv(csv_file) 

# Conversion en fichier Excel
df.to_excel(excel_file, index=False)

print(f"Conversion terminée ! Le fichier '{excel_file}' a été créé avec succès.")
