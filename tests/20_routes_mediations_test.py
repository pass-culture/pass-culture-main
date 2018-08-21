from os import path
from pathlib import Path

from utils.test_utils import API_URL, req_with_auth


def test_10_create_mediation():
    with open(Path(path.dirname(path.realpath(__file__))) / '..'
              / 'mock' / 'thumbs' / 'mediations' / '1', 'rb') as thumb_file:
        data = {
                'offerId': 'AE',
                'offererId': 'AE',
               }
        files = {
                 'thumb': ('1.jpg', thumb_file)
                }
        r_create = req_with_auth().post(API_URL + '/mediations',
                                        data=data,
                                        files=files)
        assert r_create.status_code == 201
