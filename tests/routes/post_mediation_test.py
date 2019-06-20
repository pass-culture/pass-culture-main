from io import BytesIO

from models import PcObject
from tests.conftest import clean_database, TestClient
from tests.files.images import ONE_PIXEL_PNG
from tests.test_utils import create_user, \
    create_offer_with_event_product, \
    create_offerer, \
    create_user_offerer, \
    create_venue
from utils.human_ids import humanize


class Post:
    class Returns201:
        @clean_database
        def when_mediation_is_created_with_thumb_url(self, app):
            # given
            user = create_user()
            offerer = create_offerer()
            venue = create_venue(offerer)
            offer = create_offer_with_event_product(venue)
            user_offerer = create_user_offerer(user, offerer)

            PcObject.save(offer)
            PcObject.save(user, venue, offerer, user_offerer)

            auth_request = TestClient(app.test_client()).with_auth(email=user.email)

            data = {
                'offerId': humanize(offer.id),
                'offererId': humanize(offerer.id),
                'thumbUrl': 'https://www.deridet.com/photo/art/grande/8682609-13705793.jpg?v=1450665370'
            }

            # when
            response = auth_request.post('/mediations', form=data)

            # then
            assert response.status_code == 201

        @clean_database
        def when_mediation_is_created_with_thumb_file(self, app):
            # given
            user = create_user()
            offerer = create_offerer()
            venue = create_venue(offerer)
            offer = create_offer_with_event_product(venue)
            user_offerer = create_user_offerer(user, offerer)

            PcObject.save(offer)
            PcObject.save(user, venue, offerer, user_offerer)

            auth_request = TestClient(app.test_client()).with_auth(email=user.email)

            files = {
                'offerId': humanize(offer.id),
                'offererId': humanize(offerer.id),
                'thumb': (BytesIO(ONE_PIXEL_PNG), 'image.png')
            }

            # when
            response = auth_request.post('/mediations', files=files)

            # then
            assert response.status_code == 201

    class Returns400:
        @clean_database
        def when_mediation_is_created_with_thumb_url_pointing_to_not_an_image(self, app):
            # given
            user = create_user()
            offerer = create_offerer()
            venue = create_venue(offerer)
            offer = create_offer_with_event_product(venue)
            user_offerer = create_user_offerer(user, offerer)
            PcObject.save(user, venue, user_offerer)

            auth_request = TestClient(app.test_client()).with_auth(email=user.email)

            data = {
                'offerId': humanize(offer.id),
                'offererId': humanize(offerer.id),
                'thumbUrl': 'https://beta.gouv.fr/'
            }

            # when
            response = auth_request.post('/mediations', form=data)

            # then
            assert response.status_code == 400
            assert response.json['thumbUrl'] == ["L'adresse saisie n'est pas valide"]
