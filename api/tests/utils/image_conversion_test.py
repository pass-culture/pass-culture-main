import io
import pathlib
from unittest.mock import patch

import PIL
import pytest

from pcapi.utils.image_conversion import MAX_THUMB_WIDTH
from pcapi.utils.image_conversion import CropParams
from pcapi.utils.image_conversion import ImageRatio
from pcapi.utils.image_conversion import ImageRatioError
from pcapi.utils.image_conversion import _crop_image
from pcapi.utils.image_conversion import _pre_process_image
from pcapi.utils.image_conversion import _resize_image
from pcapi.utils.image_conversion import _shrink_image
from pcapi.utils.image_conversion import center_crop_image
from pcapi.utils.image_conversion import get_crop_params
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

    def test_do_not_raise_error_when_image_is_truncated(self):
        image_as_bytes = (IMAGES_DIR / "mouette_full_size.jpg").read_bytes()
        assert _pre_process_image(image_as_bytes[:-25]).size == (1786, 1785)


class ShrinkImageTest:
    def test_shrinks_image_to_default_width(self):
        image = PIL.Image.new("RGB", (1500, 1000), "red")

        result = _shrink_image(image)

        assert result.width == MAX_THUMB_WIDTH

    def test_shrinks_image_to_max_width(self):
        image = PIL.Image.new("RGB", (1500, 1000), "red")

        result = _shrink_image(image, max_width=100)

        assert result.width == 100

    def test_does_not_shrink_image_smaller_than_max_width(self):
        image = PIL.Image.new("RGB", (400, 300), "red")

        result = _shrink_image(image)

        assert result.size == (400, 300)

    def test_preserves_ratio(self):
        image = PIL.Image.new("RGB", (2000, 1000), "red")
        original_ratio = image.width / image.height

        result = _shrink_image(image)

        assert (result.width / result.height) == original_ratio


class CenterCropImageTest:
    @patch("pcapi.utils.image_conversion._post_process_image")
    @patch("pcapi.utils.image_conversion._shrink_image")
    @patch("pcapi.utils.image_conversion._crop_image")
    @patch("pcapi.utils.image_conversion.get_crop_params")
    @patch("pcapi.utils.image_conversion._pre_process_image")
    def test_center_crop_image_with_landscape_ratio(
        self, mock_pre_process, mock_get_crop_params, mock_crop, mock_shrink, mock_post_process
    ):
        pre_processed_image = PIL.Image.new("RGB", (800, 600))
        mock_pre_process.return_value = pre_processed_image
        mock_get_crop_params.return_value = CropParams(
            x_crop_percent=0.1, y_crop_percent=0.0, height_crop_percent=1.0, width_crop_percent=0.8
        )
        mock_crop.return_value = b"cropped-image"
        mock_shrink.return_value = b"shrunk-image"
        mock_post_process.return_value = b"post-processed-image"

        result = center_crop_image(b"fake-image", ratio=ImageRatio.LANDSCAPE)

        assert result == b"post-processed-image"
        mock_pre_process.assert_called_once_with(b"fake-image")
        mock_get_crop_params.assert_called_once_with(800, 600, ImageRatio.LANDSCAPE)
        mock_crop.assert_called_once_with(0.1, 0.0, 1.0, 0.8, pre_processed_image)
        mock_shrink.assert_called_once_with(b"cropped-image", MAX_THUMB_WIDTH)
        mock_post_process.assert_called_once_with(b"shrunk-image")

    @patch("pcapi.utils.image_conversion._post_process_image")
    @patch("pcapi.utils.image_conversion._shrink_image")
    @patch("pcapi.utils.image_conversion._crop_image")
    @patch("pcapi.utils.image_conversion.get_crop_params")
    @patch("pcapi.utils.image_conversion._pre_process_image")
    def test_center_crop_image_with_custom_max_width(
        self, mock_pre_process, mock_get_crop_params, mock_crop, mock_shrink, mock_post_process
    ):
        pre_processed_image = PIL.Image.new("RGB", (1000, 500))
        mock_pre_process.return_value = pre_processed_image
        mock_get_crop_params.return_value = CropParams(
            x_crop_percent=0.0, y_crop_percent=0.2, height_crop_percent=0.6, width_crop_percent=1.0
        )
        mock_crop.return_value = b"cropped-image"
        mock_shrink.return_value = b"shrunk-image"
        mock_post_process.return_value = b"post-processed-image"

        result = center_crop_image(b"fake-image", ratio=ImageRatio.PORTRAIT, max_width=400)

        assert result == b"post-processed-image"
        mock_pre_process.assert_called_once_with(b"fake-image")
        mock_get_crop_params.assert_called_once_with(1000, 500, ImageRatio.PORTRAIT)
        mock_crop.assert_called_once_with(0.0, 0.2, 0.6, 1.0, pre_processed_image)
        mock_shrink.assert_called_once_with(b"cropped-image", 400)
        mock_post_process.assert_called_once_with(b"shrunk-image")


class GetCropParamsTest:
    def test_landscape_wider_image(self):
        crop_params = get_crop_params(400, 200, ImageRatio.LANDSCAPE)

        assert crop_params.x_crop_percent == 0.125
        assert crop_params.y_crop_percent == 0
        assert crop_params.width_crop_percent == 0.75
        assert crop_params.height_crop_percent == 1

    def test_landscape_taller_image(self):
        crop_params = get_crop_params(300, 1000, ImageRatio.LANDSCAPE)

        assert crop_params.x_crop_percent == 0
        assert crop_params.y_crop_percent == 0.4
        assert crop_params.width_crop_percent == 1
        assert crop_params.height_crop_percent == 0.2

    def test_portrait_taller_image(self):
        crop_params = get_crop_params(200, 400, ImageRatio.PORTRAIT)

        assert crop_params.x_crop_percent == 0
        assert crop_params.y_crop_percent == 0.125
        assert crop_params.width_crop_percent == 1
        assert crop_params.height_crop_percent == 0.75

    def test_portrait_wider_image(self):
        crop_params = get_crop_params(1000, 300, ImageRatio.PORTRAIT)

        assert crop_params.x_crop_percent == 0.4
        assert crop_params.y_crop_percent == 0
        assert crop_params.width_crop_percent == 0.2
        assert crop_params.height_crop_percent == 1
