"""
Handle some basic image processing.
Those functions are basically wrapper around one or more functions
from the PIL library:

    https://pillow.readthedocs.io/
"""

import enum
import io
import math
import typing
from dataclasses import dataclass
from typing import TYPE_CHECKING

import PIL.Image
import pydantic
from PIL import ImageFile
from PIL import ImageOps
from PIL import UnidentifiedImageError
from pydantic.v1 import confloat


if TYPE_CHECKING:
    CropParam = float
else:
    CropParam = confloat(ge=0.0, le=1.0)

ImageFile.LOAD_TRUNCATED_IMAGES = True


@dataclass
class CropParams:
    x_crop_percent: CropParam = 0.0
    y_crop_percent: CropParam = 0.0
    height_crop_percent: CropParam = 1.0
    width_crop_percent: CropParam = 1.0

    @classmethod
    def build(cls, **kwargs: CropParam | None) -> typing.Self:
        return cls(**{k: v for k, v in kwargs.items() if v})


CropPercent = typing.Annotated[float, pydantic.Field(ge=0.0, le=1.0)]


@dataclass
class CropParamsV2:
    x_crop_percent: CropPercent = 0.0
    y_crop_percent: CropPercent = 0.0
    height_crop_percent: CropPercent = 1.0
    width_crop_percent: CropPercent = 1.0

    @classmethod
    def build(cls, **kwargs: CropParam | None) -> typing.Self:
        return cls(**{k: v for k, v in kwargs.items() if v})


@dataclass
class Coordinates:
    x: int
    y: int


class ImageRatio(enum.Enum):
    """Ratio is width / height"""

    PORTRAIT = 2.0 / 3.0
    LANDSCAPE = 3.0 / 2.0
    SQUARE = 1.0


class ImageRatioError(Exception):
    def __init__(self, expected: float, found: float):
        self.expected = expected
        self.found = found
        super().__init__(f"Bad image ratio: expected {expected}, found {found}")


MAX_THUMB_WIDTH = 750
MINI_THUMB_WIDTH = 72
CONVERSION_QUALITY = 90
DO_NOT_CROP = CropParams()


def standardize_image(content: bytes, ratio: ImageRatio, crop_params: CropParams | None = None) -> bytes:
    """
    Standardization steps are:
        * transpose image
        * convert to RGB mode
        * resize image in three stages:
            1. Crop original image if needed (crop_params)
            2. Shrink the image to max thumb width: 750px
            3. Check if the image ratio is correct
        * convert to jpeg using predefined values
    """
    preprocessed_image = _pre_process_image(content)

    crop_params = crop_params or DO_NOT_CROP
    cropped_image = _crop_image(
        crop_params.x_crop_percent,
        crop_params.y_crop_percent,
        crop_params.height_crop_percent,
        crop_params.width_crop_percent,
        preprocessed_image,
    )
    shrunk_image = _shrink_image(cropped_image)
    validated_image = _check_ratio(shrunk_image, ratio)

    return _post_process_image(validated_image)


def process_original_image(content: bytes, resize: bool = True) -> bytes:
    """
    Process steps are:
        * transpose image
        * convert to RGB mode
        * shrink image if necessary (keep the original ratio)
        * convert to jpeg using predefined values
    """
    image = _pre_process_image(content)
    if resize:
        image = _shrink_image(image)
    return _post_process_image(image)


def _pre_process_image(content: bytes) -> PIL.Image.Image:
    raw_image = PIL.Image.open(io.BytesIO(content))

    # Remove exif orientation so that it doesn't rotate after upload
    try:
        transposed_image = ImageOps.exif_transpose(raw_image)
    except (SyntaxError, ZeroDivisionError) as exc:
        # PIL may raise `SyntaxError("not a TIFF file [...]")` or a
        # similar message, depending on the expected type of file. In
        # that case, re-reraise as a more specific, PIL-related error.
        # It can also raise ZeroDivisionError in some cases.
        raise UnidentifiedImageError() from exc
    assert transposed_image is not None  # helps mypy

    if transposed_image.mode == "RGBA":
        background = PIL.Image.new("RGB", transposed_image.size, (255, 255, 255))
        background.paste(transposed_image, mask=transposed_image.split()[3])
        transposed_image = background

    return transposed_image.convert("RGB")


def _post_process_image(image: PIL.Image.Image) -> bytes:
    return _convert_to_jpeg(image)


def _check_ratio(image: PIL.Image.Image, ratio: ImageRatio) -> PIL.Image.Image:
    image_ratio = image.width / image.height
    if not math.isclose(image_ratio, ratio.value, abs_tol=0.04):
        raise ImageRatioError(expected=ratio.value, found=image_ratio)
    return image


def _crop_image(
    x_crop_percent: CropParam,
    y_crop_percent: CropParam,
    height_crop_percent: CropParam,
    width_crop_percent: CropParam,
    image: PIL.Image.Image,
) -> PIL.Image.Image:
    """
    Crop a rectangular region from the image using percentage-based parameters.

    All crop_params are floats between 0.0 and 1.0 :
        - x_crop_percent: horizontal offset of the crop box's top-left corner
        - y_crop_percent: vertical offset of the crop box's top-left corner
        - width_crop_percent: width of the crop box
        - height_crop_percent: height of the crop box

    See: https://pillow.readthedocs.io/en/stable/handbook/concepts.html#coordinate-system
    """
    if (x_crop_percent, y_crop_percent, height_crop_percent, width_crop_percent) == DO_NOT_CROP:
        return image

    width = image.size[0]
    height = image.size[1]

    top_left_corner = Coordinates(
        x=int(width * x_crop_percent),
        y=int(height * y_crop_percent),
    )

    updated_height = int(height * height_crop_percent)
    updated_width = int(width * width_crop_percent)

    bottom_right_corner = Coordinates(
        x=min(top_left_corner.x + updated_width, width),
        y=min(top_left_corner.y + updated_height, height),
    )

    cropped_img = image.crop((top_left_corner.x, top_left_corner.y, bottom_right_corner.x, bottom_right_corner.y))

    return cropped_img


def _shrink_image(image: PIL.Image.Image, max_width: int = MAX_THUMB_WIDTH) -> PIL.Image.Image:
    """
    Resize image, keep its original ratio
    """
    if image.width <= max_width:
        return image

    reduce_factor = max_width / image.width
    height = int(image.height * reduce_factor)
    return image.resize((max_width, height))


def _convert_to_jpeg(image: PIL.Image.Image) -> bytes:
    new_bytes = io.BytesIO()

    image.save(new_bytes, format="JPEG", quality=CONVERSION_QUALITY, optimize=True, progressive=True)

    return new_bytes.getvalue()


def get_crop_params(width: int, height: int, expected_ratio: ImageRatio) -> CropParams:
    ratio = width / height

    x_crop_percent = 0.0
    y_crop_percent = 0.0
    width_crop_percentage = 1.0
    height_crop_percentage = 1.0

    if ratio < expected_ratio.value:  # height is too big
        new_height = width / expected_ratio.value
        height_crop_percentage = new_height / height
        y_crop_start = (height - new_height) / 2
        y_crop_percent = y_crop_start / height

    else:  # width is too big
        new_width = height * expected_ratio.value
        width_crop_percentage = new_width / width
        x_crop_start = (width - new_width) / 2
        x_crop_percent = x_crop_start / width

    return CropParams(x_crop_percent, y_crop_percent, height_crop_percentage, width_crop_percentage)
