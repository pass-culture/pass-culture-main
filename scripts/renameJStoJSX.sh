#!/bin/sh

echo "Fetching misnamed files"
FILES_TO_RENAME=$(grep --exclude-dir={node_modules,scripts} --exclude=\*.jsx -Rl 'import React' ./)

echo "Rename fetched results"
for FILE in $FILES_TO_RENAME
do
  mv -- "$FILE" "$(dirname "$FILE")/$(basename "$FILE" .js).jsx"
  echo "Renamed $(dirname "$FILE")/$(basename "$FILE") to jsx"
done

printf -- '\033[32m SUCCESS: yay \033[0m\n';
printf -- '\n';
exit 0
