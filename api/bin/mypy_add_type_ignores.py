"""
This script is used to add type ignores to files that have mypy errors.
It is NOT meant to be run regularly, but only when mypy is upgraded, and we cannot fix all the errors in one go.

It is meant to be run after `mypy --show-error-codes src > mypy_results.txt` has been run.

The script will read the mypy output file mypy_results.txt, and add '# type: ignore' comments to the files that have errors.
"""

import os


# First, run `mypy --show-error-codes src > mypy_results.txt`


def add_type_ignore() -> None:
    result_dict: dict = {}

    with open(os.path.abspath(os.getcwd()) + "/mypy_results.txt", "r", encoding="utf8") as file_pointer:
        lines = file_pointer.readlines()
        lines.pop()
        for line in lines:
            split_line = line.split(" ")
            filename_and_line = split_line[0]

            log_type = split_line[1]
            if "error" not in log_type:
                continue

            error_code = split_line[-1].strip()
            filename = filename_and_line.split(":")[0]
            line_number = filename_and_line.split(":")[1]

            if filename not in result_dict:
                result_dict[filename] = []

            result_dict[filename].append((line_number, error_code))

    for filename, line_number_and_error in result_dict.items():
        with open(os.path.abspath(os.getcwd()) + "/" + filename, "r", encoding="utf8") as file_pointer:
            lines = file_pointer.readlines()
        with open(os.path.abspath(os.getcwd()) + "/" + filename, "w", encoding="utf8") as file_pointer:
            for line_number, error_code in line_number_and_error:
                line = lines[int(line_number) - 1]
                if "#" in line:
                    existing_comment = line.split("#")[1].strip()
                    stripped_error_code = error_code[1:-1]
                    if stripped_error_code in existing_comment:
                        continue
                    if "type: ignore" in existing_comment:
                        new_comment = existing_comment.replace("]", f", {stripped_error_code}]")
                        line = line.replace(existing_comment, new_comment)
                    else:
                        line = line.replace("#", f"# type: ignore {error_code} #")
                else:
                    line = line.replace("\n", f" # type: ignore {error_code}\n")
                lines[int(line_number) - 1] = line
            file_pointer.writelines(lines)


add_type_ignore()
