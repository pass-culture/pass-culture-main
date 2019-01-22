import io

from PIL.Image import Image

MAX_THUMB_WIDTH = 750
CONVERSION_QUALITY = 90
FILE_FORMAT = 'JPEG'
DO_NOT_CROP = [0, 0, 1]


def crop_image(crop_x: int, crop_y: int, crop_width: int, image: Image) -> Image:
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


def resize_image(image: Image) -> Image:
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


def convert_to_jpeg(image: Image) -> bytes:
    new_bytes = io.BytesIO()

    image.save(
        new_bytes,
        format=FILE_FORMAT,
        quality=CONVERSION_QUALITY,
        optimize=True,
        progressive=True
    )

    return new_bytes.getvalue()
