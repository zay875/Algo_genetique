#!/bin/bash

#SBATCH -J SimpleJobExample
#SBATCH --output=job-%j.log
#SBATCH --partition=h100
#SBATCH -t "3-8"

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
python "parameters selection_GA.py"


echo
echo "--------------------------------------------------------------------------------"
echo "--- Job post execution stats"
echo "--------------------------------------------------------------------------------"
echo
lgi2a_displayInfo --stats
