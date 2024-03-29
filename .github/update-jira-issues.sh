#!/bin/bash
# Iterate over a list of commits. For each commits, grab the github commit number and update the jira ticket
# to get all commits since last run use the command : 
# `git log XXX..  --pretty=format:"%H" --reverse >> file.txt`
# where XXX is the last commit

JIRA_BINARY="$HOME/go/bin/jira"

Help()
{
  # Display Help
  echo "Iterate over a list of commits. For each commits, grab the github commit number and update the jira ticket"
  echo
  echo "Syntax: emmet-brown.sh [-h|f]"
  echo "options:"
  echo "h     Print this Help."
  echo "f     file to scan"
  echo
}


while getopts ":h:f:" option; do
  case $option in
    h) # display Help
        Help
        exit
        ;;
    f) # display Help
        FILE=$OPTARG
        ;;
    *) # Invalid option
        echo "Error: Invalid option"
        exit
        ;;
  esac
done

shift $((OPTIND-1))
if [ -z "${FILE}" ]; then
    Help
    exit
fi

Get_commit_number()
{
  local COMMIT_NUMBER=$(git rev-list --count $1)
  echo "$COMMIT_NUMBER"
}

Get_issue_id_from_commit()
{
  local COMMIT_MSG=$(git rev-list --format=%B --max-count=1 $1 | tail +2)
  local MSG_FMT=$(echo $COMMIT_MSG|tr -d '\n')
  local PC_NUMBER=$(echo $MSG_FMT | sed -E 's|\((PC-[0-9]{5})\).*|\1|g')
  if [[ "$MSG_FMT" == "$PC_NUMBER" ]]; then
    echo ""
  else
    echo "$PC_NUMBER"
  fi
}

Get_type_from_issue()
{
  local TYPE_ISSUE=$($JIRA_BINARY view $1 --template viewType)
  echo "$TYPE_ISSUE"
}

Get_jira_previous_commit_number()
{
  local PREV_COMMIT_NUMBER=$($JIRA_BINARY view $1)
  echo "$PREV_COMMIT_NUMBER"
}

Mark_issue_as_not_deployable()
{
  echo 'je m''apprete à update la jira avec jira edit --query=''"Numéro de commit[Number]" > '$1''' --override customfield_10044=true --override customfield_10086=false --noedit'
  $JIRA_BINARY edit --query='"Numéro de commit[Number]" > '$1'' --override customfield_10044=true --noedit

}

Push_commit_number_and_commit_hash_to_jira_issue()
{
  echo 'je m''apprete à update la jira avec jira edit '$1' --override customfield_10044=false --override customfield_10059='$2' --override customfield_10060='$3' --override customfield_10086=true --noedit'
  $JIRA_BINARY edit $1 --override customfield_10044=false --override customfield_10059=$2 --override customfield_10060=$3 --noedit
}

echo "Init jira env"
cp -R ../.jira.d/* $HOME/.jira.d
cat <<EOF >  $HOME/.jira.d/config.yml
endpoint: https://passculture.atlassian.net
user: dev@passculture.app
password-source: keyring
project: PC
EOF

echo parsed file : $FILE

while read line; do
  COMMIT_NUMBER=$(Get_commit_number $line)
  COMMIT_HASH=$line
  PC_NUMBER=$(Get_issue_id_from_commit $line)
  
  echo "COMMIT_HASH:$COMMIT_HASH"
  echo "COMMIT_NUMBER:$COMMIT_NUMBER"
  echo "PC_NUMBER:$PC_NUMBER"
  if [ "$PC_NUMBER" == "" ]; then
    echo "does not contain PC_NUMBER in commit message -> skip"
    continue
  fi
  TYPE_ISSUE=$(Get_type_from_issue $PC_NUMBER)
  echo "TYPE_ISSUE: $TYPE_ISSUE"
  if [[ "$TYPE_ISSUE" == "OPS Task" || "$TYPE_ISSUE" == "Infra Task" ]]; then
    echo "Ticket de type Infra Task -> skip"
    continue
  fi
  PREV_COMMIT_NUMBER=$(Get_jira_previous_commit_number $PC_NUMBER)
  echo "PREV_COMMIT_NUMBER:$PREV_COMMIT_NUMBER"
  if [[ "$PREV_COMMIT_NUMBER" != "<no value>" ]]; then
    Mark_issue_as_not_deployable $PREV_COMMIT_NUMBER
  fi
  Push_commit_number_and_commit_hash_to_jira_issue $PC_NUMBER $COMMIT_NUMBER $COMMIT_HASH
  echo
done < "$FILE"