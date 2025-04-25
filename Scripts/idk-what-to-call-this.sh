#!/bin/bash

for m in {2..10}; do
  PYTHONPATH=. python Programs/Source/permutation2.mpc --m "$m"
  Scripts/ltos.sh permutation2 -N 2
done
