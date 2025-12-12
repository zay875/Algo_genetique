/* Copyright 2025, Gurobi Optimization, LLC */

/* This example reads a model from a file and tunes it.
   It then writes the best parameter settings to a file
   and solves the model using these parameters. */

import com.gurobi.gurobi.*;

public class Tune {
  public static void main(String[] args) {

    if (args.length < 1) {
      System.out.println("Usage: java Tune filename");
      System.exit(1);
    }

    try {
      GRBEnv env = new GRBEnv();

      // Read model from file
      GRBModel model = new GRBModel(env, args[0]);

      // Set a time limit for the model
      model.set(GRB.DoubleParam.TimeLimit, 5);

      // Set a time limit for the whole tuning run
      // Note that both time limits are chosen to have a quick demonstration.
      // In general, a total tune time limit should be set such that the
      // tuning tool can test several hundreds of parameter setting
      model.set(GRB.DoubleParam.TuneTimeLimit, 60);

      // Set the TuneResults parameter to 2
      //
      // The first parameter setting is the result for the first solved
      // setting. The second entry the parameter setting of the best
      // parameter setting.
      model.set(GRB.IntParam.TuneResults, 2);

      // Tune the model
      model.tune();

      // Get the number of tuning results
      int resultcount = model.get(GRB.IntAttr.TuneResultCount);

      if (resultcount >= 2) {

        // Load the tuned parameters into the model's environment
        //
        // Note, the first parameter setting is associated to the first
        // solved setting and the second parameter setting to best tune
        // result.
        model.getTuneResult(1);

        // Write the tuned parameters to a file
        model.write("tune.prm");

        // Solve the model using the tuned parameters
        model.optimize();
      }

      // Dispose of model and environment
      model.dispose();
      env.dispose();

    } catch (GRBException e) {
      System.out.println("Error code: " + e.getErrorCode() + ". "
          + e.getMessage());
    }
  }
}
