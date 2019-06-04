from models import PcObject
from tests.conftest import clean_database, TestClient
from tests.files.images import ONE_PIXEL_PNG
from tests.test_utils import API_URL, create_venue, create_offerer, create_user, \
    create_mediation, create_offer_with_event_product, create_user_offerer
from utils.human_ids import humanize


@clean_database
def test_post_storage_file_returns_bad_request_if_upload_is_not_authorized_on_model(app):
    # given
    user = create_user()
    offerer = create_offerer()
    venue = create_venue(offerer)
    PcObject.save(user, venue, offerer)

    auth_request = TestClient().with_auth(email=user.email)

    # when
    response = auth_request.post(
        API_URL + '/storage/thumb/%s/%s/%s' % ('venues', humanize(venue.id), '1'),
        json={},
        files={'file': ('1.png', b'123')}
    )

    # then
    assert response.status_code == 400
    assert response.json()['text'] == 'upload is not authorized for this model'


@clean_database
def test_post_storage_file_update_a_thumb_for_an_user(app):
    # given
    user = create_user()
    offerer = create_offerer()
    venue = create_venue(offerer)
    PcObject.save(user, venue, offerer)

    auth_request = TestClient().with_auth(email=user.email)

    # when
    response = auth_request.post(
        API_URL + '/storage/thumb/%s/%s/%s' % ('users', humanize(user.id), '0'),
        json={},
        files={'file': ('1.png', ONE_PIXEL_PNG)}
    )

    # then
    assert response.status_code == 200


@clean_database
def test_post_storage_file_on_a_mediation_returns_bad_request_if_user_is_not_attached_to_offerer(app):
    # given
    user = create_user()
    offerer = create_offerer()
    venue = create_venue(offerer)
    offer = create_offer_with_event_product(venue)
    mediation = create_mediation(offer)
    PcObject.save(user, offer, mediation, venue, offerer)

    auth_request = TestClient().with_auth(email=user.email)

    # when
    response = auth_request.post(
        API_URL + '/storage/thumb/%s/%s/%s' % ('mediations', humanize(mediation.id), '0'),
        json={},
        files={'file': ('1.png', ONE_PIXEL_PNG)}
    )

    # then
    assert response.status_code == 403
    assert response.json()['global'] == ["Cette structure n'est pas enregistrée chez cet utilisateur."]


@clean_database
def test_post_storage_file_on_a_mediation_returns_200_if_user_is_attached_to_offerer(app):
    # given
    user = create_user()
    offerer = create_offerer()
    user_offerer = create_user_offerer(user, offerer)
    venue = create_venue(offerer)
    offer = create_offer_with_event_product(venue)
    mediation = create_mediation(offer)
    PcObject.save(user_offerer, mediation)

    auth_request = TestClient().with_auth(email=user.email)

    # when
    response = auth_request.post(
        API_URL + '/storage/thumb/%s/%s/%s' % ('mediations', humanize(mediation.id), '0'),
        json={},
        files={'file': ('1.png', ONE_PIXEL_PNG)}
    )

    # then
    assert response.status_code == 200
