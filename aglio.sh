#!/bin/bash

rm -f out.apib.md
rm -f out_include.apib.md
for i in *.apib.md; do
  echo "<!-- include($i) -->" >> out_include.apib.md
  cat $i >> out.apib.md
  aglio -i out_include.apib.md -o out.htm
done
