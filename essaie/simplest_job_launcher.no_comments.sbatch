#!/bin/bash

#SBATCH -J SimpleJobExample
#SBATCH --output=job-%j.log
#SBATCH --partition=h100
#SBATCH -t "999:30"

. /data/lgi2a_data/bin/lgi2a_initBatch
module load python3.12-gurobi


echo
echo "--------------------------------------------------------------------------------"
echo "--- Execution context"
echo "--------------------------------------------------------------------------------"
echo
lgi2a_displayInfo --cpu --gpu --cuda --python --job

echo
echo "--------------------------------------------------------------------------------"
echo "--- Start of the job tasks"
echo "--------------------------------------------------------------------------------"
echo
python "sol_exact_all_instances_instanncesv_3.py"


echo
echo "--------------------------------------------------------------------------------"
echo "--- Job post execution stats"
echo "--------------------------------------------------------------------------------"
echo
lgi2a_displayInfo --stats
