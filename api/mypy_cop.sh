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


extra=""

if [ ${this_branch_count} -eq ${master_count} ]
then
    # blue circle
    symbol_url="https://github.githubassets.com/images/icons/emoji/unicode/1f535.png"
    sign="="
elif [ ${this_branch_count} -lt ${master_count} ]
then
    # green check mark
    symbol_url="https://github.githubassets.com/images/icons/emoji/unicode/2714.png"
    sign="↘"
    extra="<p>Have yourself a merry little break and learn a few facts about the year <a href='https://fr.wikipedia.org/wiki/${this_branch_count}' target='_blank'>${this_branch_count}</a>.</p>"
elif [ ${this_branch_count} -gt ${master_count} ]
then
    # red cross
    sign="↗"
    symbol_url="https://github.githubassets.com/images/icons/emoji/unicode/274c.png"
fi

echo "<p><img src=\"${symbol_url}\" width=\"12\" height=\"12\"> mypy cop report: ${master_count} (master) ${sign} ${this_branch_count} (your branch)</p>"
echo ${extra}
