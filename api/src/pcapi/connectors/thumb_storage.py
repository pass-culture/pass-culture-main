from pcapi import settings
from pcapi.core import object_storage
from pcapi.core.offers import validation as offers_validation
from pcapi.models.has_thumb_mixin import HasThumbMixin
from pcapi.utils.image_conversion import CropParams
from pcapi.utils.image_conversion import ImageRatio
from pcapi.utils.image_conversion import process_original_image
from pcapi.utils.image_conversion import standardize_image


def create_thumb(
    model_with_thumb: HasThumbMixin,
    image_as_bytes: bytes,
    *,
    storage_id_suffix_str: str = "",
    crop_params: CropParams | None = None,
    ratio: ImageRatio = ImageRatio.PORTRAIT,
    keep_ratio: bool = False,
    object_id: str | None = None,
) -> None:
    offers_validation.check_image(image_as_bytes, min_height=None, min_width=None)
    if keep_ratio:
        image_as_bytes = process_original_image(image_as_bytes)
    else:
        image_as_bytes = standardize_image(image_as_bytes, ratio=ratio, crop_params=crop_params)
    if object_id is None:
        model_with_thumb.thumbCount += 1
    object_storage.store_public_object(
        folder=settings.THUMBS_FOLDER_NAME,
        object_id=model_with_thumb.get_thumb_storage_id(storage_id_suffix_str) if object_id is None else object_id,
        blob=image_as_bytes,
        content_type="image/jpeg",
    )


def remove_thumb(
    model_with_thumb: HasThumbMixin,
    storage_id_suffix: str,
    ignore_thumb_count: bool = False,
) -> None:
    object_storage.delete_public_object(
        folder="thumbs",
        object_id=model_with_thumb.get_thumb_storage_id(storage_id_suffix, ignore_thumb_count),
    )
