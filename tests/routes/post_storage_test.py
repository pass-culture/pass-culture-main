from io import BytesIO

from repository import repository
import pytest
from tests.conftest import TestClient
from tests.files.images import ONE_PIXEL_PNG
from model_creators.generic_creators import create_user, create_offerer, create_venue, create_user_offerer, \
    create_mediation
from model_creators.specific_creators import create_offer_with_event_product
from utils.human_ids import humanize


class Post:
    class Returns200:
        @pytest.mark.usefixtures("db_session")
        def when_a_file_is_uploaded_for_a_mediation(self, app):
            # given
            user = create_user()
            offerer = create_offerer()
            user_offerer = create_user_offerer(user, offerer)
            venue = create_venue(offerer)
            offer = create_offer_with_event_product(venue)
            mediation = create_mediation(offer)
            repository.save(user_offerer, mediation)

            auth_request = TestClient(app.test_client()).with_auth(email=user.email)

            # when
            response = auth_request.post(
                '/storage/thumb/%s/%s/%s' % ('mediations', humanize(mediation.id), '0'),
                files={'file': (BytesIO(ONE_PIXEL_PNG), '1.png')}
            )

            # then
            assert response.status_code == 200

    class Returns400:
        @pytest.mark.usefixtures("db_session")
        def when_upload_is_not_authorized_on_model(self, app):
            # given
            user = create_user()
            offerer = create_offerer()
            venue = create_venue(offerer)
            repository.save(user, venue, offerer)

            auth_request = TestClient(app.test_client()).with_auth(email=user.email)

            # when
            response = auth_request.post(
                '/storage/thumb/%s/%s/%s' % ('venues', humanize(venue.id), '1'),
                files={'file': (BytesIO(b'123'), '1.png')}
            )

            # then
            assert response.status_code == 400
            assert response.json['text'] == 'upload is not authorized for this model'

    class Returns403:
        @pytest.mark.usefixtures("db_session")
        def when_the_current_user_is_not_attached_to_the_offerers(self, app):
            # given
            user = create_user()
            offerer = create_offerer()
            venue = create_venue(offerer)
            offer = create_offer_with_event_product(venue)
            mediation = create_mediation(offer)
            repository.save(user, offer, mediation, venue, offerer)

            auth_request = TestClient(app.test_client()).with_auth(email=user.email)

            # when
            response = auth_request.post(
                '/storage/thumb/%s/%s/%s' % ('mediations', humanize(mediation.id), '0'),
                files={'file': (BytesIO(ONE_PIXEL_PNG), '1.png')}
            )

            # then
            assert response.status_code == 403
            assert response.json['global'] == ["Vous n'avez pas les droits d'accès suffisant pour accéder à cette information."]
