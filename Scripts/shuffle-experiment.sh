#!/bin/bash

# $1 = mascot or ltos
# $2 = M
# $3 = N
# $4 = F for fake offline or R for real offline
# $5 = NoMake
if [ "$#" -le 2 ]; then
    echo "Usage: $0 <mascot|ltos> <M> <N> [F|R] [NoMake]"
    exit 1
fi

if [ "$1" = "all" ]; then 
echo "Ltos with real offline phase" > party0.out 
  ./$0 "ltos" $2 $3 "R"
echo "Ltos with fake offline phase" >> party0.out 
  ./$0 "ltos" $2 $3 "F" "NoMake"
echo "Waksman based with real offline phase" >> party0.out
  ./$0 "mascot" $2 $3 "R"
echo "Waksman based with fake offline phase" >> party0.out
  ./$0 "mascot" $2 $3 "F" "NoMake"
exit 0
fi
if [ "$5" != "NoMake" ]; then
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
fi


if [ "$4" = "F" ]; then
  make Fake-Offline.x mascot-party.x . > /dev/null
  Scripts/setup-online.sh "$3" > /dev/null
  ./Fake-Offline.x "$3" > /dev/null # Might need to to do all integers up to N, instead of just N
fi

run_script() {
  # $1 = number of repetitions
  # $2 = number of parties
  # $3 = mascot or ltos
  # $4 = fake offline
  # $5 = batch size
  echo $0
  echo $5
  for ((i=0;i<$1;i++)); do
    if [ "$4" = "F" ]; then
      Scripts/"$3".sh permutation2 -N $2 -F --batch-size $5
    else 
      Scripts/"$3".sh permutation2 -N $2 --batch-size $5
    fi
  done
}


run_experiemtn() {
  # $1 = mascot or ltos
  # $2 = M
  # $3 = N
  # $4 = F for fake offline or R for real offline
  for ((m=2;m<=$2;m++)); do
      PYTHONPATH=. python3 Programs/Source/permutation2.mpc --m "$m"
      
      echo "running "$1" with n=2 and m="$m""
      if [ $m -le 8 ]; then
        run_script 10 2 $1 $4
      elif [ $m -le 10 ]; then
        run_script 5 2 $1 $4
      elif [ $m -le 12 ]; then
        run_script 3 2 $1 $4
      else
        run_script 1 2 $1 $4
      fi
  done

  echo "-" >> party0.out 

  for ((n=2;n<=$3;n++)); do
      PYTHONPATH=. python3 Programs/Source/permutation2.mpc --m 12
      
      echo "running "$1" with n="$n" and m=12"
      run_script 1 $n $1 $4
  done

  echo "-" >> party0.out 
}


batch_test() {
  # $1 = m
  # $2 = mascot/ltos
  # $3 = fake offline
  PYTHONPATH=. python3 Programs/Source/permutation2.mpc --m "$1"

  for ((j = 100; j<=2000;j+=100)); do
    run_script 1 2 $2 $3 $j
    echo "ran script with batch size $j" >> party0.out
  done
}


batch_test 12 "ltos" "R"