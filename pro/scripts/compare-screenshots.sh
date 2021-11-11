#!/bin/bash

git checkout master
yarn qa:test
mv testcafe_screenshots/branch testcafe_screenshots/origin
rm -rf testcafe_screenshots/origin/thumbnails
git checkout -
yarn qa:test

rm -rf testcafe_screenshots/diff
mkdir testcafe_screenshots/diff

for screenshot in $(ls testcafe_screenshots/origin/); do
  convert testcafe_screenshots/origin/$screenshot origin.rgba
  convert testcafe_screenshots/branch/$screenshot branch.rgba
  cmp -s {origin,branch}.rgba

  if [ $? != 0 ]; then
    convert '(' testcafe_screenshots/origin/$screenshot -flatten -grayscale Rec709Luminance ')' \
            '(' testcafe_screenshots/branch/$screenshot -flatten -grayscale Rec709Luminance ')' \
            '(' -clone 0-1 -compose darken -composite ')' \
            -channel RGB -combine testcafe_screenshots/diff/$screenshot

    rm origin.rgba
    rm branch.rgba

    exit 1
  fi
done

rm origin.rgba
rm branch.rgba
