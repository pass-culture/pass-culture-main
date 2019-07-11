""" utils thumb """
import os
from pathlib import Path

import pytest
from werkzeug.datastructures import FileStorage

from models import ApiErrors, EventType
from validation.mediations import read_thumb


def test_read_thumb_returns_api_error_when_no_extension_in_filename():
    # given
    dir_path = Path(os.path.dirname(os.path.realpath(__file__)))
    thumb_path = dir_path / '..' / '..' / \
                 'sandboxes' / 'thumbs' / 'products' \
                 / str(EventType.CINEMA)

    files = {
        'thumb': FileStorage(open(thumb_path, mode='rb'))
    }

    # when
    with pytest.raises(ApiErrors) as api_errors:
        read_thumb(files=files, form={})

    # then
    assert api_errors.value.errors['thumb'] == [
        "Cet image manque d'une extension (.png, .jpg, .jpeg, .gif) ou son format n'est pas autoris\u00e9"
    ]
