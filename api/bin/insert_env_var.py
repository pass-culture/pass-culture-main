"""
Script to insert a new environment variable in all .env files.

Usage: python bin/insert_env_var.py VARIABLE_NAME
If the variable name is not provided as an argument, the script will prompt the user for it.

The script will then prompt the user for the value of the variable in each environment.
If no value is provided, the variable will not be inserted in the corresponding .env file.
"""

import re
import sys


ENV_FILES = ["integration", "production", "staging", "testing", "development"]


# If the variable name is provided as an argument, use it. Otherwise, prompt the user for it.
if len(sys.argv) > 1:
    var_name = sys.argv[1]
else:
    var_name = input("Name of the environnement variable: ")

# check if the variable name is already in any of the .env.{environment} files
for env in ENV_FILES:
    with open(".env.{}".format(env), "r", encoding="utf8") as f:
        # if the variable name is already defined, exit the script
        if re.search(r"^{}=.*$".format(var_name), f.read(), re.MULTILINE):
            print("The variable {} is already defined in the .env.{} file.".format(var_name, env))
            sys.exit(1)


# Then, prompt the user for the variable value in integration, production, staging, testing and development
# If no value is provided, ignore the environment
var_value = {}

for env in ENV_FILES:
    env_value = input("value in {} (enter to skip): ".format(env.upper()))
    if env_value:
        var_value[env] = env_value

# Finally, write the variable to each .env.{environment_name} file
for env, value in var_value.items():
    with open(".env.{}".format(env), "r", encoding="utf8") as file_pointer:
        lines = file_pointer.readlines()
        # find the line to insert the variable after
        # Find line where the variable name is alphabetically before the variable to insert. Ignore lines that are comments.
        # If no line is found, insert the variable at the beginning of the file.
        line_index = next(
            (i for i, line in enumerate(lines) if not line.startswith("#") and line > "{}=".format(var_name)),
            len(lines),
        )

    with open(".env.{}".format(env), "w", encoding="utf8") as f:
        # Write the variable at the right place
        lines = lines[:line_index] + ["{}={}\n".format(var_name, value)] + lines[line_index:]
        f.writelines(lines)
