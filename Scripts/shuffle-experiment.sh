#!/bin/bash

# $1 = mascot or ltos
# $2 = M
# $3 = N
# $4 = F for fake offline
if [ "$#" -le 2 ]; then
    echo "Usage: $0 <mascot|ltos> <M> <N> [F]"
    exit 1
fi

if [ "$1" = "mascot" ]; then
  make clean
  make mascot -j
elif [ "$1" = "ltos" ]; then
  make clean
  make ltos -j
else
  echo "Invalid argument. Use 'mascot' or 'ltos'."
  exit 1
fi


if [ "$4" = "F" ]; then
  make Fake-Offline.x mascot-party.x. > /dev/null
  Scripts/setup-online.sh "$3" > /dev/null
fi

run_script() {
  # $1 = number of repetitions
  # $2 = number of parties
  # $3 = mascot or ltos
  # $4 = fake offline
  for ((i=0;i<$1;i++)); do
    if [ "$4" = "F" ]; then
      Scripts/"$3".sh permutation2 -N $2 -F
    else 
      Scripts/"$3".sh permutation2 -N $2 
    fi
  done
}



for ((m=2;m<=$2;m++)); do
    PYTHONPATH=. python3 Programs/Source/permutation2.mpc --m "$m"
    
    run_script 1 2 $1 $4
done

for ((n=2;n<=$3;n++)); do
    PYTHONPATH=. python3 Programs/Source/permutation2.mpc --m 12
    
    run_script 1 $n $1 $4
done

