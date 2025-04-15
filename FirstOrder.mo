model FirstOrder
  Real x;
initial equation
  x = 0;
equation
  der(x) = 1-x;
  annotation(experiment(StartTime=0,StopTime=8));
end FirstOrder;
