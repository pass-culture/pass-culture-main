from datetime import datetime
from datetime import timedelta
import io
import os
import pathlib
from unittest import mock

import PIL.Image
from flask import current_app as app
import pytest

from pcapi import models
import pcapi.core.bookings.factories as bookings_factories
from pcapi.core.bookings.models import Booking
import pcapi.core.offerers.factories as offerers_factories
from pcapi.core.offers import api
from pcapi.core.offers import exceptions
from pcapi.core.offers import factories
from pcapi.core.offers.exceptions import ThumbnailStorageError
from pcapi.core.offers.models import Offer
from pcapi.core.offers.models import Stock
from pcapi.core.testing import override_features
import pcapi.core.users.factories as users_factories
from pcapi.models import api_errors
from pcapi.models import offer_type
from pcapi.routes.serialization import offers_serialize
from pcapi.routes.serialization.stock_serialize import StockCreationBodyModel
from pcapi.routes.serialization.stock_serialize import StockEditionBodyModel
from pcapi.utils.human_ids import humanize

import tests


IMAGES_DIR = pathlib.Path(tests.__path__[0]) / "files"


@pytest.mark.usefixtures("db_session")
class UpsertStocksTest:
    @mock.patch("pcapi.domain.user_emails.send_batch_stock_postponement_emails_to_users")
    @mock.patch("pcapi.connectors.redis.add_offer_id")
    def test_upsert_multiple_stocks(self, mocked_add_offer_id, mock_update_confirmation_dates):
        # Given
        offer = factories.ThingOfferFactory()
        existing_stock = factories.StockFactory(offer=offer, price=10)
        created_stock_data = StockCreationBodyModel(price=10, quantity=7)
        edited_stock_data = StockEditionBodyModel(id=existing_stock.id, price=5, quantity=7)

        # When
        stocks_upserted = api.upsert_stocks(offer_id=offer.id, stock_data_list=[created_stock_data, edited_stock_data])

        # Then
        created_stock = Stock.query.filter_by(id=stocks_upserted[0].id).first()
        assert created_stock.offer == offer
        assert created_stock.price == 10
        assert created_stock.quantity == 7
        edited_stock = Stock.query.filter_by(id=existing_stock.id).first()
        assert edited_stock.price == 5
        assert edited_stock.quantity == 7
        mocked_add_offer_id.assert_called_once_with(client=app.redis_client, offer_id=offer.id)

    @mock.patch("pcapi.domain.user_emails.send_batch_stock_postponement_emails_to_users")
    def test_sends_email_if_beginning_date_changes_on_edition(self, mocked_send_email):
        # Given
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
        api.upsert_stocks(offer_id=offer.id, stock_data_list=[edited_stock_data])

        # Then
        stock = models.Stock.query.one()
        assert stock.beginningDatetime == beginning
        notified_bookings = mocked_send_email.call_args_list[0][0][0]
        assert notified_bookings == [booking]

    @mock.patch("pcapi.core.offers.api.update_confirmation_dates")
    def should_update_bookings_confirmation_date_if_report_of_event(self, mock_update_confirmation_dates):
        # Given
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
        api.upsert_stocks(offer_id=offer.id, stock_data_list=[edited_stock_data])

        # Then
        mock_update_confirmation_dates.assert_called_once_with([booking], event_reported_in_10_days)

    @mock.patch("pcapi.domain.user_emails.send_batch_stock_postponement_emails_to_users")
    def should_invalidate_booking_token_when_event_is_reported(self, mock_update_confirmation_dates):
        # Given
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
        api.upsert_stocks(offer_id=offer.id, stock_data_list=[edited_stock_data])

        # Then
        updated_booking = Booking.query.get(booking.id)
        assert updated_booking.isUsed is False
        assert updated_booking.dateUsed is None
        assert updated_booking.confirmationDate == booking.confirmationDate

    @mock.patch("pcapi.domain.user_emails.send_batch_stock_postponement_emails_to_users")
    @mock.patch("pcapi.core.offers.api.mark_as_unused")
    def should_not_invalidate_booking_token_when_event_is_reported_in_less_than_48_hours(
        self, mock_mark_as_unused, mock_update_confirmation_dates
    ):
        # Given
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
        api.upsert_stocks(offer_id=offer.id, stock_data_list=[edited_stock_data])

        # Then
        updated_booking = Booking.query.get(booking.id)
        assert updated_booking.isUsed is True
        assert updated_booking.dateUsed == date_used_in_48_hours

    @override_features(SYNCHRONIZE_ALGOLIA=False)
    @mock.patch("pcapi.domain.user_emails.send_batch_stock_postponement_emails_to_users")
    @mock.patch("pcapi.connectors.redis.add_offer_id")
    def test_do_not_sync_algolia_if_feature_is_disabled(self, mocked_add_offer_id, mock_update_confirmation_dates):
        # Given
        offer = factories.ThingOfferFactory()
        created_stock_data = StockCreationBodyModel(price=10)

        # When
        api.upsert_stocks(offer_id=offer.id, stock_data_list=[created_stock_data])

        # Then
        mocked_add_offer_id.assert_not_called()

    @mock.patch("pcapi.domain.user_emails.send_batch_stock_postponement_emails_to_users")
    def test_does_not_allow_edition_of_stock_of_another_offer_than_given(self, mock_update_confirmation_dates):
        # Given
        offer = factories.ThingOfferFactory()
        other_offer = factories.ThingOfferFactory()
        existing_stock_on_other_offer = factories.StockFactory(offer=other_offer, price=10)
        edited_stock_data = StockEditionBodyModel(id=existing_stock_on_other_offer.id, price=30)

        # When
        with pytest.raises(api_errors.ApiErrors) as error:
            api.upsert_stocks(offer_id=offer.id, stock_data_list=[edited_stock_data])

        # Then
        assert error.value.status_code == 403
        assert error.value.errors == {
            "global": ["Vous n'avez pas les droits d'accès suffisant pour accéder à cette information."]
        }

    @mock.patch("pcapi.domain.user_emails.send_batch_stock_postponement_emails_to_users")
    def test_does_not_allow_invalid_quantity_on_creation_and_edition(self, mock_update_confirmation_dates):
        # Given
        offer = factories.ThingOfferFactory()
        existing_stock = factories.StockFactory(offer=offer, price=10)
        created_stock_data = StockCreationBodyModel(price=10, quantity=-2)
        edited_stock_data = StockEditionBodyModel(id=existing_stock.id, price=30, quantity=-4)

        # When
        with pytest.raises(api_errors.ApiErrors) as error:
            api.upsert_stocks(offer_id=offer.id, stock_data_list=[created_stock_data, edited_stock_data])

        # Then
        assert error.value.errors == {"quantity": ["Le stock doit être positif"]}

    @mock.patch("pcapi.domain.user_emails.send_batch_stock_postponement_emails_to_users")
    def test_does_not_allow_invalid_price_on_creation_and_edition(self, mock_update_confirmation_dates):
        # Given
        offer = factories.ThingOfferFactory()
        existing_stock = factories.StockFactory(offer=offer, price=10)
        created_stock_data = StockCreationBodyModel(price=-1)
        edited_stock_data = StockEditionBodyModel(id=existing_stock.id, price=-3)

        # When
        with pytest.raises(api_errors.ApiErrors) as error:
            api.upsert_stocks(offer_id=offer.id, stock_data_list=[created_stock_data, edited_stock_data])

        # Then
        assert error.value.errors == {
            "price": ["Le prix doit être positif"],
        }

    @mock.patch("pcapi.domain.user_emails.send_batch_stock_postponement_emails_to_users")
    def test_does_not_allow_beginning_datetime_on_thing_offer_on_creation_and_edition(
        self, mock_update_confirmation_dates
    ):
        # Given
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
            api.upsert_stocks(offer_id=offer.id, stock_data_list=[created_stock_data, edited_stock_data])

        # Then
        assert error.value.errors == {
            "global": ["Impossible de mettre une date de début si l'offre ne porte pas sur un événement"],
        }

    @mock.patch("pcapi.domain.user_emails.send_batch_stock_postponement_emails_to_users")
    def test_does_not_allow_a_negative_remaining_quantity_on_edition(self, mock_update_confirmation_dates):
        # Given
        offer = factories.ThingOfferFactory()
        booking = bookings_factories.BookingFactory(stock__offer=offer, stock__quantity=10)
        existing_stock = booking.stock
        edited_stock_data = StockEditionBodyModel(id=existing_stock.id, quantity=0, price=10)

        # When
        with pytest.raises(api_errors.ApiErrors) as error:
            api.upsert_stocks(offer_id=offer.id, stock_data_list=[edited_stock_data])

        # Then
        assert error.value.errors == {"quantity": ["Le stock total ne peut être inférieur au nombre de réservations"]}

    @mock.patch("pcapi.domain.user_emails.send_batch_stock_postponement_emails_to_users")
    def test_does_not_allow_missing_dates_for_an_event_offer_on_creation_and_edition(
        self, mock_update_confirmation_dates
    ):
        # Given
        offer = factories.EventOfferFactory()
        created_stock_data = StockCreationBodyModel(price=10, beginningDatetime=None, bookingLimitDatetime=None)

        # When
        with pytest.raises(api_errors.ApiErrors) as error:
            api.upsert_stocks(offer_id=offer.id, stock_data_list=[created_stock_data])

        # Then
        assert error.value.errors == {"beginningDatetime": ["Ce paramètre est obligatoire"]}

    @mock.patch("pcapi.domain.user_emails.send_batch_stock_postponement_emails_to_users")
    def test_does_not_allow_booking_limit_after_beginning_for_an_event_offer_on_creation_and_edition(
        self, mock_update_confirmation_dates
    ):
        # Given
        offer = factories.EventOfferFactory()
        beginning_date = datetime.utcnow() + timedelta(days=4)
        booking_limit = beginning_date + timedelta(days=4)
        created_stock_data = StockCreationBodyModel(
            price=10, beginningDatetime=beginning_date, bookingLimitDatetime=booking_limit
        )

        # When
        with pytest.raises(api_errors.ApiErrors) as error:
            api.upsert_stocks(offer_id=offer.id, stock_data_list=[created_stock_data])

        # Then
        assert error.value.errors == {
            "bookingLimitDatetime": [
                "La date limite de réservation pour cette offre est postérieure à la date de début de l'évènement"
            ]
        }

    @mock.patch("pcapi.domain.user_emails.send_batch_stock_postponement_emails_to_users")
    def test_does_not_allow_edition_of_a_past_event_stock(self, mock_update_confirmation_dates):
        # Given
        offer = factories.ThingOfferFactory()
        date_in_the_past = datetime.utcnow() - timedelta(days=4)
        existing_stock = factories.StockFactory(offer=offer, price=10, beginningDatetime=date_in_the_past)
        edited_stock_data = StockEditionBodyModel(id=existing_stock.id, price=4)

        # When
        with pytest.raises(api_errors.ApiErrors) as error:
            api.upsert_stocks(offer_id=offer.id, stock_data_list=[edited_stock_data])

        # Then
        assert error.value.errors == {"global": ["Les événements passés ne sont pas modifiables"]}

    @mock.patch("pcapi.domain.user_emails.send_batch_stock_postponement_emails_to_users")
    def test_does_not_allow_upsert_stocks_on_a_synchronized_offer(self, mock_update_confirmation_dates):
        # Given
        offer = factories.ThingOfferFactory(
            lastProvider=offerers_factories.ProviderFactory(localClass="TiteLiveStocks")
        )
        created_stock_data = StockCreationBodyModel(price=10)

        # When
        with pytest.raises(api_errors.ApiErrors) as error:
            api.upsert_stocks(offer_id=offer.id, stock_data_list=[created_stock_data])

        # Then
        assert error.value.errors == {"global": ["Les offres importées ne sont pas modifiables"]}

    @mock.patch("pcapi.domain.user_emails.send_batch_stock_postponement_emails_to_users")
    def test_allow_edition_of_price_and_quantity_for_stocks_of_offers_synchronized_with_allocine(
        self, mock_update_confirmation_dates
    ):
        # Given
        offer = factories.EventOfferFactory(
            lastProvider=offerers_factories.ProviderFactory(localClass="AllocineStocks")
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
        api.upsert_stocks(offer_id=offer.id, stock_data_list=[edited_stock_data])

        # Then
        edited_stock = Stock.query.filter_by(id=existing_stock.id).first()
        assert edited_stock.price == 4

    @mock.patch("pcapi.domain.user_emails.send_batch_stock_postponement_emails_to_users")
    def test_does_not_allow_edition_of_beginningDateTime_for_stocks_of_offers_synchronized_with_allocine(
        self, mock_update_confirmation_dates
    ):
        # Given
        offer = factories.EventOfferFactory(
            lastProvider=offerers_factories.ProviderFactory(localClass="AllocineStocks")
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
            api.upsert_stocks(offer_id=offer.id, stock_data_list=[edited_stock_data])

        # Then
        assert error.value.errors == {"global": ["Pour les offres importées, certains champs ne sont pas modifiables"]}


@pytest.mark.usefixtures("db_session")
class DeleteStockTest:
    @mock.patch("pcapi.connectors.redis.add_offer_id")
    def test_delete_stock_basics(self, mocked_add_offer_id):
        stock = factories.EventStockFactory()

        api.delete_stock(stock)

        stock = models.Stock.query.one()
        assert stock.isSoftDeleted
        mocked_add_offer_id.assert_called_once_with(client=app.redis_client, offer_id=stock.offerId)

    @mock.patch("pcapi.domain.user_emails.send_batch_cancellation_emails_to_users")
    @mock.patch("pcapi.domain.user_emails.send_offerer_bookings_recap_email_after_offerer_cancellation")
    def test_delete_stock_cancel_bookings_and_send_emails(self, mocked_send_to_beneficiaries, mocked_send_to_offerer):
        stock = factories.EventStockFactory()
        booking1 = bookings_factories.BookingFactory(stock=stock)
        booking2 = bookings_factories.BookingFactory(stock=stock, isCancelled=True)
        booking3 = bookings_factories.BookingFactory(stock=stock, isUsed=True)

        api.delete_stock(stock)

        stock = models.Stock.query.one()
        assert stock.isSoftDeleted
        booking1 = models.Booking.query.get(booking1.id)
        assert booking1.isCancelled
        booking2 = models.Booking.query.get(booking2.id)
        assert booking2.isCancelled  # unchanged
        booking3 = models.Booking.query.get(booking3.id)
        assert not booking3.isCancelled  # unchanged

        notified_bookings_beneficiaries = mocked_send_to_beneficiaries.call_args_list[0][0][0]
        notified_bookings_offerers = mocked_send_to_offerer.call_args_list[0][0][0]
        assert notified_bookings_beneficiaries == notified_bookings_offerers
        assert notified_bookings_beneficiaries == [booking1]

    def test_can_delete_if_stock_from_allocine(self):
        provider = offerers_factories.ProviderFactory(localClass="AllocineStocks")
        offer = factories.OfferFactory(lastProvider=provider, idAtProviders="1")
        stock = factories.StockFactory(offer=offer)

        api.delete_stock(stock)

        stock = models.Stock.query.one()
        assert stock.isSoftDeleted

    def test_cannot_delete_if_stock_from_titelive(self):
        provider = offerers_factories.ProviderFactory(localClass="TiteLiveStocks")
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
class CreateMediationTest:
    @mock.patch("pcapi.connectors.redis.add_offer_id")
    def test_create_mediation_basics(self, mocked_add_offer_id):
        user = users_factories.UserFactory()
        offer = factories.ThingOfferFactory()
        image_as_bytes = (IMAGES_DIR / "mouette_full_size.jpg").read_bytes()

        mediation = api.create_mediation(user, offer, "credits", image_as_bytes)

        assert mediation.author == user
        assert mediation.offer == offer
        assert mediation.credit == "credits"
        assert mediation.thumbCount == 1
        mocked_add_offer_id.assert_called_once_with(client=app.redis_client, offer_id=offer.id)

    @mock.patch("pcapi.core.object_storage.store_public_object")
    def test_crop_params(self, mocked_store_public_object):
        user = users_factories.UserFactory()
        offer = factories.ThingOfferFactory()
        image_as_bytes = (IMAGES_DIR / "mouette_full_size.jpg").read_bytes()
        crop_params = (0.8, 0.8, 1)

        mediation = api.create_mediation(user, offer, "credits", image_as_bytes, crop_params)
        assert mediation.thumbCount == 1
        resized_as_bytes = mocked_store_public_object.call_args[1]["blob"]
        resized = PIL.Image.open(io.BytesIO(resized_as_bytes))
        assert resized.size == (357, 357)

    def test_check_image_quality(self):
        user = users_factories.UserFactory()
        offer = factories.ThingOfferFactory()
        image_as_bytes = (IMAGES_DIR / "mouette_small.jpg").read_bytes()

        with pytest.raises(models.ApiErrors) as error:
            api.create_mediation(user, offer, "credits", image_as_bytes)

        assert error.value.errors["thumb"] == ["L'image doit faire 400 * 400 px minimum"]
        assert models.Mediation.query.count() == 0


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

    @mock.patch("pcapi.connectors.redis.add_offer_id")
    def test_ok(self, mocked_add_offer_id):
        # Given
        user = users_factories.UserFactory()
        offer = factories.ThingOfferFactory()
        image_as_bytes = (IMAGES_DIR / "mouette_full_size.jpg").read_bytes()

        # When
        api.create_mediation_v2(user, offer, "©Photographe", image_as_bytes)

        # Then
        mediation = models.Mediation.query.one()
        assert mediation.author == user
        assert mediation.offer == offer
        assert mediation.credit == "©Photographe"
        assert mediation.thumbCount == 1
        assert models.Mediation.query.filter(models.Mediation.offerId == offer.id).count() == 1
        mocked_add_offer_id.assert_called_once_with(client=app.redis_client, offer_id=offer.id)

    def test_erase_former_mediations(self):
        # Given
        user = users_factories.UserFactory()
        offer = factories.ThingOfferFactory()
        image_as_bytes = (IMAGES_DIR / "mouette_full_size.jpg").read_bytes()
        existing_number_of_files = len(os.listdir(self.THUMBS_DIR))

        mediation_1 = api.create_mediation_v2(user, offer, "©Photographe", image_as_bytes)
        mediation_2 = api.create_mediation_v2(user, offer, "©Alice", image_as_bytes)
        thumb_1_id = humanize(mediation_1.id)
        thumb_2_id = humanize(mediation_2.id)

        # When
        api.create_mediation_v2(user, offer, "©moi", image_as_bytes)

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
            api.create_mediation_v2(user, offer, "©Photographe", image_as_bytes)

        # Then
        assert models.Mediation.query.count() == 0
        assert len(os.listdir(self.THUMBS_DIR)) == existing_number_of_files


@pytest.mark.usefixtures("db_session")
class CreateOfferTest:
    @mock.patch("pcapi.domain.admin_emails.send_offer_creation_notification_to_administration")
    def test_create_offer_from_scratch(self, mocked_offer_creation_notification_to_admin):
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
        assert offer.product.owningOfferer == offerer
        assert offer.externalTicketOfficeUrl == "http://example.net"
        assert offer.audioDisabilityCompliant
        assert offer.mentalDisabilityCompliant
        assert offer.motorDisabilityCompliant
        assert offer.visualDisabilityCompliant
        assert not offer.bookingEmail
        assert Offer.query.count() == 1
        mocked_offer_creation_notification_to_admin.assert_called_once_with(offer, user)

    @mock.patch("pcapi.domain.admin_emails.send_offer_creation_notification_to_administration")
    def test_create_offer_from_existing_product(self, mocked_offer_creation_notification_to_admin):
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
        assert Offer.query.count() == 1
        mocked_offer_creation_notification_to_admin.assert_called_once_with(offer, user)

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

    def test_fail_if_unknown_venue(self):
        user = users_factories.UserFactory()
        data = offers_serialize.PostOfferBodyModel(
            venueId=humanize(1),
            name="An awful offer",
            type=str(offer_type.EventType.ACTIVATION),
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

    def test_fail_to_create_activation_offer_if_not_admin(self):
        venue = factories.VenueFactory()
        offerer = venue.managingOfferer
        user_offerer = factories.UserOffererFactory(offerer=offerer)
        user = user_offerer.user

        data = offers_serialize.PostOfferBodyModel(
            venueId=humanize(venue.id),
            name="A pathetic offer",
            type=str(offer_type.EventType.ACTIVATION),
            audioDisabilityCompliant=True,
            mentalDisabilityCompliant=True,
            motorDisabilityCompliant=True,
            visualDisabilityCompliant=True,
        )
        with pytest.raises(api_errors.ApiErrors) as error:
            api.create_offer(data, user)
        err = "Seuls les administrateurs du pass Culture peuvent créer des offres d'activation"
        assert error.value.errors["type"] == [err]


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
    @mock.patch("pcapi.connectors.redis.add_offer_id")
    def test_basics(self, mocked_add_offer_id):
        offer = factories.OfferFactory(isDuo=False, bookingEmail="old@example.com")

        offer = api.update_offer(offer, isDuo=True, bookingEmail="new@example.com")

        assert offer.isDuo
        assert offer.bookingEmail == "new@example.com"
        mocked_add_offer_id.assert_called_once_with(client=app.redis_client, offer_id=offer.id)

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
        provider = offerers_factories.ProviderFactory(localClass="AllocineStocks")
        offer = factories.OfferFactory(lastProvider=provider, name="Old name")

        api.update_offer(offer, name="Old name", isDuo=True)

        offer = models.Offer.query.one()
        assert offer.name == "Old name"
        assert offer.isDuo

    def test_forbidden_on_allocine_offer_on_certain_fields(self):
        provider = offerers_factories.ProviderFactory(localClass="AllocineStocks")
        offer = factories.OfferFactory(lastProvider=provider, name="Old name")

        with pytest.raises(models.ApiErrors) as error:
            api.update_offer(offer, name="New name", isDuo=True)

        assert error.value.errors == {"name": ["Vous ne pouvez pas modifier ce champ"]}
        offer = models.Offer.query.one()
        assert offer.name == "Old name"
        assert not offer.isDuo

    def test_success_on_imported_offer_on_external_ticket_office_url(self):
        provider = offerers_factories.ProviderFactory()
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
        provider = offerers_factories.ProviderFactory()
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
        provider = offerers_factories.ProviderFactory()
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


@pytest.mark.usefixtures("db_session")
class UpdateOffersActiveStatusTest:
    @mock.patch("pcapi.connectors.redis.add_offer_id")
    def test_activate(self, mocked_add_offer_id):
        offer1 = factories.OfferFactory(isActive=False)
        offer2 = factories.OfferFactory(isActive=False)
        offer3 = factories.OfferFactory(isActive=False)

        query = models.Offer.query.filter(models.Offer.id.in_({offer1.id, offer2.id}))
        api.update_offers_active_status(query, is_active=True)

        assert models.Offer.query.get(offer1.id).isActive
        assert models.Offer.query.get(offer2.id).isActive
        assert not models.Offer.query.get(offer3.id).isActive
        assert mocked_add_offer_id.call_count == 2
        mocked_add_offer_id.assert_has_calls(
            [
                mock.call(client=app.redis_client, offer_id=offer1.id),
                mock.call(client=app.redis_client, offer_id=offer2.id),
            ],
            any_order=True,
        )

    def test_deactivate(self):
        offer1 = factories.OfferFactory()
        offer2 = factories.OfferFactory()
        offer3 = factories.OfferFactory()

        query = models.Offer.query.filter(models.Offer.id.in_({offer1.id, offer2.id}))
        api.update_offers_active_status(query, is_active=False)

        assert not models.Offer.query.get(offer1.id).isActive
        assert not models.Offer.query.get(offer2.id).isActive
        assert models.Offer.query.get(offer3.id).isActive
