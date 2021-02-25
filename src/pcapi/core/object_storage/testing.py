import os
from pathlib import Path
import shutil


TESTS_STORAGE_DIR = (
    Path(os.path.dirname(os.path.realpath(__file__))) / ".." / ".." / "static" / "object_store_data" / "tests"
)


def reset_bucket() -> None:
    try:
        shutil.rmtree(TESTS_STORAGE_DIR)
    except FileNotFoundError:
        pass
