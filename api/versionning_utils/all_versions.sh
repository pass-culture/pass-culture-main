show_help() {
  echo "Usage: $(basename $0) [OPTIONS]"
  echo "Find all versions of a route in the code for a specific method organized by method"
  echo "Options:"
  echo "  -h, --help     Display this help message"
  echo "  -u             route URL (optional) if not provided, will return all versions of all routes"
  echo "  -m             route Method (GET, POST, PUT, DELETE, PATCH, OPTIONS, HEAD, TRACE) (optional) if not provided, will return all versions for each method"
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

while IFS= read -r method; do
    if [[ $METHOD ]] &&  [[ "$METHOD" != "$method" ]]; then

        continue
    fi
    first_in_method=True
    grep -rEn "@blueprint\.native_route\( *(rule *= *)?\"$URL\"(, *(version=)?\"v?[0-9]+\")?" src/pcapi/routes/native --include \*.py |
    while read -r line; do
        # Extract versions, assuming they start with "v" followed by numbers
        
        if [[ $line == *"$method"* ]]; then
            if [[ $first_in_method == True ]]; then
                echo "***$method***"
                first_in_method=False
            fi
            version=$(echo "$line" | sed -n 's/.*"v\([0-9]*\)".*/v\1/p')
            if [[ -z $version ]]; then
                # If no version is found, assume it's v1.
                version="v1"
            fi
            echo "$version: $line"
        fi
    done
done < "versionning_utils/http_methods.txt"
rm versionning_utils/http_methods.txt
