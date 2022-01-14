import os
import pathlib
import shutil

from pcapi import settings


def reset_bucket() -> None:
    try:
        shutil.rmtree(settings.LOCAL_STORAGE_DIR)
    except FileNotFoundError:
        pass


def recursive_listdir(directory_path: pathlib.Path) -> list[str]:
    """This function will return all files in the given directory and its subdirectory"""
    return [os.path.join(dirpath, f) for dirpath, _dirname, filename in os.walk(directory_path) for f in filename]
