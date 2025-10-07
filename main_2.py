from population import generate_initial_population
from fitness import FitnessEvaluator
from ga_runner import run_ga
import pandas as pd
import itertools
import matplotlib.pyplot as plt


data = {
    'Container': [1, 2, 3, 4, 5, 6],
    'Length': [2, 4, 2, 5, 10, 4],
    'Position': [57, 63, 58, 49, 26, 71],
    'Destination' : [2,2,2,1,1,2]
}

data_2 = {
    'Truck': [1, 2,3,4,5],
    'Destination': [1, 1,2,2,2],
    'Cost': [624,624, 479,479,479]
}
Truck_cost_df = pd.DataFrame(data_2)
#containers_df = pd.DataFrame(data)

# Charger les données
containers_df = pd.read_csv("C:/Users/Taieb/Algo_genetique/containers_all (1).csv")
trucks_df = pd.read_csv("C:/Users/Taieb/Algo_genetique/trucks_all (1).csv")
docks_df = pd.read_csv("C:/Users/Taieb/Algo_genetique/docks_all (1).csv")
#truck_cost_df = pd.read_csv("truck_cost.csv")

results = []

for pop_size, mutation_rate, crossover_rate, num_elites in itertools.product(
    [20, 50, 100],
    [0.01, 0.05, 0.1, 0.2],
    [0.6, 0.8, 0.9],
    [1, 2, 5]
):
    # Génération de la population initiale
    initial_population = generate_initial_population(
        pop_size, containers_df, trucks_df, docks_df, instance_id=12
    )

    # Exécution du GA
    best_solution, best_fitness,history = run_ga(
        initial_population,
        FitnessEvaluator(containers_df, Truck_cost_df, C_E=1),
        num_docks=len(docks_df),
        num_generations=100,
        num_elites=num_elites,
        crossover_rate=crossover_rate,
        mutation_rate=mutation_rate
    )

    # Enregistrement du résultat
    results.append({
        "pop_size": pop_size,
        "mutation_rate": mutation_rate,
        "crossover_rate": crossover_rate,
        "num_elites": num_elites,
        "best_fitness": best_fitness
    })

# Transformer en DataFrame pour analyser facilement
df_results = pd.DataFrame(results)
df_results.sort_values(by="best_fitness", ascending=True)
print(df_results.head())
import seaborn as sns
sns.scatterplot(data=df_results, x="mutation_rate", y="best_fitness", hue="pop_size")

plt.title("Impact de mutation_rate et pop_size sur la fitness")
plt.xlabel("mutation_rate")
plt.ylabel("best_fitness")

# Afficher la figure
plt.show()
