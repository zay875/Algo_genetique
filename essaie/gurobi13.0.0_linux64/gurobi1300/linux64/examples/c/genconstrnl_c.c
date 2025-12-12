/* Copyright 2025, Gurobi Optimization, LLC */

/* This example formulates and solves the following simple nonlinear model:

     minimize    y1 + y2
     subject to  y1 = x2 ^2
                 y2 = sin(2.5 * x1) + x2
                 y1, y2 free
                 -1 <= x1, x2 <= 1
*/

#include <stdlib.h>
#include <stdio.h>
#include "gurobi_c.h"

int
main(int   argc,
     char *argv[])
{
  GRBenv   *env   = NULL;
  GRBmodel *model = NULL;
  int       error = 0;

  /* Data for optimization variables */
  double  lb[4]       = {-GRB_INFINITY, -GRB_INFINITY, -1.0, -1.0};
  double  ub[4]       = {GRB_INFINITY, GRB_INFINITY, 1.0, 1.0};
  double  obj[4]      = {1.0, 1.0, 0.0, 0.0};
  char   *varnames[4] = {"y1", "y2", "x1", "x2"};

  /* Array representation of first expression tree for x2 ^2 */
  int     opcode1[3] = {GRB_OPCODE_POW, GRB_OPCODE_VARIABLE, GRB_OPCODE_CONSTANT};
  double  data1[3]   = {-1.0, 3.0, 2.0};
  int     parent1[3] = {-1, 0, 0};
  /* Array representation of second expression tree for sin(2.5 * x1) + x2 */
  int     opcode2[6] = {GRB_OPCODE_PLUS, GRB_OPCODE_SIN, GRB_OPCODE_MULTIPLY,
                        GRB_OPCODE_CONSTANT, GRB_OPCODE_VARIABLE,
                        GRB_OPCODE_VARIABLE};
  double  data2[6]   = {-1.0, -1.0, -1.0, 2.5, 2.0, 3.0};
  int     parent2[6] = {-1, 0, 1, 2, 2, 0};

  /* Data for querying solution information */
  double    sol[4];
  int       optimstatus;
  double    objval;

  /* Create environment */
  error = GRBloadenv(&env, "genconstrnl.log");
  if (error) goto QUIT;

  /* Create model with the three optimization variables */
  error = GRBnewmodel(env, &model, "genconstrnl", 4, obj, lb, ub, NULL,
                      varnames);
  if (error) goto QUIT;

  /* Add first nonlinear constraint y1 = x2 ^2 */
  error = GRBaddgenconstrNL(model, NULL, 0, 3, opcode1, data1, parent1);
  if (error) goto QUIT;
  /* Add second nonlinear constraint y2 = sin(2.5 * x1) + x2 */
  error = GRBaddgenconstrNL(model, NULL, 1, 6, opcode2, data2, parent2);
  if (error) goto QUIT;

  /* Optimize model */
  error = GRBoptimize(model);
  if (error) goto QUIT;

  /* Capture solution information */
  error = GRBgetintattr(model, GRB_INT_ATTR_STATUS, &optimstatus);
  if (error) goto QUIT;

  printf("\nOptimization complete\n");
  if (optimstatus == GRB_OPTIMAL) {
    error = GRBgetdblattr(model, GRB_DBL_ATTR_OBJVAL, &objval);
    if (error) goto QUIT;

    error = GRBgetdblattrarray(model, GRB_DBL_ATTR_X, 0, 4, sol);
    if (error) goto QUIT;

    printf("Optimal objective: %.4e\n", objval);

    printf("  y1=%.6f, y2=%.6f, x1=%.6f, x2=%.6f\n", sol[0], sol[1], sol[2], sol[3]);
  } else if (optimstatus == GRB_INF_OR_UNBD) {
    printf("Model is infeasible or unbounded\n");
  } else {
    printf("Optimization was stopped early\n");
  }


QUIT:

  /* Error reporting */
  if (error) {
    printf("ERROR: %s\n", GRBgeterrormsg(env));
    exit(1);
  }

  /* Free model */
  GRBfreemodel(model);

  /* Free environment */
  GRBfreeenv(env);

  return 0;
}
