/* Copyright 2025, Gurobi Optimization, LLC */

/* This example formulates and solves the following simple nonlinear model:

     minimize    y1 + y2
     subject to  y1 = x2 ^2
                 y2 = sin(2.5 * x1) + x2
                 y1, y2 free
                 -1 <= x1, x2 <= 1
*/

#include "gurobi_c++.h"
using namespace std;

int
main(int   argc,
     char *argv[])
{

  try {

    // Create an environment
    GRBEnv env = GRBEnv("genconstrnl.log");

    // Create an empty model
    GRBModel model = GRBModel(env);

    // Create variables, only y variables have an objective coefficient
    GRBVar y1 = model.addVar(-GRB_INFINITY, GRB_INFINITY, 1.0, GRB_CONTINUOUS,
                             "y1");
    GRBVar y2 = model.addVar(-GRB_INFINITY, GRB_INFINITY, 1.0, GRB_CONTINUOUS,
                             "y2");
    GRBVar x1 = model.addVar(-1.0, 1.0, 0.0, GRB_CONTINUOUS, "x1");
    GRBVar x2 = model.addVar(-1.0, 1.0, 0.0, GRB_CONTINUOUS, "x2");

    // Array representation of first expression tree for x2 ^2
    int     opcode1[3] = {GRB_OPCODE_POW, GRB_OPCODE_VARIABLE, GRB_OPCODE_CONSTANT};
    double  data1[3]   = {-1.0, x2.index(), 2.0};
    int     parent1[3] = {-1, 0, 0};
    // Add first nonlinear constraint y1 = x2 ^2
    model.addGenConstrNL(y1, 3, opcode1, data1, parent1);

    // Array representation of second expression tree for sin(2.5 * x1) + x2
    int     opcode2[6] = {GRB_OPCODE_PLUS, GRB_OPCODE_SIN, GRB_OPCODE_MULTIPLY,
                          GRB_OPCODE_CONSTANT, GRB_OPCODE_VARIABLE,
                          GRB_OPCODE_VARIABLE};
    double  data2[6]   = {-1.0, -1.0, -1.0, 2.5, x1.index(), x2.index()};
    int     parent2[6] = {-1, 0, 1, 2, 2, 0};
    // Add second nonlinear constraint y2 = sin(2.5 *x 1) + x2
    model.addGenConstrNL(y2, 6, opcode2, data2, parent2);

    // Optimize model
    model.optimize();

    cout << y1.get(GRB_StringAttr_VarName) << " "
         << y1.get(GRB_DoubleAttr_X) << endl;
    cout << y2.get(GRB_StringAttr_VarName) << " "
         << y2.get(GRB_DoubleAttr_X) << endl;
    cout << x1.get(GRB_StringAttr_VarName) << " "
         << x1.get(GRB_DoubleAttr_X) << endl;
    cout << x2.get(GRB_StringAttr_VarName) << " "
         << x2.get(GRB_DoubleAttr_X) << endl;

    cout << "Obj: " << model.get(GRB_DoubleAttr_ObjVal) << endl;

  } catch(GRBException e) {
    cout << "Error code = " << e.getErrorCode() << endl;
    cout << e.getMessage() << endl;
  } catch(...) {
    cout << "Exception during optimization" << endl;
  }

  return 0;
}
