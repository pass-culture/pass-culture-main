import pytest

from pcapi.core.users import factories as users_factories
from pcapi.model_creators.generic_creators import create_favorite
from pcapi.model_creators.generic_creators import create_mediation
from pcapi.model_creators.generic_creators import create_offerer
from pcapi.model_creators.generic_creators import create_venue
from pcapi.model_creators.specific_creators import create_offer_with_thing_product
from pcapi.models import Favorite
from pcapi.repository import repository
from pcapi.utils.human_ids import humanize

from tests.conftest import TestClient


class Returns204Test:
    @pytest.mark.usefixtures("db_session")
    def when_favorite_exists_with_offerId(self, app):
        # Given
        user = users_factories.UserFactory(email="test@email.com")
        offerer = create_offerer()
        venue = create_venue(offerer, postal_code="29100", siret="12345678912341")
        offer = create_offer_with_thing_product(venue, thumb_count=0)
        mediation = None
        favorite = create_favorite(mediation=mediation, offer=offer, user=user)
        repository.save(favorite)

        # When
        response = TestClient(app.test_client()).with_auth(user.email).delete(f"/favorites/{humanize(offer.id)}")

        # Then
        assert response.status_code == 200
        assert "id" in response.json
        deleted_favorite = Favorite.query.first()
        assert deleted_favorite is None


class Returns404Test:
    @pytest.mark.usefixtures("db_session")
    def when_expected_parameters_are_not_given(self, app):
        # Given
        user = users_factories.UserFactory(email="test@email.com")
        offerer = create_offerer()
        venue = create_venue(offerer, postal_code="29100", siret="12345678912341")
        offer = create_offer_with_thing_product(venue, thumb_count=0)
        mediation = create_mediation(offer, is_active=True)
        favorite = create_favorite(mediation=mediation, offer=offer, user=user)
        repository.save(favorite)

        # When
        response = TestClient(app.test_client()).with_auth(user.email).delete("/favorites/1")

        # Then
        assert response.status_code == 404

    @pytest.mark.usefixtures("db_session")
    def when_favorite_does_not_exist(self, app):
        # Given
        user = users_factories.UserFactory(email="test@email.com")
        offerer = create_offerer()
        venue = create_venue(offerer, postal_code="29100", siret="12345678912341")
        offer = create_offer_with_thing_product(venue, thumb_count=0)
        mediation = create_mediation(offer, is_active=True)
        favorite = create_favorite(mediation=mediation, offer=offer, user=user)
        repository.save(favorite)

        # When
        response = TestClient(app.test_client()).with_auth(user.email).delete("/favorites/ABCD/ABCD")

        # Then
        assert response.status_code == 404
        deleted_favorite = Favorite.query.first()
        assert deleted_favorite == favorite
