import pytest

from pcapi.model_creators.generic_creators import API_URL
from pcapi.model_creators.generic_creators import create_favorite
from pcapi.model_creators.generic_creators import create_mediation
from pcapi.model_creators.generic_creators import create_offerer
from pcapi.model_creators.generic_creators import create_recommendation
from pcapi.model_creators.generic_creators import create_user
from pcapi.model_creators.generic_creators import create_venue
from pcapi.model_creators.specific_creators import create_offer_with_thing_product
from pcapi.models import FavoriteSQLEntity
from pcapi.repository import repository
from pcapi.utils.human_ids import humanize

from tests.conftest import TestClient


class Delete:
    class Returns204:
        @pytest.mark.usefixtures("db_session")
        def when_favorite_exists_with_offerId(self, app):
            # Given
            user = create_user(email="test@email.com")
            offerer = create_offerer()
            venue = create_venue(offerer, postal_code="29100", siret="12345678912341")
            offer = create_offer_with_thing_product(venue, thumb_count=0)
            mediation = None
            recommendation = create_recommendation(offer=offer, user=user, mediation=mediation)
            favorite = create_favorite(mediation=mediation, offer=offer, user=user)
            repository.save(recommendation, user, favorite)

            # When
            response = (
                TestClient(app.test_client()).with_auth(user.email).delete(f"{API_URL}/favorites/{humanize(offer.id)}")
            )

            # Then
            assert response.status_code == 200
            assert "id" in response.json
            deleted_favorite = FavoriteSQLEntity.query.first()
            assert deleted_favorite is None

    class Returns404:
        @pytest.mark.usefixtures("db_session")
        def when_expected_parameters_are_not_given(self, app):
            # Given
            user = create_user(email="test@email.com")
            offerer = create_offerer()
            venue = create_venue(offerer, postal_code="29100", siret="12345678912341")
            offer = create_offer_with_thing_product(venue, thumb_count=0)
            mediation = create_mediation(offer, is_active=True)
            recommendation = create_recommendation(offer=offer, user=user, mediation=mediation, is_clicked=False)
            favorite = create_favorite(mediation=mediation, offer=offer, user=user)
            repository.save(recommendation, user, favorite)

            # When
            response = TestClient(app.test_client()).with_auth(user.email).delete(f"{API_URL}/favorites/1")

            # Then
            assert response.status_code == 404

        @pytest.mark.usefixtures("db_session")
        def when_favorite_does_not_exist(self, app):
            # Given
            user = create_user(email="test@email.com")
            offerer = create_offerer()
            venue = create_venue(offerer, postal_code="29100", siret="12345678912341")
            offer = create_offer_with_thing_product(venue, thumb_count=0)
            mediation = create_mediation(offer, is_active=True)
            recommendation = create_recommendation(offer=offer, user=user, mediation=mediation, is_clicked=False)
            favorite = create_favorite(mediation=mediation, offer=offer, user=user)
            repository.save(recommendation, user, favorite)

            # When
            response = TestClient(app.test_client()).with_auth(user.email).delete(f"{API_URL}/favorites/ABCD/ABCD")

            # Then
            assert response.status_code == 404
            deleted_favorite = FavoriteSQLEntity.query.first()
            assert deleted_favorite == favorite
