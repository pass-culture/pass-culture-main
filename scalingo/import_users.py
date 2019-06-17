from scripts.beneficiary.file_import import run
import sys

if len(sys.argv) == 1:
    raise ValueError("This script need the uploaded file name as an argument")

file_to_import = sys.argv[1]
run('/tmp/uploads/' + file_to_import)
