import copy
from datetime import datetime
from datetime import timedelta
import logging
import os
import pathlib
from unittest import mock
from unittest.mock import patch

from freezegun import freeze_time
import pytest

import pcapi.core.bookings.factories as bookings_factories
import pcapi.core.bookings.models as bookings_models
from pcapi.core.categories import subcategories
import pcapi.core.criteria.factories as criteria_factories
import pcapi.core.criteria.models as criteria_models
import pcapi.core.finance.factories as finance_factories
import pcapi.core.finance.models as finance_models
import pcapi.core.mails.testing as mails_testing
import pcapi.core.offerers.factories as offerers_factories
from pcapi.core.offers import api
from pcapi.core.offers import exceptions
from pcapi.core.offers import factories
from pcapi.core.offers import models
from pcapi.core.offers import offer_validation
import pcapi.core.providers.factories as providers_factories
import pcapi.core.providers.repository as providers_repository
from pcapi.core.testing import override_features
from pcapi.core.testing import override_settings
import pcapi.core.users.factories as users_factories
import pcapi.core.users.models as users_models
from pcapi.models import api_errors
from pcapi.models import db
from pcapi.models.offer_mixin import OfferValidationStatus
from pcapi.notifications.push import testing as push_testing
from pcapi.utils.human_ids import humanize

import tests
from tests import conftest


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


@pytest.mark.usefixtures("db_session")
class CreateStockTest:
    def test_create_stock(self):
        # Given
        offer = factories.ThingOfferFactory()

        # When
        created_stock = api.create_stock(offer=offer, price=10, quantity=7)

        # Then
        assert created_stock.offerId == offer.id
        assert created_stock.price == 10
        assert created_stock.quantity == 7

    def test_does_not_allow_invalid_quantity(self):
        # Given
        offer = factories.ThingOfferFactory()

        # When
        with pytest.raises(api_errors.ApiErrors) as error:
            api.create_stock(offer=offer, quantity=-4, price=30)

        # Then
        assert error.value.errors == {"quantity": ["Le stock doit être positif"]}

    def test_does_not_allow_invalid_price(self):
        # Given
        offer = factories.ThingOfferFactory()

        # When
        with pytest.raises(api_errors.ApiErrors) as error:
            api.create_stock(offer=offer, price=-3, quantity=1)

        # Then
        assert error.value.errors == {"price": ["Le prix doit être positif"]}

    def test_does_not_allow_price_above_300_euros(self):
        # Given
        offer = factories.ThingOfferFactory()

        # When
        with pytest.raises(api_errors.ApiErrors) as error:
            api.create_stock(offer=offer, price=301, quantity=None)

        # Then
        assert error.value.errors == {"price300": ["Le prix d’une offre ne peut excéder 300 euros."]}

    def test_cannot_create_with_different_price_if_reimbursement_rule_exists(self):
        # If a stock exists with a price, we cannot add a new stock
        # with another price.
        stock = factories.ThingStockFactory(price=10)
        offer = stock.offer
        finance_factories.CustomReimbursementRuleFactory(offer=stock.offer)

        with pytest.raises(api_errors.ApiErrors) as error:
            api.create_stock(offer=offer, price=9, quantity=None)
        assert error.value.errors["price"][0].startswith("Vous ne pouvez pas modifier le prix")

    def test_cannot_create_stock_with_different_price_if_reimbursement_rule_exists_with_soft_deleted_price(self):
        # Same as above, but with an offer than only has one,
        # soft-deleted stock.
        stock = factories.ThingStockFactory(price=10, isSoftDeleted=True)
        offer = stock.offer
        finance_factories.CustomReimbursementRuleFactory(offer=stock.offer)

        with pytest.raises(api_errors.ApiErrors) as error:
            api.create_stock(offer=offer, quantity=None, price=9)
        assert error.value.errors["price"][0].startswith("Vous ne pouvez pas modifier le prix")

    def test_does_not_allow_beginning_datetime_for_thing_offers(self):
        # Given
        offer = factories.ThingOfferFactory()
        beginning_date = datetime.utcnow() + timedelta(days=4)

        # When
        with pytest.raises(api_errors.ApiErrors) as error:
            api.create_stock(
                offer=offer,
                price=0,
                quantity=None,
                beginning_datetime=beginning_date,
                booking_limit_datetime=beginning_date,
            )

        # Then
        assert error.value.errors == {
            "global": ["Impossible de mettre une date de début si l'offre ne porte pas sur un évènement"],
        }

    def test_validate_booking_limit_datetime_with_expiration_datetime(self):
        # Given
        offer = factories.DigitalOfferFactory()

        # When
        with pytest.raises(api_errors.ApiErrors) as error:
            api.create_stock(
                offer=offer,
                price=0,
                quantity=None,
                booking_limit_datetime=None,
                activation_codes=["ABC", "DEF"],
                activation_codes_expiration_datetime=datetime.utcnow(),
            )

        # Then
        assert error.value.errors == {
            "bookingLimitDatetime": [
                (
                    "Une date limite de validité a été renseignée. Dans ce cas, il faut également"
                    " renseigner une date limite de réservation qui doit être antérieure d'au moins 7 jours."
                ),
            ],
        }

    def test_does_not_allow_missing_dates_for_an_event_offer(self):
        # Given
        offer = factories.EventOfferFactory()

        # When
        with pytest.raises(api_errors.ApiErrors) as error:
            api.create_stock(offer=offer, price=10, quantity=None, beginning_datetime=None, booking_limit_datetime=None)

        # Then
        assert error.value.errors == {"beginningDatetime": ["Ce paramètre est obligatoire"]}

    def test_does_not_allow_booking_limit_after_beginning_for_an_event_offer(self):
        # Given
        offer = factories.EventOfferFactory()
        beginning_date = datetime.utcnow() + timedelta(days=4)
        booking_limit = beginning_date + timedelta(days=4)

        # When
        with pytest.raises(exceptions.BookingLimitDatetimeTooLate):
            api.create_stock(
                offer=offer,
                price=10,
                quantity=None,
                beginning_datetime=beginning_date,
                booking_limit_datetime=booking_limit,
            )

        # Then
        assert models.Stock.query.count() == 0

    def test_does_not_allow_creation_on_a_synchronized_offer(self):
        # Given
        offer = factories.ThingOfferFactory(
            lastProvider=providers_factories.AllocineProviderFactory(localClass="TiteLiveStocks")
        )

        # When
        with pytest.raises(api_errors.ApiErrors) as error:
            api.create_stock(offer=offer, price=10, quantity=1)

        # Then
        assert error.value.errors == {"global": ["Les offres importées ne sont pas modifiables"]}

    @mock.patch("pcapi.core.mails.transactional.send_first_venue_approved_offer_email_to_pro")
    def test_create_stock_for_non_approved_offer_fails(self, mocked_send_first_venue_approved_offer_email_to_pro):
        offer = factories.ThingOfferFactory(validation=models.OfferValidationStatus.PENDING)

        with pytest.raises(api_errors.ApiErrors) as error:
            api.create_stock(offer=offer, price=10, quantity=7)

        assert error.value.errors == {
            "global": ["Les offres refusées ou en attente de validation ne sont pas modifiables"]
        }
        assert models.Stock.query.count() == 0

        assert not mocked_send_first_venue_approved_offer_email_to_pro.called


@pytest.mark.usefixtures("db_session")
class EditStockTest:
    def test_edit_stock(self):
        # Given
        existing_stock = factories.StockFactory(price=10)

        # When
        edited_stock, update_info = api.edit_stock(stock=existing_stock, price=5, quantity=7)

        # Then
        assert edited_stock == models.Stock.query.filter_by(id=existing_stock.id).first()
        assert edited_stock.price == 5
        assert edited_stock.quantity == 7
        assert update_info is False

    def test_edit_beginning_datetime(self):
        # Given
        previous_booking_limit = datetime.utcnow() + timedelta(days=4)
        previous_beginning = datetime.utcnow() + timedelta(days=8)
        new_beginning = datetime.utcnow() + timedelta(days=15)
        existing_stock = factories.EventStockFactory(
            price=10, quantity=7, beginningDatetime=previous_beginning, bookingLimitDatetime=previous_booking_limit
        )

        # When
        edited_stock, update_info = api.edit_stock(
            stock=existing_stock,
            price=12,
            quantity=77,
            beginning_datetime=new_beginning,
            booking_limit_datetime=previous_booking_limit,
        )

        # Then
        assert edited_stock == models.Stock.query.filter_by(id=existing_stock.id).first()
        assert edited_stock.price == 12
        assert edited_stock.quantity == 77
        assert edited_stock.beginningDatetime == new_beginning
        assert edited_stock.bookingLimitDatetime == previous_booking_limit
        assert update_info is True

    def test_edit_event_without_beginning_update(self):
        # Given
        previous_booking_limit = datetime.utcnow() + timedelta(days=4)
        beginning = datetime.utcnow() + timedelta(days=8)
        new_booking_limit = datetime.utcnow() + timedelta(days=6)
        existing_stock = factories.EventStockFactory(
            price=10, quantity=7, beginningDatetime=beginning, bookingLimitDatetime=previous_booking_limit
        )

        # When
        edited_stock, update_info = api.edit_stock(
            stock=existing_stock,
            price=10,
            quantity=7,
            beginning_datetime=beginning,
            booking_limit_datetime=new_booking_limit,
        )

        # Then
        assert edited_stock == models.Stock.query.filter_by(id=existing_stock.id).first()
        assert edited_stock.price == 10
        assert edited_stock.quantity == 7
        assert edited_stock.beginningDatetime == beginning
        assert edited_stock.bookingLimitDatetime == new_booking_limit
        assert update_info is False

    def test_update_fields_updated_on_allocine_stocks(self):
        allocine_provider = providers_factories.ProviderFactory(localClass="AllocineStocks")
        stock = factories.StockFactory(
            fieldsUpdated=["price"],  # suppose we already customized the price
            quantity=5,
            offer__idAtProvider="dummy",
            offer__lastProviderId=allocine_provider.id,
        )

        edited_stock, _ = api.edit_stock(stock=stock, price=stock.price, quantity=50)

        assert edited_stock == models.Stock.query.filter_by(id=stock.id).first()
        assert set(stock.fieldsUpdated) == {"quantity", "price"}

    def test_does_not_allow_invalid_quantity(self):
        # Given
        existing_stock = factories.StockFactory(price=10)

        # When
        with pytest.raises(api_errors.ApiErrors) as error:
            api.edit_stock(stock=existing_stock, quantity=-4, price=30)

        # Then
        assert error.value.errors == {"quantity": ["Le stock doit être positif"]}

    def test_does_not_allow_invalid_price(self):
        existing_stock = factories.StockFactory(price=10)

        # When
        with pytest.raises(api_errors.ApiErrors) as error:
            api.edit_stock(stock=existing_stock, price=-3, quantity=existing_stock.quantity)

        # Then
        assert error.value.errors == {"price": ["Le prix doit être positif"]}

    def test_does_not_allow_price_above_300_euros_on_edition_for_individual_thing_offers(self):
        # Given
        existing_stock = factories.ThingStockFactory(price=10)

        # When
        with pytest.raises(api_errors.ApiErrors) as error:
            api.edit_stock(stock=existing_stock, price=301, quantity=existing_stock.quantity)

        # Then
        assert error.value.errors == {
            "price300": ["Le prix d’une offre ne peut excéder 300 euros."],
        }

    def test_does_not_allow_price_above_300_euros(self):
        # Given
        existing_stock = factories.EventStockFactory(price=10)
        now = datetime.utcnow()

        # When
        with pytest.raises(api_errors.ApiErrors) as error:
            api.edit_stock(
                stock=existing_stock,
                price=301,
                quantity=None,
                beginning_datetime=now,
                booking_limit_datetime=now,
            )

        # Then
        assert error.value.errors == {"price300": ["Le prix d’une offre ne peut excéder 300 euros."]}

    def test_cannot_edit_price_if_reimbursement_rule_exists(self):
        stock = factories.ThingStockFactory(price=10)
        finance_factories.CustomReimbursementRuleFactory(offer=stock.offer)

        with pytest.raises(api_errors.ApiErrors) as error:
            api.edit_stock(stock=stock, price=9, quantity=None)
        assert error.value.errors["price"][0].startswith("Vous ne pouvez pas modifier le prix")

    def test_does_not_allow_beginning_datetime_for_thing_offers(self):
        # Given
        offer = factories.ThingOfferFactory()
        beginning_date = datetime.utcnow() + timedelta(days=4)
        existing_stock = factories.StockFactory(offer=offer, price=10)

        # When
        with pytest.raises(api_errors.ApiErrors) as error:
            api.edit_stock(
                stock=existing_stock,
                price=0,
                quantity=None,
                beginning_datetime=beginning_date,
                booking_limit_datetime=beginning_date,
            )

        # Then
        assert error.value.errors == {
            "global": ["Impossible de mettre une date de début si l'offre ne porte pas sur un évènement"],
        }

    def test_validate_booking_limit_datetime_with_expiration_datetime(self):
        # Given
        existing_stock = factories.StockFactory(bookingLimitDatetime=datetime.utcnow())
        factories.ActivationCodeFactory(expirationDate=datetime.utcnow(), stock=existing_stock)

        # When
        with pytest.raises(api_errors.ApiErrors) as error:
            api.edit_stock(stock=existing_stock, price=0, quantity=None, booking_limit_datetime=None)

        # Then
        assert error.value.errors == {
            "bookingLimitDatetime": [
                (
                    "Une date limite de validité a été renseignée. Dans ce cas, il faut également"
                    " renseigner une date limite de réservation qui doit être antérieure d'au moins 7 jours."
                ),
            ],
        }

    def test_does_not_allow_a_negative_remaining_quantity(self):
        # Given
        booking = bookings_factories.BookingFactory(stock__quantity=10)

        # When
        with pytest.raises(api_errors.ApiErrors) as error:
            api.edit_stock(stock=booking.stock, price=10, quantity=0)

        # Then
        assert error.value.errors == {"quantity": ["Le stock total ne peut être inférieur au nombre de réservations"]}

    def test_does_not_allow_booking_limit_after_beginning_for_an_event_offer(self):
        # Given
        previous_booking_limit = datetime.utcnow()
        previous_beginning = datetime.utcnow() + timedelta(days=1)
        existing_stock = factories.EventStockFactory(
            bookingLimitDatetime=previous_booking_limit, beginningDatetime=previous_beginning
        )
        beginning_date = datetime.utcnow() + timedelta(days=4)
        booking_limit = beginning_date + timedelta(days=4)

        # When
        with pytest.raises(exceptions.BookingLimitDatetimeTooLate):
            api.edit_stock(
                stock=existing_stock,
                beginning_datetime=beginning_date,
                booking_limit_datetime=booking_limit,
                price=10,
                quantity=existing_stock.quantity,
            )

        # Then
        assert existing_stock.bookingLimitDatetime == previous_booking_limit
        assert existing_stock.beginningDatetime == previous_beginning

    def test_does_not_allow_edition_of_a_past_event_stock(self):
        # Given
        date_in_the_past = datetime.utcnow() - timedelta(days=4)
        existing_stock = factories.EventStockFactory(price=10, beginningDatetime=date_in_the_past)

        # When
        with pytest.raises(api_errors.ApiErrors) as error:
            api.edit_stock(
                stock=existing_stock,
                price=4,
                beginning_datetime=date_in_the_past,
                quantity=1,
            )

        # Then
        assert error.value.errors == {"global": ["Les évènements passés ne sont pas modifiables"]}

    def test_allow_edition_of_price_and_quantity_for_stocks_of_offers_synchronized_with_allocine(self):
        offer = factories.EventOfferFactory(
            lastProvider=providers_factories.AllocineProviderFactory(localClass="AllocineStocks")
        )
        date_in_the_future = datetime.utcnow() + timedelta(days=4)
        existing_stock = factories.StockFactory(offer=offer, price=10, beginningDatetime=date_in_the_future, quantity=2)

        # When
        api.edit_stock(
            stock=existing_stock,
            price=4,
            quantity=None,
            beginning_datetime=existing_stock.beginningDatetime,
            booking_limit_datetime=existing_stock.bookingLimitDatetime,
        )

        # Then
        edited_stock = models.Stock.query.filter_by(id=existing_stock.id).first()
        assert edited_stock.price == 4
        assert edited_stock.quantity == None

    def test_does_not_allow_edition_of_beginningDateTime_for_stocks_of_offers_synchronized_with_allocine(self):
        # Given
        offer = factories.EventOfferFactory(
            lastProvider=providers_factories.AllocineProviderFactory(localClass="AllocineStocks")
        )
        date_in_the_future = datetime.utcnow() + timedelta(days=4)
        other_date_in_the_future = datetime.utcnow() + timedelta(days=6)
        existing_stock = factories.StockFactory(offer=offer, price=10, beginningDatetime=date_in_the_future)

        # When
        with pytest.raises(api_errors.ApiErrors) as error:
            api.edit_stock(
                stock=existing_stock,
                price=10,
                quantity=None,
                beginning_datetime=other_date_in_the_future,
                booking_limit_datetime=other_date_in_the_future,
            )

        # Then
        assert error.value.errors == {"global": ["Pour les offres importées, certains champs ne sont pas modifiables"]}

    @mock.patch("pcapi.core.mails.transactional.send_first_venue_approved_offer_email_to_pro")
    def test_edit_stock_of_non_approved_offer_fails(
        self,
        mocked_send_first_venue_approved_offer_email_to_pro,
    ):
        offer = factories.ThingOfferFactory(validation=models.OfferValidationStatus.PENDING)
        existing_stock = factories.StockFactory(offer=offer, price=10)

        with pytest.raises(api_errors.ApiErrors) as error:
            api.edit_stock(stock=existing_stock, price=5, quantity=7)

        assert error.value.errors == {
            "global": ["Les offres refusées ou en attente de validation ne sont pas modifiables"]
        }
        existing_stock = models.Stock.query.one()
        assert existing_stock.price == 10

        assert not mocked_send_first_venue_approved_offer_email_to_pro.called


@pytest.mark.usefixtures("db_session")
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
        booking1 = bookings_factories.BookingFactory(stock=stock)
        booking2 = bookings_factories.CancelledBookingFactory(stock=stock)
        booking3 = bookings_factories.UsedBookingFactory(stock=stock)
        booking4 = bookings_factories.UsedBookingFactory(stock=stock)
        finance_factories.PricingFactory(
            booking=booking4,
            status=finance_models.PricingStatus.PROCESSED,
        )

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
        booking4 = bookings_models.Booking.query.get(booking4.id)
        assert booking4.status == bookings_models.BookingStatus.USED  # unchanged
        assert booking4.pricings[0].status == finance_models.PricingStatus.PROCESSED  # unchanged

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
                booking1.userId,
                booking3.userId,
            },
            "message": {
                "body": f"""Ta réservation "{stock.offer.name}" a été annulée par l'offreur.""",
                "title": "Réservation annulée",
            },
            "can_be_asynchronously_retried": False,
        }

    def test_can_delete_if_stock_from_provider(self):
        provider = providers_factories.AllocineProviderFactory(localClass="TiteLiveStocks")
        offer = factories.OfferFactory(lastProvider=provider, idAtProvider="1")
        stock = factories.StockFactory(offer=offer)

        api.delete_stock(stock)

        stock = models.Stock.query.one()
        assert stock.isSoftDeleted

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
    @pytest.mark.usefixtures("db_session")
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
    @pytest.mark.usefixtures("db_session")
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
    @conftest.clean_database
    # this test needs "clean_database" instead of "db_session" fixture because with the latter, the mediation would still be present in databse
    def test_rollback_if_exception(self, mock_store_public_object, clear_tests_assets_bucket):
        user = users_factories.ProFactory()
        offer = factories.ThingOfferFactory()
        image_as_bytes = (IMAGES_DIR / "mouette_full_size.jpg").read_bytes()
        existing_number_of_files = len(os.listdir(self.THUMBS_DIR))

        # When
        with pytest.raises(exceptions.ThumbnailStorageError):
            api.create_mediation(user, offer, "©Photographe", image_as_bytes)
        db.session.rollback()

        # Then
        assert models.Mediation.query.count() == 0
        assert len(os.listdir(self.THUMBS_DIR)) == existing_number_of_files


@pytest.mark.usefixtures("db_session")
class CreateOfferTest:
    def test_create_offer_from_scratch(self):
        venue = offerers_factories.VenueFactory()
        offerer = venue.managingOfferer

        offer = api.create_offer(
            venue=venue,
            name="A pretty good offer",
            subcategory_id=subcategories.SEANCE_CINE.id,
            external_ticket_office_url="http://example.net",
            audio_disability_compliant=True,
            mental_disability_compliant=True,
            motor_disability_compliant=True,
            visual_disability_compliant=True,
        )

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
        assert offer.extraData == {}
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

        offer = api.create_offer(
            venue=venue,
            name="FONDATION T.1",
            subcategory_id=subcategories.LIVRE_PAPIER.id,
            extra_data={"isbn": "9782207300893", "author": "Isaac Asimov"},
            audio_disability_compliant=True,
            mental_disability_compliant=True,
            motor_disability_compliant=True,
            visual_disability_compliant=False,
        )

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

        with pytest.raises(exceptions.NotEligibleISBN) as exception_info:
            api.create_offer(
                venue=venue,
                name="FONDATION T.1",
                subcategory_id=subcategories.LIVRE_PAPIER.id,
                extra_data={"isbn": "9782207300893"},
                audio_disability_compliant=True,
                mental_disability_compliant=True,
                motor_disability_compliant=True,
                visual_disability_compliant=False,
            )

        assert exception_info.value.errors == {"isbn": ["product not eligible to pass Culture"]}

    @override_features(ENABLE_ISBN_REQUIRED_IN_LIVRE_EDITION_OFFER_CREATION=True)
    def test_create_offer_livre_edition_from_isbn_with_product_not_exists_should_fail(self):
        venue = offerers_factories.VenueFactory()

        with pytest.raises(exceptions.NotEligibleISBN) as exception_info:
            api.create_offer(
                venue=venue,
                name="FONDATION T.1",
                subcategory_id=subcategories.LIVRE_PAPIER.id,
                extra_data={"isbn": "9782207300893"},
                audio_disability_compliant=True,
                mental_disability_compliant=True,
                motor_disability_compliant=True,
                visual_disability_compliant=False,
            )

        assert exception_info.value.errors == {"isbn": ["product not eligible to pass Culture"]}

    def test_cannot_create_activation_offer(self):
        venue = offerers_factories.VenueFactory()
        with pytest.raises(exceptions.SubCategoryIsInactive) as error:
            api.create_offer(
                venue=venue,
                name="An offer he can't refuse",
                subcategory_id=subcategories.ACTIVATION_EVENT.id,
                audio_disability_compliant=True,
                mental_disability_compliant=True,
                motor_disability_compliant=True,
                visual_disability_compliant=True,
            )

        assert error.value.errors["subcategory"] == [
            "Une offre ne peut être créée ou éditée en utilisant cette sous-catégorie"
        ]

    def test_cannot_create_offer_when_invalid_subcategory(self):
        venue = offerers_factories.VenueFactory()
        with pytest.raises(exceptions.UnknownOfferSubCategory) as error:
            api.create_offer(
                venue=venue,
                name="An offer he can't refuse",
                subcategory_id="TOTO",
                audio_disability_compliant=True,
                mental_disability_compliant=True,
                motor_disability_compliant=True,
                visual_disability_compliant=True,
            )

        assert error.value.errors["subcategory"] == ["La sous-catégorie de cette offre est inconnue"]

    def test_raise_error_if_extra_data_mandatory_fields_not_provided(self):
        venue = offerers_factories.VenueFactory()

        with pytest.raises(api_errors.ApiErrors) as error:
            api.create_offer(
                venue=venue,
                name="A pretty good offer",
                subcategory_id=subcategories.CONCERT.id,
                audio_disability_compliant=True,
                mental_disability_compliant=True,
                motor_disability_compliant=True,
                visual_disability_compliant=True,
            )

        assert error.value.errors["musicType"] == ["Ce champ est obligatoire"]


@pytest.mark.usefixtures("db_session")
class UpdateOfferTest:
    @mock.patch("pcapi.core.search.async_index_offer_ids")
    def test_basics(self, mocked_async_index_offer_ids):
        offer = factories.OfferFactory(
            isDuo=False, bookingEmail="old@example.com", subcategoryId=subcategories.ESCAPE_GAME.id
        )

        offer = api.update_offer(offer, isDuo=True, bookingEmail="new@example.com")

        assert offer.isDuo
        assert offer.bookingEmail == "new@example.com"
        mocked_async_index_offer_ids.assert_called_once_with([offer.id])

    def test_update_extra_data_should_raise_error_when_mandatory_field_not_provided(self):
        offer = factories.OfferFactory(subcategoryId=subcategories.SPECTACLE_REPRESENTATION.id)

        with pytest.raises(api_errors.ApiErrors) as error:
            api.update_offer(offer, extraData={"author": "Asimov"})

        assert error.value.errors == {
            "showType": ["Ce champ est obligatoire"],
            "showSubType": ["Ce champ est obligatoire"],
        }

    def test_error_when_missing_mandatory_extra_data(self):
        offer = factories.OfferFactory(
            subcategoryId=subcategories.SPECTACLE_REPRESENTATION.id, extraData={"showType": 200}
        )
        with pytest.raises(api_errors.ApiErrors) as error:
            offer = api.update_offer(offer, extraData=None)
        assert error.value.errors == {
            "showType": ["Ce champ est obligatoire"],
            "showSubType": ["Ce champ est obligatoire"],
        }

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
        offer = factories.OfferFactory(
            lastProvider=provider, name="Old name", subcategoryId=subcategories.SEANCE_CINE.id
        )

        api.update_offer(offer, name="Old name", isDuo=True)

        offer = models.Offer.query.one()
        assert offer.name == "Old name"
        assert offer.isDuo

    def test_forbidden_on_allocine_offer_on_certain_fields(self):
        provider = providers_factories.AllocineProviderFactory(localClass="AllocineStocks")
        offer = factories.OfferFactory(
            lastProvider=provider, name="Old name", subcategoryId=subcategories.SEANCE_CINE.id
        )

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
            lastProvider=provider,
            name="Old name",
            isDuo=False,
            audioDisabilityCompliant=True,
            subcategoryId=subcategories.SEANCE_CINE.id,
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


@pytest.mark.usefixtures("db_session")
class BatchUpdateOffersTest:
    @mock.patch("pcapi.core.search.async_index_offer_ids")
    def test_activate_empty_list(self, mocked_async_index_offer_ids, caplog):
        pending_offer = factories.OfferFactory(validation=models.OfferValidationStatus.PENDING)

        query = models.Offer.query.filter(models.Offer.id.in_({pending_offer.id}))
        with caplog.at_level(logging.INFO):
            api.batch_update_offers(query, {"isActive": True})

        assert not models.Offer.query.get(pending_offer.id).isActive
        mocked_async_index_offer_ids.assert_not_called()

        assert len(caplog.records) == 2
        first_record = caplog.records[0]
        second_record = caplog.records[1]

        assert first_record.message == "Batch update of offers"
        assert first_record.extra == {
            "nb_offers": 0,
            "updated_fields": {"isActive": True},
            "venue_ids": [],
        }
        assert second_record.message == "Offers has been activated"
        assert second_record.extra == {"offer_ids": [], "venue_id": []}

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

        assert len(caplog.records) == 2
        first_record = caplog.records[0]
        second_record = caplog.records[1]

        assert first_record.message == "Batch update of offers"
        assert first_record.extra == {
            "nb_offers": 2,
            "updated_fields": {"isActive": True},
            "venue_ids": [offer1.venueId, offer2.venueId],
        }
        assert second_record.message == "Offers has been activated"
        assert second_record.extra.keys() == {"offer_ids", "venue_id"}
        assert set(second_record.extra["offer_ids"]) == {offer1.id, offer2.id}
        assert second_record.extra["venue_id"] == [offer1.venueId, offer2.venueId]

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

        assert len(caplog.records) == 2
        first_record = caplog.records[0]
        second_record = caplog.records[1]

        assert first_record.message == "Batch update of offers"
        assert first_record.extra == {
            "nb_offers": 2,
            "updated_fields": {"isActive": False},
            "venue_ids": [offer1.venueId, offer2.venueId],
        }
        assert second_record.message == "Offers has been deactivated"
        assert second_record.extra.keys() == {"offer_ids", "venue_id"}
        assert set(second_record.extra["offer_ids"]) == {offer1.id, offer2.id}
        assert second_record.extra["venue_id"] == [offer1.venueId, offer2.venueId]


@pytest.mark.usefixtures("db_session")
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


@pytest.mark.usefixtures("db_session")
class OfferExpenseDomainsTest:
    def test_offer_expense_domains(self):
        assert api.get_expense_domains(factories.OfferFactory(subcategoryId=subcategories.EVENEMENT_JEU.id)) == [
            users_models.ExpenseDomain.ALL
        ]
        assert set(
            api.get_expense_domains(
                factories.OfferFactory(subcategoryId=subcategories.JEU_EN_LIGNE.id, url="https://example.com")
            )
        ) == {
            users_models.ExpenseDomain.ALL,
            users_models.ExpenseDomain.DIGITAL,
        }
        assert set(api.get_expense_domains(factories.OfferFactory(subcategoryId=subcategories.OEUVRE_ART.id))) == {
            users_models.ExpenseDomain.ALL,
            users_models.ExpenseDomain.PHYSICAL,
        }


@pytest.mark.usefixtures("db_session")
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


@pytest.mark.usefixtures("db_session")
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


@pytest.mark.usefixtures("db_session")
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


@pytest.mark.usefixtures("db_session")
class ComputeOfferValidationTest:
    def test_approve_if_no_offer_validation_config(self):
        offer = models.Offer(name="Maybe we should reject this offer")

        assert api.set_offer_status_based_on_fraud_criteria(offer) == models.OfferValidationStatus.APPROVED

    def test_matching_keyword_in_name(self):
        offer = factories.OfferFactory(name="A suspicious offer")
        factories.StockFactory(price=10, offer=offer)
        api.import_offer_validation_config(SIMPLE_OFFER_VALIDATION_CONFIG, users_factories.UserFactory())
        assert api.set_offer_status_based_on_fraud_criteria(offer) == models.OfferValidationStatus.PENDING


@pytest.mark.usefixtures("db_session")
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


@pytest.mark.usefixtures("db_session")
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
            api.import_offer_validation_config(config_yaml, users_factories.UserFactory())
        assert error.value.__dict__ == {"errors": {"KeyError": "'Wrong key: WRONG_KEY'"}}

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
            api.import_offer_validation_config(config_yaml, users_factories.UserFactory())
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
            api.import_offer_validation_config(config_yaml, users_factories.UserFactory())
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
            api.import_offer_validation_config(config_yaml, users_factories.UserFactory())

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
        api.import_offer_validation_config(config_yaml, users_factories.UserFactory())

        current_config = models.OfferValidationConfig.query.one()
        assert current_config is not None
        assert current_config.specs["minimum_score"] == 0.6
        assert current_config.specs["rules"][0]["conditions"][0]["condition"]["comparated"] == "REJECTED"
        assert current_config.specs["rules"][1]["conditions"][0]["attribute"] == "max_price"


@pytest.mark.usefixtures("db_session")
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
        offer_validation_config = api.import_offer_validation_config(config_yaml, users_factories.UserFactory())
        min_score, validation_rules = offer_validation.parse_offer_validation_config(offer, offer_validation_config)
        assert min_score == 0.6
        assert len(validation_rules) == 1
        assert validation_rules[0].factor == 0
        assert validation_rules[0].name == "modalités de retrait"
        assert validation_rules[0].offer_validation_items[0].model == offer
        assert validation_rules[0].offer_validation_items[0].attribute == "withdrawalDetails"


@pytest.mark.usefixtures("db_session")
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


@pytest.mark.usefixtures("db_session")
class LoadProductByIsbn:
    def test_returns_product_if_found_and_is_gcu_compatible(self):
        isbn = "2221001648"
        product = factories.ProductFactory(extraData={"isbn": isbn}, isGcuCompatible=True)

        result = api._load_product_by_isbn(isbn)

        assert result == product

    def test_raise_api_error_if_no_product(self):
        factories.ProductFactory(isGcuCompatible=True)

        with pytest.raises(exceptions.NotEligibleISBN) as exception_info:
            api._load_product_by_isbn("2221001649")

        assert exception_info.value.errors["isbn"] == ["product not eligible to pass Culture"]

    def test_raise_api_error_if_product_is_not_gcu_compatible(self):
        isbn = "2221001648"
        factories.ProductFactory(extraData={"isbn": isbn}, isGcuCompatible=False)

        with pytest.raises(exceptions.NotEligibleISBN) as exception_info:
            api._load_product_by_isbn(isbn)

        assert exception_info.value.errors["isbn"] == ["product not eligible to pass Culture"]


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


@pytest.mark.usefixtures("db_session")
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


@pytest.mark.usefixtures("db_session")
class DeleteDraftOffersTest:
    def test_delete_draft_with_mediation_offer_criterion_activation_code_and_stocks(self, client):
        criterion = criteria_factories.CriterionFactory()
        draft_offer = factories.OfferFactory(validation=OfferValidationStatus.DRAFT, criteria=[criterion])
        factories.MediationFactory(offer=draft_offer)
        stock = factories.StockFactory(offer=draft_offer)
        factories.ActivationCodeFactory(stock=stock)
        other_draft_offer = factories.OfferFactory(validation=OfferValidationStatus.DRAFT)

        offer_ids = [draft_offer.id, other_draft_offer.id]

        api.batch_delete_draft_offers(models.Offer.query.filter(models.Offer.id.in_(offer_ids)))

        assert criteria_models.OfferCriterion.query.count() == 0
        assert models.Mediation.query.count() == 0
        assert models.Stock.query.count() == 0
        assert models.Offer.query.count() == 0
        assert models.ActivationCode.query.count() == 0


class FormatExtraDataTest:
    def test_format_extra_data(self):
        extra_data = {
            "musicType": "1",  # applicable and filled
            "musicSubType": "100",  # applicable and filled
            "other": "value",  # not applicable field
            "performer": "",  # applicable but empty
        }
        assert api._format_extra_data(subcategories.FESTIVAL_MUSIQUE.id, extra_data) == {
            "musicType": "1",
            "musicSubType": "100",
        }


@pytest.mark.usefixtures("db_session")
class UpdateStockQuantityToMatchCinemaVenueProviderRemainingPlacesTest:
    DATETIME_10_DAYS_AFTER = datetime.today() + timedelta(days=10)
    DATETIME_10_DAYS_AGO = datetime.today() - timedelta(days=10)

    @override_features(ENABLE_CDS_IMPLEMENTATION=True)
    @pytest.mark.parametrize(
        "show_id, show_beginning_datetime, api_return_value, expected_remaining_quantity",
        [
            (888, DATETIME_10_DAYS_AFTER, {888: 10}, 10),
            (888, DATETIME_10_DAYS_AFTER, {888: 5}, 10),
            (888, DATETIME_10_DAYS_AFTER, {888: 1}, 1),
            (888, DATETIME_10_DAYS_AFTER, {888: 0}, 0),
            (123, DATETIME_10_DAYS_AFTER, {888: 0}, 0),
            (888, DATETIME_10_DAYS_AGO, None, 10),
        ],
    )
    @patch("pcapi.core.search.async_index_offer_ids")
    @patch("pcapi.core.offers.api.external_bookings_api.get_shows_stock")
    def test_cds(
        self,
        mocked_get_shows_stock,
        mocked_async_index_offer_ids,
        show_id,
        show_beginning_datetime,
        api_return_value,
        expected_remaining_quantity,
    ):
        cds_provider = providers_repository.get_provider_by_local_class("CDSStocks")
        venue_provider = providers_factories.VenueProviderFactory(provider=cds_provider)
        providers_factories.CinemaProviderPivotFactory(
            venue=venue_provider.venue,
            provider=venue_provider.provider,
            idAtProvider=venue_provider.venueIdAtOfferProvider,
        )
        movie_id = 456
        offer_id_at_provider = f"{movie_id}%{venue_provider.venue.siret}%CDS"
        offer = factories.EventOfferFactory(
            venue=venue_provider.venue, idAtProvider=offer_id_at_provider, lastProviderId=cds_provider.id
        )
        showtime = "2023-02-08"
        stock = factories.EventStockFactory(
            offer=offer,
            quantity=10,
            idAtProviders=f"{offer_id_at_provider}#{show_id}/{showtime}",
            beginningDatetime=show_beginning_datetime,
        )

        mocked_get_shows_stock.return_value = api_return_value
        api.update_stock_quantity_to_match_cinema_venue_provider_remaining_places(offer)

        assert stock.remainingQuantity == expected_remaining_quantity
        if expected_remaining_quantity == 0:
            mocked_async_index_offer_ids.assert_called_once_with([offer.id])
        else:
            mocked_async_index_offer_ids.assert_not_called()

    @override_features(ENABLE_BOOST_API_INTEGRATION=True)
    @pytest.mark.parametrize(
        "show_id, show_beginning_datetime, api_return_value, expected_remaining_quantity",
        [
            (888, DATETIME_10_DAYS_AFTER, {888: 10}, 10),
            (888, DATETIME_10_DAYS_AFTER, {888: 5}, 10),
            (888, DATETIME_10_DAYS_AFTER, {888: 1}, 1),
            (888, DATETIME_10_DAYS_AFTER, {888: 0}, 0),
            (123, DATETIME_10_DAYS_AFTER, {888: 0}, 0),
            (888, DATETIME_10_DAYS_AGO, None, 10),
        ],
    )
    @patch("pcapi.core.search.async_index_offer_ids")
    @patch("pcapi.core.offers.api.external_bookings_api.get_movie_stocks")
    def test_boost(
        self,
        mocked_get_movie_shows_stock,
        mocked_async_index_offer_ids,
        show_id,
        show_beginning_datetime,
        api_return_value,
        expected_remaining_quantity,
    ):
        boost_provider = providers_repository.get_provider_by_local_class("BoostStocks")
        venue_provider = providers_factories.VenueProviderFactory(provider=boost_provider)
        providers_factories.CinemaProviderPivotFactory(
            venue=venue_provider.venue,
            provider=venue_provider.provider,
            idAtProvider=venue_provider.venueIdAtOfferProvider,
        )
        movie_id = 456
        offer_id_at_provider = f"{movie_id}%{venue_provider.venueId}%Boost"
        offer = factories.EventOfferFactory(
            venue=venue_provider.venue, idAtProvider=offer_id_at_provider, lastProviderId=boost_provider.id
        )
        stock = factories.EventStockFactory(
            offer=offer,
            quantity=10,
            idAtProviders=f"{offer_id_at_provider}#{show_id}",
            beginningDatetime=show_beginning_datetime,
        )

        mocked_get_movie_shows_stock.return_value = api_return_value
        api.update_stock_quantity_to_match_cinema_venue_provider_remaining_places(offer)

        assert stock.remainingQuantity == expected_remaining_quantity
        if expected_remaining_quantity == 0:
            mocked_async_index_offer_ids.assert_called_once_with([offer.id])
        else:
            mocked_async_index_offer_ids.assert_not_called()

    @override_features(ENABLE_CGR_INTEGRATION=True)
    @pytest.mark.parametrize(
        "show_id, show_beginning_datetime, api_return_value, expected_remaining_quantity",
        [
            (888, DATETIME_10_DAYS_AFTER, {888: 10}, 10),
            (888, DATETIME_10_DAYS_AFTER, {888: 5}, 10),
            (888, DATETIME_10_DAYS_AFTER, {888: 1}, 1),
            (888, DATETIME_10_DAYS_AFTER, {888: 0}, 0),
            (123, DATETIME_10_DAYS_AFTER, {888: 0}, 0),
            (888, DATETIME_10_DAYS_AGO, None, 10),
        ],
    )
    @patch("pcapi.core.search.async_index_offer_ids")
    @patch("pcapi.core.offers.api.external_bookings_api.get_movie_stocks")
    def test_cgr(
        self,
        mocked_get_movie_shows_stock,
        mocked_async_index_offer_ids,
        show_id,
        show_beginning_datetime,
        api_return_value,
        expected_remaining_quantity,
    ):
        cgr_provider = providers_repository.get_provider_by_local_class("CGRStocks")
        venue_provider = providers_factories.VenueProviderFactory(provider=cgr_provider)
        providers_factories.CinemaProviderPivotFactory(
            venue=venue_provider.venue,
            provider=venue_provider.provider,
            idAtProvider=venue_provider.venueIdAtOfferProvider,
        )
        movie_id = 523
        offer_id_at_provider = f"{movie_id}%{venue_provider.venueId}%CGR"
        offer = factories.EventOfferFactory(
            venue=venue_provider.venue, idAtProvider=offer_id_at_provider, lastProviderId=cgr_provider.id
        )
        stock = factories.EventStockFactory(
            offer=offer,
            quantity=10,
            idAtProviders=f"{offer_id_at_provider}#{show_id}",
            beginningDatetime=show_beginning_datetime,
        )

        mocked_get_movie_shows_stock.return_value = api_return_value
        api.update_stock_quantity_to_match_cinema_venue_provider_remaining_places(offer)

        assert stock.remainingQuantity == expected_remaining_quantity
        if expected_remaining_quantity == 0:
            mocked_async_index_offer_ids.assert_called_once_with([offer.id])
        else:
            mocked_async_index_offer_ids.assert_not_called()

    @override_features(ENABLE_BOOST_API_INTEGRATION=True)
    @patch("pcapi.core.search.async_index_offer_ids")
    @patch("pcapi.core.offers.api.external_bookings_api.get_movie_stocks")
    def test_should_retry_when_inconsistent_stock(self, mocked_get_movie_shows_stock, mocked_async_index_offer_ids):
        boost_provider = providers_repository.get_provider_by_local_class("BoostStocks")
        venue_provider = providers_factories.VenueProviderFactory(provider=boost_provider)
        movie_id = 456
        show_id = 777
        offer_id_at_provider = f"{movie_id}%{venue_provider.venueId}%Boost"
        providers_factories.CinemaProviderPivotFactory(
            venue=venue_provider.venue,
            provider=venue_provider.provider,
            idAtProvider=venue_provider.venueIdAtOfferProvider,
        )
        offer = factories.EventOfferFactory(
            venue=venue_provider.venue, idAtProvider=offer_id_at_provider, lastProviderId=boost_provider.id
        )
        stock = factories.EventStockFactory(
            offer=offer,
            quantity=10,
            idAtProviders=f"{offer_id_at_provider}#{show_id}",
        )
        bookings_factories.BookingFactory(stock=stock)
        stock.dnBookedQuantity = 0

        mocked_get_movie_shows_stock.return_value = {777: 0}
        api.update_stock_quantity_to_match_cinema_venue_provider_remaining_places(offer)

        assert stock.remainingQuantity == 0
        mocked_async_index_offer_ids.assert_called_once_with([offer.id])
