from PIL.Image import Image


def crop_image(crop_x: int, crop_y: int, crop_width: int, image: Image):
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