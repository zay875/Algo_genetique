' Copyright 2025, Gurobi Optimization, LLC
'
' This example formulates and solves the following simple nonlinear model:
'
'    minimize    y1 + y2
'    subject to  y1 = x2 ^2
'                y2 = sin(2.5 * x1) + x2
'                y1, y2 free
'                -1 <= x1, x2 <= 1


Imports System
Imports Gurobi

Class mip1_vb
    Shared Sub Main()

        Try
            Dim env As GRBEnv = New GRBEnv("genconstrnl.log")
            Dim model As GRBModel = New GRBModel(env)

            ' Create variables, only y variables have an objective coefficient
            Dim y1 As GRBVar = model.AddVar(-GRB.INFINITY, GRB.INFINITY, 1.0,
	        GRB.CONTINUOUS, "y1")
            Dim y2 As GRBVar = model.AddVar(-GRB.INFINITY, GRB.INFINITY, 1.0,
	        GRB.CONTINUOUS, "y2")
            Dim x1 As GRBVar = model.AddVar(-1.0, 1.0, 0.0, GRB.CONTINUOUS, "x1")
            Dim x2 As GRBVar = model.AddVar(-1.0, 1.0, 0.0, GRB.CONTINUOUS, "x2")

            ' Array representation of first expression tree for x2 ^2
            Dim opcode1 As Integer() = new Integer() {GRB.OPCODE_POW,
                GRB.OPCODE_VARIABLE, GRB.OPCODE_CONSTANT}
            Dim data1 As Double() = new Double() {-1.0, x2.Index, 2.0}
            Dim parent1 As Integer() = new Integer() {-1, 0, 0}
            ' Add second nonlinear constraint y1 = x2 ^2
            model.AddGenConstrNL(y1, opcode1, data1, parent1, "univariate_constraint")

            ' Array representation of second expression tree for sin(2.5 * x1) + x2
            Dim opcode2 As Integer() = new Integer() {GRB.OPCODE_PLUS,
                GRB.OPCODE_SIN, GRB.OPCODE_MULTIPLY, GRB.OPCODE_CONSTANT,
                GRB.OPCODE_VARIABLE, GRB.OPCODE_VARIABLE}
            Dim data2 As Double() = new Double() {-1.0, -1.0, -1.0, 2.5, x1.Index, x2.Index}
            Dim parent2 As Integer() = new Integer() {-1, 0, 1, 2, 2, 0}
            ' Add second nonlinear constraint y2 = sin(2.5 * x1) + x2
            model.AddGenConstrNL(y2, opcode2, data2, parent2, "multivariate_constraint")

            ' Optimize model

            model.Optimize()

            Console.WriteLine(y1.VarName & " " & y1.X)
            Console.WriteLine(y2.VarName & " " & y2.X)
            Console.WriteLine(x1.VarName & " " & x1.X)
            Console.WriteLine(x2.VarName & " " & x2.X)

            Console.WriteLine("Obj: " & model.ObjVal)

            ' Dispose of model and env

            model.Dispose()
            env.Dispose()

        Catch e As GRBException
            Console.WriteLine("Error code: " & e.ErrorCode & ". " & e.Message)
        End Try
    End Sub
End Class
