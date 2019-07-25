#!/usr/bin/env bash


if [ "$1" == "-h" ]; then
    echo "$(basename "$0") [-h] [-b backups_directory_path] -- program to delete backups older than 6 months
     and keeping 1 per week between 1 and 6 months
where:
    -h  show this help text
    -b  backup directory absolute path (whithout / at the end)"
    exit 0
fi

# GET BACKUP DIRECTORY
if [[ $# -gt 1 ]] && [[ "$1" == "-b" ]]; then
  absolute_path_to_backup_directory=$2
  shift 2
else
  echo "You must provide an absolute path for backups directory."
  exit 1
fi

# Delete all backups older than 6 months
find "$absolute_path_to_backup_directory"/* -type f -ctime +180 -delete

# One per week between 1 week and 6 months
files_between_1_week_and_1_months=$(find "$absolute_path_to_backup_directory"/* -type f -ctime -180 -ctime +7)

IFS='
' read -d '' -a files <<< "${files_between_1_week_and_1_months}"

for file in "${files[@]}"
do
    num_of_day=${file:(-16):2}
    if [[ ${num_of_day:0:1} == 0 ]];then
        num_of_day=${num_of_day:1:1}
    fi
    if [[ $(( num_of_day % 7 )) == 0 ]]; then
        echo "$file: kept"
    else
        rm "$file"
        echo "$file: deleted"
    fi
done