#!/bin/bash
input="user_list"
while IFS= read -r var
do
  echo "$var"$(pwgen 20) >> user_list_2
done < "$input"