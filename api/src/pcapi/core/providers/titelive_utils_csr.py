import csv
import json
import logging
import os.path
from pathlib import Path
import typing
from typing import TypedDict

from black import FileMode
from black import format_str

from pcapi import settings


logger = logging.getLogger(__name__)

DIRECTORY = Path(__file__).resolve().parent
FILENAME = "titelive_csr_to_gtl.py"
FILE_PATH = os.path.join(DIRECTORY, FILENAME)

HEADER_LINES_COUNT = 1
HEADER_DOCUMENTATION = f"""
# This source was generated 
# DO NOT EDIT !
# 
# Tite live will provide update to this file a few times per year, in order to regenerate the file:
# 
# 1. Save the new file in CSV format using tab separator:
#   - It should be exported totally without any edition
#   - You should have {HEADER_LINES_COUNT} header rows
#   - You can find CSRversGTL.xlsx exemple here: https://www.notion.so/passcultureapp/Mise-jour-de-titelive_things-synchronisation-version-2019-19-cddfb66ac8ee4e1bb935a40e7a8fa0e4 
# 2. Run the following command:
#     flask update_csr --file 'Correspondance CSRversGTL.csv'
#
"""

COLUMN_INDICES = {"CSR_ID": 0, "CSR_LABEL": 1, "GTL_ID": 6}


class Csr(TypedDict):
    label: str
    gtl_id: str


def _get_csrs_from_csv_reader(reader: typing.Any) -> dict[str, Csr]:
    csrs: dict[str, Csr] = {}
    reader_as_list = list(reader)
    rows = reversed(reader_as_list)
    for index, row in enumerate(rows):
        if index < len(reader_as_list) - HEADER_LINES_COUNT:
            gtl_id = str(row[COLUMN_INDICES["GTL_ID"]]).zfill(8)
            csr_label = row[COLUMN_INDICES["CSR_LABEL"]]
            csr_id = row[COLUMN_INDICES["CSR_ID"]]

            csrs[gtl_id] = {
                "label": csr_label,
                "csr_id": csr_id,
            }
    return csrs


def generate_titelive_csr_from_file(file: str) -> None:
    if not settings.IS_DEV:
        raise RuntimeError("Not DEV environment")

    import_str = "from .titelive_utils_csr import Csr"
    method_str = """
def get_csr(gtl_id: str) -> Csr | None:
    gtl_id_8_char = gtl_id.zfill(8)
    if gtl_id_8_char not in CSRS:
        return None
    return CSRS[gtl_id_8_char]
    """

    with open(file, newline="", encoding="utf-8") as csr_csv_file:
        csr_reader = csv.reader(csr_csv_file, delimiter="\t")
        csrs = _get_csrs_from_csv_reader(csr_reader)

        if not os.path.isdir(DIRECTORY):
            os.mkdir(DIRECTORY)

        with open(FILE_PATH, "w", encoding="utf-8") as csr_python_file:
            csr_file_content = format_str(
                f"""{HEADER_DOCUMENTATION}
{import_str}
{method_str}
CSRS: dict[str, Csr] = {json.dumps(csrs).encode('ascii').decode('unicode-escape')}
""".replace(
                    ": null", ": None"
                ),
                mode=FileMode(),
            )
            csr_python_file.write(csr_file_content)


def get_closest_csr(gtl_id: str) -> Csr | None:
    from .titelive_csr_to_gtl import get_csr

    gtl_id = gtl_id.zfill(8)
    csr_level_1 = get_csr(f"{gtl_id[:2]}000000")
    csr_level_2 = get_csr(f"{gtl_id[:4]}0000")
    csr_level_3 = get_csr(f"{gtl_id[:6]}00")
    csr_level_4 = get_csr(gtl_id)
    csr = csr_level_4 or csr_level_3 or csr_level_2 or csr_level_1
    if csr is None:
        logger.warning("GTL %s has no matching csr", gtl_id)
    return csr
