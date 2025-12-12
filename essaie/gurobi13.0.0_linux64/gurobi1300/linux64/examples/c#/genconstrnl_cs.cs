/* Copyright 2025, Gurobi Optimization, LLC */

/* This example formulates and solves the following simple nonlinear model:

     minimize    y1 + y2
     subject to  y1 = x2 ^2
                 y2 = sin(2.5 * x1) + x2
                 y1, y2 free
                 -1 <= x1, x2 <= 1
*/

using System;
using Gurobi;

class mip1_cs
{
  static void Main()
  {

    try {

      // Create environment
      GRBEnv env = new GRBEnv("genconstrnl.log");

      // Create empty model
      GRBModel model = new GRBModel(env);

      // Create variables, only y variables have an objective coefficient
      GRBVar y1 = model.AddVar(-GRB.INFINITY, GRB.INFINITY, 1.0, GRB.CONTINUOUS,
		                           "y1");
      GRBVar y2 = model.AddVar(-GRB.INFINITY, GRB.INFINITY, 1.0, GRB.CONTINUOUS,
		                           "y2");
      GRBVar x1 = model.AddVar(-1.0, 1.0, 0.0, GRB.CONTINUOUS, "x1");
      GRBVar x2 = model.AddVar(-1.0, 1.0, 0.0, GRB.CONTINUOUS, "x2");

      // Array representation of first expression tree for x2 ^2
      int[] opcode1 = {GRB.OPCODE_POW, GRB.OPCODE_VARIABLE, GRB.OPCODE_CONSTANT};
      double[] data1 = {-1.0, x2.Index, 2.0};
      int[] parent1 = {-1, 0, 0};
      // Add first nonlinear constraint y1 = x2 ^2
      model.AddGenConstrNL(y1, opcode1, data1, parent1, "univariate_constraint");

      // Array representation of second expression tree for sin(2.5 * x1) + x2
      int[] opcode2 = {GRB.OPCODE_PLUS, GRB.OPCODE_SIN, GRB.OPCODE_MULTIPLY,
                       GRB.OPCODE_CONSTANT, GRB.OPCODE_VARIABLE,
                       GRB.OPCODE_VARIABLE};
      double[] data2 = {-1.0, -1.0, -1.0, 2.5, x1.Index, x2.Index};
      int[] parent2 = {-1, 0, 1, 2, 2, 0};
      // Add second nonlinear constraint y2 = sin(2.5 * x1) + x2
      model.AddGenConstrNL(y2, opcode2, data2, parent2, "multivariate_constraint");

      // Optimize model
      model.Optimize();

      Console.WriteLine(y1.VarName + " " + y1.X);
      Console.WriteLine(y2.VarName + " " + y2.X);
      Console.WriteLine(x1.VarName + " " + x1.X);
      Console.WriteLine(x2.VarName + " " + x2.X);

      Console.WriteLine("Obj: " + model.ObjVal);

      // Dispose of model and env
      model.Dispose();
      env.Dispose();

    } catch (GRBException e) {
      Console.WriteLine("Error code: " + e.ErrorCode + ". " + e.Message);
    }
  }
}
