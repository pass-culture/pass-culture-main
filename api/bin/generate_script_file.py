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

PYTHON_TEMPLATE = """\
import argparse
import logging

from pcapi.app import app
from pcapi.models import db


logger = logging.getLogger(__name__)

if __name__ == "__main__":
    app.app_context().push()

    parser = argparse.ArgumentParser()
    parser.add_argument("--not-dry", action="store_true")
    args = parser.parse_args()

    if args.not_dry:
        logger.info("Finished")
        db.session.commit()
    else:
        logger.info("Finished dry run, rollback")
        db.session.rollback()
"""


def main(namespace: str, with_sql: bool) -> None:
    path = SCRIPT_PATH / namespace
    if not os.path.exists(path):
        os.makedirs(path)

    if not os.path.exists(path / "main.py"):
        with open(path / "main.py", mode="w", encoding="utf8") as f:
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

    main(namespace=args.namespace, with_sql=args.with_sql)
