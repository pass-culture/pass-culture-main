from datetime import datetime
import secrets
from unittest.mock import patch

from freezegun import freeze_time
import pytest

from pcapi.core.offerers.models import Offerer
from pcapi.core.users import factories as users_factories
from pcapi.model_creators.generic_creators import create_offerer
from pcapi.model_creators.generic_creators import create_user_offerer
from pcapi.model_creators.generic_creators import create_venue
from pcapi.repository import repository

from tests.conftest import TestClient


class Returns202Test:
    @pytest.mark.usefixtures("db_session")
    def expect_offerer_to_be_validated(self, app):
        with freeze_time("2021-06-22 14:48:00") as frozen_time:
            # Given
            offerer_token = secrets.token_urlsafe(20)
            offerer = create_offerer(validation_token=offerer_token)
            user = users_factories.AdminFactory()
            admin = create_user_offerer(user, offerer)
            repository.save(admin)

            # When
            frozen_time.move_to("2021-06-23 11:00:00")
            response = TestClient(app.test_client()).get(
                f"/validate/offerer/{offerer_token}", headers={"origin": "http://localhost:3000"}
            )

        # Then
        assert response.status_code == 202
        assert response.data.decode("utf8") == "Validation effectuée"
        offerer = Offerer.query.filter_by(id=offerer.id).first()
        assert offerer.isValidated is True
        assert offerer.dateValidated == datetime(2021, 6, 23, 11)

    @patch("pcapi.core.search.async_index_venue_ids")
    @pytest.mark.usefixtures("db_session")
    def expect_offerer_managed_venues_to_be_reindexed(self, mocked_async_index_venue_ids, app):
        # Given
        offerer_token = secrets.token_urlsafe(20)
        offerer = create_offerer(validation_token=offerer_token)
        create_venue(offerer, idx=1)
        create_venue(offerer, idx=2, siret=f"{offerer.siren}65371")
        create_venue(offerer, idx=3, is_virtual=True, siret=None)
        user = users_factories.AdminFactory()
        admin = create_user_offerer(user, offerer)
        repository.save(admin)

        # When
        client = TestClient(app.test_client())
        response = client.get(f"/validate/offerer/{offerer_token}")

        # Then
        assert response.status_code == 202
        mocked_async_index_venue_ids.assert_called_once()
        called_args, _ = mocked_async_index_venue_ids.call_args
        assert set(called_args[0]) == set([1, 2, 3])


class Returns404Test:
    @pytest.mark.usefixtures("db_session")
    def expect_offerer_not_to_be_validated_with_unknown_token(self, app):
        # Given
        user = users_factories.ProFactory()

        # When
        response = TestClient(app.test_client()).with_session_auth(email=user.email).get("/validate/offerer/123")

        # Then
        assert response.status_code == 404
