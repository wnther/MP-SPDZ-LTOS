#!/bin/bash

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


run_experiment() {
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
  # $4 = output file
  run_make $2

  PYTHONPATH=. python3 Programs/Source/permutation2.mpc --m "$1"

  for ((j = 100; j<=2000;j+=100)); do
    run_script 1 2 $2 $3 $j $4
  done
}

get_fake_data_size() {
  # $1 = m
  let f_size=2**$1*$1*4;
  echo $f_size
}

# $1 = which tests to run
if [ "$#" -lt 2 ]; then
    echo "Usage: $0 <experiment> <outfile>"
    echo "Where:"
    echo "experiment=fake-data|batch"
    echo "outfile is a string such as party0.out"
    exit 1
fi

if [ "$1" = "fake-data" ]; then
  setup_fake_data 2 $(get_fake_data_size 18)
elif [ "$1" = "batch" ]; then
  for ((vec_size=5;vec_size<=10;vec_size+=5)); do
    echo "running ltos batch test with m=$vec_size and real prep"
    echo "NEW_EXPERIMENT: ltos_batch_real_$vec_size" >> $2
    batch_test $vec_size "ltos" "R" $2
    echo "running ltos batch test with m=$vec_size and fake prep"
    echo "NEW_EXPERIMENT: ltos_batch_fake_$vec_size" >> $2
    batch_test $vec_size "ltos" "F" $2
  done
  for ((vec_size=5;vec_size<=10;vec_size+=5)); do
    echo "running mascot batch test with m=$vec_size and real prep"
    echo "NEW_EXPERIMENT: mascot_batch_real_$vec_size" >> $2
    batch_test $vec_size "mascot" "R" $2
    echo "running mascot batch test with m=$vec_size and fake prep"
    echo "NEW_EXPERIMENT: mascot_batch_fake_$vec_size" >> $2
    batch_test $vec_size "mascot" "F" $2
  done

elif [ "$1" = "2" ]; then
  run_experiment $1 12 12 "R"
elif [ "$1" = "3" ]; then
  run_experiment $1 12 12 "F"
else
  echo "Invalid argument for experiment. Use fake-data|batch"
fi
