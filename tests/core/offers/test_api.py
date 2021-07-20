from datetime import datetime
from datetime import timedelta
import os
import pathlib
from unittest import mock

from freezegun import freeze_time
import pytest

from pcapi import models
import pcapi.core.bookings.factories as bookings_factories
from pcapi.core.bookings.models import Booking
from pcapi.core.bookings.models import BookingCancellationReasons
from pcapi.core.categories import subcategories
import pcapi.core.offerers.factories as offerers_factories
from pcapi.core.offers import api
from pcapi.core.offers import exceptions
from pcapi.core.offers import factories
from pcapi.core.offers.api import _load_product_by_isbn_and_check_is_gcu_compatible_or_raise_error
from pcapi.core.offers.api import add_criteria_to_offers
from pcapi.core.offers.api import deactivate_inappropriate_products
from pcapi.core.offers.api import get_expense_domains
from pcapi.core.offers.api import import_offer_validation_config
from pcapi.core.offers.api import set_offer_status_based_on_fraud_criteria
from pcapi.core.offers.api import update_offer_and_stock_id_at_providers
from pcapi.core.offers.api import update_pending_offer_validation
from pcapi.core.offers.exceptions import ThumbnailStorageError
from pcapi.core.offers.exceptions import WrongFormatInFraudConfigurationFile
from pcapi.core.offers.factories import ActivationCodeFactory
from pcapi.core.offers.factories import CriterionFactory
from pcapi.core.offers.factories import OfferFactory
from pcapi.core.offers.factories import ProductFactory
from pcapi.core.offers.factories import StockFactory
from pcapi.core.offers.factories import ThingProductFactory
from pcapi.core.offers.factories import VenueFactory
from pcapi.core.offers.models import Offer
from pcapi.core.offers.models import OfferValidationConfig
from pcapi.core.offers.models import OfferValidationStatus
from pcapi.core.offers.models import Stock
from pcapi.core.offers.offer_validation import OfferValidationItem
from pcapi.core.offers.offer_validation import OfferValidationRuleItem
from pcapi.core.offers.offer_validation import compute_offer_validation_score
from pcapi.core.offers.offer_validation import parse_offer_validation_config
from pcapi.core.testing import override_features
from pcapi.core.testing import override_settings
import pcapi.core.users.factories as users_factories
from pcapi.models import ApiErrors
from pcapi.models import api_errors
from pcapi.models import offer_type
from pcapi.models.product import Product
from pcapi.notifications.push import testing as push_testing
from pcapi.routes.serialization import offers_serialize
from pcapi.routes.serialization.stock_serialize import StockCreationBodyModel
from pcapi.routes.serialization.stock_serialize import StockEditionBodyModel
from pcapi.utils.human_ids import humanize

import tests


IMAGES_DIR = pathlib.Path(tests.__path__[0]) / "files"


@pytest.mark.usefixtures("db_session")
class UpsertStocksTest:
    @mock.patch("pcapi.core.search.async_index_offer_ids")
    def test_upsert_multiple_stocks(self, mocked_async_index_offer_ids):
        # Given
        user = users_factories.UserFactory()
        offer = factories.ThingOfferFactory()
        existing_stock = factories.StockFactory(offer=offer, price=10)
        created_stock_data = StockCreationBodyModel(price=10, quantity=7)
        edited_stock_data = StockEditionBodyModel(id=existing_stock.id, price=5, quantity=7)

        # When
        stocks_upserted = api.upsert_stocks(
            offer_id=offer.id, stock_data_list=[created_stock_data, edited_stock_data], user=user
        )

        # Then
        created_stock = Stock.query.filter_by(id=stocks_upserted[0].id).first()
        assert created_stock.offer == offer
        assert created_stock.price == 10
        assert created_stock.quantity == 7
        edited_stock = Stock.query.filter_by(id=existing_stock.id).first()
        assert edited_stock.price == 5
        assert edited_stock.quantity == 7
        mocked_async_index_offer_ids.assert_called_once_with([offer.id])

    @freeze_time("2020-11-17 15:00:00")
    def test_upsert_stocks_triggers_draft_offer_validation(self):
        # Given draft offers and new stock data
        user = users_factories.UserFactory()
        draft_approvable_offer = OfferFactory(name="a great offer", validation=OfferValidationStatus.DRAFT)
        draft_suspicious_offer = OfferFactory(name="An PENDING offer", validation=OfferValidationStatus.DRAFT)
        draft_fraudulent_offer = OfferFactory(name="A REJECTED offer", validation=OfferValidationStatus.DRAFT)
        created_stock_data = StockCreationBodyModel(price=10, quantity=7)

        # When stocks are upserted
        api.upsert_stocks(offer_id=draft_approvable_offer.id, stock_data_list=[created_stock_data], user=user)
        api.upsert_stocks(offer_id=draft_suspicious_offer.id, stock_data_list=[created_stock_data], user=user)
        api.upsert_stocks(offer_id=draft_fraudulent_offer.id, stock_data_list=[created_stock_data], user=user)

        # Then validations statuses are correctly computed
        assert draft_approvable_offer.validation == OfferValidationStatus.APPROVED
        assert draft_approvable_offer.isActive
        assert draft_approvable_offer.lastValidationDate == datetime(2020, 11, 17, 15, 0)
        assert draft_suspicious_offer.validation == OfferValidationStatus.PENDING
        assert not draft_suspicious_offer.isActive
        assert draft_suspicious_offer.lastValidationDate == datetime(2020, 11, 17, 15, 0)
        assert draft_fraudulent_offer.validation == OfferValidationStatus.REJECTED
        assert not draft_fraudulent_offer.isActive
        assert draft_fraudulent_offer.lastValidationDate == datetime(2020, 11, 17, 15, 0)

    def test_upsert_stocks_does_not_trigger_approved_offer_validation(self):
        # Given offers with stock and new stock data
        user = users_factories.UserFactory()
        approved_offer = OfferFactory(name="a great offer that should be REJECTED")
        factories.StockFactory(offer=approved_offer, price=10)
        created_stock_data = StockCreationBodyModel(price=8, quantity=7)

        # When stocks are upserted
        api.upsert_stocks(offer_id=approved_offer.id, stock_data_list=[created_stock_data], user=user)

        # Then validations status is not recomputed
        assert approved_offer.validation == OfferValidationStatus.APPROVED
        assert approved_offer.isActive

    @mock.patch("pcapi.domain.user_emails.send_batch_stock_postponement_emails_to_users")
    def test_sends_email_if_beginning_date_changes_on_edition(self, mocked_send_email):
        # Given
        user = users_factories.UserFactory()
        offer = factories.EventOfferFactory()
        existing_stock = factories.StockFactory(offer=offer, price=10)
        beginning = datetime.now() + timedelta(days=10)
        edited_stock_data = StockEditionBodyModel(
            id=existing_stock.id,
            beginningDatetime=beginning,
            bookingLimitDatetime=existing_stock.bookingLimitDatetime,
            price=2,
        )
        booking = bookings_factories.BookingFactory(stock=existing_stock)
        bookings_factories.BookingFactory(stock=existing_stock, isCancelled=True)

        # When
        api.upsert_stocks(offer_id=offer.id, stock_data_list=[edited_stock_data], user=user)

        # Then
        stock = models.Stock.query.one()
        assert stock.beginningDatetime == beginning
        notified_bookings = mocked_send_email.call_args_list[0][0][0]
        assert notified_bookings == [booking]

    @mock.patch("pcapi.core.offers.api.update_cancellation_limit_dates")
    def should_update_bookings_cancellation_limit_date_if_report_of_event(self, mock_update_cancellation_limit_dates):
        # Given
        user = users_factories.UserFactory()
        now = datetime.now()
        event_in_4_days = now + timedelta(days=4)
        event_reported_in_10_days = now + timedelta(days=10)
        offer = factories.EventOfferFactory()
        existing_stock = factories.StockFactory(offer=offer, beginningDatetime=event_in_4_days)
        booking = bookings_factories.BookingFactory(stock=existing_stock, dateCreated=now)
        edited_stock_data = StockEditionBodyModel(
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
        user = users_factories.UserFactory()
        now = datetime.now()
        booking_made_3_days_ago = now - timedelta(days=3)
        event_in_4_days = now + timedelta(days=4)
        event_reported_in_10_days = now + timedelta(days=10)
        offer = factories.EventOfferFactory()
        existing_stock = factories.StockFactory(offer=offer, beginningDatetime=event_in_4_days)
        booking = bookings_factories.BookingFactory(
            stock=existing_stock, dateCreated=booking_made_3_days_ago, isUsed=True
        )
        edited_stock_data = StockEditionBodyModel(
            id=existing_stock.id,
            beginningDatetime=event_reported_in_10_days,
            bookingLimitDatetime=existing_stock.bookingLimitDatetime,
            price=2,
        )

        # When
        api.upsert_stocks(offer_id=offer.id, stock_data_list=[edited_stock_data], user=user)

        # Then
        updated_booking = Booking.query.get(booking.id)
        assert updated_booking.isUsed is False
        assert updated_booking.dateUsed is None
        assert updated_booking.cancellationLimitDate == booking.cancellationLimitDate

    def should_not_invalidate_booking_token_when_event_is_reported_in_less_than_48_hours(self):
        # Given
        user = users_factories.UserFactory()
        now = datetime.now()
        date_used_in_48_hours = datetime.now() + timedelta(days=2)
        event_in_3_days = now + timedelta(days=3)
        event_reported_in_less_48_hours = now + timedelta(days=1)
        offer = factories.EventOfferFactory()
        existing_stock = factories.StockFactory(offer=offer, beginningDatetime=event_in_3_days)
        booking = bookings_factories.BookingFactory(
            stock=existing_stock, dateCreated=now, isUsed=True, dateUsed=date_used_in_48_hours
        )
        edited_stock_data = StockEditionBodyModel(
            id=existing_stock.id,
            beginningDatetime=event_reported_in_less_48_hours,
            bookingLimitDatetime=existing_stock.bookingLimitDatetime,
            price=2,
        )

        # When
        api.upsert_stocks(offer_id=offer.id, stock_data_list=[edited_stock_data], user=user)

        # Then
        updated_booking = Booking.query.get(booking.id)
        assert updated_booking.isUsed is True
        assert updated_booking.dateUsed == date_used_in_48_hours

    def test_does_not_allow_edition_of_stock_of_another_offer_than_given(self):
        # Given
        user = users_factories.UserFactory()
        offer = factories.ThingOfferFactory()
        other_offer = factories.ThingOfferFactory()
        existing_stock_on_other_offer = factories.StockFactory(offer=other_offer, price=10)
        edited_stock_data = StockEditionBodyModel(id=existing_stock_on_other_offer.id, price=30)

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
        user = users_factories.UserFactory()
        offer = factories.ThingOfferFactory()
        existing_stock = factories.StockFactory(offer=offer, price=10)
        created_stock_data = StockCreationBodyModel(price=10, quantity=-2)
        edited_stock_data = StockEditionBodyModel(id=existing_stock.id, price=30, quantity=-4)

        # When
        with pytest.raises(api_errors.ApiErrors) as error:
            api.upsert_stocks(offer_id=offer.id, stock_data_list=[created_stock_data, edited_stock_data], user=user)

        # Then
        assert error.value.errors == {"quantity": ["Le stock doit être positif"]}

    def test_does_not_allow_invalid_price_on_creation_and_edition(self):
        # Given
        user = users_factories.UserFactory()
        offer = factories.ThingOfferFactory()
        existing_stock = factories.StockFactory(offer=offer, price=10)
        created_stock_data = StockCreationBodyModel(price=-1)
        edited_stock_data = StockEditionBodyModel(id=existing_stock.id, price=-3)

        # When
        with pytest.raises(api_errors.ApiErrors) as error:
            api.upsert_stocks(offer_id=offer.id, stock_data_list=[created_stock_data, edited_stock_data], user=user)

        # Then
        assert error.value.errors == {
            "price": ["Le prix doit être positif"],
        }

    def test_does_not_allow_beginning_datetime_on_thing_offer_on_creation_and_edition(self):
        # Given
        user = users_factories.UserFactory()
        offer = factories.ThingOfferFactory()
        beginning_date = datetime.utcnow() + timedelta(days=4)
        existing_stock = factories.StockFactory(offer=offer, price=10)
        created_stock_data = StockCreationBodyModel(
            price=-1, beginningDatetime=beginning_date, bookingLimitDatetime=beginning_date
        )
        edited_stock_data = StockEditionBodyModel(
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
        user = users_factories.UserFactory()
        offer = factories.DigitalOfferFactory()
        created_stock_data = StockCreationBodyModel(
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
        user = users_factories.UserFactory()
        offer = factories.DigitalOfferFactory()
        existing_stock = factories.StockFactory(offer=offer)
        ActivationCodeFactory(expirationDate=datetime.now(), stock=existing_stock)
        edited_stock_data = StockEditionBodyModel(id=existing_stock.id, price=0, bookingLimitDatetime=None)

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
        user = users_factories.UserFactory()
        offer = factories.ThingOfferFactory()
        booking = bookings_factories.BookingFactory(stock__offer=offer, stock__quantity=10)
        existing_stock = booking.stock
        edited_stock_data = StockEditionBodyModel(id=existing_stock.id, quantity=0, price=10)

        # When
        with pytest.raises(api_errors.ApiErrors) as error:
            api.upsert_stocks(offer_id=offer.id, stock_data_list=[edited_stock_data], user=user)

        # Then
        assert error.value.errors == {"quantity": ["Le stock total ne peut être inférieur au nombre de réservations"]}

    def test_does_not_allow_missing_dates_for_an_event_offer_on_creation_and_edition(self):
        # Given
        user = users_factories.UserFactory()
        offer = factories.EventOfferFactory()
        created_stock_data = StockCreationBodyModel(price=10, beginningDatetime=None, bookingLimitDatetime=None)

        # When
        with pytest.raises(api_errors.ApiErrors) as error:
            api.upsert_stocks(offer_id=offer.id, stock_data_list=[created_stock_data], user=user)

        # Then
        assert error.value.errors == {"beginningDatetime": ["Ce paramètre est obligatoire"]}

    def test_does_not_allow_booking_limit_after_beginning_for_an_event_offer_on_creation_and_edition(self):
        # Given
        user = users_factories.UserFactory()
        offer = factories.EventOfferFactory()
        beginning_date = datetime.utcnow() + timedelta(days=4)
        booking_limit = beginning_date + timedelta(days=4)
        created_stock_data = StockCreationBodyModel(
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
        user = users_factories.UserFactory()
        offer = factories.ThingOfferFactory()
        date_in_the_past = datetime.utcnow() - timedelta(days=4)
        existing_stock = factories.StockFactory(offer=offer, price=10, beginningDatetime=date_in_the_past)
        edited_stock_data = StockEditionBodyModel(id=existing_stock.id, price=4)

        # When
        with pytest.raises(api_errors.ApiErrors) as error:
            api.upsert_stocks(offer_id=offer.id, stock_data_list=[edited_stock_data], user=user)

        # Then
        assert error.value.errors == {"global": ["Les événements passés ne sont pas modifiables"]}

    def test_does_not_allow_upsert_stocks_on_a_synchronized_offer(self):
        # Given
        user = users_factories.UserFactory()
        offer = factories.ThingOfferFactory(
            lastProvider=offerers_factories.AllocineProviderFactory(localClass="TiteLiveStocks")
        )
        created_stock_data = StockCreationBodyModel(price=10)

        # When
        with pytest.raises(api_errors.ApiErrors) as error:
            api.upsert_stocks(offer_id=offer.id, stock_data_list=[created_stock_data], user=user)

        # Then
        assert error.value.errors == {"global": ["Les offres importées ne sont pas modifiables"]}

    def test_allow_edition_of_price_and_quantity_for_stocks_of_offers_synchronized_with_allocine(self):
        # Given
        user = users_factories.UserFactory()
        offer = factories.EventOfferFactory(
            lastProvider=offerers_factories.AllocineProviderFactory(localClass="AllocineStocks")
        )
        date_in_the_future = datetime.utcnow() + timedelta(days=4)
        existing_stock = factories.StockFactory(offer=offer, price=10, beginningDatetime=date_in_the_future)
        edited_stock_data = StockEditionBodyModel(
            id=existing_stock.id,
            beginningDatetime=existing_stock.beginningDatetime,
            bookingLimitDatetime=existing_stock.bookingLimitDatetime,
            price=4,
        )

        # When
        api.upsert_stocks(offer_id=offer.id, stock_data_list=[edited_stock_data], user=user)

        # Then
        edited_stock = Stock.query.filter_by(id=existing_stock.id).first()
        assert edited_stock.price == 4

    def test_does_not_allow_edition_of_beginningDateTime_for_stocks_of_offers_synchronized_with_allocine(self):
        # Given
        user = users_factories.UserFactory()
        offer = factories.EventOfferFactory(
            lastProvider=offerers_factories.AllocineProviderFactory(localClass="AllocineStocks")
        )
        date_in_the_future = datetime.utcnow() + timedelta(days=4)
        other_date_in_the_future = datetime.utcnow() + timedelta(days=6)
        existing_stock = factories.StockFactory(offer=offer, price=10, beginningDatetime=date_in_the_future)
        edited_stock_data = StockEditionBodyModel(
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
        user = users_factories.UserFactory()
        offer = factories.ThingOfferFactory(validation=OfferValidationStatus.PENDING)
        created_stock_data = StockCreationBodyModel(price=10, quantity=7)

        with pytest.raises(api_errors.ApiErrors) as error:
            api.upsert_stocks(offer_id=offer.id, stock_data_list=[created_stock_data], user=user)

        assert error.value.errors == {
            "global": ["Les offres refusées ou en attente de validation ne sont pas modifiables"]
        }
        assert Stock.query.count() == 0

    def test_edit_stock_of_non_approved_offer_fails(self):
        user = users_factories.UserFactory()
        offer = factories.ThingOfferFactory(validation=OfferValidationStatus.PENDING)
        existing_stock = factories.StockFactory(offer=offer, price=10)
        edited_stock_data = StockEditionBodyModel(id=existing_stock.id, price=5, quantity=7)

        with pytest.raises(api_errors.ApiErrors) as error:
            api.upsert_stocks(offer_id=offer.id, stock_data_list=[edited_stock_data], user=user)

        assert error.value.errors == {
            "global": ["Les offres refusées ou en attente de validation ne sont pas modifiables"]
        }
        existing_stock = Stock.query.one()
        assert existing_stock.price == 10

    @mock.patch("pcapi.domain.admin_emails.send_offer_creation_notification_to_administration")
    @mock.patch("pcapi.core.offers.api.set_offer_status_based_on_fraud_criteria")
    def test_send_email_when_offer_automatically_approved_based_on_fraud_criteria(
        self, mocked_set_offer_status_based_on_fraud_criteria, mocked_offer_creation_notification_to_admin
    ):
        user = users_factories.UserFactory()
        offer = factories.ThingOfferFactory(validation=OfferValidationStatus.DRAFT)
        created_stock_data = StockCreationBodyModel(price=10, quantity=7)
        mocked_set_offer_status_based_on_fraud_criteria.return_value = OfferValidationStatus.APPROVED

        api.upsert_stocks(offer_id=offer.id, stock_data_list=[created_stock_data], user=user)

        mocked_offer_creation_notification_to_admin.assert_called_once_with(offer)

    @mock.patch("pcapi.domain.admin_emails.send_offer_creation_notification_to_administration")
    @mock.patch("pcapi.core.offers.api.set_offer_status_based_on_fraud_criteria")
    def test_not_send_email_when_offer_pass_to_pending_based_on_fraud_criteria(
        self, mocked_set_offer_status_based_on_fraud_criteria, mocked_offer_creation_notification_to_admin
    ):
        user = users_factories.UserFactory()
        offer = factories.ThingOfferFactory(validation=OfferValidationStatus.DRAFT)
        created_stock_data = StockCreationBodyModel(price=10, quantity=7)
        mocked_set_offer_status_based_on_fraud_criteria.return_value = OfferValidationStatus.PENDING

        api.upsert_stocks(offer_id=offer.id, stock_data_list=[created_stock_data], user=user)

        assert not mocked_offer_creation_notification_to_admin.called


@pytest.mark.usefixtures("db_session")
class DeleteStockTest:
    @mock.patch("pcapi.core.search.async_index_offer_ids")
    def test_delete_stock_basics(self, mocked_async_index_offer_ids):
        stock = factories.EventStockFactory()

        api.delete_stock(stock)

        stock = models.Stock.query.one()
        assert stock.isSoftDeleted
        mocked_async_index_offer_ids.assert_called_once_with([stock.offerId])

    @mock.patch("pcapi.domain.user_emails.send_offerer_bookings_recap_email_after_offerer_cancellation")
    @mock.patch("pcapi.domain.user_emails.send_warning_to_beneficiary_after_pro_booking_cancellation")
    def test_delete_stock_cancel_bookings_and_send_emails(self, mocked_send_to_beneficiaries, mocked_send_to_offerer):
        stock = factories.EventStockFactory()
        booking1 = bookings_factories.BookingFactory(stock=stock)
        booking2 = bookings_factories.BookingFactory(
            stock=stock, isCancelled=True, cancellationReason=BookingCancellationReasons.BENEFICIARY
        )
        booking3 = bookings_factories.BookingFactory(stock=stock, isUsed=True)

        api.delete_stock(stock)

        # cancellation can trigger more than one request to Batch
        assert len(push_testing.requests) >= 1

        stock = models.Stock.query.one()
        assert stock.isSoftDeleted
        booking1 = models.Booking.query.get(booking1.id)
        assert booking1.isCancelled
        assert booking1.cancellationReason == BookingCancellationReasons.OFFERER
        booking2 = models.Booking.query.get(booking2.id)
        assert booking2.isCancelled  # unchanged
        assert booking2.cancellationReason == BookingCancellationReasons.BENEFICIARY
        booking3 = models.Booking.query.get(booking3.id)
        assert not booking3.isCancelled  # unchanged
        assert not booking3.cancellationReason

        assert mocked_send_to_beneficiaries.mock_calls == [mock.call(booking1)]
        assert mocked_send_to_offerer.mock_calls == [mock.call([booking1])]

        assert push_testing.requests[-1] == {
            "group_id": "Cancel_booking",
            "user_ids": [booking1.userId],
            "message": {
                "body": f"""Ta réservation "{stock.offer.name}" a été annulée par l'offreur.""",
                "title": "Réservation annulée",
            },
        }

    def test_can_delete_if_stock_from_allocine(self):
        provider = offerers_factories.AllocineProviderFactory(localClass="AllocineStocks")
        offer = factories.OfferFactory(lastProvider=provider, idAtProviders="1")
        stock = factories.StockFactory(offer=offer)

        api.delete_stock(stock)

        stock = models.Stock.query.one()
        assert stock.isSoftDeleted

    def test_cannot_delete_if_stock_from_titelive(self):
        provider = offerers_factories.AllocineProviderFactory(localClass="TiteLiveStocks")
        offer = factories.OfferFactory(lastProvider=provider, idAtProviders="1")
        stock = factories.StockFactory(offer=offer)

        with pytest.raises(api_errors.ApiErrors) as error:
            api.delete_stock(stock)
        msg = "Les offres importées ne sont pas modifiables"
        assert error.value.errors["global"][0] == msg

        stock = models.Stock.query.one()
        assert not stock.isSoftDeleted

    def test_can_delete_if_event_ended_recently(self):
        recently = datetime.now() - timedelta(days=1)
        stock = factories.EventStockFactory(beginningDatetime=recently)

        api.delete_stock(stock)
        stock = models.Stock.query.one()
        assert stock.isSoftDeleted

    def test_cannot_delete_if_too_late(self):
        too_long_ago = datetime.now() - timedelta(days=3)
        stock = factories.EventStockFactory(beginningDatetime=too_long_ago)

        with pytest.raises(exceptions.TooLateToDeleteStock):
            api.delete_stock(stock)
        stock = models.Stock.query.one()
        assert not stock.isSoftDeleted


@pytest.mark.usefixtures("db_session")
class CreateMediationV2Test:
    THUMBS_DIR = (
        pathlib.Path(tests.__path__[0])
        / ".."
        / "src"
        / "pcapi"
        / "static"
        / "object_store_data"
        / "thumbs"
        / "mediations"
    )

    @mock.patch("pcapi.core.search.async_index_offer_ids")
    def test_ok(self, mocked_async_index_offer_ids):
        # Given
        user = users_factories.UserFactory()
        offer = factories.ThingOfferFactory()
        image_as_bytes = (IMAGES_DIR / "mouette_full_size.jpg").read_bytes()

        # When
        api.create_mediation(user, offer, "©Photographe", image_as_bytes)

        # Then
        mediation = models.Mediation.query.one()
        assert mediation.author == user
        assert mediation.offer == offer
        assert mediation.credit == "©Photographe"
        assert mediation.thumbCount == 1
        assert models.Mediation.query.filter(models.Mediation.offerId == offer.id).count() == 1
        mocked_async_index_offer_ids.assert_called_once_with([offer.id])

    def test_erase_former_mediations(self):
        # Given
        user = users_factories.UserFactory()
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
        mediation_3 = models.Mediation.query.one()
        assert mediation_3.credit == "©moi"
        thumb_3_id = humanize(mediation_3.id)

        assert not (self.THUMBS_DIR / thumb_1_id).exists()
        assert not (self.THUMBS_DIR / (thumb_1_id + ".type")).exists()
        assert not (self.THUMBS_DIR / thumb_2_id).exists()
        assert not (self.THUMBS_DIR / (thumb_2_id + ".type")).exists()

        assert len(os.listdir(self.THUMBS_DIR)) == existing_number_of_files + 2
        assert (self.THUMBS_DIR / thumb_3_id).exists()
        assert (self.THUMBS_DIR / (thumb_3_id + ".type")).exists()

    @mock.patch("pcapi.core.object_storage.store_public_object", side_effect=Exception)
    def test_rollback_if_exception(self, mock_store_public_object):
        # Given
        user = users_factories.UserFactory()
        offer = factories.ThingOfferFactory()
        image_as_bytes = (IMAGES_DIR / "mouette_full_size.jpg").read_bytes()
        existing_number_of_files = len(os.listdir(self.THUMBS_DIR))

        # When
        with pytest.raises(ThumbnailStorageError):
            api.create_mediation(user, offer, "©Photographe", image_as_bytes)

        # Then
        assert models.Mediation.query.count() == 0
        assert len(os.listdir(self.THUMBS_DIR)) == existing_number_of_files


@pytest.mark.usefixtures("db_session")
class CreateOfferTest:
    def test_create_offer_from_scratch(self):
        venue = factories.VenueFactory()
        offerer = venue.managingOfferer
        user_offerer = factories.UserOffererFactory(offerer=offerer)
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
        assert offer.type == str(offer_type.EventType.CINEMA)
        assert offer.subcategoryId == subcategories.SEANCE_CINE.id
        assert offer.product.owningOfferer == offerer
        assert offer.externalTicketOfficeUrl == "http://example.net"
        assert offer.audioDisabilityCompliant
        assert offer.mentalDisabilityCompliant
        assert offer.motorDisabilityCompliant
        assert offer.visualDisabilityCompliant
        assert offer.validation == OfferValidationStatus.DRAFT
        assert not offer.bookingEmail
        assert Offer.query.count() == 1

    def test_create_offer_from_scratch_without_subcategory(self):
        venue = factories.VenueFactory()
        offerer = venue.managingOfferer
        user_offerer = factories.UserOffererFactory(offerer=offerer)
        user = user_offerer.user

        data = offers_serialize.PostOfferBodyModel(
            venueId=humanize(venue.id),
            name="A pretty good offer",
            type=str(offer_type.EventType.CINEMA),
            externalTicketOfficeUrl="http://example.net",
            audioDisabilityCompliant=True,
            mentalDisabilityCompliant=True,
            motorDisabilityCompliant=True,
            visualDisabilityCompliant=True,
        )
        offer = api.create_offer(data, user)

        assert offer.name == "A pretty good offer"
        assert offer.venue == venue
        assert offer.type == str(offer_type.EventType.CINEMA)
        assert not offer.subcategoryId
        assert offer.product.owningOfferer == offerer
        assert offer.externalTicketOfficeUrl == "http://example.net"
        assert offer.audioDisabilityCompliant
        assert offer.mentalDisabilityCompliant
        assert offer.motorDisabilityCompliant
        assert offer.visualDisabilityCompliant
        assert offer.validation == OfferValidationStatus.DRAFT
        assert not offer.bookingEmail
        assert Offer.query.count() == 1

    def test_create_offer_from_existing_product(self):
        product = factories.ProductFactory(
            name="An excellent offer",
            type=str(offer_type.EventType.CINEMA),
        )
        venue = factories.VenueFactory()
        offerer = venue.managingOfferer
        user_offerer = factories.UserOffererFactory(offerer=offerer)
        user = user_offerer.user

        data = offers_serialize.PostOfferBodyModel(
            venueId=humanize(venue.id),
            productId=humanize(product.id),
            externalTicketOfficeUrl="http://example.net",
            audioDisabilityCompliant=True,
            mentalDisabilityCompliant=True,
            motorDisabilityCompliant=True,
            visualDisabilityCompliant=True,
        )
        offer = api.create_offer(data, user)

        assert offer.name == "An excellent offer"
        assert offer.type == str(offer_type.EventType.CINEMA)
        assert offer.product == product
        assert offer.externalTicketOfficeUrl == "http://example.net"
        assert offer.audioDisabilityCompliant
        assert offer.mentalDisabilityCompliant
        assert offer.motorDisabilityCompliant
        assert offer.visualDisabilityCompliant
        assert offer.validation == OfferValidationStatus.DRAFT
        assert Offer.query.count() == 1

    @override_features(ENABLE_ISBN_REQUIRED_IN_LIVRE_EDITION_OFFER_CREATION=True)
    def test_create_offer_livre_edition_from_isbn_with_existing_product(self):
        factories.ProductFactory(
            type=str(offer_type.ThingType.LIVRE_EDITION),
            description="Les prévisions du psychohistorien Hari Seldon sont formelles.",
            extraData={"isbn": "9782207300893", "author": "Asimov", "bookFormat": "Soft cover"},
            isGcuCompatible=True,
        )
        venue = factories.VenueFactory()
        offerer = venue.managingOfferer
        user_offerer = factories.UserOffererFactory(offerer=offerer)
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
        assert offer.type == str(offer_type.ThingType.LIVRE_EDITION)
        assert offer.description == "Les prévisions du psychohistorien Hari Seldon sont formelles."
        assert offer.extraData == {"isbn": "9782207300893", "author": "Isaac Asimov", "bookFormat": "Soft cover"}
        assert offer.audioDisabilityCompliant
        assert offer.mentalDisabilityCompliant
        assert offer.motorDisabilityCompliant
        assert not offer.visualDisabilityCompliant
        assert Product.query.count() == 1

    @override_features(ENABLE_ISBN_REQUIRED_IN_LIVRE_EDITION_OFFER_CREATION=True)
    def test_create_offer_livre_edition_from_isbn_with_is_not_compatible_gcu_should_fail(self):
        factories.ProductFactory(
            type=str(offer_type.ThingType.LIVRE_EDITION),
            description="Les prévisions du psychohistorien Hari Seldon sont formelles.",
            extraData={"isbn": "9782207300893", "author": "Asimov", "bookFormat": "Soft cover"},
            isGcuCompatible=False,
        )

        venue = factories.VenueFactory()
        offerer = venue.managingOfferer
        user_offerer = factories.UserOffererFactory(offerer=offerer)
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

        with pytest.raises(ApiErrors) as error:
            api.create_offer(data, user)

        assert error.value.errors["isbn"] == ["Ce produit n’est pas éligible au pass Culture."]

    @override_features(ENABLE_ISBN_REQUIRED_IN_LIVRE_EDITION_OFFER_CREATION=True)
    def test_create_offer_livre_edition_from_isbn_with_product_not_exists_should_fail(self):
        venue = factories.VenueFactory()
        offerer = venue.managingOfferer
        user_offerer = factories.UserOffererFactory(offerer=offerer)
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

        with pytest.raises(ApiErrors) as error:
            api.create_offer(data, user)

        assert error.value.errors["isbn"] == ["Ce produit n’est pas éligible au pass Culture."]

    def test_create_activation_offer(self):
        user = users_factories.UserFactory(isAdmin=True)
        venue = factories.VenueFactory()

        data = offers_serialize.PostOfferBodyModel(
            venueId=humanize(venue.id),
            name="An offer he can't refuse",
            type=str(offer_type.EventType.ACTIVATION),
            audioDisabilityCompliant=True,
            mentalDisabilityCompliant=True,
            motorDisabilityCompliant=True,
            visualDisabilityCompliant=True,
        )
        offer = api.create_offer(data, user)

        assert offer.type == str(offer_type.EventType.ACTIVATION)

    def test_create_educational_offer(self):
        venue = factories.VenueFactory()
        offerer = venue.managingOfferer
        user_offerer = factories.UserOffererFactory(offerer=offerer)
        user = user_offerer.user

        data = offers_serialize.PostOfferBodyModel(
            venueId=humanize(venue.id),
            name="A pretty good offer",
            type=str(offer_type.EventType.CINEMA),
            externalTicketOfficeUrl="http://example.net",
            isEducational=True,
            audioDisabilityCompliant=True,
            mentalDisabilityCompliant=True,
            motorDisabilityCompliant=True,
            visualDisabilityCompliant=True,
        )
        offer = api.create_offer(data, user)

        assert offer.isEducational

    def test_fail_if_unknown_venue(self):
        user = users_factories.UserFactory()
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
        venue = factories.VenueFactory()
        user = users_factories.UserFactory()
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


@pytest.mark.usefixtures("db_session")
class CreateOfferBusinessLogicChecksTest:
    def test_success_if_physical_product_and_physical_venue(self):
        venue = factories.VenueFactory()
        user_offerer = factories.UserOffererFactory(offerer=venue.managingOfferer)
        product = factories.ProductFactory()

        data = offers_serialize.PostOfferBodyModel(
            venueId=humanize(venue.id),
            productId=humanize(product.id),
            audioDisabilityCompliant=True,
            mentalDisabilityCompliant=True,
            motorDisabilityCompliant=True,
            visualDisabilityCompliant=True,
        )
        api.create_offer(data, user_offerer.user)  # should not fail

    def test_success_if_digital_product_and_virtual_venue(self):
        venue = factories.VirtualVenueFactory()
        user_offerer = factories.UserOffererFactory(offerer=venue.managingOfferer)
        product = factories.DigitalProductFactory()

        data = offers_serialize.PostOfferBodyModel(
            venueId=humanize(venue.id),
            productId=humanize(product.id),
            audioDisabilityCompliant=True,
            mentalDisabilityCompliant=True,
            motorDisabilityCompliant=True,
            visualDisabilityCompliant=True,
        )
        api.create_offer(data, user_offerer.user)  # should not fail

    def test_fail_if_digital_product_and_physical_venue(self):
        venue = factories.VenueFactory()
        user_offerer = factories.UserOffererFactory(offerer=venue.managingOfferer)
        product = factories.DigitalProductFactory()

        data = offers_serialize.PostOfferBodyModel(
            venueId=humanize(venue.id),
            productId=humanize(product.id),
            audioDisabilityCompliant=True,
            mentalDisabilityCompliant=True,
            motorDisabilityCompliant=True,
            visualDisabilityCompliant=True,
        )
        with pytest.raises(api_errors.ApiErrors) as error:
            api.create_offer(data, user_offerer.user)
        err = 'Une offre numérique doit obligatoirement être associée au lieu "Offre numérique"'
        assert error.value.errors["venue"] == [err]

    def test_fail_if_physical_product_and_virtual_venue(self):
        venue = factories.VirtualVenueFactory()
        user_offerer = factories.UserOffererFactory(offerer=venue.managingOfferer)
        product = factories.ProductFactory()

        data = offers_serialize.PostOfferBodyModel(
            venueId=humanize(venue.id),
            productId=humanize(product.id),
            audioDisabilityCompliant=True,
            mentalDisabilityCompliant=True,
            motorDisabilityCompliant=True,
            visualDisabilityCompliant=True,
        )
        with pytest.raises(api_errors.ApiErrors) as error:
            api.create_offer(data, user_offerer.user)
        err = 'Une offre physique ne peut être associée au lieu "Offre numérique"'
        assert error.value.errors["venue"] == [err]


@pytest.mark.usefixtures("db_session")
class UpdateOfferTest:
    @mock.patch("pcapi.core.search.async_index_offer_ids")
    def test_basics(self, mocked_async_index_offer_ids):
        offer = factories.OfferFactory(isDuo=False, bookingEmail="old@example.com")

        offer = api.update_offer(offer, isDuo=True, bookingEmail="new@example.com")

        assert offer.isDuo
        assert offer.bookingEmail == "new@example.com"
        mocked_async_index_offer_ids.assert_called_once_with([offer.id])

    def test_update_product_if_owning_offerer_is_the_venue_managing_offerer(self):
        offerer = factories.OffererFactory()
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

        with pytest.raises(models.ApiErrors) as error:
            api.update_offer(offer, name="Luftballons" * 99)

        assert error.value.errors == {"name": ["Vous devez saisir moins de 140 caractères"]}
        assert models.Offer.query.one().name == "Old name"

    def test_success_on_allocine_offer(self):
        provider = offerers_factories.AllocineProviderFactory(localClass="AllocineStocks")
        offer = factories.OfferFactory(lastProvider=provider, name="Old name")

        api.update_offer(offer, name="Old name", isDuo=True)

        offer = models.Offer.query.one()
        assert offer.name == "Old name"
        assert offer.isDuo

    def test_forbidden_on_allocine_offer_on_certain_fields(self):
        provider = offerers_factories.AllocineProviderFactory(localClass="AllocineStocks")
        offer = factories.OfferFactory(lastProvider=provider, name="Old name")

        with pytest.raises(models.ApiErrors) as error:
            api.update_offer(offer, name="New name", isDuo=True)

        assert error.value.errors == {"name": ["Vous ne pouvez pas modifier ce champ"]}
        offer = models.Offer.query.one()
        assert offer.name == "Old name"
        assert not offer.isDuo

    def test_success_on_imported_offer_on_external_ticket_office_url(self):
        provider = offerers_factories.AllocineProviderFactory()
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
        provider = offerers_factories.AllocineProviderFactory()
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
        provider = offerers_factories.APIProviderFactory()
        offer = factories.OfferFactory(
            lastProvider=provider, name="Old name", isDuo=False, audioDisabilityCompliant=True
        )

        with pytest.raises(models.ApiErrors) as error:
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
        pending_offer = factories.OfferFactory(name="Soliloquy", validation=OfferValidationStatus.PENDING)

        with pytest.raises(models.ApiErrors) as error:
            api.update_offer(pending_offer, name="Monologue")

        assert error.value.errors == {
            "global": ["Les offres refusées ou en attente de validation ne sont pas modifiables"]
        }
        pending_offer = models.Offer.query.one()
        assert pending_offer.name == "Soliloquy"


@pytest.mark.usefixtures("db_session")
class BatchUpdateOffersTest:
    @mock.patch("pcapi.core.search.async_index_offer_ids")
    def test_activate(self, mocked_async_index_offer_ids):
        offer1 = factories.OfferFactory(isActive=False)
        offer2 = factories.OfferFactory(isActive=False)
        offer3 = factories.OfferFactory(isActive=False)
        rejected_offer = factories.OfferFactory(isActive=False, validation=OfferValidationStatus.REJECTED)
        pending_offer = factories.OfferFactory(validation=OfferValidationStatus.PENDING)

        query = models.Offer.query.filter(
            models.Offer.id.in_({offer1.id, offer2.id, rejected_offer.id, pending_offer.id})
        )
        api.batch_update_offers(query, {"isActive": True})

        assert models.Offer.query.get(offer1.id).isActive
        assert models.Offer.query.get(offer2.id).isActive
        assert not models.Offer.query.get(offer3.id).isActive
        assert not models.Offer.query.get(rejected_offer.id).isActive
        assert not models.Offer.query.get(pending_offer.id).isActive
        mocked_async_index_offer_ids.assert_called_once_with([offer1.id, offer2.id])

    def test_deactivate(self):
        offer1 = factories.OfferFactory()
        offer2 = factories.OfferFactory()
        offer3 = factories.OfferFactory()

        query = models.Offer.query.filter(models.Offer.id.in_({offer1.id, offer2.id}))
        api.batch_update_offers(query, {"isActive": False})

        assert not models.Offer.query.get(offer1.id).isActive
        assert not models.Offer.query.get(offer2.id).isActive
        assert models.Offer.query.get(offer3.id).isActive


class UpdateOfferAndStockIdAtProvidersTest:
    @pytest.mark.usefixtures("db_session")
    def test_update_offer_and_stock_id_at_providers(self):
        # Given
        current_siret = "88888888888888"
        venue = VenueFactory(siret=current_siret)
        offer = OfferFactory(venue=venue, idAtProviders="1111111111111@22222222222222")
        other_venue_offer = OfferFactory(venue=venue, idAtProviders="3333333333333@12222222222222")
        stock = StockFactory(offer=offer, idAtProviders="1111111111111@22222222222222")

        # When
        update_offer_and_stock_id_at_providers(venue, "22222222222222")

        # Then
        assert offer.idAtProviders == "1111111111111@88888888888888"
        assert stock.idAtProviders == "1111111111111@88888888888888"
        assert other_venue_offer.idAtProviders == "3333333333333@12222222222222"


class OfferExpenseDomainsTest:
    def test_offer_expense_domains(self):
        assert get_expense_domains(models.Offer(type=str(offer_type.EventType.JEUX))) == ["all"]
        assert set(
            get_expense_domains(models.Offer(type=str(offer_type.ThingType.JEUX_VIDEO), url="https://example.com"))
        ) == {
            "all",
            "digital",
        }
        assert set(get_expense_domains(models.Offer(type=str(offer_type.ThingType.OEUVRE_ART)))) == {
            "all",
            "physical",
        }


@pytest.mark.usefixtures("db_session")
class AddCriterionToOffersTest:
    @mock.patch("pcapi.core.search.async_index_offer_ids")
    def test_add_criteria_from_isbn(self, mocked_async_index_offer_ids):
        # Given
        isbn = "2-221-00164-8"
        product1 = ProductFactory(extraData={"isbn": "2221001648"})
        offer11 = OfferFactory(product=product1)
        offer12 = OfferFactory(product=product1)
        product2 = ProductFactory(extraData={"isbn": "2221001648"})
        offer21 = OfferFactory(product=product2)
        inactive_offer = OfferFactory(product=product1, isActive=False)
        unmatched_offer = OfferFactory()
        criterion1 = CriterionFactory(name="Pretty good books")
        criterion2 = CriterionFactory(name="Other pretty good books")

        # When
        is_successful = add_criteria_to_offers([criterion1, criterion2], isbn=isbn)

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
        product1 = ProductFactory(extraData={"visa": visa})
        offer11 = OfferFactory(product=product1)
        offer12 = OfferFactory(product=product1)
        product2 = ProductFactory(extraData={"visa": visa})
        offer21 = OfferFactory(product=product2)
        inactive_offer = OfferFactory(product=product1, isActive=False)
        unmatched_offer = OfferFactory()
        criterion1 = CriterionFactory(name="Pretty good books")
        criterion2 = CriterionFactory(name="Other pretty good books")

        # When
        is_successful = add_criteria_to_offers([criterion1, criterion2], visa=visa)

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
        OfferFactory(extraData={"isbn": "2221001647"})
        criterion = CriterionFactory(name="Pretty good books")

        # When
        is_successful = add_criteria_to_offers([criterion], isbn=isbn)

        # Then
        assert is_successful is False


class DeactivateInappropriateProductTest:
    @mock.patch("pcapi.core.search.async_index_offer_ids")
    @pytest.mark.usefixtures("db_session")
    def test_should_deactivate_product_with_inappropriate_content(self, mocked_async_index_offer_ids):
        # Given
        product1 = ThingProductFactory(extraData={"isbn": "isbn-de-test"})
        product2 = ThingProductFactory(extraData={"isbn": "isbn-de-test"})
        OfferFactory(product=product1)
        OfferFactory(product=product1)
        OfferFactory(product=product2)

        # When
        deactivate_inappropriate_products("isbn-de-test")

        # Then
        products = Product.query.all()
        offers = Offer.query.all()

        assert not any(product.isGcuCompatible for product in products)
        assert not any(offer.isActive for offer in offers)
        mocked_async_index_offer_ids.assert_called_once_with([o.id for o in offers])


@pytest.mark.usefixtures("db_session")
class ComputeOfferValidationTest:
    def test_matching_keyword(self):
        offer = Offer(name="An offer PENDING validation")

        assert set_offer_status_based_on_fraud_criteria(offer) == OfferValidationStatus.PENDING

    def test_not_matching_keyword(self):
        offer = Offer(name="An offer pending validation")

        assert set_offer_status_based_on_fraud_criteria(offer) == OfferValidationStatus.APPROVED

    @override_features(OFFER_VALIDATION_MOCK_COMPUTATION=False)
    def test_deactivated_check(self):
        offer = Offer(name="An offer PENDING validation")

        assert set_offer_status_based_on_fraud_criteria(offer) == OfferValidationStatus.APPROVED

    @override_features(OFFER_VALIDATION_MOCK_COMPUTATION=False)
    def test_matching_keyword_in_name(self):
        offer = OfferFactory(name="A suspicious offer")
        StockFactory(price=10, offer=offer)
        example_yaml = """
        minimum_score: 0.6
        rules:
            - name: "check offer name"
              factor: 0
              conditions:
               - model: "Offer"
                 attribute: "name"
                 condition:
                    operator: "contains"
                    comparated: "suspicious"
        """
        import_offer_validation_config(example_yaml)
        assert set_offer_status_based_on_fraud_criteria(offer) == OfferValidationStatus.PENDING


@pytest.mark.usefixtures("db_session")
class UpdateOfferValidationStatusTest:
    def test_update_pending_offer_validation_status_to_approved(self):
        offer = OfferFactory(validation=OfferValidationStatus.PENDING)

        is_offer_updated = update_pending_offer_validation(offer, OfferValidationStatus.APPROVED)

        assert is_offer_updated is True
        assert offer.validation == OfferValidationStatus.APPROVED
        assert offer.isActive is True

    def test_update_pending_offer_validation_status_to_rejected(self):
        offer = OfferFactory(validation=OfferValidationStatus.PENDING)

        is_offer_updated = update_pending_offer_validation(offer, OfferValidationStatus.REJECTED)

        assert is_offer_updated is True
        assert offer.validation == OfferValidationStatus.REJECTED
        assert offer.isActive is False

    def test_cannot_update_pending_offer_validation_with_a_rejected_offer(self):
        offer = OfferFactory(validation=OfferValidationStatus.REJECTED)

        is_offer_updated = update_pending_offer_validation(offer, OfferValidationStatus.APPROVED)

        assert is_offer_updated is False
        assert offer.validation == OfferValidationStatus.REJECTED

    @mock.patch("pcapi.core.search.async_index_offer_ids")
    def test_update_pending_offer_validation_status_and_reindex(self, mocked_async_index_offer_ids):
        offer = OfferFactory(validation=OfferValidationStatus.PENDING)

        update_pending_offer_validation(offer, OfferValidationStatus.APPROVED)

        mocked_async_index_offer_ids.assert_called_once_with([offer.id])


@pytest.mark.usefixtures("db_session")
class ImportOfferValidationConfigTest:
    @override_features(OFFER_VALIDATION_MOCK_COMPUTATION=False)
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
        with pytest.raises(WrongFormatInFraudConfigurationFile) as error:
            import_offer_validation_config(config_yaml)
        assert str(error.value) == "\"'Wrong key: WRONG_KEY'\""

    @override_features(OFFER_VALIDATION_MOCK_COMPUTATION=False)
    def test_raise_a_WrongFormatInFraudConfigurationFile_error_for_wrong_type(self):
        config_yaml = """
            minimum_score: 0.6
            rules:
                - name: "nom de l'offre"
                  factor: "0"
                  conditions:
                    - model: "Offer"
                      attribute: "name"
                      condition:
                        operator: "not in"
                        comparated: "REJECTED"
                - name: "prix maximum"
                  factor: 0.2
                  conditions:
                    - model: "Offer"
                      attribute: "max_price"
                      condition:
                        operator: ">"
                        comparated: 100
            """
        with pytest.raises(WrongFormatInFraudConfigurationFile) as error:
            import_offer_validation_config(config_yaml)
        assert "0" in str(error.value)

    @override_features(OFFER_VALIDATION_MOCK_COMPUTATION=False)
    def test_raise_a_WrongFormatInFraudConfigurationFile_error_for_wrong_leaf_value(self):
        config_yaml = """
            minimum_score: 0.6
            rules:
                - namme: "nom de l'offre"
                  factor: 0
                  conditions:
                    - model: "Offer"
                      attribute: "name"
                      condition:
                        operator: "not in"
                        comparated: "REJECTED"
                - name: "prix maximum"
                  conditions:
                    - model: "Offer"
                      attribute: "max_price"
                      condition:
                        operator: ">"
                        comparated: 100
            """
        with pytest.raises(WrongFormatInFraudConfigurationFile) as error:
            import_offer_validation_config(config_yaml)
        assert "namme" in str(error.value)

    @override_features(OFFER_VALIDATION_MOCK_COMPUTATION=False)
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
        import_offer_validation_config(config_yaml)

        current_config = OfferValidationConfig.query.one()
        assert current_config is not None
        assert current_config.specs["minimum_score"] == 0.6
        assert current_config.specs["rules"][0]["conditions"][0]["condition"]["comparated"] == "REJECTED"
        assert current_config.specs["rules"][1]["conditions"][0]["attribute"] == "max_price"


@pytest.mark.usefixtures("db_session")
class ParseOfferValidationConfigTest:
    @override_features(OFFER_VALIDATION_MOCK_COMPUTATION=False)
    def test_parse_offer_validation_config(self):
        offer = OfferFactory(name="REJECTED")
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
        offer_validation_config = import_offer_validation_config(config_yaml)
        min_score, validation_rules = parse_offer_validation_config(offer, offer_validation_config)
        assert min_score == 0.6
        assert len(validation_rules) == 1
        assert validation_rules[0].factor == 0
        assert validation_rules[0].name == "modalités de retrait"
        assert validation_rules[0].offer_validation_items[0].model == offer
        assert validation_rules[0].offer_validation_items[0].attribute == "withdrawalDetails"


@pytest.mark.usefixtures("db_session")
class ComputeOfferValidationScoreTest:
    @override_features(OFFER_VALIDATION_MOCK_COMPUTATION=False)
    def test_offer_validation_with_one_item_config_with_in(self):
        offer = OfferFactory(name="REJECTED")
        validation_item = OfferValidationItem(
            model=offer, attribute="name", type=["str"], condition={"operator": "in", "comparated": ["REJECTED"]}
        )
        validation_rules = OfferValidationRuleItem(
            name="nom de l'offre", factor=0.2, offer_validation_items=[validation_item]
        )

        score = compute_offer_validation_score([validation_rules])

        assert score == 0.2

    @override_features(OFFER_VALIDATION_MOCK_COMPUTATION=False)
    def test_offer_validation_with_one_item_config_with_greater_than(self):
        offer = OfferFactory(name="REJECTED")
        StockFactory(offer=offer, price=12)
        validation_item = OfferValidationItem(
            model=offer, attribute="max_price", type=["int"], condition={"operator": ">", "comparated": 10}
        )
        validation_rule = OfferValidationRuleItem(name="prix max", factor=0.2, offer_validation_items=[validation_item])

        score = compute_offer_validation_score([validation_rule])

        assert score == 0.2

    def test_offer_validation_with_one_item_config_with_less_than(self):
        offer = OfferFactory(name="REJECTED")
        StockFactory(offer=offer, price=8)
        validation_item = OfferValidationItem(
            model=offer, attribute="max_price", type=["int"], condition={"operator": "<", "comparated": 10}
        )
        validation_rule = OfferValidationRuleItem(name="prix max", factor=0.2, offer_validation_items=[validation_item])

        score = compute_offer_validation_score([validation_rule])

        assert score == 0.2

    @override_features(OFFER_VALIDATION_MOCK_COMPUTATION=False)
    def test_offer_validation_with_one_item_config_with_greater_or_equal_than(self):
        offer = OfferFactory(name="REJECTED")
        StockFactory(offer=offer, price=12)
        validation_item = OfferValidationItem(
            model=offer, attribute="max_price", type=["int"], condition={"operator": ">=", "comparated": 10}
        )
        validation_rule = OfferValidationRuleItem(name="prix max", factor=0.2, offer_validation_items=[validation_item])

        score = compute_offer_validation_score([validation_rule])

        assert score == 0.2

    def test_offer_validation_with_one_item_config_with_less_or_equal_than(self):
        offer = OfferFactory(name="REJECTED")
        StockFactory(offer=offer, price=8)
        validation_item = OfferValidationItem(
            model=offer, attribute="max_price", type=["int"], condition={"operator": "<=", "comparated": 10}
        )
        validation_rule = OfferValidationRuleItem(name="prix max", factor=0.2, offer_validation_items=[validation_item])

        score = compute_offer_validation_score([validation_rule])

        assert score == 0.2

    @override_features(OFFER_VALIDATION_MOCK_COMPUTATION=False)
    def test_offer_validation_with_one_item_config_with_equal(self):
        offer = OfferFactory(name="test offer")
        StockFactory(offer=offer, price=15)
        validation_item = OfferValidationItem(
            model=offer,
            attribute="name",
            type=["str"],
            condition={"operator": "==", "comparated": "test offer"},
        )
        validation_rule = OfferValidationRuleItem(
            name="nom de l'offre", factor=0.3, offer_validation_items=[validation_item]
        )
        score = compute_offer_validation_score([validation_rule])
        assert score == 0.3

    @override_features(OFFER_VALIDATION_MOCK_COMPUTATION=False)
    def test_offer_validation_with_one_item_config_with_not_in(self):
        offer = OfferFactory(name="rejected")
        validation_item = OfferValidationItem(
            model=offer,
            attribute="name",
            type=["str"],
            condition={"operator": "not in", "comparated": "[approved]"},
        )
        validation_rule = OfferValidationRuleItem(
            name="nom de l'offre", factor=0.3, offer_validation_items=[validation_item]
        )
        score = compute_offer_validation_score([validation_rule])
        assert score == 0.3

    @override_features(OFFER_VALIDATION_MOCK_COMPUTATION=False)
    def test_offer_validation_with_multiple_item_config(self):
        offer = OfferFactory(name="test offer")
        StockFactory(offer=offer, price=15)
        validation_item_1 = OfferValidationItem(
            model=offer,
            attribute="name",
            type=["str"],
            condition={"operator": "==", "comparated": "test offer"},
        )
        validation_item_2 = OfferValidationItem(
            model=offer, attribute="max_price", type=["str"], condition={"operator": ">", "comparated": 10}
        )
        validation_rule_1 = OfferValidationRuleItem(
            name="nom de l'offre", factor=0.3, offer_validation_items=[validation_item_1]
        )
        validation_rule_2 = OfferValidationRuleItem(
            name="prix de l'offre", factor=0.2, offer_validation_items=[validation_item_2]
        )

        score = compute_offer_validation_score([validation_rule_1, validation_rule_2])
        assert score == 0.06

    @override_features(OFFER_VALIDATION_MOCK_COMPUTATION=False)
    def test_offer_validation_rule_with_multiple_conditions(self):
        offer = OfferFactory(name="Livre")
        StockFactory(offer=offer, price=75)
        validation_item_1 = OfferValidationItem(
            model=offer,
            attribute="name",
            type=["str"],
            condition={"operator": "==", "comparated": "Livre"},
        )
        validation_item_2 = OfferValidationItem(
            model=offer, attribute="max_price", type=["str"], condition={"operator": ">", "comparated": 70}
        )

        validation_rule = OfferValidationRuleItem(
            name="prix d'un livre", factor=0.5, offer_validation_items=[validation_item_1, validation_item_2]
        )

        score = compute_offer_validation_score([validation_rule])
        assert score == 0.5

    @override_features(OFFER_VALIDATION_MOCK_COMPUTATION=False)
    def test_offer_validation_with_emails_blacklist(self):

        venue = VenueFactory(siret="12345678912345", bookingEmail="fake@yopmail.com")
        offer = OfferFactory(name="test offer", venue=venue)
        StockFactory(offer=offer, price=15)
        validation_item_1 = OfferValidationItem(
            model=venue,
            attribute="bookingEmail",
            type=["str"],
            condition={"operator": "contains", "comparated": ["yopmail.com", "suspect.com"]},
        )

        validation_rule = OfferValidationRuleItem(
            name="adresses mail", factor=0.3, offer_validation_items=[validation_item_1]
        )

        score = compute_offer_validation_score([validation_rule])
        assert score == 0.3

    @override_features(OFFER_VALIDATION_MOCK_COMPUTATION=False)
    def test_offer_validation_with_description_rule_and_offer_without_description(self):
        offer = OfferFactory(name="test offer", description=None)
        StockFactory(offer=offer, price=15)
        validation_item_1 = OfferValidationItem(
            model=offer,
            attribute="description",
            type=["str"],
            condition={"operator": "contains", "comparated": ["suspect", "fake"]},
        )
        validation_rule = OfferValidationRuleItem(
            name="description de l'offre", factor=0.3, offer_validation_items=[validation_item_1]
        )

        score = compute_offer_validation_score([validation_rule])
        assert score == 1

    @override_features(OFFER_VALIDATION_MOCK_COMPUTATION=False)
    def test_offer_validation_with_id_at_providers_is_none(self):
        offer = OfferFactory(name="test offer", description=None)
        assert offer.idAtProviders is None
        StockFactory(offer=offer, price=15)
        validation_item_1 = OfferValidationItem(
            model=offer,
            attribute="idAtProviders",
            type=["None"],
            condition={"operator": "==", "comparated": None},
        )
        validation_rule = OfferValidationRuleItem(
            name="offre non synchro", factor=0.3, offer_validation_items=[validation_item_1]
        )

        score = compute_offer_validation_score([validation_rule])
        assert score == 0.3

    @override_features(OFFER_VALIDATION_MOCK_COMPUTATION=False)
    def test_offer_validation_with_contains_exact_word(self):
        offer = OfferFactory(name="test offer", description=None)
        assert offer.idAtProviders is None
        StockFactory(offer=offer, price=15)
        validation_item_1 = OfferValidationItem(
            model=offer,
            attribute="name",
            type=["str"],
            condition={"operator": "contains-exact", "comparated": ["test"]},
        )
        validation_rule = OfferValidationRuleItem(
            name="offer name contains exact words", factor=0.3, offer_validation_items=[validation_item_1]
        )

        score = compute_offer_validation_score([validation_rule])
        assert score == 0.3


class LoadProductByIsbnAndCheckIsGCUCompatibleOrRaiseErrorTest:
    @pytest.mark.usefixtures("db_session")
    def test_returns_product_if_found_and_is_gcu_compatible(self):
        isbn = "2221001648"
        product = ProductFactory(extraData={"isbn": isbn}, isGcuCompatible=True)

        result = _load_product_by_isbn_and_check_is_gcu_compatible_or_raise_error(isbn)

        assert result == product

    @pytest.mark.usefixtures("db_session")
    def test_raise_api_error_if_no_product(self):
        ProductFactory(isGcuCompatible=True)

        with pytest.raises(ApiErrors) as error:
            _load_product_by_isbn_and_check_is_gcu_compatible_or_raise_error("2221001649")

        assert error.value.errors["isbn"] == ["Ce produit n’est pas éligible au pass Culture."]

    @pytest.mark.usefixtures("db_session")
    def test_raise_api_error_if_product_is_not_gcu_compatible(self):
        isbn = "2221001648"
        ProductFactory(extraData={"isbn": isbn}, isGcuCompatible=False)

        with pytest.raises(ApiErrors) as error:
            _load_product_by_isbn_and_check_is_gcu_compatible_or_raise_error(isbn)

        assert error.value.errors["isbn"] == ["Ce produit n’est pas éligible au pass Culture."]


@freeze_time("2020-01-05 10:00:00")
@pytest.mark.usefixtures("db_session")
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
