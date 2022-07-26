import pytest

from pcapi.core.educational import factories as educational_factories
from pcapi.core.educational.models import CollectiveOffer
from pcapi.core.educational.models import CollectiveOfferTemplate
import pcapi.core.offerers.factories as offerers_factories
from pcapi.utils.human_ids import dehumanize_or_raise
from pcapi.utils.human_ids import humanize


@pytest.mark.usefixtures("db_session")
class Returns200Test:
    def test_create_collective_offer_template_with_educational_price_detail(self, client):
        # Given
        venue = offerers_factories.VenueFactory()
        offerers_factories.UserOffererFactory(offerer=venue.managingOfferer, user__email="user@example.com")
        domain = educational_factories.EducationalDomainFactory(name="Test domain")
        offer = educational_factories.CollectiveOfferFactory(venue=venue, educational_domains=[domain])

        # When
        data = {
            "educationalPriceDetail": "pouet",
        }
        response = client.with_session_auth(offer.venue.managingOfferer.UserOfferers[0].user.email).post(
            f"/collective/offers-template/{humanize(offer.id)}/", json=data
        )

        # Then
        assert response.status_code == 201
        template_id = dehumanize_or_raise(response.json["id"])
        template = CollectiveOfferTemplate.query.filter_by(id=template_id).one_or_none()
        assert template is not None
        assert CollectiveOffer.query.filter_by(id=offer.id).one_or_none() is None
        assert template.name == offer.name
        assert template.venueId == offer.venueId
        assert template.priceDetail == data["educationalPriceDetail"]
        assert template.offerVenue == offer.offerVenue
        assert template.bookingEmail == offer.bookingEmail
        assert template.domains == [domain]

    def test_create_collective_offer_template_without_price_detail(self, client):
        # Given
        venue = offerers_factories.VenueFactory()
        offerers_factories.UserOffererFactory(offerer=venue.managingOfferer, user__email="user@example.com")
        offer = educational_factories.CollectiveOfferFactory(venue=venue)

        # When
        response = client.with_session_auth(offer.venue.managingOfferer.UserOfferers[0].user.email).post(
            f"/collective/offers-template/{humanize(offer.id)}/",
        )

        # Then
        assert response.status_code == 201
        template_id = dehumanize_or_raise(response.json["id"])
        template = CollectiveOfferTemplate.query.filter_by(id=template_id).one_or_none()
        assert template is not None
        assert CollectiveOffer.query.filter_by(id=offer.id).one_or_none() is None
        assert template.name == offer.name
        assert template.venueId == offer.venueId
        assert template.priceDetail is None
        assert template.offerVenue == offer.offerVenue
        assert template.bookingEmail == offer.bookingEmail


@pytest.mark.usefixtures("db_session")
class Returns400Test:
    def test_create_collective_offer_template_from_offer_with_stock(self, client):
        # Given
        venue = offerers_factories.VenueFactory()
        offerers_factories.UserOffererFactory(offerer=venue.managingOfferer, user__email="user@example.com")
        stock = educational_factories.CollectiveStockFactory()
        offer = educational_factories.CollectiveOfferFactory(venue=venue, collectiveStock=stock)

        # When
        response = client.with_session_auth(offer.venue.managingOfferer.UserOfferers[0].user.email).post(
            f"/collective/offers-template/{humanize(offer.id)}/",
        )

        # Then
        assert response.status_code == 400
        assert CollectiveOffer.query.filter_by(id=offer.id).one_or_none() is not None


@pytest.mark.usefixtures("db_session")
class Returns403Test:
    def test_create_collective_offer_template_random_user(self, client):
        # Given
        offerers_factories.UserOffererFactory(user__email="azerty@example.com")
        venue = offerers_factories.VenueFactory()
        offerers_factories.UserOffererFactory(offerer=venue.managingOfferer, user__email="user@example.com")
        offer = educational_factories.CollectiveOfferFactory(venue=venue)

        # When
        response = client.with_session_auth("azerty@example.com").post(
            f"/collective/offers-template/{humanize(offer.id)}/",
        )

        # Then
        assert response.status_code == 403
        assert CollectiveOffer.query.filter_by(id=offer.id).one_or_none() is not None


@pytest.mark.usefixtures("db_session")
class Returns404Test:
    def test_create_collective_offer_template_without_collective_offer(self, client):
        # Given
        venue = offerers_factories.VenueFactory()
        offerers_factories.UserOffererFactory(offerer=venue.managingOfferer, user__email="user@example.com")
        offer = educational_factories.CollectiveOfferFactory(venue=venue)

        # When
        response = client.with_session_auth(offer.venue.managingOfferer.UserOfferers[0].user.email).post(
            "/collective/offers-template/P8UET/"
        )

        # Then
        assert response.status_code == 404
        assert CollectiveOffer.query.filter_by(id=offer.id).one_or_none() is not None
