rm -f apiary.apib
rm -f apiary.apib.md
for i in ./src/*.apib.md; do
  cat $i >> apiary.apib
  cat $i >> apiary.apib.md
  echo "\n" >> apiary.apib
  echo "\n" >> apiary.apib.md
done
