
import pandas as pd
from utils import verify_solution_feasibility
class FitnessEvaluator:
    def __init__(self, containers_df, Truck_cost_df, C_E, W1=0.5, W2=0.5):
        self.containers_df = containers_df
        self.Truck_cost_df = Truck_cost_df
        self.C_E = C_E
        self.W1 = W1
        self.W2 = W2

        #adding weights for penalty
        self.P_DUP=500   #duplicate penalty
        self.P_DEST =300  #wrong destination penalty
        self.P_CAP =200   #exceeded cpacity penalty
        self.P_UNASSIGNED=5000 #unassigned container penalty

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
    
    #panalty function
    def calculate_penalties(self, chromosome, trucks_df, containers_df, instance_id):
        
        feasable, error = verify_solution_feasibility(chromosome, trucks_df, containers_df, instance_id)
        total_penalty = 0
        for e in error:
            if "plusieurs fois" in e:
                total_penalty += self.P_DUP
            elif "dépasse la capacité"in e :
                total_penalty += self.P_CAP
            elif "assigné à camion" in e :
                total_penalty += self.P_DEST
            elif "non assignés" in e: 
                # Extract the list of unassigned containers from the string
             import re
             match = re.findall(r"\[(.*?)\]", e)
             if match:
              unassigned_list = match[0].replace(" ", "").split(",")
              nb_unassigned = len(unassigned_list)
              total_penalty += self.P_UNASSIGNED * nb_unassigned
             else:
                total_penalty += self.P_UNASSIGNED     
            if "n'existe pas" in e or "sans camion correspondant" in e:
                total_penalty += self.P_UNASSIGNED
        return total_penalty, error 

    def calculate_fitness(self, chromosome,trucks_df, containers_df, instance_id):

        cost_f1= self.calculate_truck_cost_f1(chromosome)
        cost_F2=  self.calculate_energy_cost_f2(chromosome)
        # ✅ call the penalty function
        penalty, errors = self.calculate_penalties(chromosome, trucks_df, containers_df, instance_id)
        total_fitness = self.W1 * cost_f1 + self.W2 * cost_F2 + penalty

        return  total_fitness
               
