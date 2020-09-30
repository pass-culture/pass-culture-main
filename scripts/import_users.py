from scripts.beneficiary.file_import import run
import sys

if __name__ == "__main__":
    if len(sys.argv) == 1:
        raise ValueError("This script need the uploaded file name as an argument")
    path_to_file_to_import = sys.argv[1]
    run(path_to_file_to_import)
