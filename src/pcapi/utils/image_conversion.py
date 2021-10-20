import io

import PIL
from PIL import Image
from PIL import ImageOps


MAX_THUMB_WIDTH = 750
CONVERSION_QUALITY = 90
DO_NOT_CROP = (0, 0, 1)
IMAGE_RATIO_V2 = 6 / 9


def standardize_image(image: bytes, crop_params: tuple = None) -> bytes:
    crop_params = crop_params or DO_NOT_CROP
    raw_image = PIL.Image.open(io.BytesIO(image))

    # Remove exif orientation so that it doesnt rotate after upload
    transposed_image = _transpose_image(raw_image)

    if transposed_image.mode == "RGBA":
        background = PIL.Image.new("RGB", transposed_image.size, (255, 255, 255))
        background.paste(transposed_image, mask=transposed_image.split()[3])
        transposed_image = background
    transposed_image = transposed_image.convert("RGB")

    x_position, y_position, crop_size = crop_params
    cropped_image = _crop_image(x_position, y_position, crop_size, transposed_image)
    resized_image = _resize_image(cropped_image)
    standard_image = _convert_to_jpeg(resized_image)
    return standard_image


def _transpose_image(raw_image):
    return ImageOps.exif_transpose(raw_image)


def _crop_image(crop_origin_x: int, crop_origin_y: int, crop_rect_height: int, image: Image) -> Image:
    if (crop_origin_x, crop_origin_y, crop_rect_height) == DO_NOT_CROP:
        return image

    width = image.size[0]
    height = image.size[1]
    updated_x_position = width * crop_origin_x
    updated_y_position = height * crop_origin_y
    updated_height = height * crop_rect_height
    updated_width_from_ratio = updated_height * IMAGE_RATIO_V2
    bottom_right_corner_x = min(updated_x_position + updated_width_from_ratio, width)
    bottom_right_corner_y = min(updated_y_position + updated_height, height)

    cropped_img = image.crop((updated_x_position, updated_y_position, bottom_right_corner_x, bottom_right_corner_y))

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
