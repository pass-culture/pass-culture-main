""" storage utils """
import os
from pathlib import Path

from models.pc_object import PcObject
from utils.human_ids import humanize
from utils.object_storage import store_public_object
from utils.string_processing import get_model_plural_name

MIMES_BY_FOLDER = {
    "spreadsheets": "application/CSV",
    "thumbs": "image/jpeg",
    "zips": "application/zip"
}

def store_public_object_from_sandbox_assets(folder, obj, thumb_id, index=0):
    dir_path = Path(os.path.dirname(os.path.realpath(__file__)))
    plural_model_name = get_model_plural_name(obj)
    thumb_path = dir_path\
                 / '..' / '..' / folder / plural_model_name\
                 / str(thumb_id)

    with open(thumb_path, mode='rb') as thumb_file:
        if folder == "thumbs":
            obj.save_thumb(
                thumb_file.read(),
                index,
                dominant_color=b'\x00\x00\x00',
                convert=False,
                symlink_path=thumb_path
            )
        else:
            store_public_object(folder,
                                plural_model_name + '/' + humanize(obj.id),
                                thumb_file.read(),
                                MIMES_BY_FOLDER[folder],
                                symlink_path=thumb_path)

    PcObject.save(obj)
