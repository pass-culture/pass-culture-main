import io
from typing import List

import PIL
from PIL.Image import Image
from colorthief import ColorThief

from utils.logger import logger

MAX_THUMB_WIDTH = 750
CONVERSION_QUALITY = 90
FILE_FORMAT = 'JPEG'
DO_NOT_CROP = [0, 0, 1]
BLACK = b'\x00\x00\x00'


def convert_image(image: bytes, crop_params: List) -> bytes:
    raw_image = PIL.Image.open(io.BytesIO(image)).convert('RGB')
    cropped_image = _crop_image(crop_params[0], crop_params[1], crop_params[2], raw_image)
    resized_image = _resize_image(cropped_image)
    converted_image = _convert_to_jpeg(resized_image)
    return converted_image


def compute_dominant_color(thumb: bytes) -> bytes:
    thumb_bytes = io.BytesIO(thumb)
    color_thief = ColorThief(thumb_bytes)
    dominant_color = bytearray(color_thief.get_color(quality=1))

    if dominant_color is None:
        logger.warning('Warning: could not determine dominant_color for thumb')
        return BLACK
    else:
        return dominant_color


def _crop_image(crop_x: int, crop_y: int, crop_width: int, image: Image) -> Image:
    if crop_x == 0 and crop_y == 0 and crop_width == 1:
        return image

    width = image.size[0]
    height = image.size[1]
    new_x = width * crop_x
    new_y = height * crop_y
    new_width = height * crop_width

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

    ratio = image.size[1] / image.size[0]
    resized_image = image.resize(
        [
            MAX_THUMB_WIDTH,
            int(MAX_THUMB_WIDTH * ratio)
        ]
    )

    return resized_image


def _convert_to_jpeg(image: Image) -> bytes:
    new_bytes = io.BytesIO()

    image.save(
        new_bytes,
        format=FILE_FORMAT,
        quality=CONVERSION_QUALITY,
        optimize=True,
        progressive=True
    )

    return new_bytes.getvalue()
