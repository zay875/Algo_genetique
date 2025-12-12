# Copyright 2025, Gurobi Optimization, LLC

PLATFORM = linux64
TWOUP    = ..
KEEPTU   = ../..
INC      = $(TWOUP)/../include/
CC       = gcc
CPP      = g++
CARGS    = -m64 -g
CPPARGS  = -std=c++98 -m64 -g
CLIB     = -L$(TWOUP)/../lib -lgurobi130
CPPLIB   = -L$(TWOUP)/../lib -lgurobi_c++ -lgurobi130
JSRC     = $(TWOUP)/java
CLASSDIR = -classpath $(TWOUP)/../lib/gurobi.jar:.
JFLAG    = -d . $(CLASSDIR)
GRBAPP   = dotnet
DOTNETFRAMEWORK ?= net8.0
PROJECTFILE     ?= gurobi-nuget.csproj

# Example names for C, C++, Java, C#/.Net
EXAMPLES = bilinear callback dense diet facility feasopt fixanddive \
           gc_pwl gc_pwl_func genconstr genconstrnl lp lpmethod lpmod mip1 mip2 multiobj \
           multiscenario params piecewise poolsearch qcp qp sensitivity sos sudoku tsp tune \
           workforce1 workforce2 workforce3 workforce4 workforce5

# Build examples are built by default but not run since it requires a remote server setup
BUILD_EXAMPLES = batchmode $(EXAMPLES)

# Java examples, same as above but different naming scheme
JAVA_EXAMPLES = Bilinear Callback Dense Diet Facility Feasopt Fixanddive \
                GCPWL GCPWLFunc Genconstr GenconstrNL Lp Lpmethod Lpmod Mip1 Mip2 Multiobj \
                Multiscenario Params Piecewise Poolsearch Qcp Qp Sensitivity Sos Sudoku Tsp Tune \
                Workforce1 Workforce2 Workforce3 Workforce4 Workforce5

JAVA_BUILD_EXAMPLES = Batchmode $(JAVA_EXAMPLES)

# Arguments for examples that require them
ARGS_batchmode     = $(TWOUP)/data/p0033.mps
ARGS_callback      = $(TWOUP)/data/p0033.mps
ARGS_feasopt       = $(TWOUP)/data/klein1.mps
ARGS_fixanddive    = $(TWOUP)/data/stein9.mps
ARGS_lp            = $(TWOUP)/data/klein1.mps
ARGS_lpmethod      = $(TWOUP)/data/afiro.mps
ARGS_lpmod         = $(TWOUP)/data/afiro.mps
ARGS_mip2          = $(TWOUP)/data/stein9.mps
ARGS_params        = $(TWOUP)/data/misc07.mps
ARGS_sensitivity   = $(TWOUP)/data/p0033.lp
ARGS_sudoku        = $(TWOUP)/data/sudoku
ARGS_sudoku_c++    = < $(TWOUP)/data/sudoku
ARGS_tsp           = 50
ARGS_tune          = $(TWOUP)/data/p0033.mps

all: $(addsuffix _c, $(BUILD_EXAMPLES)) \
     $(addsuffix _c++, $(BUILD_EXAMPLES)) \
     $(addsuffix .class, $(JAVA_BUILD_EXAMPLES))

build: build_c build_c++ build_java

build_c: $(addsuffix _c, $(EXAMPLES))

build_c++: $(addsuffix _c++, $(EXAMPLES))

build_java: $(addsuffix .class, $(JAVA_EXAMPLES))

run: run_c run_c++ run_java # run_dotnet

run_c: $(addprefix run_, $(addsuffix _c, $(EXAMPLES)))

run_c++: $(addprefix run_, $(addsuffix _c++, $(EXAMPLES)))

run_java: $(addprefix run_, $(JAVA_EXAMPLES))

run_dotnet: $(addprefix run_, $(addsuffix _cs, $(EXAMPLES)))

## Build rules
%_c: $(TWOUP)/c/%_c.c
	$(CC) $(CARGS) -o $@ $< -I$(INC) $(CLIB) -lm

%_c++: $(TWOUP)/c++/%_c++.cpp
	$(CPP) $(CPPARGS) -o $@ $< -I$(INC) $(CPPLIB) -lm

%.class: $(JSRC)/%.java
	javac $(JFLAG) $<

## Run rules
run_%_c: %_c
	./$< $(ARGS_$*)

# Use specialized c++ ARGS entry if exists
run_%_c++: %_c++
	./$< $(or $(ARGS_$*_c++),$(ARGS_$*))

run_%: %.class
	java $(CLASSDIR) $* $(ARGS_$(shell echo $* | tr '[:upper:]' '[:lower:]'))

run_%_cs:
	cd $(GRBAPP); \
	rm -f *.cs; \
	cp $(KEEPTU)/c#/$*_cs.cs .; \
	dotnet run --project=$(PROJECTFILE) -p:TargetFrameworks=$(DOTNETFRAMEWORK) --framework=$(DOTNETFRAMEWORK) $(ARGS_$* | sed 's|$(TWOUP)|$(KEEPTU)|g')


clean:
	rm -rf *.o *_c *_c++ *.class *.log *.rlp *.lp *.bas *.ilp *.mps *.prm; \
	if [ -d $(GRBAPP) ]; then \
		cd $(GRBAPP); \
		find . ! \( -name "gurobi*.csproj" -o -name . \) -exec rm -rf {} +; \
	fi
