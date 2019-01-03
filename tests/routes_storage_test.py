import pytest

from models import PcObject
from tests.conftest import clean_database
from tests.files.images import ONE_PIXEL_PNG
from utils.human_ids import humanize
from utils.test_utils import API_URL, create_venue, create_offerer, create_user, req_with_auth, \
    create_mediation, create_event_offer, create_user_offerer


@clean_database
@pytest.mark.standalone
def test_post_storage_file_returns_bad_request_if_upload_is_not_authorized_on_model(app):
    # given
    user = create_user(password='p@55sw0rd')
    offerer = create_offerer()
    venue = create_venue(offerer)
    PcObject.check_and_save(user, venue, offerer)

    auth_request = req_with_auth(email=user.email, password='p@55sw0rd')

    # when
    response = auth_request.post(
        API_URL + '/storage/thumb/%s/%s/%s' % ('venues', humanize(venue.id), '1'),
        data={},
        files={'file': ('1.png', b'123')}
    )

    # then
    assert response.status_code == 400
    assert response.json()['text'] == 'upload is not authorized for this model'


@clean_database
@pytest.mark.standalone
def test_post_storage_file_update_a_thumb_for_an_user(app):
    # given
    user = create_user(password='p@55sw0rd')
    offerer = create_offerer()
    venue = create_venue(offerer)
    PcObject.check_and_save(user, venue, offerer)

    auth_request = req_with_auth(email=user.email, password='p@55sw0rd')

    # when
    response = auth_request.post(
        API_URL + '/storage/thumb/%s/%s/%s' % ('users', humanize(user.id), '0'),
        data={},
        files={'file': ('1.png', ONE_PIXEL_PNG)}
    )

    # then
    assert response.status_code == 200


@clean_database
@pytest.mark.standalone
def test_post_storage_file_on_a_mediation_returns_bad_request_if_user_is_not_attached_to_offerer(app):
    # given
    user = create_user(password='p@55sw0rd')
    offerer = create_offerer()
    venue = create_venue(offerer)
    offer = create_event_offer(venue)
    mediation = create_mediation(offer)
    PcObject.check_and_save(user, offer, mediation, venue, offerer)

    auth_request = req_with_auth(email=user.email, password='p@55sw0rd')

    # when
    response = auth_request.post(
        API_URL + '/storage/thumb/%s/%s/%s' % ('mediations', humanize(mediation.id), '0'),
        data={},
        files={'file': ('1.png', ONE_PIXEL_PNG)}
    )

    # then
    assert response.status_code == 403
    assert response.json()['global'] == ["Cette structure n'est pas enregistrée chez cet utilisateur."]


@clean_database
@pytest.mark.standalone
def test_post_storage_file_on_a_mediation_returns_200_if_user_is_attached_to_offerer(app):
    # given
    user = create_user(password='p@55sw0rd')
    offerer = create_offerer()
    user_offerer = create_user_offerer(user, offerer)
    venue = create_venue(offerer)
    offer = create_event_offer(venue)
    mediation = create_mediation(offer)
    PcObject.check_and_save(user_offerer, mediation)

    auth_request = req_with_auth(email=user.email, password='p@55sw0rd')

    # when
    response = auth_request.post(
        API_URL + '/storage/thumb/%s/%s/%s' % ('mediations', humanize(mediation.id), '0'),
        data={},
        files={'file': ('1.png', ONE_PIXEL_PNG)}
    )

    # then
    assert response.status_code == 200
