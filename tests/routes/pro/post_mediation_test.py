from io import BytesIO
import os
from pathlib import Path
from unittest.mock import MagicMock
from unittest.mock import patch

import pytest

from pcapi.core.offers.models import Mediation
from pcapi.model_creators.generic_creators import create_offerer
from pcapi.model_creators.generic_creators import create_user
from pcapi.model_creators.generic_creators import create_user_offerer
from pcapi.model_creators.generic_creators import create_venue
from pcapi.model_creators.specific_creators import create_offer_with_event_product
from pcapi.repository import repository
from pcapi.utils.date import format_into_utc_date
from pcapi.utils.human_ids import humanize

import tests
from tests.conftest import TestClient
from tests.conftest import clean_database


IMAGES_DIR = Path(tests.__path__[0]) / "files"


@pytest.mark.usefixtures("db_session")
class Returns201:
    @patch("pcapi.routes.pro.mediations.feature_queries.is_active", return_value=True)
    @patch("pcapi.routes.pro.mediations.redis.add_offer_id")
    @patch("pcapi.routes.pro.mediations.read_thumb")
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

        read_thumb.return_value = (IMAGES_DIR / "mouette_full_size.jpg").read_bytes()

        data = {
            "offerId": humanize(offer.id),
            "offererId": humanize(offerer.id),
            "thumbUrl": "https://www.deridet.com/photo/art/grande/8682609-13705793.jpg?v=1450665370",
        }

        # when
        response = auth_request.post("/mediations", form=data)

        # then
        assert response.status_code == 201
        mediation = Mediation.query.one()
        assert mediation.thumbCount == 1
        assert response.json == {
            "id": humanize(mediation.id),
        }

    @patch("pcapi.routes.pro.mediations.feature_queries.is_active", return_value=True)
    @patch("pcapi.routes.pro.mediations.redis.add_offer_id")
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

        thumb = (IMAGES_DIR / "mouette_full_size.jpg").read_bytes()

        files = {
            "offerId": humanize(offer.id),
            "offererId": humanize(offerer.id),
            "thumb": (BytesIO(thumb), "image.png"),
        }

        # when
        response = auth_request.post("/mediations", files=files)

        # then
        mediation = Mediation.query.one()
        assert mediation.thumbCount == 1
        assert response.status_code == 201

    @patch("pcapi.routes.pro.mediations.feature_queries.is_active", return_value=True)
    @patch("pcapi.routes.pro.mediations.redis.add_offer_id")
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

        thumb = (IMAGES_DIR / "mouette_full_size.jpg").read_bytes()

        files = {
            "offerId": humanize(offer.id),
            "offererId": humanize(offerer.id),
            "thumb": (BytesIO(thumb), "image.png"),
        }

        # when
        response = auth_request.post("/mediations", files=files)

        # then
        assert response.status_code == 201
        mock_redis.assert_called_once()
        mock_kwargs = mock_redis.call_args[1]
        assert mock_kwargs["offer_id"] == offer.id


class Returns400:
    @patch("pcapi.connectors.thumb_storage.requests.get")
    def when_mediation_is_created_with_thumb_url_pointing_to_not_an_image(
        self, mock_thumb_storage_request, app, db_session
    ):
        # given
        api_response = {}
        response_return_value = MagicMock(status_code=200, text="")
        response_return_value.headers = MagicMock(return_value={"Content-type": "image/jpeg"})
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
            "offerId": humanize(offer.id),
            "offererId": humanize(offerer.id),
            "thumbUrl": "https://beta.gouv.fr/",
        }

        # when
        response = auth_request.post("/mediations", form=data)

        # then
        assert response.status_code == 400
        assert response.json == {"thumb_url": ["L'adresse saisie n'est pas valide"]}

    def when_mediation_is_created_with_file_upload_but_without_filename(self, app, db_session):
        # given
        user = create_user()
        offerer = create_offerer()
        venue = create_venue(offerer)
        offer = create_offer_with_event_product(venue)
        user_offerer = create_user_offerer(user, offerer)
        repository.save(user, venue, user_offerer)

        # when
        with open(IMAGES_DIR / "pixel.png", "rb") as fp:
            data = {"offerId": humanize(offer.id), "offererId": humanize(offerer.id), "thumb": (fp, "")}
            response = TestClient(app.test_client()).with_auth(email=user.email).post("/mediations", form=data)

        # then
        assert response.status_code == 400
        assert response.json == {"thumb": ["Vous devez fournir une image d'accroche"]}

    @clean_database
    def when_mediation_is_created_with_file_upload_but_image_is_too_small(self, app):
        # given
        user = create_user()
        offerer = create_offerer()
        venue = create_venue(offerer)
        offer = create_offer_with_event_product(venue)
        user_offerer = create_user_offerer(user, offerer)
        repository.save(user, venue, user_offerer)
        thumb = (IMAGES_DIR / "mouette_small.jpg").read_bytes()
        data = {
            "offerId": humanize(offer.id),
            "offererId": humanize(offerer.id),
            "thumb": (BytesIO(thumb), "image.png"),
        }

        # when
        response = TestClient(app.test_client()).with_auth(email=user.email).post("/mediations", form=data)

        # then
        assert response.status_code == 400
        assert response.json == {"thumb": ["L'image doit faire 400 * 400 px minimum"]}

    @clean_database
    @patch("pcapi.routes.pro.mediations.repository")
    def expect_mediation_not_to_be_saved(self, mock_repository, app):
        # given
        user = create_user()
        offerer = create_offerer()
        venue = create_venue(offerer)
        offer = create_offer_with_event_product(venue)
        user_offerer = create_user_offerer(user, offerer)
        repository.save(user, venue, user_offerer)
        thumb = (IMAGES_DIR / "mouette_small.jpg").read_bytes()
        data = {
            "offerId": humanize(offer.id),
            "offererId": humanize(offerer.id),
            "thumb": (BytesIO(thumb), "image.png"),
        }
        mock_repository.save.reset_mock()

        # when
        TestClient(app.test_client()).with_auth(email=user.email).post("/mediations", form=data)

        # then
        mock_repository.save.assert_not_called()
