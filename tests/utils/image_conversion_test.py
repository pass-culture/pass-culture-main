import io
import pathlib
from unittest import mock

import PIL

from pcapi.utils.image_conversion import _crop_image
from pcapi.utils.image_conversion import _resize_image
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
        cropped_image = _crop_image(crop_origin_x, crop_origin_y, crop_rect_height, raw_image)

        # then
        difference = PIL.ImageChops.difference(cropped_image, expected_image)
        assert difference.getbbox() is None

    @mock.patch("pcapi.utils.image_conversion.PIL.Image.open")
    @mock.patch("pcapi.utils.image_conversion._crop_image")
    @mock.patch("pcapi.utils.image_conversion._resize_image")
    @mock.patch("pcapi.utils.image_conversion._convert_to_jpeg")
    def when_standardize_image_is_called_with_right_arguments(
        self, mock_convert_to_jpeg, mock_resize_image, mock_crop_image, mock_open_image
    ):
        # given
        crop_origin_x = 0.2
        crop_origin_y = 0.45
        crop_rect_height = 0.23
        crop_params = (crop_origin_x, crop_origin_y, crop_rect_height)
        image_bytes = b"test_image"

        mock_open_image.return_value.convert.return_value = "A"
        mock_crop_image.return_value = "B"
        mock_resize_image.return_value = "C"

        # when
        standardize_image(image_bytes, crop_params)

        # then
        mock_crop_image.assert_called_once_with(crop_origin_x, crop_origin_y, crop_rect_height, "A")
        mock_resize_image.assert_called_once_with("B")
        mock_convert_to_jpeg.assert_called_once_with("C")

    def when_resize_image_that_have_width_less_than_max_width(self):
        # given
        image_as_bytes = (IMAGES_DIR / "mosaique_cropped.png").read_bytes()
        expected_image = PIL.Image.open(io.BytesIO(image_as_bytes)).convert("RGB")

        # when
        resized_image = _resize_image(expected_image)

        # then
        difference = PIL.ImageChops.difference(resized_image, expected_image)
        assert difference.getbbox() is None
