import os
from io import BytesIO
from pathlib import Path
from unittest.mock import patch

from models import PcObject
from tests.conftest import clean_database, TestClient
from tests.files.images import ONE_PIXEL_PNG
from tests.test_utils import create_user, \
    create_offer_with_event_product, \
    create_offerer, \
    create_user_offerer, \
    create_venue
from utils.human_ids import humanize

MODULE_PATH = Path(os.path.dirname(os.path.realpath(__file__)))


class Post:
    class Returns201:
        @clean_database
        @patch('routes.mediations.read_thumb')
        def when_mediation_is_created_with_thumb_url(self, read_thumb, app):
            # given
            user = create_user()
            offerer = create_offerer()
            venue = create_venue(offerer)
            offer = create_offer_with_event_product(venue)
            user_offerer = create_user_offerer(user, offerer)

            PcObject.save(offer)
            PcObject.save(user, venue, offerer, user_offerer)

            auth_request = TestClient(app.test_client()).with_auth(email=user.email)

            with open(MODULE_PATH / '..' / 'files/mouette_full_size.jpg', 'rb') as f:
                read_thumb.return_value = f.read()

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

            with open(MODULE_PATH / '..' / 'files/mouette_full_size.jpg', 'rb') as f:
                thumb = f.read()

            files = {
                'offerId': humanize(offer.id),
                'offererId': humanize(offerer.id),
                'thumb': (BytesIO(thumb), 'image.png')
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

        @clean_database
        def when_mediation_is_created_with_file_upload_but_without_filename(self, app):
            # given
            user = create_user()
            offerer = create_offerer()
            venue = create_venue(offerer)
            offer = create_offer_with_event_product(venue)
            user_offerer = create_user_offerer(user, offerer)
            PcObject.save(user, venue, user_offerer)

            data = {
                'offerId': humanize(offer.id),
                'offererId': humanize(offerer.id),
                'thumb': (BytesIO(ONE_PIXEL_PNG), '')

            }

            # when
            response = TestClient(app.test_client()) \
                .with_auth(email=user.email) \
                .post('/mediations', form=data)

            # then
            assert response.status_code == 400
            assert response.json['thumb'] == ["Vous devez fournir une image d'accroche"]

        @clean_database
        def when_mediation_is_created_with_file_upload_but_image_is_too_small(self, app):
            # given
            user = create_user()
            offerer = create_offerer()
            venue = create_venue(offerer)
            offer = create_offer_with_event_product(venue)
            user_offerer = create_user_offerer(user, offerer)
            PcObject.save(user, venue, user_offerer)
            with open(MODULE_PATH / '..' / 'files/mouette_small.jpg', 'rb') as f:
                thumb = f.read()
            data = {
                'offerId': humanize(offer.id),
                'offererId': humanize(offerer.id),
                'thumb': (BytesIO(thumb), 'image.png')

            }

            # when
            response = TestClient(app.test_client()) \
                .with_auth(email=user.email) \
                .post('/mediations', form=data)

            # then
            assert response.status_code == 400
            assert response.json['thumb'] == [
                "L'image doit faire 100 ko minimum",
                "L'image doit faire 400 * 400 px minimum"
            ]
