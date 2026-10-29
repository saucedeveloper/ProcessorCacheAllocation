#!/bin/bash

#sizes=(1024 2048 4096 8192 16384 32768 65536 131072 262144 524288 1048576 2097152 4194304)
sizes=(4096 8192 16384 32768 65536 131072 262144 524288 1048576 2097152 4194304)
#sizes=(1024 2048)

for i in ${sizes[@]}; 
do
	valgrind --tool=cachegrind --cache-sim=yes --LL=$i,4,64 --I1=32768,4,64 --D1=32768,4,64  ./pca-medium medium.data 722 800 R 2>&1 | tee cachegrind_run_$i.log; 
done



