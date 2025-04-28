import pytest

import pcapi.core.offerers.factories as offerers_factories
import pcapi.core.offers.factories as offers_factories
import pcapi.core.offers.models as offer_models
import pcapi.core.users.factories as users_factory
from pcapi.models import db
from pcapi.models.offer_mixin import OfferValidationStatus


pytestmark = pytest.mark.usefixtures("db_session")


class Returns204Test:
    def test_delete_draft(self, client):
        pro = users_factory.ProFactory()
        draft_offer = offers_factories.OfferFactory(validation=OfferValidationStatus.DRAFT)
        validated_offer = offers_factories.OfferFactory(
            validation=OfferValidationStatus.APPROVED, venue=draft_offer.venue
        )
        offerers_factories.UserOffererFactory(user=pro, offerer=draft_offer.venue.managingOfferer)
        data = {"ids": [draft_offer.id, validated_offer.id]}

        response = client.with_session_auth(pro.email).post("/offers/delete-draft", json=data)

        assert response.status_code == 204

        assert db.session.query(offer_models.Offer).one() == validated_offer

    def test_delete_unaccessible_draft(self, client):
        pro = users_factory.ProFactory()
        draft_offer = offers_factories.OfferFactory(validation=OfferValidationStatus.DRAFT)
        offerers_factories.UserOffererFactory(offerer=draft_offer.venue.managingOfferer)
        data = {"ids": [draft_offer.id]}

        response = client.with_session_auth(pro.email).post("/offers/delete-draft", json=data)

        assert response.status_code == 204

        assert db.session.query(offer_models.Offer).count() == 1


class Returns401Test:
    def test_delete_not_connected_draft(self, client):
        pro = users_factory.ProFactory()
        draft_offer = offers_factories.OfferFactory(validation=OfferValidationStatus.DRAFT)
        offerers_factories.UserOffererFactory(user=pro, offerer=draft_offer.venue.managingOfferer)
        data = {"ids": [draft_offer.id]}

        response = client.post("/offers/delete-draft", json=data)

        assert response.status_code == 401

        assert db.session.query(offer_models.Offer).count() == 1
