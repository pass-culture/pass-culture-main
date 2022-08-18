#!/bin/bash


rm -f /tmp/bats-mock.*
for filename in .;
do
    bats "$filename" | tee result_output.txt
    rm /tmp/bats-mock.*
    if [[ $(cat result_output.txt | grep "not ok") ]];then
        exit 1
    fi
done
