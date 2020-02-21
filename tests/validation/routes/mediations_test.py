import os
from pathlib import Path

import pytest

from models import ApiErrors
from validation.routes.mediations import check_thumb_quality

MODULE_PATH = Path(os.path.dirname(os.path.realpath(__file__)))


class CheckThumbQualityTest:
    def test_an_error_is_raised_if_the_thumb_width_is_less_than_400_px(self):
        # given
        with open(f'{MODULE_PATH}/../../files/mouette_portrait.jpg', 'rb') as f:
            thumb = f.read()

        # when
        with pytest.raises(ApiErrors) as e:
            check_thumb_quality(thumb)

        # then
        assert e.value.errors['thumb'] == ["L'image doit faire 400 * 400 px minimum"]

    def test_an_error_is_raised_if_the_thumb_height_is_less_than_400_px(self):
        # given
        with open(f'{MODULE_PATH}/../../files/mouette_landscape.jpg', 'rb') as f:
            thumb = f.read()

        # when
        with pytest.raises(ApiErrors) as e:
            check_thumb_quality(thumb)

        # then
        assert e.value.errors['thumb'] == ["L'image doit faire 400 * 400 px minimum"]

    def test_no_error_is_raised_if_the_thumb_is_heavier_than_100_ko(self):
        # given
        with open(f'{MODULE_PATH}/../../files/mouette_full_size.jpg', 'rb') as f:
            thumb = f.read()

        try:
            # when
            check_thumb_quality(thumb)
        except:
            # then
            assert False, 'Images heavier than 100 ko should be accepted'
