import copy
import dataclasses
from datetime import datetime
from datetime import timedelta
import logging
import os
import pathlib
from unittest import mock

from freezegun import freeze_time
import pytest

import pcapi.core.bookings.factories as bookings_factories
import pcapi.core.bookings.models as bookings_models
from pcapi.core.categories import subcategories
import pcapi.core.criteria.factories as criteria_factories
import pcapi.core.mails.testing as mails_testing
from pcapi.core.mails.transactional.sendinblue_template_ids import TransactionalEmail
import pcapi.core.offerers.factories as offerers_factories
from pcapi.core.offers import api
from pcapi.core.offers import exceptions
from pcapi.core.offers import factories
from pcapi.core.offers import models
from pcapi.core.offers import offer_validation
import pcapi.core.payments.factories as payments_factories
import pcapi.core.providers.factories as providers_factories
from pcapi.core.testing import override_features
from pcapi.core.testing import override_settings
import pcapi.core.users.factories as users_factories
import pcapi.core.users.models as users_models
from pcapi.models import api_errors
from pcapi.models.offer_mixin import OfferValidationStatus
from pcapi.models.offer_mixin import OfferValidationType
from pcapi.notifications.push import testing as push_testing
from pcapi.routes.serialization import offers_serialize
from pcapi.routes.serialization import stock_serialize
from pcapi.utils.human_ids import humanize

import tests


pytestmark = pytest.mark.usefixtures("db_session")
IMAGES_DIR = pathlib.Path(tests.__path__[0]) / "files"


SIMPLE_OFFER_VALIDATION_CONFIG = """
        minimum_score: 0.6
        rules:
            - name: "check offer name"
              factor: 0
              conditions:
               - model: "Offer"
                 attribute: "name"
                 condition:
                    operator: "contains"
                    comparated:
                      - "suspicious"
        """


class UpsertStocksTest:
    @mock.patch("pcapi.core.search.async_index_offer_ids")
    def test_upsert_multiple_stocks(self, mocked_async_index_offer_ids):
        # Given
        user = users_factories.ProFactory()
        offer = factories.ThingOfferFactory()
        existing_stock = factories.StockFactory(offer=offer, price=10)
        created_stock_data = stock_serialize.StockCreationBodyModel(price=10, quantity=7)
        edited_stock_data = stock_serialize.StockEditionBodyModel(id=existing_stock.id, price=5, quantity=7)

        # When
        stocks_upserted = api.upsert_stocks(
            offer_id=offer.id, stock_data_list=[created_stock_data, edited_stock_data], user=user
        )

        # Then
        created_stock = models.Stock.query.filter_by(id=stocks_upserted[0].id).first()
        assert created_stock.offer == offer
        assert created_stock.price == 10
        assert created_stock.quantity == 7
        edited_stock = models.Stock.query.filter_by(id=existing_stock.id).first()
        assert edited_stock.price == 5
        assert edited_stock.quantity == 7
        mocked_async_index_offer_ids.assert_called_once_with([offer.id])

    @freeze_time("2020-11-17 15:00:00")
    @override_features(OFFER_FORM_SUMMARY_PAGE=False)
    def test_upsert_stocks_triggers_draft_offer_validation(self):
        api.import_offer_validation_config(SIMPLE_OFFER_VALIDATION_CONFIG)
        # Given draft offers and new stock data
        user = users_factories.ProFactory()
        draft_approvable_offer = factories.OfferFactory(
            name="a great offer", validation=models.OfferValidationStatus.DRAFT
        )
        draft_suspicious_offer = factories.OfferFactory(
            name="A suspicious offer", validation=models.OfferValidationStatus.DRAFT
        )
        created_stock_data = stock_serialize.StockCreationBodyModel(price=10, quantity=7)

        # When stocks are upserted
        api.upsert_stocks(offer_id=draft_approvable_offer.id, stock_data_list=[created_stock_data], user=user)
        api.upsert_stocks(offer_id=draft_suspicious_offer.id, stock_data_list=[created_stock_data], user=user)

        # Then validations statuses are correctly computed
        assert draft_approvable_offer.validation == models.OfferValidationStatus.APPROVED
        assert draft_approvable_offer.isActive
        assert draft_approvable_offer.lastValidationDate == datetime(2020, 11, 17, 15, 0)
        assert draft_approvable_offer.lastValidationType == OfferValidationType.AUTO
        assert draft_suspicious_offer.validation == models.OfferValidationStatus.PENDING
        assert not draft_suspicious_offer.isActive
        assert draft_suspicious_offer.lastValidationDate == datetime(2020, 11, 17, 15, 0)
        assert draft_suspicious_offer.lastValidationType == OfferValidationType.AUTO

    def test_upsert_stocks_does_not_trigger_approved_offer_validation(self):
        # Given offers with stock and new stock data
        user = users_factories.ProFactory()
        approved_offer = factories.OfferFactory(name="a great offer that should be REJECTED")
        factories.StockFactory(offer=approved_offer, price=10)
        created_stock_data = stock_serialize.StockCreationBodyModel(price=8, quantity=7)

        # When stocks are upserted
        api.upsert_stocks(offer_id=approved_offer.id, stock_data_list=[created_stock_data], user=user)

        # Then validations status is not recomputed
        assert approved_offer.validation == models.OfferValidationStatus.APPROVED
        assert approved_offer.isActive

    def test_sends_email_if_beginning_date_changes_on_edition(self):
        # Given
        user = users_factories.ProFactory()
        offerer = offerers_factories.OffererFactory()
        offerers_factories.UserOffererFactory(user=user, offerer=offerer)

        venue = offerers_factories.VenueFactory(managingOfferer=offerer, bookingEmail="venue@postponed.net")
        offer = factories.EventOfferFactory(venue=venue, bookingEmail="offer@bookingemail.fr")
        existing_stock = factories.StockFactory(offer=offer, price=10)
        beginning = datetime.utcnow() + timedelta(days=10)
        edited_stock_data = stock_serialize.StockEditionBodyModel(
            id=existing_stock.id,
            beginningDatetime=beginning,
            bookingLimitDatetime=existing_stock.bookingLimitDatetime,
            price=2,
        )

        bookings_factories.IndividualBookingFactory(
            stock=existing_stock, individualBooking__user__email="beneficiary@bookingEmail.fr"
        )
        bookings_factories.CancelledBookingFactory(stock=existing_stock)

        # When
        api.upsert_stocks(offer_id=offer.id, stock_data_list=[edited_stock_data], user=user)

        # Then
        stock = models.Stock.query.one()
        assert stock.beginningDatetime == beginning

        assert len(mails_testing.outbox) == 2
        assert mails_testing.outbox[0].sent_data["template"] == dataclasses.asdict(
            TransactionalEmail.EVENT_OFFER_POSTPONED_CONFIRMATION_TO_PRO.value
        )
        assert mails_testing.outbox[0].sent_data["To"] == "venue@postponed.net"
        assert mails_testing.outbox[1].sent_data["template"] == dataclasses.asdict(
            TransactionalEmail.BOOKING_POSTPONED_BY_PRO_TO_BENEFICIARY.value
        )
        assert mails_testing.outbox[1].sent_data["To"] == "beneficiary@bookingEmail.fr"

    @mock.patch("pcapi.core.offers.api.update_cancellation_limit_dates")
    def should_update_bookings_cancellation_limit_date_if_report_of_event(self, mock_update_cancellation_limit_dates):
        # Given
        user = users_factories.ProFactory()
        now = datetime.utcnow()
        event_in_4_days = now + timedelta(days=4)
        event_reported_in_10_days = now + timedelta(days=10)
        offer = factories.EventOfferFactory(bookingEmail="test@bookingEmail.fr")
        existing_stock = factories.StockFactory(offer=offer, beginningDatetime=event_in_4_days)
        booking = bookings_factories.BookingFactory(stock=existing_stock, dateCreated=now)
        edited_stock_data = stock_serialize.StockEditionBodyModel(
            id=existing_stock.id,
            beginningDatetime=event_reported_in_10_days,
            bookingLimitDatetime=existing_stock.bookingLimitDatetime,
            price=2,
        )

        # When
        api.upsert_stocks(offer_id=offer.id, stock_data_list=[edited_stock_data], user=user)

        # Then
        mock_update_cancellation_limit_dates.assert_called_once_with([booking], event_reported_in_10_days)

    def should_invalidate_booking_token_when_event_is_reported(self):
        # Given
        user = users_factories.ProFactory()
        now = datetime.utcnow()
        booking_made_3_days_ago = now - timedelta(days=3)
        event_in_4_days = now + timedelta(days=4)
        event_reported_in_10_days = now + timedelta(days=10)
        offer = factories.EventOfferFactory(bookingEmail="test@bookingEmail.fr")
        existing_stock = factories.StockFactory(offer=offer, beginningDatetime=event_in_4_days)
        booking = bookings_factories.UsedIndividualBookingFactory(
            stock=existing_stock, dateCreated=booking_made_3_days_ago
        )
        edited_stock_data = stock_serialize.StockEditionBodyModel(
            id=existing_stock.id,
            beginningDatetime=event_reported_in_10_days,
            bookingLimitDatetime=existing_stock.bookingLimitDatetime,
            price=2,
        )

        # When
        api.upsert_stocks(offer_id=offer.id, stock_data_list=[edited_stock_data], user=user)

        # Then
        updated_booking = bookings_models.Booking.query.get(booking.id)
        assert updated_booking.status is not bookings_models.BookingStatus.USED
        assert updated_booking.dateUsed is None
        assert updated_booking.cancellationLimitDate == booking.cancellationLimitDate

    def should_not_invalidate_booking_token_when_event_is_reported_in_less_than_48_hours(self):
        # Given
        user = users_factories.ProFactory()
        now = datetime.utcnow()
        date_used_in_48_hours = datetime.utcnow() + timedelta(days=2)
        event_in_3_days = now + timedelta(days=3)
        event_reported_in_less_48_hours = now + timedelta(days=1)
        offer = factories.EventOfferFactory(bookingEmail="test@bookingEmail.fr")
        existing_stock = factories.StockFactory(offer=offer, beginningDatetime=event_in_3_days)
        booking = bookings_factories.UsedIndividualBookingFactory(
            stock=existing_stock, dateCreated=now, dateUsed=date_used_in_48_hours
        )
        edited_stock_data = stock_serialize.StockEditionBodyModel(
            id=existing_stock.id,
            beginningDatetime=event_reported_in_less_48_hours,
            bookingLimitDatetime=existing_stock.bookingLimitDatetime,
            price=2,
        )

        # When
        api.upsert_stocks(offer_id=offer.id, stock_data_list=[edited_stock_data], user=user)

        # Then
        updated_booking = bookings_models.Booking.query.get(booking.id)
        assert updated_booking.status is bookings_models.BookingStatus.USED
        assert updated_booking.dateUsed == date_used_in_48_hours

    def test_update_fields_updated_on_allocine_stocks(self):
        allocine_provider = providers_factories.ProviderFactory(localClass="AllocineStocks")
        stock = factories.StockFactory(
            fieldsUpdated=["price"],  # suppose we already customized the price
            quantity=5,
            offer__idAtProvider="dummy",
            offer__lastProviderId=allocine_provider.id,
        )
        stock_data = stock_serialize.StockEditionBodyModel(
            id=stock.id,
            price=stock.price,
            quantity=50,
        )
        api.upsert_stocks(stock.offerId, stock_data_list=[stock_data], user="not needed")
        assert set(stock.fieldsUpdated) == {"quantity", "price"}

    def test_does_not_allow_edition_of_stock_of_another_offer_than_given(self):
        # Given
        user = users_factories.ProFactory()
        offer = factories.ThingOfferFactory()
        other_offer = factories.ThingOfferFactory()
        existing_stock_on_other_offer = factories.StockFactory(offer=other_offer, price=10)
        edited_stock_data = stock_serialize.StockEditionBodyModel(id=existing_stock_on_other_offer.id, price=30)

        # When
        with pytest.raises(api_errors.ApiErrors) as error:
            api.upsert_stocks(offer_id=offer.id, stock_data_list=[edited_stock_data], user=user)

        # Then
        assert error.value.status_code == 403
        assert error.value.errors == {
            "global": ["Vous n'avez pas les droits d'accès suffisant pour accéder à cette information."]
        }

    def test_does_not_allow_invalid_quantity_on_creation_and_edition(self):
        # Given
        user = users_factories.ProFactory()
        offer = factories.ThingOfferFactory()
        existing_stock = factories.StockFactory(offer=offer, price=10)
        created_stock_data = stock_serialize.StockCreationBodyModel(price=10, quantity=-2)
        edited_stock_data = stock_serialize.StockEditionBodyModel(id=existing_stock.id, price=30, quantity=-4)

        # When
        with pytest.raises(api_errors.ApiErrors) as error:
            api.upsert_stocks(offer_id=offer.id, stock_data_list=[created_stock_data, edited_stock_data], user=user)

        # Then
        assert error.value.errors == {"quantity": ["Le stock doit être positif"]}

    def test_does_not_allow_invalid_price_on_creation_and_edition(self):
        # Given
        user = users_factories.ProFactory()
        offer = factories.ThingOfferFactory()
        existing_stock = factories.StockFactory(offer=offer, price=10)
        created_stock_data = stock_serialize.StockCreationBodyModel(price=-1)
        edited_stock_data = stock_serialize.StockEditionBodyModel(id=existing_stock.id, price=-3)

        # When
        with pytest.raises(api_errors.ApiErrors) as error:
            api.upsert_stocks(offer_id=offer.id, stock_data_list=[created_stock_data, edited_stock_data], user=user)

        # Then
        assert error.value.errors == {
            "price": ["Le prix doit être positif"],
        }

    def test_does_not_allow_price_above_300_euros_on_creation_for_individual_thing_offers(self):
        # Given
        user = users_factories.ProFactory()
        offer = factories.ThingOfferFactory()
        created_stock_data = stock_serialize.StockCreationBodyModel(price=301)

        # When
        with pytest.raises(api_errors.ApiErrors) as error:
            api.upsert_stocks(offer_id=offer.id, stock_data_list=[created_stock_data], user=user)

        # Then
        assert error.value.errors == {
            "price300": ["Le prix d’une offre ne peut excéder 300 euros."],
        }

    def test_does_not_allow_price_above_300_euros_on_edition_for_individual_thing_offers(self):
        # Given
        user = users_factories.ProFactory()
        existing_stock = factories.ThingStockFactory(price=10)
        edited_stock_data = stock_serialize.StockEditionBodyModel(id=existing_stock.id, price=301)

        # When
        with pytest.raises(api_errors.ApiErrors) as error:
            api.upsert_stocks(offer_id=existing_stock.offer.id, stock_data_list=[edited_stock_data], user=user)

        # Then
        assert error.value.errors == {
            "price300": ["Le prix d’une offre ne peut excéder 300 euros."],
        }

    def test_allow_price_above_300_euros_on_creation_for_individual_event_offers(self):
        # Given
        user = users_factories.ProFactory()
        offer = factories.EventOfferFactory()
        now = datetime.utcnow()
        created_stock_data = stock_serialize.StockCreationBodyModel(
            price=301, beginningDatetime=now, bookingLimitDatetime=now
        )

        # When
        api.upsert_stocks(offer_id=offer.id, stock_data_list=[created_stock_data], user=user)

        # Then
        created_stock = models.Stock.query.one()
        assert created_stock.price == 301

    def test_allow_price_above_300_euros_on_edition_for_individual_event_offers(self):
        # Given
        user = users_factories.ProFactory()
        existing_stock = factories.EventStockFactory(price=10, offer__bookingEmail="test@bookingEmail.fr")
        now = datetime.utcnow()
        edited_stock_data = stock_serialize.StockEditionBodyModel(
            id=existing_stock.id, price=301, beginningDatetime=now, bookingLimitDatetime=now
        )

        # When
        api.upsert_stocks(offer_id=existing_stock.offer.id, stock_data_list=[edited_stock_data], user=user)

        # Then
        assert existing_stock.price == 301

    def test_cannot_edit_price_if_reimbursement_rule_exists(self):
        user = users_factories.AdminFactory()
        stock = factories.ThingStockFactory(price=10)
        payments_factories.CustomReimbursementRuleFactory(offer=stock.offer)

        data = stock_serialize.StockEditionBodyModel(id=stock.id, price=9)
        with pytest.raises(api_errors.ApiErrors) as error:
            api.upsert_stocks(offer_id=stock.offerId, stock_data_list=[data], user=user)
        assert error.value.errors["price"][0].startswith("Vous ne pouvez pas modifier le prix")

    def test_cannot_create_stock_with_different_price_if_reimbursement_rule_exists(self):
        # If a stock exists with a price, we cannot add a new stock
        # with another price.
        user = users_factories.AdminFactory()
        stock = factories.ThingStockFactory(price=10)
        offer = stock.offer
        payments_factories.CustomReimbursementRuleFactory(offer=stock.offer)

        data = stock_serialize.StockCreationBodyModel(price=9)
        with pytest.raises(api_errors.ApiErrors) as error:
            api.upsert_stocks(offer_id=offer.id, stock_data_list=[data], user=user)
        assert error.value.errors["price"][0].startswith("Vous ne pouvez pas modifier le prix")

    def test_cannot_create_stock_with_different_price_if_reimbursement_rule_exists_with_soft_deleted_price(self):
        # Same as above, but with an offer than only has one,
        # soft-deleted stock.
        user = users_factories.AdminFactory()
        stock = factories.ThingStockFactory(price=10, isSoftDeleted=True)
        offer = stock.offer
        payments_factories.CustomReimbursementRuleFactory(offer=stock.offer)

        data = stock_serialize.StockCreationBodyModel(price=9)
        with pytest.raises(api_errors.ApiErrors) as error:
            api.upsert_stocks(offer_id=offer.id, stock_data_list=[data], user=user)
        assert error.value.errors["price"][0].startswith("Vous ne pouvez pas modifier le prix")

    def test_cannot_create_stock_if_reimbursement_rule_exists(self):
        # We really should not have a custom reimbursement rule for an
        # offer that does not have any stock. Let's be defensive,
        # though, and block stock creation.
        user = users_factories.AdminFactory()
        offer = factories.ThingOfferFactory()
        payments_factories.CustomReimbursementRuleFactory(offer=offer)

        data = stock_serialize.StockCreationBodyModel(price=9)
        with pytest.raises(api_errors.ApiErrors) as error:
            api.upsert_stocks(offer_id=offer.id, stock_data_list=[data], user=user)
        assert error.value.errors["price"][0].startswith("Vous ne pouvez pas modifier le prix")

    def test_does_not_allow_beginning_datetime_on_thing_offer_on_creation_and_edition(self):
        # Given
        user = users_factories.ProFactory()
        offer = factories.ThingOfferFactory()
        beginning_date = datetime.utcnow() + timedelta(days=4)
        existing_stock = factories.StockFactory(offer=offer, price=10)
        created_stock_data = stock_serialize.StockCreationBodyModel(
            price=-1, beginningDatetime=beginning_date, bookingLimitDatetime=beginning_date
        )
        edited_stock_data = stock_serialize.StockEditionBodyModel(
            id=existing_stock.id, price=0, beginningDatetime=beginning_date, bookingLimitDatetime=beginning_date
        )

        # When
        with pytest.raises(api_errors.ApiErrors) as error:
            api.upsert_stocks(offer_id=offer.id, stock_data_list=[created_stock_data, edited_stock_data], user=user)

        # Then
        assert error.value.errors == {
            "global": ["Impossible de mettre une date de début si l'offre ne porte pas sur un événement"],
        }

    def test_validate_booking_limit_datetime_with_expiration_datetime_on_creation(self):
        # Given
        user = users_factories.ProFactory()
        offer = factories.DigitalOfferFactory()
        created_stock_data = stock_serialize.StockCreationBodyModel(
            price=0,
            bookingLimitDatetime=None,
            activationCodesExpirationDatetime=datetime.utcnow(),
            activationCodes=["ABC", "DEF"],
        )

        # When
        with pytest.raises(api_errors.ApiErrors) as error:
            api.upsert_stocks(offer_id=offer.id, stock_data_list=[created_stock_data], user=user)

        # Then
        assert error.value.errors == {
            "bookingLimitDatetime": [
                (
                    "Une date limite de validité a été renseignée. Dans ce cas, il faut également"
                    " renseigner une date limite de réservation qui doit être antérieure d'au moins 7 jours."
                ),
            ],
        }

    def test_validate_booking_limit_datetime_with_expiration_datetime_on_edition(self):
        # Given
        user = users_factories.ProFactory()
        offer = factories.DigitalOfferFactory()
        existing_stock = factories.StockFactory(offer=offer)
        factories.ActivationCodeFactory(expirationDate=datetime.utcnow(), stock=existing_stock)
        edited_stock_data = stock_serialize.StockEditionBodyModel(
            id=existing_stock.id, price=0, bookingLimitDatetime=None
        )

        # When
        with pytest.raises(api_errors.ApiErrors) as error:
            api.upsert_stocks(offer_id=offer.id, stock_data_list=[edited_stock_data], user=user)

        # Then
        assert error.value.errors == {
            "bookingLimitDatetime": [
                (
                    "Une date limite de validité a été renseignée. Dans ce cas, il faut également"
                    " renseigner une date limite de réservation qui doit être antérieure d'au moins 7 jours."
                ),
            ],
        }

    def test_does_not_allow_a_negative_remaining_quantity_on_edition(self):
        # Given
        user = users_factories.ProFactory()
        offer = factories.ThingOfferFactory()
        booking = bookings_factories.BookingFactory(stock__offer=offer, stock__quantity=10)
        existing_stock = booking.stock
        edited_stock_data = stock_serialize.StockEditionBodyModel(id=existing_stock.id, quantity=0, price=10)

        # When
        with pytest.raises(api_errors.ApiErrors) as error:
            api.upsert_stocks(offer_id=offer.id, stock_data_list=[edited_stock_data], user=user)

        # Then
        assert error.value.errors == {"quantity": ["Le stock total ne peut être inférieur au nombre de réservations"]}

    def test_does_not_allow_missing_dates_for_an_event_offer_on_creation_and_edition(self):
        # Given
        user = users_factories.ProFactory()
        offer = factories.EventOfferFactory()
        created_stock_data = stock_serialize.StockCreationBodyModel(
            price=10, beginningDatetime=None, bookingLimitDatetime=None
        )

        # When
        with pytest.raises(api_errors.ApiErrors) as error:
            api.upsert_stocks(offer_id=offer.id, stock_data_list=[created_stock_data], user=user)

        # Then
        assert error.value.errors == {"beginningDatetime": ["Ce paramètre est obligatoire"]}

    def test_does_not_allow_booking_limit_after_beginning_for_an_event_offer_on_creation_and_edition(self):
        # Given
        user = users_factories.ProFactory()
        offer = factories.EventOfferFactory()
        beginning_date = datetime.utcnow() + timedelta(days=4)
        booking_limit = beginning_date + timedelta(days=4)
        created_stock_data = stock_serialize.StockCreationBodyModel(
            price=10, beginningDatetime=beginning_date, bookingLimitDatetime=booking_limit
        )

        # When
        with pytest.raises(exceptions.BookingLimitDatetimeTooLate):
            api.upsert_stocks(offer_id=offer.id, stock_data_list=[created_stock_data], user=user)

        # Then
        assert models.Stock.query.count() == 0

    def test_does_not_allow_edition_of_a_past_event_stock(self):
        # Given
        user = users_factories.ProFactory()
        offer = factories.ThingOfferFactory()
        date_in_the_past = datetime.utcnow() - timedelta(days=4)
        existing_stock = factories.StockFactory(offer=offer, price=10, beginningDatetime=date_in_the_past)
        edited_stock_data = stock_serialize.StockEditionBodyModel(id=existing_stock.id, price=4)

        # When
        with pytest.raises(api_errors.ApiErrors) as error:
            api.upsert_stocks(offer_id=offer.id, stock_data_list=[edited_stock_data], user=user)

        # Then
        assert error.value.errors == {"global": ["Les événements passés ne sont pas modifiables"]}

    def test_does_not_allow_upsert_stocks_on_a_synchronized_offer(self):
        # Given
        user = users_factories.ProFactory()
        offer = factories.ThingOfferFactory(
            lastProvider=providers_factories.AllocineProviderFactory(localClass="TiteLiveStocks")
        )
        created_stock_data = stock_serialize.StockCreationBodyModel(price=10)

        # When
        with pytest.raises(api_errors.ApiErrors) as error:
            api.upsert_stocks(offer_id=offer.id, stock_data_list=[created_stock_data], user=user)

        # Then
        assert error.value.errors == {"global": ["Les offres importées ne sont pas modifiables"]}

    def test_allow_edition_of_price_and_quantity_for_stocks_of_offers_synchronized_with_allocine(self):
        # Given
        user = users_factories.ProFactory()
        offer = factories.EventOfferFactory(
            lastProvider=providers_factories.AllocineProviderFactory(localClass="AllocineStocks")
        )
        date_in_the_future = datetime.utcnow() + timedelta(days=4)
        existing_stock = factories.StockFactory(offer=offer, price=10, beginningDatetime=date_in_the_future)
        edited_stock_data = stock_serialize.StockEditionBodyModel(
            id=existing_stock.id,
            beginningDatetime=existing_stock.beginningDatetime,
            bookingLimitDatetime=existing_stock.bookingLimitDatetime,
            price=4,
        )

        # When
        api.upsert_stocks(offer_id=offer.id, stock_data_list=[edited_stock_data], user=user)

        # Then
        edited_stock = models.Stock.query.filter_by(id=existing_stock.id).first()
        assert edited_stock.price == 4

    def test_does_not_allow_edition_of_beginningDateTime_for_stocks_of_offers_synchronized_with_allocine(self):
        # Given
        user = users_factories.ProFactory()
        offer = factories.EventOfferFactory(
            lastProvider=providers_factories.AllocineProviderFactory(localClass="AllocineStocks")
        )
        date_in_the_future = datetime.utcnow() + timedelta(days=4)
        other_date_in_the_future = datetime.utcnow() + timedelta(days=6)
        existing_stock = factories.StockFactory(offer=offer, price=10, beginningDatetime=date_in_the_future)
        edited_stock_data = stock_serialize.StockEditionBodyModel(
            id=existing_stock.id,
            beginningDatetime=other_date_in_the_future,
            bookingLimitDatetime=other_date_in_the_future,
            price=10,
        )

        # When
        with pytest.raises(api_errors.ApiErrors) as error:
            api.upsert_stocks(offer_id=offer.id, stock_data_list=[edited_stock_data], user=user)

        # Then
        assert error.value.errors == {"global": ["Pour les offres importées, certains champs ne sont pas modifiables"]}

    @mock.patch("pcapi.core.mails.transactional.send_first_venue_approved_offer_email_to_pro")
    def test_create_stock_for_non_approved_offer_fails(self, mocked_send_first_venue_approved_offer_email_to_pro):
        user = users_factories.ProFactory()
        offer = factories.ThingOfferFactory(validation=models.OfferValidationStatus.PENDING)
        created_stock_data = stock_serialize.StockCreationBodyModel(price=10, quantity=7)

        with pytest.raises(api_errors.ApiErrors) as error:
            api.upsert_stocks(offer_id=offer.id, stock_data_list=[created_stock_data], user=user)

        assert error.value.errors == {
            "global": ["Les offres refusées ou en attente de validation ne sont pas modifiables"]
        }
        assert models.Stock.query.count() == 0

        assert not mocked_send_first_venue_approved_offer_email_to_pro.called

    @mock.patch("pcapi.core.mails.transactional.send_first_venue_approved_offer_email_to_pro")
    def test_edit_stock_of_non_approved_offer_fails(
        self,
        mocked_send_first_venue_approved_offer_email_to_pro,
    ):
        user = users_factories.ProFactory()
        offer = factories.ThingOfferFactory(validation=models.OfferValidationStatus.PENDING)
        existing_stock = factories.StockFactory(offer=offer, price=10)
        edited_stock_data = stock_serialize.StockEditionBodyModel(id=existing_stock.id, price=5, quantity=7)

        with pytest.raises(api_errors.ApiErrors) as error:
            api.upsert_stocks(offer_id=offer.id, stock_data_list=[edited_stock_data], user=user)

        assert error.value.errors == {
            "global": ["Les offres refusées ou en attente de validation ne sont pas modifiables"]
        }
        existing_stock = models.Stock.query.one()
        assert existing_stock.price == 10

        assert not mocked_send_first_venue_approved_offer_email_to_pro.called

    @mock.patch("pcapi.domain.admin_emails.send_offer_creation_notification_to_administration")
    @mock.patch("pcapi.core.mails.transactional.send_first_venue_approved_offer_email_to_pro")
    @mock.patch("pcapi.core.offers.api.set_offer_status_based_on_fraud_criteria")
    @override_features(OFFER_FORM_SUMMARY_PAGE=False)
    def test_send_email_when_offer_automatically_approved_based_on_fraud_criteria(
        self,
        mocked_set_offer_status_based_on_fraud_criteria,
        mocked_send_first_venue_approved_offer_email_to_pro,
        mocked_offer_creation_notification_to_admin,
    ):
        user = users_factories.ProFactory()
        offer = factories.ThingOfferFactory(validation=models.OfferValidationStatus.DRAFT)
        created_stock_data = stock_serialize.StockCreationBodyModel(price=10, quantity=7)
        mocked_set_offer_status_based_on_fraud_criteria.return_value = models.OfferValidationStatus.APPROVED

        api.upsert_stocks(offer_id=offer.id, stock_data_list=[created_stock_data], user=user)

        mocked_offer_creation_notification_to_admin.assert_called_once_with(offer)
        mocked_send_first_venue_approved_offer_email_to_pro.assert_called_once_with(offer)

    @mock.patch("pcapi.domain.admin_emails.send_offer_creation_notification_to_administration")
    @mock.patch("pcapi.core.mails.transactional.send_first_venue_approved_offer_email_to_pro")
    @mock.patch("pcapi.core.offers.api.set_offer_status_based_on_fraud_criteria")
    def test_not_send_email_when_offer_pass_to_pending_based_on_fraud_criteria(
        self,
        mocked_set_offer_status_based_on_fraud_criteria,
        mocked_send_first_venue_approved_offer_email_to_pro,
        mocked_offer_creation_notification_to_admin,
    ):
        user = users_factories.ProFactory()
        offer = factories.ThingOfferFactory(validation=models.OfferValidationStatus.DRAFT)
        created_stock_data = stock_serialize.StockCreationBodyModel(price=10, quantity=7)
        mocked_set_offer_status_based_on_fraud_criteria.return_value = models.OfferValidationStatus.PENDING

        api.upsert_stocks(offer_id=offer.id, stock_data_list=[created_stock_data], user=user)

        assert not mocked_offer_creation_notification_to_admin.called
        assert not mocked_send_first_venue_approved_offer_email_to_pro.called


class DeleteStockTest:
    @mock.patch("pcapi.core.search.async_index_offer_ids")
    def test_delete_stock_basics(self, mocked_async_index_offer_ids):
        stock = factories.EventStockFactory()

        api.delete_stock(stock)

        stock = models.Stock.query.one()
        assert stock.isSoftDeleted
        mocked_async_index_offer_ids.assert_called_once_with([stock.offerId])

    def test_delete_stock_cancel_bookings_and_send_emails(self):
        offerer_email = "offerer@example.com"
        stock = factories.EventStockFactory(offer__bookingEmail=offerer_email)
        booking1 = bookings_factories.IndividualBookingFactory(
            stock=stock,
            individualBooking__user__email="beneficiary@example.com",
        )
        booking2 = bookings_factories.CancelledIndividualBookingFactory(stock=stock)
        booking3 = bookings_factories.UsedIndividualBookingFactory(stock=stock)

        api.delete_stock(stock)

        # cancellation can trigger more than one request to Batch
        assert len(push_testing.requests) >= 1

        stock = models.Stock.query.one()
        assert stock.isSoftDeleted
        booking1 = bookings_models.Booking.query.get(booking1.id)
        assert booking1.status == bookings_models.BookingStatus.CANCELLED
        assert booking1.cancellationReason == bookings_models.BookingCancellationReasons.OFFERER
        booking2 = bookings_models.Booking.query.get(booking2.id)
        assert booking2.status == bookings_models.BookingStatus.CANCELLED  # unchanged
        assert booking2.cancellationReason == bookings_models.BookingCancellationReasons.BENEFICIARY
        booking3 = bookings_models.Booking.query.get(booking3.id)
        assert booking3.status == bookings_models.BookingStatus.CANCELLED  # cancel used booking for event offer
        assert booking3.cancellationReason == bookings_models.BookingCancellationReasons.OFFERER

        assert len(mails_testing.outbox) == 3
        assert {outbox.sent_data["To"] for outbox in mails_testing.outbox} == {
            booking1.email,
            booking3.email,
            offerer_email,
        }

        last_request = copy.deepcopy(push_testing.requests[-1])
        last_request["user_ids"] = set(last_request["user_ids"])
        assert last_request == {
            "group_id": "Cancel_booking",
            "user_ids": {
                booking1.individualBooking.userId,
                booking3.individualBooking.userId,
            },
            "message": {
                "body": f"""Ta réservation "{stock.offer.name}" a été annulée par l'offreur.""",
                "title": "Réservation annulée",
            },
            "can_be_asynchronously_retried": False,
        }

    def test_can_delete_if_stock_from_allocine(self):
        provider = providers_factories.AllocineProviderFactory(localClass="AllocineStocks")
        offer = factories.OfferFactory(lastProvider=provider, idAtProvider="1")
        stock = factories.StockFactory(offer=offer)

        api.delete_stock(stock)

        stock = models.Stock.query.one()
        assert stock.isSoftDeleted

    def test_cannot_delete_if_stock_from_titelive(self):
        provider = providers_factories.AllocineProviderFactory(localClass="TiteLiveStocks")
        offer = factories.OfferFactory(lastProvider=provider, idAtProvider="1")
        stock = factories.StockFactory(offer=offer)

        with pytest.raises(api_errors.ApiErrors) as error:
            api.delete_stock(stock)
        msg = "Les offres importées ne sont pas modifiables"
        assert error.value.errors["global"][0] == msg

        stock = models.Stock.query.one()
        assert not stock.isSoftDeleted

    def test_can_delete_if_event_ended_recently(self):
        recently = datetime.utcnow() - timedelta(days=1)
        stock = factories.EventStockFactory(beginningDatetime=recently)

        api.delete_stock(stock)
        stock = models.Stock.query.one()
        assert stock.isSoftDeleted

    def test_cannot_delete_if_too_late(self):
        too_long_ago = datetime.utcnow() - timedelta(days=3)
        stock = factories.EventStockFactory(beginningDatetime=too_long_ago)

        with pytest.raises(exceptions.TooLateToDeleteStock):
            api.delete_stock(stock)
        stock = models.Stock.query.one()
        assert not stock.isSoftDeleted


class CreateMediationV2Test:
    BASE_THUMBS_DIR = pathlib.Path(tests.__path__[0]) / ".." / "src" / "pcapi" / "static" / "object_store_data"
    THUMBS_DIR = BASE_THUMBS_DIR / "thumbs" / "mediations"

    @mock.patch("pcapi.core.search.async_index_offer_ids")
    @override_settings(LOCAL_STORAGE_DIR=BASE_THUMBS_DIR)
    def test_ok(self, mocked_async_index_offer_ids, clear_tests_assets_bucket):
        # Given
        user = users_factories.ProFactory()
        offer = factories.ThingOfferFactory()
        image_as_bytes = (IMAGES_DIR / "mouette_full_size.jpg").read_bytes()

        # When
        api.create_mediation(user, offer, "©Photographe", image_as_bytes)

        # Then
        models.mediation = models.Mediation.query.one()
        assert models.mediation.author == user
        assert models.mediation.offer == offer
        assert models.mediation.credit == "©Photographe"
        assert models.mediation.thumbCount == 1
        assert models.Mediation.query.filter(models.Mediation.offerId == offer.id).count() == 1
        mocked_async_index_offer_ids.assert_called_once_with([offer.id])

    @override_settings(LOCAL_STORAGE_DIR=BASE_THUMBS_DIR)
    def test_erase_former_mediations(self, clear_tests_assets_bucket):
        # Given
        user = users_factories.ProFactory()
        offer = factories.ThingOfferFactory()
        image_as_bytes = (IMAGES_DIR / "mouette_full_size.jpg").read_bytes()
        existing_number_of_files = len(os.listdir(self.THUMBS_DIR))

        mediation_1 = api.create_mediation(user, offer, "©Photographe", image_as_bytes)
        mediation_2 = api.create_mediation(user, offer, "©Alice", image_as_bytes)
        thumb_1_id = humanize(mediation_1.id)
        thumb_2_id = humanize(mediation_2.id)

        # When
        api.create_mediation(user, offer, "©moi", image_as_bytes)

        # Then
        models.mediation_3 = models.Mediation.query.one()
        assert models.mediation_3.credit == "©moi"
        thumb_3_id = humanize(models.mediation_3.id)

        assert not (self.THUMBS_DIR / thumb_1_id).exists()
        assert not (self.THUMBS_DIR / (thumb_1_id + ".type")).exists()
        assert not (self.THUMBS_DIR / thumb_2_id).exists()
        assert not (self.THUMBS_DIR / (thumb_2_id + ".type")).exists()

        assert len(os.listdir(self.THUMBS_DIR)) == existing_number_of_files + 2
        assert (self.THUMBS_DIR / thumb_3_id).exists()
        assert (self.THUMBS_DIR / (thumb_3_id + ".type")).exists()

    @mock.patch("pcapi.core.object_storage.store_public_object", side_effect=Exception)
    @override_settings(LOCAL_STORAGE_DIR=BASE_THUMBS_DIR)
    def test_rollback_if_exception(self, mock_store_public_object, clear_tests_assets_bucket):
        # Given
        user = users_factories.ProFactory()
        offer = factories.ThingOfferFactory()
        image_as_bytes = (IMAGES_DIR / "mouette_full_size.jpg").read_bytes()
        existing_number_of_files = len(os.listdir(self.THUMBS_DIR))

        # When
        with pytest.raises(exceptions.ThumbnailStorageError):
            api.create_mediation(user, offer, "©Photographe", image_as_bytes)

        # Then
        assert models.Mediation.query.count() == 0
        assert len(os.listdir(self.THUMBS_DIR)) == existing_number_of_files


class CreateOfferTest:
    def test_create_offer_from_scratch(self):
        venue = offerers_factories.VenueFactory()
        offerer = venue.managingOfferer
        user_offerer = offerers_factories.UserOffererFactory(offerer=offerer)
        user = user_offerer.user

        data = offers_serialize.PostOfferBodyModel(
            venueId=humanize(venue.id),
            name="A pretty good offer",
            subcategoryId=subcategories.SEANCE_CINE.id,
            externalTicketOfficeUrl="http://example.net",
            audioDisabilityCompliant=True,
            mentalDisabilityCompliant=True,
            motorDisabilityCompliant=True,
            visualDisabilityCompliant=True,
        )
        offer = api.create_offer(data, user)

        assert offer.name == "A pretty good offer"
        assert offer.venue == venue
        assert offer.subcategoryId == subcategories.SEANCE_CINE.id
        assert offer.product.owningOfferer == offerer
        assert offer.externalTicketOfficeUrl == "http://example.net"
        assert offer.audioDisabilityCompliant
        assert offer.mentalDisabilityCompliant
        assert offer.motorDisabilityCompliant
        assert offer.visualDisabilityCompliant
        assert offer.validation == models.OfferValidationStatus.DRAFT
        assert not offer.bookingEmail
        assert models.Offer.query.count() == 1

    @override_features(ENABLE_ISBN_REQUIRED_IN_LIVRE_EDITION_OFFER_CREATION=True)
    def test_create_offer_livre_edition_from_isbn_with_existing_product(self):
        factories.ProductFactory(
            subcategoryId=subcategories.LIVRE_PAPIER.id,
            description="Les prévisions du psychohistorien Hari Seldon sont formelles.",
            extraData={"isbn": "9782207300893", "author": "Asimov", "bookFormat": "Soft cover"},
            isGcuCompatible=True,
        )
        venue = offerers_factories.VenueFactory()
        offerer = venue.managingOfferer
        user_offerer = offerers_factories.UserOffererFactory(offerer=offerer)
        user = user_offerer.user

        data = offers_serialize.PostOfferBodyModel(
            venueId=humanize(venue.id),
            name="FONDATION T.1",
            subcategoryId=subcategories.LIVRE_PAPIER.id,
            extraData={"isbn": "9782207300893", "author": "Isaac Asimov"},
            audioDisabilityCompliant=True,
            mentalDisabilityCompliant=True,
            motorDisabilityCompliant=True,
            visualDisabilityCompliant=False,
        )
        offer = api.create_offer(data, user)

        assert offer.name == "FONDATION T.1"
        assert offer.subcategoryId == subcategories.LIVRE_PAPIER.id
        assert offer.description == "Les prévisions du psychohistorien Hari Seldon sont formelles."
        assert offer.extraData == {"isbn": "9782207300893", "author": "Isaac Asimov", "bookFormat": "Soft cover"}
        assert offer.audioDisabilityCompliant
        assert offer.mentalDisabilityCompliant
        assert offer.motorDisabilityCompliant
        assert not offer.visualDisabilityCompliant
        assert models.Product.query.count() == 1

    @override_features(ENABLE_ISBN_REQUIRED_IN_LIVRE_EDITION_OFFER_CREATION=True)
    def test_create_offer_livre_edition_from_isbn_with_is_not_compatible_gcu_should_fail(self):
        factories.ProductFactory(
            subcategoryId=subcategories.LIVRE_PAPIER.id,
            description="Les prévisions du psychohistorien Hari Seldon sont formelles.",
            extraData={"isbn": "9782207300893", "author": "Asimov", "bookFormat": "Soft cover"},
            isGcuCompatible=False,
        )

        venue = offerers_factories.VenueFactory()
        offerer = venue.managingOfferer
        user_offerer = offerers_factories.UserOffererFactory(offerer=offerer)
        user = user_offerer.user

        data = offers_serialize.PostOfferBodyModel(
            venueId=humanize(venue.id),
            name="FONDATION T.1",
            subcategoryId=subcategories.LIVRE_PAPIER.id,
            extraData={"isbn": "9782207300893"},
            audioDisabilityCompliant=True,
            mentalDisabilityCompliant=True,
            motorDisabilityCompliant=True,
            visualDisabilityCompliant=False,
        )

        with pytest.raises(api_errors.ApiErrors) as error:
            api.create_offer(data, user)

        assert error.value.errors["isbn"] == ["Ce produit n’est pas éligible au pass Culture."]

    @override_features(ENABLE_ISBN_REQUIRED_IN_LIVRE_EDITION_OFFER_CREATION=True)
    def test_create_offer_livre_edition_from_isbn_with_product_not_exists_should_fail(self):
        venue = offerers_factories.VenueFactory()
        offerer = venue.managingOfferer
        user_offerer = offerers_factories.UserOffererFactory(offerer=offerer)
        user = user_offerer.user

        data = offers_serialize.PostOfferBodyModel(
            venueId=humanize(venue.id),
            name="FONDATION T.1",
            subcategoryId=subcategories.LIVRE_PAPIER.id,
            extraData={"isbn": "9782207300893"},
            audioDisabilityCompliant=True,
            mentalDisabilityCompliant=True,
            motorDisabilityCompliant=True,
            visualDisabilityCompliant=False,
        )

        with pytest.raises(api_errors.ApiErrors) as error:
            api.create_offer(data, user)

        assert error.value.errors["isbn"] == ["Ce produit n’est pas éligible au pass Culture."]

    def test_cannot_create_activation_offer(self):
        venue = offerers_factories.VenueFactory()
        user_offerer = offerers_factories.UserOffererFactory(offerer=venue.managingOfferer)
        with pytest.raises(exceptions.SubCategoryIsInactive) as error:
            data = offers_serialize.PostOfferBodyModel(
                venueId=humanize(venue.id),
                name="An offer he can't refuse",
                subcategoryId=subcategories.ACTIVATION_EVENT.id,
                audioDisabilityCompliant=True,
                mentalDisabilityCompliant=True,
                motorDisabilityCompliant=True,
                visualDisabilityCompliant=True,
            )
            api.create_offer(data, user_offerer.user)

        assert error.value.errors["subcategory"] == [
            "Une offre ne peut être créée ou éditée en utilisant cette sous-catégorie"
        ]

    def test_cannot_create_offer_when_invalid_subcategory(self):
        venue = offerers_factories.VenueFactory()
        user_offerer = offerers_factories.UserOffererFactory(offerer=venue.managingOfferer)
        with pytest.raises(exceptions.UnknownOfferSubCategory) as error:
            data = offers_serialize.PostOfferBodyModel(
                venueId=humanize(venue.id),
                name="An offer he can't refuse",
                subcategoryId="TOTO",
                audioDisabilityCompliant=True,
                mentalDisabilityCompliant=True,
                motorDisabilityCompliant=True,
                visualDisabilityCompliant=True,
            )
            api.create_offer(data, user_offerer.user)

        assert error.value.errors["subcategory"] == ["La sous-catégorie de cette offre est inconnue"]

    def test_fail_if_unknown_venue(self):
        user = users_factories.ProFactory()
        data = offers_serialize.PostOfferBodyModel(
            venueId=humanize(1),
            name="An awful offer",
            subcategoryId=subcategories.CONCERT.id,
            audioDisabilityCompliant=True,
            mentalDisabilityCompliant=True,
            motorDisabilityCompliant=True,
            visualDisabilityCompliant=True,
        )
        with pytest.raises(api_errors.ApiErrors) as error:
            api.create_offer(data, user)
        err = "Aucun objet ne correspond à cet identifiant dans notre base de données"
        assert error.value.errors["global"] == [err]

    def test_fail_if_user_not_related_to_offerer(self):
        venue = offerers_factories.VenueFactory()
        user = users_factories.ProFactory()
        data = offers_serialize.PostOfferBodyModel(
            venueId=humanize(venue.id),
            subcategoryId=subcategories.CONCERT.id,
            audioDisabilityCompliant=True,
            mentalDisabilityCompliant=True,
            motorDisabilityCompliant=True,
            visualDisabilityCompliant=True,
        )
        with pytest.raises(api_errors.ApiErrors) as error:
            api.create_offer(data, user)
        err = "Vous n'avez pas les droits d'accès suffisant pour accéder à cette information."
        assert error.value.errors["global"] == [err]

    def test_raise_error_if_extra_data_mandatory_fields_not_provided(self):
        venue = offerers_factories.VenueFactory()
        offerer = venue.managingOfferer
        user_offerer = offerers_factories.UserOffererFactory(offerer=offerer)
        user = user_offerer.user

        data = offers_serialize.PostOfferBodyModel(
            venueId=humanize(venue.id),
            name="A pretty good offer",
            subcategoryId=subcategories.CONCERT.id,
        )

        with pytest.raises(api_errors.ApiErrors) as error:
            api.create_offer(data, user)

        assert error.value.errors["musicType"] == ["Ce champ est obligatoire"]


class UpdateOfferTest:
    @mock.patch("pcapi.core.search.async_index_offer_ids")
    def test_basics(self, mocked_async_index_offer_ids):
        offer = factories.OfferFactory(isDuo=False, bookingEmail="old@example.com")

        offer = api.update_offer(offer, isDuo=True, bookingEmail="new@example.com")

        assert offer.isDuo
        assert offer.bookingEmail == "new@example.com"
        mocked_async_index_offer_ids.assert_called_once_with([offer.id])

    def test_update_extra_data_should_not_erase_mandatory_fields(self):
        offer = factories.OfferFactory(
            subcategoryId=subcategories.SPECTACLE_REPRESENTATION.id, extraData={"showType": 200}
        )

        offer = api.update_offer(offer, extraData={"author": "Asimov"})

        assert offer.extraData == {"author": "Asimov", "showType": 200}

    def test_update_extra_data_should_raise_error_when_mandatory_field_not_provided(self):
        offer = factories.OfferFactory(subcategoryId=subcategories.SPECTACLE_REPRESENTATION.id)

        with pytest.raises(api_errors.ApiErrors) as error:
            api.update_offer(offer, extraData={"author": "Asimov"})

        assert error.value.errors == {"showType": ["Ce champ est obligatoire"]}

    def test_should_be_able_to_update_offer_when_extra_data_is_none(self):
        offer = factories.OfferFactory(
            subcategoryId=subcategories.SPECTACLE_REPRESENTATION.id, extraData={"showType": 200}
        )

        offer = api.update_offer(offer, extraData=None)

        assert offer.extraData == {"showType": 200}

    def test_update_product_if_owning_offerer_is_the_venue_managing_offerer(self):
        offerer = offerers_factories.OffererFactory()
        product = factories.ProductFactory(owningOfferer=offerer)
        offer = factories.OfferFactory(product=product, venue__managingOfferer=offerer)

        offer = api.update_offer(offer, name="New name")

        assert offer.name == "New name"
        assert product.name == "New name"

    def test_do_not_update_product_if_owning_offerer_is_not_the_venue_managing_offerer(self):
        product = factories.ProductFactory(name="Old name")
        offer = factories.OfferFactory(product=product, name="Old name")

        offer = api.update_offer(offer, name="New name")

        assert offer.name == "New name"
        assert product.name == "Old name"

    def test_cannot_update_with_name_too_long(self):
        offer = factories.OfferFactory(name="Old name")

        with pytest.raises(api_errors.ApiErrors) as error:
            api.update_offer(offer, name="Luftballons" * 99)

        assert error.value.errors == {"name": ["Vous devez saisir moins de 140 caractères"]}
        assert models.Offer.query.one().name == "Old name"

    def test_success_on_allocine_offer(self):
        provider = providers_factories.AllocineProviderFactory(localClass="AllocineStocks")
        offer = factories.OfferFactory(lastProvider=provider, name="Old name")

        api.update_offer(offer, name="Old name", isDuo=True)

        offer = models.Offer.query.one()
        assert offer.name == "Old name"
        assert offer.isDuo

    def test_forbidden_on_allocine_offer_on_certain_fields(self):
        provider = providers_factories.AllocineProviderFactory(localClass="AllocineStocks")
        offer = factories.OfferFactory(lastProvider=provider, name="Old name")

        with pytest.raises(api_errors.ApiErrors) as error:
            api.update_offer(offer, name="New name", isDuo=True)

        assert error.value.errors == {"name": ["Vous ne pouvez pas modifier ce champ"]}
        offer = models.Offer.query.one()
        assert offer.name == "Old name"
        assert not offer.isDuo

    def test_success_on_imported_offer_on_external_ticket_office_url(self):
        provider = providers_factories.AllocineProviderFactory()
        offer = factories.OfferFactory(
            externalTicketOfficeUrl="http://example.org",
            lastProvider=provider,
            name="Old name",
        )

        api.update_offer(
            offer,
            externalTicketOfficeUrl="https://example.com",
        )

        offer = models.Offer.query.one()
        assert offer.name == "Old name"
        assert offer.externalTicketOfficeUrl == "https://example.com"

    def test_success_on_imported_offer_on_accessibility_fields(self):
        provider = providers_factories.AllocineProviderFactory()
        offer = factories.OfferFactory(
            lastProvider=provider,
            name="Old name",
            audioDisabilityCompliant=True,
            visualDisabilityCompliant=False,
            motorDisabilityCompliant=False,
            mentalDisabilityCompliant=True,
        )

        api.update_offer(
            offer,
            name="Old name",
            audioDisabilityCompliant=False,
            visualDisabilityCompliant=True,
            motorDisabilityCompliant=True,
            mentalDisabilityCompliant=False,
        )

        offer = models.Offer.query.one()
        assert offer.name == "Old name"
        assert offer.audioDisabilityCompliant == False
        assert offer.visualDisabilityCompliant == True
        assert offer.motorDisabilityCompliant == True
        assert offer.mentalDisabilityCompliant == False

    def test_forbidden_on_imported_offer_on_other_fields(self):
        provider = providers_factories.APIProviderFactory()
        offer = factories.OfferFactory(
            lastProvider=provider, name="Old name", isDuo=False, audioDisabilityCompliant=True
        )

        with pytest.raises(api_errors.ApiErrors) as error:
            api.update_offer(offer, name="New name", isDuo=True, audioDisabilityCompliant=False)

        assert error.value.errors == {
            "name": ["Vous ne pouvez pas modifier ce champ"],
            "isDuo": ["Vous ne pouvez pas modifier ce champ"],
        }
        offer = models.Offer.query.one()
        assert offer.name == "Old name"
        assert offer.isDuo == False
        assert offer.audioDisabilityCompliant == True

    def test_update_non_approved_offer_fails(self):
        pending_offer = factories.OfferFactory(name="Soliloquy", validation=models.OfferValidationStatus.PENDING)

        with pytest.raises(api_errors.ApiErrors) as error:
            api.update_offer(pending_offer, name="Monologue")

        assert error.value.errors == {
            "global": ["Les offres refusées ou en attente de validation ne sont pas modifiables"]
        }
        pending_offer = models.Offer.query.one()
        assert pending_offer.name == "Soliloquy"


class BatchUpdateOffersTest:
    @mock.patch("pcapi.core.search.async_index_offer_ids")
    def test_activate_empty_list(self, mocked_async_index_offer_ids, caplog):
        pending_offer = factories.OfferFactory(validation=models.OfferValidationStatus.PENDING)

        query = models.Offer.query.filter(models.Offer.id.in_({pending_offer.id}))
        with caplog.at_level(logging.INFO):
            api.batch_update_offers(query, {"isActive": True})

        assert not models.Offer.query.get(pending_offer.id).isActive
        mocked_async_index_offer_ids.assert_not_called()

        assert len(caplog.records) == 1
        record = caplog.records[0]

        assert record.message == "Batch update of offers"
        assert record.extra == {
            "nb_offers": 0,
            "updated_fields": {"isActive": True},
            "venue_ids": [],
        }

    @mock.patch("pcapi.core.search.async_index_offer_ids")
    def test_activate(self, mocked_async_index_offer_ids, caplog):
        offer1 = factories.OfferFactory(isActive=False)
        offer2 = factories.OfferFactory(isActive=False)
        offer3 = factories.OfferFactory(isActive=False)
        rejected_offer = factories.OfferFactory(isActive=False, validation=models.OfferValidationStatus.REJECTED)
        pending_offer = factories.OfferFactory(validation=models.OfferValidationStatus.PENDING)

        query = models.Offer.query.filter(
            models.Offer.id.in_({offer1.id, offer2.id, rejected_offer.id, pending_offer.id})
        )
        with caplog.at_level(logging.INFO):
            api.batch_update_offers(query, {"isActive": True})

        assert models.Offer.query.get(offer1.id).isActive
        assert models.Offer.query.get(offer2.id).isActive
        assert not models.Offer.query.get(offer3.id).isActive
        assert not models.Offer.query.get(rejected_offer.id).isActive
        assert not models.Offer.query.get(pending_offer.id).isActive
        mocked_async_index_offer_ids.assert_called_once()
        assert set(mocked_async_index_offer_ids.call_args[0][0]) == set([offer1.id, offer2.id])

        assert len(caplog.records) == 1
        record = caplog.records[0]

        assert record.message == "Batch update of offers"
        assert record.extra == {
            "nb_offers": 2,
            "updated_fields": {"isActive": True},
            "venue_ids": [offer1.venueId, offer2.venueId],
        }

    def test_deactivate(self, caplog):
        offer1 = factories.OfferFactory()
        offer2 = factories.OfferFactory()
        offer3 = factories.OfferFactory()

        query = models.Offer.query.filter(models.Offer.id.in_({offer1.id, offer2.id}))
        with caplog.at_level(logging.INFO):
            api.batch_update_offers(query, {"isActive": False})

        assert not models.Offer.query.get(offer1.id).isActive
        assert not models.Offer.query.get(offer2.id).isActive
        assert models.Offer.query.get(offer3.id).isActive

        assert len(caplog.records) == 1
        record = caplog.records[0]

        assert record.message == "Batch update of offers"
        assert record.extra == {
            "nb_offers": 2,
            "updated_fields": {"isActive": False},
            "venue_ids": [offer1.venueId, offer2.venueId],
        }


class UpdateStockIdAtProvidersTest:
    def test_update_and_stock_id_at_providers(self):
        # Given
        current_siret = "88888888888888"
        venue = offerers_factories.VenueFactory(siret=current_siret)
        offer = factories.OfferFactory(venue=venue, idAtProvider="1111111111111")
        stock = factories.StockFactory(offer=offer, idAtProviders="1111111111111@22222222222222")

        # When
        api.update_stock_id_at_providers(venue, "22222222222222")

        # Then
        assert stock.idAtProviders == "1111111111111@88888888888888"


class OfferExpenseDomainsTest:
    def test_offer_expense_domains(self):
        assert api.get_expense_domains(factories.OfferFactory(subcategoryId=subcategories.EVENEMENT_JEU.id)) == ["all"]
        assert set(
            api.get_expense_domains(
                factories.OfferFactory(subcategoryId=subcategories.JEU_EN_LIGNE.id, url="https://example.com")
            )
        ) == {
            "all",
            "digital",
        }
        assert set(api.get_expense_domains(factories.OfferFactory(subcategoryId=subcategories.OEUVRE_ART.id))) == {
            "all",
            "physical",
        }


class AddCriterionToOffersTest:
    @mock.patch("pcapi.core.search.async_index_offer_ids")
    def test_add_criteria_from_isbn(self, mocked_async_index_offer_ids):
        # Given
        isbn = "2-221-00164-8"
        product1 = factories.ProductFactory(extraData={"isbn": "2221001648"})
        offer11 = factories.OfferFactory(product=product1)
        offer12 = factories.OfferFactory(product=product1)
        product2 = factories.ProductFactory(extraData={"isbn": "2221001648"})
        offer21 = factories.OfferFactory(product=product2)
        inactive_offer = factories.OfferFactory(product=product1, isActive=False)
        unmatched_offer = factories.OfferFactory()
        criterion1 = criteria_factories.CriterionFactory(name="Pretty good books")
        criterion2 = criteria_factories.CriterionFactory(name="Other pretty good books")

        # When
        is_successful = api.add_criteria_to_offers([criterion1, criterion2], isbn=isbn)

        # Then
        assert is_successful is True
        assert set(offer11.criteria) == {criterion1, criterion2}
        assert set(offer12.criteria) == {criterion1, criterion2}
        assert set(offer21.criteria) == {criterion1, criterion2}
        assert not inactive_offer.criteria
        assert not unmatched_offer.criteria
        mocked_async_index_offer_ids.called_once_with([offer11.id, offer12.id, offer21.id])

    @mock.patch("pcapi.core.search.async_index_offer_ids")
    def test_add_criteria_from_isbn_when_one_has_criteria(self, mocked_async_index_offer_ids):
        # Given
        isbn = "2221001648"
        criterion1 = criteria_factories.CriterionFactory(name="Pretty good books")
        criterion2 = criteria_factories.CriterionFactory(name="Other pretty good books")
        product1 = factories.ProductFactory(extraData={"isbn": isbn})
        offer11 = factories.OfferFactory(product=product1, criteria=[criterion1])
        offer12 = factories.OfferFactory(product=product1, criteria=[criterion2])
        product2 = factories.ProductFactory(extraData={"isbn": isbn})
        offer21 = factories.OfferFactory(product=product2)
        inactive_offer = factories.OfferFactory(product=product1, isActive=False)
        unmatched_offer = factories.OfferFactory()

        # When
        is_successful = api.add_criteria_to_offers([criterion1, criterion2], isbn=isbn)

        # Then
        assert is_successful is True
        assert set(offer11.criteria) == {criterion1, criterion2}
        assert set(offer12.criteria) == {criterion1, criterion2}
        assert set(offer21.criteria) == {criterion1, criterion2}
        assert not inactive_offer.criteria
        assert not unmatched_offer.criteria
        mocked_async_index_offer_ids.called_once_with([offer11.id, offer12.id, offer21.id])

    @mock.patch("pcapi.core.search.async_index_offer_ids")
    def test_add_criteria_from_visa(self, mocked_async_index_offer_ids):
        # Given
        visa = "222100"
        product1 = factories.ProductFactory(extraData={"visa": visa})
        offer11 = factories.OfferFactory(product=product1)
        offer12 = factories.OfferFactory(product=product1)
        product2 = factories.ProductFactory(extraData={"visa": visa})
        offer21 = factories.OfferFactory(product=product2)
        inactive_offer = factories.OfferFactory(product=product1, isActive=False)
        unmatched_offer = factories.OfferFactory()
        criterion1 = criteria_factories.CriterionFactory(name="Pretty good books")
        criterion2 = criteria_factories.CriterionFactory(name="Other pretty good books")

        # When
        is_successful = api.add_criteria_to_offers([criterion1, criterion2], visa=visa)

        # Then
        assert is_successful is True
        assert set(offer11.criteria) == {criterion1, criterion2}
        assert set(offer12.criteria) == {criterion1, criterion2}
        assert set(offer21.criteria) == {criterion1, criterion2}
        assert not inactive_offer.criteria
        assert not unmatched_offer.criteria
        mocked_async_index_offer_ids.called_once_with([offer11.id, offer12.id, offer21.id])

    @mock.patch("pcapi.core.search.async_index_offer_ids")
    def test_add_criteria_when_no_offers_is_found(self, mocked_async_index_offer_ids):
        # Given
        isbn = "2-221-00164-8"
        factories.OfferFactory(extraData={"isbn": "2221001647"})
        criterion = criteria_factories.CriterionFactory(name="Pretty good books")

        # When
        is_successful = api.add_criteria_to_offers([criterion], isbn=isbn)

        # Then
        assert is_successful is False


class DeactivateInappropriateProductTest:
    @mock.patch("pcapi.core.search.async_index_offer_ids")
    def test_should_deactivate_product_with_inappropriate_content(self, mocked_async_index_offer_ids):
        # Given
        product1 = factories.ThingProductFactory(
            subcategoryId=subcategories.LIVRE_PAPIER.id, extraData={"isbn": "isbn-de-test"}
        )
        product2 = factories.ThingProductFactory(
            subcategoryId=subcategories.LIVRE_PAPIER.id, extraData={"isbn": "isbn-de-test"}
        )
        factories.OfferFactory(product=product1)
        factories.OfferFactory(product=product1)
        factories.OfferFactory(product=product2)

        # When
        api.reject_inappropriate_products("isbn-de-test")

        # Then
        products = models.Product.query.all()
        offers = models.Offer.query.all()

        assert not any(product.isGcuCompatible for product in products)
        assert all(offer.validation == OfferValidationStatus.REJECTED for offer in offers)
        mocked_async_index_offer_ids.assert_called_once()
        assert set(mocked_async_index_offer_ids.call_args[0][0]) == {o.id for o in offers}


class DeactivatePermanentlyUnavailableProductTest:
    @mock.patch("pcapi.core.search.async_index_offer_ids")
    def test_should_deactivate_permanently_unavailable_product(self, mocked_async_index_offer_ids):
        # Given
        product1 = factories.ThingProductFactory(
            subcategoryId=subcategories.LIVRE_PAPIER.id, extraData={"isbn": "isbn-de-test"}
        )
        product2 = factories.ThingProductFactory(
            subcategoryId=subcategories.LIVRE_PAPIER.id, extraData={"isbn": "isbn-de-test"}
        )
        factories.OfferFactory(product=product1)
        factories.OfferFactory(product=product1)
        factories.OfferFactory(product=product2)

        # When
        api.deactivate_permanently_unavailable_products("isbn-de-test")

        # Then
        products = models.Product.query.all()
        offers = models.Offer.query.all()

        assert any(product.name == "xxx" for product in products)
        assert not any(offer.isActive for offer in offers)
        assert any(offer.name == "xxx" for offer in offers)
        mocked_async_index_offer_ids.assert_called_once()
        assert set(mocked_async_index_offer_ids.call_args[0][0]) == {o.id for o in offers}


class ComputeOfferValidationTest:
    def test_approve_if_no_offer_validation_config(self):
        offer = models.Offer(name="Maybe we should reject this offer")

        assert api.set_offer_status_based_on_fraud_criteria(offer) == models.OfferValidationStatus.APPROVED

    def test_matching_keyword_in_name(self):
        offer = factories.OfferFactory(name="A suspicious offer")
        factories.StockFactory(price=10, offer=offer)
        api.import_offer_validation_config(SIMPLE_OFFER_VALIDATION_CONFIG)
        assert api.set_offer_status_based_on_fraud_criteria(offer) == models.OfferValidationStatus.PENDING


class UpdateOfferValidationStatusTest:
    def test_update_pending_offer_validation_status_to_approved(self):
        offer = factories.OfferFactory(validation=models.OfferValidationStatus.PENDING)

        is_offer_updated = api.update_pending_offer_validation(offer, models.OfferValidationStatus.APPROVED)

        assert is_offer_updated is True
        assert offer.validation == models.OfferValidationStatus.APPROVED
        assert offer.isActive is True

    def test_update_pending_offer_validation_status_to_rejected(self):
        offer = factories.OfferFactory(validation=models.OfferValidationStatus.PENDING)

        is_offer_updated = api.update_pending_offer_validation(offer, models.OfferValidationStatus.REJECTED)

        assert is_offer_updated is True
        assert offer.validation == models.OfferValidationStatus.REJECTED
        assert offer.isActive is False

    def test_cannot_update_pending_offer_validation_with_a_rejected_offer(self):
        offer = factories.OfferFactory(validation=models.OfferValidationStatus.REJECTED)

        is_offer_updated = api.update_pending_offer_validation(offer, models.OfferValidationStatus.APPROVED)

        assert is_offer_updated is False
        assert offer.validation == models.OfferValidationStatus.REJECTED

    @mock.patch("pcapi.core.search.async_index_offer_ids")
    def test_update_pending_offer_validation_status_and_reindex(self, mocked_async_index_offer_ids):
        offer = factories.OfferFactory(validation=models.OfferValidationStatus.PENDING)

        api.update_pending_offer_validation(offer, models.OfferValidationStatus.APPROVED)

        mocked_async_index_offer_ids.assert_called_once_with([offer.id])


class ImportOfferValidationConfigTest:
    def test_raise_a_WrongFormatInFraudConfigurationFile_error_for_key_error(self):
        config_yaml = """
        minimum_score: 0.6
        rules:
            - name: "check offer name"
              factor: 0
              conditions:
               - model: "Offer"
                 attribute: "name"
                 condition:
                    operator: "!="
                    WRONG_KEY: "REJECTED"
            - name: "price_all_types"
              factor: 0.7
              conditions:
               - model: "Offer"
                 attribute: "max_price"
                 condition:
                    operator: ">"
                    comparated: 100
        """
        with pytest.raises(exceptions.WrongFormatInFraudConfigurationFile) as error:
            api.import_offer_validation_config(config_yaml)
        assert str(error.value) == "\"'Wrong key: WRONG_KEY'\""

    def test_raise_a_WrongFormatInFraudConfigurationFile_error_for_wrong_type(self):
        config_yaml = """
            minimum_score: 0.6
            rules:
                - name: "nom de l'offre"
                  factor: "0"
                  conditions:
                    - model: "models.Offer"
                      attribute: "name"
                      condition:
                        operator: "not in"
                        comparated: "REJECTED"
                - name: "prix maximum"
                  factor: 0.2
                  conditions:
                    - model: "models.Offer"
                      attribute: "max_price"
                      condition:
                        operator: ">"
                        comparated: 100
            """
        with pytest.raises(exceptions.WrongFormatInFraudConfigurationFile) as error:
            api.import_offer_validation_config(config_yaml)
        assert "0" in str(error.value)

    def test_raise_a_WrongFormatInFraudConfigurationFile_error_for_wrong_leaf_value(self):
        config_yaml = """
            minimum_score: 0.6
            rules:
                - namme: "nom de l'offre"
                  factor: 0
                  conditions:
                    - model: "models.Offer"
                      attribute: "name"
                      condition:
                        operator: "not in"
                        comparated: "REJECTED"
                - name: "prix maximum"
                  conditions:
                    - model: "models.Offer"
                      attribute: "max_price"
                      condition:
                        operator: ">"
                        comparated: 100
            """
        with pytest.raises(exceptions.WrongFormatInFraudConfigurationFile) as error:
            api.import_offer_validation_config(config_yaml)
        assert "namme" in str(error.value)

    def test_raise_if_contains_comparated_not_a_list(self):
        config_yaml = """
            minimum_score: 0.6
            rules:
                - name: "nom de l'offre"
                  factor: 0
                  conditions:
                    - model: "Offer"
                      attribute: "name"
                      condition:
                        operator: "contains"
                        comparated: "danger"
            """

        with pytest.raises(TypeError) as exc:
            api.import_offer_validation_config(config_yaml)

        assert str(exc.value) == "The `comparated` argument `danger` for the `contains` operator is not a list"

    def test_is_saved(self):
        config_yaml = """
        minimum_score: 0.6
        rules:
            - name: "check offer name"
              factor: 0
              conditions:
               - model: "Offer"
                 attribute: "name"
                 condition:
                    operator: "!="
                    comparated: "REJECTED"
            - name: "price_all_types"
              factor: 0.7
              conditions:
               - model: "Offer"
                 attribute: "max_price"
                 condition:
                    operator: ">"
                    comparated: 100
        """
        api.import_offer_validation_config(config_yaml)

        current_config = models.OfferValidationConfig.query.one()
        assert current_config is not None
        assert current_config.specs["minimum_score"] == 0.6
        assert current_config.specs["rules"][0]["conditions"][0]["condition"]["comparated"] == "REJECTED"
        assert current_config.specs["rules"][1]["conditions"][0]["attribute"] == "max_price"


class ParseOfferValidationConfigTest:
    def test_parse_offer_validation_config(self):
        offer = factories.OfferFactory(name="REJECTED")
        config_yaml = """
        minimum_score: 0.6
        rules:
         - name: "modalités de retrait"
           factor: 0
           conditions:
            - model: "Offer"
              attribute: "withdrawalDetails"
              condition:
                operator: "contains"
                comparated:
                 - "Livraison"
                 - "Expédition"
                 - "à domicile"
                 - "Envoi"
            """
        offer_validation_config = api.import_offer_validation_config(config_yaml)
        min_score, validation_rules = offer_validation.parse_offer_validation_config(offer, offer_validation_config)
        assert min_score == 0.6
        assert len(validation_rules) == 1
        assert validation_rules[0].factor == 0
        assert validation_rules[0].name == "modalités de retrait"
        assert validation_rules[0].offer_validation_items[0].model == offer
        assert validation_rules[0].offer_validation_items[0].attribute == "withdrawalDetails"


class ComputeOfferValidationScoreTest:
    def test_offer_validation_with_one_item_config_with_in(self):
        offer = factories.OfferFactory(name="REJECTED")
        validation_item = offer_validation.OfferValidationItem(
            model=offer, attribute="name", type=["str"], condition={"operator": "in", "comparated": ["REJECTED"]}
        )
        validation_rules = offer_validation.OfferValidationRuleItem(
            name="nom de l'offre", factor=0.2, offer_validation_items=[validation_item]
        )

        score = offer_validation.compute_offer_validation_score([validation_rules])

        assert score == 0.2

    def test_offer_validation_with_one_item_config_with_greater_than(self):
        offer = factories.OfferFactory(name="REJECTED")
        factories.StockFactory(offer=offer, price=12)
        validation_item = offer_validation.OfferValidationItem(
            model=offer, attribute="max_price", type=["int"], condition={"operator": ">", "comparated": 10}
        )
        validation_rule = offer_validation.OfferValidationRuleItem(
            name="prix max", factor=0.2, offer_validation_items=[validation_item]
        )

        score = offer_validation.compute_offer_validation_score([validation_rule])

        assert score == 0.2

    def test_offer_validation_with_one_item_config_with_less_than(self):
        offer = factories.OfferFactory(name="REJECTED")
        factories.StockFactory(offer=offer, price=8)
        validation_item = offer_validation.OfferValidationItem(
            model=offer, attribute="max_price", type=["int"], condition={"operator": "<", "comparated": 10}
        )
        validation_rule = offer_validation.OfferValidationRuleItem(
            name="prix max", factor=0.2, offer_validation_items=[validation_item]
        )

        score = offer_validation.compute_offer_validation_score([validation_rule])

        assert score == 0.2

    def test_offer_validation_with_one_item_config_with_greater_or_equal_than(self):
        offer = factories.OfferFactory(name="REJECTED")
        factories.StockFactory(offer=offer, price=12)
        validation_item = offer_validation.OfferValidationItem(
            model=offer, attribute="max_price", type=["int"], condition={"operator": ">=", "comparated": 10}
        )
        validation_rule = offer_validation.OfferValidationRuleItem(
            name="prix max", factor=0.2, offer_validation_items=[validation_item]
        )

        score = offer_validation.compute_offer_validation_score([validation_rule])

        assert score == 0.2

    def test_offer_validation_with_one_item_config_with_less_or_equal_than(self):
        offer = factories.OfferFactory(name="REJECTED")
        factories.StockFactory(offer=offer, price=8)
        validation_item = offer_validation.OfferValidationItem(
            model=offer, attribute="max_price", type=["int"], condition={"operator": "<=", "comparated": 10}
        )
        validation_rule = offer_validation.OfferValidationRuleItem(
            name="prix max", factor=0.2, offer_validation_items=[validation_item]
        )

        score = offer_validation.compute_offer_validation_score([validation_rule])

        assert score == 0.2

    def test_offer_validation_with_one_item_config_with_equal(self):
        offer = factories.OfferFactory(name="test offer")
        factories.StockFactory(offer=offer, price=15)
        validation_item = offer_validation.OfferValidationItem(
            model=offer,
            attribute="name",
            type=["str"],
            condition={"operator": "==", "comparated": "test offer"},
        )
        validation_rule = offer_validation.OfferValidationRuleItem(
            name="nom de l'offre", factor=0.3, offer_validation_items=[validation_item]
        )
        score = offer_validation.compute_offer_validation_score([validation_rule])
        assert score == 0.3

    def test_offer_validation_with_one_item_config_with_not_in(self):
        offer = factories.OfferFactory(name="rejected")
        validation_item = offer_validation.OfferValidationItem(
            model=offer,
            attribute="name",
            type=["str"],
            condition={"operator": "not in", "comparated": "[approved]"},
        )
        validation_rule = offer_validation.OfferValidationRuleItem(
            name="nom de l'offre", factor=0.3, offer_validation_items=[validation_item]
        )
        score = offer_validation.compute_offer_validation_score([validation_rule])
        assert score == 0.3

    def test_offer_validation_with_multiple_item_config(self):
        offer = factories.OfferFactory(name="test offer")
        factories.StockFactory(offer=offer, price=15)
        validation_item_1 = offer_validation.OfferValidationItem(
            model=offer,
            attribute="name",
            type=["str"],
            condition={"operator": "==", "comparated": "test offer"},
        )
        validation_item_2 = offer_validation.OfferValidationItem(
            model=offer, attribute="max_price", type=["str"], condition={"operator": ">", "comparated": 10}
        )
        validation_rule_1 = offer_validation.OfferValidationRuleItem(
            name="nom de l'offre", factor=0.3, offer_validation_items=[validation_item_1]
        )
        validation_rule_2 = offer_validation.OfferValidationRuleItem(
            name="prix de l'offre", factor=0.2, offer_validation_items=[validation_item_2]
        )

        score = offer_validation.compute_offer_validation_score([validation_rule_1, validation_rule_2])
        assert score == 0.06

    def test_offer_validation_rule_with_multiple_conditions(self):
        offer = factories.OfferFactory(name="Livre")
        factories.StockFactory(offer=offer, price=75)
        validation_item_1 = offer_validation.OfferValidationItem(
            model=offer,
            attribute="name",
            type=["str"],
            condition={"operator": "==", "comparated": "Livre"},
        )
        validation_item_2 = offer_validation.OfferValidationItem(
            model=offer, attribute="max_price", type=["str"], condition={"operator": ">", "comparated": 70}
        )

        validation_rule = offer_validation.OfferValidationRuleItem(
            name="prix d'un livre", factor=0.5, offer_validation_items=[validation_item_1, validation_item_2]
        )

        score = offer_validation.compute_offer_validation_score([validation_rule])
        assert score == 0.5

    def test_offer_validation_with_emails_blacklist(self):

        venue = offerers_factories.VenueFactory(siret="12345678912345", bookingEmail="fake@yopmail.com")
        offer = factories.OfferFactory(name="test offer", venue=venue)
        factories.StockFactory(offer=offer, price=15)
        validation_item_1 = offer_validation.OfferValidationItem(
            model=venue,
            attribute="bookingEmail",
            type=["str"],
            condition={"operator": "contains", "comparated": ["yopmail.com", "suspect.com"]},
        )

        validation_rule = offer_validation.OfferValidationRuleItem(
            name="adresses mail", factor=0.3, offer_validation_items=[validation_item_1]
        )

        score = offer_validation.compute_offer_validation_score([validation_rule])
        assert score == 0.3

    def test_offer_validation_with_description_rule_and_offer_without_description(self):
        offer = factories.OfferFactory(name="test offer", description=None)
        factories.StockFactory(offer=offer, price=15)
        validation_item_1 = offer_validation.OfferValidationItem(
            model=offer,
            attribute="description",
            type=["str"],
            condition={"operator": "contains", "comparated": ["suspect", "fake"]},
        )
        validation_rule = offer_validation.OfferValidationRuleItem(
            name="description de l'offre", factor=0.3, offer_validation_items=[validation_item_1]
        )

        score = offer_validation.compute_offer_validation_score([validation_rule])
        assert score == 1

    def test_offer_validation_with_id_at_providers_is_none(self):
        offer = factories.OfferFactory(name="test offer", description=None)
        assert offer.idAtProvider is None
        factories.StockFactory(offer=offer, price=15)
        validation_item_1 = offer_validation.OfferValidationItem(
            model=offer,
            attribute="idAtProvider",
            type=["None"],
            condition={"operator": "==", "comparated": None},
        )
        validation_rule = offer_validation.OfferValidationRuleItem(
            name="offre non synchro", factor=0.3, offer_validation_items=[validation_item_1]
        )

        score = offer_validation.compute_offer_validation_score([validation_rule])
        assert score == 0.3

    def test_offer_validation_with_contains_exact_word(self):
        offer = factories.OfferFactory(name="test offer", description=None)
        assert offer.idAtProvider is None
        factories.StockFactory(offer=offer, price=15)
        validation_item_1 = offer_validation.OfferValidationItem(
            model=offer,
            attribute="name",
            type=["str"],
            condition={"operator": "contains-exact", "comparated": ["test"]},
        )
        validation_rule = offer_validation.OfferValidationRuleItem(
            name="offer name contains exact words", factor=0.3, offer_validation_items=[validation_item_1]
        )

        score = offer_validation.compute_offer_validation_score([validation_rule])
        assert score == 0.3


class LoadProductByIsbnAndCheckIsGCUCompatibleOrRaiseErrorTest:
    def test_returns_product_if_found_and_is_gcu_compatible(self):
        isbn = "2221001648"
        product = factories.ProductFactory(extraData={"isbn": isbn}, isGcuCompatible=True)

        result = api._load_product_by_isbn_and_check_is_gcu_compatible_or_raise_error(isbn)

        assert result == product

    def test_raise_api_error_if_no_product(self):
        factories.ProductFactory(isGcuCompatible=True)

        with pytest.raises(api_errors.ApiErrors) as error:
            api._load_product_by_isbn_and_check_is_gcu_compatible_or_raise_error("2221001649")

        assert error.value.errors["isbn"] == ["Ce produit n’est pas éligible au pass Culture."]

    def test_raise_api_error_if_product_is_not_gcu_compatible(self):
        isbn = "2221001648"
        factories.ProductFactory(extraData={"isbn": isbn}, isGcuCompatible=False)

        with pytest.raises(api_errors.ApiErrors) as error:
            api._load_product_by_isbn_and_check_is_gcu_compatible_or_raise_error(isbn)

        assert error.value.errors["isbn"] == ["Ce produit n’est pas éligible au pass Culture."]


@freeze_time("2020-01-05 10:00:00")
class UnindexExpiredOffersTest:
    @override_settings(ALGOLIA_DELETING_OFFERS_CHUNK_SIZE=2)
    @mock.patch("pcapi.core.search.unindex_offer_ids")
    def test_default_run(self, mock_unindex_offer_ids):
        # Given
        factories.StockFactory(bookingLimitDatetime=datetime(2020, 1, 2, 12, 0))
        stock1 = factories.StockFactory(bookingLimitDatetime=datetime(2020, 1, 3, 12, 0))
        stock2 = factories.StockFactory(bookingLimitDatetime=datetime(2020, 1, 3, 12, 0))
        stock3 = factories.StockFactory(bookingLimitDatetime=datetime(2020, 1, 4, 12, 0))
        factories.StockFactory(bookingLimitDatetime=datetime(2020, 1, 5, 12, 0))

        # When
        api.unindex_expired_offers()

        # Then
        assert mock_unindex_offer_ids.mock_calls == [
            mock.call([stock1.offerId, stock2.offerId]),
            mock.call([stock3.offerId]),
        ]

    @mock.patch("pcapi.core.search.unindex_offer_ids")
    def test_run_unlimited(self, mock_unindex_offer_ids):
        # more than 2 days ago, must be processed
        stock1 = factories.StockFactory(bookingLimitDatetime=datetime(2020, 1, 2, 12, 0))
        # today, must be ignored
        factories.StockFactory(bookingLimitDatetime=datetime(2020, 1, 5, 12, 0))

        # When
        api.unindex_expired_offers(process_all_expired=True)

        # Then
        assert mock_unindex_offer_ids.mock_calls == [
            mock.call([stock1.offerId]),
        ]


class DeleteUnwantedExistingProductTest:
    def test_delete_product_when_isbn_found(self):
        isbn = "1111111111111"
        product_to_delete = factories.ProductFactory(
            idAtProviders=isbn,
            isSynchronizationCompatible=True,
            subcategoryId=subcategories.LIVRE_PAPIER.id,
        )
        offer_to_delete = factories.OfferFactory(product=product_to_delete)
        factories.MediationFactory(offer=offer_to_delete)
        users_factories.FavoriteFactory(offer=offer_to_delete)
        product_to_keep_other_isbn = factories.ProductFactory(
            idAtProviders="something-else",
            isSynchronizationCompatible=True,
            subcategoryId=subcategories.LIVRE_PAPIER.id,
        )

        api.delete_unwanted_existing_product("1111111111111")

        assert models.Product.query.all() == [product_to_keep_other_isbn]
        assert models.Mediation.query.count() == 0
        assert models.Offer.query.count() == 0
        assert users_models.Favorite.query.count() == 0

    def test_keep_but_modify_product_if_booked(self):
        isbn = "1111111111111"
        product = factories.ProductFactory(
            idAtProviders=isbn,
            isGcuCompatible=True,
            isSynchronizationCompatible=True,
            subcategoryId=subcategories.LIVRE_PAPIER.id,
        )
        bookings_factories.BookingFactory(stock__offer__product=product)

        with pytest.raises(exceptions.CannotDeleteProductWithBookings):
            api.delete_unwanted_existing_product("1111111111111")

        offer = models.Offer.query.one()
        assert offer.isActive is False
        assert models.Product.query.one() == product
        assert not product.isGcuCompatible
        assert not product.isSynchronizationCompatible
