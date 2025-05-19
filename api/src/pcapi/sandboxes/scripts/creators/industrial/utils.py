import itertools
import pathlib
from decimal import Decimal

import pcapi.core.offers.models as offers_models
import pcapi.sandboxes.thumbs.generic_pictures as generic_pictures_thumbs
from pcapi.connectors import thumb_storage


def get_occurrence_short_name_or_none(concatened_names_with_a_date: str) -> str | None:
    splitted_names = concatened_names_with_a_date.split(" / ")

    if len(splitted_names) > 0:
        return splitted_names[0]

    return None


def get_occurrence_short_name(concatened_names_with_a_date: str) -> str:
    short_name = get_occurrence_short_name_or_none(concatened_names_with_a_date)
    if not short_name:
        raise ValueError("Missing value from short name, please verify how shortname is build")

    return short_name


def get_price_by_short_name(occurrence_short_name: str | None = None) -> Decimal:
    if occurrence_short_name is None:
        return Decimal(0)

    return Decimal(str(sum(map(ord, occurrence_short_name)) % 50))


def create_products_thumb(products: list[offers_models.Product]) -> None:
    image_dir = pathlib.Path(generic_pictures_thumbs.__path__[0])
    image_paths = image_dir.iterdir()

    for product, image_path in zip(products, itertools.cycle(image_paths)):
        thumb_storage.create_thumb(product, image_path.read_bytes(), keep_ratio=True)
