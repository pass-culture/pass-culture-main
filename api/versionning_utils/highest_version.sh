#!/bin/bash
show_help() {
  echo "Usage: $(basename $0) [OPTIONS]"
  echo "Find the highest version of a route in the code"
  echo "Options:"
  echo "  -h, --help     Display this help message"
  echo "  -u             route URL (optional) if not provided, will return the highest version of all routes"
  echo "  -m             route Method (GET, POST, PUT, DELETE, PATCH, OPTIONS, HEAD, TRACE) (optional) if not provided, will return the highest version for each method"
  # Add more options and descriptions as needed
  exit 0
}

if [[ "$1" == "-h" || "$1" == "--help" ]]; then
  show_help
fi

URL=".*"; # Default value
while getopts u:m: flag
do
    case "${flag}" in
        u) URL=${OPTARG};;
        m) METHOD=${OPTARG};;
    esac
done
echo $'GET\nHEAD\nPOST\nPUT\nDELETE\nCONNECT\nOPTIONS\nTRACE\nPATCH'>versionning_utils/http_methods.txt
number_of_methods_found=0
while IFS= read -r method; do
    if [[ $METHOD ]] &&  [[ "$METHOD" != "$method" ]]; then
        continue
    fi
    first_in_method=True
    highest_version=0  # Initialize highest_version

    # Using process substitution to avoid subshell creation by pipe.
    while IFS= read -r line; do
        # Extract the version number, assuming it starts with "v" followed by numbers.
        if [[ $line == *"$method"* ]]; then
            version=$(echo "$line" | sed -n 's/.*"v\([0-9]*\)".*/\1/p')
            
            if [[ -z $version ]]; then
                # If no version is found, assume it's v1.
                version=1
            fi
            # Update the highest_version if a higher version is found.
            if (( version > highest_version )); then
                highest_version=$version
            fi
        fi
    done < <(grep -rEn "@blueprint\.native_route\( *(rule *= *)?\"$URL\"(, *(\"version\"=)?\"v?[0-9]+\")?" src/pcapi/routes/native/  --include \*.py)
    # Output the highest version found.
    if [[ $highest_version != 0 ]]; then
        if [[ $first_in_method == True ]]; then
            echo "***$method***"
            first_in_method=False
        fi
        echo "Highest version found: v$highest_version"
        number_of_methods_found=$((number_of_methods_found+1))
    fi
done < "versionning_utils/http_methods.txt"
echo "Number of methods found: $number_of_methods_found"
if [[ $number_of_methods_found == 0 ]]; then
    echo "Route $URL not found"
fi
rm versionning_utils/http_methods.txt