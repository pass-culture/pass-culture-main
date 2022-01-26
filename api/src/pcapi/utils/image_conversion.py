"""
Handle some basic image processing.
Those functions are basically wrapper around one or more functions
from the PIL library:

    https://pillow.readthedocs.io/
"""
from dataclasses import dataclass
import io
from typing import Optional

import PIL
from PIL import Image
from PIL import ImageOps
from pydantic import confloat


MAX_THUMB_WIDTH = 750
CONVERSION_QUALITY = 90
DO_NOT_CROP = (0, 0, 1)
IMAGE_RATIO_V2 = 6 / 9


CropParam = confloat(ge=0.0, le=1.0)
CropParams = tuple[CropParam, CropParam, CropParam]  # type: ignore


@dataclass
class Coordinates:
    x: float
    y: float


def standardize_image(image: bytes, crop_params: Optional[CropParams] = None) -> bytes:
    """
    Standardization steps are:
        * transpose image
        * convert to RGB mode
        * crop image (if specified), see below
        * convert to jpeg using predefined values

    The cropping sets a new top left corner position, the crop_params
    are used to compute its new coordinates. The bottom right corner's
    coordinates will be computed using the top left's ones using some
    predifined ratio and max height (see constants below).

    crop_params is a three-float tuple. All values must be between 0.0
    and 1.0.

    The first value will be used to set the top left corner's abscissa
    (X): width * <first_value> = new X value. The second value will be
    used to set the ordinate (Y). The third to set the height.

    Check PIL's documentation regarding the coordinate system to have a
    better understanding of how the cropping works:
        https://pillow.readthedocs.io/en/stable/handbook/concepts.html#coordinate-system
    """
    crop_params = crop_params or DO_NOT_CROP
    raw_image = PIL.Image.open(io.BytesIO(image))

    # Remove exif orientation so that it doesnt rotate after upload
    transposed_image = _transpose_image(raw_image)

    if transposed_image.mode == "RGBA":
        background = PIL.Image.new("RGB", transposed_image.size, (255, 255, 255))
        background.paste(transposed_image, mask=transposed_image.split()[3])
        transposed_image = background
    transposed_image = transposed_image.convert("RGB")

    x_crop_percent, y_crop_percent, height_crop_percent = crop_params
    cropped_image = _crop_image(x_crop_percent, y_crop_percent, height_crop_percent, transposed_image)
    resized_image = _resize_image(cropped_image)
    standard_image = _convert_to_jpeg(resized_image)
    return standard_image


def _transpose_image(raw_image):
    return ImageOps.exif_transpose(raw_image)


def _crop_image(
    x_crop_percent: CropParam, y_crop_percent: CropParam, height_crop_percent: CropParam, image: Image
) -> Image:
    """
    x_crop_percent and y_crop_percent will be used to compute new top left
    corner coordinates.

    height_crop_percent will be used to compute the bottom right corner's
    Y value, since X is computed using a predefined ratio.
    """
    if (x_crop_percent, y_crop_percent, height_crop_percent) == DO_NOT_CROP:
        return image

    width = image.size[0]
    height = image.size[1]

    top_left_corner = Coordinates(x=width * x_crop_percent, y=height * y_crop_percent)

    updated_height = height * height_crop_percent
    updated_width_from_ratio = updated_height * IMAGE_RATIO_V2

    bottom_right_corner = Coordinates(
        x=min(top_left_corner.x + updated_width_from_ratio, width), y=min(top_left_corner.y + updated_height, height)
    )

    cropped_img = image.crop((top_left_corner.x, top_left_corner.y, bottom_right_corner.x, bottom_right_corner.y))

    return cropped_img


def _resize_image(image: Image) -> Image:
    if image.size[0] <= MAX_THUMB_WIDTH:
        return image

    height_to_width_ratio = 1 / IMAGE_RATIO_V2
    new_height = int(MAX_THUMB_WIDTH * height_to_width_ratio)
    resized_image = image.resize([MAX_THUMB_WIDTH, new_height])

    return resized_image


def _convert_to_jpeg(image: Image) -> bytes:
    new_bytes = io.BytesIO()

    image.save(new_bytes, format="JPEG", quality=CONVERSION_QUALITY, optimize=True, progressive=True)

    return new_bytes.getvalue()
