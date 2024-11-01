#! /bin/sh

output_file="booking.csv"
use_cache=

if [ ! -f "$output_file" ] || [ ! "$use_cache" ]; then
  echo "Querying Algolia..."
  ./algolia.sh >"$output_file"
  echo "Done!"
fi

table_name="booking"
sql_query=$(
  cat <<EOM
SELECT
    $table_name."distinct",
    $table_name.indexedAt,
    $table_name.last30DaysBookings,
    substr($table_name.name, 0, 50) as short_name,
    $table_name.objectID as example_id,
    count(*) as number_of_lines
FROM
    $table_name
GROUP BY
    $table_name."distinct",
    $table_name.last30DaysBookings
ORDER BY
    $table_name."distinct" ASC,
    $table_name.indexedAt DESC,
    number_of_lines DESC;
EOM
)

./db.sh "$output_file" "$sql_query" "$table_name"
