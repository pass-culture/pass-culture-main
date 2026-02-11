from pcapi import settings
from pcapi.core import object_storage
from pcapi.core.offers import validation as offers_validation
from pcapi.models.has_thumb_mixin import HasThumbMixin
from pcapi.utils.image_conversion import MAX_THUMB_WIDTH
from pcapi.utils.image_conversion import CropParams
from pcapi.utils.image_conversion import ImageRatio
from pcapi.utils.image_conversion import process_original_image
from pcapi.utils.image_conversion import standardize_image


def create_thumb(
    image_as_bytes: bytes,
    *,
    model_with_thumb: HasThumbMixin | None = None,
    storage_id_suffix_str: str = "",
    crop_params: CropParams | None = None,
    ratio: ImageRatio = ImageRatio.PORTRAIT,
    keep_ratio: bool = False,
    folder: str = settings.THUMBS_FOLDER_NAME,
    object_id: str | None = None,
    max_width: int = MAX_THUMB_WIDTH,
) -> None:
    if model_with_thumb is None and object_id is None:
        raise ValueError("model_with_thumb or object_id must be provided")

    if object_id is None:
        assert model_with_thumb is not None
        model_with_thumb.thumbCount += 1
        object_id = model_with_thumb.get_thumb_storage_id(storage_id_suffix_str)

    offers_validation.check_image(image_as_bytes, min_height=None, min_width=None)
    if keep_ratio:
        image_as_bytes = process_original_image(image_as_bytes, resize=True)
    else:
        image_as_bytes = standardize_image(
            image_as_bytes,
            ratio=ratio,
            crop_params=crop_params,
            max_width=max_width,
        )

    object_storage.store_public_object(
        folder=folder,
        object_id=object_id,
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
