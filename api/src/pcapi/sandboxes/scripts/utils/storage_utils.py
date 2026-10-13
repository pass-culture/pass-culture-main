from pathlib import Path

import pcapi.sandboxes
from pcapi import settings
from pcapi.core import object_storage
from pcapi.core.discoveries import models as discoveries_models
from pcapi.core.educational import models as educational_models
from pcapi.utils.image_conversion import DO_NOT_CROP


def read_sandbox_mediation_asset(subcategory_id: str) -> bytes:
    picture_path = str(Path(pcapi.sandboxes.__path__[0]) / "thumbs" / "mediations" / subcategory_id) + ".jpg"
    with open(picture_path, mode="rb") as thumb_file:
        return thumb_file.read()


def add_image_to_work(work: discoveries_models.Work, subcategory_id: str) -> None:
    if work.id is None:
        raise ValueError("The work must be persisted before adding its image")
    folder = "thumbs/works"
    object_id = f"{work.id}.jpg"
    object_storage.store_public_object(
        folder=folder,
        object_id=object_id,
        blob=read_sandbox_mediation_asset(subcategory_id),
        content_type="image/jpeg",
    )
    work.visual_url = f"{settings.OBJECT_STORAGE_URL.rstrip('/')}/{folder}/{object_id}"


def add_image_to_offer(
    offer: educational_models.CollectiveOffer | educational_models.CollectiveOfferTemplate,
    image_name: str,
    alternative_text: str = "Image de la conférence gesticulée",
) -> None:
    with open(
        f"./src/pcapi/sandboxes/thumbs/collectif/{image_name}",
        mode="rb",
    ) as file:
        offer.set_image(
            image=file.read(),
            credit="CC-BY-SA WIKIPEDIA",
            crop_params=DO_NOT_CROP,
            alternative_text=alternative_text,
        )
