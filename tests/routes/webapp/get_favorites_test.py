import pytest

from pcapi.core.users import factories as users_factories
from pcapi.model_creators.generic_creators import create_booking
from pcapi.model_creators.generic_creators import create_favorite
from pcapi.model_creators.generic_creators import create_mediation
from pcapi.model_creators.generic_creators import create_offerer
from pcapi.model_creators.generic_creators import create_stock
from pcapi.model_creators.generic_creators import create_venue
from pcapi.model_creators.specific_creators import create_offer_with_thing_product
from pcapi.repository import repository
from pcapi.utils.human_ids import humanize

from tests.conftest import TestClient


class Returns200Test:
    @pytest.mark.usefixtures("db_session")
    def when_user_is_logged_in_but_has_no_favorites(self, app):
        # Given
        user = users_factories.BeneficiaryFactory()
        repository.save(user)

        # When
        response = TestClient(app.test_client()).with_auth(user.email).get("/favorites")

        # Then
        assert response.status_code == 200
        assert response.json == []

    @pytest.mark.usefixtures("db_session")
    def when_user_is_logged_in_and_has_two_favorite_offers(self, app):
        # Given
        user = users_factories.BeneficiaryFactory()
        offerer = create_offerer()
        venue = create_venue(offerer, postal_code="29100", siret="12345678912341")
        offer1 = create_offer_with_thing_product(venue=venue, thumb_count=0)
        mediation1 = create_mediation(offer=offer1, is_active=True, idx=123)
        favorite1 = create_favorite(mediation=mediation1, offer=offer1, user=user)
        offer2 = create_offer_with_thing_product(venue=venue, thumb_count=0)
        favorite2 = create_favorite(offer=offer2, user=user)
        repository.save(user, favorite1, favorite2)

        # When
        response = TestClient(app.test_client()).with_auth(user.email).get("/favorites")

        # Then
        assert response.status_code == 200
        assert len(response.json) == 2
        first_favorite = response.json[0]
        assert "offer" in first_favorite
        assert "venue" in first_favorite["offer"]
        assert "mediationId" in first_favorite
        assert "validationToken" not in first_favorite["offer"]["venue"]

    @pytest.mark.usefixtures("db_session")
    def when_user_is_logged_in_and_a_favorite_booked_offer_exist(self, app):
        # Given
        user = users_factories.BeneficiaryFactory()
        offerer = create_offerer()
        venue = create_venue(offerer, postal_code="29100", siret="12345678912341")
        offer = create_offer_with_thing_product(venue, thumb_count=0)
        mediation = create_mediation(offer, is_active=True)
        favorite = create_favorite(mediation=mediation, offer=offer, user=user)
        stock = create_stock(offer=offer, price=0)
        booking = create_booking(user=user, stock=stock)
        repository.save(booking, favorite)

        # When
        response = TestClient(app.test_client()).with_auth(user.email).get("/favorites")

        # Then
        assert response.status_code == 200
        assert len(response.json) == 1
        favorite = response.json[0]
        assert "offer" in favorite
        assert "venue" in favorite["offer"]
        assert "stocks" in favorite["offer"]
        assert stock.price == favorite["offer"]["stocks"][0]["price"]
        assert booking.quantity == favorite["booking"]["quantity"]
        assert humanize(booking.id) in favorite["booking"]["id"]
        assert "validationToken" not in favorite["offer"]["venue"]


class Returns401Test:
    @pytest.mark.usefixtures("db_session")
    def when_user_is_not_logged_in(self, app):
        # When
        response = TestClient(app.test_client()).get("/favorites")

        # Then
        assert response.status_code == 401
