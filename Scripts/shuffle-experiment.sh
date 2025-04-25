#!/bin/bash

# $1 = Mascot or Ltos
# $2 = M
# $3 = N
# $4 = F for fake offline
if [ "$#" -le 2 ]; then
    echo "Usage: $0 <Mascot|Ltos> <M> <N> [F]"
    exit 1
fi

if [ "$1" = "Mascot" ]; then
  make clean
  make mascot -j
elif [ "$1" = "Ltos" ]; then
  make clean
  make ltos -j
else
  echo "Invalid argument. Use 'Mascot' or 'Ltos'."
  exit 1
fi


if [ "$4" = "F" ]; then
  make Fake-Offline.x mascot-party.x. > /dev/null
  Scripts/setup-online.sh "$3" > /dev/null
fi

for ((m=2;m<=$2;m++)); do
    PYTHONPATH=. python3 Programs/Source/permutation2.mpc --m "$m"
    
    if [ "$4" = "F" ]; then
      Scripts/ltos.sh permutation2 -N 2 -F
    else 
      Scripts/ltos.sh permutation2 -N 2 
    fi
done

for ((n=2;n<=$3;n++)); do
    PYTHONPATH=. python3 Programs/Source/permutation2.mpc --m 12
    
    if [ "$4" = "F" ]; then
      Scripts/ltos.sh permutation2 -N "$n" -F
    else 
      Scripts/ltos.sh permutation2 -N "$n" 
    fi
done

