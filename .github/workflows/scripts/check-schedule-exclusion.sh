CALENDAR_FILE="./.github/workflows/scripts/schedule_exclusions.yml"
TODAY=$(date +%Y-%m-%d)
MATCH=$(yq '.[] | select(.date == "'$TODAY'") | .comment' "$CALENDAR_FILE")

if test -n "$MATCH"; then
  echo schedule_exclusion=true
  echo reason="$MATCH"
else
  echo schedule_exclusion=false
fi
