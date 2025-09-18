import copy
import decimal
import json
import logging
import os
import pathlib
from datetime import date
from datetime import datetime
from datetime import timedelta
from datetime import timezone
from decimal import Decimal
from unittest import mock

import pytest
import sqlalchemy as sa
import time_machine
from factory.faker import faker
from pydantic.v1 import ValidationError

import pcapi.core.bookings.factories as bookings_factories
import pcapi.core.bookings.models as bookings_models
import pcapi.core.chronicles.factories as chronicles_factories
import pcapi.core.chronicles.models as chronicles_models
import pcapi.core.criteria.factories as criteria_factories
import pcapi.core.criteria.models as criteria_models
import pcapi.core.educational.factories as educational_factories
import pcapi.core.educational.models as educational_models
import pcapi.core.finance.factories as finance_factories
import pcapi.core.finance.models as finance_models
import pcapi.core.mails.testing as mails_testing
import pcapi.core.offerers.factories as offerers_factories
import pcapi.core.offerers.models as offerers_models
import pcapi.core.providers.factories as providers_factories
import pcapi.core.providers.repository as providers_repository
import pcapi.core.reactions.factories as reactions_factories
import pcapi.core.reactions.models as reactions_models
import pcapi.core.search.testing as search_testing
import pcapi.core.users.factories as users_factories
import pcapi.core.users.models as users_models
from pcapi.connectors import youtube
from pcapi.connectors.acceslibre import ExpectedFieldsEnum as acceslibre_enum
from pcapi.connectors.serialization.youtube_serializers import YoutubeApiResponse
from pcapi.core import search
from pcapi.core.categories import subcategories
from pcapi.core.categories.models import EacFormat
from pcapi.core.offerers.schemas import VenueTypeCode
from pcapi.core.offers import api
from pcapi.core.offers import exceptions
from pcapi.core.offers import factories
from pcapi.core.offers import models
from pcapi.core.offers import repository as offers_repository
from pcapi.core.offers import schemas as offers_schemas
from pcapi.core.offers.exceptions import NotUpdateProductOrOffers
from pcapi.core.offers.exceptions import ProductNotFound
from pcapi.core.providers.allocine import get_allocine_products_provider
from pcapi.core.reminders import factories as reminders_factories
from pcapi.core.testing import assert_num_queries
from pcapi.models import api_errors
from pcapi.models import db
from pcapi.models.offer_mixin import OfferStatus
from pcapi.models.offer_mixin import OfferValidationStatus
from pcapi.models.offer_mixin import OfferValidationType
from pcapi.notifications.push import testing as push_testing
from pcapi.utils.human_ids import humanize
from pcapi.utils.requests import ExternalAPIException
from pcapi.utils.transaction_manager import atomic

import tests
from tests.connectors.titelive import fixtures


IMAGES_DIR = pathlib.Path(tests.__path__[0]) / "files"

Fake = faker.Faker(locale="fr_FR")


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

    def test_create_stock_with_id_at_provider(self):
        # Given
        offer = factories.ThingOfferFactory()

        # When
        created_stock = api.create_stock(offer=offer, price=10, quantity=7, id_at_provider="heyyyy!")

        # Then
        assert created_stock.offerId == offer.id
        assert created_stock.price == 10
        assert created_stock.quantity == 7
        assert created_stock.idAtProviders == "heyyyy!"

    def test_create_stock_with_id_at_provider_that_exists_in_different_offer(self):
        # Given
        id_at_provider = "dos_veces"
        offer = factories.ThingOfferFactory()
        factories.StockFactory(idAtProviders=id_at_provider)

        # When
        created_stock = api.create_stock(offer=offer, price=10, quantity=7, id_at_provider=id_at_provider)

        # Then
        assert created_stock.idAtProviders == id_at_provider

    def test_create_first_stock_of_offer(self):
        # Given
        offer = factories.ThingOfferFactory()
        assert offer.stocks == []

        # When
        api.create_stock(offer=offer, price=10, quantity=7)

        # Then
        assert offer.lastValidationPrice == 10

        # Create a second stock
        api.create_stock(offer=offer, price=20, quantity=7)

        # Then
        assert offer.lastValidationPrice == 10

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

    @pytest.mark.parametrize("new_price", [49, 151])
    def test_does_not_allow_price_outside_of_price_limitation(self, new_price, caplog):
        # Given
        factories.OfferPriceLimitationRuleFactory(
            subcategoryId=subcategories.ACHAT_INSTRUMENT.id, rate=decimal.Decimal("0.5")
        )
        offer_with_no_stock = factories.ThingOfferFactory(
            subcategoryId=subcategories.ACHAT_INSTRUMENT.id,
        )

        api.create_stock(offer=offer_with_no_stock, price=100, quantity=12)
        db.session.refresh(offer_with_no_stock)
        assert offer_with_no_stock.lastValidationPrice == 100

        # When
        with pytest.raises(api_errors.ApiErrors) as error:
            with caplog.at_level(logging.INFO):
                api.create_stock(offer=offer_with_no_stock, price=new_price, quantity=12)

        # Then
        assert error.value.errors == {
            "priceLimitationRule": ["Le prix indiqué est invalide, veuillez créer une nouvelle offre"]
        }

        assert len(caplog.records) == 1
        assert caplog.records[0].message == "Stock update blocked because of price limitation"
        assert caplog.records[0].technical_message_id == "stock.price.forbidden"
        assert caplog.records[0].extra == {
            "offer_id": offer_with_no_stock.id,
            "reference_price": 100,
            "old_price": None,
            "stock_price": new_price,
        }

    @pytest.mark.parametrize("new_price", [49, 151])
    def test_does_not_allow_price_while_no_last_validation_price(self, new_price, caplog):
        # Given
        factories.OfferPriceLimitationRuleFactory(
            subcategoryId=subcategories.ACHAT_INSTRUMENT.id, rate=decimal.Decimal("0.5")
        )
        offer = factories.ThingOfferFactory(subcategoryId=subcategories.ACHAT_INSTRUMENT.id, lastValidationPrice=None)
        factories.ThingStockFactory(price=100, offer=offer)
        factories.ThingStockFactory(price=8, offer=offer)

        # When
        with pytest.raises(api_errors.ApiErrors) as error:
            with caplog.at_level(logging.INFO):
                api.create_stock(offer=offer, price=new_price, quantity=12)

        # Then
        assert error.value.errors == {
            "priceLimitationRule": ["Le prix indiqué est invalide, veuillez créer une nouvelle offre"]
        }

        assert len(caplog.records) == 1
        assert caplog.records[0].message == "Stock update blocked because of price limitation"
        assert caplog.records[0].technical_message_id == "stock.price.forbidden"
        assert caplog.records[0].extra == {
            "offer_id": offer.id,
            "reference_price": 100,
            "old_price": None,
            "stock_price": new_price,
        }

    @pytest.mark.parametrize("new_price", [49, 151])
    def test_allow_price_edition_while_unrelated_price_limitation_rule(self, new_price):
        # Given
        factories.OfferPriceLimitationRuleFactory(
            subcategoryId=subcategories.ABO_BIBLIOTHEQUE.id, rate=decimal.Decimal("0.5")
        )
        offer = factories.ThingStockFactory(
            offer__subcategoryId=subcategories.ACHAT_INSTRUMENT.id,
            offer__lastValidationPrice=decimal.Decimal("100.00"),
            price=decimal.Decimal("100.00"),
        ).offer

        # When
        new_stock = api.create_stock(offer=offer, price=new_price, quantity=12)

        # Then
        assert new_stock.price == decimal.Decimal(str(new_price))

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

    def test_does_not_allow_idAtProvider_that_is_already_taken(self):
        duplicate_id_at_provider = "dos_veces"
        offer = factories.EventOfferFactory()
        factories.StockFactory(offer=offer, idAtProviders=duplicate_id_at_provider)

        with pytest.raises(exceptions.OfferException) as error:
            api.create_stock(
                offer=offer,
                id_at_provider=duplicate_id_at_provider,
                price=10,
                quantity=10,
            )

        assert error.value.errors == {"idAtProvider": ["`dos_veces` is already taken by another offer stock"]}

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
        assert db.session.query(models.Stock).count() == 0

    def test_does_not_allow_creation_on_a_synchronized_offer(self):
        # Given
        offer = factories.ThingOfferFactory(lastProvider=providers_factories.PublicApiProviderFactory())

        # When
        with pytest.raises(api_errors.ApiErrors) as error:
            api.create_stock(offer=offer, price=10, quantity=1)

        # Then
        assert error.value.errors == {"global": ["Les offres importées ne sont pas modifiables"]}

    @mock.patch("pcapi.core.mails.transactional.send_first_venue_approved_offer_email_to_pro")
    def test_create_stock_for_rejected_offer_fails(self, mocked_send_first_venue_approved_offer_email_to_pro):
        offer = factories.ThingOfferFactory(validation=models.OfferValidationStatus.REJECTED)

        with pytest.raises(exceptions.OfferException) as error:
            api.create_stock(offer=offer, price=10, quantity=7)

        assert error.value.errors == {"global": ["Les offres refusées ne sont pas modifiables"]}
        assert db.session.query(models.Stock).count() == 0

        assert not mocked_send_first_venue_approved_offer_email_to_pro.called


@pytest.mark.usefixtures("db_session")
class EditStockTest:
    def test_edit_stock(self):
        # Given
        existing_stock = factories.StockFactory(price=10)

        # When
        edited_stock, update_info = api.edit_stock(stock=existing_stock, price=5, quantity=7)

        # Then
        assert edited_stock == db.session.query(models.Stock).filter_by(id=existing_stock.id).first()
        assert edited_stock.price == 5
        assert edited_stock.quantity == 7
        assert update_info is False

    @pytest.mark.parametrize(
        "init_value,edit_value",
        [
            ("I have a secret", "I'm Batman !!!"),
            ("i_dont_want_to_change", "i_dont_want_to_change"),
            ("i_am_going_to_be_erased", None),
            (None, "i_have_an_id_now"),
        ],
    )
    def test_edit_stock_id_at_provider(self, init_value, edit_value):
        # Given
        existing_stock = factories.StockFactory(price=10, idAtProviders=init_value)

        # When
        edited_stock, _ = api.edit_stock(stock=existing_stock, id_at_provider=edit_value, quantity=2)

        # Then
        assert edited_stock == db.session.query(models.Stock).filter_by(id=existing_stock.id).first()
        assert edited_stock.idAtProviders == edit_value

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
        assert edited_stock == db.session.query(models.Stock).filter_by(id=existing_stock.id).first()
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
        assert edited_stock == db.session.query(models.Stock).filter_by(id=existing_stock.id).first()
        assert edited_stock.price == 10
        assert edited_stock.quantity == 7
        assert edited_stock.beginningDatetime == beginning
        assert edited_stock.bookingLimitDatetime == new_booking_limit
        assert update_info is False

    def test_update_fields_updated_on_allocine_stocks(self):
        allocine_provider = providers_factories.AllocineProviderFactory()
        stock = factories.StockFactory(
            fieldsUpdated=["price"],  # suppose we already customized the price
            quantity=5,
            offer__idAtProvider="dummy",
            offer__lastProviderId=allocine_provider.id,
        )

        edited_stock, _ = api.edit_stock(stock=stock, price=stock.price, quantity=50)

        assert edited_stock == db.session.query(models.Stock).filter_by(id=stock.id).first()
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

    @pytest.mark.parametrize("new_price", [49, 151])
    def test_does_not_allow_price_outside_of_price_limitation(self, new_price, caplog):
        # Given
        factories.OfferPriceLimitationRuleFactory(
            subcategoryId=subcategories.ACHAT_INSTRUMENT.id, rate=decimal.Decimal("0.5")
        )
        existing_stock = factories.ThingStockFactory(
            price=110,
            offer__subcategoryId=subcategories.ACHAT_INSTRUMENT.id,
            offer__lastValidationPrice=decimal.Decimal("100"),
        )

        # When
        with pytest.raises(api_errors.ApiErrors) as error:
            with caplog.at_level(logging.INFO):
                api.edit_stock(stock=existing_stock, price=new_price, quantity=existing_stock.quantity)

        # Then
        assert error.value.errors == {
            "priceLimitationRule": ["Le prix indiqué est invalide, veuillez créer une nouvelle offre"]
        }

        assert len(caplog.records) == 1
        assert caplog.records[0].message == "Stock update blocked because of price limitation"
        assert caplog.records[0].technical_message_id == "stock.price.forbidden"
        assert caplog.records[0].extra == {
            "offer_id": existing_stock.offerId,
            "reference_price": 100,
            "old_price": 110,
            "stock_price": new_price,
        }

    @pytest.mark.parametrize("new_price", [49, 151])
    def test_does_not_allow_price_while_no_last_validation_price(self, new_price, caplog):
        # Given
        factories.OfferPriceLimitationRuleFactory(
            subcategoryId=subcategories.ACHAT_INSTRUMENT.id, rate=decimal.Decimal("0.5")
        )
        offer = factories.ThingOfferFactory(subcategoryId=subcategories.ACHAT_INSTRUMENT.id, lastValidationPrice=None)
        existing_stock = factories.ThingStockFactory(price=100, offer=offer)
        factories.ThingStockFactory(price=1, offer=offer)

        # When
        with pytest.raises(api_errors.ApiErrors) as error:
            with caplog.at_level(logging.INFO):
                api.edit_stock(stock=existing_stock, price=new_price, quantity=existing_stock.quantity)

        # Then
        assert error.value.errors == {
            "priceLimitationRule": ["Le prix indiqué est invalide, veuillez créer une nouvelle offre"]
        }

        assert len(caplog.records) == 1
        assert caplog.records[0].message == "Stock update blocked because of price limitation"
        assert caplog.records[0].technical_message_id == "stock.price.forbidden"
        assert caplog.records[0].extra == {
            "offer_id": offer.id,
            "reference_price": 100,
            "old_price": 100,
            "stock_price": new_price,
        }

    @pytest.mark.parametrize("new_price", [49, 151])
    def test_allow_price_edition_while_unrelated_price_limitation_rule(self, new_price):
        # Given
        factories.OfferPriceLimitationRuleFactory(
            subcategoryId=subcategories.ABO_BIBLIOTHEQUE.id, rate=decimal.Decimal("0.5")
        )
        existing_stock = factories.ThingStockFactory(
            price=110,
            offer__subcategoryId=subcategories.ACHAT_INSTRUMENT.id,
            offer__lastValidationPrice=decimal.Decimal("100"),
        )

        # When
        api.edit_stock(stock=existing_stock, price=new_price, quantity=existing_stock.quantity)

        # Then
        edited_stock = db.session.query(models.Stock).filter_by(id=existing_stock.id).first()
        assert edited_stock.price == decimal.Decimal(str(new_price))

    @pytest.mark.parametrize("new_price", [49, 151])
    def test_allow_price_edition_if_offer_has_ean(self, new_price):
        # Given
        factories.OfferPriceLimitationRuleFactory(
            subcategoryId=subcategories.LIVRE_PAPIER.id, rate=decimal.Decimal("0.5")
        )
        existing_stock = factories.ThingStockFactory(
            price=110,
            offer__subcategoryId=subcategories.LIVRE_PAPIER.id,
            offer__lastValidationPrice=decimal.Decimal("100"),
            offer__ean="1234567890123",
        )

        # When
        api.edit_stock(stock=existing_stock, price=new_price, quantity=existing_stock.quantity)

        # Then
        edited_stock = db.session.query(models.Stock).filter_by(id=existing_stock.id).first()
        assert edited_stock.price == decimal.Decimal(str(new_price))

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
        edited_stock = db.session.query(models.Stock).filter_by(id=existing_stock.id).first()
        assert edited_stock.price == 4
        assert edited_stock.quantity is None

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
    def test_edit_stock_of_rejected_offer_fails(
        self,
        mocked_send_first_venue_approved_offer_email_to_pro,
    ):
        offer = factories.ThingOfferFactory(validation=models.OfferValidationStatus.REJECTED)
        existing_stock = factories.StockFactory(offer=offer, price=10)

        with pytest.raises(exceptions.OfferException) as error:
            api.edit_stock(stock=existing_stock, price=5, quantity=7)

        assert error.value.errors == {"global": ["Les offres refusées ne sont pas modifiables"]}
        existing_stock = db.session.query(models.Stock).one()
        assert existing_stock.price == 10

        assert not mocked_send_first_venue_approved_offer_email_to_pro.called

    @time_machine.travel("2023-10-20 17:00:00", tick=False)
    def test_editing_beginning_datetime_edits_finance_event(self):
        # Given
        new_beginning_datetime = datetime.utcnow() + timedelta(days=4)

        pricing_point = offerers_factories.VenueFactory()
        oldest_event = _generate_finance_event_context(
            pricing_point, stock_date=datetime.utcnow() + timedelta(days=2), used_date=datetime.utcnow()
        )
        older_event = _generate_finance_event_context(
            pricing_point, stock_date=datetime.utcnow() + timedelta(days=6), used_date=datetime.utcnow()
        )
        changing_event = _generate_finance_event_context(
            pricing_point, datetime.utcnow() + timedelta(days=8), used_date=datetime.utcnow()
        )
        newest_event = _generate_finance_event_context(
            pricing_point, stock_date=datetime.utcnow() + timedelta(days=10), used_date=datetime.utcnow()
        )

        unrelated_event = _generate_finance_event_context(
            offerers_factories.VenueFactory(),
            stock_date=datetime.utcnow() + timedelta(days=8),
            used_date=datetime.utcnow(),
        )

        # When
        api.edit_stock(
            stock=changing_event.booking.stock,
            beginning_datetime=new_beginning_datetime,
        )

        # Then
        assert oldest_event.pricingOrderingDate == datetime.utcnow() + timedelta(days=2)
        assert oldest_event.status == finance_models.FinanceEventStatus.PRICED
        assert len(oldest_event.pricings) == 1

        assert older_event.pricingOrderingDate == datetime.utcnow() + timedelta(days=6)
        assert older_event.status == finance_models.FinanceEventStatus.READY
        assert len(older_event.pricings) == 0

        assert changing_event.pricingOrderingDate == datetime.utcnow() + timedelta(days=4)
        assert changing_event.status == finance_models.FinanceEventStatus.READY
        assert len(changing_event.pricings) == 1
        assert changing_event.pricings[0].status == finance_models.PricingStatus.CANCELLED

        assert newest_event.pricingOrderingDate == datetime.utcnow() + timedelta(days=10)
        assert newest_event.status == finance_models.FinanceEventStatus.READY
        assert len(newest_event.pricings) == 0

        assert unrelated_event.pricingOrderingDate == datetime.utcnow() + timedelta(days=8)
        assert unrelated_event.status == finance_models.FinanceEventStatus.PRICED
        assert len(unrelated_event.pricings) == 1

    def test_edited_price_is_tracked(self, caplog):
        # Given
        existing_stock = factories.StockFactory(price=10)

        # When
        with caplog.at_level(logging.INFO):
            api.edit_stock(stock=existing_stock, price=12.5)
        db.session.flush()  # otherwise "Failed to add object to the flush context!" in teardown

        # Then
        assert len(caplog.records) == 2
        last_record = caplog.records[-1]  # First record is Request to asynchronously reindex

        assert last_record.message == "Successfully updated stock"
        assert last_record.technical_message_id == "stock.updated"
        assert last_record.extra == {
            "offer_id": existing_stock.offerId,
            "stock_id": existing_stock.id,
            "provider_id": None,
            "stock_dnBookedQuantity": 0,
            "changes": {
                "price": {"old_value": Decimal("10.00"), "new_value": 12.5},
            },
        }

    def test_unchanged_price_is_not_tracked(self, caplog):
        # Given
        existing_stock = factories.StockFactory(price=10, quantity=15)

        # When
        with caplog.at_level(logging.INFO):
            api.edit_stock(stock=existing_stock, quantity=7)
        db.session.flush()  # otherwise "Failed to add object to the flush context!" in teardown

        # Then
        assert len(caplog.records) == 2
        last_record = caplog.records[-1]  # First record is Request to asynchronously reindex

        assert last_record.message == "Successfully updated stock"
        assert last_record.technical_message_id == "stock.updated"
        assert last_record.extra == {
            "offer_id": existing_stock.offerId,
            "stock_id": existing_stock.id,
            "provider_id": None,
            "stock_dnBookedQuantity": 0,
            "changes": {
                "quantity": {"old_value": 15, "new_value": 7},
            },
        }


def _generate_finance_event_context(
    pricing_point: offerers_models.Venue, stock_date: datetime, used_date: datetime
) -> finance_models.FinanceEvent:
    venue = offerers_factories.VenueFactory(pricing_point=pricing_point)
    stock = factories.EventStockFactory(
        offer__venue=venue,
        beginningDatetime=stock_date,
        bookingLimitDatetime=used_date - timedelta(days=1),
    )
    booking = bookings_factories.UsedBookingFactory(stock=stock, dateUsed=used_date)
    event = finance_factories.FinanceEventFactory(
        booking=booking,
        pricingOrderingDate=stock.beginningDatetime,
        status=finance_models.FinanceEventStatus.PRICED,
        venue=venue,
    )
    finance_factories.PricingFactory(event=event, booking=event.booking)
    return event


@pytest.mark.usefixtures("db_session")
class DeleteStockTest:
    @mock.patch("pcapi.core.search.async_index_offer_ids")
    def test_delete_stock_basics(self, mocked_async_index_offer_ids, caplog):
        stock = factories.EventStockFactory()

        with caplog.at_level(logging.INFO):
            api.delete_stock(stock)

        stock = db.session.query(models.Stock).one()
        assert stock.isSoftDeleted
        mocked_async_index_offer_ids.assert_called_once_with(
            [stock.offerId],
            reason=search.IndexationReason.STOCK_DELETION,
        )

        # Test tracking
        last_record = caplog.records[-1]
        assert last_record.technical_message_id == "stock.deleted"
        assert last_record.message == "Deleted stock and cancelled its bookings"
        assert last_record.extra == {
            "stock": stock.id,
            "bookings": [],
            "author_id": None,
            "user_connect_as": False,
        }

    def test_delete_stock_cancel_bookings_and_send_emails(self):
        offerer_email = "offerer@example.com"
        stock = factories.EventStockFactory(
            offer__bookingEmail=offerer_email,
            offer__venue__pricing_point="self",
        )
        booking1 = bookings_factories.BookingFactory(stock=stock)
        booking2 = bookings_factories.CancelledBookingFactory(stock=stock)
        booking3 = bookings_factories.UsedBookingFactory(stock=stock)
        event4 = finance_factories.UsedBookingFinanceEventFactory(booking__stock=stock)
        booking4 = event4.booking
        finance_factories.PricingFactory(
            event=event4,
            booking=booking4,
            status=finance_models.PricingStatus.PROCESSED,
        )
        booking_id_1 = booking1.id
        booking_id_2 = booking2.id
        booking_id_3 = booking3.id
        booking_id_4 = booking4.id

        with atomic():
            api.delete_stock(stock)

        # cancellation can trigger more than one request to Batch
        assert len(push_testing.requests) >= 1
        db.session.expunge_all()
        assert db.session.query(models.Stock.isSoftDeleted).scalar()
        booking1 = db.session.get(bookings_models.Booking, booking_id_1)
        assert booking1.status == bookings_models.BookingStatus.CANCELLED
        assert booking1.cancellationReason == bookings_models.BookingCancellationReasons.OFFERER
        booking2 = db.session.get(bookings_models.Booking, booking_id_2)
        assert booking2.status == bookings_models.BookingStatus.CANCELLED  # unchanged
        assert booking2.cancellationReason == bookings_models.BookingCancellationReasons.BENEFICIARY
        booking3 = db.session.get(bookings_models.Booking, booking_id_3)
        assert booking3.status == bookings_models.BookingStatus.CANCELLED  # cancel used booking for event offer
        assert booking3.cancellationReason == bookings_models.BookingCancellationReasons.OFFERER
        booking4 = db.session.get(bookings_models.Booking, booking_id_4)
        assert booking4.status == bookings_models.BookingStatus.USED  # unchanged
        assert booking4.cancellationDate is None
        assert booking4.pricings[0].status == finance_models.PricingStatus.PROCESSED  # unchanged

        assert len(mails_testing.outbox) == 3
        assert {email_data["To"] for email_data in mails_testing.outbox} == {
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

    @pytest.mark.features(WIP_DISABLE_CANCEL_BOOKING_NOTIFICATION=True)
    def test_delete_stock_cancel_bookings_and_send_emails_with_FF(self):
        offerer_email = "offerer@example.com"
        stock = factories.EventStockFactory(
            offer__bookingEmail=offerer_email,
            offer__venue__pricing_point="self",
        )
        booking1 = bookings_factories.BookingFactory(stock=stock)
        booking2 = bookings_factories.CancelledBookingFactory(stock=stock)
        booking3 = bookings_factories.UsedBookingFactory(stock=stock)
        event4 = finance_factories.UsedBookingFinanceEventFactory(booking__stock=stock)
        booking4 = event4.booking
        finance_factories.PricingFactory(
            event=event4,
            booking=booking4,
            status=finance_models.PricingStatus.PROCESSED,
        )

        booking_id_1 = booking1.id
        booking_id_2 = booking2.id
        booking_id_3 = booking3.id
        booking_id_4 = booking4.id

        api.delete_stock(stock)

        # cancellation can trigger more than one request to Batch
        assert len(push_testing.requests) >= 1
        db.session.expunge_all()
        stock = db.session.query(models.Stock).one()
        assert stock.isSoftDeleted
        booking1 = db.session.get(bookings_models.Booking, booking_id_1)
        assert booking1.status == bookings_models.BookingStatus.CANCELLED
        assert booking1.cancellationReason == bookings_models.BookingCancellationReasons.OFFERER
        booking2 = db.session.get(bookings_models.Booking, booking_id_2)
        assert booking2.status == bookings_models.BookingStatus.CANCELLED  # unchanged
        assert booking2.cancellationReason == bookings_models.BookingCancellationReasons.BENEFICIARY
        booking3 = db.session.get(bookings_models.Booking, booking_id_3)
        assert booking3.status == bookings_models.BookingStatus.CANCELLED  # cancel used booking for event offer
        assert booking3.cancellationReason == bookings_models.BookingCancellationReasons.OFFERER
        booking4 = db.session.get(bookings_models.Booking, booking_id_4)
        assert booking4.status == bookings_models.BookingStatus.USED  # unchanged
        assert booking4.cancellationDate is None
        assert booking4.pricings[0].status == finance_models.PricingStatus.PROCESSED  # unchanged

        assert len(mails_testing.outbox) == 3
        assert {email_data["To"] for email_data in mails_testing.outbox} == {
            booking1.email,
            booking3.email,
            offerer_email,
        }

        cancel_notification_requests = [req for req in push_testing.requests if req.get("group_id") == "Cancel_booking"]
        assert len(cancel_notification_requests) == 0

    def test_can_delete_if_stock_from_provider(self):
        provider = providers_factories.PublicApiProviderFactory()
        offer = factories.OfferFactory(lastProvider=provider, idAtProvider="1")
        stock = factories.StockFactory(offer=offer)

        api.delete_stock(stock)

        stock = db.session.query(models.Stock).one()
        assert stock.isSoftDeleted

    def test_can_delete_if_event_ended_recently(self):
        recently = datetime.utcnow() - timedelta(days=1)
        stock = factories.EventStockFactory(beginningDatetime=recently)

        api.delete_stock(stock)
        stock = db.session.query(models.Stock).one()
        assert stock.isSoftDeleted

    def test_cannot_delete_if_too_late(self):
        too_long_ago = datetime.utcnow() - timedelta(days=3)
        stock = factories.EventStockFactory(beginningDatetime=too_long_ago)

        with pytest.raises(exceptions.OfferException):
            api.delete_stock(stock)
        stock = db.session.query(models.Stock).one()
        assert not stock.isSoftDeleted


class CreateMediationV2Test:
    BASE_THUMBS_DIR = pathlib.Path(tests.__path__[0]) / ".." / "src" / "pcapi" / "static" / "object_store_data"
    THUMBS_DIR = BASE_THUMBS_DIR / "thumbs" / "mediations"

    @mock.patch("pcapi.core.search.async_index_offer_ids")
    @pytest.mark.settings(LOCAL_STORAGE_DIR=BASE_THUMBS_DIR)
    @pytest.mark.usefixtures("db_session")
    def test_ok(self, mocked_async_index_offer_ids, clear_tests_assets_bucket):
        # Given
        user = users_factories.ProFactory()
        offer = factories.ThingOfferFactory()
        image_as_bytes = (IMAGES_DIR / "mouette_full_size.jpg").read_bytes()

        # When
        api.create_mediation(user, offer, "©Photographe", image_as_bytes)

        # Then
        models.mediation = db.session.query(models.Mediation).one()
        assert models.mediation.author == user
        assert models.mediation.offer == offer
        assert models.mediation.credit == "©Photographe"
        assert models.mediation.thumbCount == 1
        assert db.session.query(models.Mediation).filter(models.Mediation.offerId == offer.id).count() == 1
        mocked_async_index_offer_ids.assert_called_once_with(
            [offer.id],
            reason=search.IndexationReason.MEDIATION_CREATION,
        )

    @pytest.mark.settings(LOCAL_STORAGE_DIR=BASE_THUMBS_DIR)
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
        models.mediation_3 = db.session.query(models.Mediation).one()
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
    @pytest.mark.settings(LOCAL_STORAGE_DIR=BASE_THUMBS_DIR)
    @pytest.mark.usefixtures("clean_database")
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
        assert db.session.query(models.Mediation).count() == 0
        assert len(os.listdir(self.THUMBS_DIR)) == existing_number_of_files


@pytest.mark.usefixtures("db_session")
class CreateDraftOfferTest:
    def test_create_draft_offer_from_scratch(self):
        venue = offerers_factories.VenueFactory()
        body = offers_schemas.PostDraftOfferBodyModel(
            name="A pretty good offer",
            subcategoryId=subcategories.SEANCE_CINE.id,
            venueId=venue.id,
        )
        offer = api.create_draft_offer(body, venue=venue)

        assert offer.name == "A pretty good offer"
        assert offer.subcategoryId == subcategories.SEANCE_CINE.id
        assert offer.venue == venue
        assert not offer.description
        assert not offer.isActive
        assert offer.validation == models.OfferValidationStatus.DRAFT
        assert not offer.product
        assert db.session.query(models.Offer).count() == 1
        assert offer.metaData is None

    def test_cannot_create_draft_offer_with_ean_in_name(self):
        venue = offerers_factories.VenueFactory()
        body = offers_schemas.PostDraftOfferBodyModel(
            name="A pretty good offer 4759217254634",
            subcategoryId=subcategories.SEANCE_CINE.id,
            venueId=venue.id,
        )
        with pytest.raises(exceptions.OfferException):
            api.create_draft_offer(body, venue=venue)

    def test_create_draft_offer_with_accessibility_provider(self):
        # when venue is synchronized with acceslibre, create draft offer should
        # have acceslibre accessibility informations
        venue = offerers_factories.VenueFactory(
            audioDisabilityCompliant=False,
            mentalDisabilityCompliant=True,
            motorDisabilityCompliant=False,
            visualDisabilityCompliant=True,
        )
        offerers_factories.AccessibilityProviderFactory(
            externalAccessibilityData={
                "access_modality": [acceslibre_enum.EXTERIOR_ACCESS_ELEVATOR],  # motorDisabilityCompliant is True
                "audio_description": [],  # visualDisabilityCompliant is False
                "deaf_and_hard_of_hearing_amenities": [
                    acceslibre_enum.DEAF_AND_HARD_OF_HEARING_PORTABLE_INDUCTION_LOOP,  # audioDisabilityCompliant is True
                ],
                "facilities": [],
                "sound_beacon": [],
                "trained_personnel": [acceslibre_enum.PERSONNEL_UNTRAINED],  # mentalDisabilityCompliant is False
                "transport_modality": [],
            },
            venue=venue,
        )

        body = offers_schemas.PostDraftOfferBodyModel(
            name="A pretty good offer",
            subcategoryId=subcategories.SEANCE_CINE.id,
            venueId=venue.id,
        )
        offer = api.create_draft_offer(body, venue=venue)
        assert offer.audioDisabilityCompliant == True
        assert offer.mentalDisabilityCompliant == False
        assert offer.motorDisabilityCompliant == True
        assert offer.visualDisabilityCompliant == False

    def test_create_draft_offer_with_withrawal_details_from_venue(self):
        venue = offerers_factories.VenueFactory(withdrawalDetails="Details from my venue")

        body = offers_schemas.PostDraftOfferBodyModel(
            name="A pretty good offer",
            subcategoryId=subcategories.SEANCE_CINE.id,
            venueId=venue.id,
        )
        offer = api.create_draft_offer(body, venue=venue)

        assert offer.withdrawalDetails == venue.withdrawalDetails

    def test_cannot_create_activation_offer(self):
        venue = offerers_factories.VenueFactory()
        body = offers_schemas.PostDraftOfferBodyModel(
            name="An offer he can't refuse",
            subcategoryId=subcategories.ACTIVATION_EVENT.id,
            venueId=venue.id,
        )
        with pytest.raises(exceptions.OfferException) as error:
            api.create_draft_offer(body, venue=venue)

        msg = "Une offre ne peut être créée ou éditée en utilisant cette sous-catégorie"
        assert error.value.errors["subcategory"] == [msg]

    def test_cannot_create_offer_when_invalid_subcategory(self):
        venue = offerers_factories.VenueFactory()
        body = offers_schemas.PostDraftOfferBodyModel(
            name="An offer he can't refuse",
            subcategoryId="TOTO",
            venueId=venue.id,
        )
        with pytest.raises(exceptions.OfferException) as error:
            api.create_draft_offer(body, venue=venue)

        assert error.value.errors["subcategory"] == ["La sous-catégorie de cette offre est inconnue"]

    def test_create_draft_offer_with_video_url(self):
        venue = offerers_factories.VenueFactory()
        body = offers_schemas.PostDraftOfferBodyModel(
            name="A pretty good offer",
            subcategoryId=subcategories.SEANCE_CINE.id,
            venueId=venue.id,
            videoUrl="https://www.youtube.com/watch?v=uIR_vSRASxM",
        )
        offer = api.create_draft_offer(body, venue=venue)

        assert offer.metaData.videoUrl == "https://www.youtube.com/watch?v=uIR_vSRASxM"


@pytest.mark.usefixtures("db_session")
class GetVideoMetadataFromCacheTest:
    def test_get_video_metadata_from_cache_no_video_id(self):
        video_metadata = api.get_video_metadata_from_cache(None)
        assert video_metadata is None

    @mock.patch("pcapi.connectors.youtube.requests.get")
    def test_get_video_metadata_from_cache_with_data_in_cache(self, mock_requests_get, app):
        mock_requests_get.raiseError.side_effect = AssertionError(
            "Call to external service should not have been performed"
        )
        video_url = "https://www.youtube.com/watch?v=WtM4OW2qVjY"
        video_id = offers_schemas.extract_youtube_video_id(video_url)
        app.redis_client.set(
            f"{api.YOUTUBE_INFO_CACHE_PREFIX}{video_id}",
            json.dumps(
                {
                    "title": "Title",
                    "thumbnail_url": "thumbnail url",
                    "duration": 100,
                }
            ),
        )
        video_metadata = api.get_video_metadata_from_cache(video_url)
        assert video_metadata.id == video_id
        assert video_metadata.title == "Title"
        assert video_metadata.thumbnail_url == "thumbnail url"
        assert video_metadata.duration == 100

    @mock.patch("pcapi.connectors.youtube.requests.get")
    def test_get_video_metadata_from_cache_without_data_in_cache(self, mock_requests_get):
        mock_response = mock.Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "items": [
                {
                    "id": "test_video_id",
                    "snippet": {
                        "title": "Test Video",
                        "thumbnails": {
                            "high": {"url": "https://example.com/high.jpg"},
                        },
                    },
                    "contentDetails": {"duration": "PT1M40S"},
                }
            ]
        }
        mock_requests_get.return_value = mock_response
        video_url = "https://www.youtube.com/watch?v=WtM4OW2qVjY"

        video_metadata = api.get_video_metadata_from_cache(video_url)
        assert video_metadata.id == "test_video_id"
        assert video_metadata.title == "Test Video"
        assert video_metadata.thumbnail_url == "https://example.com/high.jpg"
        assert video_metadata.duration == 100

    @mock.patch("pcapi.connectors.youtube.requests.get")
    def test_get_video_metadata_from_cache_without_data_in_cache_connector_raise_error(self, mock_requests_get):
        mock_requests_get.raiseError.side_effect = ValidationError("bad data", YoutubeApiResponse)
        video_url = "https://www.youtube.com/watch?v=WtM4OW2qVjY"

        with pytest.raises(ExternalAPIException):
            api.get_video_metadata_from_cache(video_url)


@pytest.mark.usefixtures("db_session")
class UpdateDraftOfferTest:
    def test_basics(self):
        offer = factories.OfferFactory(
            name="Name",
            subcategoryId=subcategories.ESCAPE_GAME.id,
            description="description",
        )
        body = offers_schemas.PatchDraftOfferBodyModel(
            name="New name",
            description="New description",
        )
        offer = api.update_draft_offer(offer, body)
        db.session.flush()

        assert offer.name == "New name"
        assert offer.description == "New description"

    @mock.patch("pcapi.core.offers.api.get_video_metadata_from_cache")
    def test_new_video_url(self, get_video_metadata_from_cache_mock):
        video_url = "https://www.youtube.com/watch?v=WtM4OW2qVjY"
        video_id = offers_schemas.extract_youtube_video_id(video_url)
        get_video_metadata_from_cache_mock.return_value = youtube.YoutubeVideoMetadata(
            id=video_id,
            title="Title",
            thumbnail_url="thumbnail url",
            duration=100,
        )
        offer = factories.OfferFactory(
            name="Name",
            subcategoryId=subcategories.ESCAPE_GAME.id,
            description="description",
        )
        body = offers_schemas.PatchDraftOfferBodyModel(videoUrl=video_url)
        offer = api.update_draft_offer(offer, body)
        db.session.flush()

        assert offer.metaData.videoExternalId == video_id
        assert offer.metaData.videoTitle == "Title"
        assert offer.metaData.videoThumbnailUrl == "thumbnail url"
        assert offer.metaData.videoDuration == 100
        assert offer.metaData.videoUrl == video_url

    def test_can_delete_video_url(self):
        meta_data = factories.OfferMetaDataFactory(videoUrl="https://www.youtube.com/watch?v=WtM4OW2qVjY")

        offer = factories.OfferFactory(metaData=meta_data)
        body = offers_schemas.PatchDraftOfferBodyModel(videoUrl="")
        offer = api.update_draft_offer(offer, body)
        db.session.flush()
        db.session.refresh(offer)

        assert offer.metaData.videoUrl is None

    def test_cannot_update_if_ean_in_name(self):
        offer = factories.OfferFactory(
            name="Name",
            subcategoryId=subcategories.ESCAPE_GAME.id,
            description="description",
        )
        body = offers_schemas.PatchDraftOfferBodyModel(
            name="New name 4759217254634",
            description="New description",
        )

        with pytest.raises(exceptions.OfferException):
            api.update_draft_offer(offer, body)

        db.session.flush()

        assert offer.name == "Name"
        assert offer.description == "description"


@pytest.mark.usefixtures("db_session")
class CreateOfferTest:
    def test_create_digital_offer_from_scratch(
        self,
    ):
        venue = offerers_factories.VenueFactory(isVirtual=True, offererAddress=None, siret=None)
        offerer_address = offerers_factories.OffererAddressFactory(offerer=venue.managingOfferer)

        body = offers_schemas.CreateOffer(
            name="A pretty good offer",
            externalTicketOfficeUrl="http://example.net",
            audioDisabilityCompliant=True,
            mentalDisabilityCompliant=True,
            motorDisabilityCompliant=True,
            visualDisabilityCompliant=True,
            url="http://example.com",
            subcategoryId=subcategories.VOD.id,
        )

        offer = api.create_offer(body=body, venue=venue, offerer_address=offerer_address)

        assert offer.offererAddressId == None

    def test_create_offer_from_scratch(self, caplog):
        venue = offerers_factories.VenueFactory()
        offerer_address = offerers_factories.OffererAddressFactory(offerer=venue.managingOfferer)

        body = offers_schemas.CreateOffer(
            name="A pretty good offer",
            subcategoryId=subcategories.SEANCE_CINE.id,
            externalTicketOfficeUrl="http://example.net",
            audioDisabilityCompliant=True,
            mentalDisabilityCompliant=True,
            motorDisabilityCompliant=True,
            visualDisabilityCompliant=True,
        )
        with caplog.at_level(logging.INFO):
            offer = api.create_offer(body, venue=venue, offerer_address=offerer_address)

        assert offer.name == "A pretty good offer"
        assert offer.venue == venue
        assert offer.subcategoryId == subcategories.SEANCE_CINE.id
        assert not offer.product
        assert offer.externalTicketOfficeUrl == "http://example.net"
        assert offer.audioDisabilityCompliant
        assert offer.mentalDisabilityCompliant
        assert offer.motorDisabilityCompliant
        assert offer.visualDisabilityCompliant
        assert offer.validation == models.OfferValidationStatus.DRAFT
        assert offer.extraData == {}
        assert offer.metaData is None
        assert not offer.bookingEmail
        assert db.session.query(models.Offer).count() == 1
        assert offer.offererAddress == offerer_address
        assert offer.offererAddress != venue.offererAddress

        # Test tracking
        offer_update_record = caplog.records[0]
        mail_third_party_record = caplog.records[1]
        assert offer_update_record.technical_message_id == "offer.created"
        assert offer_update_record.message == "Offer has been created"

        assert mail_third_party_record.message == "update_sib_pro_attributes_task"

    def test_create_offer_with_id_at_provider(self):
        venue = offerers_factories.VenueFactory()
        provider = providers_factories.PublicApiProviderFactory()

        body = offers_schemas.CreateOffer(
            name="A pretty good offer",
            subcategoryId=subcategories.SEANCE_CINE.id,
            audioDisabilityCompliant=True,
            mentalDisabilityCompliant=True,
            motorDisabilityCompliant=True,
            visualDisabilityCompliant=True,
            idAtProvider="coucou",
        )
        offer = api.create_offer(body, venue=venue, provider=provider)

        assert offer.name == "A pretty good offer"
        assert offer.venue == venue
        assert offer.subcategoryId == subcategories.SEANCE_CINE.id
        assert offer.validation == models.OfferValidationStatus.DRAFT
        assert offer.extraData == {}
        assert offer.idAtProvider == "coucou"
        assert db.session.query(models.Offer).count() == 1

    def test_cannot_create_activation_offer(self):
        venue = offerers_factories.VenueFactory()
        body = offers_schemas.CreateOffer(
            name="An offer he can't refuse",
            subcategoryId=subcategories.ACTIVATION_EVENT.id,
            audioDisabilityCompliant=True,
            mentalDisabilityCompliant=True,
            motorDisabilityCompliant=True,
            visualDisabilityCompliant=True,
        )
        with pytest.raises(exceptions.OfferException) as error:
            api.create_offer(body, venue=venue)

        assert error.value.errors["subcategory"] == [
            "Une offre ne peut être créée ou éditée en utilisant cette sous-catégorie"
        ]

    def test_cannot_create_offer_when_invalid_subcategory(self):
        venue = offerers_factories.VenueFactory()
        body = offers_schemas.CreateOffer(
            name="An offer he can't refuse",
            subcategoryId="TOTO",
            audioDisabilityCompliant=True,
            mentalDisabilityCompliant=True,
            motorDisabilityCompliant=True,
            visualDisabilityCompliant=True,
        )
        with pytest.raises(exceptions.OfferException) as error:
            api.create_offer(body, venue=venue)

        assert error.value.errors["subcategory"] == ["La sous-catégorie de cette offre est inconnue"]

    def test_cannot_create_offer_with_ean_in_name(self):
        venue = offerers_factories.VenueFactory()
        body = offers_schemas.CreateOffer(
            name="An offer he can't refuse - 4759217254634",
            subcategoryId=subcategories.SEANCE_CINE.id,
            audioDisabilityCompliant=True,
            mentalDisabilityCompliant=True,
            motorDisabilityCompliant=True,
            visualDisabilityCompliant=True,
        )
        with pytest.raises(exceptions.OfferException) as error:
            api.create_offer(body, venue=venue)

        assert error.value.errors["name"] == ["Le titre d'une offre ne peut contenir l'EAN"]

    @pytest.mark.parametrize(
        "url, subcategory_id, expected_error",
        [
            (
                "https://coucou.com",
                subcategories.SEANCE_CINE.id,
                ['Une offre de sous-catégorie "Séance de cinéma" ne peut contenir un champ `url`'],
            ),
            (
                None,
                subcategories.ABO_LIVRE_NUMERIQUE.id,
                ['Une offre de catégorie "Abonnement livres numériques" doit contenir un champ `url`'],
            ),
        ],
    )
    def test_raise_error_if_url_not_coherent_with_subcategory(self, url, subcategory_id, expected_error):
        venue = offerers_factories.VenueFactory()
        body = offers_schemas.CreateOffer(
            name="An offer he can't refuse",
            subcategoryId=subcategory_id,
            url=url,
            audioDisabilityCompliant=True,
            mentalDisabilityCompliant=True,
            motorDisabilityCompliant=True,
            visualDisabilityCompliant=True,
        )
        with pytest.raises(api_errors.ApiErrors) as error:
            api.create_offer(body, venue=venue)

        assert error.value.errors["url"] == expected_error

    def test_raise_error_if_extra_data_mandatory_fields_not_provided(self):
        venue = offerers_factories.VenueFactory()
        body = offers_schemas.CreateOffer(
            name="A pretty good offer",
            subcategoryId=subcategories.CONCERT.id,
            audioDisabilityCompliant=True,
            mentalDisabilityCompliant=True,
            motorDisabilityCompliant=True,
            visualDisabilityCompliant=True,
            bookingContact="booking@conta.ct",
            withdrawalType=models.WithdrawalTypeEnum.NO_TICKET,
        )
        with pytest.raises(api_errors.ApiErrors) as error:
            api.create_offer(body, venue=venue)

        assert error.value.errors["musicType"] == ["Ce champ est obligatoire"]

    def test_raise_error_on_creating_because_this_id_at_provider_is_already_taken(self):
        provider = providers_factories.PublicApiProviderFactory()
        offerer = offerers_factories.OffererFactory()
        providers_factories.OffererProviderFactory(offerer=offerer, provider=provider)
        venue = offerers_factories.VenueFactory()
        id_at_provider = "rolalala"

        # existing offer with `id_at_provider`
        factories.OfferFactory(
            lastProvider=provider,
            name="Offer linked to a provider",
            venue=venue,
            idAtProvider=id_at_provider,
        )
        body = offers_schemas.CreateOffer(
            name="A pretty good offer",
            subcategoryId=subcategories.SEANCE_CINE.id,
            externalTicketOfficeUrl="http://example.net",
            audioDisabilityCompliant=True,
            mentalDisabilityCompliant=True,
            motorDisabilityCompliant=True,
            visualDisabilityCompliant=True,
            idAtProvider=id_at_provider,
        )
        with pytest.raises(exceptions.OfferException) as error:
            api.create_offer(
                body,
                venue=venue,
                provider=provider,
            )

        assert error.value.errors["idAtProvider"] == ["`rolalala` is already taken by another venue offer"]


@pytest.mark.usefixtures("db_session")
class UpdateOfferTest:
    @mock.patch("pcapi.core.search.async_index_offer_ids")
    def test_basics(self, mocked_async_index_offer_ids, caplog):
        offer = factories.OfferFactory(
            isDuo=False, bookingEmail="old@example.com", subcategoryId=subcategories.ESCAPE_GAME.id
        )

        body = offers_schemas.UpdateOffer(isDuo=True, bookingEmail="new@example.com")
        with caplog.at_level(logging.DEBUG):
            offer = api.update_offer(offer, body)
        db.session.flush()

        assert offer.isDuo
        assert offer.bookingEmail == "new@example.com"
        mocked_async_index_offer_ids.assert_called_once_with(
            [offer.id],
            reason=search.IndexationReason.OFFER_UPDATE,
            log_extra={"changes": {"bookingEmail", "isDuo"}},
        )

        # Test tracking
        last_record = caplog.records[-1]
        assert last_record.technical_message_id == "offer.updated"
        assert last_record.message == "Offer has been updated"
        assert last_record.extra == {
            "offer_id": offer.id,
            "venue_id": offer.venueId,
            "product_id": offer.productId,
            "changes": {
                "bookingEmail": {"oldValue": "old@example.com", "newValue": "new@example.com"},
                "isDuo": {"oldValue": False, "newValue": True},
            },
        }

    def test_update_extra_data_should_raise_error_when_mandatory_field_not_provided(self):
        offer = factories.OfferFactory(subcategoryId=subcategories.SPECTACLE_REPRESENTATION.id)
        body = offers_schemas.UpdateOffer(extraData={"author": "Asimov"})
        with pytest.raises(api_errors.ApiErrors) as error:
            api.update_offer(offer, body)

        assert error.value.errors == {
            "showType": ["Ce champ est obligatoire"],
            "showSubType": ["Ce champ est obligatoire"],
        }

    def test_error_when_missing_mandatory_extra_data(self):
        offer = factories.OfferFactory(
            subcategoryId=subcategories.SPECTACLE_REPRESENTATION.id, extraData={"showType": 200}
        )
        body = offers_schemas.UpdateOffer(extraData=None)
        with pytest.raises(api_errors.ApiErrors) as error:
            api.update_offer(offer, body)
        assert error.value.errors == {
            "showType": ["Ce champ est obligatoire"],
            "showSubType": ["Ce champ est obligatoire"],
        }

    def test_update_offer_with_existing_ean(self):
        offer = factories.OfferFactory(
            name="Old name",
            ean="1234567890123",
            extraData={"gtl_id": "02000000"},
            subcategoryId=subcategories.SUPPORT_PHYSIQUE_MUSIQUE_CD.id,
        )
        body = offers_schemas.UpdateOffer(name="New name", description="new Description")
        offer = api.update_offer(offer, body)
        db.session.flush()

        assert offer.name == "New name"
        assert offer.description == "new Description"

    def test_cannot_update_with_name_too_long(self):
        offer = factories.OfferFactory(name="Old name", ean="1234567890124")
        body = offers_schemas.UpdateOffer(name="Luftballons" * 99)
        with pytest.raises(api_errors.ApiErrors) as error:
            api.update_offer(offer, body)

        assert error.value.errors == {"name": ["Vous devez saisir moins de 140 caractères"]}
        assert db.session.query(models.Offer).one().name == "Old name"

    def test_cannot_update_with_name_containing_ean(self):
        offer = factories.OfferFactory(name="Old name", ean="1234567890124")
        body = offers_schemas.UpdateOffer(name="Luftballons 1234567890124")
        with pytest.raises(exceptions.OfferException) as error:
            api.update_offer(offer, body)

        assert error.value.errors == {"name": ["Le titre d'une offre ne peut contenir l'EAN"]}
        assert db.session.query(models.Offer).one().name == "Old name"

    def test_success_on_allocine_offer(self):
        provider = providers_factories.AllocineProviderFactory(localClass="AllocineStocks")
        offer = factories.OfferFactory(
            lastProvider=provider, name="Old name", subcategoryId=subcategories.SEANCE_CINE.id
        )
        body = offers_schemas.UpdateOffer(name="Old name", isDuo=True)
        api.update_offer(offer, body)

        offer = db.session.query(models.Offer).one()
        assert offer.name == "Old name"
        assert offer.isDuo

    def test_forbidden_on_allocine_offer_on_certain_fields(self):
        provider = providers_factories.AllocineProviderFactory(localClass="AllocineStocks")
        offer = factories.OfferFactory(
            lastProvider=provider, durationMinutes=90, subcategoryId=subcategories.SEANCE_CINE.id
        )
        body = offers_schemas.UpdateOffer(durationMinutes=120, isDuo=True)
        with pytest.raises(api_errors.ApiErrors) as error:
            api.update_offer(offer, body)

        assert error.value.errors == {"durationMinutes": ["Vous ne pouvez pas modifier ce champ"]}
        offer = db.session.query(models.Offer).one()
        assert offer.durationMinutes == 90
        assert not offer.isDuo

    def test_success_on_imported_offer_on_external_ticket_office_url(self):
        provider = providers_factories.AllocineProviderFactory()
        offer = factories.OfferFactory(
            externalTicketOfficeUrl="http://example.org",
            lastProvider=provider,
            name="Old name",
            ean="1234567890124",
        )
        body = offers_schemas.UpdateOffer(externalTicketOfficeUrl="https://example.com")
        api.update_offer(offer, body)

        offer = db.session.query(models.Offer).one()
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
        body = offers_schemas.UpdateOffer(
            name="Old name",
            audioDisabilityCompliant=False,
            visualDisabilityCompliant=True,
            motorDisabilityCompliant=True,
            mentalDisabilityCompliant=False,
        )
        api.update_offer(offer, body)

        offer = db.session.query(models.Offer).one()
        assert offer.name == "Old name"
        assert offer.audioDisabilityCompliant is False
        assert offer.visualDisabilityCompliant is True
        assert offer.motorDisabilityCompliant is True
        assert offer.mentalDisabilityCompliant is False

    def test_success_on_imported_offer_with_product_not_music_related_with_gtl_id(self):
        provider = providers_factories.PublicApiProviderFactory(name="BookProvider")
        product = factories.ProductFactory(
            subcategoryId=subcategories.LIVRE_PAPIER.id,
            lastProvider=provider,
            ean="1234567890123",
            extraData={"gtl_id": "01020602", "author": "Asimov"},
        )
        offer = factories.OfferFactory(
            product=product,
            lastProvider=provider,
            audioDisabilityCompliant=True,
            visualDisabilityCompliant=False,
            motorDisabilityCompliant=False,
            mentalDisabilityCompliant=True,
        )
        body = offers_schemas.UpdateOffer(
            name="Old name",
            audioDisabilityCompliant=False,
            visualDisabilityCompliant=True,
            motorDisabilityCompliant=True,
            mentalDisabilityCompliant=False,
        )
        api.update_offer(offer, body)

        offer = db.session.query(models.Offer).one()
        assert offer.name == "Old name"
        assert offer.audioDisabilityCompliant is False
        assert offer.visualDisabilityCompliant is True
        assert offer.motorDisabilityCompliant is True
        assert offer.mentalDisabilityCompliant is False

    def test_forbidden_on_imported_offer_on_other_fields(self):
        provider = providers_factories.PublicApiProviderFactory()
        offer = factories.OfferFactory(
            lastProvider=provider,
            durationMinutes=90,
            isDuo=False,
            audioDisabilityCompliant=True,
            subcategoryId=subcategories.SEANCE_CINE.id,
        )
        body = offers_schemas.UpdateOffer(
            durationMinutes=120,
            isDuo=True,
            audioDisabilityCompliant=False,
        )
        with pytest.raises(api_errors.ApiErrors) as error:
            api.update_offer(offer, body)

        assert error.value.errors == {
            "durationMinutes": ["Vous ne pouvez pas modifier ce champ"],
            "isDuo": ["Vous ne pouvez pas modifier ce champ"],
        }
        offer = db.session.query(models.Offer).one()
        assert offer.durationMinutes == 90
        assert offer.isDuo is False
        assert offer.audioDisabilityCompliant is True

    def test_update_rejected_offer_fails(self):
        pending_offer = factories.OfferFactory(name="Soliloquy", validation=models.OfferValidationStatus.REJECTED)
        body = offers_schemas.UpdateOffer(name="Monologue")
        with pytest.raises(exceptions.OfferException) as error:
            api.update_offer(pending_offer, body)

        assert error.value.errors == {"global": ["Les offres refusées ne sont pas modifiables"]}
        pending_offer = db.session.query(models.Offer).one()
        assert pending_offer.name == "Soliloquy"

    def test_success_on_updating_id_at_provider(self):
        provider = providers_factories.PublicApiProviderFactory()
        offerer = offerers_factories.OffererFactory()
        providers_factories.OffererProviderFactory(offerer=offerer, provider=provider)
        offer = factories.OfferFactory(
            lastProvider=provider,
            name="Offer linked to a provider",
            ean="1234567890124",
        )
        body = offers_schemas.UpdateOffer(idAtProvider="some_id_at_provider")
        api.update_offer(offer, body)

        offer = db.session.query(models.Offer).one()
        assert offer.name == "Offer linked to a provider"
        assert offer.idAtProvider == "some_id_at_provider"

    def test_success_should_duplicate_ean(self):
        provider = providers_factories.PublicApiProviderFactory()
        offerer = offerers_factories.OffererFactory()
        providers_factories.OffererProviderFactory(offerer=offerer, provider=provider)
        offer = factories.OfferFactory(
            lastProvider=provider,
            name="Offer linked to a provider",
            ean="1234567890124",
        )
        body = offers_schemas.UpdateOffer(ean="1234567890125")
        api.update_offer(offer, body)

        offer = db.session.query(models.Offer).one()
        assert offer.ean == "1234567890125"

    def test_success_should_not_duplicate_ean_when_it_is_an_empty_string(self):
        provider = providers_factories.PublicApiProviderFactory()
        offerer = offerers_factories.OffererFactory()
        providers_factories.OffererProviderFactory(offerer=offerer, provider=provider)
        offer = factories.EventOfferFactory(lastProvider=provider, name="Offer linked to a provider", ean=None)
        body = offers_schemas.UpdateOffer(ean=None)
        api.update_offer(offer, body)

        offer = db.session.query(models.Offer).one()
        assert offer.ean == None

    def test_raise_error_on_updating_id_at_provider(self):
        offer = factories.OfferFactory(
            lastProvider=None,
            name="Offer linked to a provider",
            ean="1234567890124",
        )
        body = offers_schemas.UpdateOffer(idAtProvider="some_id_at_provider")
        with pytest.raises(exceptions.OfferException) as error:
            api.update_offer(offer, body)

        assert error.value.errors["idAtProvider"] == [
            "Une offre ne peut être créée ou éditée avec un idAtProvider si elle n'a pas de provider"
        ]

    def test_raise_error_on_updating_id_at_provider_because_this_id_is_already_taken(self):
        provider = providers_factories.PublicApiProviderFactory()
        offerer = offerers_factories.OffererFactory()
        providers_factories.OffererProviderFactory(offerer=offerer, provider=provider)
        venue = offerers_factories.VenueFactory()
        id_at_provider = "rolalala"

        # existing offer with `id_at_provider`
        factories.OfferFactory(
            lastProvider=provider,
            name="Offer linked to a provider",
            venue=venue,
            idAtProvider=id_at_provider,
        )
        offer = factories.OfferFactory(
            lastProvider=provider,
            name="Offer linked to a provider",
            ean="1234567890124",
            venue=venue,
        )

        body = offers_schemas.UpdateOffer(idAtProvider=id_at_provider)
        with pytest.raises(exceptions.OfferException) as error:
            api.update_offer(offer, body)

        assert error.value.errors["idAtProvider"] == ["`rolalala` is already taken by another venue offer"]

    @pytest.mark.parametrize("isDigital", [True, False])
    def test_offer_update_accordingly_of_its_digitalness(self, isDigital):
        kwargs = {}
        if isDigital:
            kwargs["isVirtual"] = True
            kwargs["offererAddress"] = None
            kwargs["siret"] = None
        venue = offerers_factories.VenueFactory(**kwargs)
        offerer_address = offerers_factories.OffererAddressFactory(offerer=venue.managingOfferer)
        offer = factories.OfferFactory(
            offererAddress=None,
            venue=venue,
            url="http://example.com" if isDigital else None,
            subcategoryId=subcategories.VOD.id if isDigital else subcategories.SPECTACLE_REPRESENTATION.id,
        )
        body = offers_schemas.UpdateOffer(name="New name", offererAddress=offerer_address)
        if isDigital:
            with pytest.raises(api_errors.ApiErrors) as error:
                api.update_offer(offer, body)
                assert error.value.errors["offerUrl"] == ["Une offre numérique ne peut pas avoir d'adresse"]
        else:
            api.update_offer(offer, body)
            offer = db.session.query(models.Offer).one()
            assert offer.offererAddress == offerer_address

    def test_update_venue(self):
        offerer = offerers_factories.OffererFactory()
        offer_oa = offerers_factories.OffererAddressFactory(offerer=offerer)
        venue_oa = offerers_factories.OffererAddressFactory(offerer=offerer)
        offer = factories.OfferFactory(offererAddress=offer_oa)
        offer_oa_id = offer.offererAddressId
        new_venue = offerers_factories.VenueFactory(
            managingOfferer=offer.venue.managingOfferer,
            offererAddress=venue_oa,
        )
        venue_oa_id = new_venue.offererAddressId
        body = offers_schemas.UpdateOffer()
        assert offer_oa_id != venue_oa_id

        updated_offer = api.update_offer(offer, body, venue=new_venue)

        db.session.commit()
        db.session.refresh(updated_offer)

        assert updated_offer
        assert updated_offer.venueId == new_venue.id
        assert updated_offer.offererAddressId == offer_oa_id

    def test_update_offerer_address(self):
        new_offerer_address = offerers_factories.OffererAddressFactory(
            address__latitude=50.63153,
            address__longitude=3.06089,
            address__postalCode="59000",
            address__city="Lille",
        )
        offer = factories.OfferFactory()
        body = offers_schemas.UpdateOffer()

        updated_offer = api.update_offer(offer, body, offerer_address=new_offerer_address)

        db.session.commit()
        db.session.refresh(updated_offer)

        assert updated_offer
        assert updated_offer.offererAddressId == new_offerer_address.id

    def test_update_both_venue_and_offerer_address(self):
        new_offerer_address = offerers_factories.OffererAddressFactory(
            address__latitude=50.63153,
            address__longitude=3.06089,
            address__postalCode="59000",
            address__city="Lille",
        )
        offer = factories.OfferFactory()
        new_venue = offerers_factories.VenueFactory(managingOfferer=offer.venue.managingOfferer)
        body = offers_schemas.UpdateOffer()

        updated_offer = api.update_offer(offer, body, venue=new_venue, offerer_address=new_offerer_address)

        db.session.commit()
        db.session.refresh(updated_offer)

        assert updated_offer
        assert updated_offer.offererAddressId == new_offerer_address.id
        assert updated_offer.venueId == new_venue.id

    @pytest.mark.parametrize(
        "bookingAllowedDatetime,expected_calls_count",
        [
            (datetime.now() - timedelta(minutes=5), 1),
            (None, 1),
            (datetime.now() + timedelta(days=5), 0),
        ],
    )
    @mock.patch("pcapi.core.reminders.external.reminders_notifications.notify_users_offer_is_bookable")
    def test_booking_allowed_datetime_update(
        self, notify_users_offer_is_bookable_mock, bookingAllowedDatetime, expected_calls_count
    ):
        offer = factories.OfferFactory(bookingAllowedDatetime=datetime.now() + timedelta(days=1))

        body = offers_schemas.UpdateOffer(bookingAllowedDatetime=bookingAllowedDatetime)

        updated_offer = api.update_offer(offer, body)
        assert len(notify_users_offer_is_bookable_mock.mock_calls) == expected_calls_count
        assert updated_offer.bookingAllowedDatetime == bookingAllowedDatetime


now_datetime_with_tz = datetime.now(timezone.utc)
now_datetime_without_tz = now_datetime_with_tz.replace(tzinfo=None)

yesterday_datetime_with_tz = now_datetime_with_tz - timedelta(days=1)
yesterday_datetime_without_tz = yesterday_datetime_with_tz.replace(tzinfo=None)


@pytest.mark.usefixtures("db_session")
class BatchUpdateOffersTest:
    @time_machine.travel(now_datetime_with_tz, tick=False)
    @mock.patch("pcapi.core.search.async_index_offer_ids")
    def test_activate_empty_list(self, mocked_async_index_offer_ids, caplog):
        pending_offer = factories.OfferFactory(validation=models.OfferValidationStatus.PENDING)

        query = db.session.query(models.Offer).filter(models.Offer.id.in_({pending_offer.id}))

        with caplog.at_level(logging.INFO):
            api.batch_update_offers(query, activate=True)

        db.session.refresh(pending_offer)
        assert not pending_offer.isActive
        assert not pending_offer.publicationDatetime

        mocked_async_index_offer_ids.assert_not_called()

        assert len(caplog.records) == 2
        first_record = caplog.records[0]

        assert first_record.message == "Batch update of offers: start"
        assert first_record.extra == {"updated_fields": {"publicationDatetime": now_datetime_without_tz}}

        second_record = caplog.records[1]

        assert second_record.message == "Batch update of offers: end"
        assert second_record.extra == {
            "updated_fields": {"publicationDatetime": now_datetime_without_tz},
            "nb_offers": 0,
            "nb_venues": 0,
        }

    @time_machine.travel(now_datetime_with_tz, tick=False)
    @mock.patch("pcapi.core.search.async_index_offer_ids")
    def test_activate(self, mocked_async_index_offer_ids, caplog):
        offer1 = factories.OfferFactory(publicationDatetime=None)
        offer2 = factories.OfferFactory(publicationDatetime=None)
        offer3 = factories.OfferFactory(publicationDatetime=None)
        rejected_offer = factories.OfferFactory(
            publicationDatetime=None, validation=models.OfferValidationStatus.REJECTED
        )
        pending_offer = factories.OfferFactory(validation=models.OfferValidationStatus.PENDING)

        query = db.session.query(models.Offer).filter(
            models.Offer.id.in_({offer1.id, offer2.id, rejected_offer.id, pending_offer.id})
        )

        with caplog.at_level(logging.INFO):
            api.batch_update_offers(query, activate=True)

        db.session.refresh(offer1)
        db.session.refresh(offer2)
        db.session.refresh(offer3)
        db.session.refresh(rejected_offer)
        db.session.refresh(pending_offer)

        assert offer1.isActive
        assert offer1.publicationDatetime == now_datetime_without_tz

        assert offer2.isActive
        assert offer2.publicationDatetime == now_datetime_without_tz

        assert not offer3.isActive
        assert not offer3.publicationDatetime

        assert not rejected_offer.isActive
        assert not rejected_offer.publicationDatetime

        assert not pending_offer.isActive
        assert not pending_offer.publicationDatetime

        mocked_async_index_offer_ids.assert_called_once()
        assert set(mocked_async_index_offer_ids.call_args[0][0]) == set([offer1.id, offer2.id])

        assert len(caplog.records) == 3
        first_record = caplog.records[0]
        second_record = caplog.records[1]
        third_record = caplog.records[2]

        assert first_record.message == "Batch update of offers: start"
        assert first_record.extra == {
            "updated_fields": {"publicationDatetime": now_datetime_with_tz.replace(tzinfo=None)}
        }

        assert second_record.message == "Offers has been activated"
        assert second_record.extra.keys() == {"offer_ids", "venue_ids"}
        assert set(second_record.extra["offer_ids"]) == {offer1.id, offer2.id}
        assert second_record.extra["venue_ids"] == {offer1.venueId, offer2.venueId}

        assert third_record.message == "Batch update of offers: end"
        assert third_record.extra == {
            "updated_fields": {"publicationDatetime": now_datetime_with_tz.replace(tzinfo=None)},
            "nb_offers": 2,
            "nb_venues": 2,
        }

    def test_deactivate(self, caplog):
        offer1 = factories.OfferFactory(
            publicationDatetime=now_datetime_with_tz, bookingAllowedDatetime=now_datetime_with_tz
        )
        offer2 = factories.OfferFactory(
            publicationDatetime=now_datetime_with_tz, bookingAllowedDatetime=now_datetime_without_tz
        )
        offer3 = factories.OfferFactory(
            publicationDatetime=now_datetime_without_tz, bookingAllowedDatetime=now_datetime_without_tz
        )

        query = db.session.query(models.Offer).filter(models.Offer.id.in_({offer1.id, offer2.id}))
        with caplog.at_level(logging.INFO):
            api.batch_update_offers(query, activate=False)

        db.session.refresh(offer1)
        db.session.refresh(offer2)
        db.session.refresh(offer3)

        assert not offer1.isActive
        assert not offer1.publicationDatetime
        assert offer1.bookingAllowedDatetime

        assert not offer2.isActive
        assert not offer2.publicationDatetime
        assert offer2.bookingAllowedDatetime == now_datetime_without_tz

        assert offer3.isActive
        assert offer3.publicationDatetime == now_datetime_without_tz
        assert offer3.bookingAllowedDatetime == now_datetime_without_tz

        assert len(caplog.records) == 4
        first_record = caplog.records[0]
        second_record = caplog.records[1]
        last_record = caplog.records[-1]

        assert first_record.message == "Batch update of offers: start"
        assert first_record.extra == {"updated_fields": {"publicationDatetime": None}}

        assert second_record.message == "Offers has been deactivated"
        assert second_record.extra.keys() == {"offer_ids", "venue_ids"}
        assert set(second_record.extra["offer_ids"]) == {offer1.id, offer2.id}
        assert second_record.extra["venue_ids"] == {offer1.venueId, offer2.venueId}

        assert last_record.message == "Batch update of offers: end"
        assert last_record.extra == {
            "updated_fields": {"publicationDatetime": None},
            "nb_offers": 2,
            "nb_venues": 2,
        }


@pytest.mark.usefixtures("db_session")
class FutureOfferReminderTest:
    @mock.patch("pcapi.core.search.async_index_offer_ids")
    def test_reindex_recently_published_offers(self, mocked_async_index_offer_ids):
        publication_date = (now_datetime_with_tz - timedelta(minutes=10)).replace(tzinfo=None)

        offer_1 = factories.OfferFactory(publicationDatetime=publication_date)
        offer_2 = factories.OfferFactory(publicationDatetime=publication_date)
        offer_3 = factories.OfferFactory(publicationDatetime=None)

        api.reindex_recently_published_offers(publication_date)

        mocked_async_index_offer_ids.assert_called_once()
        assert set(mocked_async_index_offer_ids.call_args[0][0]) == set([offer_1.id, offer_2.id])

        assert db.session.get(models.Offer, offer_1.id).isActive
        assert db.session.get(models.Offer, offer_2.id).isActive
        assert not db.session.get(models.Offer, offer_3.id).isActive

    @mock.patch("pcapi.core.reminders.external.reminders_notifications.send_users_reminders_for_offer")
    def test_remind_users(self, send_reminder_mock):
        booking_allowed_datetime = (now_datetime_with_tz - timedelta(minutes=10)).replace(tzinfo=None)

        user_1 = users_factories.BeneficiaryFactory()
        user_2 = users_factories.BeneficiaryFactory()

        offer_1 = factories.OfferFactory(bookingAllowedDatetime=booking_allowed_datetime)
        offer_2 = factories.OfferFactory(bookingAllowedDatetime=booking_allowed_datetime)
        factories.OfferFactory(bookingAllowedDatetime=None)

        reminders_factories.OfferReminderFactory(offer=offer_1, user=user_1)
        reminders_factories.OfferReminderFactory(offer=offer_2, user=user_1)
        reminders_factories.OfferReminderFactory(offer=offer_2, user=user_2)

        api.send_future_offer_reminders()

        send_reminder_mock.assert_called()

        assert len(send_reminder_mock.call_args_list) == 2

        expected_first_call = mock.call([user_1.id], offer_1)
        expected_second_call = mock.call([user_1.id, user_2.id], offer_2)

        send_reminder_mock.assert_has_calls([expected_first_call, expected_second_call], any_order=True)


@pytest.mark.usefixtures("db_session")
class HeadlineOfferTest:
    @mock.patch("pcapi.core.search.async_index_offer_ids")
    def test_make_new_offer_headline(self, mocked_async_index_offer_ids):
        venue = offerers_factories.VenueFactory(venueTypeCode=VenueTypeCode.LIBRARY)
        offer = factories.OfferFactory(publicationDatetime=yesterday_datetime_with_tz, venue=venue)
        factories.StockFactory(offer=offer)
        factories.MediationFactory(offer=offer)
        headline_offer = api.make_offer_headline(offer=offer)
        db.session.commit()  # see comment in make_offer_headline()

        assert offer.is_headline_offer
        assert headline_offer.isActive
        assert headline_offer.timespan.lower
        assert not headline_offer.timespan.upper

        mocked_async_index_offer_ids.assert_called_once_with(
            {offer.id},
            reason=search.IndexationReason.OFFER_REINDEXATION,
        )

    @mock.patch("pcapi.core.search.async_index_offer_ids")
    def test_create_offer_headline_when_another_is_still_active_should_fail(self, mocked_async_index_offer_ids):
        venue = offerers_factories.VenueFactory(venueTypeCode=VenueTypeCode.LIBRARY)
        offer = factories.OfferFactory(publicationDatetime=yesterday_datetime_with_tz, venue=venue)
        factories.StockFactory(offer=offer)
        factories.MediationFactory(offer=offer)
        api.make_offer_headline(offer=offer)
        mocked_async_index_offer_ids.assert_called_once_with(
            {offer.id},
            reason=search.IndexationReason.OFFER_REINDEXATION,
        )
        with pytest.raises(exceptions.OfferHasAlreadyAnActiveHeadlineOffer) as error:
            api.make_offer_headline(offer=offer)
            assert error.value.errors["headlineOffer"] == ["This offer is already an active headline offer"]

    @mock.patch("pcapi.core.search.async_index_offer_ids")
    def test_remove_headline_offer(self, mocked_async_index_offer_ids):
        offer = factories.OfferFactory(publicationDatetime=now_datetime_with_tz)
        headline_offer = factories.HeadlineOfferFactory(offer=offer)

        api.remove_headline_offer(headline_offer)
        db.session.commit()  # see comment in make_offer_headline()

        assert headline_offer.timespan.upper
        assert not headline_offer.isActive
        assert not offer.is_headline_offer

        mocked_async_index_offer_ids.assert_called_once_with(
            {offer.id},
            reason=search.IndexationReason.OFFER_REINDEXATION,
        )

    @time_machine.travel("2024-12-13 15:44:00")
    @mock.patch("pcapi.core.search.async_index_offer_ids")
    def test_make_offer_headline_again(self, mocked_async_index_offer_ids):
        venue = offerers_factories.VenueFactory(venueTypeCode=VenueTypeCode.LIBRARY)
        offer = factories.OfferFactory(publicationDatetime=now_datetime_with_tz, venue=venue)
        creation_time = datetime.utcnow()
        finished_timespan = (creation_time, creation_time + timedelta(days=10))
        old_headline_offer = factories.HeadlineOfferFactory(offer=offer, timespan=finished_timespan)

        one_eternity_later = creation_time + timedelta(days=1000)
        with time_machine.travel(one_eternity_later):
            new_headline_offer = api.make_offer_headline(offer=offer)
            db.session.commit()  # see comment in make_offer_headline()
            assert offer.is_headline_offer
            assert not old_headline_offer.isActive
            assert new_headline_offer.isActive
            assert new_headline_offer.timespan.lower.date() != creation_time.date()
            assert new_headline_offer.timespan.upper == None

        mocked_async_index_offer_ids.assert_called_once_with(
            {offer.id},
            reason=search.IndexationReason.OFFER_REINDEXATION,
        )

    @time_machine.travel(now_datetime_with_tz)
    @mock.patch("pcapi.core.search.async_index_offer_ids")
    def test_make_another_offer_headline_on_same_venue(self, mocked_async_index_offer_ids):
        venue = offerers_factories.VenueFactory(venueTypeCode=VenueTypeCode.LIBRARY)
        offer_1 = factories.OfferFactory(publicationDatetime=yesterday_datetime_with_tz, venue=venue)
        offer_2 = factories.OfferFactory(publicationDatetime=yesterday_datetime_with_tz, venue=venue)
        factories.StockFactory(offer=offer_2)
        factories.MediationFactory(offer=offer_2)

        ten_days_ago = datetime.utcnow() - timedelta(days=10)
        finished_timespan = (ten_days_ago, ten_days_ago + timedelta(days=1))
        old_headline_offer = factories.HeadlineOfferFactory(offer=offer_1, timespan=finished_timespan)
        new_headline_offer = api.make_offer_headline(offer=offer_2)
        db.session.commit()  # see comment in make_offer_headline()

        assert not old_headline_offer.isActive
        assert new_headline_offer.isActive
        assert not offer_1.is_headline_offer
        assert offer_2.is_headline_offer
        assert venue.has_headline_offer

        mocked_async_index_offer_ids.assert_called_once_with(
            {offer_2.id},
            reason=search.IndexationReason.OFFER_REINDEXATION,
        )

    @mock.patch("pcapi.core.search.async_index_offer_ids")
    def test_headline_offer_on_offer_turned_inactive_is_inactive(self, mocked_async_index_offer_ids):
        venue = offerers_factories.VenueFactory(venueTypeCode=VenueTypeCode.LIBRARY)
        active_offer = factories.OfferFactory(publicationDatetime=now_datetime_without_tz, venue=venue)
        factories.StockFactory(offer=active_offer)
        factories.MediationFactory(offer=active_offer)

        api.make_offer_headline(offer=active_offer)

        active_offer.publicationDatetime = None
        assert not active_offer.is_headline_offer

        mocked_async_index_offer_ids.assert_called_once_with(
            {active_offer.id},
            reason=search.IndexationReason.OFFER_REINDEXATION,
        )

    @mock.patch("pcapi.core.search.async_index_offer_ids")
    def test_headline_offer_on_sold_out_offer_is_inactive(self, mocked_async_index_offer_ids):
        venue = offerers_factories.VenueFactory(venueTypeCode=VenueTypeCode.LIBRARY)
        stock = factories.StockFactory(quantity=10)
        mediation = factories.MediationFactory()
        offer = factories.OfferFactory(
            publicationDatetime=yesterday_datetime_with_tz, stocks=[stock], mediations=[mediation], venue=venue
        )

        api.make_offer_headline(offer=offer)
        assert offer.is_headline_offer

        stock.quantity = 0
        assert not offer.is_headline_offer

        mocked_async_index_offer_ids.assert_called_once_with(
            {offer.id},
            reason=search.IndexationReason.OFFER_REINDEXATION,
        )

    @mock.patch("pcapi.core.search.async_index_offer_ids")
    def test_headline_offer_on_expired_offer_is_inactive(self, mocked_async_index_offer_ids):
        venue = offerers_factories.VenueFactory(venueTypeCode=VenueTypeCode.LIBRARY)
        tomorrow = date.today() + timedelta(days=1)
        stock = factories.StockFactory(bookingLimitDatetime=tomorrow)
        mediation = factories.MediationFactory()
        offer = factories.OfferFactory(
            validation=models.OfferValidationStatus.APPROVED,
            publicationDatetime=yesterday_datetime_with_tz,
            stocks=[
                stock,
            ],
            venue=venue,
            mediations=[mediation],
        )
        api.make_offer_headline(offer=offer)
        assert offer.is_headline_offer
        with time_machine.travel(tomorrow + timedelta(days=1)):
            assert not offer.is_headline_offer

        mocked_async_index_offer_ids.assert_called_once_with(
            {offer.id},
            reason=search.IndexationReason.OFFER_REINDEXATION,
        )

    @mock.patch("pcapi.core.search.async_index_offer_ids")
    def test_headline_offer_on_rejected_offer_is_inactive(self, mocked_async_index_offer_ids):
        venue = offerers_factories.VenueFactory(venueTypeCode=VenueTypeCode.LIBRARY)
        offer = factories.OfferFactory(publicationDatetime=yesterday_datetime_with_tz, venue=venue)
        factories.StockFactory(offer=offer)
        factories.MediationFactory(offer=offer)

        api.make_offer_headline(offer=offer)
        offer.validation = models.OfferValidationStatus.REJECTED
        assert not offer.is_headline_offer

        mocked_async_index_offer_ids.assert_called_once_with(
            {offer.id},
            reason=search.IndexationReason.OFFER_REINDEXATION,
        )

    @mock.patch("pcapi.core.search.async_index_offer_ids")
    def test_set_upper_timespan_of_inactive_headline_offers(self, mocked_async_index_offer_ids, caplog):
        headline_offer_1 = factories.HeadlineOfferFactory()
        headline_offer_3 = factories.HeadlineOfferFactory()
        headline_offer_2 = factories.HeadlineOfferFactory()

        assert headline_offer_1.isActive
        assert headline_offer_1.timespan.upper is None
        assert headline_offer_2.isActive
        assert headline_offer_2.timespan.upper is None

        headline_offer_1.offer.validation = models.OfferValidationStatus.REJECTED
        headline_offer_2.offer.stocks[0].quantity = 0

        with caplog.at_level(logging.INFO):
            api.set_upper_timespan_of_inactive_headline_offers()

        assert len(caplog.records) == 2
        assert caplog.records[0].message == "Headline Offer Deactivation"
        assert caplog.records[0].extra["Reason"] == "Offer is not active anymore, or image has been removed"
        assert caplog.records[0].extra["analyticsSource"] == "app-pro"
        assert caplog.records[0].technical_message_id == "headline_offer_deactivation"
        assert caplog.records[1].message == "Headline Offer Deactivation"
        assert caplog.records[1].extra["Reason"] == "Offer is not active anymore, or image has been removed"
        assert caplog.records[1].extra["analyticsSource"] == "app-pro"
        assert caplog.records[1].technical_message_id == "headline_offer_deactivation"

        assert not headline_offer_1.isActive
        assert headline_offer_1.timespan.upper is not None
        assert not headline_offer_2.isActive
        assert headline_offer_2.timespan.upper is not None

        assert headline_offer_3.isActive
        assert headline_offer_3.timespan.upper is None

        mocked_async_index_offer_ids.assert_called_once_with(
            {headline_offer_1.offerId, headline_offer_2.offerId},
            reason=search.IndexationReason.OFFER_REINDEXATION,
        )

    @mock.patch("pcapi.core.search.async_index_offer_ids")
    def test_do_not_deactivate_headline_offer_with_product_mediation(self, mocked_async_index_offer_ids, caplog):
        product_without_mediation = factories.ProductFactory()
        product_with_mediation = factories.ProductFactory()
        factories.ProductMediationFactory(product=product_with_mediation)
        offer_with_product_mediation = factories.OfferFactory(product=product_with_mediation)
        offer_without_product_mediation = factories.OfferFactory(product=product_without_mediation)
        headline_offer_with_product_mediation = factories.HeadlineOfferFactory(
            offer=offer_with_product_mediation, without_mediation=True
        )
        headline_offer_without_product_mediation = factories.HeadlineOfferFactory(
            offer=offer_without_product_mediation, without_mediation=True
        )

        assert headline_offer_with_product_mediation.offer.images
        assert not headline_offer_without_product_mediation.offer.images

        with caplog.at_level(logging.INFO):
            api.set_upper_timespan_of_inactive_headline_offers()

        assert len(caplog.records) == 1
        assert caplog.records[0].message == "Headline Offer Deactivation"
        assert caplog.records[0].extra == {
            "analyticsSource": "app-pro",
            "HeadlineOfferId": headline_offer_without_product_mediation.id,
            "Reason": "Offer is not active anymore, or image has been removed",
        }

        assert headline_offer_with_product_mediation.isActive
        assert headline_offer_with_product_mediation.timespan.upper is None

        assert not headline_offer_without_product_mediation.isActive
        assert headline_offer_without_product_mediation.timespan.upper is not None

        mocked_async_index_offer_ids.assert_called_once_with(
            {
                headline_offer_without_product_mediation.offerId,
            },
            reason=search.IndexationReason.OFFER_REINDEXATION,
        )

    @mock.patch("pcapi.core.search.async_index_offer_ids")
    def test_do_not_update_upper_timespan_of_already_inactive_headline_offers(
        self, mocked_async_index_offer_ids, caplog
    ):
        creation_time = datetime.utcnow() - timedelta(days=20)
        finished_timespan = (creation_time, creation_time + timedelta(days=10))
        old_headline_offer = factories.HeadlineOfferFactory(timespan=finished_timespan)

        with caplog.at_level(logging.INFO):
            api.set_upper_timespan_of_inactive_headline_offers()

        assert len(caplog.records) == 0
        assert old_headline_offer.timespan.lower.date() == creation_time.date()
        assert old_headline_offer.timespan.upper.date() == (creation_time + timedelta(days=10)).date()

        mocked_async_index_offer_ids.assert_called_once_with(
            set(),
            reason=search.IndexationReason.OFFER_REINDEXATION,
        )

    @mock.patch("pcapi.core.search.async_index_offer_ids")
    def test_should_not_change_upper_timespan_of_already_deactivated_offers(self, mocked_async_index_offer_ids, caplog):
        creation_time_1 = datetime.utcnow() - timedelta(days=3)
        ending_time_1 = datetime.utcnow() - timedelta(days=2)
        creation_time_2 = datetime.utcnow() - timedelta(days=1)
        finished_timespan = (creation_time_1, ending_time_1)
        unfinished_timespan = (creation_time_2, None)
        old_headline_offer = factories.HeadlineOfferFactory(timespan=finished_timespan)
        current_headline_offer = factories.HeadlineOfferFactory(timespan=unfinished_timespan, without_mediation=True)

        with caplog.at_level(logging.INFO):
            api.set_upper_timespan_of_inactive_headline_offers()

        assert len(caplog.records) == 1
        assert caplog.records[0].message == "Headline Offer Deactivation"
        assert caplog.records[0].extra == {
            "analyticsSource": "app-pro",
            "HeadlineOfferId": current_headline_offer.id,
            "Reason": "Offer is not active anymore, or image has been removed",
        }
        assert old_headline_offer.timespan.lower == creation_time_1
        assert old_headline_offer.timespan.upper == ending_time_1
        assert current_headline_offer.timespan.lower == creation_time_2
        assert current_headline_offer.timespan.upper is not None

        mocked_async_index_offer_ids.assert_called_once_with(
            {
                current_headline_offer.offerId,
            },
            reason=search.IndexationReason.OFFER_REINDEXATION,
        )

    @mock.patch("pcapi.core.search.async_index_offer_ids")
    def test_set_upper_timespan_of_inactive_headline_offers_without_image(self, mocked_async_index_offer_ids, caplog):
        offer = factories.OfferFactory(publicationDatetime=now_datetime_with_tz)

        headline_offer = factories.HeadlineOfferFactory(offer=offer, without_mediation=True)
        assert not headline_offer.isActive

        with caplog.at_level(logging.INFO):
            api.set_upper_timespan_of_inactive_headline_offers()

        assert len(caplog.records) == 1
        assert caplog.records[0].message == "Headline Offer Deactivation"
        assert caplog.records[0].extra == {
            "analyticsSource": "app-pro",
            "HeadlineOfferId": headline_offer.id,
            "Reason": "Offer is not active anymore, or image has been removed",
        }

        assert headline_offer.timespan.upper is not None

        mocked_async_index_offer_ids.assert_called_once_with(
            {headline_offer.offerId},
            reason=search.IndexationReason.OFFER_REINDEXATION,
        )

    @mock.patch("pcapi.core.search.async_index_offer_ids")
    def test_upsert_headline_offer_on_another_offer(self, mocked_async_index_offer_ids, caplog):
        offer = factories.OfferFactory(venue__venueTypeCode=VenueTypeCode.LIBRARY)
        another_offer = factories.OfferFactory(venue=offer.venue)
        factories.StockFactory(offer=another_offer)
        factories.MediationFactory(offer=another_offer)
        headline_offer = factories.HeadlineOfferFactory(offer=offer)

        with caplog.at_level(logging.INFO):
            new_headline_offer = api.upsert_headline_offer(another_offer)
            db.session.commit()  # see comment in make_offer_headline()

        assert len(caplog.records) == 1
        assert caplog.records[0].message == "Headline Offer Deactivation"
        assert caplog.records[0].extra == {
            "analyticsSource": "app-pro",
            "HeadlineOfferId": headline_offer.id,
            "Reason": "User chose to replace this headline offer by another offer",
        }

        assert not offer.is_headline_offer
        assert another_offer.is_headline_offer
        assert not headline_offer.isActive
        assert headline_offer.timespan.upper is not None
        assert new_headline_offer.isActive
        assert new_headline_offer.timespan.upper is None

        expected_reindexation_calls = [
            mock.call({offer.id}, reason=search.IndexationReason.OFFER_REINDEXATION),
            mock.call({another_offer.id}, reason=search.IndexationReason.OFFER_REINDEXATION),
        ]
        mocked_async_index_offer_ids.assert_has_calls(expected_reindexation_calls)

    @mock.patch("pcapi.core.search.async_index_offer_ids")
    def test_upsert_headline_offer_on_same_offer(self, mocked_async_index_offer_ids, caplog):
        offer = factories.OfferFactory(venue__venueTypeCode=VenueTypeCode.LIBRARY)
        creation_time = datetime.utcnow() - timedelta(days=20)
        finished_timespan = (creation_time, creation_time + timedelta(days=10))
        headline_offer = factories.HeadlineOfferFactory(offer=offer, timespan=finished_timespan)
        with caplog.at_level(logging.INFO):
            new_headline_offer = api.upsert_headline_offer(offer)
            db.session.commit()  # see comment in make_offer_headline()

        assert len(caplog.records) == 0

        assert not headline_offer.isActive
        assert headline_offer.timespan.upper is not None
        assert new_headline_offer.isActive
        assert new_headline_offer.timespan.upper is None

        mocked_async_index_offer_ids.assert_called_once_with(
            {headline_offer.offerId},
            reason=search.IndexationReason.OFFER_REINDEXATION,
        )


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
    def test_add_criteria_from_ean(self, mocked_async_index_offer_ids):
        # Given
        ean1 = Fake.ean13()
        product1 = factories.ProductFactory(ean=ean1)
        offer11 = factories.OfferFactory(product=product1)
        offer12 = factories.OfferFactory(product=product1)
        inactive_offer = factories.OfferFactory(product=product1, publicationDatetime=None)
        unmatched_offer = factories.OfferFactory()
        criterion1 = criteria_factories.CriterionFactory(name="Pretty good books")
        criterion2 = criteria_factories.CriterionFactory(name="Other pretty good books")

        # When
        is_successful = api.add_criteria_to_offers([criterion1.id, criterion2.id], ean=ean1)

        # Then
        assert is_successful is True
        assert set(offer11.criteria) == {criterion1, criterion2}
        assert set(offer12.criteria) == {criterion1, criterion2}
        assert not inactive_offer.criteria
        assert not unmatched_offer.criteria
        mocked_async_index_offer_ids.assert_called_once_with(
            {offer11.id, offer12.id},
            reason=search.IndexationReason.CRITERIA_LINK,
            log_extra={"criterion_ids": [criterion1.id, criterion2.id]},
        )

    @mock.patch("pcapi.core.search.async_index_offer_ids")
    def test_add_criteria_from_ean_when_one_has_criteria(self, mocked_async_index_offer_ids):
        # Given
        ean_1 = Fake.ean13()
        criterion1 = criteria_factories.CriterionFactory(name="Pretty good books")
        criterion2 = criteria_factories.CriterionFactory(name="Other pretty good books")
        product1 = factories.ProductFactory(ean=ean_1)
        offer11 = factories.OfferFactory(product=product1, criteria=[criterion1])
        offer12 = factories.OfferFactory(product=product1, criteria=[criterion2])
        inactive_offer = factories.OfferFactory(product=product1, publicationDatetime=None)
        unmatched_offer = factories.OfferFactory()

        # When
        is_successful = api.add_criteria_to_offers([criterion1.id, criterion2.id], ean=ean_1)

        # Then
        assert is_successful is True
        assert set(offer11.criteria) == {criterion1, criterion2}
        assert set(offer12.criteria) == {criterion1, criterion2}
        assert not inactive_offer.criteria
        assert not unmatched_offer.criteria
        mocked_async_index_offer_ids.assert_called_once_with(
            {offer11.id, offer12.id},
            reason=search.IndexationReason.CRITERIA_LINK,
            log_extra={"criterion_ids": [criterion1.id, criterion2.id]},
        )

    @mock.patch("pcapi.core.search.async_index_offer_ids")
    def test_add_criteria_from_visa(self, mocked_async_index_offer_ids):
        # Given
        visa = "222100"
        product = factories.ProductFactory(extraData={"visa": visa})
        offer1 = factories.OfferFactory(product=product)
        offer2 = factories.OfferFactory(product=product)
        inactive_offer = factories.OfferFactory(product=product, publicationDatetime=None)
        unmatched_offer = factories.OfferFactory()
        criterion1 = criteria_factories.CriterionFactory(name="Pretty good books")
        criterion2 = criteria_factories.CriterionFactory(name="Other pretty good books")

        # When
        is_successful = api.add_criteria_to_offers([criterion1.id, criterion2.id], visa=visa)

        # Then
        assert is_successful is True
        assert set(offer1.criteria) == {criterion1, criterion2}
        assert set(offer2.criteria) == {criterion1, criterion2}
        assert not inactive_offer.criteria
        assert not unmatched_offer.criteria
        mocked_async_index_offer_ids.assert_called_once_with(
            {offer1.id, offer2.id},
            reason=search.IndexationReason.CRITERIA_LINK,
            log_extra={"criterion_ids": [criterion1.id, criterion2.id]},
        )

    @mock.patch("pcapi.core.search.async_index_offer_ids")
    def test_add_criteria_when_no_offers_is_found(self, mocked_async_index_offer_ids):
        # Given
        ean = "1234567899999"
        factories.OfferFactory(ean="1234567899999")
        criterion = criteria_factories.CriterionFactory(name="Pretty good books")

        # When
        is_successful = api.add_criteria_to_offers([criterion.id], ean=ean)

        # Then
        assert is_successful is False
        mocked_async_index_offer_ids.assert_not_called()

    @mock.patch("pcapi.core.search.async_index_offer_ids")
    def test_add_criteria_when_no_criterion_to_add(self, mocked_async_index_offer_ids):
        ean = Fake.ean13()
        product = factories.ProductFactory(ean=ean)
        factories.OfferFactory(product=product)

        is_successful = api.add_criteria_to_offers([], ean=ean)

        assert is_successful is False
        mocked_async_index_offer_ids.assert_not_called()


@pytest.mark.usefixtures("db_session")
class RejectInappropriateProductTest:
    @mock.patch("pcapi.core.search.async_index_offer_ids")
    @mock.patch("pcapi.core.mails.transactional.send_booking_cancellation_emails_to_user_and_offerer")
    def test_should_reject_product_with_inappropriate_content(
        self, mocked_send_booking_cancellation_emails_to_user_and_offerer, mocked_async_index_offer_ids
    ):
        # Given
        ean_1 = Fake.ean13()
        ean_2 = Fake.ean13()
        provider = providers_factories.PublicApiProviderFactory()
        product1 = factories.ThingProductFactory(
            subcategoryId=subcategories.LIVRE_PAPIER.id, ean=ean_1, lastProvider=provider
        )
        product2 = factories.ThingProductFactory(
            subcategoryId=subcategories.LIVRE_PAPIER.id, ean=ean_2, lastProvider=provider
        )
        offers = {
            factories.OfferFactory(product=product1),
            factories.OfferFactory(product=product1),
            factories.OfferFactory(product=product2),
        }
        user = users_factories.UserFactory()

        for offer in offers:
            users_factories.FavoriteFactory(offer=offer)
            bookings_factories.BookingFactory(stock__offer=offer)

        # When
        api.reject_inappropriate_products([ean_1], user, send_booking_cancellation_emails=False)

        # Then
        offers = db.session.query(models.Offer).all()
        bookings = db.session.query(bookings_models.Booking).all()

        product1 = db.session.query(models.Product).filter(models.Product.ean == ean_1).one()
        assert product1.gcuCompatibilityType == models.GcuCompatibilityType.PROVIDER_INCOMPATIBLE

        product2 = db.session.query(models.Product).filter(models.Product.ean == ean_2).one()
        assert product2.isGcuCompatible

        assert all(
            offer.validation == OfferValidationStatus.REJECTED for offer in offers if offer.product.id == product1.id
        )
        assert all(offer.lastValidationAuthorUserId == user.id for offer in offers if offer.product.id == product1.id)

        assert all(
            offer.validation == OfferValidationStatus.APPROVED for offer in offers if offer.product.id == product2.id
        )

        mocked_async_index_offer_ids.assert_called()
        assert set(mocked_async_index_offer_ids.call_args[0][0]) == {
            o.id for o in offers if o.product.id == product1.id
        }
        assert db.session.query(users_models.Favorite).count() == 1  # product 2
        assert all(booking.isCancelled is True for booking in bookings if booking.stock.offer.product.id == product1)
        mocked_send_booking_cancellation_emails_to_user_and_offerer.assert_not_called()

    @mock.patch("pcapi.core.mails.transactional.send_booking_cancellation_emails_to_user_and_offerer")
    def test_should_reject_product_with_inappropriate_content_and_send_email(
        self, mocked_send_booking_cancellation_emails_to_user_and_offerer
    ):
        # Given
        ean_1 = Fake.ean13()
        ean_2 = Fake.ean13()
        provider = providers_factories.PublicApiProviderFactory()
        product1 = factories.ThingProductFactory(
            subcategoryId=subcategories.LIVRE_PAPIER.id, ean=ean_1, lastProvider=provider
        )
        product2 = factories.ThingProductFactory(
            subcategoryId=subcategories.LIVRE_PAPIER.id, ean=ean_2, lastProvider=provider
        )
        offers = {
            factories.OfferFactory(product=product1),
            factories.OfferFactory(product=product1),
            factories.OfferFactory(product=product2),
        }
        user = users_factories.UserFactory()

        for offer in offers:
            users_factories.FavoriteFactory(offer=offer)
            bookings_factories.BookingFactory(stock__offer=offer)

        assert db.session.query(users_models.Favorite).count() == len(offers)
        assert db.session.query(bookings_models.Booking).count() == len(offers)

        # When
        api.reject_inappropriate_products([ean_1], user)

        # Then
        mocked_send_booking_cancellation_emails_to_user_and_offerer.assert_called()

    @mock.patch("pcapi.core.search.async_index_offer_ids")
    @mock.patch("pcapi.core.mails.transactional.send_booking_cancellation_emails_to_user_and_offerer")
    def test_update_should_not_override_fraud_incompatibility(
        self, mocked_send_booking_cancellation_emails_to_user_and_offerer, mocked_async_index_offer_ids
    ):
        # Given
        ean = Fake.ean13()
        provider = providers_factories.PublicApiProviderFactory()
        factories.ThingProductFactory(
            subcategoryId=subcategories.LIVRE_PAPIER.id,
            ean=ean,
            lastProvider=provider,
            gcuCompatibilityType=models.GcuCompatibilityType.FRAUD_INCOMPATIBLE,
        )
        user = users_factories.UserFactory()

        # When
        api.reject_inappropriate_products([ean], user, send_booking_cancellation_emails=False)

        # Then

        product = db.session.query(models.Product).filter(models.Product.ean == ean).one()
        assert product.gcuCompatibilityType == models.GcuCompatibilityType.FRAUD_INCOMPATIBLE

        mocked_send_booking_cancellation_emails_to_user_and_offerer.assert_not_called()


@pytest.fixture(name="offer_matching_one_validation_rule")
def offer_matching_one_validation_rule_fixture():
    factories.OfferValidationSubRuleFactory(
        model=models.OfferValidationModel.OFFER,
        attribute=models.OfferValidationAttribute.NAME,
        operator=models.OfferValidationRuleOperator.CONTAINS,
        comparated={"comparated": ["REJECTED"]},
    )
    return factories.OfferFactory(name="REJECTED")


@pytest.mark.usefixtures("db_session")
class ResolveOfferValidationRuleTest:
    def test_offer_validation_with_one_rule_with_in(self, offer_matching_one_validation_rule):
        assert (
            api.set_offer_status_based_on_fraud_criteria(offer_matching_one_validation_rule)
            == models.OfferValidationStatus.PENDING
        )
        assert db.session.query(models.ValidationRuleOfferLink).count() == 1

    def test_offer_validation_with_unrelated_rule(self):
        collective_offer = educational_factories.CollectiveOfferFactory(name="REJECTED")
        factories.OfferValidationSubRuleFactory(
            model=models.OfferValidationModel.OFFER,
            attribute=models.OfferValidationAttribute.NAME,
            operator=models.OfferValidationRuleOperator.CONTAINS,
            comparated={"comparated": ["REJECTED"]},
        )

        assert api.set_offer_status_based_on_fraud_criteria(collective_offer) == models.OfferValidationStatus.APPROVED
        assert db.session.query(models.ValidationRuleOfferLink).count() == 0

    @pytest.mark.parametrize(
        "price, expected_status",
        [
            (8, models.OfferValidationStatus.APPROVED),
            (10, models.OfferValidationStatus.APPROVED),
            (12, models.OfferValidationStatus.PENDING),
        ],
    )
    def test_offer_validation_with_one_rule_with_greater_than(self, price, expected_status):
        offer = factories.OfferFactory()
        factories.StockFactory(offer=offer, price=price)
        factories.OfferValidationSubRuleFactory(
            model=models.OfferValidationModel.OFFER,
            attribute=models.OfferValidationAttribute.MAX_PRICE,
            operator=models.OfferValidationRuleOperator.GREATER_THAN,
            comparated={"comparated": 10},
        )

        assert api.set_offer_status_based_on_fraud_criteria(offer) == expected_status

    @pytest.mark.parametrize(
        "price, expected_status",
        [
            (8, models.OfferValidationStatus.PENDING),
            (10, models.OfferValidationStatus.APPROVED),
            (12, models.OfferValidationStatus.APPROVED),
        ],
    )
    def test_offer_validation_with_one_rule_with_less_than(self, price, expected_status):
        offer = factories.OfferFactory()
        factories.StockFactory(offer=offer, price=price)
        factories.OfferValidationSubRuleFactory(
            model=models.OfferValidationModel.OFFER,
            attribute=models.OfferValidationAttribute.MAX_PRICE,
            operator=models.OfferValidationRuleOperator.LESS_THAN,
            comparated={"comparated": 10},
        )

        assert api.set_offer_status_based_on_fraud_criteria(offer) == expected_status

    @pytest.mark.parametrize(
        "price, expected_status",
        [
            (8, models.OfferValidationStatus.APPROVED),
            (10, models.OfferValidationStatus.PENDING),
            (12, models.OfferValidationStatus.PENDING),
        ],
    )
    def test_offer_validation_with_one_rule_with_greater_than_or_equal_to(self, price, expected_status):
        offer = factories.OfferFactory()
        factories.StockFactory(offer=offer, price=price)
        factories.OfferValidationSubRuleFactory(
            model=models.OfferValidationModel.OFFER,
            attribute=models.OfferValidationAttribute.MAX_PRICE,
            operator=models.OfferValidationRuleOperator.GREATER_THAN_OR_EQUAL_TO,
            comparated={"comparated": 10},
        )

        assert api.set_offer_status_based_on_fraud_criteria(offer) == expected_status

    @pytest.mark.parametrize(
        "price, expected_status",
        [
            (8, models.OfferValidationStatus.PENDING),
            (10, models.OfferValidationStatus.PENDING),
            (12, models.OfferValidationStatus.APPROVED),
        ],
    )
    def test_offer_validation_with_one_rule_with_less_than_or_equal_to(self, price, expected_status):
        offer = factories.OfferFactory()
        factories.StockFactory(offer=offer, price=price)
        factories.OfferValidationSubRuleFactory(
            model=models.OfferValidationModel.OFFER,
            attribute=models.OfferValidationAttribute.MAX_PRICE,
            operator=models.OfferValidationRuleOperator.LESS_THAN_OR_EQUAL_TO,
            comparated={"comparated": 10},
        )

        assert api.set_offer_status_based_on_fraud_criteria(offer) == expected_status

    @pytest.mark.parametrize(
        "subcategoryId, expected_status",
        [
            (subcategories.ESCAPE_GAME.id, models.OfferValidationStatus.PENDING),
            (subcategories.SUPPORT_PHYSIQUE_FILM.id, models.OfferValidationStatus.APPROVED),
        ],
    )
    def test_offer_validation_with_one_rule_with_equals(self, subcategoryId, expected_status):
        offer = factories.OfferFactory(subcategoryId=subcategoryId)

        factories.OfferValidationSubRuleFactory(
            model=models.OfferValidationModel.OFFER,
            attribute=models.OfferValidationAttribute.SUBCATEGORY_ID,
            operator=models.OfferValidationRuleOperator.IN,
            comparated={"comparated": ["ESCAPE_GAME"]},
        )

        assert api.set_offer_status_based_on_fraud_criteria(offer) == expected_status

    def test_offer_validation_with_one_rule_with_not_in(self):
        offer = factories.OfferFactory(subcategoryId=subcategories.ESCAPE_GAME.id)
        factories.OfferValidationSubRuleFactory(
            model=models.OfferValidationModel.OFFER,
            attribute=models.OfferValidationAttribute.CATEGORY_ID,
            operator=models.OfferValidationRuleOperator.IN,
            comparated={"comparated": ["MUSEE", "LIVRE", "CINEMA"]},
        )

        assert api.set_offer_status_based_on_fraud_criteria(offer) == models.OfferValidationStatus.APPROVED

    def test_offer_validation_with_one_rule_with_categories(self):
        offer = factories.OfferFactory(subcategoryId=subcategories.ESCAPE_GAME.id)
        factories.OfferValidationSubRuleFactory(
            model=models.OfferValidationModel.OFFER,
            attribute=models.OfferValidationAttribute.CATEGORY_ID,
            operator=models.OfferValidationRuleOperator.IN,
            comparated={"comparated": ["JEU"]},
        )

        assert api.set_offer_status_based_on_fraud_criteria(offer) == models.OfferValidationStatus.PENDING

    def test_offer_validation_with_contains_exact_rule(self):
        offer_to_approve = factories.OfferFactory(name="La blanquette est bonne")
        offer_to_flag = factories.OfferFactory(name="Sapristi, un bon d'achat")
        offer_name_rule = factories.OfferValidationRuleFactory(name="Règle sur le nom des offres")
        factories.OfferValidationSubRuleFactory(
            validationRule=offer_name_rule,
            model=models.OfferValidationModel.OFFER,
            attribute=models.OfferValidationAttribute.NAME,
            operator=models.OfferValidationRuleOperator.CONTAINS_EXACTLY,
            comparated={"comparated": ["bon", "lot"]},
        )

        assert api.set_offer_status_based_on_fraud_criteria(offer_to_approve) == models.OfferValidationStatus.APPROVED
        assert api.set_offer_status_based_on_fraud_criteria(offer_to_flag) == models.OfferValidationStatus.PENDING

    def test_offer_validation_with_contains_rule(self):
        offer_to_flag = factories.OfferFactory(name="Sapristi, un lot interdit")
        offer_to_flag_too = factories.OfferFactory(name="Les complots de la théorie")
        offer_name_rule = factories.OfferValidationRuleFactory(name="Règle sur le nom des offres")
        factories.OfferValidationSubRuleFactory(
            validationRule=offer_name_rule,
            model=models.OfferValidationModel.OFFER,
            attribute=models.OfferValidationAttribute.NAME,
            operator=models.OfferValidationRuleOperator.CONTAINS,
            comparated={"comparated": ["bon", "lot"]},
        )

        assert api.set_offer_status_based_on_fraud_criteria(offer_to_flag) == models.OfferValidationStatus.PENDING
        assert api.set_offer_status_based_on_fraud_criteria(offer_to_flag_too) == models.OfferValidationStatus.PENDING
        assert db.session.query(models.ValidationRuleOfferLink).count() == 2

    def test_offer_validation_rule_with_offer_type(self):
        offer = factories.OfferFactory()
        collective_offer = educational_factories.CollectiveOfferFactory()
        offer_validation_rule = factories.OfferValidationRuleFactory(name="Règle sur les types d'offres")
        factories.OfferValidationSubRuleFactory(
            validationRule=offer_validation_rule,
            model=None,
            attribute=models.OfferValidationAttribute.CLASS_NAME,
            operator=models.OfferValidationRuleOperator.IN,
            comparated={"comparated": ["CollectiveOffer"]},
        )
        assert api.set_offer_status_based_on_fraud_criteria(offer) == models.OfferValidationStatus.APPROVED
        assert api.set_offer_status_based_on_fraud_criteria(collective_offer) == models.OfferValidationStatus.PENDING
        assert db.session.query(models.ValidationRuleOfferLink).count() == 0
        assert db.session.query(educational_models.ValidationRuleCollectiveOfferLink).count() == 1

    def test_offer_validation_rule_with_venue_id(self):
        venue = offerers_factories.VenueFactory()

        offer = factories.OfferFactory(venue=venue)
        collective_offer = educational_factories.CollectiveOfferFactory(venue=venue)
        offer_validation_rule = factories.OfferValidationRuleFactory(name="Règle sur les lieux")
        factories.OfferValidationSubRuleFactory(
            validationRule=offer_validation_rule,
            model=models.OfferValidationModel.VENUE,
            attribute=models.OfferValidationAttribute.ID,
            operator=models.OfferValidationRuleOperator.IN,
            comparated={"comparated": [venue.id]},
        )
        assert api.set_offer_status_based_on_fraud_criteria(offer) == models.OfferValidationStatus.PENDING
        assert api.set_offer_status_based_on_fraud_criteria(collective_offer) == models.OfferValidationStatus.PENDING
        assert db.session.query(models.ValidationRuleOfferLink).count() == 1
        assert db.session.query(educational_models.ValidationRuleCollectiveOfferLink).count() == 1

    def test_offer_validation_rule_with_offerer_id(self):
        offerer = offerers_factories.OffererFactory()
        venue = offerers_factories.VenueFactory(managingOfferer=offerer)

        offer = factories.OfferFactory(venue=venue)
        collective_offer = educational_factories.CollectiveOfferFactory(venue=venue)
        offer_validation_rule = factories.OfferValidationRuleFactory(name="Règle sur les structures")
        factories.OfferValidationSubRuleFactory(
            validationRule=offer_validation_rule,
            model=models.OfferValidationModel.OFFERER,
            attribute=models.OfferValidationAttribute.ID,
            operator=models.OfferValidationRuleOperator.IN,
            comparated={"comparated": [offerer.id]},
        )
        assert api.set_offer_status_based_on_fraud_criteria(offer) == models.OfferValidationStatus.PENDING
        assert api.set_offer_status_based_on_fraud_criteria(collective_offer) == models.OfferValidationStatus.PENDING
        assert db.session.query(models.ValidationRuleOfferLink).count() == 1
        assert db.session.query(educational_models.ValidationRuleCollectiveOfferLink).count() == 1

    @pytest.mark.parametrize(
        "offer_kwargs, expected_status",
        [
            ({"name": "Come to the dark side, we have cookies"}, models.OfferValidationStatus.PENDING),
            ({"description": "Come to the dark side, we have cookies"}, models.OfferValidationStatus.PENDING),
            ({}, models.OfferValidationStatus.APPROVED),
        ],
    )
    def test_offer_validation_rule_with_offer_text(self, offer_kwargs, expected_status):
        offer = factories.OfferFactory(**offer_kwargs)
        offer_validation_rule = factories.OfferValidationRuleFactory(name="Règle sur les texte d'offres")
        factories.OfferValidationSubRuleFactory(
            validationRule=offer_validation_rule,
            model=models.OfferValidationModel.OFFER,
            attribute=models.OfferValidationAttribute.TEXT,
            operator=models.OfferValidationRuleOperator.CONTAINS_EXACTLY,
            comparated={"comparated": ["dark"]},
        )
        assert api.set_offer_status_based_on_fraud_criteria(offer) == expected_status

    @pytest.mark.parametrize(
        "offer_kwargs, expected_status",
        [
            ({"collectiveOffer__name": "Come to the dark side, we have cookies"}, models.OfferValidationStatus.PENDING),
            (
                {"collectiveOffer__description": "Come to the dark side, we have cookies"},
                models.OfferValidationStatus.PENDING,
            ),
            ({"priceDetail": "Come to the dark side, we have cookies"}, models.OfferValidationStatus.PENDING),
            ({}, models.OfferValidationStatus.APPROVED),
        ],
    )
    def test_collective_offer_validation_rule_with_offer_text(self, offer_kwargs, expected_status):
        stock = educational_factories.CollectiveStockFactory(**offer_kwargs)
        offer_validation_rule = factories.OfferValidationRuleFactory(name="Règle sur les texte d'offres")
        factories.OfferValidationSubRuleFactory(
            validationRule=offer_validation_rule,
            model=models.OfferValidationModel.COLLECTIVE_OFFER,
            attribute=models.OfferValidationAttribute.TEXT,
            operator=models.OfferValidationRuleOperator.CONTAINS_EXACTLY,
            comparated={"comparated": ["dark"]},
        )
        assert api.set_offer_status_based_on_fraud_criteria(stock.collectiveOffer) == expected_status

    @pytest.mark.parametrize(
        "offer_kwargs, expected_status",
        [
            ({"name": "Come to the dark side, we have cookies"}, models.OfferValidationStatus.PENDING),
            ({"description": "Come to the dark side, we have cookies"}, models.OfferValidationStatus.PENDING),
            ({"priceDetail": "Come to the dark side, we have cookies"}, models.OfferValidationStatus.PENDING),
            ({}, models.OfferValidationStatus.APPROVED),
        ],
    )
    def test_collective_offer_template_validation_rule_with_offer_text(self, offer_kwargs, expected_status):
        offer = educational_factories.CollectiveOfferTemplateFactory(**offer_kwargs)
        offer_validation_rule = factories.OfferValidationRuleFactory(name="Règle sur les texte d'offres")
        factories.OfferValidationSubRuleFactory(
            validationRule=offer_validation_rule,
            model=models.OfferValidationModel.COLLECTIVE_OFFER_TEMPLATE,
            attribute=models.OfferValidationAttribute.TEXT,
            operator=models.OfferValidationRuleOperator.CONTAINS_EXACTLY,
            comparated={"comparated": ["dark"]},
        )
        assert api.set_offer_status_based_on_fraud_criteria(offer) == expected_status

    def test_offer_validation_with_multiple_rules(self):
        offer = factories.OfferFactory(name="offer with a verboten name")
        factories.StockFactory(offer=offer, price=15)
        offer_name_rule = factories.OfferValidationRuleFactory(name="Règle sur le nom des offres")
        factories.OfferValidationSubRuleFactory(
            validationRule=offer_name_rule,
            model=models.OfferValidationModel.OFFER,
            attribute=models.OfferValidationAttribute.NAME,
            operator=models.OfferValidationRuleOperator.CONTAINS_EXACTLY,
            comparated={"comparated": ["interdit", "forbidden", "verboten"]},
        )
        offer_price_rule = factories.OfferValidationRuleFactory(name="Règle sur le prix des offres")
        factories.OfferValidationSubRuleFactory(
            validationRule=offer_price_rule,
            model=models.OfferValidationModel.OFFER,
            attribute=models.OfferValidationAttribute.MAX_PRICE,
            operator=models.OfferValidationRuleOperator.GREATER_THAN,
            comparated={"comparated": 100},
        )

        assert api.set_offer_status_based_on_fraud_criteria(offer) == models.OfferValidationStatus.PENDING
        assert db.session.query(models.ValidationRuleOfferLink).count() == 1

    def test_offer_validation_rule_with_multiple_sub_rules(self):
        offer_to_approve = factories.OfferFactory(name="offer with a verboten name")
        factories.StockFactory(offer=offer_to_approve, price=15)
        offer_to_flag = factories.OfferFactory(name="offer with a verboten name")
        factories.StockFactory(offer=offer_to_flag, price=150)
        offer_name_and_price_rule = factories.OfferValidationRuleFactory(name="Règle sur le nom des offres")
        factories.OfferValidationSubRuleFactory(
            validationRule=offer_name_and_price_rule,
            model=models.OfferValidationModel.OFFER,
            attribute=models.OfferValidationAttribute.NAME,
            operator=models.OfferValidationRuleOperator.CONTAINS_EXACTLY,
            comparated={"comparated": ["interdit", "forbidden", "verboten"]},
        )
        factories.OfferValidationSubRuleFactory(
            validationRule=offer_name_and_price_rule,
            model=models.OfferValidationModel.OFFER,
            attribute=models.OfferValidationAttribute.MAX_PRICE,
            operator=models.OfferValidationRuleOperator.GREATER_THAN,
            comparated={"comparated": 100},
        )
        assert api.set_offer_status_based_on_fraud_criteria(offer_to_approve) == models.OfferValidationStatus.APPROVED
        assert api.set_offer_status_based_on_fraud_criteria(offer_to_flag) == models.OfferValidationStatus.PENDING
        assert db.session.query(models.ValidationRuleOfferLink).count() == 1

    def test_offer_validation_rule_with_unrelated_rules(self):
        offer_to_flag = factories.OfferFactory(name="offer with a verboten name")
        factories.StockFactory(offer=offer_to_flag, price=15)
        collective_offer_to_flag = educational_factories.CollectiveOfferFactory(name="offer with a nice name")
        educational_factories.CollectiveStockFactory(collectiveOffer=collective_offer_to_flag, price=150)
        offer_name_rule = factories.OfferValidationRuleFactory(name="Règle sur le nom des offres")
        collective_offer_price_rule = factories.OfferValidationRuleFactory(
            name="Règle sur le prix des offres collectives"
        )
        factories.OfferValidationSubRuleFactory(
            validationRule=offer_name_rule,
            model=models.OfferValidationModel.OFFER,
            attribute=models.OfferValidationAttribute.NAME,
            operator=models.OfferValidationRuleOperator.CONTAINS_EXACTLY,
            comparated={"comparated": ["interdit", "forbidden", "verboten"]},
        )
        factories.OfferValidationSubRuleFactory(
            validationRule=collective_offer_price_rule,
            model=models.OfferValidationModel.COLLECTIVE_STOCK,
            attribute=models.OfferValidationAttribute.PRICE,
            operator=models.OfferValidationRuleOperator.GREATER_THAN,
            comparated={"comparated": 100},
        )
        assert api.set_offer_status_based_on_fraud_criteria(offer_to_flag) == models.OfferValidationStatus.PENDING
        assert (
            api.set_offer_status_based_on_fraud_criteria(collective_offer_to_flag)
            == models.OfferValidationStatus.PENDING
        )
        assert db.session.query(models.ValidationRuleOfferLink).count() == 1
        assert db.session.query(educational_models.ValidationRuleCollectiveOfferLink).count() == 1

    def test_offer_validation_with_description_rule_and_offer_without_description(self):
        offer = factories.OfferFactory(description=None)
        factories.OfferValidationSubRuleFactory(
            model=models.OfferValidationModel.OFFER,
            attribute=models.OfferValidationAttribute.DESCRIPTION,
            operator=models.OfferValidationRuleOperator.CONTAINS,
            comparated={"comparated": ["forbidden", "words"]},
        )

        assert api.set_offer_status_based_on_fraud_criteria(offer) == models.OfferValidationStatus.APPROVED

    def test_validation_rule_offer_link_data(self):
        offer_to_flag = factories.OfferFactory(name="Sapristi, un lot interdit")
        factories.StockFactory(offer=offer_to_flag, price=300)
        offer_to_flag_too = factories.OfferFactory(name="Les complots de la théorie")
        factories.StockFactory(offer=offer_to_flag_too, price=30)
        offer_name_rule = factories.OfferValidationRuleFactory(name="Règle sur le nom des offres")
        factories.OfferValidationSubRuleFactory(
            validationRule=offer_name_rule,
            model=models.OfferValidationModel.OFFER,
            attribute=models.OfferValidationAttribute.NAME,
            operator=models.OfferValidationRuleOperator.CONTAINS,
            comparated={"comparated": ["bon", "lot"]},
        )
        offer_price_rule = factories.OfferValidationRuleFactory(name="Règle sur le prix des offres")
        factories.OfferValidationSubRuleFactory(
            validationRule=offer_price_rule,
            model=models.OfferValidationModel.OFFER,
            attribute=models.OfferValidationAttribute.MAX_PRICE,
            operator=models.OfferValidationRuleOperator.GREATER_THAN,
            comparated={"comparated": 250},
        )

        assert api.set_offer_status_based_on_fraud_criteria(offer_to_flag) == models.OfferValidationStatus.PENDING
        assert api.set_offer_status_based_on_fraud_criteria(offer_to_flag_too) == models.OfferValidationStatus.PENDING

        assert db.session.query(models.ValidationRuleOfferLink).filter_by(offerId=offer_to_flag.id).count() == 2
        assert db.session.query(models.ValidationRuleOfferLink).filter_by(offerId=offer_to_flag_too.id).count() == 1
        assert db.session.query(models.ValidationRuleOfferLink).filter_by(ruleId=offer_name_rule.id).count() == 2
        assert db.session.query(models.ValidationRuleOfferLink).filter_by(ruleId=offer_price_rule.id).count() == 1
        assert db.session.query(models.ValidationRuleOfferLink).count() == 3

    @pytest.mark.parametrize(
        "formats, excluded_formats, expected_status",
        [
            (
                [EacFormat.VISITE_LIBRE],
                [EacFormat.CONCERT, EacFormat.REPRESENTATION],
                models.OfferValidationStatus.PENDING,
            ),
            (
                [
                    EacFormat.CONCERT,
                    EacFormat.VISITE_LIBRE,
                    EacFormat.REPRESENTATION,
                ],
                [EacFormat.CONCERT, EacFormat.VISITE_LIBRE],
                models.OfferValidationStatus.APPROVED,
            ),
        ],
    )
    def test_offer_validation_with_not_intersects(self, formats, excluded_formats, expected_status):
        collective_offer = educational_factories.CollectiveOfferFactory(formats=formats)
        factories.OfferValidationSubRuleFactory(
            model=models.OfferValidationModel.COLLECTIVE_OFFER,
            attribute=models.OfferValidationAttribute.FORMATS,
            operator=models.OfferValidationRuleOperator.NOT_INTERSECTS,
            comparated={"comparated": [fmt.name for fmt in excluded_formats]},
        )

        assert api.set_offer_status_based_on_fraud_criteria(collective_offer) == expected_status

    @pytest.mark.parametrize(
        "formats, excluded_formats, expected_status",
        [
            (
                [EacFormat.VISITE_LIBRE],
                [EacFormat.CONCERT],
                models.OfferValidationStatus.APPROVED,
            ),
            (
                [EacFormat.CONCERT, EacFormat.VISITE_LIBRE],
                [EacFormat.CONCERT],
                models.OfferValidationStatus.PENDING,
            ),
        ],
    )
    def test_offer_validation_with_intersects(self, formats, excluded_formats, expected_status):
        collective_offer = educational_factories.CollectiveOfferFactory(formats=formats)
        factories.OfferValidationSubRuleFactory(
            model=models.OfferValidationModel.COLLECTIVE_OFFER,
            attribute=models.OfferValidationAttribute.FORMATS,
            operator=models.OfferValidationRuleOperator.INTERSECTS,
            comparated={"comparated": [fmt.name for fmt in excluded_formats]},
        )

        assert api.set_offer_status_based_on_fraud_criteria(collective_offer) == expected_status

    def test_offer_validation_when_offerer_whitelisted(self, offer_matching_one_validation_rule):
        offerers_factories.WhitelistedOffererConfidenceRuleFactory(
            offerer=offer_matching_one_validation_rule.venue.managingOfferer
        )

        status = api.set_offer_status_based_on_fraud_criteria(offer_matching_one_validation_rule)

        assert status == models.OfferValidationStatus.APPROVED
        assert db.session.query(models.ValidationRuleOfferLink).count() == 0

    def test_offer_validation_when_offerer_on_manual_review(self):
        collective_offer = educational_factories.CollectiveOfferFactory()
        offerers_factories.ManualReviewOffererConfidenceRuleFactory(offerer=collective_offer.venue.managingOfferer)

        status = api.set_offer_status_based_on_fraud_criteria(collective_offer)

        assert status == models.OfferValidationStatus.PENDING
        assert db.session.query(models.ValidationRuleOfferLink).count() == 0

    def test_offer_validation_when_offerer_on_manual_review_with_rules(self, offer_matching_one_validation_rule):
        offerers_factories.ManualReviewOffererConfidenceRuleFactory(
            offerer=offer_matching_one_validation_rule.venue.managingOfferer
        )

        status = api.set_offer_status_based_on_fraud_criteria(offer_matching_one_validation_rule)

        assert status == models.OfferValidationStatus.PENDING
        assert db.session.query(models.ValidationRuleOfferLink).count() == 1

    def test_offer_validation_when_venue_whitelisted(self, offer_matching_one_validation_rule):
        offerers_factories.WhitelistedVenueConfidenceRuleFactory(venue=offer_matching_one_validation_rule.venue)

        status = api.set_offer_status_based_on_fraud_criteria(offer_matching_one_validation_rule)

        assert status == models.OfferValidationStatus.APPROVED
        assert db.session.query(models.ValidationRuleOfferLink).count() == 0

    def test_offer_validation_when_venue_on_manual_review(self):
        collective_offer = educational_factories.CollectiveOfferFactory()
        offerers_factories.ManualReviewVenueConfidenceRuleFactory(venue=collective_offer.venue)

        status = api.set_offer_status_based_on_fraud_criteria(collective_offer)

        assert status == models.OfferValidationStatus.PENDING
        assert db.session.query(models.ValidationRuleOfferLink).count() == 0


@pytest.mark.usefixtures("db_session")
class UnindexExpiredOffersTest:
    @time_machine.travel("2020-01-05 10:00:00")
    @pytest.mark.settings(ALGOLIA_DELETING_OFFERS_CHUNK_SIZE=2)
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

    @time_machine.travel("2020-01-05 10:00:00")
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
class WhitelistExistingProductTest:
    @pytest.mark.settings(TITELIVE_EPAGINE_API_USERNAME="test@example.com", TITELIVE_EPAGINE_API_PASSWORD="qwerty123")
    def test_modify_product_if_existing_and_not_gcu_compatible(self, requests_mock, settings):
        ean = "9782070455379"
        requests_mock.post(
            f"{settings.TITELIVE_EPAGINE_API_AUTH_URL}/login/test@example.com/token",
            json={"token": "XYZ"},
        )
        requests_mock.get(
            f"{settings.TITELIVE_EPAGINE_API_URL}/ean/{ean}",
            json=fixtures.BOOK_BY_SINGLE_EAN_FIXTURE,
        )

        product = factories.ProductFactory(
            name="test",
            subcategoryId=subcategories.LIVRE_PAPIER.id,
            ean=ean,
            extraData={
                "author": "author",
                "prix_livre": "66.6€",
                "collection": "collection",
                "comic_series": "comic_series",
                "date_parution": "date_parution",
                "distributeur": "distributeur",
                "editeur": "editeur",
                "num_in_collection": "test",
                "schoolbook": False,
                "csr_id": "csr_id",
                "gtl_id": "gtl_id",
                "code_clil": "code_clil",
                "rayon": "test",
            },
            gcuCompatibilityType=models.GcuCompatibilityType.PROVIDER_INCOMPATIBLE,
        )

        api.whitelist_product(ean)

        assert db.session.query(models.Product).one() == product
        assert product.isGcuCompatible
        oeuvre = fixtures.BOOK_BY_SINGLE_EAN_FIXTURE["oeuvre"]
        article = oeuvre["article"][0]
        assert product.name == oeuvre["titre"]
        assert product.description == article["resume"]
        assert product.extraData["author"] == oeuvre["auteurs"]
        assert product.extraData["prix_livre"] == article["prix"]
        assert product.extraData["collection"] == article["collection"]
        assert product.extraData["comic_series"] == article["serie"]
        assert product.extraData["date_parution"] == "2014-10-02 00:00:00"
        assert product.extraData["distributeur"] == article["distributeur"]
        assert product.extraData["editeur"] == article["editeur"]
        assert product.extraData["num_in_collection"] == article["collection_no"]
        assert product.extraData["schoolbook"] == (article["scolaire"] == "1")
        assert product.extraData["csr_id"] == "0105"
        assert product.extraData["gtl_id"] == "01050000"
        assert product.extraData["code_clil"] == "3665"

    @pytest.mark.settings(TITELIVE_EPAGINE_API_USERNAME="test@example.com", TITELIVE_EPAGINE_API_PASSWORD="qwerty123")
    def test_create_product_if_not_existing(self, requests_mock, settings):
        ean = "9782070455379"
        requests_mock.post(
            f"{settings.TITELIVE_EPAGINE_API_AUTH_URL}/login/test@example.com/token",
            json={"token": "XYZ"},
        )
        requests_mock.get(
            f"{settings.TITELIVE_EPAGINE_API_URL}/ean/{ean}",
            json=fixtures.BOOK_BY_SINGLE_EAN_FIXTURE,
        )
        assert not db.session.query(models.Product).filter(models.Product.ean == ean).one_or_none()

        api.whitelist_product(ean)

        product = db.session.query(models.Product).filter(models.Product.ean == ean).one()
        assert product
        assert len(product.extraData["gtl_id"]) == 8


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

        api.batch_delete_draft_offers(db.session.query(models.Offer).filter(models.Offer.id.in_(offer_ids)))

        assert db.session.query(criteria_models.OfferCriterion).count() == 0
        assert db.session.query(models.Mediation).count() == 0
        assert db.session.query(models.Stock).count() == 0
        assert db.session.query(models.Offer).count() == 0
        assert db.session.query(models.ActivationCode).count() == 0


@pytest.mark.usefixtures("db_session")
class DeleteStocksTest:
    def test_delete_batch_stocks(self, client):
        stocks = factories.StockFactory.create_batch(3)
        api.batch_delete_stocks(stocks, author_id=None, user_connect_as=None)
        assert all(stock.isSoftDeleted for stock in stocks)

    @time_machine.travel("2020-10-15 00:00:00")
    def test_delete_batch_stocks_filtered_by_date(self):
        # Given
        beginning_datetime = datetime.utcnow()
        offer = factories.OfferFactory()
        stock_1 = factories.EventStockFactory(offer=offer, beginningDatetime=beginning_datetime)
        stock_2 = factories.EventStockFactory(offer=offer, beginningDatetime=beginning_datetime + timedelta(days=1))

        # When
        stocks = offers_repository.get_filtered_stocks(
            offer=offer,
            date=beginning_datetime.date(),
            venue=offer.venue,
        ).all()
        api.batch_delete_stocks(stocks, author_id=None, user_connect_as=None)

        # Then
        assert stock_1.isSoftDeleted
        assert not stock_2.isSoftDeleted

    @time_machine.travel("2020-10-15 00:00:00")
    def test_delete_batch_stocks_filtered_by_time(self):
        # Given
        beginning_datetime = datetime.utcnow()
        offer = factories.OfferFactory()
        stock_1 = factories.EventStockFactory(offer=offer, beginningDatetime=beginning_datetime + timedelta(seconds=15))
        stock_2 = factories.EventStockFactory(offer=offer, beginningDatetime=beginning_datetime + timedelta(hours=1))

        # When
        stocks = offers_repository.get_filtered_stocks(
            offer=offer,
            time=beginning_datetime.time(),
            venue=offer.venue,
        ).all()
        api.batch_delete_stocks(stocks, author_id=None, user_connect_as=None)

        # Then
        assert stock_1.isSoftDeleted
        assert not stock_2.isSoftDeleted

    def test_delete_batch_stocks_filtered_by_price_cat(self):
        # Given

        offer = factories.OfferFactory()
        price_category_1 = api.create_price_category(offer=offer, label="p_cat_1", price=10)
        price_category_2 = api.create_price_category(offer=offer, label="p_cat_2", price=20)
        stock_1 = factories.EventStockFactory(offer=offer, priceCategory=price_category_1)
        stock_2 = factories.EventStockFactory(offer=offer, priceCategory=price_category_2)
        stock_3 = factories.EventStockFactory(offer=offer, priceCategory=price_category_1)

        # When
        stocks = offers_repository.get_filtered_stocks(
            offer=offer,
            price_category_id=stock_1.priceCategoryId,
            venue=offer.venue,
        ).all()
        api.batch_delete_stocks(stocks, author_id=None, user_connect_as=None)

        # Then
        assert stock_1.isSoftDeleted
        assert not stock_2.isSoftDeleted
        assert stock_3.isSoftDeleted


class FormatExtraDataTest:
    def test_format_extra_data(self):
        extra_data = {
            "musicType": "-1",  # applicable and filled
            "musicSubType": "100",  # applicable and filled
            "gtl_id": "19000000",  # applicable and filled in deserializer
            "other": "value",  # not applicable field
            "performer": "",  # applicable but empty
        }
        assert api._format_extra_data(subcategories.FESTIVAL_MUSIQUE.id, extra_data) == {
            "musicType": "-1",
            "musicSubType": "100",
            "gtl_id": "19000000",
        }


@pytest.mark.usefixtures("db_session")
class ApproveProductAndRejectedOffersTest:
    @mock.patch("pcapi.core.search.async_index_offer_ids")
    def test_should_no_approve_product_and_offers_with_unknown_product(self, mocked_async_index_offer_ids):
        # Given
        ean = "ean-de-test"

        # When
        with pytest.raises(ProductNotFound):
            api.approves_provider_product_and_rejected_offers(ean)

        # Then
        mocked_async_index_offer_ids.assert_not_called()

    @mock.patch("pcapi.core.search.async_index_offer_ids")
    def test_should_approve_product_and_offers_with_no_offers(self, mocked_async_index_offer_ids):
        # Given
        provider = providers_factories.PublicApiProviderFactory()
        ean = Fake.ean13()
        factories.ThingProductFactory(
            subcategoryId=subcategories.LIVRE_PAPIER.id,
            ean=ean,
            lastProvider=provider,
            gcuCompatibilityType=models.GcuCompatibilityType.PROVIDER_INCOMPATIBLE,
        )

        # When
        api.approves_provider_product_and_rejected_offers(ean)

        # Then
        product = db.session.query(models.Product).filter(models.Product.ean == ean).one()
        assert product.isGcuCompatible

        mocked_async_index_offer_ids.assert_not_called()

    @mock.patch("pcapi.core.search.async_index_offer_ids")
    def test_should_approve_product_and_offers_on_approved_offers(self, mocked_async_index_offer_ids):
        # Given
        provider = providers_factories.PublicApiProviderFactory()
        ean = Fake.ean13()
        product = factories.ThingProductFactory(
            subcategoryId=subcategories.LIVRE_PAPIER.id,
            ean=ean,
            lastProvider=provider,
            gcuCompatibilityType=models.GcuCompatibilityType.PROVIDER_INCOMPATIBLE,
        )

        factories.OfferFactory(product=product)
        factories.OfferFactory(product=product)

        # When
        api.approves_provider_product_and_rejected_offers(ean)

        # Then
        product = db.session.query(models.Product).filter(models.Product.ean == ean).one()
        assert product.isGcuCompatible

        assert (
            db.session.query(models.Offer).filter(models.Offer.validation == OfferValidationStatus.APPROVED).count()
            == 2
        )

        mocked_async_index_offer_ids.assert_not_called()

    @mock.patch("pcapi.core.search.async_index_offer_ids")
    def test_should_approve_product_and_offers_with_one_rejected_offer_for_gcu_inappropriate(
        self, mocked_async_index_offer_ids
    ):
        # Given
        provider = providers_factories.PublicApiProviderFactory()
        ean = Fake.ean13()
        product = factories.ThingProductFactory(
            subcategoryId=subcategories.LIVRE_PAPIER.id,
            ean=ean,
            lastProvider=provider,
            gcuCompatibilityType=models.GcuCompatibilityType.PROVIDER_INCOMPATIBLE,
        )

        offert_to_approve = factories.OfferFactory(
            product=product,
            validation=OfferValidationStatus.REJECTED,
            lastValidationType=OfferValidationType.CGU_INCOMPATIBLE_PRODUCT,
        )
        factories.OfferFactory(product=product, lastValidationType=OfferValidationType.MANUAL)

        # When
        api.approves_provider_product_and_rejected_offers(ean)

        # Then
        product = db.session.query(models.Product).filter(models.Product.ean == ean).one()
        assert product.isGcuCompatible

        assert (
            db.session.query(models.Offer).filter(models.Offer.validation == OfferValidationStatus.APPROVED).count()
            == 2
        )
        assert (
            db.session.query(models.Offer)
            .filter(
                models.Offer.id == offert_to_approve.id, models.Offer.lastValidationType == OfferValidationType.AUTO
            )
            .count()
            == 1
        )

        mocked_async_index_offer_ids.assert_called()
        assert set(mocked_async_index_offer_ids.call_args[0][0]) == set([offert_to_approve.id])

    @mock.patch("pcapi.core.search.async_index_offer_ids")
    def test_should_approve_product_and_offers_with_one_offer_manually_rejected(self, mocked_async_index_offer_ids):
        # Given
        provider = providers_factories.PublicApiProviderFactory()
        ean = Fake.ean13()
        product = factories.ThingProductFactory(
            subcategoryId=subcategories.LIVRE_PAPIER.id,
            ean=ean,
            lastProvider=provider,
            gcuCompatibilityType=models.GcuCompatibilityType.PROVIDER_INCOMPATIBLE,
        )

        factories.OfferFactory(
            product=product, validation=OfferValidationStatus.REJECTED, lastValidationType=OfferValidationType.MANUAL
        )

        # When
        api.approves_provider_product_and_rejected_offers(ean)

        # Then
        product = db.session.query(models.Product).filter(models.Product.ean == ean).one()
        assert product.isGcuCompatible

        assert (
            db.session.query(models.Offer).filter(models.Offer.validation == OfferValidationStatus.REJECTED).count()
            == 1
        )
        mocked_async_index_offer_ids.assert_not_called()

    @mock.patch("pcapi.core.search.async_index_offer_ids")
    def test_should_approve_product_and_offers_with_one_offer_auto_rejected(self, mocked_async_index_offer_ids):
        # Given
        provider = providers_factories.PublicApiProviderFactory()
        ean = Fake.ean13()
        product = factories.ThingProductFactory(
            subcategoryId=subcategories.LIVRE_PAPIER.id,
            ean=ean,
            lastProvider=provider,
            gcuCompatibilityType=models.GcuCompatibilityType.PROVIDER_INCOMPATIBLE,
        )

        factories.OfferFactory(
            product=product, validation=OfferValidationStatus.REJECTED, lastValidationType=OfferValidationType.AUTO
        )

        # When
        api.approves_provider_product_and_rejected_offers(ean)

        # Then
        product = db.session.query(models.Product).filter(models.Product.ean == ean).one()
        assert product.isGcuCompatible

        assert (
            db.session.query(models.Offer).filter(models.Offer.validation == OfferValidationStatus.REJECTED).count()
            == 1
        )
        mocked_async_index_offer_ids.assert_not_called()

    def test_should_approve_product_and_offers_with_update_exception(self):
        # Given
        provider = providers_factories.PublicApiProviderFactory()
        ean = Fake.ean13()
        product = factories.ThingProductFactory(
            subcategoryId=subcategories.LIVRE_PAPIER.id,
            ean=ean,
            lastProvider=provider,
            gcuCompatibilityType=models.GcuCompatibilityType.PROVIDER_INCOMPATIBLE,
        )

        factories.OfferFactory(
            product=product,
            validation=OfferValidationStatus.REJECTED,
            lastValidationType=OfferValidationType.CGU_INCOMPATIBLE_PRODUCT,
        )

        # When
        with pytest.raises(NotUpdateProductOrOffers):
            with mock.patch("pcapi.models.db.session.commit", side_effect=Exception):
                api.approves_provider_product_and_rejected_offers(ean)


@pytest.mark.usefixtures("db_session")
class GetStocksStatsTest:
    def test_get_stocks_stats(self):
        # Given
        offer = factories.OfferFactory()
        now = datetime.utcnow()
        factories.StockFactory(offer=offer, quantity=10, dnBookedQuantity=5, beginningDatetime=now)
        factories.StockFactory(offer=offer, quantity=20, dnBookedQuantity=5, beginningDatetime=now + timedelta(hours=1))

        # When
        stats = api.get_stocks_stats(offer_id=offer.id)

        # Then
        assert stats.stock_count == 2
        assert stats.remaining_quantity == 20
        assert stats.oldest_stock == now
        assert stats.newest_stock == now + timedelta(hours=1)

    def test_get_stocks_stats_with_soft_deleted_stock(self):
        # Given
        offer = factories.OfferFactory()
        factories.StockFactory(offer=offer, quantity=None, dnBookedQuantity=5, isSoftDeleted=True)
        factories.StockFactory(offer=offer, quantity=10, dnBookedQuantity=5)

        # When
        stats = api.get_stocks_stats(offer_id=offer.id)

        # Then
        assert stats.stock_count == 1
        assert stats.remaining_quantity == 5

    def test_get_stocks_stats_when_stock_has_unlimited_quantity(self):
        # Given
        offer = factories.OfferFactory()
        factories.StockFactory(offer=offer, quantity=None)

        # When
        stats = api.get_stocks_stats(offer_id=offer.id)

        # Then
        assert stats.stock_count == 1
        assert stats.remaining_quantity == None

    def test_get_stocks_stats_with_another_stock_has_unlimited_quantity(self):
        # Given
        offer = factories.OfferFactory()
        now = datetime.utcnow()
        factories.StockFactory(
            beginningDatetime=now + timedelta(hours=1),
            quantity=20,
            dnBookedQuantity=10,
            offer=offer,
        )
        factories.StockFactory(
            beginningDatetime=now + timedelta(hours=2),
            quantity=30,
            dnBookedQuantity=25,
            offer=offer,
        )
        # Stock on another offer
        factories.StockFactory(
            beginningDatetime=now + timedelta(hours=2),
            quantity=None,
            dnBookedQuantity=25,
        )

        # When
        stats = api.get_stocks_stats(offer_id=offer.id)

        # Then
        assert stats.stock_count == 2
        assert stats.remaining_quantity == 15

    def test_get_stocks_stats_when_one_stock_has_unlimited_quantity(self):
        # Given
        offer = factories.OfferFactory()
        price_category_1 = api.create_price_category(offer=offer, label="1", price=10)
        price_category_2 = api.create_price_category(offer=offer, label="2", price=20)

        factories.StockFactory(offer=offer, priceCategory=price_category_1, quantity=None)
        factories.StockFactory(offer=offer, priceCategory=price_category_2, quantity=5)

        # When
        stats = api.get_stocks_stats(offer_id=offer.id)

        # Then
        assert stats.stock_count == 2
        assert stats.remaining_quantity == None

    def test_get_stocks_stats_with_no_stock(self):
        # Given
        offer = factories.OfferFactory()

        # When
        with pytest.raises(api_errors.ApiErrors) as error:
            api.get_stocks_stats(offer_id=offer.id)

        # Then
        assert error.value.errors == {
            "global": ["L'offre en cours de création ne possède aucun Stock"],
        }


@pytest.mark.usefixtures("db_session")
class UpdateUsedStockPriceTest:
    def test_update_used_stock_price_should_raise_on_non_event(self):
        booking = bookings_factories.UsedBookingFactory()

        with pytest.raises(ValueError):
            api.update_used_stock_price(booking.stock, new_price=booking.stock.price - 1)

    def test_update_used_stock_price_should_delete_pricings_on_used_event(self):
        offer = factories.OfferFactory(subcategoryId=subcategories.CONFERENCE.id)
        venue = offer.venue
        stock_to_edit = factories.StockFactory(
            offer=offer,
            price=decimal.Decimal("123.45"),
        )
        booking_to_edit = bookings_factories.UsedBookingFactory(
            stock=stock_to_edit,
            amount=decimal.Decimal("123.45"),
        )
        stock_untouched = factories.StockFactory(
            offer=offer,
            price=decimal.Decimal("123.45"),
        )
        booking_untouched = bookings_factories.UsedBookingFactory(
            stock=stock_untouched,
            amount=decimal.Decimal("123.45"),
        )
        cancelled_event = finance_factories.FinanceEventFactory(
            booking=booking_to_edit, venue=venue, pricingPoint=venue
        )
        cancelled_pricing = finance_factories.PricingFactory(
            event=cancelled_event,
            pricingPoint=venue,
        )
        later_booking = bookings_factories.UsedBookingFactory(
            stock__offer__venue=venue,
            stock__offer__subcategoryId=subcategories.CONFERENCE.id,
            stock__beginningDatetime=datetime.utcnow() + timedelta(hours=2),
        )
        later_event = finance_factories.FinanceEventFactory(
            booking=later_booking,
            venue=venue,
            pricingPoint=venue,
            pricingOrderingDate=later_booking.stock.beginningDatetime,
        )
        later_pricing = finance_factories.PricingFactory(
            event=later_event,
            pricingPoint=venue,
        )
        later_pricing_id = later_pricing.id

        api.update_used_stock_price(booking_to_edit.stock, 50.1)

        db.session.refresh(booking_to_edit)
        db.session.refresh(booking_untouched)
        db.session.refresh(stock_to_edit)
        db.session.refresh(stock_untouched)
        db.session.refresh(cancelled_event)
        db.session.refresh(later_event)

        assert stock_untouched.price == decimal.Decimal("123.45")
        assert booking_untouched.amount == decimal.Decimal("123.45")
        assert cancelled_event.status == finance_models.FinanceEventStatus.READY
        assert cancelled_pricing.status == finance_models.PricingStatus.CANCELLED

        assert stock_to_edit.price == decimal.Decimal("50.1")
        assert booking_to_edit.amount == decimal.Decimal("50.1")
        assert later_event.status == finance_models.FinanceEventStatus.READY
        assert db.session.query(finance_models.Pricing).filter_by(id=later_pricing_id).count() == 0

    def test_update_used_stock_price_should_update_confirmed_events(self):
        stock_to_edit = factories.StockFactory(
            offer__subcategoryId=subcategories.CONFERENCE.id,
            price=decimal.Decimal("123.45"),
        )
        booking_to_edit = bookings_factories.BookingFactory(
            status=bookings_models.BookingStatus.CONFIRMED,
            stock=stock_to_edit,
            amount=decimal.Decimal("123.45"),
        )

        api.update_used_stock_price(booking_to_edit.stock, 50.1)

        db.session.refresh(booking_to_edit)
        db.session.refresh(stock_to_edit)

        assert stock_to_edit.price == decimal.Decimal("50.1")
        assert booking_to_edit.amount == decimal.Decimal("50.1")


@pytest.mark.usefixtures("db_session")
class UpsertMovieProductFromProviderTest:
    @classmethod
    def setup_class(cls):
        cls.allocine_provider = get_allocine_products_provider()
        cls.allocine_stocks_provider = providers_repository.get_provider_by_local_class("AllocineStocks")
        cls.boost_provider = providers_repository.get_provider_by_local_class("BoostStocks")

    def setup_method(self):
        db.session.query(models.Product).delete()

    def teardown_method(self):
        db.session.query(models.Product).delete()

    def _get_movie(self, allocine_id: str | None = None, visa: str | None = None):
        return models.Movie(
            title="Mon film",
            duration=90,
            description="description de Mon film",
            poster_url=None,
            allocine_id=allocine_id,
            visa=visa,
            extra_data={"allocineId": int(allocine_id) if allocine_id else None, "visa": visa},
        )

    def test_creates_allocine_product_without_visa_if_does_not_exist(self):
        movie = self._get_movie(allocine_id="12345")

        product = api.upsert_movie_product_from_provider(movie, self.allocine_provider, "idAllocine")

        assert product.extraData["allocineId"] == 12345
        assert product.extraData.get("visa") is None

    def test_creates_allocine_product_even_if_the_title_is_too_long(self):
        movie = self._get_movie(allocine_id="12345")
        movie.title = "Chroniques fidèles survenues au siècle dernier à l’hôpital psychiatrique Blida-Joinville, au temps où le Docteur Frantz Fanon était chef de la cinquième division entre 1953 et 1956"

        product = api.upsert_movie_product_from_provider(movie, self.allocine_provider, "idAllocine")

        assert product.extraData["allocineId"] == 12345
        assert (
            product.name
            == "Chroniques fidèles survenues au siècle dernier à l’hôpital psychiatrique Blida-Joinville, au temps où le Docteur Frantz Fanon était chef de…"
        )

    def test_do_nothing_if_no_allocine_id_and_no_visa(self):
        movie = self._get_movie(allocine_id=None, visa=None)

        with assert_num_queries(0):
            product = api.upsert_movie_product_from_provider(movie, self.allocine_provider, "idAllocine")

        assert product is None

    def test_does_not_create_product_if_exists(self):
        product = factories.ProductFactory(extraData={"allocineId": 12345})
        movie = self._get_movie(allocine_id="12345")

        new_product = api.upsert_movie_product_from_provider(movie, self.allocine_provider, "idAllocine")

        assert product.id == new_product.id

    def test_updates_product_if_exists(self):
        allocine_id = 12345
        visa = "67890"

        allocine_movie = factories.ProductFactory(extraData={"allocineId": allocine_id})
        random_movie_with_visa = factories.ProductFactory(extraData={"visa": visa})

        movie = self._get_movie(allocine_id=str(allocine_id), visa=visa)
        offer = factories.OfferFactory(product=random_movie_with_visa)

        # When
        api.upsert_movie_product_from_provider(movie, self.allocine_provider, "idAllocine")

        # Then
        assert allocine_movie.lastProvider.id == self.allocine_provider.id

        db.session.refresh(offer)
        assert offer.productId == allocine_movie.id

    def test_updates_product_if_exists_and_title_is_too_ling(self):
        allocine_id = 12345
        visa = "67890"

        allocine_movie = factories.ProductFactory(extraData={"allocineId": allocine_id})
        random_movie_with_visa = factories.ProductFactory(extraData={"visa": visa})

        movie = self._get_movie(allocine_id=str(allocine_id), visa=visa)
        movie.title = "Chroniques fidèles survenues au siècle dernier à l’hôpital psychiatrique Blida-Joinville, au temps où le Docteur Frantz Fanon était chef de la cinquième division entre 1953 et 1956"
        offer = factories.OfferFactory(product=random_movie_with_visa)

        product = api.upsert_movie_product_from_provider(movie, self.allocine_provider, "idAllocine")

        assert allocine_movie.lastProvider.id == self.allocine_provider.id

        db.session.refresh(offer)
        assert offer.productId == allocine_movie.id
        assert (
            product.name
            == "Chroniques fidèles survenues au siècle dernier à l’hôpital psychiatrique Blida-Joinville, au temps où le Docteur Frantz Fanon était chef de…"
        )

    def test_does_not_update_allocine_product_from_non_allocine_synchro(self):
        product = factories.ProductFactory(lastProviderId=self.allocine_provider.id, extraData={"allocineId": 12345})
        movie = self._get_movie(allocine_id="12345")

        # When
        api.upsert_movie_product_from_provider(movie, self.boost_provider, "idBoost")

        # Then
        assert product.lastProvider.id == self.allocine_provider.id

    def test_updates_allocine_product_from_allocine_stocks_synchro(self):
        product = factories.ProductFactory(lastProviderId=self.allocine_provider.id, extraData={"allocineId": 12345})
        movie = self._get_movie(allocine_id="12345")

        api.upsert_movie_product_from_provider(movie, self.allocine_stocks_provider, "idAllocineStocks")

        assert product.lastProvider.id == self.allocine_stocks_provider.id

    def test_updates_product_from_same_synchro(self):
        product = factories.ProductFactory(lastProviderId=self.boost_provider.id, extraData={"allocineId": 12345})
        movie = self._get_movie(allocine_id="12345")

        api.upsert_movie_product_from_provider(movie, self.boost_provider, "idBoost2")

        assert product.lastProvider.id == self.boost_provider.id

    def test_updates_allocine_id_when_updates_product_by_visa(self):
        product = factories.ProductFactory(lastProviderId=self.boost_provider.id, extraData={"visa": "54321"})
        movie = self._get_movie(allocine_id="12345", visa="54321")

        api.upsert_movie_product_from_provider(movie, self.allocine_stocks_provider, "idAllocine")

        assert product.extraData["allocineId"] == 12345

    def test_updates_visa_when_updating_with_visa_provided(self):
        product = factories.ProductFactory(
            lastProviderId=self.boost_provider.id,
            extraData={"allocineId": 12345, "visa": "54321"},
        )
        movie = self._get_movie(allocine_id="12345", visa="54322")

        api.upsert_movie_product_from_provider(movie, self.allocine_stocks_provider, "idAllocine")

        assert product.extraData["allocineId"] == 12345
        assert product.extraData["visa"] == "54322"

    def test_keep_visa_when_updating_with_no_visa_provided(self):
        product = factories.ProductFactory(
            lastProviderId=self.boost_provider.id,
            extraData={"allocineId": 12345, "visa": "54321"},
        )
        movie = self._get_movie(allocine_id="12345", visa=None)

        api.upsert_movie_product_from_provider(movie, self.allocine_stocks_provider, "idAllocine")

        assert product.extraData["allocineId"] == 12345
        assert product.extraData["visa"] == "54321"

    def test_does_not_update_data_when_provided_data_is_none(self):
        product = factories.ProductFactory(
            lastProviderId=self.boost_provider.id,
            extraData={"allocineId": 12345, "title": "Mon vieux film"},
        )
        movie = self._get_movie(allocine_id="12345", visa=None)
        movie.extra_data = None

        api.upsert_movie_product_from_provider(movie, self.allocine_stocks_provider, "idAllocine")

        assert product.extraData == {"allocineId": 12345, "title": "Mon vieux film"}

    def test_handles_coexisting_incomplete_movies(self, caplog):
        boost_product = factories.ProductFactory(
            lastProviderId=self.boost_provider.id,
            name="MON VIEUX FILM D'EPOQUE",
            description="Vieux film des années 50",
            extraData={"visa": "54321", "title": "MON VIEUX FILM D'EPOQUE"},
        )
        boost_product_id = boost_product.id
        allocine_product = factories.ProductFactory(
            lastProviderId=self.boost_provider.id,
            name="Mon vieux film d'époque",
            description="Vieux film des années cinquante",
            extraData={"allocineId": 12345, "title": "Mon vieux film d'époque"},
        )
        offer = factories.OfferFactory(product=boost_product)
        reaction = reactions_factories.ReactionFactory(product=boost_product)
        factories.ProductMediationFactory(product=boost_product)
        movie = self._get_movie(allocine_id="12345", visa="54321")

        with caplog.at_level(logging.INFO):
            api.upsert_movie_product_from_provider(movie, self.allocine_stocks_provider, "idAllocineProducts")

        assert caplog.records[0].extra == {
            "allocine_id": "12345",
            "visa": "54321",
            "provider_id": self.allocine_stocks_provider.id,
            "deleted": {
                "name": "MON VIEUX FILM D'EPOQUE",
                "description": "Vieux film des années 50",
            },
            "kept": {
                "name": "Mon vieux film d'époque",
                "description": "Vieux film des années cinquante",
            },
        }
        assert offer.product == allocine_product
        assert reaction.product == allocine_product
        assert (
            db.session.query(models.ProductMediation)
            .filter(models.ProductMediation.productId == boost_product_id)
            .count()
            == 0
        )
        assert db.session.query(models.Product).filter(models.Product.id == boost_product_id).count() == 0
        assert allocine_product.extraData == {"allocineId": 12345, "visa": "54321", "title": "Mon vieux film d'époque"}

    def test_should_not_merge_when_visa_and_allocineId_sent_by_provider_are_incoherent(self, caplog):
        movie = models.Movie(
            allocine_id="1000006691",  # allocine_id pointing to "L'Accident de piano"
            visa="164773",  # pointing to "F1 Film"
            title="F1 : LE FILM",
            description="Sonny Hayes était le prodige de la F1 des années 90 jusqu’à son terrible accident. Trente ans plus tard, devenu un pilote indépendant, il est contacté par Ruben Cervantes, patron d’une écurie en faillite qui le convainc de revenir pour sauver l’équipe et prouver qu’il est toujours le meilleur. Aux côtés de Joshua Pearce, diamant brut prêt à devenir le numéro 1, Sonny réalise vite qu'en F1, son coéquipier est aussi son plus grand rival, que le danger est partout et qu'il risque de tout perdre.",
            duration=None,
            poster_url=None,
            extra_data={},
        )

        f1_movie_product = factories.ProductFactory(
            lastProviderId=self.boost_provider.id,
            name="F1® LE FILM",
            description="Sonny Hayes était le prodige de la F1 des années 90 jusqu’à son terrible accident. Trente ans plus tard, devenu un pilote indépendant, il est contacté par Ruben Cervantes, patron d’une écurie en faillite qui le convainc de revenir pour sauver l’équipe et prouver qu’il est toujours le meilleur. Aux côtés de Joshua Pearce, diamant brut prêt à devenir le numéro 1, Sonny réalise vite qu'en F1, son coéquipier est aussi son plus grand rival, que le danger est partout et qu'il risque de tout perdre.",
            extraData={"visa": "164773", "title": "F1® LE FILM"},
        )
        accident_piano_movie_product = factories.ProductFactory(
            lastProviderId=self.allocine_provider.id,
            name="L'Accident de piano",
            description="Magalie est une star du web hors sol et sans morale qui gagne des fortunes en postant des contenus choc sur les réseaux. Après un accident grave survenu sur le tournage d'une de ses vidéos, Magalie s'isole à la montagne avec Patrick, son assistant personnel, pour faire un break. Une journaliste détenant une information sensible commence à lui faire du chantage… La vie de Magalie bascule.",
            extraData={"allocineId": 1000006691, "title": "L'Accident de piano"},
        )
        accident_piano_movie_product_id = accident_piano_movie_product.id

        with caplog.at_level(logging.WARNING):
            product = api.upsert_movie_product_from_provider(movie, self.boost_provider, "idBoostProducts")

        assert caplog.records[0].message == "Provider sent incoherent visa and allocineId"
        assert caplog.records[0].extra == {
            "movie": {
                "allocine_id": "1000006691",
                "visa": "164773",
                "title": "F1 : LE FILM",
                "description": "Sonny Hayes était le prodige de la F1 des années 90 jusqu’à son terrible accident. Trente ans plus tard, devenu un pilote indépendant, il est contacté par Ruben Cervantes, patron d’une écurie en faillite qui le convainc de revenir pour sauver l’équipe et prouver qu’il est toujours le meilleur. Aux côtés de Joshua Pearce, diamant brut prêt à devenir le numéro 1, Sonny réalise vite qu'en F1, son coéquipier est aussi son plus grand rival, que le danger est partout et qu'il risque de tout perdre.",
            },
            "provider_id": self.boost_provider.id,
            "product_id": f1_movie_product.id,
        }
        assert product == f1_movie_product
        assert db.session.query(models.Product).filter_by(id=accident_piano_movie_product_id).one_or_none()


@pytest.mark.usefixtures("db_session")
class CreatePriceCategoryTest:
    def test_should_create_price_category(self):
        offer = factories.EventOfferFactory()
        # without idAtProvider
        price_category_1 = api.create_price_category(offer, "Carré or où ça douille sa maman", decimal.Decimal("70.5"))
        assert price_category_1.price == 70.5
        assert price_category_1.label == "Carré or où ça douille sa maman"
        assert price_category_1.idAtProvider == None

        # with idAtProvider
        price_category_2 = api.create_price_category(
            offer, "Fosse pour le bas peuple", decimal.Decimal("0.5"), "categorie_pour_les_prolos"
        )
        assert price_category_2.price == 0.5
        assert price_category_2.label == "Fosse pour le bas peuple"
        assert price_category_2.idAtProvider == "categorie_pour_les_prolos"

    def test_should_raise_because_id_at_provider_already_exists_for_this_offer(self):
        offer = factories.EventOfferFactory()
        factories.PriceCategoryFactory(offer=offer, idAtProvider="aHÇaVaBugguer")

        with pytest.raises(exceptions.OfferException) as error:
            api.create_price_category(offer, "Carré d'as", decimal.Decimal("70.5"), id_at_provider="aHÇaVaBugguer")

        assert error.value.errors["idAtProvider"] == [
            "`aHÇaVaBugguer` is already taken by another offer price category"
        ]


@pytest.mark.usefixtures("db_session")
class EditPriceCategoryTest:
    def test_should_update_price_category(self):
        price_category = factories.PriceCategoryFactory()
        updated_price_category = api.edit_price_category(
            price_category.offer,
            price_category,
            label="Carré Diamant, à part en vendant un rein vous n'y accéderez jamais",
            id_at_provider="price_category_ou_il_faut_khalass",
        )
        assert updated_price_category.label == "Carré Diamant, à part en vendant un rein vous n'y accéderez jamais"
        assert updated_price_category.idAtProvider == "price_category_ou_il_faut_khalass"

    def test_should_delete_id_at_provider(self):
        factories.PriceCategoryFactory()
        price_category = factories.PriceCategoryFactory(idAtProvider="id_qui_n_en_a_plus_pour_longtemps")
        updated_price_category = api.edit_price_category(
            price_category.offer,
            price_category,
            id_at_provider=None,
        )
        assert updated_price_category.idAtProvider == None

    def test_should_raise_because_id_at_provider_already_taken(self):
        offer = factories.EventOfferFactory()
        failing_id = "aHÇaVaBugguer"
        factories.PriceCategoryFactory(offer=offer, idAtProvider=failing_id)
        price_category = factories.PriceCategoryFactory(offer=offer)

        with pytest.raises(exceptions.OfferException) as error:
            api.edit_price_category(
                price_category.offer,
                price_category,
                id_at_provider=failing_id,
            )

        assert error.value.errors["idAtProvider"] == [
            "`aHÇaVaBugguer` is already taken by another offer price category"
        ]


@pytest.mark.usefixtures("db_session")
@pytest.mark.features(VENUE_REGULARIZATION=True)
class MoveOfferTest:
    def test_move_physical_offer_without_pricing_point(self):
        """Moving an offer from a venue without pricing point to another venue
        without pricing point should work and the offer's location should not change."""
        offer = factories.OfferFactory()
        new_venue = offerers_factories.VenueFactory(managingOfferer=offer.venue.managingOfferer)
        assert offer.venue.current_pricing_point is None
        assert new_venue.current_pricing_point is None
        assert offer.offererAddressId == offer.venue.offererAddressId
        assert offer.offererAddressId != new_venue.offererAddressId

        initial_offerer_address_id = offer.offererAddressId
        initial_address_id = offer.offererAddress.addressId
        initial_oa_label = offer.venue.common_name
        api.move_offer(offer, new_venue)

        db.session.refresh(offer)
        assert offer.venue == new_venue
        # The address remains the same but OA is different and uses the source venue's common name
        assert offer.offererAddressId != initial_offerer_address_id
        assert offer.offererAddress.addressId == initial_address_id
        assert offer.offererAddress.label == initial_oa_label

    def test_move_physical_offer_without_pricing_point_to_venue_with_pricing_point(self):
        """Moving an offer from a venue without pricing point to another venue
        with pricing point should not work"""
        offer = factories.OfferFactory()
        new_venue = offerers_factories.VenueFactory(managingOfferer=offer.venue.managingOfferer)
        offerers_factories.VenuePricingPointLinkFactory(
            venue=new_venue,
            pricingPoint=new_venue,
            timespan=[datetime.utcnow() - timedelta(days=1), None],
        )
        assert offer.venue.current_pricing_point is None
        assert new_venue.current_pricing_point is not None

        with pytest.raises(exceptions.NoDestinationVenue):
            api.move_offer(offer, new_venue)

        db.session.refresh(offer)
        assert offer.venue != new_venue

    def test_move_physical_offer_that_has_a_dedicated_oa(self):
        """Moving an offer that has a custom location from a venue to another venue
        should not change its location."""
        offerer = offerers_factories.OffererFactory()
        offer_oa = offerers_factories.OffererAddressFactory(offerer=offerer, label="Custom location")
        venue_oa = offerers_factories.OffererAddressFactory(offerer=offerer)
        offer = factories.OfferFactory(
            venue__managingOfferer=offerer, offererAddress=offer_oa, venue__offererAddress=venue_oa
        )
        new_venue = offerers_factories.VenueFactory(managingOfferer=offerer)
        assert new_venue.current_pricing_point is None
        assert offer.offererAddressId != new_venue.offererAddressId
        initial_offerer_address_id = offer_oa.id

        api.move_offer(offer, new_venue)

        db.session.refresh(offer)
        assert offer.venue == new_venue
        assert offer.offererAddressId == initial_offerer_address_id

    def test_move_physical_offer_with_different_pricing_point(self):
        """Moving a physical offer from a venue to another venue without
        a pricing point should raise an exception"""
        offer = factories.OfferFactory()
        new_venue = offerers_factories.VenueFactory(managingOfferer=offer.venue.managingOfferer)
        offerers_factories.VenuePricingPointLinkFactory(
            venue=offer.venue,
            pricingPoint=offerers_factories.VenueFactory(managingOfferer=offer.venue.managingOfferer),
            timespan=[datetime.utcnow() - timedelta(days=7), None],
        )
        offerers_factories.VenuePricingPointLinkFactory(
            venue=new_venue,
            pricingPoint=offerers_factories.VenueFactory(managingOfferer=new_venue.managingOfferer),
            timespan=[datetime.utcnow() - timedelta(days=7), None],
        )
        assert offer.venue.current_pricing_point != new_venue.current_pricing_point

        with pytest.raises(exceptions.NoDestinationVenue):
            api.move_offer(offer, new_venue)

        db.session.refresh(offer)
        assert offer.venue != new_venue

    def test_move_event_offer_with_past_stocks(self):
        """Moving an event offer with past stocks should be possible"""
        today = date.today()
        yesterday = today - timedelta(days=1)
        tomorow = today + timedelta(days=1)

        offer = factories.EventOfferFactory()
        factories.EventStockFactory(
            offer=offer,
            quantity=10,
            beginningDatetime=yesterday,
        )
        factories.EventStockFactory(
            offer=offer,
            quantity=10,
            beginningDatetime=today,
        )
        factories.EventStockFactory(
            offer=offer,
            quantity=10,
            beginningDatetime=tomorow,
        )
        new_venue = offerers_factories.VenueFactory(managingOfferer=offer.venue.managingOfferer)
        api.move_offer(offer, new_venue)

        db.session.refresh(offer)
        assert offer.venue == new_venue

    def create_offer_by_state(self, venue, state):
        offer = None
        if state == OfferValidationStatus.DRAFT:
            offer = factories.OfferFactory(venue=venue, validation=OfferValidationStatus.DRAFT)
        if state == OfferStatus.ACTIVE:
            offer = factories.OfferFactory(venue=venue)
        if state == OfferValidationStatus.PENDING:
            offer = factories.OfferFactory(venue=venue, validation=OfferValidationStatus.PENDING)
        if state == OfferValidationStatus.REJECTED:
            offer = factories.OfferFactory(venue=venue, validation=OfferValidationStatus.REJECTED)
        if state == OfferStatus.INACTIVE:
            offer = factories.OfferFactory(venue=venue, publicationDatetime=None)
        if state == OfferStatus.SOLD_OUT:
            offer = factories.OfferFactory(venue=venue)
            stock = factories.StockFactory(offer=offer, quantity=1)
            bookings_factories.UsedBookingFactory(stock=stock)
        if state == OfferStatus.EXPIRED:
            offer = factories.EventOfferFactory(venue=venue)
            factories.EventStockFactory(
                offer=offer, quantity=10, beginningDatetime=datetime.utcnow() - timedelta(days=30)
            )
        if state == bookings_models.BookingStatus.CONFIRMED:
            offer = factories.OfferFactory(venue=venue)
            stock = factories.StockFactory(offer=offer, quantity=2)
            bookings_factories.BookingFactory(stock=stock)
        if state == bookings_models.BookingStatus.CANCELLED:
            offer = factories.OfferFactory(venue=venue)
            stock = factories.StockFactory(offer=offer, quantity=2)
            bookings_factories.CancelledBookingFactory(stock=stock)
        if state == bookings_models.BookingStatus.REIMBURSED:
            offer = factories.OfferFactory(venue=venue)
            stock = factories.StockFactory(offer=offer, quantity=2)
            bookings_factories.ReimbursedBookingFactory(stock=stock)
            # TODO(xordoquy): might add finance stuffs too
        if state == bookings_models.BookingStatus.USED:
            offer = factories.OfferFactory(venue=venue)
            stock = factories.StockFactory(offer=offer, quantity=2)
            bookings_factories.UsedBookingFactory(stock=stock)
        return offer

    @pytest.mark.parametrize(
        "state",
        [
            OfferValidationStatus.DRAFT,
            OfferStatus.ACTIVE,
            OfferValidationStatus.PENDING,
            OfferValidationStatus.REJECTED,
            OfferStatus.INACTIVE,
            OfferStatus.SOLD_OUT,
            OfferStatus.EXPIRED,
            bookings_models.BookingStatus.CONFIRMED,
            bookings_models.BookingStatus.CANCELLED,
            bookings_models.BookingStatus.USED,
            bookings_models.BookingStatus.REIMBURSED,
        ],
    )
    def test_move_offer_with_different_statuses(self, state):
        venue = offerers_factories.VenueFactory()
        new_venue = offerers_factories.VenueFactory(managingOfferer=venue.managingOfferer)
        offer = self.create_offer_by_state(venue, state)

        api.move_offer(offer, new_venue)

        db.session.refresh(offer)
        assert offer.venue == new_venue
        if state in (
            OfferStatus.SOLD_OUT,
            bookings_models.BookingStatus.CONFIRMED,
            bookings_models.BookingStatus.CANCELLED,
            bookings_models.BookingStatus.USED,
            bookings_models.BookingStatus.REIMBURSED,
        ):
            assert db.session.query(bookings_models.Booking).count() == 1
            assert db.session.query(bookings_models.Booking).all()[0].venue == new_venue

    def test_move_offer_with_booking_with_pending_finance_event(self):
        new_venue = offerers_factories.VenueFactory(pricing_point="self")
        venue = offerers_factories.VenueFactory(pricing_point=new_venue, managingOfferer=new_venue.managingOfferer)

        offer = factories.OfferFactory(venue=venue)
        stock = factories.StockFactory(offer=offer, quantity=2)
        booking = bookings_factories.UsedBookingFactory(stock=stock)
        finance_factories.FinanceEventFactory(
            booking=booking,
            pricingOrderingDate=stock.beginningDatetime,
            status=finance_models.FinanceEventStatus.PENDING,
            venue=venue,
            pricingPoint=None,
        )

        api.move_offer(offer, new_venue)

        db.session.refresh(offer)
        assert offer.venue == new_venue
        assert db.session.query(bookings_models.Booking).count() == 1
        assert db.session.query(bookings_models.Booking).all()[0].venue == new_venue
        assert db.session.query(finance_models.FinanceEvent).all()[0].venue == venue

    def test_move_physical_offer_with_booking_with_pricing_with_different_pricing_point(self):
        """Moving an offer from a venue with a pricing point A
        and a booking with a pricing with a different pricing point B
        to another venue with the same pricing point A should work."""
        offer = factories.OfferFactory()
        new_venue = offerers_factories.VenueFactory(managingOfferer=offer.venue.managingOfferer)
        offerers_factories.VenuePricingPointLinkFactory(
            venue=offer.venue, pricingPoint=new_venue, timespan=[datetime.utcnow() - timedelta(days=7), None]
        )
        offerers_factories.VenuePricingPointLinkFactory(
            venue=new_venue, pricingPoint=new_venue, timespan=[datetime.utcnow() - timedelta(days=7), None]
        )
        stock = factories.StockFactory(offer=offer, quantity=2)
        booking = bookings_factories.UsedBookingFactory(stock=stock)
        finance_factories.PricingFactory(
            pricingPoint=offerers_factories.VenueFactory(managingOfferer=new_venue.managingOfferer), booking=booking
        )

        api.move_offer(offer, new_venue)

        db.session.refresh(offer)
        assert offer.venue == new_venue


@pytest.mark.usefixtures("db_session")
class DeleteOffersStocksRelatedObjectsTest:
    def test_delete_one_offer_with_one_stock_without_any_related_objects(self):
        stock = factories.StockFactory()

        api.delete_offers_stocks_related_objects([stock.offerId])
        self.assert_no_more_stocks_related_objects()

    def test_delete_one_offer_with_many_stocks_with_many_related_objects(self):
        offer = factories.OfferFactory()
        for stock in factories.StockFactory.create_batch(3, offer=offer):
            factories.ActivationCodeFactory.create_batch(2, stock=stock)

        api.delete_offers_stocks_related_objects([offer.id])
        self.assert_no_more_stocks_related_objects()

    def test_delete_many_offers_with_many_stock_with_many_related_objects(self):
        offers = factories.OfferFactory.create_batch(3)
        for offer in offers:
            for stock in factories.StockFactory.create_batch(3, offer=offer):
                factories.ActivationCodeFactory.create_batch(2, stock=stock)

        api.delete_offers_stocks_related_objects([offer.id for offer in offers])
        self.assert_no_more_stocks_related_objects()

    @pytest.mark.parametrize("offer_ids", ([0], []))
    def test_delete_unknown_offers_does_not_delete_anything(self, offer_ids):
        stock = factories.StockFactory()
        factories.ActivationCodeFactory(stock=stock)

        api.delete_offers_stocks_related_objects(offer_ids)
        assert db.session.query(models.Stock).count() == 1
        assert db.session.query(models.ActivationCode).count() == 1

    def assert_no_more_stocks_related_objects(self):
        db.session.commit()
        assert db.session.query(models.ActivationCode).count() == 0


@pytest.mark.usefixtures("db_session")
class DeleteOffersRelatedObjectsTest:
    def test_delete_one_offer_without_any_related_objects_works_but_does_nothing(self):
        offer = factories.OfferFactory()
        api.delete_offers_related_objects([offer.id])

    def test_one_offers_related_objects_are_deleted(self):
        offer = self.build_offer_with_related_objects()

        api.delete_offers_related_objects([offer.id])
        self.assert_offer_related_objects_are_deleted([offer.id])

    def test_only_objects_related_to_target_offer_are_deleted(self):
        target_offer = self.build_offer_with_related_objects()
        other_offer = self.build_offer_with_related_objects()

        api.delete_offers_related_objects([target_offer.id])

        self.assert_offer_related_objects_are_deleted([target_offer.id])
        self.assert_offer_related_objects_have_not_been_deleted([other_offer.id])

    @pytest.mark.parametrize("offer_ids", ([0], []))
    def test_nothing_deleted_if_offer_ids_are_unknown(self, offer_ids):
        api.delete_offers_related_objects(offer_ids)
        self.assert_offer_related_objects_are_deleted(offer_ids)

    def build_offer_with_related_objects(self):
        offer = factories.OfferFactory()
        factories.StockFactory.create_batch(2, offer=offer)
        users_factories.FavoriteFactory(offer=offer)
        factories.MediationFactory.create_batch(2, offer=offer)
        factories.OfferReportFactory(offer=offer)
        criteria_factories.OfferCriterionFactory(offerId=offer.id, criterionId=criteria_factories.CriterionFactory().id)

        return offer

    def assert_offer_related_objects_are_deleted(self, offer_ids):
        db.session.commit()

        # not efficient but will be fine for testing
        for offer_id in offer_ids:
            assert db.session.query(models.Stock).filter_by(offerId=offer_id).count() == 0
            assert db.session.query(users_models.Favorite).filter_by(offerId=offer_id).count() == 0
            assert db.session.query(models.Mediation).filter_by(offerId=offer_id).count() == 0
            assert db.session.query(models.OfferReport).filter_by(offerId=offer_id).count() == 0

    def assert_offer_related_objects_have_not_been_deleted(self, offer_ids):
        db.session.commit()

        # not efficient but will be fine for testing
        for offer_id in offer_ids:
            assert db.session.query(models.Stock).filter_by(offerId=offer_id).count() > 0
            assert db.session.query(users_models.Favorite).filter_by(offerId=offer_id).count() > 0
            assert db.session.query(criteria_models.OfferCriterion).filter_by(offerId=offer_id).count() > 0
            assert db.session.query(models.Mediation).filter_by(offerId=offer_id).count() > 0
            assert db.session.query(models.OfferReport).filter_by(offerId=offer_id).count() > 0


def assert_offers_have_been_completely_cleaned(offer_ids):
    # should not be necessary but testing sessions sometimes comes with
    # unexpected behaviour.
    db.session.commit()

    assert db.session.query(models.Offer).filter(models.Offer.id.in_(offer_ids)).count() == 0

    # not efficient but will be fine for testing
    for offer_id in offer_ids:
        assert offer_id not in search_testing.search_store["offers"]

        assert db.session.query(finance_models.CustomReimbursementRule).filter_by(offerId=offer_id).count() == 0
        assert db.session.query(users_models.Favorite).filter_by(offerId=offer_id).count() == 0
        assert db.session.query(models.HeadlineOffer).filter_by(offerId=offer_id).count() == 0
        assert db.session.query(models.Mediation).filter_by(offerId=offer_id).count() == 0
        assert db.session.query(chronicles_models.OfferChronicle).filter_by(offerId=offer_id).count() == 0
        assert db.session.query(models.OfferCompliance).filter_by(offerId=offer_id).count() == 0
        assert db.session.query(criteria_models.OfferCriterion).filter_by(offerId=offer_id).count() == 0
        assert db.session.query(models.OfferReport).filter_by(offerId=offer_id).count() == 0
        assert db.session.query(models.PriceCategory).filter_by(offerId=offer_id).count() == 0
        assert db.session.query(reactions_models.Reaction).filter_by(offerId=offer_id).count() == 0
        assert db.session.query(models.Stock).filter_by(offerId=offer_id).count() == 0
        assert db.session.query(models.ValidationRuleOfferLink).filter_by(offerId=offer_id).count() == 0


@pytest.mark.usefixtures("db_session")
class DeleteOffersAndAllRelatedObjectsTest:
    def test_one_unindexed_offer_without_related_object_is_deleted(self):
        offer_id = factories.OfferFactory().id
        api.delete_offers_and_all_related_objects([offer_id])
        assert_offers_have_been_completely_cleaned([offer_id])

    def test_many_offers_are_deleted_with_their_related_objects_and_unindexed(self):
        offers = self.build_many_eligible_for_search_offers_with_related_objects()
        offer_ids = [offer.id for offer in offers]

        api.delete_offers_and_all_related_objects(offer_ids)
        assert_offers_have_been_completely_cleaned(offer_ids)

    def test_only_targetted_offers_are_deleted_with_their_related_objects_and_unindexed(self):
        offers = self.build_many_eligible_for_search_offers_with_related_objects()
        offer_ids = [offer.id for offer in offers]

        other_offer_id = factories.StockFactory().offerId
        search.reindex_offer_ids([other_offer_id])

        api.delete_offers_and_all_related_objects(offer_ids)
        assert_offers_have_been_completely_cleaned(offer_ids)

        assert db.session.get(models.Offer, other_offer_id) is not None
        assert db.session.query(models.Stock).filter_by(offerId=other_offer_id).one()
        assert other_offer_id in search_testing.search_store["offers"]

    def test_offer_is_deleted_and_unindexed_with_chunk_size_set(self):
        offers = self.build_many_eligible_for_search_offers_with_related_objects()
        offer_ids = [offer.id for offer in offers]

        api.delete_offers_and_all_related_objects(offer_ids, offer_chunk_size=1)
        assert_offers_have_been_completely_cleaned(offer_ids)

    @pytest.mark.parametrize(
        "error", [sa.exc.IntegrityError("bad query", "<params>", "<orig>"), Exception("bad query")]
    )
    @mock.patch("pcapi.core.offers.api._fix_price_categories", return_value=None)  # avoid interference with test
    def test_function_does_not_stop_if_error_occurs_at_a_random_round(self, mock_fix_price_categories, caplog, error):
        offers = self.build_many_eligible_for_search_offers_with_related_objects()
        offer_ids = [offer.id for offer in offers]

        with mock.patch("pcapi.core.offers.api.logger.info") as logger_mock:
            with caplog.at_level(logging.ERROR):
                logger_mock.side_effect = [error] + [None for _ in range(len(offers) - 1)]

                api.delete_offers_and_all_related_objects(offer_ids, offer_chunk_size=1)

                assert len(caplog.records[0].extra["ids"]) == 1
                assert caplog.records[0].extra["ids"][0] in offer_ids
                assert "bad query" in caplog.records[0].extra["error"]

        # all offers except one (because of the error) should have been deleted
        assert db.session.query(models.Offer).count() == 1

    def build_many_eligible_for_search_offers_with_related_objects(self, count=3):
        offers = []
        for _ in range(count):
            offer = factories.StockFactory().offer
            offers.append(offer)
            search.reindex_offer_ids([offer.id])

            factories.StockFactory.create_batch(2, offer=offer)
            users_factories.FavoriteFactory(offer=offer)
        return offers

    def test_delete_offer_with_price_categories(self, caplog):
        venue = offerers_factories.VenueFactory()
        shared_label = factories.PriceCategoryLabelFactory(label="Tarif partagé", venue=venue)
        unique_label = factories.PriceCategoryLabelFactory(label="Tarif non partagé", venue=venue)
        offer = factories.EventOfferFactory(venue=venue)
        category_1 = factories.PriceCategoryFactory(offer=offer, priceCategoryLabel=shared_label, price=10)
        category_2 = factories.PriceCategoryFactory(offer=offer, priceCategoryLabel=unique_label, price=20)
        factories.EventStockFactory(offer=offer, priceCategory=category_1)
        factories.EventStockFactory(offer=offer, priceCategory=category_2)
        other_offer = factories.EventOfferFactory(venue=venue)
        other_category = factories.PriceCategoryFactory(offer=other_offer, priceCategoryLabel=shared_label, price=30)
        other_stock = factories.EventStockFactory(offer=other_offer, priceCategory=other_category)
        stock_with_wrong_category = factories.EventStockFactory(offer__venue=venue, priceCategory=category_1)

        offer_id = offer.id

        with caplog.at_level(logging.ERROR):
            api.delete_offers_and_all_related_objects([offer_id])

        assert caplog.records == []

        assert_offers_have_been_completely_cleaned([offer_id])

        assert len(other_offer.priceCategories) == 1
        assert other_offer.priceCategories[0].priceCategoryLabel.label == "Tarif partagé"
        assert other_stock.priceCategory == other_category
        assert stock_with_wrong_category.priceCategory == category_1
        assert category_1.offer == stock_with_wrong_category.offer


@pytest.mark.usefixtures("db_session")
class DeleteUnbookableUnusedOldOffersTest:
    @property
    def a_year_ago(self):
        return date.today() - timedelta(days=366)

    def test_old_offer_without_any_stock_id_deleted(self):
        offer_id = factories.OfferFactory(dateCreated=self.a_year_ago, dateUpdated=self.a_year_ago).id

        api.delete_unbookable_unbooked_old_offers()
        assert_offers_have_been_completely_cleaned([offer_id])

    def test_old_offer_with_unbookable_stocks_and_more_is_deleted(self):
        offer = factories.OfferFactory(dateCreated=self.a_year_ago, dateUpdated=self.a_year_ago)
        offer_id = offer.id

        factories.StockFactory.create_batch(2, offer=offer, isSoftDeleted=True)
        users_factories.FavoriteFactory(offer=offer)
        factories.OfferReportFactory(offer=offer)

        api.delete_unbookable_unbooked_old_offers()
        assert_offers_have_been_completely_cleaned([offer_id])

    def test_recent_or_still_bookable_old_offers_are_ignored(self):
        offer = factories.OfferFactory(dateCreated=self.a_year_ago, dateUpdated=self.a_year_ago)
        offer_id = offer.id

        # old but still bookable -> should be ignored
        old_bookable_offer = factories.StockFactory(
            offer__dateCreated=self.a_year_ago,
            offer__dateUpdated=self.a_year_ago,
        ).offer
        # recent -> should be ignored (event if it is not bookable, eg. it has no stocks)
        recent_offer = factories.OfferFactory()

        api.delete_unbookable_unbooked_old_offers()
        db.session.flush()
        assert_offers_have_been_completely_cleaned([offer_id])

        assert db.session.get(models.Offer, old_bookable_offer.id) is not None
        assert db.session.get(models.Offer, recent_offer.id) is not None


@pytest.mark.usefixtures("db_session")
class ProductCountsConsistencyTest:
    def test_chronicles_count(self) -> None:
        product_1 = factories.ProductFactory()
        product_2 = factories.ProductFactory()
        chronicles_factories.ChronicleFactory.create(products=[product_1, product_2])

        product_1.chroniclesCount = 0

        assert api.fetch_inconsistent_products() == {product_1.id}

    def test_headlines_count(self) -> None:
        product_1 = factories.ProductFactory()
        product_2 = factories.ProductFactory()
        factories.HeadlineOfferFactory(offer__product=product_1)
        factories.HeadlineOfferFactory(offer__product=product_2)

        product_1.headlinesCount = 0

        assert api.fetch_inconsistent_products() == {product_1.id}

    def test_likes_count(self) -> None:
        product = factories.ProductFactory()
        reactions_factories.ReactionFactory(product=product, reactionType=reactions_models.ReactionTypeEnum.LIKE)

        product.likesCount = 0

        assert api.fetch_inconsistent_products() == {product.id}

    def test_ids_are_unique(self) -> None:
        product = factories.ProductFactory()
        chronicles_factories.ChronicleFactory.create(products=[product])
        reactions_factories.ReactionFactory(product=product, reactionType=reactions_models.ReactionTypeEnum.LIKE)

        product.chroniclesCount = 0
        product.likesCount = 0

        assert api.fetch_inconsistent_products() == {product.id}
