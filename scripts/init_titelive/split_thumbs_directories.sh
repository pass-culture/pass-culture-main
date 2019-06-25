#!/usr/bin/env bash

if [ "$1" == "-h" ]; then
    echo "$(basename "$0") [-h] [-d directory_to_split_path] -- program to split folder into subfolders
where:
    -h  show this help text
    -d  images directories absolute path (with / at the end)
    -n  number of elements per subdirectory"
    exit 0
fi

# GET DIRECTORY TO SPLIT
if [[ $# -gt 1 ]] && [[ "$1" == "-d" ]]; then
  top_level_directory=$2
  shift 2
else
  echo "You must provide an absolute path for directory to split."
  exit 1
fi

# GET NUMBER OF ELEMENTS PER SUBDIRECTORY
if [[ $# -gt 1 ]] && [[ "$1" == "-d" ]]; then
  max_files_per_directory=$2
  shift 2
else
  max_files_per_directory=20000
fi


declare -i file_count=0
declare -i directory_count=4

for filename in "$top_level_directory"/*
do
    if [[ -f "$filename" ]]; then
        if [ "$file_count" -eq 0 ]
        then
            mkdir "$top_level_directory/$directory_count"
        fi

        mv "$filename" "${directory_count}/"
        file_count+=1

        if [ "$file_count" -ge "$max_files_per_directory" ]
        then
            directory_count+=1
            file_count=0
        fi
    fi
done
