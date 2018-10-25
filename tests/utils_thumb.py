""" utils thumb """
import os
from pathlib import Path
from flask import Flask
import pytest
import requests

from models import ApiErrors
from utils.thumb import read_thumb

"""
@pytest.mark.standalone
def test_read_thumb_returns_api_error_when_no_extension_in_filename():
    dir_path = Path(os.path.dirname(os.path.realpath(__file__)))

    thumb_path = dir_path / '..' / 'sandboxes'\
                 / 'thumbs' / 'events'\
                 / str(1)
    files = {
        'thumb': open(thumb_path, mode='rb')
    }

    #app = Flask(__name__)
    #url = '/thumb'
    #@app.route('/thumb', methods=['POST'])
    #def post_thumb():
    #    read_thumb(files=request.files, form=request.form)
    #response = requests.Session().post(url, files=files)

    print('files["thumb"]', dir(files["thumb"]))

    read_thumb(files=files, form={})

    with pytest.raises(ApiErrors) as api_errors:
        print('OK')
"""
