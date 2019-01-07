#!/bin/sh

# Add generic redirects for netlify which work with everything routed to
# index.htm and relative paths to main.js and main.css for phonegap
# This is also used so that updates (and therefore new JS/CSS filenames)
# don't break the app for users that have the html in cache

JSPATH=`grep -o 'static/js/main\.[a-z0-9]*\.js' build/index.html`
CSSPATH=`grep -o 'static/css/main\.[a-z0-9]*\.css' build/index.html`

echo "" > build/_redirects

echo "/static/js/* /$JSPATH 301" >> build/_redirects
echo "/:path1/static/js/* /$JSPATH 301" >> build/_redirects
echo "/:path1/:path2/static/js/* /$JSPATH 301" >> build/_redirects
echo "/:path1/:path2/:path3/static/js/* /$JSPATH 301" >> build/_redirects
echo "/:path1/:path2/:path3/:path4/static/js/* /$JSPATH 301" >> build/_redirects
echo "/:path1/:path2/:path3/:path4/:path5/static/js/* /$JSPATH 301" >> build/_redirects
echo "/:path1/:path2/:path3/:path4/:path5/:path6/static/js/* /$JSPATH 301" >> build/_redirects

echo "/static/css/* /$JSPATH 301" >> build/_redirects
echo "/:path1/static/css/* /$JSPATH 301" >> build/_redirects
echo "/:path1/:path2/static/css/* /$JSPATH 301" >> build/_redirects
echo "/:path1/:path2/:path3/static/css/* /$JSPATH 301" >> build/_redirects
echo "/:path1/:path2/:path3/:path4/static/css/* /$JSPATH 301" >> build/_redirects
echo "/:path1/:path2/:path3/:path4/:path5/static/css/* /$JSPATH 301" >> build/_redirects
echo "/:path1/:path2/:path3/:path4/:path5/:path6/static/css/* /$JSPATH 301" >> build/_redirects

cat "public/_redirects" >> build/_redirects

echo "Redirects created."
