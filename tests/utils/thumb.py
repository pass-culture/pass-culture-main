""" utils thumb """
import os
from pathlib import Path
import pytest
from werkzeug.datastructures import FileStorage

from models import ApiErrors
from utils.thumb import read_thumb

def test_read_thumb_returns_api_error_when_no_extension_in_filename():
    dir_path = Path(os.path.dirname(os.path.realpath(__file__)))

    thumb_path = dir_path / '..' / 'sandboxes'\
                 / 'thumbs' / 'events'\
                 / str(1)
    files = {
        'thumb': FileStorage(open(thumb_path, mode='rb'))
    }

    with pytest.raises(ApiErrors) as api_errors:
        read_thumb(files=files, form={})

    assert api_errors.value.errors['thumb'] == [
        "Cet image manque d'une extension (.png, .jpg...) ou son format n'est pas autoris\u00e9"
    ]
