#!/bin/bash

# ***
#
# Script for running experiments
#
# ***

run_make() {
  # $1 = mascot or ltos
  if test -f "$1-has-been-made"; then
    :
  else 
    make clean
    
    rm "ltos-has-been-made"
    rm "mascot-has-been-made"

    make "$1" -j
    touch "$1-has-been-made"
  fi
}

setup_fake_data() {
  # $1 = N
  # $2 = data amount
  make Fake-Offline.x mascot-party.x . -j > /dev/null
  Scripts/setup-online.sh "$1" 128 128 "$2" > /dev/null
  # ./Fake-Offline.x "$1" > /dev/null # Might need to to all integers up to N, instead of just N
}

run_script() {
  # $1 = number of repetitions
  # $2 = number of parties
  # $3 = mascot or ltos
  # $4 = fake offline
  # $5 = batch size
  # $6 = output file
  for ((run_script_i=0;run_script_i<$1;run_script_i++)); do
    if [ "$4" = "F" ]; then
      Scripts/"$3".sh permutation2 -N $2 -F --batch-size $5 >> $6
    else 
      Scripts/"$3".sh permutation2 -N $2 --batch-size $5 >> $6
    fi
    echo "ran script with batch size $5" >> $6
  done
}



# ***
#
# Different helper functions for running specific experiments
#
# ***


batch_test_large() {
  # $1 = m
  # $2 = mascot/ltos
  # $3 = fake offline
  # $4 = output file
  run_make $2
  PYTHONPATH=. python3 Programs/Source/permutation2.mpc --m "$1"

  for ((j = 1000; j<=20000;j+=1000)); do
    run_script 1 2 $2 $3 $j $4
  done
}

batch_test_small() {
  # $1 = m
  # $2 = mascot/ltos
  # $3 = fake offline
  # $4 = output file
  run_make $2
  PYTHONPATH=. python3 Programs/Source/permutation2.mpc --m "$1"

  for ((j = 25; j<=500;j+=25)); do
    run_script 1 2 $2 $3 $j $4
  done
}

fake_compare_test_20() {
  # $1 = output file

  run_make "ltos"
  echo "NEW_EXPERIMENT: ltos_fake" >> $1
  for ((vec_size=3;vec_size<=20;vec_size+=1)); do
    PYTHONPATH=. python3 Programs/Source/permutation2.mpc --m $vec_size
    echo "running fake (ltos) comparrison test with vec_size=$vec_size"
    run_script 1 2 "ltos" "F" 100 $1
  done

  run_make "mascot"
  echo "NEW_EXPERIMENT: waksman_based_fake" >> $1
  for ((vec_size=3;vec_size<=20;vec_size+=1)); do
    PYTHONPATH=. python3 Programs/Source/permutation2.mpc --m $vec_size
    echo "running fake (mascot) comparrison test with vec_size=$vec_size"
    run_script 1 2 "mascot" "F" 100 $1
  done
}

real_compare_test_20() {
  # $1 = output file

  # BATCH SIZE IS NOT OPTIMAL IN TERMS OF ROUND COMPLEXITY

  run_make "ltos"
  echo "NEW_EXPERIMENT: ltos_real" >> $1
  for ((vec_size=3;vec_size<=20;vec_size+=1)); do
    PYTHONPATH=. python3 Programs/Source/permutation2.mpc --m $vec_size
    echo "running real (ltos) comparrison test with vec_size=$vec_size"
    run_script 1 2 "ltos" "R" 1000 $1
  done

  run_make "mascot"
  echo "NEW_EXPERIMENT: waksman_based_real" >> $1
  for ((vec_size=3;vec_size<=20;vec_size+=1)); do
    PYTHONPATH=. python3 Programs/Source/permutation2.mpc --m $vec_size
    echo "running real (mascot) comparrison test with vec_size=$vec_size"
    run_script 1 2 "mascot" "R" 1000 $1
  done
}

fake_compare_test_network_20() {
  # $1 = output file
  # $2 = ip address
  # $3 = party number
  # $4 = nomake
  if [ "$4" == "nomake" ]; then
    echo "Press any key to continue..." 
    read -n 1 -s
    echo "Continuing..." 
  else
    run_make "ltos"
  fi
  echo "NEW_EXPERIMENT: ltos_fake_network_local" >> $1
  for ((vec_size=3;vec_size<=20;vec_size+=1)); do
    PYTHONPATH=. python3 Programs/Source/permutation2.mpc --m $vec_size
    echo "running fake (ltos) comparrison test over simulated network with vec_size=$vec_size"
    ./ltos-mascot-party.x -N 2 -h $2 $3 permutation2 -F >> $1
    echo "ran script with batch size 1000" >> $1
    echo "plot_line_break" >> $1
  done
  
  if [ "$4" = "nomake" ]; then
    echo "Press any key to continue..." 
    read -n 1 -s
    echo "Continuing..." 
  else
    run_make "mascot"
  fi
  echo "NEW_EXPERIMENT: waksman_based_fake_network_local" >> $1
  for ((vec_size=3;vec_size<=20;vec_size+=1)); do
    PYTHONPATH=. python3 Programs/Source/permutation2.mpc --m $vec_size
    echo "running fake (mascot) comparrison test over simulated network with vec_size=$vec_size"
    ./mascot-party.x -N 2 -h $2 $3 permutation2 -F >> $1
    echo "ran script with batch size 1000" >> $1
    echo "plot_line_break" >> $1
  done
}

get_fake_data_size() {
  # $1 = m
  let f_size=2**$1*$1*4;
  echo $f_size
}




# $1 = which tests to run
if [ "$#" -lt 2 ]; then
    echo "Usage: $0 <experiment> <outfile> [ip address] [party number] [nomake]"
    echo "Where:"
    echo "experiment=fake-data|batch"
    echo "outfile is a string such as party0.out"
    exit 1
fi

if [ "$1" = "fake-data" ]; then
  setup_fake_data 2 $(get_fake_data_size 18)
elif [ "$1" = "batch-real" ]; then
  for ((vec_size=3;vec_size<=15;vec_size+=3)); do
    echo "running ltos batch test with vec_size=$vec_size and real prep"
    echo "NEW_EXPERIMENT: ltos_batch_real_$vec_size" >> $2
    batch_test_large $vec_size "ltos" "R" $2
  done
  for ((vec_size=3;vec_size<=15;vec_size+=3)); do
    echo "running mascot batch test with vec_size=$vec_size and real prep"
    echo "NEW_EXPERIMENT: mascot_batch_real_$vec_size" >> $2
    batch_test_large $vec_size "mascot" "R" $2
  done
elif [ "$1" = "batch-fake" ]; then
  for ((vec_size=5;vec_size<=20;vec_size+=5)); do
    echo "running ltos batch test with vec_size=$vec_size and fake prep"
    echo "NEW_EXPERIMENT: ltos_batch_fake_$vec_size" >> $2
    batch_test_small $vec_size "ltos" "F" $2
  done
  for ((vec_size=5;vec_size<=20;vec_size+=5)); do
    echo "running mascot batch test with vec_size=$vec_size and fake prep"
    echo "NEW_EXPERIMENT: mascot_batch_fake_$vec_size" >> $2
    batch_test_small $vec_size "mascot" "F" $2
  done
elif [ "$1" = "compare-fake" ]; then
  fake_compare_test_20 $2
elif [ "$1" = "compare-real" ]; then
  real_compare_test_20 $2
elif [ "$1" = "compare-fake-network" ]; then
  if [ "$#" -lt 4 ]; then
    echo "no ip address or party number given"
    exit 1
  fi
  fake_compare_test_network_20 $2 $3 $4 $5
else
  echo "Invalid argument for experiment. Use fake-data|batch-fake|batch-real|compare-fake|compare-real|compare-fake-network"
fi
