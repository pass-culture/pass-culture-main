import io
import pathlib

import PIL
import pytest

from pcapi.utils.image_conversion import IMAGE_RATIO_LANDSCAPE_DEFAULT
from pcapi.utils.image_conversion import IMAGE_RATIO_PORTRAIT_DEFAULT
from pcapi.utils.image_conversion import _crop_image
from pcapi.utils.image_conversion import _resize_image
from pcapi.utils.image_conversion import _transpose_image
from pcapi.utils.image_conversion import standardize_image

import tests


IMAGES_DIR = pathlib.Path(tests.__path__[0]) / "files"


class ImageConversionTest:
    def when_image_is_correctly_cropped(self):
        # given
        crop_origin_x = 0.3288307188857965
        crop_origin_y = 0.14834245742092478
        crop_rect_height = 0.7299270072992701

        image_as_bytes = (IMAGES_DIR / "mosaique.png").read_bytes()
        raw_image = PIL.Image.open(io.BytesIO(image_as_bytes)).convert("RGB")

        expected_image_as_bytes = (IMAGES_DIR / "mosaique_cropped.png").read_bytes()
        expected_image = PIL.Image.open(io.BytesIO(expected_image_as_bytes)).convert("RGB")

        # when
        cropped_image = _crop_image(
            crop_origin_x, crop_origin_y, crop_rect_height, raw_image, ratio=IMAGE_RATIO_PORTRAIT_DEFAULT
        )

        # then
        difference = PIL.ImageChops.difference(cropped_image, expected_image)
        assert difference.getbbox() is None

    def when_image_has_an_original_orientation(self):
        # given
        image_as_bytes = (IMAGES_DIR / "image_with_exif_orientation.jpeg").read_bytes()
        expected_image = PIL.Image.open(io.BytesIO(image_as_bytes)).convert("RGB")

        exif_info = expected_image.getexif()
        # They exif tag 274 is the image orientation
        assert 274 in exif_info

        # when
        transposed_image = _transpose_image(expected_image)

        # then
        exif_info = transposed_image.getexif()
        assert 274 not in exif_info

    def when_resize_image_that_have_width_less_than_max_width(self):
        # given
        image_as_bytes = (IMAGES_DIR / "mosaique_cropped.png").read_bytes()
        expected_image = PIL.Image.open(io.BytesIO(image_as_bytes)).convert("RGB")

        # when
        resized_image = _resize_image(expected_image, ratio=IMAGE_RATIO_PORTRAIT_DEFAULT)

        # then
        difference = PIL.ImageChops.difference(resized_image, expected_image)
        assert difference.getbbox() is None

    def test_image_ratio_portrait(self):
        image_as_bytes = (IMAGES_DIR / "mouette_full_size.jpg").read_bytes()

        standardized_image = standardize_image(image_as_bytes, ratio=IMAGE_RATIO_PORTRAIT_DEFAULT)

        result_image = PIL.Image.open(io.BytesIO(standardized_image)).convert("RGB")
        assert (result_image.width / result_image.height) == pytest.approx(IMAGE_RATIO_PORTRAIT_DEFAULT, 0.01)

    def test_image_ratio_landscape(self):
        image_as_bytes = (IMAGES_DIR / "mouette_full_size.jpg").read_bytes()

        standardized_image = standardize_image(image_as_bytes, ratio=IMAGE_RATIO_LANDSCAPE_DEFAULT)

        result_image = PIL.Image.open(io.BytesIO(standardized_image)).convert("RGB")
        assert (result_image.width / result_image.height) == pytest.approx(IMAGE_RATIO_LANDSCAPE_DEFAULT, 0.01)
