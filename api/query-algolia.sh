#! /bin/sh

do_query() {
  query="$1"
  request_file="$2"
  algolia_request=$(sed -E "/\"query\":/ s/:.*/: \"\\\\\"$query\\\\\"\",/" $request_file)
  curl "https://e2ikxj325n-dsn.algolia.net/1/indexes/*/queries" \
    -H "x-algolia-api-key: $ALGOLIA_API_KEY" \
    -H "x-algolia-application-id: $ALGOLIA_APP_ID" \
    -d "$algolia_request" \
    2>/dev/null
}

parse_response() {
  jq '.results[].hits[] | [.objectID, .offer[]] | @csv' |
    sed 's/[\\"]//g'
}

sort_lines() {
  sort -n | uniq -i
}

get_outdated_records() {
  query="$(cat outdated-records.sql)"
  sqlite3 :memory: -separator ' | ' -cmd ".mode column" ".import -csv $output_file booking" "$query" 2>/dev/null
}

init_output_file() {
  echo "object_id,ean,indexed_at,bookings,name" >"$output_file"
}

output_file="booking.csv"
query="jamais plus"
request_file="query.json"
use_cache=1

while [ $# -gt 0 ]; do
  case $1 in
  -o | --output-file)
    output_file="$2"
    shift
    shift
    ;;
  -n | --no-cache)
    use_cache=
    shift
    ;;
  -q | --query)
    query="$2"
    shift
    shift
    ;;
  -r | --request-file)
    request_file="$2"
    shift
    shift
    ;;
  esac
done

if [ -f "$output_file" ] && [ ! $use_cache ]; then

  if [ ! "$ALGOLIA_API_KEY" ] || [ ! "$ALGOLIA_APP_ID" ]; then
    echo "Error: environment variables ALGOLIA_API_KEY and ALGOLIA_APP_ID are not set"
    exit 1
  fi

  init_output_file
  echo "$output_file cleared"

  echo "Querying Algolia for '$query'..."

  do_query "$query" "$request_file" |
    parse_response |
    sort_lines \
      >>"$output_file"

  echo "Done!"
fi

get_outdated_records
