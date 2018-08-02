#!/bin/sh

# ------
# ESLint Checking using script
#
# If git is reporting that your prettified files are still modified
# after committing, you may need to add a post-commit script
# to update git's index as described in this issue.
#
# @see https://prettier.io/docs/en/precommit.html#option-5-bash-script
#
jsfiles=$(git diff --cached --name-only --diff-filter=ACM "*.js" "*.jsx" | tr '\n' ' ')
[ -z "$jsfiles" ] && exit 0

for file in $jsfiles
do
  # we only want to lint the staged changes, not any un-staged changes
  git show ":$file" | ./node_modules/.bin/eslint --stdin --stdin-filename "$file"
  if [ $? -ne 0 ]; then
    echo "ESLint failed on staged file '$file'. Please check your code and try again. You can run ESLint manually via npm run eslint."
    # exit with failure status
    exit 1
  fi
done

# Prettify all staged .js files
echo "$jsfiles" | xargs ./node_modules/.bin/prettier-eslint --eslint-config-path ./.eslintrc.json --config ./.prettierrc.json --list-different --write

# Add back the modified/prettified files to staging
echo "$jsfiles" | xargs git add

exit 0
