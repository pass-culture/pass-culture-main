#!/bin/bash
#
# Display an HTML report about the evolution of mypy ignore count
# between the master branch and the current branch.
#
# Usage:
#
#   mypy_cop.sh <master_count> <this_branch_count>
#

master_count=$1
this_branch_count=$2

echo "<h2>🚓 Mypy cop report:</h2>"

if [ ${this_branch_count} -eq ${master_count} ]
then
    echo "<p>Number of type ignore equal to master:</p>"
elif [ ${this_branch_count} -lt ${master_count} ]
then
    echo '<p>🎉 Number of type ignore inferior to master, good job !</p>'
    echo "<p>Have yourself a merry little break and learn a few facts about the year <a href='https://fr.wikipedia.org/wiki/${this_branch_count}' target='_blank'>${this_branch_count}</a> </p>"
elif [ ${this_branch_count} -gt ${master_count} ]
then
    diff=$((${this_branch_count} - ${master_count}))
    echo '<p>😿 Number of type ignore superior to master</p>'
    echo "<p>At least $diff <i>#type:ignore</i> comments need to be resolved before merging</p>"
fi

echo "<table>"
echo "<tr><th>Master</th><th>Current branch</th></tr>"
echo "<tr><td>$master_count</td><td>$this_branch_count</td></tr>"
echo "</table>"
