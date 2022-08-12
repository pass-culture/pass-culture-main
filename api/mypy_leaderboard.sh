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

# diff is positive if we reduce the number of errors
diff = $((master_count - this_branch_count))

if [ ${this_branch_count} -eq ${master_count} ]
then
    text="RAS"
elif [ ${this_branch_count} -lt ${master_count} ]
then
    text="Woop woop! 🎉"
elif [ ${this_branch_count} -gt ${master_count} ]
then
    text="Oh no! 💥"
fi

echo "<p>mypy report: ${text} this PR reduces by ${diff} the number of errors</p>"
