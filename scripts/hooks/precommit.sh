#!/bin/bash

# ------
# ESLint Checking using script
#
# If git is reporting that your prettified files are still modified
# after committing, you may need to add a post-commit script
# to update git's index as described in this issue.

STAGED_SVG=$(git diff --cached --name-only --diff-filter=ACM | grep -E ".svg$")
if [[ "$STAGED_SVG" != "" ]]; then
  echo "$STAGED_SVG" | xargs ./node_modules/.bin/svgo --disable=removeViewBox
  echo "$STAGED_SVG" | xargs git add
fi

STAGED_FILES=$(git diff --cached --name-only --diff-filter=ACM | grep -E ".js$|.jsx$")
if [[ "$STAGED_FILES" = "" ]]; then
  exit 0
fi

for FILE in $STAGED_FILES
do
  eslint --quiet --max-warnings 0 "$FILE"
  if [[ "$?" == 0 ]]; then
    echo "\t\033[32mESLint Passed: $FILE\033[0m"
  else
    echo "\t\033[41mESLint Failed: $FILE\033[0m"
    exit 1
  fi
done

# Prettify all staged .js files
echo "$STAGED_FILES" | xargs ./node_modules/.bin/prettier-eslint --eslint-config-path ./.eslintrc --config ./.prettierrc --list-different --write

# Add back the modified/prettified files to staging
echo "$STAGED_FILES" | xargs git add

exit 0
