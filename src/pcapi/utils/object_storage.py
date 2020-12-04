from datetime import datetime
import os
from pathlib import Path
from pathlib import PurePath

import swiftclient

from pcapi import settings
from pcapi.models.db import Model
from pcapi.utils.human_ids import humanize
from pcapi.utils.inflect_engine import inflect_engine


def swift_con():
    return swiftclient.Connection(
        user=settings.SWIFT_USER,
        key=settings.SWIFT_KEY,
        authurl=settings.SWIFT_AUTH_URL,
        os_options={"region_name": settings.SWIFT_REGION_NAME},
        tenant_name=settings.SWIFT_TENANT_NAME,
        auth_version="3",
    )


STORAGE_DIR = Path(os.path.dirname(os.path.realpath(__file__))) / ".." / "static" / "object_store_data"


def local_dir(bucket, object_id):
    if "/" in object_id:
        idFolders = PurePath(object_id).parent
    else:
        idFolders = ""
    return STORAGE_DIR / bucket / idFolders


def local_path(bucket, object_id):
    return local_dir(bucket, object_id) / PurePath(object_id).name


def store_public_object(bucket, object_id, blob, content_type, symlink_path=None):
    if settings.IS_DEV:
        os.makedirs(local_dir(bucket, object_id), exist_ok=True)

        file_local_path = local_path(bucket, object_id)

        new_type_file = open(str(file_local_path) + ".type", "w")
        new_type_file.write(content_type)

        if symlink_path and not os.path.isfile(file_local_path) and not os.path.islink(file_local_path):
            os.symlink(symlink_path, file_local_path)
            return

        new_file = open(file_local_path, "wb")
        new_file.write(blob)
    else:
        container_name = settings.SWIFT_BUCKET_NAME
        storage_path = "thumbs/" + object_id
        swift_con().put_object(container_name, storage_path, contents=blob, content_type=content_type)


def delete_public_object(bucket, object_id):
    lpath = local_path(bucket, object_id)
    if os.path.isfile(lpath):
        os.remove(lpath)


def get_public_object_date(bucket, object_id):
    lpath = local_path(bucket, object_id)
    if not os.path.isfile(lpath):
        return None
    return datetime.fromtimestamp(os.path.getmtime(lpath))


def build_thumb_path(pc_object: Model, index: int) -> str:
    return (
        inflect_engine.plural(pc_object.__class__.__tablename__.lower())
        + "/"
        + humanize(pc_object.id)
        + (("_" + str(index)) if index > 0 else "")
    )
