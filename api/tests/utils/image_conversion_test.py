import io
import pathlib

import PIL
import pytest

from pcapi.utils.image_conversion import CropParams
from pcapi.utils.image_conversion import ImageRatio
from pcapi.utils.image_conversion import ImageRatioError
from pcapi.utils.image_conversion import _crop_image
from pcapi.utils.image_conversion import _pre_process_image
from pcapi.utils.image_conversion import _resize_image
from pcapi.utils.image_conversion import process_original_image
from pcapi.utils.image_conversion import standardize_image

import tests


IMAGES_DIR = pathlib.Path(tests.__path__[0]) / "files"


class ImageConversionTest:
    def when_image_is_correctly_cropped(self):
        # given
        crop_origin_x = 0.3288307188857965
        crop_origin_y = 0.14834245742092478
        crop_rect_height = 0.7299270072992701
        crop_rect_width = 0.7299270072992701

        image_as_bytes = (IMAGES_DIR / "mosaique.png").read_bytes()
        raw_image = PIL.Image.open(io.BytesIO(image_as_bytes)).convert("RGB")

        expected_image_as_bytes = (IMAGES_DIR / "mosaique_cropped.png").read_bytes()
        expected_image = PIL.Image.open(io.BytesIO(expected_image_as_bytes)).convert("RGB")

        # when
        cropped_image = _crop_image(crop_origin_x, crop_origin_y, crop_rect_height, crop_rect_width, raw_image)

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
        transposed_image = _pre_process_image(image_as_bytes)

        # then
        exif_info = transposed_image.getexif()
        assert 274 not in exif_info

    def when_resize_image_that_have_width_less_than_max_width(self):
        # given
        image_as_bytes = (IMAGES_DIR / "mosaique_cropped.png").read_bytes()
        expected_image = PIL.Image.open(io.BytesIO(image_as_bytes)).convert("RGB")

        # when
        resized_image = _resize_image(expected_image, ratio=ImageRatio.PORTRAIT)

        # then
        difference = PIL.ImageChops.difference(resized_image, expected_image)
        assert difference.getbbox() is None

    def test_image_ratio_portrait(self):
        image_as_bytes = (IMAGES_DIR / "mouette_full_size.jpg").read_bytes()

        standardized_image = standardize_image(image_as_bytes, ratio=ImageRatio.PORTRAIT)

        result_image = PIL.Image.open(io.BytesIO(standardized_image)).convert("RGB")
        assert (result_image.width / result_image.height) == pytest.approx(ImageRatio.PORTRAIT.value, 0.01)

    def test_image_ratio_landscape(self):
        image_as_bytes = (IMAGES_DIR / "mouette_full_size.jpg").read_bytes()

        standardized_image = standardize_image(image_as_bytes, ratio=ImageRatio.LANDSCAPE)

        result_image = PIL.Image.open(io.BytesIO(standardized_image)).convert("RGB")
        assert (result_image.width / result_image.height) == pytest.approx(ImageRatio.LANDSCAPE.value, 0.01)

    def test_crop_with_incorrect_ratio(self):
        image_as_bytes = (IMAGES_DIR / "mouette_full_size.jpg").read_bytes()

        with pytest.raises(ImageRatioError):
            crop_params = CropParams(height_crop_percent=0.3, width_crop_percent=0.3)
            standardize_image(image_as_bytes, crop_params=crop_params, ratio=ImageRatio.LANDSCAPE)

    def test_image_shrink_with_same_ratio(self):
        image_as_bytes = (IMAGES_DIR / "mouette_full_size.jpg").read_bytes()
        original_image = PIL.Image.open(io.BytesIO(image_as_bytes))

        expected_ratio = original_image.width / original_image.height

        standardized_image = process_original_image(image_as_bytes)

        result_image = PIL.Image.open(io.BytesIO(standardized_image))

        assert result_image.width < original_image.width
        assert result_image.height < original_image.height
        assert (result_image.width / result_image.height) == pytest.approx(expected_ratio, 0.01)

    def test_do_not_raise_error_when_image_is_truncated(self):
        image_as_bytes = (IMAGES_DIR / "mouette_full_size.jpg").read_bytes()
        assert _pre_process_image(image_as_bytes[:-25]).size == (1786, 1785)
