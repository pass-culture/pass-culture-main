import pytest

from pcapi.core import testing
from pcapi.core.categories import subcategories
from pcapi.core.offerers import factories as offerers_factories
from pcapi.core.offers import factories as offers_factories
from pcapi.core.offers.models import GcuCompatibilityType
from pcapi.core.offers.models import ImageType
from pcapi.core.testing import assert_num_queries
from pcapi.core.users import factories as users_factories
from pcapi.models.api_errors import OBJECT_NOT_FOUND_ERROR_MESSAGE


pytestmark = pytest.mark.usefixtures("db_session")


class Return200Test:
    num_queries = testing.AUTHENTICATION_QUERIES
    num_queries += 1  # check user_offerer exists
    num_queries += 1  # select offer that is headline

    def test_get_venue_headline_offer_success(self, client):
        user_offerer = offerers_factories.UserOffererFactory()
        pro = user_offerer.user
        venue = offerers_factories.VenueFactory(managingOfferer=user_offerer.offerer)
        offer = offers_factories.OfferFactory(venue=venue)
        offers_factories.HeadlineOfferFactory(offer=offer, venue=venue)
        client = client.with_session_auth(email=pro.email)
        venue_id = venue.id
        with assert_num_queries(self.num_queries):
            response = client.get(f"/venues/{venue_id}/headline-offer")

        assert response.status_code == 200
        assert response.json == {
            "name": offer.name,
            "id": offer.id,
            "image": {
                "credit": offer.image.credit,
                "url": offer.image.url,
            },
            "venueId": offer.venueId,
        }

    def test_get_venue_headline_offer_with_product_mediations(self, client):
        user_offerer = offerers_factories.UserOffererFactory()
        pro = user_offerer.user
        venue = offerers_factories.VenueFactory(managingOfferer=user_offerer.offerer)
        product = offers_factories.ProductFactory(
            name="Les Héritiers",
            description="Les étudiants et la culture",
            subcategoryId=subcategories.LIVRE_PAPIER.id,
            gcuCompatibilityType=GcuCompatibilityType.COMPATIBLE,
        )
        offers_factories.ProductMediationFactory(product=product, imageType=ImageType.RECTO)
        offers_factories.ProductMediationFactory(product=product, imageType=ImageType.VERSO)

        offer = offers_factories.OfferFactory(venue=venue, product=product)
        offers_factories.HeadlineOfferFactory(offer=offer, venue=venue, without_mediation=True)
        client = client.with_session_auth(email=pro.email)
        venue_id = venue.id
        with assert_num_queries(self.num_queries):
            response = client.get(f"/venues/{venue_id}/headline-offer")
            assert response.status_code == 200


class Return404Test:
    num_queries = testing.AUTHENTICATION_QUERIES
    num_queries += 1  # check user_offerer
    num_queries += 1  # get headline offer
    num_queries += 1  # rollback (atomic)
    num_queries += 1  # rollback (atomic)

    def test_access_by_unauthorized_pro_user(self, client):
        pro = users_factories.ProFactory()
        venue = offerers_factories.VenueFactory()
        client = client.with_session_auth(email=pro.email)
        venue_id = venue.id
        with assert_num_queries(self.num_queries - 1):  # unauthorized, so no query to headline offer made
            response = client.get(f"/venues/{venue_id}/headline-offer")
            assert response.status_code == 404
            assert response.json == {"global": [OBJECT_NOT_FOUND_ERROR_MESSAGE]}

    def test_get_venue_headline_offer_not_found(self, client):
        user_offerer = offerers_factories.UserOffererFactory()
        pro = user_offerer.user
        venue = offerers_factories.VenueFactory(managingOfferer=user_offerer.offerer)
        client = client.with_session_auth(email=pro.email)
        venue_id = venue.id
        with assert_num_queries(self.num_queries):
            response = client.get(f"/venues/{venue_id}/headline-offer")
            assert response.status_code == 404
            assert response.json == {"global": [OBJECT_NOT_FOUND_ERROR_MESSAGE]}
