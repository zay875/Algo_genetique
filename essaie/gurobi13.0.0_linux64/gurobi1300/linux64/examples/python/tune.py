#!/usr/bin/env python3

# Copyright 2025, Gurobi Optimization, LLC

#  This example reads a model from a file and tunes it.
#  It then writes the best parameter settings to a file
#  and solves the model using these parameters.

import sys
import gurobipy as gp

if len(sys.argv) < 2:
    print("Usage: tune.py filename")
    sys.exit(0)

# Read the model
model = gp.read(sys.argv[1])

# Set a time limit for the model
model.Params.TimeLimit = 5

# Set a time limit for the whole tuning run
# Note that both time limits are chosen to have a quick demonstration.
# In general, a total tune time limit should be set such that the
# tuning tool can test several hundreds of parameter setting
model.Params.TuneTimeLimit = 60

# Set the TuneResults parameter to 2
#
# The first parameter setting is the result for the first solved
# setting. The second entry the parameter setting of the best parameter
# setting.
model.Params.TuneResults = 2

# Tune the model
model.tune()

if model.TuneResultCount >= 2:
    # Load the best tuned parameters into the model
    #
    # Note, the first parameter setting is associated to the first solved
    # setting and the second parameter setting to best tune result.
    model.getTuneResult(1)

    # Write tuned parameters to a file
    model.write("tune.prm")

    # Solve the model using the tuned parameters
    model.optimize()
