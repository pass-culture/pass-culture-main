#!/bin/bash


rm -f /tmp/bats-mock.*
for filename in .;
do
    bats "$filename"
    rm /tmp/bats-mock.*
done

