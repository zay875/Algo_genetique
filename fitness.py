
import pandas as pd

class FitnessEvaluator:
    def __init__(self, containers_df, Truck_cost_df, C_E, W1=0.5, W2=0.5):
        self.containers_df = containers_df
        self.Truck_cost_df = Truck_cost_df
        self.C_E = C_E
        self.W1 = W1
        self.W2 = W2

    def calculate_truck_cost_f1(self, chromosome):
        trucks_assigned = []
        for i in range(0, len(chromosome), 4):
            if chromosome[i]:
                trucks_assigned.append(i // 4 + 1)

        total_cost = 0
        for t in trucks_assigned:
            row = self.Truck_cost_df[self.Truck_cost_df['Truck'] == t]
            if not row.empty:
                total_cost += row['Cost'].iloc[0]
        return total_cost

    def calculate_energy_cost_f2(self, chromosome):
        total = 0
        for i in range(0, len(chromosome), 4):
            containers = chromosome[i]
            dock = chromosome[i+2]
            for c in containers:
                info = self.containers_df[self.containers_df['ContainerID'] == c].iloc[0]
                pos, length = info['Position'], info['Length']
                z = 2 * abs(pos - dock) + 1 * length
                total += self.C_E * z
        return total

    def calculate_fitness(self, chromosome):
        return self.W1 * self.calculate_truck_cost_f1(chromosome) + \
               self.W2 * self.calculate_energy_cost_f2(chromosome)
