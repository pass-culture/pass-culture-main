import copy
import dataclasses
from datetime import datetime
from datetime import timedelta
import os
import pathlib
from unittest import mock

import dateutil
from freezegun import freeze_time
import pytest

import pcapi.core.bookings.factories as bookings_factories
from pcapi.core.bookings.models import Booking
from pcapi.core.bookings.models import BookingCancellationReasons
from pcapi.core.bookings.models import BookingStatus
from pcapi.core.categories import subcategories
from pcapi.core.educational import exceptions as educational_exceptions
import pcapi.core.mails.testing as mails_testing
from pcapi.core.mails.transactional.sendinblue_template_ids import TransactionalEmail
from pcapi.core.offers import api
from pcapi.core.offers import exceptions as offer_exceptions
from pcapi.core.offers import factories as offer_factories
from pcapi.core.offers import models as offer_models
from pcapi.core.offers import offer_validation
import pcapi.core.payments.factories as payments_factories
import pcapi.core.providers.factories as providers_factories
from pcapi.core.testing import override_features
from pcapi.core.testing import override_settings
import pcapi.core.users.factories as users_factories
from pcapi.models import api_errors
from pcapi.models.product import Product
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
        offer = offer_factories.ThingOfferFactory()
        existing_stock = offer_factories.StockFactory(offer=offer, price=10)
        created_stock_data = stock_serialize.StockCreationBodyModel(price=10, quantity=7)
        edited_stock_data = stock_serialize.StockEditionBodyModel(id=existing_stock.id, price=5, quantity=7)

        # When
        stocks_upserted = api.upsert_stocks(
            offer_id=offer.id, stock_data_list=[created_stock_data, edited_stock_data], user=user
        )

        # Then
        created_stock = offer_models.Stock.query.filter_by(id=stocks_upserted[0].id).first()
        assert created_stock.offer == offer
        assert created_stock.price == 10
        assert created_stock.quantity == 7
        edited_stock = offer_models.Stock.query.filter_by(id=existing_stock.id).first()
        assert edited_stock.price == 5
        assert edited_stock.quantity == 7
        mocked_async_index_offer_ids.assert_called_once_with([offer.id])

    @freeze_time("2020-11-17 15:00:00")
    def test_upsert_stocks_triggers_draft_offer_validation(self):
        api.import_offer_validation_config(SIMPLE_OFFER_VALIDATION_CONFIG)
        # Given draft offers and new stock data
        user = users_factories.ProFactory()
        draft_approvable_offer = offer_factories.OfferFactory(
            name="a great offer", validation=offer_models.OfferValidationStatus.DRAFT
        )
        draft_suspicious_offer = offer_factories.OfferFactory(
            name="A suspicious offer", validation=offer_models.OfferValidationStatus.DRAFT
        )
        created_stock_data = stock_serialize.StockCreationBodyModel(price=10, quantity=7)

        # When stocks are upserted
        api.upsert_stocks(offer_id=draft_approvable_offer.id, stock_data_list=[created_stock_data], user=user)
        api.upsert_stocks(offer_id=draft_suspicious_offer.id, stock_data_list=[created_stock_data], user=user)

        # Then validations statuses are correctly computed
        assert draft_approvable_offer.validation == offer_models.OfferValidationStatus.APPROVED
        assert draft_approvable_offer.isActive
        assert draft_approvable_offer.lastValidationDate == datetime(2020, 11, 17, 15, 0)
        assert draft_suspicious_offer.validation == offer_models.OfferValidationStatus.PENDING
        assert not draft_suspicious_offer.isActive
        assert draft_suspicious_offer.lastValidationDate == datetime(2020, 11, 17, 15, 0)

    def test_upsert_stocks_does_not_trigger_approved_offer_validation(self):
        # Given offers with stock and new stock data
        user = users_factories.ProFactory()
        approved_offer = offer_factories.OfferFactory(name="a great offer that should be REJECTED")
        offer_factories.StockFactory(offer=approved_offer, price=10)
        created_stock_data = stock_serialize.StockCreationBodyModel(price=8, quantity=7)

        # When stocks are upserted
        api.upsert_stocks(offer_id=approved_offer.id, stock_data_list=[created_stock_data], user=user)

        # Then validations status is not recomputed
        assert approved_offer.validation == offer_models.OfferValidationStatus.APPROVED
        assert approved_offer.isActive

    def test_sends_email_if_beginning_date_changes_on_edition(self):
        # Given
        user = users_factories.ProFactory()
        offer = offer_factories.EventOfferFactory(bookingEmail="offer@bookingemail.fr")
        existing_stock = offer_factories.StockFactory(offer=offer, price=10)
        beginning = datetime.now() + timedelta(days=10)
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
        stock = offer_models.Stock.query.one()
        assert stock.beginningDatetime == beginning

        assert len(mails_testing.outbox) == 2
        assert mails_testing.outbox[0].sent_data["template"] == dataclasses.asdict(
            TransactionalEmail.EVENT_OFFER_POSTPONED_CONFIRMATION_TO_PRO.value
        )
        assert mails_testing.outbox[0].sent_data["To"] == "offer@bookingemail.fr"
        assert mails_testing.outbox[1].sent_data["template"] == dataclasses.asdict(
            TransactionalEmail.BOOKING_POSTPONED_BY_PRO_TO_BENEFICIARY.value
        )
        assert mails_testing.outbox[1].sent_data["To"] == "beneficiary@bookingEmail.fr"

    @mock.patch("pcapi.core.offers.api.update_cancellation_limit_dates")
    def should_update_bookings_cancellation_limit_date_if_report_of_event(self, mock_update_cancellation_limit_dates):
        # Given
        user = users_factories.ProFactory()
        now = datetime.now()
        event_in_4_days = now + timedelta(days=4)
        event_reported_in_10_days = now + timedelta(days=10)
        offer = offer_factories.EventOfferFactory(bookingEmail="test@bookingEmail.fr")
        existing_stock = offer_factories.StockFactory(offer=offer, beginningDatetime=event_in_4_days)
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
        now = datetime.now()
        booking_made_3_days_ago = now - timedelta(days=3)
        event_in_4_days = now + timedelta(days=4)
        event_reported_in_10_days = now + timedelta(days=10)
        offer = offer_factories.EventOfferFactory(bookingEmail="test@bookingEmail.fr")
        existing_stock = offer_factories.StockFactory(offer=offer, beginningDatetime=event_in_4_days)
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
        updated_booking = Booking.query.get(booking.id)
        assert updated_booking.status is not BookingStatus.USED
        assert updated_booking.dateUsed is None
        assert updated_booking.cancellationLimitDate == booking.cancellationLimitDate

    def should_not_invalidate_booking_token_when_event_is_reported_in_less_than_48_hours(self):
        # Given
        user = users_factories.ProFactory()
        now = datetime.now()
        date_used_in_48_hours = datetime.now() + timedelta(days=2)
        event_in_3_days = now + timedelta(days=3)
        event_reported_in_less_48_hours = now + timedelta(days=1)
        offer = offer_factories.EventOfferFactory(bookingEmail="test@bookingEmail.fr")
        existing_stock = offer_factories.StockFactory(offer=offer, beginningDatetime=event_in_3_days)
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
        updated_booking = Booking.query.get(booking.id)
        assert updated_booking.status is BookingStatus.USED
        assert updated_booking.dateUsed == date_used_in_48_hours

    def test_does_not_allow_edition_of_stock_of_another_offer_than_given(self):
        # Given
        user = users_factories.ProFactory()
        offer = offer_factories.ThingOfferFactory()
        other_offer = offer_factories.ThingOfferFactory()
        existing_stock_on_other_offer = offer_factories.StockFactory(offer=other_offer, price=10)
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
        offer = offer_factories.ThingOfferFactory()
        existing_stock = offer_factories.StockFactory(offer=offer, price=10)
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
        offer = offer_factories.ThingOfferFactory()
        existing_stock = offer_factories.StockFactory(offer=offer, price=10)
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
        offer = offer_factories.ThingOfferFactory()
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
        existing_stock = offer_factories.ThingStockFactory(price=10)
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
        offer = offer_factories.EventOfferFactory()
        now = datetime.now()
        created_stock_data = stock_serialize.StockCreationBodyModel(
            price=301, beginningDatetime=now, bookingLimitDatetime=now
        )

        # When
        api.upsert_stocks(offer_id=offer.id, stock_data_list=[created_stock_data], user=user)

        # Then
        created_stock = offer_models.Stock.query.one()
        assert created_stock.price == 301

    def test_allow_price_above_300_euros_on_edition_for_individual_event_offers(self):
        # Given
        user = users_factories.ProFactory()
        existing_stock = offer_factories.EventStockFactory(price=10, offer__bookingEmail="test@bookingEmail.fr")
        now = datetime.now()
        edited_stock_data = stock_serialize.StockEditionBodyModel(
            id=existing_stock.id, price=301, beginningDatetime=now, bookingLimitDatetime=now
        )

        # When
        api.upsert_stocks(offer_id=existing_stock.offer.id, stock_data_list=[edited_stock_data], user=user)

        # Then
        assert existing_stock.price == 301

        # Given
        user = users_factories.ProFactory()
        existing_stock = offer_factories.EducationalThingStockFactory(price=10)
        edited_stock_data = stock_serialize.StockEditionBodyModel(id=existing_stock.id, price=301)

        # When
        api.upsert_stocks(offer_id=existing_stock.offer.id, stock_data_list=[edited_stock_data], user=user)

        # Then
        assert existing_stock.price == 301

    def test_cannot_edit_price_if_reimbursement_rule_exists(self):
        user = users_factories.AdminFactory()
        stock = offer_factories.ThingStockFactory(price=10)
        payments_factories.CustomReimbursementRuleFactory(offer=stock.offer)

        data = stock_serialize.StockEditionBodyModel(id=stock.id, price=9)
        with pytest.raises(api_errors.ApiErrors) as error:
            api.upsert_stocks(offer_id=stock.offerId, stock_data_list=[data], user=user)
        assert error.value.errors["price"][0].startswith("Vous ne pouvez pas modifier le prix")

    def test_cannot_create_stock_with_different_price_if_reimbursement_rule_exists(self):
        # If a stock exists with a price, we cannot add a new stock
        # with another price.
        user = users_factories.AdminFactory()
        stock = offer_factories.ThingStockFactory(price=10)
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
        stock = offer_factories.ThingStockFactory(price=10, isSoftDeleted=True)
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
        offer = offer_factories.ThingOfferFactory()
        payments_factories.CustomReimbursementRuleFactory(offer=offer)

        data = stock_serialize.StockCreationBodyModel(price=9)
        with pytest.raises(api_errors.ApiErrors) as error:
            api.upsert_stocks(offer_id=offer.id, stock_data_list=[data], user=user)
        assert error.value.errors["price"][0].startswith("Vous ne pouvez pas modifier le prix")

    def test_does_not_allow_beginning_datetime_on_thing_offer_on_creation_and_edition(self):
        # Given
        user = users_factories.ProFactory()
        offer = offer_factories.ThingOfferFactory()
        beginning_date = datetime.utcnow() + timedelta(days=4)
        existing_stock = offer_factories.StockFactory(offer=offer, price=10)
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
        offer = offer_factories.DigitalOfferFactory()
        created_stock_data = stock_serialize.StockCreationBodyModel(
            price=0,
            bookingLimitDatetime=None,
            activationCodesExpirationDatetime=datetime.now(),
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
        offer = offer_factories.DigitalOfferFactory()
        existing_stock = offer_factories.StockFactory(offer=offer)
        offer_factories.ActivationCodeFactory(expirationDate=datetime.now(), stock=existing_stock)
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
        offer = offer_factories.ThingOfferFactory()
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
        offer = offer_factories.EventOfferFactory()
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
        offer = offer_factories.EventOfferFactory()
        beginning_date = datetime.utcnow() + timedelta(days=4)
        booking_limit = beginning_date + timedelta(days=4)
        created_stock_data = stock_serialize.StockCreationBodyModel(
            price=10, beginningDatetime=beginning_date, bookingLimitDatetime=booking_limit
        )

        # When
        with pytest.raises(api_errors.ApiErrors) as error:
            api.upsert_stocks(offer_id=offer.id, stock_data_list=[created_stock_data], user=user)

        # Then
        assert error.value.errors == {
            "bookingLimitDatetime": [
                "La date limite de réservation pour cette offre est postérieure à la date de début de l'évènement"
            ]
        }

    def test_does_not_allow_edition_of_a_past_event_stock(self):
        # Given
        user = users_factories.ProFactory()
        offer = offer_factories.ThingOfferFactory()
        date_in_the_past = datetime.utcnow() - timedelta(days=4)
        existing_stock = offer_factories.StockFactory(offer=offer, price=10, beginningDatetime=date_in_the_past)
        edited_stock_data = stock_serialize.StockEditionBodyModel(id=existing_stock.id, price=4)

        # When
        with pytest.raises(api_errors.ApiErrors) as error:
            api.upsert_stocks(offer_id=offer.id, stock_data_list=[edited_stock_data], user=user)

        # Then
        assert error.value.errors == {"global": ["Les événements passés ne sont pas modifiables"]}

    def test_does_not_allow_upsert_stocks_on_a_synchronized_offer(self):
        # Given
        user = users_factories.ProFactory()
        offer = offer_factories.ThingOfferFactory(
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
        offer = offer_factories.EventOfferFactory(
            lastProvider=providers_factories.AllocineProviderFactory(localClass="AllocineStocks")
        )
        date_in_the_future = datetime.utcnow() + timedelta(days=4)
        existing_stock = offer_factories.StockFactory(offer=offer, price=10, beginningDatetime=date_in_the_future)
        edited_stock_data = stock_serialize.StockEditionBodyModel(
            id=existing_stock.id,
            beginningDatetime=existing_stock.beginningDatetime,
            bookingLimitDatetime=existing_stock.bookingLimitDatetime,
            price=4,
        )

        # When
        api.upsert_stocks(offer_id=offer.id, stock_data_list=[edited_stock_data], user=user)

        # Then
        edited_stock = offer_models.Stock.query.filter_by(id=existing_stock.id).first()
        assert edited_stock.price == 4

    def test_does_not_allow_edition_of_beginningDateTime_for_stocks_of_offers_synchronized_with_allocine(self):
        # Given
        user = users_factories.ProFactory()
        offer = offer_factories.EventOfferFactory(
            lastProvider=providers_factories.AllocineProviderFactory(localClass="AllocineStocks")
        )
        date_in_the_future = datetime.utcnow() + timedelta(days=4)
        other_date_in_the_future = datetime.utcnow() + timedelta(days=6)
        existing_stock = offer_factories.StockFactory(offer=offer, price=10, beginningDatetime=date_in_the_future)
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

    def test_create_stock_for_non_approved_offer_fails(self):
        user = users_factories.ProFactory()
        offer = offer_factories.ThingOfferFactory(validation=offer_models.OfferValidationStatus.PENDING)
        created_stock_data = stock_serialize.StockCreationBodyModel(price=10, quantity=7)

        with pytest.raises(api_errors.ApiErrors) as error:
            api.upsert_stocks(offer_id=offer.id, stock_data_list=[created_stock_data], user=user)

        assert error.value.errors == {
            "global": ["Les offres refusées ou en attente de validation ne sont pas modifiables"]
        }
        assert offer_models.Stock.query.count() == 0

    def test_edit_stock_of_non_approved_offer_fails(self):
        user = users_factories.ProFactory()
        offer = offer_factories.ThingOfferFactory(validation=offer_models.OfferValidationStatus.PENDING)
        existing_stock = offer_factories.StockFactory(offer=offer, price=10)
        edited_stock_data = stock_serialize.StockEditionBodyModel(id=existing_stock.id, price=5, quantity=7)

        with pytest.raises(api_errors.ApiErrors) as error:
            api.upsert_stocks(offer_id=offer.id, stock_data_list=[edited_stock_data], user=user)

        assert error.value.errors == {
            "global": ["Les offres refusées ou en attente de validation ne sont pas modifiables"]
        }
        existing_stock = offer_models.Stock.query.one()
        assert existing_stock.price == 10

    @mock.patch("pcapi.domain.admin_emails.send_offer_creation_notification_to_administration")
    @mock.patch("pcapi.core.offers.api.set_offer_status_based_on_fraud_criteria")
    def test_send_email_when_offer_automatically_approved_based_on_fraud_criteria(
        self, mocked_set_offer_status_based_on_fraud_criteria, mocked_offer_creation_notification_to_admin
    ):
        user = users_factories.ProFactory()
        offer = offer_factories.ThingOfferFactory(validation=offer_models.OfferValidationStatus.DRAFT)
        created_stock_data = stock_serialize.StockCreationBodyModel(price=10, quantity=7)
        mocked_set_offer_status_based_on_fraud_criteria.return_value = offer_models.OfferValidationStatus.APPROVED

        api.upsert_stocks(offer_id=offer.id, stock_data_list=[created_stock_data], user=user)

        mocked_offer_creation_notification_to_admin.assert_called_once_with(offer)

    @mock.patch("pcapi.domain.admin_emails.send_offer_creation_notification_to_administration")
    @mock.patch("pcapi.core.offers.api.set_offer_status_based_on_fraud_criteria")
    def test_not_send_email_when_offer_pass_to_pending_based_on_fraud_criteria(
        self, mocked_set_offer_status_based_on_fraud_criteria, mocked_offer_creation_notification_to_admin
    ):
        user = users_factories.ProFactory()
        offer = offer_factories.ThingOfferFactory(validation=offer_models.OfferValidationStatus.DRAFT)
        created_stock_data = stock_serialize.StockCreationBodyModel(price=10, quantity=7)
        mocked_set_offer_status_based_on_fraud_criteria.return_value = offer_models.OfferValidationStatus.PENDING

        api.upsert_stocks(offer_id=offer.id, stock_data_list=[created_stock_data], user=user)

        assert not mocked_offer_creation_notification_to_admin.called


@freeze_time("2020-11-17 15:00:00")
class CreateEducationalOfferStocksTest:
    @mock.patch("pcapi.core.search.async_index_offer_ids")
    def should_create_one_stock_on_educational_offer_stock_creation(self, mocked_async_index_offer_ids):
        # Given
        user_pro = users_factories.ProFactory()
        offer = offer_factories.EducationalEventOfferFactory()
        new_stock = stock_serialize.EducationalStockCreationBodyModel(
            offerId=offer.id,
            beginningDatetime=dateutil.parser.parse("2021-12-15T20:00:00Z"),
            bookingLimitDatetime=dateutil.parser.parse("2021-12-05T00:00:00Z"),
            totalPrice=1200,
            numberOfTickets=35,
        )

        # When
        stock_created = api.create_educational_stock(stock_data=new_stock, user=user_pro)

        # Then
        stock = offer_models.Stock.query.filter_by(id=stock_created.id).one()
        assert stock.beginningDatetime == datetime.fromisoformat("2021-12-15T20:00:00")
        assert stock.bookingLimitDatetime == datetime.fromisoformat("2021-12-05T00:00:00")
        assert stock.price == 1200
        assert stock.quantity == 1
        assert stock.numberOfTickets == 35
        mocked_async_index_offer_ids.assert_called_once_with([offer.id])

    def should_set_booking_limit_datetime_to_beginning_datetime_when_not_provided(self):
        # Given
        user_pro = users_factories.ProFactory()
        offer = offer_factories.EducationalEventOfferFactory()
        new_stock = stock_serialize.EducationalStockCreationBodyModel(
            offerId=offer.id,
            beginningDatetime=dateutil.parser.parse("2021-12-15T20:00:00Z"),
            totalPrice=1200,
            numberOfTickets=35,
        )

        # When
        stock_created = api.create_educational_stock(stock_data=new_stock, user=user_pro)

        # Then
        stock = offer_models.Stock.query.filter_by(id=stock_created.id).one()
        assert stock.bookingLimitDatetime == dateutil.parser.parse("2021-12-15T20:00:00")

    def should_not_allow_educational_stock_creation_when_offer_not_educational(self):
        # Given
        user_pro = users_factories.ProFactory()
        offer = offer_factories.EventOfferFactory()
        new_stock = stock_serialize.EducationalStockCreationBodyModel(
            offerId=offer.id,
            beginningDatetime=dateutil.parser.parse("2022-01-17T22:00:00Z"),
            bookingLimitDatetime=dateutil.parser.parse("2021-12-31T20:00:00Z"),
            totalPrice=1500,
            numberOfTickets=38,
        )

        # When
        with pytest.raises(educational_exceptions.OfferIsNotEducational) as error:
            api.create_educational_stock(stock_data=new_stock, user=user_pro)

        # Then
        assert error.value.errors == {"offer": [f"L'offre {offer.id} n'est pas une offre éducationnelle"]}
        saved_stocks = offer_models.Stock.query.all()
        assert len(saved_stocks) == 0

    def test_create_stock_triggers_draft_offer_validation(self):
        # Given
        api.import_offer_validation_config(SIMPLE_OFFER_VALIDATION_CONFIG)
        user_pro = users_factories.ProFactory()
        draft_approvable_offer = offer_factories.EducationalEventOfferFactory(
            name="a great offer", validation=offer_models.OfferValidationStatus.DRAFT
        )
        draft_suspicious_offer = offer_factories.EducationalEventOfferFactory(
            name="a suspicious offer", validation=offer_models.OfferValidationStatus.DRAFT
        )
        common_created_stock_data = {
            "beginningDatetime": dateutil.parser.parse("2022-01-17T22:00:00Z"),
            "bookingLimitDatetime": dateutil.parser.parse("2021-12-31T20:00:00Z"),
            "totalPrice": 1500,
            "numberOfTickets": 38,
        }
        created_stock_data_approvable = stock_serialize.EducationalStockCreationBodyModel(
            offerId=draft_approvable_offer.id, **common_created_stock_data
        )
        created_stock_data_suspicious = stock_serialize.EducationalStockCreationBodyModel(
            offerId=draft_suspicious_offer.id, **common_created_stock_data
        )

        # When
        api.create_educational_stock(stock_data=created_stock_data_approvable, user=user_pro)
        api.create_educational_stock(stock_data=created_stock_data_suspicious, user=user_pro)

        # Then
        assert draft_approvable_offer.validation == offer_models.OfferValidationStatus.APPROVED
        assert draft_approvable_offer.isActive
        assert draft_approvable_offer.lastValidationDate == datetime(2020, 11, 17, 15, 0)
        assert draft_suspicious_offer.validation == offer_models.OfferValidationStatus.PENDING
        assert not draft_suspicious_offer.isActive
        assert draft_suspicious_offer.lastValidationDate == datetime(2020, 11, 17, 15, 0)

    def test_create_stock_for_non_approved_offer_fails(self):
        # Given
        user = users_factories.ProFactory()
        offer = offer_factories.EducationalEventOfferFactory(validation=offer_models.OfferValidationStatus.PENDING)
        created_stock_data = stock_serialize.EducationalStockCreationBodyModel(
            offerId=offer.id,
            beginningDatetime=dateutil.parser.parse("2022-01-17T22:00:00Z"),
            bookingLimitDatetime=dateutil.parser.parse("2021-12-31T20:00:00Z"),
            totalPrice=1500,
            numberOfTickets=38,
        )

        # When
        with pytest.raises(api_errors.ApiErrors) as error:
            api.create_educational_stock(stock_data=created_stock_data, user=user)

        # Then
        assert error.value.errors == {
            "global": ["Les offres refusées ou en attente de validation ne sont pas modifiables"]
        }
        assert offer_models.Stock.query.count() == 0

    @mock.patch("pcapi.domain.admin_emails.send_offer_creation_notification_to_administration")
    @mock.patch("pcapi.core.offers.api.set_offer_status_based_on_fraud_criteria")
    def test_send_email_when_offer_automatically_approved_based_on_fraud_criteria(
        self, mocked_set_offer_status_based_on_fraud_criteria, mocked_offer_creation_notification_to_admin
    ):
        # Given
        user = users_factories.ProFactory()
        offer = offer_factories.EducationalEventOfferFactory(validation=offer_models.OfferValidationStatus.DRAFT)
        created_stock_data = stock_serialize.EducationalStockCreationBodyModel(
            offerId=offer.id,
            beginningDatetime=dateutil.parser.parse("2022-01-17T22:00:00Z"),
            bookingLimitDatetime=dateutil.parser.parse("2021-12-31T20:00:00Z"),
            totalPrice=1500,
            numberOfTickets=38,
        )
        mocked_set_offer_status_based_on_fraud_criteria.return_value = offer_models.OfferValidationStatus.APPROVED

        # When
        api.create_educational_stock(stock_data=created_stock_data, user=user)

        # Then
        mocked_offer_creation_notification_to_admin.assert_called_once_with(offer)

    @mock.patch("pcapi.domain.admin_emails.send_offer_creation_notification_to_administration")
    @mock.patch("pcapi.core.offers.api.set_offer_status_based_on_fraud_criteria")
    def test_not_send_email_when_offer_pass_to_pending_based_on_fraud_criteria(
        self, mocked_set_offer_status_based_on_fraud_criteria, mocked_offer_creation_notification_to_admin
    ):
        # Given
        user = users_factories.ProFactory()
        offer = offer_factories.EducationalEventOfferFactory(validation=offer_models.OfferValidationStatus.DRAFT)
        created_stock_data = stock_serialize.EducationalStockCreationBodyModel(
            offerId=offer.id,
            beginningDatetime=dateutil.parser.parse("2022-01-17T22:00:00Z"),
            bookingLimitDatetime=dateutil.parser.parse("2021-12-31T20:00:00Z"),
            totalPrice=1500,
            numberOfTickets=38,
        )
        mocked_set_offer_status_based_on_fraud_criteria.return_value = offer_models.OfferValidationStatus.PENDING

        # When
        api.create_educational_stock(stock_data=created_stock_data, user=user)

        # Then
        assert not mocked_offer_creation_notification_to_admin.called


class EditEducationalOfferStocksTest:
    def test_should_update_all_fields_when_all_changed(self):
        # Given
        initial_event_date = datetime.now() + timedelta(days=5)
        initial_booking_limit_date = datetime.now() + timedelta(days=3)
        stock_to_be_updated = offer_factories.EducationalEventStockFactory(
            beginningDatetime=initial_event_date,
            price=1200,
            quantity=1,
            numberOfTickets=30,
            bookingLimitDatetime=initial_booking_limit_date,
        )
        new_stock_data = stock_serialize.EducationalStockEditionBodyModel(
            beginningDatetime=datetime.now() + timedelta(days=7, hours=5),
            bookingLimitDatetime=datetime.now() + timedelta(days=5, hours=16),
            totalPrice=1500,
            numberOfTickets=35,
        )

        # When
        api.edit_educational_stock(stock=stock_to_be_updated, stock_data=new_stock_data.dict(exclude_unset=True))

        # Then
        stock = offer_models.Stock.query.filter_by(id=stock_to_be_updated.id).one()
        assert stock.beginningDatetime == new_stock_data.beginningDatetime
        assert stock.bookingLimitDatetime == new_stock_data.bookingLimitDatetime
        assert stock.price == 1500
        assert stock.numberOfTickets == 35

    def test_should_update_some_fields_and_keep_non_edited_ones(self):
        # Given
        initial_event_date = datetime.now() + timedelta(days=5)
        initial_booking_limit_date = datetime.now() + timedelta(days=3)
        stock_to_be_updated = offer_factories.EducationalEventStockFactory(
            beginningDatetime=initial_event_date,
            price=1200,
            quantity=1,
            numberOfTickets=30,
            bookingLimitDatetime=initial_booking_limit_date,
        )
        new_stock_data = stock_serialize.EducationalStockEditionBodyModel(
            beginningDatetime=datetime.now() + timedelta(days=7, hours=5),
            numberOfTickets=35,
        )

        # When
        api.edit_educational_stock(stock=stock_to_be_updated, stock_data=new_stock_data.dict(exclude_unset=True))

        # Then
        stock = offer_models.Stock.query.filter_by(id=stock_to_be_updated.id).one()
        assert stock.beginningDatetime == new_stock_data.beginningDatetime
        assert stock.bookingLimitDatetime == initial_booking_limit_date
        assert stock.price == 1200
        assert stock.numberOfTickets == 35

    def test_should_update_educational_booking_amount(self):
        # Given
        initial_event_date = datetime.now() + timedelta(days=5)
        initial_booking_limit_date = datetime.now() + timedelta(days=3)
        stock_to_be_updated = offer_factories.EducationalEventStockFactory(
            beginningDatetime=initial_event_date,
            price=1200,
            quantity=1,
            numberOfTickets=30,
            bookingLimitDatetime=initial_booking_limit_date,
        )
        booking = bookings_factories.EducationalBookingFactory(
            amount=1200,
            status=BookingStatus.PENDING,
            stock=stock_to_be_updated,
            educationalBooking__confirmationLimitDate=initial_booking_limit_date,
        )

        new_stock_data = stock_serialize.EducationalStockEditionBodyModel(totalPrice=1400)

        # When
        api.edit_educational_stock(stock=stock_to_be_updated, stock_data=new_stock_data.dict(exclude_unset=True))

        # Then
        stock = offer_models.Stock.query.filter_by(id=stock_to_be_updated.id).one()
        assert stock.price == 1400
        assert booking.amount == 1400
        assert booking.educationalBooking.confirmationLimitDate == initial_booking_limit_date

    def test_should_replace_bookingLimitDatetime_with_new_event_datetime_if_provided_but_none(self):
        # Given
        initial_event_date = datetime.now() + timedelta(days=5)
        initial_booking_limit_date = datetime.now() + timedelta(days=3)
        stock_to_be_updated = offer_factories.EducationalEventStockFactory(
            beginningDatetime=initial_event_date,
            bookingLimitDatetime=initial_booking_limit_date,
        )
        new_event_datetime = datetime.now() + timedelta(days=7, hours=5)
        new_stock_data = stock_serialize.EducationalStockEditionBodyModel(
            beginningDatetime=new_event_datetime,
            bookingLimitDatetime=None,
        )

        # When
        api.edit_educational_stock(stock=stock_to_be_updated, stock_data=new_stock_data.dict(exclude_unset=True))

        # Then
        stock = offer_models.Stock.query.filter_by(id=stock_to_be_updated.id).one()
        assert stock.bookingLimitDatetime == new_event_datetime

    def test_should_replace_bookingLimitDatetime_with_old_event_datetime_if_provided_but_none_and_event_date_unchanged(
        self,
    ):
        # Given
        initial_event_date = datetime.now() + timedelta(days=5)
        initial_booking_limit_date = datetime.now() + timedelta(days=3)
        stock_to_be_updated = offer_factories.EducationalEventStockFactory(
            beginningDatetime=initial_event_date,
            bookingLimitDatetime=initial_booking_limit_date,
        )
        new_stock_data = stock_serialize.EducationalStockEditionBodyModel(
            bookingLimitDatetime=None,
        )

        # When
        api.edit_educational_stock(stock=stock_to_be_updated, stock_data=new_stock_data.dict(exclude_unset=True))

        # Then
        stock = offer_models.Stock.query.filter_by(id=stock_to_be_updated.id).one()
        assert stock.bookingLimitDatetime == initial_event_date

    @mock.patch("pcapi.core.search.async_index_offer_ids")
    def test_should_reindex_offer_on_algolia(self, mocked_async_index_offer_ids):
        # Given
        initial_event_date = datetime.now() + timedelta(days=5)
        initial_booking_limit_date = datetime.now() + timedelta(days=3)
        stock_to_be_updated = offer_factories.EducationalEventStockFactory(
            beginningDatetime=initial_event_date,
            price=1200,
            quantity=1,
            numberOfTickets=30,
            bookingLimitDatetime=initial_booking_limit_date,
        )
        new_stock_data = stock_serialize.EducationalStockEditionBodyModel(
            beginningDatetime=datetime.now() + timedelta(days=7, hours=5),
            numberOfTickets=35,
        )

        # When
        api.edit_educational_stock(stock=stock_to_be_updated, stock_data=new_stock_data.dict(exclude_unset=True))

        # Then
        stock = offer_models.Stock.query.filter_by(id=stock_to_be_updated.id).one()
        mocked_async_index_offer_ids.assert_called_once_with([stock.offerId])

    def test_should_not_allow_stock_edition_when_booking_status_is_not_PENDING(self):
        # Given
        stock_to_be_updated = offer_factories.EducationalEventStockFactory(price=1200, quantity=1, dnBookedQuantity=1)
        bookings_factories.UsedEducationalBookingFactory(stock=stock_to_be_updated)

        new_stock_data = stock_serialize.EducationalStockEditionBodyModel(
            totalPrice=1500,
        )

        # When
        with pytest.raises(offer_exceptions.EducationalOfferStockBookedAndBookingNotPending):
            api.edit_educational_stock(stock=stock_to_be_updated, stock_data=new_stock_data.dict(exclude_unset=True))

        # Then
        stock = offer_models.Stock.query.filter_by(id=stock_to_be_updated.id).first()
        assert stock.price == 1200

    def should_update_bookings_cancellation_limit_date_if_event_postponed(self):
        # Given
        initial_event_date = datetime.now() + timedelta(days=20)
        cancellation_limit_date = datetime.now() + timedelta(days=5)
        stock_to_be_updated = offer_factories.EducationalEventStockFactory(
            beginningDatetime=initial_event_date, quantity=1, dnBookedQuantity=1
        )
        booking = bookings_factories.EducationalBookingFactory(
            stock=stock_to_be_updated, status=BookingStatus.PENDING, cancellation_limit_date=cancellation_limit_date
        )

        new_event_date = datetime.now() + timedelta(days=25, hours=5)
        new_stock_data = stock_serialize.EducationalStockEditionBodyModel(
            beginningDatetime=new_event_date,
        )

        # When
        api.edit_educational_stock(stock=stock_to_be_updated, stock_data=new_stock_data.dict(exclude_unset=True))

        # Then
        booking_updated = Booking.query.filter_by(id=booking.id).one()
        assert booking_updated.cancellationLimitDate == new_event_date - timedelta(days=15)

    @freeze_time("2020-11-17 15:00:00")
    def should_update_bookings_cancellation_limit_date_if_beginningDatetime_earlier(self):
        # Given
        initial_event_date = datetime.utcnow() + timedelta(days=20)
        cancellation_limit_date = datetime.utcnow() + timedelta(days=5)
        stock_to_be_updated = offer_factories.EducationalEventStockFactory(
            beginningDatetime=initial_event_date, quantity=1, dnBookedQuantity=1
        )
        booking = bookings_factories.EducationalBookingFactory(
            stock=stock_to_be_updated, status=BookingStatus.PENDING, cancellation_limit_date=cancellation_limit_date
        )

        new_event_date = datetime.utcnow() + timedelta(days=5, hours=5)
        new_stock_data = stock_serialize.EducationalStockEditionBodyModel(
            beginningDatetime=new_event_date,
            bookingLimitDatetime=datetime.utcnow() + timedelta(days=3, hours=5),
        )

        # When
        api.edit_educational_stock(stock=stock_to_be_updated, stock_data=new_stock_data.dict(exclude_unset=True))

        # Then
        booking_updated = Booking.query.filter_by(id=booking.id).one()
        assert booking_updated.cancellationLimitDate == datetime.utcnow()

    def test_should_allow_stock_edition_and_not_modify_cancellation_limit_date_when_booking_cancelled(self):
        # Given
        initial_event_date = datetime.now() + timedelta(days=20)
        cancellation_limit_date = datetime.now() + timedelta(days=5)
        stock_to_be_updated = offer_factories.EducationalEventStockFactory(
            beginningDatetime=initial_event_date, quantity=1, dnBookedQuantity=1
        )
        booking = bookings_factories.EducationalBookingFactory(
            stock=stock_to_be_updated, status=BookingStatus.CANCELLED, cancellation_limit_date=cancellation_limit_date
        )

        new_event_date = datetime.now() + timedelta(days=25, hours=5)
        new_stock_data = stock_serialize.EducationalStockEditionBodyModel(
            beginningDatetime=new_event_date,
        )

        # When
        api.edit_educational_stock(stock=stock_to_be_updated, stock_data=new_stock_data.dict(exclude_unset=True))

        # Then
        booking = Booking.query.filter_by(id=booking.id).one()
        assert booking.cancellationLimitDate == cancellation_limit_date
        stock = offer_models.Stock.query.filter_by(id=stock_to_be_updated.id).one()
        assert stock.beginningDatetime == new_event_date

    def test_does_not_allow_edition_of_an_expired_event_stock(self):
        # Given
        initial_event_date = datetime.now() - timedelta(days=1)
        initial_booking_limit_date = datetime.now() - timedelta(days=10)
        stock_to_be_updated = offer_factories.EducationalEventStockFactory(
            beginningDatetime=initial_event_date,
            price=1200,
            quantity=1,
            numberOfTickets=30,
            bookingLimitDatetime=initial_booking_limit_date,
        )
        new_stock_data = stock_serialize.EducationalStockEditionBodyModel(
            beginningDatetime=datetime.now() + timedelta(days=7, hours=5),
            numberOfTickets=35,
        )

        # When
        with pytest.raises(api_errors.ApiErrors) as error:
            api.edit_educational_stock(stock=stock_to_be_updated, stock_data=new_stock_data.dict(exclude_unset=True))

        # Then
        assert error.value.errors == {"global": ["Les événements passés ne sont pas modifiables"]}
        stock = offer_models.Stock.query.filter_by(id=stock_to_be_updated.id).first()
        assert stock.numberOfTickets == 30

    def test_edit_stock_of_non_approved_offer_fails(self):
        # Given
        offer = offer_factories.EducationalEventOfferFactory(validation=offer_models.OfferValidationStatus.PENDING)
        stock_to_be_updated = offer_factories.EducationalEventStockFactory(
            offer=offer,
            price=1200,
            quantity=1,
            numberOfTickets=30,
        )
        new_stock_data = stock_serialize.EducationalStockEditionBodyModel(
            numberOfTickets=35,
        )

        # When
        with pytest.raises(api_errors.ApiErrors) as error:
            api.edit_educational_stock(stock=stock_to_be_updated, stock_data=new_stock_data.dict(exclude_unset=True))

        # Then
        assert error.value.errors == {
            "global": ["Les offres refusées ou en attente de validation ne sont pas modifiables"]
        }
        stock = offer_models.Stock.query.filter_by(id=stock_to_be_updated.id).one()
        assert stock.numberOfTickets == 30

    def test_should_not_allow_stock_edition_if_offer_not_educational(self):
        # Given
        stock_to_be_updated = offer_factories.EventStockFactory(numberOfTickets=30)
        new_stock_data = stock_serialize.EducationalStockEditionBodyModel(
            numberOfTickets=35,
        )

        # When
        with pytest.raises(educational_exceptions.OfferIsNotEducational):
            api.edit_educational_stock(stock=stock_to_be_updated, stock_data=new_stock_data.dict(exclude_unset=True))

        # Then
        stock = offer_models.Stock.query.filter_by(id=stock_to_be_updated.id).one()
        assert stock.numberOfTickets == 30

    @freeze_time("2020-11-17 15:00:00")
    def test_should_not_allow_stock_edition_when_beginningDatetime_not_provided_and_bookingLimitDatetime_set_after_existing_event_datetime(
        self,
    ):
        # Given
        stock_to_be_updated = offer_factories.EducationalEventStockFactory(
            beginningDatetime=datetime(2021, 12, 10), bookingLimitDatetime=datetime(2021, 12, 5)
        )
        new_stock_data = stock_serialize.EducationalStockEditionBodyModel(bookingLimitDatetime=datetime(2021, 12, 20))

        # When
        with pytest.raises(offer_exceptions.BookingLimitDatetimeTooLate):
            api.edit_educational_stock(stock=stock_to_be_updated, stock_data=new_stock_data.dict(exclude_unset=True))

        # Then
        stock = offer_models.Stock.query.filter_by(id=stock_to_be_updated.id).one()
        assert stock.bookingLimitDatetime == datetime(2021, 12, 5)

    @freeze_time("2020-11-17 15:00:00")
    def test_should_not_allow_stock_edition_when_bookingLimitDatetime_not_provided_and_beginningDatetime_set_before_existing_event_datetime(
        self,
    ):
        # Given
        stock_to_be_updated = offer_factories.EducationalEventStockFactory(
            beginningDatetime=datetime(2021, 12, 10), bookingLimitDatetime=datetime(2021, 12, 5)
        )
        new_stock_data = stock_serialize.EducationalStockEditionBodyModel(beginningDatetime=datetime(2021, 12, 4))

        # When
        with pytest.raises(offer_exceptions.BookingLimitDatetimeTooLate):
            api.edit_educational_stock(stock=stock_to_be_updated, stock_data=new_stock_data.dict(exclude_unset=True))

        # Then
        stock = offer_models.Stock.query.filter_by(id=stock_to_be_updated.id).one()
        assert stock.beginningDatetime == datetime(2021, 12, 10)


class DeleteStockTest:
    @mock.patch("pcapi.core.search.async_index_offer_ids")
    def test_delete_stock_basics(self, mocked_async_index_offer_ids):
        stock = offer_factories.EventStockFactory()

        api.delete_stock(stock)

        stock = offer_models.Stock.query.one()
        assert stock.isSoftDeleted
        mocked_async_index_offer_ids.assert_called_once_with([stock.offerId])

    def test_delete_stock_cancel_bookings_and_send_emails(self):
        offerer_email = "offerer@example.com"
        stock = offer_factories.EventStockFactory(offer__bookingEmail=offerer_email)
        booking1 = bookings_factories.IndividualBookingFactory(
            stock=stock,
            individualBooking__user__email="beneficiary@example.com",
        )
        booking2 = bookings_factories.CancelledIndividualBookingFactory(stock=stock)
        booking3 = bookings_factories.UsedIndividualBookingFactory(stock=stock)

        api.delete_stock(stock)

        # cancellation can trigger more than one request to Batch
        assert len(push_testing.requests) >= 1

        stock = offer_models.Stock.query.one()
        assert stock.isSoftDeleted
        booking1 = Booking.query.get(booking1.id)
        assert booking1.status == BookingStatus.CANCELLED
        assert booking1.cancellationReason == BookingCancellationReasons.OFFERER
        booking2 = Booking.query.get(booking2.id)
        assert booking2.status == BookingStatus.CANCELLED  # unchanged
        assert booking2.cancellationReason == BookingCancellationReasons.BENEFICIARY
        booking3 = Booking.query.get(booking3.id)
        assert booking3.status == BookingStatus.CANCELLED  # cancel used booking for event offer
        assert booking3.cancellationReason == BookingCancellationReasons.OFFERER

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
            "user_ids": {booking1.individualBooking.userId, booking3.individualBooking.userId},
            "message": {
                "body": f"""Ta réservation "{stock.offer.name}" a été annulée par l'offreur.""",
                "title": "Réservation annulée",
            },
        }

    def test_can_delete_if_stock_from_allocine(self):
        provider = providers_factories.AllocineProviderFactory(localClass="AllocineStocks")
        offer = offer_factories.OfferFactory(lastProvider=provider, idAtProvider="1")
        stock = offer_factories.StockFactory(offer=offer)

        api.delete_stock(stock)

        stock = offer_models.Stock.query.one()
        assert stock.isSoftDeleted

    def test_cannot_delete_if_stock_from_titelive(self):
        provider = providers_factories.AllocineProviderFactory(localClass="TiteLiveStocks")
        offer = offer_factories.OfferFactory(lastProvider=provider, idAtProvider="1")
        stock = offer_factories.StockFactory(offer=offer)

        with pytest.raises(api_errors.ApiErrors) as error:
            api.delete_stock(stock)
        msg = "Les offres importées ne sont pas modifiables"
        assert error.value.errors["global"][0] == msg

        stock = offer_models.Stock.query.one()
        assert not stock.isSoftDeleted

    def test_can_delete_if_event_ended_recently(self):
        recently = datetime.now() - timedelta(days=1)
        stock = offer_factories.EventStockFactory(beginningDatetime=recently)

        api.delete_stock(stock)
        stock = offer_models.Stock.query.one()
        assert stock.isSoftDeleted

    def test_cannot_delete_if_too_late(self):
        too_long_ago = datetime.now() - timedelta(days=3)
        stock = offer_factories.EventStockFactory(beginningDatetime=too_long_ago)

        with pytest.raises(offer_exceptions.TooLateToDeleteStock):
            api.delete_stock(stock)
        stock = offer_models.Stock.query.one()
        assert not stock.isSoftDeleted


class CreateMediationV2Test:
    BASE_THUMBS_DIR = pathlib.Path(tests.__path__[0]) / ".." / "src" / "pcapi" / "static" / "object_store_data"
    THUMBS_DIR = BASE_THUMBS_DIR / "thumbs" / "mediations"

    @mock.patch("pcapi.core.search.async_index_offer_ids")
    @override_settings(LOCAL_STORAGE_DIR=BASE_THUMBS_DIR)
    def test_ok(self, mocked_async_index_offer_ids, clear_tests_assets_bucket):
        # Given
        user = users_factories.ProFactory()
        offer = offer_factories.ThingOfferFactory()
        image_as_bytes = (IMAGES_DIR / "mouette_full_size.jpg").read_bytes()

        # When
        api.create_mediation(user, offer, "©Photographe", image_as_bytes)

        # Then
        offer_models.mediation = offer_models.Mediation.query.one()
        assert offer_models.mediation.author == user
        assert offer_models.mediation.offer == offer
        assert offer_models.mediation.credit == "©Photographe"
        assert offer_models.mediation.thumbCount == 1
        assert offer_models.Mediation.query.filter(offer_models.Mediation.offerId == offer.id).count() == 1
        mocked_async_index_offer_ids.assert_called_once_with([offer.id])

    @override_settings(LOCAL_STORAGE_DIR=BASE_THUMBS_DIR)
    def test_erase_former_mediations(self, clear_tests_assets_bucket):
        # Given
        user = users_factories.ProFactory()
        offer = offer_factories.ThingOfferFactory()
        image_as_bytes = (IMAGES_DIR / "mouette_full_size.jpg").read_bytes()
        existing_number_of_files = len(os.listdir(self.THUMBS_DIR))

        mediation_1 = api.create_mediation(user, offer, "©Photographe", image_as_bytes)
        mediation_2 = api.create_mediation(user, offer, "©Alice", image_as_bytes)
        thumb_1_id = humanize(mediation_1.id)
        thumb_2_id = humanize(mediation_2.id)

        # When
        api.create_mediation(user, offer, "©moi", image_as_bytes)

        # Then
        offer_models.mediation_3 = offer_models.Mediation.query.one()
        assert offer_models.mediation_3.credit == "©moi"
        thumb_3_id = humanize(offer_models.mediation_3.id)

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
        offer = offer_factories.ThingOfferFactory()
        image_as_bytes = (IMAGES_DIR / "mouette_full_size.jpg").read_bytes()
        existing_number_of_files = len(os.listdir(self.THUMBS_DIR))

        # When
        with pytest.raises(offer_exceptions.ThumbnailStorageError):
            api.create_mediation(user, offer, "©Photographe", image_as_bytes)

        # Then
        assert offer_models.Mediation.query.count() == 0
        assert len(os.listdir(self.THUMBS_DIR)) == existing_number_of_files


class CreateOfferTest:
    def test_create_offer_from_scratch(self):
        venue = offer_factories.VenueFactory()
        offerer = venue.managingOfferer
        user_offerer = offer_factories.UserOffererFactory(offerer=offerer)
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
        assert offer.validation == offer_models.OfferValidationStatus.DRAFT
        assert not offer.bookingEmail
        assert offer_models.Offer.query.count() == 1

    @override_features(ENABLE_ISBN_REQUIRED_IN_LIVRE_EDITION_OFFER_CREATION=True)
    def test_create_offer_livre_edition_from_isbn_with_existing_product(self):
        offer_factories.ProductFactory(
            subcategoryId=subcategories.LIVRE_PAPIER.id,
            description="Les prévisions du psychohistorien Hari Seldon sont formelles.",
            extraData={"isbn": "9782207300893", "author": "Asimov", "bookFormat": "Soft cover"},
            isGcuCompatible=True,
        )
        venue = offer_factories.VenueFactory()
        offerer = venue.managingOfferer
        user_offerer = offer_factories.UserOffererFactory(offerer=offerer)
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
        assert Product.query.count() == 1

    @override_features(ENABLE_ISBN_REQUIRED_IN_LIVRE_EDITION_OFFER_CREATION=True)
    def test_create_offer_livre_edition_from_isbn_with_is_not_compatible_gcu_should_fail(self):
        offer_factories.ProductFactory(
            subcategoryId=subcategories.LIVRE_PAPIER.id,
            description="Les prévisions du psychohistorien Hari Seldon sont formelles.",
            extraData={"isbn": "9782207300893", "author": "Asimov", "bookFormat": "Soft cover"},
            isGcuCompatible=False,
        )

        venue = offer_factories.VenueFactory()
        offerer = venue.managingOfferer
        user_offerer = offer_factories.UserOffererFactory(offerer=offerer)
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
        venue = offer_factories.VenueFactory()
        offerer = venue.managingOfferer
        user_offerer = offer_factories.UserOffererFactory(offerer=offerer)
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
        venue = offer_factories.VenueFactory()
        user_offerer = offer_factories.UserOffererFactory(offerer=venue.managingOfferer)
        with pytest.raises(offer_exceptions.SubCategoryIsInactive) as error:
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
        venue = offer_factories.VenueFactory()
        user_offerer = offer_factories.UserOffererFactory(offerer=venue.managingOfferer)
        with pytest.raises(offer_exceptions.UnknownOfferSubCategory) as error:
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

    def test_create_educational_offer(self):
        venue = offer_factories.VenueFactory()
        offerer = venue.managingOfferer
        user_offerer = offer_factories.UserOffererFactory(offerer=offerer)
        user = user_offerer.user
        data = offers_serialize.PostOfferBodyModel(
            venueId=humanize(venue.id),
            name="A pretty good offer",
            subcategoryId=subcategories.SEANCE_CINE.id,
            externalTicketOfficeUrl="http://example.net",
            isEducational=True,
            audioDisabilityCompliant=True,
            mentalDisabilityCompliant=True,
            motorDisabilityCompliant=True,
            visualDisabilityCompliant=True,
        )
        offer = api.create_offer(data, user)

        assert offer.isEducational

    def test_cannot_create_educational_offer_when_not_eligible_subcategory(self):

        # Given
        unauthorized_subcategory_id = "BON_ACHAT_INSTRUMENT"
        venue = offer_factories.VenueFactory()
        offerer = venue.managingOfferer
        user_offerer = offer_factories.UserOffererFactory(offerer=offerer)
        user = user_offerer.user
        data = offers_serialize.PostOfferBodyModel(
            venueId=humanize(venue.id),
            name="A pretty good offer",
            subcategoryId=unauthorized_subcategory_id,
            externalTicketOfficeUrl="http://example.net",
            isEducational=True,
            audioDisabilityCompliant=True,
            mentalDisabilityCompliant=True,
            motorDisabilityCompliant=True,
            visualDisabilityCompliant=True,
        )

        # When
        with pytest.raises(offer_exceptions.SubcategoryNotEligibleForEducationalOffer) as error:
            api.create_offer(data, user)

        # Then
        assert error.value.errors["offer"] == ["Cette catégorie d'offre n'est pas éligible aux offres éducationnelles"]

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
        venue = offer_factories.VenueFactory()
        user = users_factories.ProFactory()
        data = offers_serialize.PostOfferBodyModel(
            venueId=humanize(venue.id),
            audioDisabilityCompliant=True,
            mentalDisabilityCompliant=True,
            motorDisabilityCompliant=True,
            visualDisabilityCompliant=True,
        )
        with pytest.raises(api_errors.ApiErrors) as error:
            api.create_offer(data, user)
        err = "Vous n'avez pas les droits d'accès suffisant pour accéder à cette information."
        assert error.value.errors["global"] == [err]


class UpdateOfferTest:
    @mock.patch("pcapi.core.search.async_index_offer_ids")
    def test_basics(self, mocked_async_index_offer_ids):
        offer = offer_factories.OfferFactory(isDuo=False, bookingEmail="old@example.com")

        offer = api.update_offer(offer, isDuo=True, bookingEmail="new@example.com")

        assert offer.isDuo
        assert offer.bookingEmail == "new@example.com"
        mocked_async_index_offer_ids.assert_called_once_with([offer.id])

    def test_update_product_if_owning_offerer_is_the_venue_managing_offerer(self):
        offerer = offer_factories.OffererFactory()
        product = offer_factories.ProductFactory(owningOfferer=offerer)
        offer = offer_factories.OfferFactory(product=product, venue__managingOfferer=offerer)

        offer = api.update_offer(offer, name="New name")

        assert offer.name == "New name"
        assert product.name == "New name"

    def test_do_not_update_product_if_owning_offerer_is_not_the_venue_managing_offerer(self):
        product = offer_factories.ProductFactory(name="Old name")
        offer = offer_factories.OfferFactory(product=product, name="Old name")

        offer = api.update_offer(offer, name="New name")

        assert offer.name == "New name"
        assert product.name == "Old name"

    def test_cannot_update_with_name_too_long(self):
        offer = offer_factories.OfferFactory(name="Old name")

        with pytest.raises(api_errors.ApiErrors) as error:
            api.update_offer(offer, name="Luftballons" * 99)

        assert error.value.errors == {"name": ["Vous devez saisir moins de 140 caractères"]}
        assert offer_models.Offer.query.one().name == "Old name"

    def test_success_on_allocine_offer(self):
        provider = providers_factories.AllocineProviderFactory(localClass="AllocineStocks")
        offer = offer_factories.OfferFactory(lastProvider=provider, name="Old name")

        api.update_offer(offer, name="Old name", isDuo=True)

        offer = offer_models.Offer.query.one()
        assert offer.name == "Old name"
        assert offer.isDuo

    def test_forbidden_on_allocine_offer_on_certain_fields(self):
        provider = providers_factories.AllocineProviderFactory(localClass="AllocineStocks")
        offer = offer_factories.OfferFactory(lastProvider=provider, name="Old name")

        with pytest.raises(api_errors.ApiErrors) as error:
            api.update_offer(offer, name="New name", isDuo=True)

        assert error.value.errors == {"name": ["Vous ne pouvez pas modifier ce champ"]}
        offer = offer_models.Offer.query.one()
        assert offer.name == "Old name"
        assert not offer.isDuo

    def test_success_on_imported_offer_on_external_ticket_office_url(self):
        provider = providers_factories.AllocineProviderFactory()
        offer = offer_factories.OfferFactory(
            externalTicketOfficeUrl="http://example.org",
            lastProvider=provider,
            name="Old name",
        )

        api.update_offer(
            offer,
            externalTicketOfficeUrl="https://example.com",
        )

        offer = offer_models.Offer.query.one()
        assert offer.name == "Old name"
        assert offer.externalTicketOfficeUrl == "https://example.com"

    def test_success_on_imported_offer_on_accessibility_fields(self):
        provider = providers_factories.AllocineProviderFactory()
        offer = offer_factories.OfferFactory(
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

        offer = offer_models.Offer.query.one()
        assert offer.name == "Old name"
        assert offer.audioDisabilityCompliant == False
        assert offer.visualDisabilityCompliant == True
        assert offer.motorDisabilityCompliant == True
        assert offer.mentalDisabilityCompliant == False

    def test_forbidden_on_imported_offer_on_other_fields(self):
        provider = providers_factories.APIProviderFactory()
        offer = offer_factories.OfferFactory(
            lastProvider=provider, name="Old name", isDuo=False, audioDisabilityCompliant=True
        )

        with pytest.raises(api_errors.ApiErrors) as error:
            api.update_offer(offer, name="New name", isDuo=True, audioDisabilityCompliant=False)

        assert error.value.errors == {
            "name": ["Vous ne pouvez pas modifier ce champ"],
            "isDuo": ["Vous ne pouvez pas modifier ce champ"],
        }
        offer = offer_models.Offer.query.one()
        assert offer.name == "Old name"
        assert offer.isDuo == False
        assert offer.audioDisabilityCompliant == True

    def test_update_non_approved_offer_fails(self):
        pending_offer = offer_factories.OfferFactory(
            name="Soliloquy", validation=offer_models.OfferValidationStatus.PENDING
        )

        with pytest.raises(api_errors.ApiErrors) as error:
            api.update_offer(pending_offer, name="Monologue")

        assert error.value.errors == {
            "global": ["Les offres refusées ou en attente de validation ne sont pas modifiables"]
        }
        pending_offer = offer_models.Offer.query.one()
        assert pending_offer.name == "Soliloquy"


class BatchUpdateOffersTest:
    @mock.patch("pcapi.core.search.async_index_offer_ids")
    def test_activate(self, mocked_async_index_offer_ids):
        offer1 = offer_factories.OfferFactory(isActive=False)
        offer2 = offer_factories.OfferFactory(isActive=False)
        offer3 = offer_factories.OfferFactory(isActive=False)
        rejected_offer = offer_factories.OfferFactory(
            isActive=False, validation=offer_models.OfferValidationStatus.REJECTED
        )
        pending_offer = offer_factories.OfferFactory(validation=offer_models.OfferValidationStatus.PENDING)

        query = offer_models.Offer.query.filter(
            offer_models.Offer.id.in_({offer1.id, offer2.id, rejected_offer.id, pending_offer.id})
        )
        api.batch_update_offers(query, {"isActive": True})

        assert offer_models.Offer.query.get(offer1.id).isActive
        assert offer_models.Offer.query.get(offer2.id).isActive
        assert not offer_models.Offer.query.get(offer3.id).isActive
        assert not offer_models.Offer.query.get(rejected_offer.id).isActive
        assert not offer_models.Offer.query.get(pending_offer.id).isActive
        mocked_async_index_offer_ids.assert_called_once()
        assert set(mocked_async_index_offer_ids.call_args[0][0]) == set([offer1.id, offer2.id])

    def test_deactivate(self):
        offer1 = offer_factories.OfferFactory()
        offer2 = offer_factories.OfferFactory()
        offer3 = offer_factories.OfferFactory()

        query = offer_models.Offer.query.filter(offer_models.Offer.id.in_({offer1.id, offer2.id}))
        api.batch_update_offers(query, {"isActive": False})

        assert not offer_models.Offer.query.get(offer1.id).isActive
        assert not offer_models.Offer.query.get(offer2.id).isActive
        assert offer_models.Offer.query.get(offer3.id).isActive


class UpdateStockIdAtProvidersTest:
    def test_update_and_stock_id_at_providers(self):
        # Given
        current_siret = "88888888888888"
        venue = offer_factories.VenueFactory(siret=current_siret)
        offer = offer_factories.OfferFactory(venue=venue, idAtProvider="1111111111111")
        stock = offer_factories.StockFactory(offer=offer, idAtProviders="1111111111111@22222222222222")

        # When
        api.update_stock_id_at_providers(venue, "22222222222222")

        # Then
        assert stock.idAtProviders == "1111111111111@88888888888888"


class OfferExpenseDomainsTest:
    def test_offer_expense_domains(self):
        assert api.get_expense_domains(offer_factories.OfferFactory(subcategoryId=subcategories.EVENEMENT_JEU.id)) == [
            "all"
        ]
        assert set(
            api.get_expense_domains(
                offer_factories.OfferFactory(subcategoryId=subcategories.JEU_EN_LIGNE.id, url="https://example.com")
            )
        ) == {
            "all",
            "digital",
        }
        assert set(
            api.get_expense_domains(offer_factories.OfferFactory(subcategoryId=subcategories.OEUVRE_ART.id))
        ) == {
            "all",
            "physical",
        }


class AddCriterionToOffersTest:
    @mock.patch("pcapi.core.search.async_index_offer_ids")
    def test_add_criteria_from_isbn(self, mocked_async_index_offer_ids):
        # Given
        isbn = "2-221-00164-8"
        product1 = offer_factories.ProductFactory(extraData={"isbn": "2221001648"})
        offer11 = offer_factories.OfferFactory(product=product1)
        offer12 = offer_factories.OfferFactory(product=product1)
        product2 = offer_factories.ProductFactory(extraData={"isbn": "2221001648"})
        offer21 = offer_factories.OfferFactory(product=product2)
        inactive_offer = offer_factories.OfferFactory(product=product1, isActive=False)
        unmatched_offer = offer_factories.OfferFactory()
        criterion1 = offer_factories.CriterionFactory(name="Pretty good books")
        criterion2 = offer_factories.CriterionFactory(name="Other pretty good books")

        # When
        is_successful = api.add_criteria_to_offers([criterion1, criterion2], isbn=isbn)

        # Then
        assert is_successful is True
        assert offer11.criteria == [criterion1, criterion2]
        assert offer12.criteria == [criterion1, criterion2]
        assert offer21.criteria == [criterion1, criterion2]
        assert not inactive_offer.criteria
        assert not unmatched_offer.criteria
        mocked_async_index_offer_ids.called_once_with([offer11.id, offer12.id, offer21.id])

    @mock.patch("pcapi.core.search.async_index_offer_ids")
    def test_add_criteria_from_visa(self, mocked_async_index_offer_ids):
        # Given
        visa = "222100"
        product1 = offer_factories.ProductFactory(extraData={"visa": visa})
        offer11 = offer_factories.OfferFactory(product=product1)
        offer12 = offer_factories.OfferFactory(product=product1)
        product2 = offer_factories.ProductFactory(extraData={"visa": visa})
        offer21 = offer_factories.OfferFactory(product=product2)
        inactive_offer = offer_factories.OfferFactory(product=product1, isActive=False)
        unmatched_offer = offer_factories.OfferFactory()
        criterion1 = offer_factories.CriterionFactory(name="Pretty good books")
        criterion2 = offer_factories.CriterionFactory(name="Other pretty good books")

        # When
        is_successful = api.add_criteria_to_offers([criterion1, criterion2], visa=visa)

        # Then
        assert is_successful is True
        assert offer11.criteria == [criterion1, criterion2]
        assert offer12.criteria == [criterion1, criterion2]
        assert offer21.criteria == [criterion1, criterion2]
        assert not inactive_offer.criteria
        assert not unmatched_offer.criteria
        mocked_async_index_offer_ids.called_once_with([offer11.id, offer12.id, offer21.id])

    @mock.patch("pcapi.core.search.async_index_offer_ids")
    def test_add_criteria_when_no_offers_is_found(self, mocked_async_index_offer_ids):
        # Given
        isbn = "2-221-00164-8"
        offer_factories.OfferFactory(extraData={"isbn": "2221001647"})
        criterion = offer_factories.CriterionFactory(name="Pretty good books")

        # When
        is_successful = api.add_criteria_to_offers([criterion], isbn=isbn)

        # Then
        assert is_successful is False


class DeactivateInappropriateProductTest:
    @mock.patch("pcapi.core.search.async_index_offer_ids")
    def test_should_deactivate_product_with_inappropriate_content(self, mocked_async_index_offer_ids):
        # Given
        product1 = offer_factories.ThingProductFactory(
            subcategoryId=subcategories.LIVRE_PAPIER.id, extraData={"isbn": "isbn-de-test"}
        )
        product2 = offer_factories.ThingProductFactory(
            subcategoryId=subcategories.LIVRE_PAPIER.id, extraData={"isbn": "isbn-de-test"}
        )
        offer_factories.OfferFactory(product=product1)
        offer_factories.OfferFactory(product=product1)
        offer_factories.OfferFactory(product=product2)

        # When
        api.deactivate_inappropriate_products("isbn-de-test")

        # Then
        products = Product.query.all()
        offers = offer_models.Offer.query.all()

        assert not any(product.isGcuCompatible for product in products)
        assert not any(offer.isActive for offer in offers)
        mocked_async_index_offer_ids.assert_called_once()
        assert set(mocked_async_index_offer_ids.call_args[0][0]) == {o.id for o in offers}


class ComputeOfferValidationTest:
    def test_approve_if_no_offer_validation_config(self):
        offer = offer_models.Offer(name="Maybe we should reject this offer")

        assert api.set_offer_status_based_on_fraud_criteria(offer) == offer_models.OfferValidationStatus.APPROVED

    def test_matching_keyword_in_name(self):
        offer = offer_factories.OfferFactory(name="A suspicious offer")
        offer_factories.StockFactory(price=10, offer=offer)
        api.import_offer_validation_config(SIMPLE_OFFER_VALIDATION_CONFIG)
        assert api.set_offer_status_based_on_fraud_criteria(offer) == offer_models.OfferValidationStatus.PENDING


class UpdateOfferValidationStatusTest:
    def test_update_pending_offer_validation_status_to_approved(self):
        offer = offer_factories.OfferFactory(validation=offer_models.OfferValidationStatus.PENDING)

        is_offer_updated = api.update_pending_offer_validation(offer, offer_models.OfferValidationStatus.APPROVED)

        assert is_offer_updated is True
        assert offer.validation == offer_models.OfferValidationStatus.APPROVED
        assert offer.isActive is True

    def test_update_pending_offer_validation_status_to_rejected(self):
        offer = offer_factories.OfferFactory(validation=offer_models.OfferValidationStatus.PENDING)

        is_offer_updated = api.update_pending_offer_validation(offer, offer_models.OfferValidationStatus.REJECTED)

        assert is_offer_updated is True
        assert offer.validation == offer_models.OfferValidationStatus.REJECTED
        assert offer.isActive is False

    def test_cannot_update_pending_offer_validation_with_a_rejected_offer(self):
        offer = offer_factories.OfferFactory(validation=offer_models.OfferValidationStatus.REJECTED)

        is_offer_updated = api.update_pending_offer_validation(offer, offer_models.OfferValidationStatus.APPROVED)

        assert is_offer_updated is False
        assert offer.validation == offer_models.OfferValidationStatus.REJECTED

    @mock.patch("pcapi.core.search.async_index_offer_ids")
    def test_update_pending_offer_validation_status_and_reindex(self, mocked_async_index_offer_ids):
        offer = offer_factories.OfferFactory(validation=offer_models.OfferValidationStatus.PENDING)

        api.update_pending_offer_validation(offer, offer_models.OfferValidationStatus.APPROVED)

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
        with pytest.raises(offer_exceptions.WrongFormatInFraudConfigurationFile) as error:
            api.import_offer_validation_config(config_yaml)
        assert str(error.value) == "\"'Wrong key: WRONG_KEY'\""

    def test_raise_a_WrongFormatInFraudConfigurationFile_error_for_wrong_type(self):
        config_yaml = """
            minimum_score: 0.6
            rules:
                - name: "nom de l'offre"
                  factor: "0"
                  conditions:
                    - model: "offer_models.Offer"
                      attribute: "name"
                      condition:
                        operator: "not in"
                        comparated: "REJECTED"
                - name: "prix maximum"
                  factor: 0.2
                  conditions:
                    - model: "offer_models.Offer"
                      attribute: "max_price"
                      condition:
                        operator: ">"
                        comparated: 100
            """
        with pytest.raises(offer_exceptions.WrongFormatInFraudConfigurationFile) as error:
            api.import_offer_validation_config(config_yaml)
        assert "0" in str(error.value)

    def test_raise_a_WrongFormatInFraudConfigurationFile_error_for_wrong_leaf_value(self):
        config_yaml = """
            minimum_score: 0.6
            rules:
                - namme: "nom de l'offre"
                  factor: 0
                  conditions:
                    - model: "offer_models.Offer"
                      attribute: "name"
                      condition:
                        operator: "not in"
                        comparated: "REJECTED"
                - name: "prix maximum"
                  conditions:
                    - model: "offer_models.Offer"
                      attribute: "max_price"
                      condition:
                        operator: ">"
                        comparated: 100
            """
        with pytest.raises(offer_exceptions.WrongFormatInFraudConfigurationFile) as error:
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

        current_config = offer_models.OfferValidationConfig.query.one()
        assert current_config is not None
        assert current_config.specs["minimum_score"] == 0.6
        assert current_config.specs["rules"][0]["conditions"][0]["condition"]["comparated"] == "REJECTED"
        assert current_config.specs["rules"][1]["conditions"][0]["attribute"] == "max_price"


class ParseOfferValidationConfigTest:
    def test_parse_offer_validation_config(self):
        offer = offer_factories.OfferFactory(name="REJECTED")
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
        offer = offer_factories.OfferFactory(name="REJECTED")
        validation_item = offer_validation.OfferValidationItem(
            model=offer, attribute="name", type=["str"], condition={"operator": "in", "comparated": ["REJECTED"]}
        )
        validation_rules = offer_validation.OfferValidationRuleItem(
            name="nom de l'offre", factor=0.2, offer_validation_items=[validation_item]
        )

        score = offer_validation.compute_offer_validation_score([validation_rules])

        assert score == 0.2

    def test_offer_validation_with_one_item_config_with_greater_than(self):
        offer = offer_factories.OfferFactory(name="REJECTED")
        offer_factories.StockFactory(offer=offer, price=12)
        validation_item = offer_validation.OfferValidationItem(
            model=offer, attribute="max_price", type=["int"], condition={"operator": ">", "comparated": 10}
        )
        validation_rule = offer_validation.OfferValidationRuleItem(
            name="prix max", factor=0.2, offer_validation_items=[validation_item]
        )

        score = offer_validation.compute_offer_validation_score([validation_rule])

        assert score == 0.2

    def test_offer_validation_with_one_item_config_with_less_than(self):
        offer = offer_factories.OfferFactory(name="REJECTED")
        offer_factories.StockFactory(offer=offer, price=8)
        validation_item = offer_validation.OfferValidationItem(
            model=offer, attribute="max_price", type=["int"], condition={"operator": "<", "comparated": 10}
        )
        validation_rule = offer_validation.OfferValidationRuleItem(
            name="prix max", factor=0.2, offer_validation_items=[validation_item]
        )

        score = offer_validation.compute_offer_validation_score([validation_rule])

        assert score == 0.2

    def test_offer_validation_with_one_item_config_with_greater_or_equal_than(self):
        offer = offer_factories.OfferFactory(name="REJECTED")
        offer_factories.StockFactory(offer=offer, price=12)
        validation_item = offer_validation.OfferValidationItem(
            model=offer, attribute="max_price", type=["int"], condition={"operator": ">=", "comparated": 10}
        )
        validation_rule = offer_validation.OfferValidationRuleItem(
            name="prix max", factor=0.2, offer_validation_items=[validation_item]
        )

        score = offer_validation.compute_offer_validation_score([validation_rule])

        assert score == 0.2

    def test_offer_validation_with_one_item_config_with_less_or_equal_than(self):
        offer = offer_factories.OfferFactory(name="REJECTED")
        offer_factories.StockFactory(offer=offer, price=8)
        validation_item = offer_validation.OfferValidationItem(
            model=offer, attribute="max_price", type=["int"], condition={"operator": "<=", "comparated": 10}
        )
        validation_rule = offer_validation.OfferValidationRuleItem(
            name="prix max", factor=0.2, offer_validation_items=[validation_item]
        )

        score = offer_validation.compute_offer_validation_score([validation_rule])

        assert score == 0.2

    def test_offer_validation_with_one_item_config_with_equal(self):
        offer = offer_factories.OfferFactory(name="test offer")
        offer_factories.StockFactory(offer=offer, price=15)
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
        offer = offer_factories.OfferFactory(name="rejected")
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
        offer = offer_factories.OfferFactory(name="test offer")
        offer_factories.StockFactory(offer=offer, price=15)
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
        offer = offer_factories.OfferFactory(name="Livre")
        offer_factories.StockFactory(offer=offer, price=75)
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

        venue = offer_factories.VenueFactory(siret="12345678912345", bookingEmail="fake@yopmail.com")
        offer = offer_factories.OfferFactory(name="test offer", venue=venue)
        offer_factories.StockFactory(offer=offer, price=15)
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
        offer = offer_factories.OfferFactory(name="test offer", description=None)
        offer_factories.StockFactory(offer=offer, price=15)
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
        offer = offer_factories.OfferFactory(name="test offer", description=None)
        assert offer.idAtProvider is None
        offer_factories.StockFactory(offer=offer, price=15)
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
        offer = offer_factories.OfferFactory(name="test offer", description=None)
        assert offer.idAtProvider is None
        offer_factories.StockFactory(offer=offer, price=15)
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
        product = offer_factories.ProductFactory(extraData={"isbn": isbn}, isGcuCompatible=True)

        result = api._load_product_by_isbn_and_check_is_gcu_compatible_or_raise_error(isbn)

        assert result == product

    def test_raise_api_error_if_no_product(self):
        offer_factories.ProductFactory(isGcuCompatible=True)

        with pytest.raises(api_errors.ApiErrors) as error:
            api._load_product_by_isbn_and_check_is_gcu_compatible_or_raise_error("2221001649")

        assert error.value.errors["isbn"] == ["Ce produit n’est pas éligible au pass Culture."]

    def test_raise_api_error_if_product_is_not_gcu_compatible(self):
        isbn = "2221001648"
        offer_factories.ProductFactory(extraData={"isbn": isbn}, isGcuCompatible=False)

        with pytest.raises(api_errors.ApiErrors) as error:
            api._load_product_by_isbn_and_check_is_gcu_compatible_or_raise_error(isbn)

        assert error.value.errors["isbn"] == ["Ce produit n’est pas éligible au pass Culture."]


@freeze_time("2020-01-05 10:00:00")
class UnindexExpiredOffersTest:
    @override_settings(ALGOLIA_DELETING_OFFERS_CHUNK_SIZE=2)
    @mock.patch("pcapi.core.search.unindex_offer_ids")
    def test_default_run(self, mock_unindex_offer_ids):
        # Given
        offer_factories.StockFactory(bookingLimitDatetime=datetime(2020, 1, 2, 12, 0))
        stock1 = offer_factories.StockFactory(bookingLimitDatetime=datetime(2020, 1, 3, 12, 0))
        stock2 = offer_factories.StockFactory(bookingLimitDatetime=datetime(2020, 1, 3, 12, 0))
        stock3 = offer_factories.StockFactory(bookingLimitDatetime=datetime(2020, 1, 4, 12, 0))
        offer_factories.StockFactory(bookingLimitDatetime=datetime(2020, 1, 5, 12, 0))

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
        stock1 = offer_factories.StockFactory(bookingLimitDatetime=datetime(2020, 1, 2, 12, 0))
        # today, must be ignored
        offer_factories.StockFactory(bookingLimitDatetime=datetime(2020, 1, 5, 12, 0))

        # When
        api.unindex_expired_offers(process_all_expired=True)

        # Then
        assert mock_unindex_offer_ids.mock_calls == [
            mock.call([stock1.offerId]),
        ]
