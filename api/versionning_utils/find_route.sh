#!/bin/bash
show_help() {
  echo "Usage: $(basename $0) [OPTIONS]"
  echo "Find a route in the code"
  echo "Options:"
  echo "  -h, --help     Display this help message"
  echo "  -u             route URL (optional) if not provided, will return all routes"
  echo "  -v             route Version (optional) if not provided, will return all versions"
  echo "  -m             route Method (GET, POST, PUT, DELETE, PATCH, OPTIONS, HEAD, TRACE) (optional) if not provided, will return all methods"
  # Add more options and descriptions as needed
  exit 0
}

if [[ "$1" == "-h" || "$1" == "--help" ]]; then
  show_help
fi
URL=".*"; # Default value
VERSION=".*";
METHOD=".*";
while getopts u:v:m: flag
do
    case "${flag}" in
        u) URL=${OPTARG};;
        v) VERSION=${OPTARG};;
        m) METHOD=${OPTARG};;
    esac
done
repeat="";
if [[ $VERSION == ".*" || $VERSION == "1" ]]; then
    repeat="?";
fi
if ! grep -rEn "@blueprint\.native_route\( *(rule *= *)?\"$URL\"(, *(version *= *)?\"v$VERSION\")$repeat, *methods *= *\[.*\"$METHOD\".*]\)" src/pcapi/routes/native --include \*.py; then
    echo "No route found";
fi




