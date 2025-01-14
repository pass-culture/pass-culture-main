from io import BytesIO
from pathlib import Path

from PIL import Image

from pcapi import settings
from pcapi.core.criteria.models import Criterion
from pcapi.core.object_storage import get_public_object
from pcapi.core.offers.api import create_mediation
from pcapi.core.offers.models import Offer
from pcapi.models import db
from pcapi.utils.image_conversion import _convert_to_jpeg


LOCAL_IMAGE_PATH = "pastille.png"
OFFERS_TAG = "vismavie_tfmac25"


def load_local_image(image_path: str) -> Image.Image:
    local_image_abs_path = Path(__file__).parent.resolve() / image_path
    image = Image.open(local_image_abs_path)
    return image.resize((200, 200))


def load_offer_image(offer: Offer) -> Image.Image | None:
    if offer.activeMediation is not None:
        try:
            image_bytes = get_public_object(
                folder=settings.THUMBS_FOLDER_NAME,
                object_id=offer.activeMediation.get_thumb_storage_id(),
            )
        except:  # pylint: disable=bare-except
            print("image not found", offer.id)
            return None
        if image_bytes:
            # GCP backend could return multiple images (they should be all the same)
            return Image.open(BytesIO(image_bytes[0]))
    return None


def save_image(offer: Offer, image: Image.Image) -> None:
    # create_mediation delete the old mediation
    if offer.activeMediation is not None:  # helps mypy
        create_mediation(
            offer=offer,
            user=offer.activeMediation.author,
            credit=offer.activeMediation.credit,
            image_as_bytes=_convert_to_jpeg(image),
            keep_ratio=True,
        )


def get_offers_from_tag(tag: str) -> list[Offer]:
    return Offer.query.join(Offer.criteria).filter(Criterion.name == tag).all()


def main() -> None:
    local_image = load_local_image(LOCAL_IMAGE_PATH)
    local_mask = local_image.convert("RGBA")
    offers = get_offers_from_tag(OFFERS_TAG)
    for offer in offers:
        if not offer.image:
            print("no image", offer.id)
            db.session.rollback()
            continue
        if not offer.image.url:
            print("no image url", offer.id)
            db.session.rollback()
            continue
        offer_image = load_offer_image(offer)
        if not offer_image:
            print("could not download image", offer.id)
            db.session.rollback()
            continue
        if offer_image.size[0] < 400:
            print("image too small", offer.id)
            db.session.rollback()
            continue

        offset_width = max((offer_image.size[0] - 220), 20)
        offset_height = max((offer_image.size[1] - 220), 20)
        try:
            offer_image.paste(local_image, (offset_width, offset_height), local_mask)
        except:  # pylint: disable=bare-except
            print("could not modify image for ", offer.id)
            db.session.rollback()
            continue
        try:
            save_image(offer=offer, image=offer_image)
        except:  # pylint: disable=bare-except
            print("could not save image for ", offer.id)
            db.session.rollback()
        db.session.commit()


if __name__ == "__main__":
    from pcapi.flask_app import app

    app.app_context().push()
    main()
