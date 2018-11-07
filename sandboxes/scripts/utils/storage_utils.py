""" mock """
import os
from pathlib import Path

from models.db import db
from models.pc_object import PcObject
from utils.human_ids import humanize
from utils.object_storage import store_public_object
from utils.string_processing import get_collection_name

MIMES_BY_FOLDER = {
    "spreadsheets": "application/CSV",
    "thumbs": "image/jpeg",
    "zips": "application/zip"
}

def get_last_stored_id_of_model(model):
    ids = db.session.query(model.id).all()
    if ids:
        return max(ids)[0]
    return 0

def store_public_object_from_sandbox_assets(folder, obj, thumb_id, index=0):
    dir_path = Path(os.path.dirname(os.path.realpath(__file__)))
    collection_name = get_collection_name(obj)
    thumb_path = dir_path\
                 / '..' / '..' / folder / collection_name\
                 / str(thumb_id)

    with open(thumb_path, mode='rb') as file:
        if folder == "thumbs":
            obj.save_thumb(
                file.read(),
                index,
                dominant_color=b'\x00\x00\x00',
                no_convert=True,
                symlink_path=thumb_path
            )
        else:
            store_public_object(folder,
                                collection_name + '/' + humanize(obj.id),
                                file.read(),
                                MIMES_BY_FOLDER[folder],
                                symlink_path=thumb_path)

    PcObject.check_and_save(obj)
