import pytest
import time_machine

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
    @time_machine.travel("2026-03-03 12:00:00", tick=False)
    def test_create_pro_advice(self, caplog):
        offer = offers_factories.OfferFactory(validation=OfferValidationStatus.APPROVED)
        user = users_factories.UserFactory()

        with caplog.at_level("INFO"):
            api.create_pro_advice(offer, "Une super reco.", "Le libraire du coin", user)

        pro_advice = db.session.query(models.ProAdvice).one()
        assert pro_advice.offerId == offer.id
        assert pro_advice.content == "Une super reco."
        assert pro_advice.author == "Le libraire du coin"
        assert pro_advice.updatedAt == date_utils.get_naive_utc_now()

        assert len(caplog.records) == 1
        assert caplog.records[0].technical_message_id == "pro_advice.created"
        assert caplog.records[0].extra == {
            "offer_id": offer.id,
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
        offers_factories.ProAdviceFactory(offer=offer)
        user = users_factories.UserFactory()

        with pytest.raises(ProAdviceException) as exception:
            api.create_pro_advice(offer, "Une autre reco.", None, user)

        assert exception.value.errors["global"] == ["Une recommandation existe déjà pour cette offre"]


class UpdateProAdviceTest:
    @time_machine.travel("2026-03-03 12:00:00", tick=False)
    def test_update_pro_advice(self, caplog):
        offer = offers_factories.OfferFactory(validation=OfferValidationStatus.APPROVED)
        offers_factories.ProAdviceFactory(
            offer=offer,
            content="Ancien conseil.",
            author="Ancien auteur",
        )
        user = users_factories.UserFactory()

        with caplog.at_level("INFO"):
            api.update_pro_advice(offer, "Nouveau conseil.", "Nouvel auteur", user)

        pro_advice = db.session.query(models.ProAdvice).one()
        assert pro_advice.offerId == offer.id
        assert pro_advice.content == "Nouveau conseil."
        assert pro_advice.author == "Nouvel auteur"
        assert pro_advice.updatedAt == date_utils.get_naive_utc_now()

        assert len(caplog.records) == 1
        assert caplog.records[0].technical_message_id == "pro_advice.updated"
        assert caplog.records[0].extra == {
            "offer_id": offer.id,
            "user_id": user.id,
        }

    @pytest.mark.parametrize(
        "validation_status",
        [OfferValidationStatus.DRAFT, OfferValidationStatus.PENDING, OfferValidationStatus.REJECTED],
    )
    def test_raises_if_offer_is_not_approved(self, validation_status):
        user = users_factories.UserFactory()

        offer = offers_factories.OfferFactory(validation=validation_status)
        offers_factories.ProAdviceFactory(offer=offer)
        with pytest.raises(ProAdviceException) as exception:
            api.update_pro_advice(offer, "Conseil.", None, user)

        assert exception.value.errors["global"] == ["Impossible de modifier une recommandation sur cette offre"]

    def test_raises_if_pro_advice_does_not_exist(self):
        offer = offers_factories.OfferFactory(validation=OfferValidationStatus.APPROVED)
        user = users_factories.UserFactory()

        with pytest.raises(ProAdviceException) as exception:
            api.update_pro_advice(offer, "Conseil.", None, user)

        assert exception.value.errors["global"] == ["Aucune recommandation n'existe pour cette offre"]


class DeleteProAdviceTest:
    def test_delete_pro_advice(self, caplog):
        offer = offers_factories.OfferFactory(validation=OfferValidationStatus.APPROVED)
        offers_factories.ProAdviceFactory(offer=offer)
        user = users_factories.UserFactory()

        with caplog.at_level("INFO"):
            api.delete_pro_advice(offer, user)

        assert db.session.query(models.ProAdvice).count() == 0

        assert len(caplog.records) == 1
        assert caplog.records[0].technical_message_id == "pro_advice.deleted"
        assert caplog.records[0].extra == {
            "offer_id": offer.id,
            "user_id": user.id,
        }

    def test_raises_if_pro_advice_does_not_exist(self):
        offer = offers_factories.OfferFactory(validation=OfferValidationStatus.APPROVED)
        user = users_factories.UserFactory()

        with pytest.raises(ProAdviceException) as exception:
            api.delete_pro_advice(offer, user)

        assert exception.value.errors["global"] == ["Aucune recommandation n'existe pour cette offre"]
