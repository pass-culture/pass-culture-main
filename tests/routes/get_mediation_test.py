from models import PcObject
from tests.conftest import clean_database, TestClient
from tests.model_creators.generic_creators import create_user, create_offerer, create_venue, create_user_offerer, \
    create_mediation
from tests.model_creators.specific_creators import create_offer_with_event_product
from utils.human_ids import humanize


class Get:
    class Returns200:
        @clean_database
        def when_the_mediation_exists(self, app):
            # given
            user = create_user()
            offerer = create_offerer()
            venue = create_venue(offerer)
            offer = create_offer_with_event_product(venue)
            user_offerer = create_user_offerer(user, offerer)
            mediation = create_mediation(offer)
            PcObject.save(mediation)
            PcObject.save(offer)
            PcObject.save(user, venue, offerer, user_offerer)

            auth_request = TestClient(app.test_client()).with_auth(email=user.email)

            # when
            response = auth_request.get('/mediations/%s' % humanize(mediation.id))

            # then
            assert response.status_code == 200
            assert response.json['id'] == humanize(mediation.id)
            assert response.json['frontText'] == mediation.frontText
            assert response.json['backText'] == mediation.backText

    class Returns404:
        @clean_database
        def when_the_mediation_does_not_exist(self, app):
            # given
            user = create_user()
            PcObject.save(user)
            auth_request = TestClient(app.test_client()).with_auth(email=user.email)

            # when
            response = auth_request.get('/mediations/AE')

            # then
            assert response.status_code == 404
