from io import BytesIO

from PIL import Image

from pcapi import settings
from pcapi.core import search
from pcapi.core.object_storage import delete_public_object
from pcapi.core.object_storage import store_public_object
from pcapi.core.offers.models import Offer
from pcapi.utils import requests
from pcapi.utils.image_conversion import _convert_to_jpeg


LOCAL_IMAGE_PATH = "pastille.png"
OFFERS_ID: list[int] = [
]


def load_local_image():
    image = Image.open(LOCAL_IMAGE_PATH)
    return image.resize((200, 200))


def load_offer_image(offer: Offer):
    response = requests.get(offer.image.url)
    if response.ok:
        return Image.open(BytesIO(response.content))
    return None


def save_image(offer: Offer, image: Image):
    delete_public_object(
        folder=settings.THUMBS_FOLDER_NAME,
        object_id=offer.activeMediation.get_thumb_storage_id(),
    )
    store_public_object(
        folder=settings.THUMBS_FOLDER_NAME,
        object_id=offer.activeMediation.get_thumb_storage_id(),
        blob=_convert_to_jpeg(image),
        content_type="image/jpeg",
    )


def main():
    local_image = load_local_image()
    local_mask = local_image.convert("RGBA")
    offers = Offer.query.filter(Offer.id.in_(OFFERS_ID))
    for offer in offers:
        if not offer.image:
            print("no image", offer.id)
            continue
        if not offer.image.url:
            print("no image url", offer.id)
            continue
        offer_image = load_offer_image(offer)
        if not offer_image:
            print("could not download image", offer.id)
            continue
        if offer_image.size[0] < 400:
            print("image too small", offer.id)
            continue

        offset_width = max((offer_image.size[0]  - 220), 20)
        offset_height = max((offer_image.size[1]  - 220), 20)
        try:
            offer_image.paste(local_image, (offset_width, offset_height), local_mask)
        except:
            print("could not modify image for ", offer.id)
            continue

        try:
            save_image(offer=offer, image=offer_image)
        except:
            print("could not save image for", offer.id)

    search.async_index_offer_ids(
        OFFERS_ID,
        reason=search.IndexationReason.MEDIATION_CREATION,
    )


main()
