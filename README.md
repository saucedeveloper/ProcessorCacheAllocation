# Processor Cache Allocation

The goal of this project is to minimize the size of the cache used to run 3 programs periodically on a single Cortex-A53 processor.
The data necessary to estimate the worst case execution time of these programs is meant to be calculated in real time through an expensive valgrind invocation for each pair of program and cache size.
However, an exhaustive collection of log files for each program, as well as a parser are also provided.

## How to run optimization
```bash
python3 solve_allocation.py > solve.log
```

## How to run pareto front
```bash
python3 solve_allocation.py -p > pareto.log
```
