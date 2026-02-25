import pytest

import pcapi.core.offers.factories as offers_factories
import pcapi.core.offers.models as models
import pcapi.core.users.factories as users_factories
import pcapi.utils.date as date_utils
from pcapi.core.pro_advice import api
from pcapi.core.pro_advice.exceptions import ProAdviceException
from pcapi.models import db
from pcapi.models.offer_mixin import OfferValidationStatus


pytestmark = pytest.mark.usefixtures("db_session")


class CreateProAdviceTest:
    def test_create_pro_advice(self, caplog):
        offer = offers_factories.OfferFactory(validation=OfferValidationStatus.APPROVED)
        user = users_factories.UserFactory()

        with caplog.at_level("INFO"):
            api.create_pro_advice(offer, "Une super reco.", "Le libraire du coin", user)

        pro_advice = db.session.query(models.ProAdvice).one()
        assert pro_advice.offerId == offer.id
        assert pro_advice.venueId == offer.venueId
        assert pro_advice.content == "Une super reco."
        assert pro_advice.author == "Le libraire du coin"
        assert pro_advice.updatedAt == date_utils.get_naive_utc_now().date()

        assert len(caplog.records) == 1
        assert caplog.records[0].technical_message_id == "pro_advice.created"
        assert caplog.records[0].extra == {
            "offer_id": offer.id,
            "venue_id": offer.venueId,
            "user_id": user.id,
        }

    @pytest.mark.parametrize(
        "validation_status",
        [OfferValidationStatus.DRAFT, OfferValidationStatus.PENDING, OfferValidationStatus.REJECTED],
    )
    def test_raises_if_offer_is_not_approved(self, validation_status):
        user = users_factories.UserFactory()

        offer = offers_factories.OfferFactory(validation=validation_status)
        with pytest.raises(ProAdviceException) as exception:
            api.create_pro_advice(offer, "Une super reco.", None, user)

        assert exception.value.errors["global"] == ["Impossible de créer une recommandation sur cette offre"]

    def test_raises_if_pro_advice_already_exists(self):
        offer = offers_factories.OfferFactory(validation=OfferValidationStatus.APPROVED)
        offers_factories.ProAdviceFactory(offer=offer, venue=offer.venue)
        user = users_factories.UserFactory()

        with pytest.raises(ProAdviceException) as exception:
            api.create_pro_advice(offer, "Une autre reco.", None, user)

        assert exception.value.errors["global"] == ["Une recommandation existe déjà pour cette offre"]

    def test_logs_creation(self, caplog):
        offer = offers_factories.OfferFactory(validation=OfferValidationStatus.APPROVED)
        user = users_factories.UserFactory()

        with caplog.at_level("INFO"):
            api.create_pro_advice(offer, "Un conseil.", None, user)

        assert caplog.records[0].technical_message_id == "pro_advice.created"
