/* Copyright 2025, Gurobi Optimization, LLC */

/* This example formulates and solves the following simple nonlinear model:

     minimize    y1 + y2
     subject to  y1 = x2 ^2
                 y2 = sin(2.5 * x1) + x2
                 y1, y2 free
                 -1 <= x1, x2 <= 1
*/

import com.gurobi.gurobi.*;

public class GenconstrNL {

  public static void main(String[] args) {
    try {
      // Create environment
      GRBEnv env = new GRBEnv("genconstrnl.log");

      // Create empty model
      GRBModel model = new GRBModel(env);

      // Create variables, only y variables have an objective coefficient
      GRBVar y1 = model.addVar(-GRB.INFINITY, GRB.INFINITY, 1.0, GRB.CONTINUOUS,
                              "y1");
      GRBVar y2 = model.addVar(-GRB.INFINITY, GRB.INFINITY, 1.0, GRB.CONTINUOUS,
                              "y2");
      GRBVar x1 = model.addVar(-1.0, 1.0, 0.0, GRB.CONTINUOUS, "x1");
      GRBVar x2 = model.addVar(-1.0, 1.0, 0.0, GRB.CONTINUOUS, "x2");

      // Array representation of first expression tree for x2 ^2
      int opcode1[] = new int[] {GRB.OPCODE_POW, GRB.OPCODE_VARIABLE, GRB.OPCODE_CONSTANT};
      double data1[] = new double[] {-1.0, x2.index(), 2.0};
      int parent1[] = new int[] {-1, 0, 0};
      // Add first nonlinear constraint y1 = x2 ^2
      model.addGenConstrNL(y1, opcode1, data1, parent1, "univariate_constraint");

      // Array representation of second expression tree for sin(2.5 * x1) + x2
      int opcode2[] = new int[] {GRB.OPCODE_PLUS, GRB.OPCODE_SIN, GRB.OPCODE_MULTIPLY,
                                 GRB.OPCODE_CONSTANT, GRB.OPCODE_VARIABLE,
                                 GRB.OPCODE_VARIABLE};
      double data2[] = new double[] {-1.0, -1.0, -1.0, 2.5, x1.index(), x2.index()};
      int parent2[] = new int[] {-1, 0, 1, 2, 2, 0};
      // Add second nonlinear constraint y2 = sin(2.5*x1) + x2
      model.addGenConstrNL(y2, opcode2, data2, parent2, "multivariate_constraint");

      // Optimize model
      model.optimize();

      System.out.println(y1.get(GRB.StringAttr.VarName)
                         + " " +y1.get(GRB.DoubleAttr.X));
      System.out.println(y2.get(GRB.StringAttr.VarName)
                         + " " +y2.get(GRB.DoubleAttr.X));
      System.out.println(x1.get(GRB.StringAttr.VarName)
                         + " " +x1.get(GRB.DoubleAttr.X));
      System.out.println(x2.get(GRB.StringAttr.VarName)
                         + " " +x2.get(GRB.DoubleAttr.X));

      System.out.println("Obj: " + model.get(GRB.DoubleAttr.ObjVal));

      // Dispose of model and environment
      model.dispose();
      env.dispose();

    } catch (GRBException e) {
      System.out.println("Error code: " + e.getErrorCode() + ". " +
                         e.getMessage());
    }
  }
}
