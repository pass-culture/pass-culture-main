import datetime
from unittest.mock import patch
from zoneinfo import ZoneInfo

import pytest
import time_machine

import pcapi.core.highlights.factories as highlights_factories
import pcapi.core.offerers.factories as offerers_factories
import pcapi.core.offers.factories as offers_factories
import pcapi.core.offers.models as offers_models
from pcapi.core.categories import subcategories
from pcapi.core.offerers.schemas import VenueTypeCode
from pcapi.core.testing import assert_num_queries
from pcapi.models import db
from pcapi.models.offer_mixin import OfferStatus
from pcapi.models.offer_mixin import OfferValidationStatus
from pcapi.utils import date as date_utils
from pcapi.utils.date import format_into_utc_date


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


now_datetime_with_tz = datetime.datetime.now(datetime.timezone.utc)


@patch("pcapi.core.search.async_index_offer_ids")
@pytest.mark.usefixtures("db_session")
class Returns200Test:
    num_queries = 1  # 1 session + user
    num_queries += 1  # 2 offerer
    num_queries += 1  # 3 user_offerer
    num_queries += 1  # 4 offer+stock+offererAddress+Address+mediaton+venue
    num_queries += 1  # 5 available stock (date comparison)
    num_queries += 1  # 6 select offer
    num_queries += 1  # 7 offerer_confidence
    num_queries += 1  # 8 offerer_confidence
    num_queries += 1  # 9 offer_validation_rule + offer_validation_sub_rule
    num_queries += 1  # 10 update offer
    num_queries += 1  # 11 artists

    @time_machine.travel(now_datetime_with_tz, tick=False)
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
        highlight = highlights_factories.HighlightFactory()
        highlights_factories.HighlightRequestFactory(offer=stock.offer, highlight=highlight)

        client = client.with_session_auth("user@example.com")
        offer_id = stock.offerId
        with assert_num_queries(self.num_queries):
            response = client.patch("/offers/publish", json={"id": offer_id})

        assert response.status_code == 200
        assert response.json["isActive"] is True
        assert response.json["isNonFreeOffer"] is True

        offer: offers_models.Offer = db.session.get(offers_models.Offer, stock.offer.id)
        assert offer.finalizationDatetime == now_datetime_with_tz
        assert offer.finalizationDatetime == offer.publicationDatetime
        assert not offer.bookingAllowedDatetime
        assert offer.validation == OfferValidationStatus.APPROVED
        assert offer.lastValidationPrice == stock.price
        # TODO(jbaudet, 2025-06): remove check once publicationDate is
        # replaced by publicationDatetime
        assert offer.publicationDate is not None
        assert response.json["isActive"] is True
        assert response.json["isNonFreeOffer"] is True
        mock_async_index_offer_ids.assert_called_once()
        mocked_send_first_venue_approved_offer_email_to_pro.assert_called_once_with(offer)

    @time_machine.travel(now_datetime_with_tz, tick=False)
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
        publication_date = now_datetime_with_tz.replace(minute=0, second=0, microsecond=0) + datetime.timedelta(days=30)
        offer_id = stock.offerId
        with assert_num_queries(self.num_queries):
            response = client.patch(
                "/offers/publish",
                json={
                    "id": offer_id,
                    "publicationDatetime": publication_date.isoformat(),
                },
            )

        assert response.status_code == 200
        assert response.json["isActive"] is False
        assert response.json["isNonFreeOffer"] is True
        assert response.json["publicationDatetime"] == format_into_utc_date(publication_date)

        offer: offers_models.Offer = db.session.get(offers_models.Offer, stock.offer.id)
        assert offer.validation == OfferValidationStatus.APPROVED
        assert offer.lastValidationPrice is None
        assert offer.finalizationDatetime == now_datetime_with_tz
        assert offer.publicationDatetime == publication_date
        assert offer.publicationDate == offer.publicationDatetime
        assert not offer.bookingAllowedDatetime
        mock_async_index_offer_ids.assert_not_called()
        mocked_send_first_venue_approved_offer_email_to_pro.assert_called_once_with(offer)

    @time_machine.travel(now_datetime_with_tz, tick=False)
    @patch("pcapi.core.mails.transactional.send_first_venue_approved_offer_email_to_pro")
    @patch("pcapi.core.offers.api.rule_flags_offer", return_value=False)
    def test_publish_offer_in_future(
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
        publication_date = datetime.datetime.now(tz=ZoneInfo("Europe/Paris")).replace(
            minute=0, second=0, microsecond=0
        ) + datetime.timedelta(days=30)
        offer_id = stock.offerId

        with assert_num_queries(self.num_queries):
            response = client.patch(
                "/offers/publish",
                json={
                    "id": offer_id,
                    "publicationDatetime": publication_date.isoformat(),
                },
            )

        expected_publication_date = publication_date.astimezone(datetime.UTC)
        assert response.status_code == 200
        assert response.json["publicationDatetime"] == format_into_utc_date(publication_date)
        assert response.json["status"] == OfferStatus.SCHEDULED.name
        assert response.json["isActive"] is False
        assert response.json["isNonFreeOffer"] is True

        offer: offers_models.Offer = db.session.get(offers_models.Offer, stock.offer.id)
        assert offer.validation == OfferValidationStatus.APPROVED
        assert offer.lastValidationPrice is None
        assert offer.finalizationDatetime == now_datetime_with_tz
        assert offer.publicationDatetime == expected_publication_date
        assert not offer.bookingAllowedDatetime
        assert response.json["isActive"] is False
        assert response.json["isNonFreeOffer"] is True
        mock_async_index_offer_ids.assert_not_called()
        mocked_send_first_venue_approved_offer_email_to_pro.assert_called_once_with(offer)

    @time_machine.travel(now_datetime_with_tz, tick=False)
    @patch("pcapi.core.mails.transactional.send_first_venue_approved_offer_email_to_pro")
    @patch("pcapi.core.offers.api.rule_flags_offer", return_value=False)
    def test_publish_now_but_bookable_in_future(
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
        booking_allowed_datetime = datetime.datetime.now(datetime.timezone.utc).replace(
            minute=0, second=0, microsecond=0
        ) + datetime.timedelta(days=30)
        offer_id = stock.offerId

        with assert_num_queries(self.num_queries):
            response = client.patch(
                "/offers/publish",
                json={
                    "id": offer_id,
                    "bookingAllowedDatetime": booking_allowed_datetime.isoformat(),
                },
            )

        expected_booking_allowed_datetime = booking_allowed_datetime
        assert response.status_code == 200
        assert response.json["bookingAllowedDatetime"] == format_into_utc_date(booking_allowed_datetime)
        assert response.json["status"] == OfferStatus.PUBLISHED.name
        assert response.json["isActive"] is True
        assert response.json["isNonFreeOffer"] is True

        offer: offers_models.Offer = db.session.get(offers_models.Offer, stock.offer.id)
        assert offer.validation == OfferValidationStatus.APPROVED
        assert offer.lastValidationPrice is None
        assert offer.finalizationDatetime == now_datetime_with_tz
        assert offer.publicationDatetime == offer.finalizationDatetime
        assert offer.bookingAllowedDatetime == expected_booking_allowed_datetime
        mock_async_index_offer_ids.assert_called_once()
        mocked_send_first_venue_approved_offer_email_to_pro.assert_called_once_with(offer)

    @time_machine.travel(now_datetime_with_tz, tick=False)
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
        publication_date = datetime.datetime.now(datetime.timezone.utc).replace(
            minute=0, second=0, microsecond=0
        ) + datetime.timedelta(days=30)
        booking_allowed_datetime = datetime.datetime.now(datetime.timezone.utc).replace(
            minute=0, second=0, microsecond=0
        ) + datetime.timedelta(days=31)
        offer_id = stock.offerId

        with assert_num_queries(self.num_queries):
            response = client.patch(
                "/offers/publish",
                json={
                    "id": offer_id,
                    "publicationDatetime": format_into_utc_date(publication_date),
                    "bookingAllowedDatetime": format_into_utc_date(booking_allowed_datetime),
                },
            )

        expected_publication_datetime = publication_date

        assert response.status_code == 200
        offer = db.session.get(offers_models.Offer, stock.offer.id)
        assert offer.publicationDate == expected_publication_datetime
        assert offer.publicationDatetime == expected_publication_datetime
        assert offer.bookingAllowedDatetime == booking_allowed_datetime
        assert offer.finalizationDatetime == now_datetime_with_tz
        first_finalization_datetime = offer.finalizationDatetime
        mock_async_index_offer_ids.assert_not_called()
        mocked_send_first_venue_approved_offer_email_to_pro.assert_called_once_with(offer)

        response = client.patch("/offers/publish", json={"id": stock.offerId})

        assert response.status_code == 200
        assert response.json["isActive"] is True

        offer = db.session.get(offers_models.Offer, stock.offer.id)
        assert offer.finalizationDatetime == first_finalization_datetime
        assert offer.finalizationDatetime <= offer.publicationDatetime
        assert response.json["isActive"] is True
        mock_async_index_offer_ids.assert_called_once()


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
        offer = db.session.get(offers_models.Offer, offer.id)
        assert offer.validation == OfferValidationStatus.DRAFT

    def test_patch_publish_offer_with_non_bookable_stock(
        self,
        client,
    ):
        stock = offers_factories.StockFactory(
            offer__isActive=False,
            offer__validation=OfferValidationStatus.DRAFT,
            beginningDatetime=date_utils.get_naive_utc_now() - datetime.timedelta(days=1),
        )
        offerers_factories.UserOffererFactory(
            user__email="user@example.com",
            offerer=stock.offer.venue.managingOfferer,
        )

        client = client.with_session_auth("user@example.com")
        response = client.patch("/offers/publish", json={"id": stock.offerId})

        assert response.status_code == 400
        assert response.json["offer"] == "Cette offre n’a pas de stock réservable"
        offer = db.session.get(offers_models.Offer, stock.offerId)
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
        publication_date = date_utils.get_naive_utc_now().replace(minute=0, second=0) - datetime.timedelta(days=30)
        response = client.patch(
            "/offers/publish",
            json={
                "id": stock.offerId,
                "publicationDatetime": format_into_utc_date(publication_date),
            },
        )

        assert response.status_code == 400
        assert response.json["publicationDatetime"] == ["The datetime must be in the future."]
        offer = db.session.get(offers_models.Offer, stock.offerId)
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
            "ean": ["Une offre avec cet EAN existe déjà. Vous pouvez la retrouver dans l'onglet Offres."]
        }
