import shutil

from pcapi import settings


def reset_bucket() -> None:
    try:
        shutil.rmtree(settings.LOCAL_STORAGE_DIR)
    except FileNotFoundError:
        pass
