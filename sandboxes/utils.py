""" mock """
import os
from pathlib import Path

from models.pc_object import PcObject
from utils.human_ids import humanize
from utils.object_storage import store_public_object, STORAGE_DIR
from utils.string_processing import inflect_engine

mimes_by_folder = {
    "spreadsheets": "application/CSV",
    "thumbs": "image/jpeg",
    "zips": "application/zip"
}

def store_public_object_from_sandbox_assets(folder, obj, thumb_id, index=0):
    dir_path = Path(os.path.dirname(os.path.realpath(__file__)))
    collection_name = inflect_engine.plural(obj.__class__.__name__.lower())
    thumb_path = dir_path\
                 / folder / collection_name\
                 / str(thumb_id)

    """
    with open(thumb_path, mode='rb') as file:
        if folder == "thumbs":
            obj.save_thumb(file.read(), index)
        else:
            store_public_object(folder,
                                collection_name + '/' + humanize(obj.id),
                                file.read(),
                                mimes_by_folder[folder])
    """

    os.symlink(thumb_path, STORAGE_DIR / folder / collection_name / str(thumb_id))
    obj.thumbCount += 1

    PcObject.check_and_save(obj)
