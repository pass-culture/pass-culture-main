import datetime

import pytest

import pcapi.core.offerers.factories as offerers_factories
from pcapi.core.offers import models as offers_models
import pcapi.core.offers.factories as offers_factories
import pcapi.core.users.factories as users_factories


pytestmark = pytest.mark.usefixtures("db_session")


class Returns200Test:
    def test_make_offer_headline(self, client):
        pro_user = users_factories.ProFactory()
        venue = offerers_factories.VenueFactory(isPermanent=True)
        offerers_factories.UserOffererFactory(user=pro_user, offerer=venue.managingOfferer)
        offer = offers_factories.OfferFactory(venue=venue)
        offers_factories.StockFactory(offer=offer)
        offers_factories.MediationFactory(offer=offer)

        data = {
            "offerId": offer.id,
        }
        client = client.with_session_auth(pro_user.email)
        response = client.post("/offers/upsert_headline", json=data)

        assert response.status_code == 204
        assert offer.is_headline_offer
        assert offers_models.HeadlineOffer.query.one()

    def test_make_new_offer_headline(self, client):
        pro_user = users_factories.ProFactory()
        venue = offerers_factories.VenueFactory(isPermanent=True)
        offerers_factories.UserOffererFactory(user=pro_user, offerer=venue.managingOfferer)
        offer = offers_factories.OfferFactory(venue=venue)
        offers_factories.HeadlineOfferFactory(
            offer=offer,
            timespan=(
                datetime.datetime.utcnow() - datetime.timedelta(days=20),
                datetime.datetime.utcnow() - datetime.timedelta(days=10),
            ),
            create_mediation=True,
        )
        assert not offer.is_headline_offer

        data = {
            "offerId": offer.id,
        }
        client = client.with_session_auth(pro_user.email)
        response = client.post("/offers/upsert_headline", json=data)

        assert response.status_code == 204
        assert offer.is_headline_offer
        assert offers_models.HeadlineOffer.query.count() == 2

    def test_make_another_offer_headline(self, client):
        pro_user = users_factories.ProFactory()
        venue = offerers_factories.VenueFactory(isPermanent=True)
        offerers_factories.UserOffererFactory(user=pro_user, offerer=venue.managingOfferer)
        offer = offers_factories.OfferFactory(venue=venue)
        another_offer = offers_factories.OfferFactory(venue=venue)
        offers_factories.StockFactory(offer=another_offer)
        offers_factories.MediationFactory(offer=another_offer)
        offers_factories.HeadlineOfferFactory(offer=offer, create_mediation=True)

        data = {
            "offerId": another_offer.id,
        }
        client = client.with_session_auth(pro_user.email)
        response = client.post("/offers/upsert_headline", json=data)

        assert response.status_code == 204

        assert not offer.is_headline_offer
        assert another_offer.is_headline_offer
        assert offers_models.HeadlineOffer.query.count() == 2

    def test_make_another_offer_headline_when_first_offer_is_not_active_anymore(self, client):
        pro_user = users_factories.ProFactory()
        venue = offerers_factories.VenueFactory(isPermanent=True)
        offerers_factories.UserOffererFactory(user=pro_user, offerer=venue.managingOfferer)
        offer = offers_factories.OfferFactory(venue=venue, isActive=False)
        another_offer = offers_factories.OfferFactory(venue=venue)
        offers_factories.StockFactory(offer=another_offer)
        offers_factories.MediationFactory(offer=another_offer)
        offers_factories.HeadlineOfferFactory(offer=offer, create_mediation=True)

        data = {
            "offerId": another_offer.id,
        }
        client = client.with_session_auth(pro_user.email)
        response = client.post("/offers/upsert_headline", json=data)

        assert response.status_code == 204

        assert not offer.is_headline_offer
        assert another_offer.is_headline_offer
        assert offers_models.HeadlineOffer.query.count() == 2


class Returns400Test:
    def test_make_several_headline_offers_should_fail(self, client):
        pro_user = users_factories.ProFactory()
        venue = offerers_factories.VenueFactory(isPermanent=True)
        offerers_factories.UserOffererFactory(user=pro_user, offerer=venue.managingOfferer)
        offer = offers_factories.OfferFactory(venue=venue)
        offers_factories.HeadlineOfferFactory(offer=offer, create_mediation=True)

        data = {
            "offerId": offer.id,
        }
        client = client.with_session_auth(pro_user.email)
        response = client.post("/offers/upsert_headline", json=data)

        assert response.status_code == 400
        assert response.json["global"] == ["Cette offre est déjà mise à la une"]

        assert offer.is_headline_offer
        assert offers_models.HeadlineOffer.query.one()

    def test_make_inactive_offer_headline_should_fail(self, client):
        pro_user = users_factories.ProFactory()
        venue = offerers_factories.VenueFactory(isPermanent=True)
        offerers_factories.UserOffererFactory(user=pro_user, offerer=venue.managingOfferer)
        offer = offers_factories.OfferFactory(venue=venue, isActive=False)
        offers_factories.StockFactory(offer=offer)
        offers_factories.MediationFactory(offer=offer)

        data = {
            "offerId": offer.id,
        }
        client = client.with_session_auth(pro_user.email)
        response = client.post("/offers/upsert_headline", json=data)

        assert response.status_code == 400
        assert response.json["global"] == ["Cette offre est inactive et ne peut pas être mise à la une"]

        assert not offer.is_headline_offer
        assert offers_models.HeadlineOffer.query.count() == 0

    def test_ineligible_offerer_can_not_create_headline_offer(self, client):
        pro_user = users_factories.ProFactory()
        offerer = offerers_factories.OffererFactory()
        offerers_factories.UserOffererFactory(user=pro_user, offerer=offerer)
        venue = offerers_factories.VenueFactory(isPermanent=True, managingOfferer=offerer)
        offerers_factories.VenueFactory(isPermanent=False, managingOfferer=offerer)
        offer = offers_factories.OfferFactory(venue=venue)
        offers_factories.StockFactory(offer=offer)
        offers_factories.MediationFactory(offer=offer)

        data = {
            "offerId": offer.id,
        }
        client = client.with_session_auth(pro_user.email)
        response = client.post("/offers/upsert_headline", json=data)

        assert response.status_code == 400
        assert response.json["global"] == [
            "Vous ne pouvez pas créer d'offre à la une sur une entité juridique possédant plusieurs structures"
        ]

        assert not offer.is_headline_offer
        assert offers_models.HeadlineOffer.query.count() == 0

    def test_virtual_offer_can_not_be_headline(self, client):
        pro_user = users_factories.ProFactory()
        offerer = offerers_factories.OffererFactory()
        offerers_factories.UserOffererFactory(user=pro_user, offerer=offerer)
        venue = offerers_factories.VenueFactory(isPermanent=True, managingOfferer=offerer)
        offer = offers_factories.DigitalOfferFactory(venue=venue)
        offers_factories.StockFactory(offer=offer)
        offers_factories.MediationFactory(offer=offer)

        data = {
            "offerId": offer.id,
        }
        client = client.with_session_auth(pro_user.email)
        response = client.post("/offers/upsert_headline", json=data)

        assert response.status_code == 400
        assert response.json["global"] == ["Une offre virtuelle ne peut pas être mise à la une"]

        assert not offer.is_headline_offer
        assert offers_models.HeadlineOffer.query.count() == 0

    def test_offer_without_image_can_not_be_headline(self, client):
        pro_user = users_factories.ProFactory()
        offerer = offerers_factories.OffererFactory()
        offerers_factories.UserOffererFactory(user=pro_user, offerer=offerer)
        venue = offerers_factories.VenueFactory(isPermanent=True, managingOfferer=offerer)
        offer = offers_factories.OfferFactory(venue=venue)
        offers_factories.StockFactory(offer=offer)

        assert not offer.images

        data = {
            "offerId": offer.id,
        }
        client = client.with_session_auth(pro_user.email)
        response = client.post("/offers/upsert_headline", json=data)

        assert response.status_code == 400
        assert response.json["global"] == ["Une offre doit avoir une image pour être mise à la une"]
