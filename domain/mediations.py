import io
from typing import List

import PIL
from PIL.Image import Image

MAX_THUMB_WIDTH = 750
CONVERSION_QUALITY = 90
DO_NOT_CROP = [0, 0, 1]
BLACK = b'\x00\x00\x00'


def standardize_image(image: bytes, crop_params: List) -> bytes:
    raw_image = PIL.Image.open(io.BytesIO(image)).convert('RGB')
    cropped_image = _crop_image(crop_params[0], crop_params[1], crop_params[2], raw_image)
    resized_image = _resize_image(cropped_image)
    standard_image = _convert_to_jpeg(resized_image)
    return standard_image


def _crop_image(crop_origin_x: int, crop_origin_y: int, crop_size: int, image: Image) -> Image:
    if crop_origin_x == 0 and crop_origin_y == 0 and crop_size == 1:
        return image

    width = image.size[0]
    height = image.size[1]
    new_x = width * crop_origin_x
    new_y = height * crop_origin_y
    new_width = height * crop_size

    cropped_img = image.crop(
        (
            new_x,
            new_y,
            min(new_x + new_width, width),
            min(new_y + new_width, height)
        )
    )

    return cropped_img


def _resize_image(image: Image) -> Image:
    if image.size[0] <= MAX_THUMB_WIDTH:
        return image

    height_to_width_ratio = image.size[1] / image.size[0]
    new_height = int(MAX_THUMB_WIDTH * height_to_width_ratio)
    resized_image = image.resize(
        [
            MAX_THUMB_WIDTH,
            new_height
        ]
    )

    return resized_image


def _convert_to_jpeg(image: Image) -> bytes:
    new_bytes = io.BytesIO()

    image.save(
        new_bytes,
        format='JPEG',
        quality=CONVERSION_QUALITY,
        optimize=True,
        progressive=True
    )

    return new_bytes.getvalue()
