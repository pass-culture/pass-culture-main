from typing import Optional

from . import subcategories


CAN_CREATE_FROM_ISBN_SUBCATEGORIES = (
    subcategories.LIVRE_PAPIER.id,
    subcategories.LIVRE_NUMERIQUE.id,
    subcategories.LIVRE_AUDIO_PHYSIQUE.id,
)


def can_create_from_isbn(subcategory_id: Optional[str]) -> bool:
    return subcategory_id in CAN_CREATE_FROM_ISBN_SUBCATEGORIES
