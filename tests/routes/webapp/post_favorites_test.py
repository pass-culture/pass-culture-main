import pytest

from pcapi.core.users import factories as users_factories
from pcapi.core.users import testing as users_testing
from pcapi.model_creators.generic_creators import create_mediation
from pcapi.model_creators.generic_creators import create_offerer
from pcapi.model_creators.generic_creators import create_venue
from pcapi.model_creators.specific_creators import create_offer_with_thing_product
from pcapi.models import Favorite
from pcapi.notifications.push import testing as push_testing
from pcapi.repository import repository
from pcapi.utils.human_ids import humanize

from tests.conftest import TestClient


class Returns400Test:
    @pytest.mark.usefixtures("db_session")
    def when_offer_id_is_not_received(self, app):
        # Given
        user = users_factories.BeneficiaryFactory(email="test@example.com")

        json = {
            "mediationId": "DA",
        }

        # When
        response = TestClient(app.test_client()).with_session_auth(user.email).post("/favorites", json=json)

        # Then
        assert response.status_code == 400
        assert response.json["global"] == ["Le paramètre offerId est obligatoire"]


class Returns404Test:
    @pytest.mark.usefixtures("db_session")
    def when_offer_is_not_found(self, app):
        # Given
        user = users_factories.BeneficiaryFactory.build(email="test@example.com")
        offerer = create_offerer()
        venue = create_venue(offerer, postal_code="29100", siret="12345678912341")
        offer = create_offer_with_thing_product(venue, thumb_count=0)
        mediation = create_mediation(offer, is_active=True)
        repository.save(user)

        json = {
            "offerId": "ABCD",
            "mediationId": humanize(mediation.id),
        }

        # When
        response = TestClient(app.test_client()).with_session_auth(user.email).post("/favorites", json=json)

        # Then
        assert response.status_code == 404

    @pytest.mark.usefixtures("db_session")
    def when_mediation_is_not_found(self, app):
        # Given
        user = users_factories.BeneficiaryFactory(email="test@example.com")
        offerer = create_offerer()
        venue = create_venue(offerer, postal_code="29100", siret="12345678912341")
        offer = create_offer_with_thing_product(venue, thumb_count=0)
        mediation = create_mediation(offer, is_active=True)
        repository.save(mediation)

        json = {
            "offerId": humanize(offer.id),
            "mediationId": "ABCD",
        }

        # When
        response = TestClient(app.test_client()).with_session_auth(user.email).post("/favorites", json=json)

        # Then
        assert response.status_code == 404


class Returns201Test:
    @pytest.mark.usefixtures("db_session")
    def when_offer_is_added_as_favorite_for_current_user(self, app):
        # Given
        user = users_factories.BeneficiaryFactory(email="test@example.com")
        offerer = create_offerer()
        venue = create_venue(offerer, postal_code="29100", siret="12345678912341")
        offer = create_offer_with_thing_product(venue, thumb_count=0)
        mediation = create_mediation(offer, is_active=True)
        repository.save(mediation)

        json = {
            "offerId": humanize(offer.id),
            "mediationId": humanize(mediation.id),
        }

        # When
        response = TestClient(app.test_client()).with_session_auth(user.email).post("/favorites", json=json)

        # Then
        assert response.status_code == 201

        favorite = Favorite.query.one()
        assert favorite.offerId == offer.id
        assert favorite.mediationId == mediation.id
        assert favorite.userId == user.id

        # One call should be sent to batch, and one to sendinblue
        assert len(push_testing.requests) == 1
        assert len(users_testing.sendinblue_requests) == 1
        sendinblue_data = users_testing.sendinblue_requests[0]
        assert sendinblue_data["attributes"]["LAST_FAVORITE_CREATION_DATE"] is not None

    @pytest.mark.usefixtures("db_session")
    def when_mediation_id_doest_not_exist(self, app):
        # Given
        user = users_factories.BeneficiaryFactory(email="test@example.com")
        offerer = create_offerer()
        venue = create_venue(offerer, postal_code="29100", siret="12345678912341")
        offer = create_offer_with_thing_product(venue, thumb_count=0)
        repository.save(offer)

        json = {
            "offerId": humanize(offer.id),
        }

        # When
        response = TestClient(app.test_client()).with_session_auth(user.email).post("/favorites", json=json)

        # Then
        assert response.status_code == 201

        # One call should be sent to batch, and one to sendinblue
        assert len(push_testing.requests) == 1
        assert len(users_testing.sendinblue_requests) == 1
        sendinblue_data = users_testing.sendinblue_requests[0]
        assert sendinblue_data["attributes"]["LAST_FAVORITE_CREATION_DATE"] is not None
