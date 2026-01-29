from pathlib import Path

import pcapi.sandboxes
from pcapi.connectors.thumb_storage import create_thumb
from pcapi.core.object_storage import store_public_object
from pcapi.core.offers.models import Mediation
from pcapi.utils.human_ids import humanize


def store_public_object_from_sandbox_assets(folder: str, model: Mediation, subcategory_id: str) -> Mediation:
    mimes_by_folder = {"spreadsheets": "application/CSV", "thumbs": "image/jpeg", "zips": "application/zip"}
    thumb_id = humanize(model.id)
    assert thumb_id  # helps mypy
    thumbs_folder_path = Path(pcapi.sandboxes.__path__[0]) / "thumbs"
    picture_path = str(thumbs_folder_path / "mediations" / subcategory_id) + ".jpg"
    with open(picture_path, mode="rb") as thumb_file:
        if folder == "thumbs":
            create_thumb(model, thumb_file.read(), keep_ratio=True)
        else:
            store_public_object(
                folder,
                model.thumb_path_component + "/" + thumb_id,
                thumb_file.read(),
                mimes_by_folder[folder],
            )

    return model
