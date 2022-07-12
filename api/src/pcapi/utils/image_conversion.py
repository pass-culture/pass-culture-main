"""
Handle some basic image processing.
Those functions are basically wrapper around one or more functions
from the PIL library:

    https://pillow.readthedocs.io/
"""
from dataclasses import dataclass
import enum
import io
import math
from typing import TYPE_CHECKING

import PIL
from PIL import Image
from PIL import ImageOps
from pydantic import confloat


if TYPE_CHECKING:
    CropParam = float
else:
    CropParam = confloat(ge=0.0, le=1.0)


@dataclass
class CropParams:
    x_crop_percent: CropParam = 0.0
    y_crop_percent: CropParam = 0.0
    height_crop_percent: CropParam = 1.0
    width_crop_percent: CropParam = 1.0

    @classmethod
    def build(cls, **kwargs: CropParam | None) -> "CropParams":
        return cls(**{k: v for k, v in kwargs.items() if v})


@dataclass
class Coordinates:
    x: float
    y: float


class ImageRatio(enum.Enum):
    """Ratio is width / height"""

    PORTRAIT: float = 6 / 9
    LANDSCAPE: float = 3 / 2


class ImageRatioError(Exception):
    def __init__(self, expected: float, found: float):
        self.expected = expected
        self.found = found
        super().__init__(f"Bad image ratio: expected {expected}, found {found}")


MAX_THUMB_WIDTH = 750
CONVERSION_QUALITY = 90
DO_NOT_CROP = CropParams()

IMAGE_RATIO_PORTRAIT_DEFAULT = 6 / 9
IMAGE_RATIO_LANDSCAPE_DEFAULT = 3 / 2


def standardize_image(content: bytes, ratio: ImageRatio, crop_params: CropParams | None = None) -> bytes:
    """
    Standardization steps are:
        * transpose image
        * convert to RGB mode
        * crop image (if specified), see below
        * convert to jpeg using predefined values

    The cropping sets a new top left corner position, the crop_params
    are used to compute its new coordinates. The bottom right corner's
    coordinates will be computed using the top left's ones using width
    and max height (see constants below).

    crop_params values must be between 0.0 and 1.0.

    The first value will be used to set the top left corner's abscissa
    (X): width * <first_value> = new X value. The second value will be
    used to set the ordinate (Y). The third to set the height.

    Check PIL's documentation regarding the coordinate system to have a
    better understanding of how the cropping works:
        https://pillow.readthedocs.io/en/stable/handbook/concepts.html#coordinate-system
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
    resized_image = _resize_image(cropped_image, ratio)
    resized_image = _check_ratio(resized_image, ratio)

    return _post_process_image(resized_image)


def process_original_image(content: bytes) -> PIL.Image:
    """
    Process steps are:
        * transpose image
        * convert to RGB mode
        * shrink image if necessary (keep the original ratio)
        * convert to jpeg using predefined values
    """
    image = _pre_process_image(content)
    image = _shrink_image(image)
    return _post_process_image(image)


def _pre_process_image(content: bytes) -> PIL.Image:
    raw_image = PIL.Image.open(io.BytesIO(content))

    # Remove exif orientation so that it doesnt rotate after upload
    transposed_image = _transpose_image(raw_image)

    if transposed_image.mode == "RGBA":
        background = PIL.Image.new("RGB", transposed_image.size, (255, 255, 255))
        background.paste(transposed_image, mask=transposed_image.split()[3])
        transposed_image = background

    return transposed_image.convert("RGB")


def _post_process_image(image: PIL.Image) -> bytes:
    return _convert_to_jpeg(image)


def _transpose_image(raw_image: PIL.Image) -> PIL.Image:
    return ImageOps.exif_transpose(raw_image)


def _check_ratio(image: PIL.Image, ratio: ImageRatio) -> PIL.Image:
    image_ratio = image.width / image.height
    if not math.isclose(image_ratio, ratio.value, abs_tol=0.04):
        raise ImageRatioError(expected=ratio.value, found=image_ratio)
    return image


def _crop_image(
    x_crop_percent: CropParam,
    y_crop_percent: CropParam,
    height_crop_percent: CropParam,
    width_crop_percent: CropParam,
    image: Image,
) -> Image:
    """
    x_crop_percent and y_crop_percent will be used to compute new top left
    corner coordinates.

    height_crop_percent will be used to compute the bottom right corner's
    """
    if (x_crop_percent, y_crop_percent, height_crop_percent, width_crop_percent) == DO_NOT_CROP:
        return image

    width = image.size[0]
    height = image.size[1]

    top_left_corner = Coordinates(x=width * x_crop_percent, y=height * y_crop_percent)

    updated_height = height * height_crop_percent
    updated_width = width * width_crop_percent

    bottom_right_corner = Coordinates(
        x=min(top_left_corner.x + updated_width, width), y=min(top_left_corner.y + updated_height, height)
    )

    cropped_img = image.crop((top_left_corner.x, top_left_corner.y, bottom_right_corner.x, bottom_right_corner.y))

    return cropped_img


def _resize_image(image: Image, ratio: ImageRatio) -> Image:
    """
    Resize image, adapt ratio if image is too wide
    """
    if image.width <= MAX_THUMB_WIDTH:
        return image

    height_to_width_ratio = 1 / ratio.value
    new_height = int(MAX_THUMB_WIDTH * height_to_width_ratio)
    return image.resize([MAX_THUMB_WIDTH, new_height])


def _shrink_image(image: Image) -> Image:
    """
    Resize image, keep its original ratio
    """
    if image.width <= MAX_THUMB_WIDTH:
        return image

    reduce_factor = MAX_THUMB_WIDTH / image.width
    height = int(image.height * reduce_factor)
    return image.resize([MAX_THUMB_WIDTH, height])


def _convert_to_jpeg(image: Image) -> bytes:
    new_bytes = io.BytesIO()

    image.save(new_bytes, format="JPEG", quality=CONVERSION_QUALITY, optimize=True, progressive=True)

    return new_bytes.getvalue()
