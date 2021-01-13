import datetime
import io
import pathlib
from unittest import mock

import PIL.Image
from flask import current_app as app
import pytest
import pytz

from pcapi import models
import pcapi.core.bookings.factories as bookings_factories
from pcapi.core.bookings.models import Booking
import pcapi.core.offerers.factories as offerers_factories
from pcapi.core.offers import api
from pcapi.core.offers import exceptions
from pcapi.core.offers import factories
from pcapi.core.offers.models import Offer
import pcapi.core.users.factories as users_factories
from pcapi.models import api_errors
from pcapi.models import offer_type
from pcapi.models.feature import override_features
from pcapi.routes.serialization import offers_serialize
from pcapi.utils.human_ids import humanize

import tests


IMAGES_DIR = pathlib.Path(tests.__path__[0]) / "files"


@pytest.mark.usefixtures("db_session")
class CreateStockTest:
    @mock.patch("pcapi.connectors.redis.add_offer_id")
    def test_create_thing_offer(self, mocked_add_offer_id):
        offer = factories.ThingOfferFactory()

        stock = api.create_stock(offer=offer, price=10)

        assert stock.offer == offer
        assert stock.price == 10
        assert stock.quantity is None
        assert stock.beginningDatetime is None
        assert stock.bookingLimitDatetime is None
        mocked_add_offer_id.assert_called_once_with(client=app.redis_client, offer_id=offer.id)

    def test_create_event_offer(self):
        offer = factories.EventOfferFactory()
        beginning = datetime.datetime(2024, 1, 1, 12, 0, 0)
        booking_limit = datetime.datetime(2024, 1, 1, 9, 0, 0)

        stock = api.create_stock(
            offer=offer,
            price=10,
            quantity=7,
            beginning=beginning,
            booking_limit_datetime=booking_limit,
        )

        assert stock.offer == offer
        assert stock.price == 10
        assert stock.quantity == 7
        assert stock.beginningDatetime == beginning
        assert stock.bookingLimitDatetime == booking_limit

    @override_features(SYNCHRONIZE_ALGOLIA=False)
    @mock.patch("pcapi.connectors.redis.add_offer_id")
    def test_do_not_sync_algolia_if_feature_is_disabled(self, mocked_add_offer_id):
        offer = factories.ThingOfferFactory()

        api.create_stock(offer=offer, price=10, quantity=7)

        mocked_add_offer_id.assert_not_called()

    def test_fail_if_missing_dates(self):
        offer = factories.EventOfferFactory()

        with pytest.raises(api_errors.ApiErrors) as error:
            api.create_stock(offer=offer, price=10, beginning=None, booking_limit_datetime=None)

        assert "beginningDatetime" in error.value.errors

    def test_fail_if_offer_is_not_editable(self):
        provider = offerers_factories.ProviderFactory()
        offer = factories.ThingOfferFactory(lastProvider=provider)

        with pytest.raises(api_errors.ApiErrors) as error:
            api.create_stock(offer=offer, price=10, beginning=None, booking_limit_datetime=None)

        assert error.value.errors == {"global": ["Les offres importées ne sont pas modifiables"]}


@pytest.mark.usefixtures("db_session")
class EditStockTest:
    @mock.patch("pcapi.connectors.redis.add_offer_id")
    def test_edit_stock_basics(self, mocked_add_offer_id):
        stock = factories.EventStockFactory()

        beginning = datetime.datetime.now() + datetime.timedelta(days=2)
        booking_limit_datetime = datetime.datetime.now() + datetime.timedelta(days=1)
        api.edit_stock(
            stock,
            price=5,
            quantity=20,
            beginning=beginning,
            booking_limit_datetime=booking_limit_datetime,
        )

        stock = models.Stock.query.one()
        assert stock.price == 5
        assert stock.quantity == 20
        assert stock.beginningDatetime == beginning
        assert stock.bookingLimitDatetime == booking_limit_datetime
        mocked_add_offer_id.assert_called_once_with(client=app.redis_client, offer_id=stock.offerId)

    @mock.patch("pcapi.domain.user_emails.send_batch_stock_postponement_emails_to_users")
    def test_sends_email_if_beginning_changes(self, mocked_send_email):
        stock = factories.EventStockFactory()
        booking1 = bookings_factories.BookingFactory(stock=stock)
        bookings_factories.BookingFactory(stock=stock, isCancelled=True)

        beginning = datetime.datetime.now() + datetime.timedelta(days=10)
        api.edit_stock(
            stock,
            price=5,
            quantity=20,
            beginning=beginning,
            booking_limit_datetime=stock.bookingLimitDatetime,
        )

        stock = models.Stock.query.one()
        assert stock.beginningDatetime == beginning
        notified_bookings = mocked_send_email.call_args_list[0][0][0]
        assert notified_bookings == [booking1]

    @mock.patch("pcapi.core.offers.api.update_confirmation_dates")
    def should_update_bookings_confirmation_date_if_report_of_event(self, mock_update_confirmation_dates):
        now = datetime.datetime.now()
        event_in_4_days = now + datetime.timedelta(days=4)
        event_reported_in_10_days = now + datetime.timedelta(days=10)
        stock = factories.EventStockFactory(beginningDatetime=event_in_4_days)
        booking = bookings_factories.BookingFactory(stock=stock, dateCreated=now)

        api.edit_stock(
            stock,
            price=5,
            quantity=20,
            beginning=event_reported_in_10_days,
            booking_limit_datetime=stock.bookingLimitDatetime,
        )

        mock_update_confirmation_dates.assert_called_once_with([booking], event_reported_in_10_days)

    def should_invalidate_booking_token_when_event_is_reported(self):
        # Given
        now = datetime.datetime.now()
        booking_made_3_days_ago = now - datetime.timedelta(days=3)
        event_in_4_days = now + datetime.timedelta(days=4)
        event_reported_in_10_days = now + datetime.timedelta(days=10)
        stock = factories.EventStockFactory(beginningDatetime=event_in_4_days)
        booking = bookings_factories.BookingFactory(stock=stock, dateCreated=booking_made_3_days_ago, isUsed=True)

        # When
        api.edit_stock(
            stock,
            price=5,
            quantity=20,
            beginning=event_reported_in_10_days,
            booking_limit_datetime=stock.bookingLimitDatetime,
        )

        # Then
        updated_booking = Booking.query.get(booking.id)
        assert updated_booking.isUsed is False
        assert updated_booking.dateUsed is None
        assert updated_booking.confirmationDate == booking.confirmationDate

    @mock.patch("pcapi.core.offers.api.mark_as_unused")
    def should_not_invalidate_booking_token_when_event_is_reported_in_less_than_48_hours(self, mock_mark_as_unused):
        # Given
        now = datetime.datetime.now()
        date_used_in_48_hours = datetime.datetime.now() + datetime.timedelta(days=2)
        event_in_3_days = now + datetime.timedelta(days=3)
        event_reported_in_less_48_hours = now + datetime.timedelta(days=1)
        stock = factories.EventStockFactory(beginningDatetime=event_in_3_days)
        booking = bookings_factories.BookingFactory(
            stock=stock, dateCreated=now, isUsed=True, dateUsed=date_used_in_48_hours
        )

        # When
        api.edit_stock(
            stock,
            price=5,
            quantity=20,
            beginning=event_reported_in_less_48_hours,
            booking_limit_datetime=event_reported_in_less_48_hours,
        )

        # Then
        updated_booking = Booking.query.get(booking.id)
        assert updated_booking.isUsed is True
        assert updated_booking.dateUsed == date_used_in_48_hours

    def test_checks_number_of_reservations(self):
        stock = factories.EventStockFactory()
        bookings_factories.BookingFactory(stock=stock)
        bookings_factories.BookingFactory(stock=stock)
        bookings_factories.BookingFactory(stock=stock, isCancelled=True)

        # With a quantity too low
        quantity = 0
        with pytest.raises(api_errors.ApiErrors) as error:
            api.edit_stock(
                stock,
                price=stock.price,
                quantity=quantity,
                beginning=stock.beginningDatetime,
                booking_limit_datetime=stock.bookingLimitDatetime,
            )
        msg = "Le stock total ne peut être inférieur au nombre de réservations"
        assert error.value.errors["quantity"][0] == msg

        # With enough quantity
        quantity = 2
        api.edit_stock(
            stock,
            price=stock.price,
            quantity=quantity,
            beginning=stock.beginningDatetime,
            booking_limit_datetime=stock.bookingLimitDatetime,
        )
        stock = models.Stock.query.one()
        assert stock.quantity == 2

    def test_checks_booking_limit_is_after_beginning(self):
        stock = factories.EventStockFactory()

        with pytest.raises(api_errors.ApiErrors) as error:
            api.edit_stock(
                stock,
                price=stock.price,
                quantity=stock.quantity,
                beginning=datetime.datetime.now(),
                booking_limit_datetime=datetime.datetime.now() + datetime.timedelta(days=1),
            )
        msg = "La date limite de réservation pour cette offre est postérieure à la date de début de l'évènement"
        assert error.value.errors["bookingLimitDatetime"][0] == msg

    def test_cannot_edit_if_provider_is_titelive(self):
        provider = offerers_factories.ProviderFactory(localClass="TiteLiveStocks")
        stock = factories.EventStockFactory(offer__lastProvider=provider, offer__idAtProviders="1")

        with pytest.raises(api_errors.ApiErrors) as error:
            api.edit_stock(
                stock,
                price=stock.price,
                quantity=stock.quantity,
                beginning=stock.beginningDatetime,
                booking_limit_datetime=stock.bookingLimitDatetime,
            )
        msg = "Les offres importées ne sont pas modifiables"
        assert error.value.errors["global"][0] == msg

    def test_can_edit_non_restricted_fields_if_provider_is_allocine(self):
        provider = offerers_factories.ProviderFactory(localClass="AllocineStocks")
        stock = factories.EventStockFactory(
            offer__lastProvider=provider,
            offer__idAtProviders="1",
        )
        initial_beginning = stock.beginningDatetime

        # Change various attributes, but keep the same beginning
        # (which we are not allowed to change).
        new_booking_limit = datetime.datetime.now() + datetime.timedelta(days=1)
        changes = {
            "price": 5,
            "quantity": 20,
            # FIXME (dbaty, 2020-11-25): see comment in edit_stock,
            # this is to match what the frontend sends.
            "beginning": stock.beginningDatetime.replace(tzinfo=pytz.UTC),
            "booking_limit_datetime": new_booking_limit,
        }
        api.edit_stock(stock, **changes)
        stock = models.Stock.query.one()
        assert stock.price == 5
        assert stock.quantity == 20
        assert stock.beginningDatetime == initial_beginning
        assert stock.bookingLimitDatetime == new_booking_limit
        assert set(stock.fieldsUpdated) == {"price", "quantity", "bookingLimitDatetime"}

    def test_cannot_edit_restricted_fields_if_provider_is_allocine(self):
        provider = offerers_factories.ProviderFactory(localClass="AllocineStocks")
        stock = factories.EventStockFactory(
            offer__lastProvider=provider,
            offer__idAtProviders="1",
        )

        # Try to change everything, including "beginningDatetime" which is forbidden.
        new_booking_limit = datetime.datetime.now() + datetime.timedelta(days=1)
        changes = {
            "price": 5,
            "quantity": 20,
            "beginning": datetime.datetime.now() + datetime.timedelta(days=2),
            "booking_limit_datetime": new_booking_limit,
        }
        with pytest.raises(api_errors.ApiErrors) as error:
            api.edit_stock(stock, **changes)
        msg = "Pour les offres importées, certains champs ne sont pas modifiables"
        assert error.value.errors["global"][0] == msg


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
        recently = datetime.datetime.now() - datetime.timedelta(days=1)
        stock = factories.EventStockFactory(beginningDatetime=recently)

        api.delete_stock(stock)
        stock = models.Stock.query.one()
        assert stock.isSoftDeleted

    def test_cannot_delete_if_too_late(self):
        too_long_ago = datetime.datetime.now() - datetime.timedelta(days=3)
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

    @mock.patch("pcapi.utils.object_storage.store_public_object")
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
class CreateOfferTest:
    @mock.patch("pcapi.domain.admin_emails.send_offer_creation_notification_to_administration")
    @mock.patch("pcapi.utils.mailing.send_raw_email")
    def test_create_offer_from_scratch(self, mocked_send_raw_email, mocked_offer_creation_notification_to_admin):
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
        mocked_offer_creation_notification_to_admin.assert_called_once_with(offer, user, mocked_send_raw_email)

    @mock.patch("pcapi.domain.admin_emails.send_offer_creation_notification_to_administration")
    @mock.patch("pcapi.utils.mailing.send_raw_email")
    def test_create_offer_from_existing_product(
        self, mocked_send_raw_email, mocked_offer_creation_notification_to_admin
    ):
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
        mocked_offer_creation_notification_to_admin.assert_called_once_with(offer, user, mocked_send_raw_email)

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
