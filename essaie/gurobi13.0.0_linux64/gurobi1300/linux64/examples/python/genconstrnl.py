import gurobipy as gp
from gurobipy import nlfunc


# Formulate and solve the simple nonlinear model

# Minimize y1 + y2
# s.t.     y1 = x2 ^2
#          y2 = sin(2.5 * x1) + x2
#          y1, y2 free
#          -1 <= x1, x2 <= 1

with gp.Env() as env, gp.Model(env=env) as model:
    # Optimization variables
    x1 = model.addVar(lb=-1, ub=1, name="x1")
    x2 = model.addVar(lb=-1, ub=1, name="x2")

    # Auxiliary resultant variables for nonlinear constraints
    y1 = model.addVar(lb=-float("inf"), obj=1.0, name="y1")
    y2 = model.addVar(lb=-float("inf"), obj=1.0, name="y2")

    # First nonlinear constraint y1 = x2 ^2
    model.addGenConstrNL(y1, x2**2, name="univariate_constraint")

    # Second nonlinear constraint y2 = sin(2.5 * x1) + x2
    model.addGenConstrNL(y2, nlfunc.sin(2.5 * x1) + x2, name="multivariate_constraint")

    model.optimize()

    print(f"x1={x1.X}  x2={x2.X} y1={y1.X} y2={y2.X} obj={model.ObjVal}")
