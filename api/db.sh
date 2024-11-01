#! /bin/sh

input_csv_file="$1"
sql_query="$2"
table="$3"
sqlite_script=$(
    cat <<EOM
.mode csv
.import $input_csv_file $table
.mode column
$sql_query
.quit
EOM
)
echo "$sqlite_script" | sqlite3
