import csv
import json
import os.path
from pathlib import Path
import typing
from typing import TypedDict

import black

from pcapi import settings


DIRECTORY = Path(__file__).resolve().parent
FILENAME = "titelive_gtl.py"
FILE_PATH = DIRECTORY / FILENAME

HEADER_LINES_COUNT = 2
HEADER_DOCUMENTATION = f"""
# pylint: skip-file
# This source was generated 
# DO NOT EDIT !
# 
# Tite live will provide an updated list of GTLs in an Excel file, a few times per year. In order to regenerate our Python file:
# 
# 1. Export the new Excel file to a CSV file with tab separators:
#   - It should be exported totally without any edition
#   - You should have {HEADER_LINES_COUNT} header rows
#   - As an example, you can check GTL_2023.xlsx here: https://www.notion.so/passcultureapp/Mise-jour-de-titelive_things-synchronisation-version-2019-19-cddfb66ac8ee4e1bb935a40e7a8fa0e4 
# 2. Run the following command:
#     flask update_gtl --file GTL_2023.csv
#
# Intermediate levels:
# - When value of level_02_code, level_03_code and level_04_code, level_02_code and level_03_code and level_04_code is "00", it means it is an intermediate GTL,
# - When you have an intermediate GTL, level_02_label, level_03_label and level_04_label may be None.
# 
"""

COLUMN_INDICES = {
    "LEVEL_01_LABEL": 1,
    "LEVEL_02_LABEL": 3,
    "LEVEL_03_LABEL": 5,
    "LEVEL_04_LABEL": 7,
    "GTL_ID": 9,
    "GTL_LABEL": 10,
}


class Gtl(TypedDict):
    label: str
    level_01_code: str
    level_01_label: str
    level_02_code: str
    level_02_label: str | None
    level_03_code: str
    level_03_label: str | None
    level_04_code: str
    level_04_label: str | None


def _get_gtls_from_csv_reader(reader: typing.Any) -> dict[str, Gtl]:
    gtls: dict[str, Gtl] = {}
    for index, row in enumerate(reader):
        if index >= HEADER_LINES_COUNT:
            level_01_label = row[COLUMN_INDICES["LEVEL_01_LABEL"]]
            level_02_label = row[COLUMN_INDICES["LEVEL_02_LABEL"]]
            level_03_label = row[COLUMN_INDICES["LEVEL_03_LABEL"]]
            level_04_label = row[COLUMN_INDICES["LEVEL_04_LABEL"]]
            gtl_id = str(row[COLUMN_INDICES["GTL_ID"]]).zfill(8)
            gtl_label = row[COLUMN_INDICES["GTL_LABEL"]]

            if gtl_id and gtl_label:
                gtls[gtl_id] = {
                    "label": gtl_label,
                    "level_01_code": gtl_id[:2],
                    "level_01_label": level_01_label,
                    "level_02_code": gtl_id[2:4],
                    "level_02_label": level_02_label or None,
                    "level_03_code": gtl_id[4:6],
                    "level_03_label": level_03_label or None,
                    "level_04_code": gtl_id[6:8],
                    "level_04_label": level_04_label or None,
                }
    return gtls


def generate_titelive_gtl_from_file(file: str) -> None:
    if not settings.IS_DEV:
        raise RuntimeError("Not DEV environment")

    import_str = "from .titelive_utils import Gtl"
    method_str = """
def get_gtl(gtl_id: str) -> Gtl | None:
    gtl_id_8chars = gtl_id.zfill(8)
    return GTLS.get(gtl_id_8chars)
    """

    with open(file, newline="", encoding="utf-8") as gtl_csv_file:
        gtl_reader = csv.reader(gtl_csv_file, delimiter="\t")
        gtls = _get_gtls_from_csv_reader(gtl_reader)

        if not os.path.isdir(DIRECTORY):
            os.mkdir(DIRECTORY)

        with open(FILE_PATH, "w", encoding="utf-8") as gtl_python_file:
            gtl_file_content = black.format_str(
                f"""{HEADER_DOCUMENTATION}
{import_str}
{method_str}
GTLS: dict[str, Gtl] = {json.dumps(gtls).encode('ascii').decode('unicode-escape')}
""".replace(
                    ": null", ": None"  # To replace all null (JSON) with None (Python)
                ),
                mode=black.FileMode(),
            )
            gtl_python_file.write(gtl_file_content)
