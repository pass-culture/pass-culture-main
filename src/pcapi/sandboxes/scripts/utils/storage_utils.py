import os

from pcapi.connectors.thumb_storage import create_thumb
from pcapi.core.object_storage import store_public_object
from pcapi.utils.human_ids import humanize


def store_public_object_from_sandbox_assets(folder, model, offer_type):
    mimes_by_folder = {"spreadsheets": "application/CSV", "thumbs": "image/jpeg", "zips": "application/zip"}
    thumb_id = humanize(model.id)
    thumb_path = (
        f"{os.path.dirname(os.path.realpath(__file__))}/../../{folder}/{model.thumb_path_component}/{str(offer_type)}"
    )

    with open(thumb_path, mode="rb") as thumb_file:
        if folder == "thumbs":
            create_thumb(model, thumb_file.read(), 0)
            model.thumbCount += 1
        else:
            store_public_object(
                folder,
                model.thumb_path_component + "/" + thumb_id,
                thumb_file.read(),
                mimes_by_folder[folder],
            )

    return model
