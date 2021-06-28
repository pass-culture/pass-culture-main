from typing import Optional

from pcapi.models import ThingType

from . import subcategories


CAN_CREATE_FROM_ISBN_SUBCATEGORIES = (
    subcategories.LIVRE_PAPIER.id,
    subcategories.LIVRE_NUMERIQUE.id,
    subcategories.LIVRE_AUDIO_PHYSIQUE.id,
)


def can_create_from_isbn(subcategory_id: Optional[str], offer_type: Optional[str]) -> bool:
    # FIXME(rchaffal, 2021-07-08): remove once all offers and product have subcategoryId
    if subcategory_id:
        return subcategory_id in CAN_CREATE_FROM_ISBN_SUBCATEGORIES
    return offer_type == str(ThingType.LIVRE_EDITION)
