import os
from io import BytesIO
from pathlib import Path
from unittest.mock import patch, MagicMock

from repository import repository
import pytest
from tests.conftest import clean_database, TestClient
from tests.files.images import ONE_PIXEL_PNG
from tests.model_creators.generic_creators import create_user, create_offerer, create_venue, create_user_offerer
from tests.model_creators.specific_creators import create_offer_with_event_product
from utils.human_ids import humanize

MODULE_PATH = Path(os.path.dirname(os.path.realpath(__file__)))


class Post:
    class Returns201:
        @pytest.mark.usefixtures("db_session")
        @patch('routes.mediations.feature_queries.is_active', return_value=True)
        @patch('routes.mediations.redis.add_offer_id')
        @patch('routes.mediations.read_thumb')
        def when_mediation_is_created_with_thumb_url(self, read_thumb, mock_redis, mock_feature, app):
            # given
            user = create_user()
            offerer = create_offerer()
            venue = create_venue(offerer)
            offer = create_offer_with_event_product(venue)
            user_offerer = create_user_offerer(user, offerer)

            repository.save(offer)
            repository.save(user, venue, offerer, user_offerer)

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

        @pytest.mark.usefixtures("db_session")
        @patch('routes.mediations.feature_queries.is_active', return_value=True)
        @patch('routes.mediations.redis.add_offer_id')
        def when_mediation_is_created_with_thumb_file(self, mock_redis, mock_feature, app):
            # given
            user = create_user()
            offerer = create_offerer()
            venue = create_venue(offerer)
            offer = create_offer_with_event_product(venue)
            user_offerer = create_user_offerer(user, offerer)

            repository.save(offer)
            repository.save(user, venue, offerer, user_offerer)

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

        @pytest.mark.usefixtures("db_session")
        @patch('routes.mediations.feature_queries.is_active', return_value=True)
        @patch('routes.mediations.redis.add_offer_id')
        def should_add_offer_id_to_redis_when_mediation_is_created_with_thumb(self, mock_redis, mock_feature, app):
            # given
            user = create_user()
            offerer = create_offerer()
            venue = create_venue(offerer)
            offer = create_offer_with_event_product(venue)
            user_offerer = create_user_offerer(user, offerer)

            repository.save(offer)
            repository.save(user, venue, offerer, user_offerer)

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
            mock_redis.assert_called_once()
            mock_args, mock_kwargs = mock_redis.call_args
            assert mock_kwargs['offer_id'] == offer.id

    class Returns400:
        @patch('connectors.thumb_storage.requests.get')
        @pytest.mark.usefixtures("db_session")
        def when_mediation_is_created_with_thumb_url_pointing_to_not_an_image(self, mock_thumb_storage_request, app):
            # given
            api_response = {}
            response_return_value = MagicMock(status_code=200, text='')
            response_return_value.headers = MagicMock(return_value={'Content-type': 'image/jpeg'})
            response_return_value.json = MagicMock(return_value=api_response)
            mock_thumb_storage_request.return_value = response_return_value

            user = create_user()
            offerer = create_offerer()
            venue = create_venue(offerer)
            offer = create_offer_with_event_product(venue)
            user_offerer = create_user_offerer(user, offerer)
            repository.save(user, venue, user_offerer)

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

        @pytest.mark.usefixtures("db_session")
        def when_mediation_is_created_with_file_upload_but_without_filename(self, app):
            # given
            user = create_user()
            offerer = create_offerer()
            venue = create_venue(offerer)
            offer = create_offer_with_event_product(venue)
            user_offerer = create_user_offerer(user, offerer)
            repository.save(user, venue, user_offerer)

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
            repository.save(user, venue, user_offerer)
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
            assert response.json['thumb'] == ["L'image doit faire 400 * 400 px minimum"]

        @clean_database
        @patch('routes.mediations.repository')
        def expect_mediation_not_to_be_saved(self, mock_repository, app):
            # given
            user = create_user()
            offerer = create_offerer()
            venue = create_venue(offerer)
            offer = create_offer_with_event_product(venue)
            user_offerer = create_user_offerer(user, offerer)
            repository.save(user, venue, user_offerer)
            with open(MODULE_PATH / '..' / 'files/mouette_small.jpg', 'rb') as f:
                thumb = f.read()
            data = {
                'offerId': humanize(offer.id),
                'offererId': humanize(offerer.id),
                'thumb': (BytesIO(thumb), 'image.png')
            }
            mock_repository.save.reset_mock()

            # when
            TestClient(app.test_client()) \
                .with_auth(email=user.email) \
                .post('/mediations', form=data)

            # then
            mock_repository.save.assert_not_called()
