#!/bin/bash

for m in {2..10}; do
    PYTHONPATH=. python Programs/Source/permutation2.mpc --m "$m"
    
    if [ "$1" = "F" ]; then
      Scripts/ltos.sh permutation2 -N 2 -F
    else 
      Scripts/ltos.sh permutation2 -N 2 
    fi
done

for n in {2..4}; do
    PYTHONPATH=. python Programs/Source/permutation2.mpc --m 12
    
    if [ "$1" = "F" ]; then
      Scripts/ltos.sh permutation2 -N "$n" -F
    else 
      Scripts/ltos.sh permutation2 -N "$n" 
    fi
done

