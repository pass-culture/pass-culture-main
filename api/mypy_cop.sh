#!/bin/bash

type_ignore_counter=$(grep "type: ignore" -r src | wc -l | xargs)
git fetch origin master:master --quiet
git checkout master --quiet
master_type_ignore_counter=$(grep "type: ignore" -r src | wc -l | xargs)
git checkout - --quiet

echo "<h2>🚓 Mypy cop report:</h2>"

if [ $type_ignore_counter -lt $master_type_ignore_counter ]; then
    echo '<p>🎉 Number of type ignore inferior to master, good job !</p>'
fi

if [ $type_ignore_counter -gt $master_type_ignore_counter ]; then
    diff=$(($type_ignore_counter - $master_type_ignore_counter))
    echo '<p>😿 Number of type ignore superior to master</p>'
    echo "<p>At least $diff <i>#type:ignore</i> comments need to be resolved before merging</p>"
fi

if [ $type_ignore_counter -eq $master_type_ignore_counter ]; then
    echo "<p>Number of type ignore equal to master:</p>"
fi

echo "<table>"
echo "<tr><th>Master</th><th>Current branch</th></tr>"
echo "<tr><td>$master_type_ignore_counter</td><td>$type_ignore_counter</td></tr>"
echo "</table>"