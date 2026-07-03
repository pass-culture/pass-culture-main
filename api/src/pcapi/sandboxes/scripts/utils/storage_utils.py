from pathlib import Path

import pcapi.sandboxes


def read_sandbox_mediation_asset(subcategory_id: str) -> bytes:
    picture_path = str(Path(pcapi.sandboxes.__path__[0]) / "thumbs" / "mediations" / subcategory_id) + ".jpg"
    with open(picture_path, mode="rb") as thumb_file:
        return thumb_file.read()
