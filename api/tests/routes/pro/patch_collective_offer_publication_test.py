import pytest

from pcapi.core.educational import factories as educational_factories
from pcapi.core.educational import models as educational_models
from pcapi.core.offerers import factories as offerers_factories
from pcapi.core.offers import factories as offers_factories
from pcapi.core.offers import models as offers_models
from pcapi.models.offer_mixin import OfferStatus
from pcapi.models.offer_mixin import OfferValidationStatus


@pytest.mark.usefixtures("db_session")
class Returns204Test:
    def expect_offer_to_be_approved(self, client):
        stock = educational_factories.CollectiveStockFactory(price=0)
        offer = educational_factories.CollectiveOfferFactory(
            collectiveStock=stock, validation=OfferValidationStatus.DRAFT
        )
        user_offerer = offerers_factories.UserOffererFactory(offerer=offer.venue.managingOfferer)

        url = f"/collective/offers/{offer.id}/publish"

        response = client.with_session_auth(user_offerer.user.email).patch(url)

        assert response.status_code == 200
        assert response.json["status"] == OfferStatus.ACTIVE.value
        assert response.json["isActive"] is True
        assert response.json["isNonFreeOffer"] is False

        offer = educational_models.CollectiveOffer.query.filter_by(id=offer.id).one()
        assert not offer.lastValidationAuthor

    def expect_offer_to_be_pending(self, client):
        stock = educational_factories.CollectiveStockFactory()
        offer = educational_factories.CollectiveOfferFactory(
            name="suspicious", collectiveStock=stock, validation=OfferValidationStatus.DRAFT
        )
        user_offerer = offerers_factories.UserOffererFactory(offerer=offer.venue.managingOfferer)

        url = f"/collective/offers/{offer.id}/publish"

        offer_name_rule = offers_factories.OfferValidationRuleFactory(name="Règle sur les noms d'offres")
        offers_factories.OfferValidationSubRuleFactory(
            validationRule=offer_name_rule,
            model=offers_models.OfferValidationModel.COLLECTIVE_OFFER,
            attribute=offers_models.OfferValidationAttribute.NAME,
            operator=offers_models.OfferValidationRuleOperator.CONTAINS,
            comparated={"comparated": ["suspicious"]},
        )
        response = client.with_session_auth(user_offerer.user.email).patch(url)

        assert response.status_code == 200
        assert response.json["status"] == OfferStatus.PENDING.value
        assert response.json["isActive"] is False
        assert response.json["isNonFreeOffer"] is True

        offer = educational_models.CollectiveOffer.query.filter_by(id=offer.id).one()
        assert not offer.lastValidationAuthor


@pytest.mark.usefixtures("db_session")
class Returns403Test:
    def expect_offer_to_be_approved(self, client):
        offer = educational_factories.CollectiveOfferFactory(validation=OfferValidationStatus.DRAFT)
        user_offerer = offerers_factories.UserOffererFactory()

        url = f"/collective/offers/{offer.id}/publish"

        response = client.with_session_auth(user_offerer.user.email).patch(url)

        assert response.status_code == 403
        offer = educational_models.CollectiveOffer.query.filter_by(id=offer.id).one()
        assert offer.validation == OfferValidationStatus.DRAFT
        assert not offer.lastValidationAuthor


@pytest.mark.usefixtures("db_session")
class Returns401Test:
    def expect_offer_to_be_approved(self, client):
        offer = educational_factories.CollectiveOfferFactory(validation=OfferValidationStatus.DRAFT)

        url = f"/collective/offers/{offer.id}/publish"

        response = client.patch(url)

        assert response.status_code == 401
        offer = educational_models.CollectiveOffer.query.filter_by(id=offer.id).one()
        assert offer.validation == OfferValidationStatus.DRAFT
        assert not offer.lastValidationAuthor
