import datetime
from unittest.mock import patch

import pytest

from pcapi.core.categories import subcategories
import pcapi.core.offerers.factories as offerers_factories
from pcapi.core.offerers.schemas import VenueTypeCode
import pcapi.core.offers.factories as offers_factories
import pcapi.core.offers.models as offers_models
from pcapi.core.testing import assert_num_queries
from pcapi.models import db
from pcapi.models.offer_mixin import OfferValidationStatus
from pcapi.utils.date import local_datetime_to_default_timezone


@pytest.mark.usefixtures("db_session")
class Returns404Test:
    def test_patch_publish_offer_unaccessible(self, client):
        stock = offers_factories.StockFactory()
        offerers_factories.UserOffererFactory(
            user__email="user@example.com",
            offerer=stock.offer.venue.managingOfferer,
        )
        other_stock = offers_factories.StockFactory()

        response = client.with_session_auth("user@example.com").patch(
            "/offers/publish", json={"id": other_stock.offer.id}
        )
        assert response.status_code == 403


@patch("pcapi.core.search.async_index_offer_ids")
@pytest.mark.usefixtures("db_session")
class Returns200Test:
    num_queries = 1  # 1 session
    num_queries += 1  # 2 user
    num_queries += 1  # 3 offer
    num_queries += 1  # 4 user_offerer
    num_queries += 1  # 5 offer+stock+offererAddress+Address+mediaton+venue
    num_queries += 1  # 6 available stock (date comparison)
    num_queries += 1  # 7 validation status
    num_queries += 1  # 8 offerer_confidence
    num_queries += 1  # 9 offerer_confidenc
    num_queries += 1  # 10 offer_validation_rule + offer_validation_sub_rule
    num_queries += 1  # 11 future_offer
    num_queries += 1  # 12 update offer

    @patch("pcapi.core.mails.transactional.send_first_venue_approved_offer_email_to_pro")
    @patch("pcapi.core.offers.api.rule_flags_offer", return_value=False)
    def test_patch_publish_offer(
        self,
        mock_rule_flags_offer,
        mocked_send_first_venue_approved_offer_email_to_pro,
        mock_async_index_offer_ids,
        client,
    ):
        stock = offers_factories.StockFactory(offer__isActive=False, offer__validation=OfferValidationStatus.DRAFT)
        offerers_factories.UserOffererFactory(
            user__email="user@example.com",
            offerer=stock.offer.venue.managingOfferer,
        )

        client = client.with_session_auth("user@example.com")
        offer_id = stock.offerId
        with assert_num_queries(self.num_queries):
            response = client.patch("/offers/publish", json={"id": offer_id})

        assert response.status_code == 200
        content = response.json
        offer = db.session.query(offers_models.Offer).get(stock.offer.id)
        assert offer.validation == OfferValidationStatus.APPROVED
        assert offer.lastValidationPrice == stock.price
        assert offer.publicationDate is None
        assert not offer.futureOffer
        assert content["isActive"] is True
        assert content["isNonFreeOffer"] is True
        mock_async_index_offer_ids.assert_called_once()
        mocked_send_first_venue_approved_offer_email_to_pro.assert_called_once_with(offer)

    @patch("pcapi.core.mails.transactional.send_first_venue_approved_offer_email_to_pro")
    @patch("pcapi.core.offers.api.rule_flags_offer", return_value=False)
    def test_patch_publish_future_offer(
        self,
        mock_rule_flags_offer,
        mocked_send_first_venue_approved_offer_email_to_pro,
        mock_async_index_offer_ids,
        client,
    ):
        stock = offers_factories.StockFactory(
            offer__isActive=False,
            offer__validation=OfferValidationStatus.DRAFT,
            offer__subcategoryId=subcategories.SEANCE_CINE.id,
        )
        offerers_factories.UserOffererFactory(
            user__email="user@example.com",
            offerer=stock.offer.venue.managingOfferer,
        )

        client = client.with_session_auth("user@example.com")
        publication_date = datetime.datetime.utcnow().replace(minute=0, second=0) + datetime.timedelta(days=30)
        offer_id = stock.offerId
        # +1 insert into future_offer
        with assert_num_queries(self.num_queries + 1):
            response = client.patch(
                "/offers/publish",
                json={
                    "id": offer_id,
                    "publicationDate": publication_date.isoformat(),
                },
            )

        assert response.status_code == 200
        content = response.json
        offer = db.session.query(offers_models.Offer).get(stock.offer.id)
        assert offer.validation == OfferValidationStatus.APPROVED
        assert offer.lastValidationPrice is None
        assert offer.publicationDate == local_datetime_to_default_timezone(publication_date, "Europe/Paris").replace(
            microsecond=0, tzinfo=None
        )
        assert offer.futureOffer.isWaitingForPublication
        assert content["isActive"] is False
        assert content["isNonFreeOffer"] is True
        mock_async_index_offer_ids.assert_not_called()
        mocked_send_first_venue_approved_offer_email_to_pro.assert_called_once_with(offer)

    @patch("pcapi.core.mails.transactional.send_first_venue_approved_offer_email_to_pro")
    def test_patch_publish_future_offer_early_publish(
        self,
        mocked_send_first_venue_approved_offer_email_to_pro,
        mock_async_index_offer_ids,
        client,
    ):
        stock = offers_factories.StockFactory(
            offer__isActive=False,
            offer__validation=OfferValidationStatus.DRAFT,
            offer__subcategoryId=subcategories.SEANCE_CINE.id,
        )
        offerers_factories.UserOffererFactory(
            user__email="user@example.com",
            offerer=stock.offer.venue.managingOfferer,
        )

        client = client.with_session_auth("user@example.com")
        publication_date = datetime.datetime.utcnow().replace(minute=0, second=0) + datetime.timedelta(days=30)
        offer_id = stock.offerId
        # +1 insert into future_offer
        with assert_num_queries(self.num_queries + 1):
            response = client.patch(
                "/offers/publish",
                json={
                    "id": offer_id,
                    "publicationDate": publication_date.isoformat(),
                },
            )

        assert response.status_code == 200
        offer = db.session.query(offers_models.Offer).get(stock.offer.id)
        assert offer.publicationDate == local_datetime_to_default_timezone(publication_date, "Europe/Paris").replace(
            microsecond=0, tzinfo=None
        )
        mock_async_index_offer_ids.assert_not_called()
        mocked_send_first_venue_approved_offer_email_to_pro.assert_called_once_with(offer)
        assert db.session.query(offers_models.FutureOffer).count() == 1

        response = client.patch("/offers/publish", json={"id": stock.offerId})

        assert response.status_code == 200
        content = response.json
        offer = db.session.query(offers_models.Offer).get(stock.offer.id)
        assert offer.publicationDate is None
        assert content["isActive"] is True
        mock_async_index_offer_ids.assert_called_once()
        assert db.session.query(offers_models.FutureOffer).count() == 0


@pytest.mark.usefixtures("db_session")
class Returns400Test:
    def test_patch_publish_offer(
        self,
        client,
    ):
        offer = offers_factories.OfferFactory(isActive=False, validation=OfferValidationStatus.DRAFT)
        offerers_factories.UserOffererFactory(
            user__email="user@example.com",
            offerer=offer.venue.managingOfferer,
        )

        client = client.with_session_auth("user@example.com")
        response = client.patch("/offers/publish", json={"id": offer.id})

        assert response.status_code == 400
        assert response.json["offer"] == "Cette offre n’a pas de stock réservable"
        offer = db.session.query(offers_models.Offer).get(offer.id)
        assert offer.validation == OfferValidationStatus.DRAFT

    def test_patch_publish_offer_with_non_bookable_stock(
        self,
        client,
    ):
        stock = offers_factories.StockFactory(
            offer__isActive=False,
            offer__validation=OfferValidationStatus.DRAFT,
            beginningDatetime=datetime.datetime.utcnow() - datetime.timedelta(days=1),
        )
        offerers_factories.UserOffererFactory(
            user__email="user@example.com",
            offerer=stock.offer.venue.managingOfferer,
        )

        client = client.with_session_auth("user@example.com")
        response = client.patch("/offers/publish", json={"id": stock.offerId})

        assert response.status_code == 400
        assert response.json["offer"] == "Cette offre n’a pas de stock réservable"
        offer = db.session.query(offers_models.Offer).get(stock.offerId)
        assert offer.validation == OfferValidationStatus.DRAFT

    def test_patch_publish_future_offer(
        self,
        client,
    ):
        stock = offers_factories.StockFactory(
            offer__isActive=False,
            offer__validation=OfferValidationStatus.DRAFT,
            offer__subcategoryId=subcategories.SEANCE_CINE.id,
        )
        offerers_factories.UserOffererFactory(
            user__email="user@example.com",
            offerer=stock.offer.venue.managingOfferer,
        )

        client = client.with_session_auth("user@example.com")
        publication_date = datetime.datetime.utcnow().replace(minute=0, second=0) - datetime.timedelta(days=30)
        response = client.patch(
            "/offers/publish",
            json={
                "id": stock.offerId,
                "publicationDate": publication_date.isoformat(),
            },
        )

        assert response.status_code == 400
        assert response.json["publication_date"] == ["Impossible de sélectionner une date de publication dans le passé"]
        offer = db.session.query(offers_models.Offer).get(stock.offerId)
        assert offer.validation == OfferValidationStatus.DRAFT

    def test_cannot_publish_offer_if_ean_is_already_used(
        self,
        client,
    ):
        ean = "0000000000001"
        email = "user@example.com"

        user_offerer = offerers_factories.UserOffererFactory(user__email=email)
        venue = offerers_factories.VenueFactory(
            managingOfferer=user_offerer.offerer, venueTypeCode=VenueTypeCode.RECORD_STORE
        )

        product = offers_factories.ProductFactory(subcategoryId=subcategories.LIVRE_PAPIER.id, ean=ean)
        offers_factories.OfferFactory(
            subcategoryId=subcategories.LIVRE_PAPIER.id,
            venue=venue,
            product=product,
            validation=OfferValidationStatus.APPROVED,
            ean=ean,
        )

        offer = offers_factories.StockFactory(
            offer__venue=venue,
            offer__isActive=False,
            offer__validation=OfferValidationStatus.DRAFT,
            offer__product=product,
            offer__ean=ean,
        ).offer

        client = client.with_session_auth(email)
        response = client.patch("/offers/publish", json={"id": offer.id})

        assert response.status_code == 400
        assert response.json == {
            "ean": ["Une offre avec cet EAN existe déjà. Vous pouvez la retrouver dans l’onglet Offres."]
        }
