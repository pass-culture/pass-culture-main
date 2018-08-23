from os import path
from pathlib import Path

import pytest

from models import PcObject, Offer
from tests.conftest import clean_database
from utils.human_ids import humanize
from utils.test_utils import API_URL, req_with_auth, create_user, create_offerer, create_user_offerer, \
    create_event_offer, create_venue


@clean_database
@pytest.mark.standalone
def test_create_mediation_with_thumb(app):
    # given
    user = create_user(password='p@55sw0rd')
    offerer = create_offerer()
    venue = create_venue(offerer)
    offer = create_event_offer(venue)
    user_offerer = create_user_offerer(user, offerer)

    PcObject.check_and_save(offer)
    PcObject.check_and_save(user, venue, offerer, user_offerer)

    auth_request = req_with_auth(email=user.email, password='p@55sw0rd')

    with open(Path(path.dirname(path.realpath(__file__))) / '..'
              / 'mock' / 'thumbs' / 'mediations' / '1', 'rb') as thumb_file:
        data = {'offerId': humanize(offer.id), 'offererId': humanize(offerer.id), }
        files = {'thumb': ('1.jpg', thumb_file)}

        # when
        response = auth_request.post(API_URL + '/mediations', data=data, files=files)

    # then
    assert response.status_code == 201
