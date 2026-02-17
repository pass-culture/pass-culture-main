import io
import pathlib
from unittest.mock import patch

import PIL
import PIL.Image
import PIL.ImageChops
import pytest

from pcapi.utils.image_conversion import MAX_THUMB_WIDTH
from pcapi.utils.image_conversion import CropParams
from pcapi.utils.image_conversion import ImageRatio
from pcapi.utils.image_conversion import ImageRatioError
from pcapi.utils.image_conversion import _check_ratio
from pcapi.utils.image_conversion import _crop_image
from pcapi.utils.image_conversion import _post_process_image
from pcapi.utils.image_conversion import _pre_process_image
from pcapi.utils.image_conversion import _resize_image
from pcapi.utils.image_conversion import _shrink_image
from pcapi.utils.image_conversion import get_crop_params
from pcapi.utils.image_conversion import process_original_image
from pcapi.utils.image_conversion import standardize_image

import tests


IMAGES_DIR = pathlib.Path(tests.__path__[0]) / "files"


class CropImageTest:
    def test_correctly_crops_image(self):
        image_as_bytes = (IMAGES_DIR / "mosaique.png").read_bytes()
        raw_image = PIL.Image.open(io.BytesIO(image_as_bytes)).convert("RGB")
        expected_image_as_bytes = (IMAGES_DIR / "mosaique_cropped.png").read_bytes()
        expected_image = PIL.Image.open(io.BytesIO(expected_image_as_bytes)).convert("RGB")

        cropped_image = _crop_image(
            0.3288307188857965, 0.14834245742092478, 0.7299270072992701, 0.7299270072992701, raw_image
        )

        difference = PIL.ImageChops.difference(cropped_image, expected_image)
        assert difference.getbbox() is None


class PreProcessImageTest:
    def test_removes_exif_orientation(self):
        image_as_bytes = (IMAGES_DIR / "image_with_exif_orientation.jpeg").read_bytes()
        expected_image = PIL.Image.open(io.BytesIO(image_as_bytes)).convert("RGB")
        exif_info = expected_image.getexif()
        assert 274 in exif_info

        transposed_image = _pre_process_image(image_as_bytes)

        exif_info = transposed_image.getexif()
        assert 274 not in exif_info

    def test_handles_truncated_image(self):
        image_as_bytes = (IMAGES_DIR / "mouette_full_size.jpg").read_bytes()

        result = _pre_process_image(image_as_bytes[:-25])

        assert result.size == (1786, 1785)

    def test_converts_to_rgb(self):
        image_as_bytes = (IMAGES_DIR / "mouette_full_size.jpg").read_bytes()

        result = _pre_process_image(image_as_bytes)

        assert result.mode == "RGB"


class ShrinkImageTest:
    def test_shrinks_large_image(self):
        image = PIL.Image.new("RGB", (1500, 1000), "red")

        result = _shrink_image(image)

        assert result.width == MAX_THUMB_WIDTH

    def test_does_not_shrink_small_image(self):
        image = PIL.Image.new("RGB", (400, 300), "red")

        result = _shrink_image(image)

        assert result.size == (400, 300)

    def test_preserves_ratio(self):
        image = PIL.Image.new("RGB", (2000, 1000), "red")
        original_ratio = image.width / image.height

        result = _shrink_image(image)

        assert (result.width / result.height) == original_ratio


class ResizeImageTest:
    def test_resizes_image_with_landscape_ratio(self):
        image = PIL.Image.new("RGB", (1500, 1500), "red")

        result = _resize_image(image, ImageRatio.LANDSCAPE)

        assert result.width == MAX_THUMB_WIDTH
        assert result.height == 500

    def test_resizes_with_portrait_ratio(self):
        image = PIL.Image.new("RGB", (1500, 1500), "red")

        result = _resize_image(image, ImageRatio.PORTRAIT)

        assert result.width == MAX_THUMB_WIDTH
        assert result.height == 1125

    def test_resizes_with_square_ratio(self):
        image = PIL.Image.new("RGB", (1500, 1500), "red")

        result = _resize_image(image, ImageRatio.SQUARE)

        assert result.width == MAX_THUMB_WIDTH
        assert result.height == MAX_THUMB_WIDTH

    def test_resize_image_with_max_width(self):
        image = PIL.Image.new("RGB", (1500, 1500), "red")

        result = _resize_image(image, ImageRatio.SQUARE, max_width=72)

        assert result.size == (72, 72)

    def test_does_not_resize_small_image(self):
        image = PIL.Image.new("RGB", (600, 600), "red")

        result = _resize_image(image, ImageRatio.PORTRAIT)

        assert result.size == (600, 600)


class CheckRatioTest:
    def test_accepts_correct_portrait_ratio(self):
        image = PIL.Image.new("RGB", (200, 300), "red")

        result = _check_ratio(image, ImageRatio.PORTRAIT)

        assert result is image

    def test_accepts_correct_landscape_ratio(self):
        image = PIL.Image.new("RGB", (300, 200), "red")

        result = _check_ratio(image, ImageRatio.LANDSCAPE)

        assert result is image

    def test_raises_on_incorrect_ratio(self):
        image = PIL.Image.new("RGB", (100, 100), "red")

        with pytest.raises(ImageRatioError):
            _check_ratio(image, ImageRatio.LANDSCAPE)


class PostProcessImageTest:
    def test_returns_jpeg_bytes(self):
        image = PIL.Image.new("RGB", (100, 100), "red")

        result = _post_process_image(image)

        result_image = PIL.Image.open(io.BytesIO(result))
        assert result_image.format == "JPEG"


class StandardizeImageTest:
    @patch("pcapi.utils.image_conversion._post_process_image")
    @patch("pcapi.utils.image_conversion._check_ratio")
    @patch("pcapi.utils.image_conversion._resize_image")
    @patch("pcapi.utils.image_conversion._crop_image")
    @patch("pcapi.utils.image_conversion._pre_process_image")
    def test_standardize_portrait_image_with_max_width(
        self, mock_pre_process, mock_crop, mock_resize, mock_check_ratio, mock_post_process
    ):
        mock_pre_process.return_value = b"pre-processed-image"
        mock_crop.return_value = b"cropped-image"
        mock_resize.return_value = b"resized-image"
        mock_check_ratio.return_value = b"validated-image"
        mock_post_process.return_value = b"post-processed-image"

        result = standardize_image(b"fake-image", ratio=ImageRatio.PORTRAIT, max_width=100)

        assert result == b"post-processed-image"
        mock_pre_process.assert_called_once_with(b"fake-image")
        mock_crop.assert_called_once_with(0.0, 0.0, 1.0, 1.0, b"pre-processed-image")
        mock_resize.assert_called_once_with(b"cropped-image", ImageRatio.PORTRAIT, 100)
        mock_check_ratio.assert_called_once_with(b"resized-image", ImageRatio.PORTRAIT)
        mock_post_process.assert_called_once_with(b"validated-image")

    @patch("pcapi.utils.image_conversion._post_process_image")
    @patch("pcapi.utils.image_conversion._check_ratio")
    @patch("pcapi.utils.image_conversion._resize_image")
    @patch("pcapi.utils.image_conversion._crop_image")
    @patch("pcapi.utils.image_conversion._pre_process_image")
    def test_standardize_landscape_image_with_crop_params(
        self, mock_pre_process, mock_crop, mock_resize, mock_check_ratio, mock_post_process
    ):
        mock_pre_process.return_value = b"pre-processed-image"
        mock_crop.return_value = b"cropped-image"
        mock_resize.return_value = b"resized-image"
        mock_check_ratio.return_value = b"validated-image"
        mock_post_process.return_value = b"post-processed-image"
        crop_params = CropParams(
            x_crop_percent=0.1, y_crop_percent=0.2, height_crop_percent=0.8, width_crop_percent=0.7
        )

        result = standardize_image(b"fake-image", ratio=ImageRatio.LANDSCAPE, crop_params=crop_params)

        assert result == b"post-processed-image"
        mock_pre_process.assert_called_once_with(b"fake-image")
        mock_crop.assert_called_once_with(0.1, 0.2, 0.8, 0.7, b"pre-processed-image")
        mock_resize.assert_called_once_with(b"cropped-image", ImageRatio.LANDSCAPE, 750)
        mock_check_ratio.assert_called_once_with(b"resized-image", ImageRatio.LANDSCAPE)
        mock_post_process.assert_called_once_with(b"validated-image")


class ProcessOriginalImageTest:
    @patch("pcapi.utils.image_conversion._post_process_image")
    @patch("pcapi.utils.image_conversion._shrink_image")
    @patch("pcapi.utils.image_conversion._pre_process_image")
    def test_process_original_image_with_resize(self, mock_pre_process, mock_shrink, mock_post_process):
        mock_pre_process.return_value = b"pre-processed-image"
        mock_shrink.return_value = b"shrunk-image"
        mock_post_process.return_value = b"post-processed-image"

        result = process_original_image(b"fake-image", resize=True)

        assert result == b"post-processed-image"
        mock_pre_process.assert_called_once_with(b"fake-image")
        mock_shrink.assert_called_once_with(b"pre-processed-image")
        mock_post_process.assert_called_once_with(b"shrunk-image")

    @patch("pcapi.utils.image_conversion._post_process_image")
    @patch("pcapi.utils.image_conversion._shrink_image")
    @patch("pcapi.utils.image_conversion._pre_process_image")
    def test_process_original_image_without_resize(self, mock_pre_process, mock_shrink, mock_post_process):
        mock_pre_process.return_value = b"pre-processed-image"
        mock_post_process.return_value = b"post-processed-image"

        result = process_original_image(b"fake-image")

        assert result == b"post-processed-image"
        mock_shrink.assert_not_called()
        mock_post_process.assert_called_once_with(b"pre-processed-image")


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
