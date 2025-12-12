// Copyright (C) 2025, Gurobi Optimization, LLC
// All Rights Reserved
#include "Common.h"

const string
GRBException::getMessage() const throw()
{
  return what();
}

int
GRBException::getErrorCode() const throw()
{
  return error;
}
