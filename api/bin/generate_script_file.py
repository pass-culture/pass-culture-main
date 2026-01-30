#!/usr/bin/env python
"""
Generate a python (and sql) file in a folder of pcapi/scripts to be ran with a GitHub Action "console job"

Usage:

    $ bin/generate_script_file.py <my_script_namespace> [--with-sql]

Create the pcapi/scripts/<my_script_namespace> folder and add a main.py file with some base script code
Add an empty main.sql file if --with-sql is passed

(do not commit the python file if you only wish to run the sql part)
"""

import argparse
import os
import pathlib

import pcapi


PCAPI_DIR = pathlib.Path(pcapi.__path__[0])
SCRIPT_PATH = PCAPI_DIR / "scripts"

HEADER = """\
\"""
Job console documentation here: https://www.notion.so/passcultureapp/Documentation-Job-Console-769beeacd5a146de9c97b6f8ee544276

You can start the job from the infra repository with github cli :

gh workflow run on_dispatch_pcapi_console_job.yaml \\
  -f ENVIRONMENT_SHORT_NAME=tst \\
  -f RESOURCES="512Mi/.5" \\
  -f BRANCH_NAME={git_branch_name} \\
  -f NAMESPACE={namespace} \\
  -f SCRIPT_ARGUMENTS="";

\"""


"""

DEFAULT_HEADER = """\
\"""
Job console documentation here: https://www.notion.so/passcultureapp/Documentation-Job-Console-769beeacd5a146de9c97b6f8ee544276
Could not generate a path to the script: no git_branch_name provided
\"""


"""

PYTHON_TEMPLATE = """\
import argparse
import logging

from pcapi.app import app
from pcapi.models import db


logger = logging.getLogger(__name__)

def main(not_dry: bool) -> None:
    # implement your script here
    pass

if __name__ == "__main__":
    app.app_context().push()

    parser = argparse.ArgumentParser()
    parser.add_argument("--not-dry", action="store_true")
    args = parser.parse_args()

    main(not_dry=args.not_dry)

    if args.not_dry:
        logger.info("Finished")
        db.session.commit()
    else:
        logger.info("Finished dry run, rollback")
        db.session.rollback()
"""


def get_active_branch_name() -> str | None:
    head_dir = PCAPI_DIR / "../../../" / ".git" / "HEAD"
    with head_dir.open("r", encoding="utf8") as f:
        content = f.read().splitlines()

    for line in content:
        if line[0:4] == "ref:":
            return line.partition("refs/heads/")[2]

    return None


def main(namespace: str, git_branch_name: str | None, with_sql: bool) -> None:
    path = SCRIPT_PATH / namespace
    if not os.path.exists(path):
        os.makedirs(path)

    if not os.path.exists(path / "main.py"):
        with open(path / "main.py", mode="w", encoding="utf8") as f:
            if not git_branch_name:
                f.write(DEFAULT_HEADER)
            else:
                f.write(HEADER.format(git_branch_name=git_branch_name, namespace=namespace))
            f.write(PYTHON_TEMPLATE)

    if with_sql:
        with open(path / "main.sql", mode="a", encoding="utf8"):
            pass


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("namespace", type=str)
    parser.add_argument("--with-sql", action="store_true")
    args = parser.parse_args()

    if not args.namespace:
        raise ValueError("Please provide a namespace")

    current_branch_name = get_active_branch_name()
    if current_branch_name is None:
        print(
            "Could not find the current branch name. Make sure you are on a branch before running this script, if you want a nice url to copy paste when running in Github Actions."
        )

    main(namespace=args.namespace, git_branch_name=current_branch_name, with_sql=args.with_sql)
