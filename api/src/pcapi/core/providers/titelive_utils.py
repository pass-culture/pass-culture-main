import csv
import json
import os.path
import typing
from pathlib import Path
from typing import TypedDict


# Black is only used for the `flask update_gtl` command, which is only
# used on development environments. We don't need (and thus don't
# install) Black on production Docker image.
try:
    import black

    HAS_BLACK = True
except ImportError:
    HAS_BLACK = False

from pcapi import settings


DIRECTORY = Path(__file__).resolve().parent
FILENAME = "titelive_gtl.py"
FILE_PATH = DIRECTORY / FILENAME

HEADER_DOCUMENTATION = """
# ruff: noqa
# This source was generated
# DO NOT EDIT !
#
# Tite live will provide update to this file a few times per year, in order to regenerate the file:
#
# 1. Save the new file in CSV format using tab separator:
#     the format seems to change every time, so profread the stript befor ani new import.
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


def rzfill(string: str, length: int) -> str:
    return string + "".zfill(length - len(string))


def _get_gtl_level_code(gtl: str, level: int) -> str:
    return rzfill(gtl[: level * 2], len(gtl))


def _get_gtl_short_level_code(gtl: str, level: int) -> str:
    return gtl[(level - 1) * 2 : level * 2]


def _get_gtls_from_csv_reader(reader: typing.Any) -> dict[str, Gtl]:
    gtls: dict[str, Gtl] = {}
    data: dict[str, str] = {}

    for row in reader:
        data[row[0]] = row[1]

    for gtl in data:
        gtl_id = gtl.zfill(8)
        gtls[gtl_id] = {
            "label": data[gtl_id],
            "level_01_code": _get_gtl_short_level_code(gtl_id, 1),
            "level_01_label": data[_get_gtl_level_code(gtl_id, 1)],
            "level_02_code": _get_gtl_short_level_code(gtl_id, 2),
            "level_02_label": (
                data[_get_gtl_level_code(gtl_id, 2)] if _get_gtl_short_level_code(gtl_id, 2) != "00" else None
            ),
            "level_03_code": _get_gtl_short_level_code(gtl_id, 3),
            "level_03_label": (
                data[_get_gtl_level_code(gtl_id, 3)] if _get_gtl_short_level_code(gtl_id, 3) != "00" else None
            ),
            "level_04_code": _get_gtl_short_level_code(gtl_id, 4),
            "level_04_label": (
                data[_get_gtl_level_code(gtl_id, 4)] if _get_gtl_short_level_code(gtl_id, 4) != "00" else None
            ),
        }
    return gtls


def generate_titelive_gtl_from_file(file: str) -> None:
    if not settings.TITELIVE_GENERATE_FROM_FILE_IN_DEV:
        raise RuntimeError("Not DEV environment")
    assert HAS_BLACK

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
GTLS: dict[str, Gtl] = {json.dumps(gtls).encode("ascii").decode("unicode-escape")}
""".replace(
                    ": null",
                    ": None",  # To replace all null (JSON) with None (Python)
                ),
                mode=black.FileMode(),
            )
            gtl_python_file.write(gtl_file_content)
