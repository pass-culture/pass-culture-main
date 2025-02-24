import pytest

from pcapi.core import testing
from pcapi.core.categories import subcategories
from pcapi.core.offerers import factories as offerers_factories
from pcapi.core.offers import factories as offers_factories
from pcapi.core.offers.models import GcuCompatibilityType
from pcapi.core.offers.models import ImageType
from pcapi.core.testing import assert_num_queries
from pcapi.core.users import factories as users_factories


pytestmark = pytest.mark.usefixtures("db_session")


class Return200Test:
    num_queries = testing.AUTHENTICATION_QUERIES
    num_queries += 1  # check user_offerer exists
    num_queries += 1  # select offer that is headline

    def test_get_offerer_headline_offer_success(self, client):
        user_offerer = offerers_factories.UserOffererFactory()
        pro = user_offerer.user
        offerer = user_offerer.offerer
        venue = offerers_factories.VenueFactory(managingOfferer=offerer)
        offer = offers_factories.OfferFactory(venue=venue)
        offers_factories.HeadlineOfferFactory(offer=offer, venue=venue)
        client = client.with_session_auth(email=pro.email)
        offerer_id = offerer.id
        with assert_num_queries(self.num_queries):
            response = client.get(f"/offerers/{offerer_id}/headline-offer")

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

    def test_get_offerer_headline_offer_with_product_mediations(self, client):
        user_offerer = offerers_factories.UserOffererFactory()
        pro = user_offerer.user
        offerer = user_offerer.offerer
        venue = offerers_factories.VenueFactory(managingOfferer=offerer)
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
        offerer_id = offerer.id
        with assert_num_queries(self.num_queries):
            response = client.get(f"/offerers/{offerer_id}/headline-offer")
            assert response.status_code == 200


class Return400Test:
    num_queries = testing.AUTHENTICATION_QUERIES
    num_queries += 1  # check user_offerer
    num_queries += 1  # get headline offer
    num_queries += 1  # rollback (atomic)

    def test_access_by_unauthorized_pro_user(self, client):
        pro = users_factories.ProFactory()
        offerer = offerers_factories.OffererFactory()
        client = client.with_session_auth(email=pro.email)
        offerer_id = offerer.id
        with assert_num_queries(self.num_queries - 1):  # unauthorized, so no query to headline offer made
            response = client.get(f"/offerers/{offerer_id}/headline-offer")
            assert response.status_code == 403

    def test_get_offerer_headline_offer_not_found(self, client):
        user_offerer = offerers_factories.UserOffererFactory()
        pro = user_offerer.user
        offerer = user_offerer.offerer
        client = client.with_session_auth(email=pro.email)
        offerer_id = offerer.id
        with assert_num_queries(self.num_queries):
            response = client.get(f"/offerers/{offerer_id}/headline-offer")
            assert response.status_code == 404

    def test_with_multiple_headline_offer_on_one_offerer_should_fail(self, client):
        user_offerer = offerers_factories.UserOffererFactory()
        pro = user_offerer.user
        offerer = user_offerer.offerer
        venue = offerers_factories.VenueFactory(managingOfferer=offerer)
        offer = offers_factories.OfferFactory(venue=venue)
        offers_factories.HeadlineOfferFactory(offer=offer, venue=venue)
        other_venue = offerers_factories.VenueFactory(managingOfferer=offerer)
        other_offer = offers_factories.OfferFactory(venue=other_venue)
        offers_factories.HeadlineOfferFactory(offer=other_offer, venue=other_venue)
        client = client.with_session_auth(email=pro.email)
        offerer_id = offerer.id
        with assert_num_queries(self.num_queries):
            response = client.get(f"/offerers/{offerer_id}/headline-offer")
            assert response.status_code == 404
            assert response.json == {"global": "Une entité juridique ne peut avoir qu’une seule offre à la une"}
