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

# Keep only 2 last backups
echo "Backups to be delete : $(find $absolute_path_to_backup_directory -name "*.pgdump" |sort -r |tail +3)"
rm $(find $absolute_path_to_backup_directory -name "*.pgdump" |sort -r |tail +3)

if [ $? -eq 0 ]; then
  echo "Old backups cleaned!"
else
  echo 'Backup cleaning failed'
fi
