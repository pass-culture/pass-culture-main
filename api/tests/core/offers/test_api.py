import copy
from datetime import date
from datetime import datetime
from datetime import timedelta
import decimal
import logging
import os
import pathlib
import re
from unittest import mock
from unittest.mock import patch

import pytest
import time_machine

from pcapi import settings
from pcapi.core import search
import pcapi.core.bookings.factories as bookings_factories
import pcapi.core.bookings.models as bookings_models
from pcapi.core.categories import subcategories_v2 as subcategories
import pcapi.core.criteria.factories as criteria_factories
import pcapi.core.criteria.models as criteria_models
import pcapi.core.educational.factories as educational_factories
import pcapi.core.educational.models as educational_models
from pcapi.core.external_bookings.boost import constants as boost_constants
import pcapi.core.finance.factories as finance_factories
import pcapi.core.finance.models as finance_models
import pcapi.core.mails.testing as mails_testing
import pcapi.core.offerers.factories as offerers_factories
import pcapi.core.offerers.models as offerers_models
from pcapi.core.offers import api
from pcapi.core.offers import exceptions
from pcapi.core.offers import factories
from pcapi.core.offers import models
from pcapi.core.offers import repository as offers_repository
from pcapi.core.offers import schemas
from pcapi.core.offers.exceptions import NotUpdateProductOrOffers
from pcapi.core.offers.exceptions import ProductNotFound
from pcapi.core.providers.allocine import get_allocine_products_provider
import pcapi.core.providers.factories as providers_factories
import pcapi.core.providers.repository as providers_repository
from pcapi.core.testing import assert_num_queries
from pcapi.core.testing import override_features
from pcapi.core.testing import override_settings
import pcapi.core.users.factories as users_factories
import pcapi.core.users.models as users_models
from pcapi.models import api_errors
from pcapi.models import db
from pcapi.models.offer_mixin import OfferValidationStatus
from pcapi.models.offer_mixin import OfferValidationType
from pcapi.notifications.push import testing as push_testing
from pcapi.utils.human_ids import humanize

import tests
from tests import conftest
from tests.connectors.cgr import soap_definitions
from tests.connectors.titelive import fixtures
from tests.local_providers.cinema_providers.boost import fixtures as boost_fixtures
from tests.local_providers.cinema_providers.cds import fixtures as cds_fixtures
import tests.local_providers.cinema_providers.cgr.fixtures as cgr_fixtures


IMAGES_DIR = pathlib.Path(tests.__path__[0]) / "files"


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
        offer = factories.ThingOfferFactory(lastProvider=providers_factories.TiteLiveThingsProviderFactory())

        # When
        with pytest.raises(api_errors.ApiErrors) as error:
            api.create_stock(offer=offer, price=10, quantity=1)

        # Then
        assert error.value.errors == {"global": ["Les offres importées ne sont pas modifiables"]}

    @mock.patch("pcapi.core.mails.transactional.send_first_venue_approved_offer_email_to_pro")
    def test_create_stock_for_non_approved_offer_fails(self, mocked_send_first_venue_approved_offer_email_to_pro):
        offer = factories.ThingOfferFactory(validation=models.OfferValidationStatus.PENDING)

        with pytest.raises(exceptions.RejectedOrPendingOfferNotEditable) as error:
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

    def test_edit_stock_id_at_provider(self):
        # Given
        existing_stock = factories.StockFactory(price=10, idAtProviders="I have a secret")

        # When
        edited_stock, _ = api.edit_stock(stock=existing_stock, id_at_provider="I'm Batman !!!")

        # Then
        assert edited_stock == models.Stock.query.filter_by(id=existing_stock.id).first()
        assert edited_stock.idAtProviders == "I'm Batman !!!"

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
        allocine_provider = providers_factories.AllocineProviderFactory()
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
        edited_stock = models.Stock.query.filter_by(id=existing_stock.id).first()
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
            offer__extraData={"ean": "1234567890123"},
        )

        # When
        api.edit_stock(stock=existing_stock, price=new_price, quantity=existing_stock.quantity)

        # Then
        edited_stock = models.Stock.query.filter_by(id=existing_stock.id).first()
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
        edited_stock = models.Stock.query.filter_by(id=existing_stock.id).first()
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
    def test_edit_stock_of_non_approved_offer_fails(
        self,
        mocked_send_first_venue_approved_offer_email_to_pro,
    ):
        offer = factories.ThingOfferFactory(validation=models.OfferValidationStatus.PENDING)
        existing_stock = factories.StockFactory(offer=offer, price=10)

        with pytest.raises(exceptions.RejectedOrPendingOfferNotEditable) as error:
            api.edit_stock(stock=existing_stock, price=5, quantity=7)

        assert error.value.errors == {
            "global": ["Les offres refusées ou en attente de validation ne sont pas modifiables"]
        }
        existing_stock = models.Stock.query.one()
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
            "old_price": 10,
            "stock_price": 12.5,
            "stock_dnBookedQuantity": 0,
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
            "old_quantity": 15,
            "stock_quantity": 7,
            "stock_dnBookedQuantity": 0,
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
    def test_delete_stock_basics(self, mocked_async_index_offer_ids):
        stock = factories.EventStockFactory()

        api.delete_stock(stock)

        stock = models.Stock.query.one()
        assert stock.isSoftDeleted
        mocked_async_index_offer_ids.assert_called_once_with(
            [stock.offerId],
            reason=search.IndexationReason.STOCK_DELETION,
        )

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

        api.delete_stock(stock)

        # cancellation can trigger more than one request to Batch
        assert len(push_testing.requests) >= 1
        db.session.expunge_all()
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

    def test_can_delete_if_stock_from_provider(self):
        provider = providers_factories.TiteLiveThingsProviderFactory()
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
        mocked_async_index_offer_ids.assert_called_once_with(
            [offer.id],
            reason=search.IndexationReason.MEDIATION_CREATION,
        )

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
class CreateDraftOfferTest:
    def test_create_draft_offer_from_scratch(self):
        venue = offerers_factories.VenueFactory()
        body = schemas.PostDraftOfferBodyModel(
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
        assert models.Offer.query.count() == 1

    def test_cannot_create_activation_offer(self):
        venue = offerers_factories.VenueFactory()
        body = schemas.PostDraftOfferBodyModel(
            name="An offer he can't refuse",
            subcategoryId=subcategories.ACTIVATION_EVENT.id,
            venueId=venue.id,
        )
        with pytest.raises(exceptions.SubCategoryIsInactive) as error:
            api.create_draft_offer(body, venue=venue)

        msg = "Une offre ne peut être créée ou éditée en utilisant cette sous-catégorie"
        assert error.value.errors["subcategory"] == [msg]

    def test_cannot_create_offer_when_invalid_subcategory(self):
        venue = offerers_factories.VenueFactory()
        body = schemas.PostDraftOfferBodyModel(
            name="An offer he can't refuse",
            subcategoryId="TOTO",
            venueId=venue.id,
        )
        with pytest.raises(exceptions.UnknownOfferSubCategory) as error:
            api.create_draft_offer(body, venue=venue)

        assert error.value.errors["subcategory"] == ["La sous-catégorie de cette offre est inconnue"]


@pytest.mark.usefixtures("db_session")
class UpdateDraftOfferTest:
    def test_basics(self):
        offer = factories.OfferFactory(
            name="Name",
            subcategoryId=subcategories.ESCAPE_GAME.id,
            description="description",
        )
        body = schemas.PatchDraftOfferBodyModel(
            name="New name",
            description="New description",
        )
        offer = api.update_draft_offer(offer, body)
        db.session.flush()

        assert offer.name == "New name"
        assert offer.description == "New description"


@pytest.mark.usefixtures("db_session")
class UpdateDraftOfferDetailsTest:
    @mock.patch("pcapi.core.search.async_index_offer_ids")
    def test_basics(self, mocked_async_index_offer_ids):
        offer = factories.OfferFactory(
            subcategoryId=subcategories.ESCAPE_GAME.id,
            bookingEmail="old@example.com",
            isDuo=False,
            audioDisabilityCompliant=None,
            mentalDisabilityCompliant=None,
            motorDisabilityCompliant=None,
            visualDisabilityCompliant=None,
        )
        body = schemas.PatchDraftOfferUsefulInformationsBodyModel(
            audioDisabilityCompliant=True,
            mentalDisabilityCompliant=False,
            motorDisabilityCompliant=True,
            visualDisabilityCompliant=False,
            bookingEmail="new@example.com",
            isDuo=True,
        )
        offer = api.update_draft_offer_useful_informations(offer, body)
        db.session.flush()

        assert offer.audioDisabilityCompliant is True
        assert offer.mentalDisabilityCompliant is False
        assert offer.motorDisabilityCompliant is True
        assert offer.visualDisabilityCompliant is False
        assert offer.isDuo
        assert offer.bookingEmail == "new@example.com"
        mocked_async_index_offer_ids.assert_called_once_with(
            [offer.id],
            reason=search.IndexationReason.OFFER_UPDATE,
            log_extra={
                "changes": {
                    "audioDisabilityCompliant",
                    "mentalDisabilityCompliant",
                    "motorDisabilityCompliant",
                    "visualDisabilityCompliant",
                    "bookingEmail",
                    "isDuo",
                },
            },
        )

    def test_update_extra_data_should_raise_error_when_mandatory_field_not_provided(self):
        offer = factories.OfferFactory(subcategoryId=subcategories.SPECTACLE_REPRESENTATION.id)
        body = schemas.PatchDraftOfferUsefulInformationsBodyModel(extraData={"author": "Asimov"})
        with pytest.raises(api_errors.ApiErrors) as error:
            api.update_draft_offer_useful_informations(offer, body)
        assert error.value.errors == {
            "showType": ["Ce champ est obligatoire"],
            "showSubType": ["Ce champ est obligatoire"],
        }

    def test_error_when_missing_mandatory_extra_data(self):
        offer = factories.OfferFactory(
            subcategoryId=subcategories.SPECTACLE_REPRESENTATION.id, extraData={"showType": 200}
        )
        body = schemas.PatchDraftOfferUsefulInformationsBodyModel(extraData=None)
        with pytest.raises(api_errors.ApiErrors) as error:
            api.update_draft_offer_useful_informations(offer, body)
        assert error.value.errors == {
            "showType": ["Ce champ est obligatoire"],
            "showSubType": ["Ce champ est obligatoire"],
        }


@pytest.mark.usefixtures("db_session")
class CreateOfferTest:
    def test_create_offer_from_scratch(self):
        venue = offerers_factories.VenueFactory()

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
        assert not offer.product
        assert offer.externalTicketOfficeUrl == "http://example.net"
        assert offer.audioDisabilityCompliant
        assert offer.mentalDisabilityCompliant
        assert offer.motorDisabilityCompliant
        assert offer.visualDisabilityCompliant
        assert offer.validation == models.OfferValidationStatus.DRAFT
        assert offer.extraData == {}
        assert not offer.bookingEmail
        assert models.Offer.query.count() == 1
        assert offer.offererAddress == venue.offererAddress

    def test_create_offer_from_scratch_with_offerer_address(self):
        venue = offerers_factories.VenueFactory()
        offerer_address = offerers_factories.OffererAddressFactory(offerer=venue.managingOfferer)

        offer = api.create_offer(
            venue=venue,
            name="A pretty good offer",
            subcategory_id=subcategories.SEANCE_CINE.id,
            external_ticket_office_url="http://example.net",
            audio_disability_compliant=True,
            mental_disability_compliant=True,
            motor_disability_compliant=True,
            visual_disability_compliant=True,
            offerer_address=offerer_address,
        )

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
        assert not offer.bookingEmail
        assert models.Offer.query.count() == 1
        assert offer.offererAddress == offerer_address
        assert offer.offererAddress != venue.offererAddress

    def test_create_offer_with_id_at_provider(self):
        venue = offerers_factories.VenueFactory()
        provider = providers_factories.APIProviderFactory()

        offer = api.create_offer(
            venue=venue,
            name="A pretty good offer",
            subcategory_id=subcategories.SEANCE_CINE.id,
            provider=provider,
            id_at_provider="coucou",
            audio_disability_compliant=True,
            mental_disability_compliant=True,
            motor_disability_compliant=True,
            visual_disability_compliant=True,
        )

        assert offer.name == "A pretty good offer"
        assert offer.venue == venue
        assert offer.subcategoryId == subcategories.SEANCE_CINE.id
        assert offer.validation == models.OfferValidationStatus.DRAFT
        assert offer.extraData == {}
        assert offer.idAtProvider == "coucou"
        assert models.Offer.query.count() == 1

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
                booking_contact="booking@conta.ct",
                withdrawal_type=models.WithdrawalTypeEnum.NO_TICKET,
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
        db.session.flush()

        assert offer.isDuo
        assert offer.bookingEmail == "new@example.com"
        mocked_async_index_offer_ids.assert_called_once_with(
            [offer.id],
            reason=search.IndexationReason.OFFER_UPDATE,
            log_extra={"changes": {"bookingEmail", "isDuo"}},
        )

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

    def test_update_offer_with_existing_ean(self):
        offer = factories.OfferFactory(
            name="Old name",
            extraData={"ean": "1234567890123"},
            subcategoryId=subcategories.SUPPORT_PHYSIQUE_MUSIQUE_CD.id,
        )

        offer = api.update_offer(offer, name="New name", description="new Description")
        db.session.flush()

        assert offer.name == "New name"
        assert offer.description == "new Description"

    def test_raise_error_if_update_ean_for_offer_with_existing_ean(self):
        offer = factories.OfferFactory(
            name="Old name",
            extraData={"ean": "1234567890123", "musicSubType": 524, "musicType": 520},
            subcategoryId=subcategories.SUPPORT_PHYSIQUE_MUSIQUE_CD.id,
        )

        offer = api.update_offer(
            offer,
            name="New name",
            description="new Description",
            extraData={"ean": "1234567890124", "musicType": 520, "musicSubType": 524},
        )
        db.session.flush()

        assert offer.name == "New name"
        assert offer.description == "new Description"
        assert offer.extraData == {"ean": "1234567890124", "musicType": 520, "musicSubType": 524}

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
            lastProvider=provider, durationMinutes=90, subcategoryId=subcategories.SEANCE_CINE.id
        )

        with pytest.raises(api_errors.ApiErrors) as error:
            api.update_offer(offer, durationMinutes=120, isDuo=True)

        assert error.value.errors == {"durationMinutes": ["Vous ne pouvez pas modifier ce champ"]}
        offer = models.Offer.query.one()
        assert offer.durationMinutes == 90
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
        assert offer.audioDisabilityCompliant is False
        assert offer.visualDisabilityCompliant is True
        assert offer.motorDisabilityCompliant is True
        assert offer.mentalDisabilityCompliant is False

    def test_forbidden_on_imported_offer_on_other_fields(self):
        provider = providers_factories.APIProviderFactory()
        offer = factories.OfferFactory(
            lastProvider=provider,
            durationMinutes=90,
            isDuo=False,
            audioDisabilityCompliant=True,
            subcategoryId=subcategories.SEANCE_CINE.id,
        )

        with pytest.raises(api_errors.ApiErrors) as error:
            api.update_offer(offer, durationMinutes=120, isDuo=True, audioDisabilityCompliant=False)

        assert error.value.errors == {
            "durationMinutes": ["Vous ne pouvez pas modifier ce champ"],
            "isDuo": ["Vous ne pouvez pas modifier ce champ"],
        }
        offer = models.Offer.query.one()
        assert offer.durationMinutes == 90
        assert offer.isDuo is False
        assert offer.audioDisabilityCompliant is True

    def test_update_non_approved_offer_fails(self):
        pending_offer = factories.OfferFactory(name="Soliloquy", validation=models.OfferValidationStatus.PENDING)

        with pytest.raises(exceptions.RejectedOrPendingOfferNotEditable) as error:
            api.update_offer(pending_offer, name="Monologue")

        assert error.value.errors == {
            "global": ["Les offres refusées ou en attente de validation ne sont pas modifiables"]
        }
        pending_offer = models.Offer.query.one()
        assert pending_offer.name == "Soliloquy"

    def test_success_on_updating_id_at_provider(self):
        provider = providers_factories.PublicApiProviderFactory()
        offerer = offerers_factories.OffererFactory()
        providers_factories.OffererProviderFactory(offerer=offerer, provider=provider)
        offer = factories.OfferFactory(
            lastProvider=provider,
            name="Offer linked to a provider",
        )

        api.update_offer(
            offer,
            idAtProvider="some_id_at_provider",
        )

        offer = models.Offer.query.one()
        assert offer.name == "Offer linked to a provider"
        assert offer.idAtProvider == "some_id_at_provider"

    def test_raise_error_on_updating_id_at_provider(self):
        offer = factories.OfferFactory(
            lastProvider=None,
            name="Offer linked to a provider",
        )

        with pytest.raises(exceptions.CannotSetIdAtProviderWithoutAProvider) as error:
            api.update_offer(
                offer,
                idAtProvider="some_id_at_provider",
            )

        assert error.value.errors["idAtProvider"] == [
            "Une offre ne peut être créée ou éditée avec un idAtProvider si elle n'a pas de provider"
        ]


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

        assert len(caplog.records) == 3
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
class ActivateFutureOffersTest:
    @mock.patch("pcapi.core.search.async_index_offer_ids")
    def test_activate_future_offers_empty(self, mocked_async_index_offer_ids):
        offer = factories.OfferFactory(isActive=False)  # Offer not in the future, i.e. no publication_date

        api.activate_future_offers()

        assert not models.Offer.query.get(offer.id).isActive
        mocked_async_index_offer_ids.assert_not_called()

    @mock.patch("pcapi.core.search.async_index_offer_ids")
    def test_activate_future_offers(self, mocked_async_index_offer_ids):
        offer = factories.OfferFactory(isActive=False)
        publication_date = datetime.utcnow().replace(minute=0, second=0, microsecond=0) + timedelta(days=30)
        factories.FutureOfferFactory(offerId=offer.id, publicationDate=publication_date)

        api.activate_future_offers(publication_date=publication_date)

        assert models.Offer.query.get(offer.id).isActive
        mocked_async_index_offer_ids.assert_called_once()
        assert set(mocked_async_index_offer_ids.call_args[0][0]) == set([offer.id])


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
        ean = "2-221-00164-8"
        product1 = factories.ProductFactory(extraData={"ean": "2221001648"})
        offer11 = factories.OfferFactory(product=product1)
        offer12 = factories.OfferFactory(product=product1)
        product2 = factories.ProductFactory(extraData={"ean": "2221001648"})
        offer21 = factories.OfferFactory(product=product2)
        inactive_offer = factories.OfferFactory(product=product1, isActive=False)
        unmatched_offer = factories.OfferFactory()
        criterion1 = criteria_factories.CriterionFactory(name="Pretty good books")
        criterion2 = criteria_factories.CriterionFactory(name="Other pretty good books")

        # When
        is_successful = api.add_criteria_to_offers([criterion1.id, criterion2.id], ean=ean)

        # Then
        assert is_successful is True
        assert set(offer11.criteria) == {criterion1, criterion2}
        assert set(offer12.criteria) == {criterion1, criterion2}
        assert set(offer21.criteria) == {criterion1, criterion2}
        assert not inactive_offer.criteria
        assert not unmatched_offer.criteria
        mocked_async_index_offer_ids.assert_called_once_with(
            {offer11.id, offer12.id, offer21.id},
            reason=search.IndexationReason.CRITERIA_LINK,
            log_extra={"criterion_ids": [criterion1.id, criterion2.id]},
        )

    @mock.patch("pcapi.core.search.async_index_offer_ids")
    def test_add_criteria_from_ean_when_one_has_criteria(self, mocked_async_index_offer_ids):
        # Given
        ean = "2221001648"
        criterion1 = criteria_factories.CriterionFactory(name="Pretty good books")
        criterion2 = criteria_factories.CriterionFactory(name="Other pretty good books")
        product1 = factories.ProductFactory(extraData={"ean": ean})
        offer11 = factories.OfferFactory(product=product1, criteria=[criterion1])
        offer12 = factories.OfferFactory(product=product1, criteria=[criterion2])
        product2 = factories.ProductFactory(extraData={"ean": ean})
        offer21 = factories.OfferFactory(product=product2)
        inactive_offer = factories.OfferFactory(product=product1, isActive=False)
        unmatched_offer = factories.OfferFactory()

        # When
        is_successful = api.add_criteria_to_offers([criterion1.id, criterion2.id], ean=ean)

        # Then
        assert is_successful is True
        assert set(offer11.criteria) == {criterion1, criterion2}
        assert set(offer12.criteria) == {criterion1, criterion2}
        assert set(offer21.criteria) == {criterion1, criterion2}
        assert not inactive_offer.criteria
        assert not unmatched_offer.criteria
        mocked_async_index_offer_ids.assert_called_once_with(
            {offer11.id, offer12.id, offer21.id},
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
        inactive_offer = factories.OfferFactory(product=product, isActive=False)
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
        ean = "2-221-00164-8"
        factories.OfferFactory(extraData={"ean": "2221001647"})
        criterion = criteria_factories.CriterionFactory(name="Pretty good books")

        # When
        is_successful = api.add_criteria_to_offers([criterion.id], ean=ean)

        # Then
        assert is_successful is False


@pytest.mark.usefixtures("db_session")
class RejectInappropriateProductTest:
    @mock.patch("pcapi.core.search.async_index_offer_ids")
    @mock.patch("pcapi.core.mails.transactional.send_booking_cancellation_emails_to_user_and_offerer")
    def test_should_reject_product_with_inappropriate_content(
        self, mocked_send_booking_cancellation_emails_to_user_and_offerer, mocked_async_index_offer_ids
    ):
        # Given
        provider = providers_factories.APIProviderFactory()
        product1 = factories.ThingProductFactory(
            subcategoryId=subcategories.LIVRE_PAPIER.id, extraData={"ean": "ean-de-test"}, lastProvider=provider
        )
        product2 = factories.ThingProductFactory(
            subcategoryId=subcategories.LIVRE_PAPIER.id, extraData={"ean": "ean-de-test-2"}, lastProvider=provider
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
        api.reject_inappropriate_products(["ean-de-test"], user, send_booking_cancellation_emails=False)

        # Then
        offers = models.Offer.query.all()
        bookings = bookings_models.Booking.query.all()

        product1 = models.Product.query.filter(models.Product.extraData["ean"].astext == "ean-de-test").one()
        assert product1.gcuCompatibilityType == models.GcuCompatibilityType.PROVIDER_INCOMPATIBLE

        product2 = models.Product.query.filter(models.Product.extraData["ean"].astext == "ean-de-test-2").one()
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
        assert users_models.Favorite.query.count() == 1  # product 2
        assert all(booking.isCancelled is True for booking in bookings if booking.stock.offer.product.id == product1)
        mocked_send_booking_cancellation_emails_to_user_and_offerer.assert_not_called()

    @mock.patch("pcapi.core.mails.transactional.send_booking_cancellation_emails_to_user_and_offerer")
    def test_should_reject_product_with_inappropriate_content_and_send_email(
        self, mocked_send_booking_cancellation_emails_to_user_and_offerer
    ):
        # Given
        provider = providers_factories.APIProviderFactory()
        product1 = factories.ThingProductFactory(
            subcategoryId=subcategories.LIVRE_PAPIER.id, extraData={"ean": "ean-de-test"}, lastProvider=provider
        )
        product2 = factories.ThingProductFactory(
            subcategoryId=subcategories.LIVRE_PAPIER.id, extraData={"ean": "ean-de-test-2"}, lastProvider=provider
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

        assert users_models.Favorite.query.count() == len(offers)
        assert bookings_models.Booking.query.count() == len(offers)

        # When
        api.reject_inappropriate_products(["ean-de-test"], user)

        # Then
        mocked_send_booking_cancellation_emails_to_user_and_offerer.assert_called()

    @mock.patch("pcapi.core.search.async_index_offer_ids")
    @mock.patch("pcapi.core.mails.transactional.send_booking_cancellation_emails_to_user_and_offerer")
    def test_update_should_not_override_fraud_incompatibility(
        self, mocked_send_booking_cancellation_emails_to_user_and_offerer, mocked_async_index_offer_ids
    ):
        # Given
        provider = providers_factories.APIProviderFactory()
        factories.ThingProductFactory(
            subcategoryId=subcategories.LIVRE_PAPIER.id,
            extraData={"ean": "ean-de-test"},
            lastProvider=provider,
            gcuCompatibilityType=models.GcuCompatibilityType.FRAUD_INCOMPATIBLE,
        )
        user = users_factories.UserFactory()

        # When
        api.reject_inappropriate_products(["ean-de-test"], user, send_booking_cancellation_emails=False)

        # Then

        product = models.Product.query.filter(models.Product.extraData["ean"].astext == "ean-de-test").one()
        assert product.gcuCompatibilityType == models.GcuCompatibilityType.FRAUD_INCOMPATIBLE

        mocked_send_booking_cancellation_emails_to_user_and_offerer.assert_not_called()


@pytest.mark.usefixtures("db_session")
class DeactivatePermanentlyUnavailableProductTest:
    @mock.patch("pcapi.core.search.async_index_offer_ids")
    def test_should_deactivate_permanently_unavailable_products(self, mocked_async_index_offer_ids):
        # Given
        product1 = factories.ThingProductFactory(
            subcategoryId=subcategories.LIVRE_PAPIER.id, extraData={"ean": "ean-de-test"}
        )
        product2 = factories.ThingProductFactory(
            subcategoryId=subcategories.LIVRE_PAPIER.id, extraData={"ean": "ean-de-test"}
        )
        factories.OfferFactory(product=product1)
        factories.OfferFactory(product=product1)
        factories.OfferFactory(product=product2)

        # When
        api.deactivate_permanently_unavailable_products("ean-de-test")

        # Then
        products = models.Product.query.all()
        offers = models.Offer.query.all()

        assert any(product.name == "xxx" for product in products)
        assert not any(offer.isActive for offer in offers)
        assert any(offer.name == "xxx" for offer in offers)
        mocked_async_index_offer_ids.assert_called_once()
        assert set(mocked_async_index_offer_ids.call_args[0][0]) == {o.id for o in offers}


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
        assert models.ValidationRuleOfferLink.query.count() == 1

    def test_offer_validation_with_unrelated_rule(self):
        collective_offer = educational_factories.CollectiveOfferFactory(name="REJECTED")
        factories.OfferValidationSubRuleFactory(
            model=models.OfferValidationModel.OFFER,
            attribute=models.OfferValidationAttribute.NAME,
            operator=models.OfferValidationRuleOperator.CONTAINS,
            comparated={"comparated": ["REJECTED"]},
        )

        assert api.set_offer_status_based_on_fraud_criteria(collective_offer) == models.OfferValidationStatus.APPROVED
        assert models.ValidationRuleOfferLink.query.count() == 0

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
        assert models.ValidationRuleOfferLink.query.count() == 2

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
        assert models.ValidationRuleOfferLink.query.count() == 0
        assert educational_models.ValidationRuleCollectiveOfferLink.query.count() == 1

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
        assert models.ValidationRuleOfferLink.query.count() == 1
        assert educational_models.ValidationRuleCollectiveOfferLink.query.count() == 1

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
        assert models.ValidationRuleOfferLink.query.count() == 1
        assert educational_models.ValidationRuleCollectiveOfferLink.query.count() == 1

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
        assert models.ValidationRuleOfferLink.query.count() == 1

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
        assert models.ValidationRuleOfferLink.query.count() == 1

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
        assert models.ValidationRuleOfferLink.query.count() == 1
        assert educational_models.ValidationRuleCollectiveOfferLink.query.count() == 1

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

        assert models.ValidationRuleOfferLink.query.filter_by(offerId=offer_to_flag.id).count() == 2
        assert models.ValidationRuleOfferLink.query.filter_by(offerId=offer_to_flag_too.id).count() == 1
        assert models.ValidationRuleOfferLink.query.filter_by(ruleId=offer_name_rule.id).count() == 2
        assert models.ValidationRuleOfferLink.query.filter_by(ruleId=offer_price_rule.id).count() == 1
        assert models.ValidationRuleOfferLink.query.count() == 3

    @pytest.mark.parametrize(
        "formats, excluded_formats, expected_status",
        [
            (
                [subcategories.EacFormat.VISITE_LIBRE],
                [subcategories.EacFormat.CONCERT, subcategories.EacFormat.REPRESENTATION],
                models.OfferValidationStatus.PENDING,
            ),
            (
                [
                    subcategories.EacFormat.CONCERT,
                    subcategories.EacFormat.VISITE_LIBRE,
                    subcategories.EacFormat.REPRESENTATION,
                ],
                [subcategories.EacFormat.CONCERT, subcategories.EacFormat.VISITE_LIBRE],
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
                [subcategories.EacFormat.VISITE_LIBRE],
                [subcategories.EacFormat.CONCERT],
                models.OfferValidationStatus.APPROVED,
            ),
            (
                [subcategories.EacFormat.CONCERT, subcategories.EacFormat.VISITE_LIBRE],
                [subcategories.EacFormat.CONCERT],
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
        assert models.ValidationRuleOfferLink.query.count() == 0

    def test_offer_validation_when_offerer_on_manual_review(self):
        collective_offer = educational_factories.CollectiveOfferFactory()
        offerers_factories.ManualReviewOffererConfidenceRuleFactory(offerer=collective_offer.venue.managingOfferer)

        status = api.set_offer_status_based_on_fraud_criteria(collective_offer)

        assert status == models.OfferValidationStatus.PENDING
        assert models.ValidationRuleOfferLink.query.count() == 0

    def test_offer_validation_when_offerer_on_manual_review_with_rules(self, offer_matching_one_validation_rule):
        offerers_factories.ManualReviewOffererConfidenceRuleFactory(
            offerer=offer_matching_one_validation_rule.venue.managingOfferer
        )

        status = api.set_offer_status_based_on_fraud_criteria(offer_matching_one_validation_rule)

        assert status == models.OfferValidationStatus.PENDING
        assert models.ValidationRuleOfferLink.query.count() == 1

    def test_offer_validation_when_venue_whitelisted(self, offer_matching_one_validation_rule):
        offerers_factories.WhitelistedVenueConfidenceRuleFactory(venue=offer_matching_one_validation_rule.venue)

        status = api.set_offer_status_based_on_fraud_criteria(offer_matching_one_validation_rule)

        assert status == models.OfferValidationStatus.APPROVED
        assert models.ValidationRuleOfferLink.query.count() == 0

    def test_offer_validation_when_venue_on_manual_review(self):
        collective_offer = educational_factories.CollectiveOfferFactory()
        offerers_factories.ManualReviewVenueConfidenceRuleFactory(venue=collective_offer.venue)

        status = api.set_offer_status_based_on_fraud_criteria(collective_offer)

        assert status == models.OfferValidationStatus.PENDING
        assert models.ValidationRuleOfferLink.query.count() == 0


@pytest.mark.usefixtures("db_session")
class UnindexExpiredOffersTest:
    @time_machine.travel("2020-01-05 10:00:00")
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
    @override_settings(TITELIVE_EPAGINE_API_USERNAME="test@example.com")
    @override_settings(TITELIVE_EPAGINE_API_PASSWORD="qwerty123")
    def test_modify_product_if_existing_and_not_gcu_compatible(self, requests_mock):
        ean = "9782070455379"
        requests_mock.post(
            f"{settings.TITELIVE_EPAGINE_API_AUTH_URL}/login/test@example.com/token",
            json={"token": "XYZ"},
        )
        requests_mock.get(
            f"{settings.TITELIVE_EPAGINE_API_URL}/ean/{ean}",
            json=fixtures.BOOK_BY_EAN_FIXTURE,
        )

        product = factories.ProductFactory(
            idAtProviders=ean,
            name="test",
            subcategoryId=subcategories.LIVRE_PAPIER.id,
            extraData={
                "ean": ean,
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

        assert models.Product.query.one() == product
        assert product.isGcuCompatible
        oeuvre = fixtures.BOOK_BY_EAN_FIXTURE["oeuvre"]
        article = oeuvre["article"][0]
        assert product.name == oeuvre["titre"]
        assert product.description == article["resume"]
        assert product.extraData["author"] == oeuvre["auteurs"]
        assert product.extraData["ean"] == ean
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

    @override_settings(TITELIVE_EPAGINE_API_USERNAME="test@example.com")
    @override_settings(TITELIVE_EPAGINE_API_PASSWORD="qwerty123")
    def test_create_product_if_not_existing(self, requests_mock):
        ean = "9782070455379"
        requests_mock.post(
            f"{settings.TITELIVE_EPAGINE_API_AUTH_URL}/login/test@example.com/token",
            json={"token": "XYZ"},
        )
        requests_mock.get(
            f"{settings.TITELIVE_EPAGINE_API_URL}/ean/{ean}",
            json=fixtures.BOOK_BY_EAN_FIXTURE,
        )
        assert not models.Product.query.filter(models.Product.idAtProviders == ean).one_or_none()

        api.whitelist_product(ean)

        product = models.Product.query.filter(models.Product.idAtProviders == ean).one()
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

        api.batch_delete_draft_offers(models.Offer.query.filter(models.Offer.id.in_(offer_ids)))

        assert criteria_models.OfferCriterion.query.count() == 0
        assert models.Mediation.query.count() == 0
        assert models.Stock.query.count() == 0
        assert models.Offer.query.count() == 0
        assert models.ActivationCode.query.count() == 0


@pytest.mark.usefixtures("db_session")
class DeleteStocksTest:
    def test_delete_batch_stocks(self, client):
        stocks = factories.StockFactory.create_batch(3)
        api.batch_delete_stocks(stocks)
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
            offer_id=offer.id,
            date=beginning_datetime.date(),
            venue=offer.venue,
        )
        api.batch_delete_stocks(stocks)

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
            offer_id=offer.id,
            time=beginning_datetime.time(),
            venue=offer.venue,
        )
        api.batch_delete_stocks(stocks)

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
            offer_id=offer.id,
            price_category_id=stock_1.priceCategoryId,
            venue=offer.venue,
        )
        api.batch_delete_stocks(stocks)

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


class FormatPublicationDateTest:
    def test_format_publication_date(self):
        assert api._format_publication_date(None, "UTC") is None
        publication_date = datetime(2024, 3, 20, 9, 0, 0)
        assert api._format_publication_date(publication_date, "Europe/Paris") == datetime(2024, 3, 20, 8, 0, 0)
        # Pacific/Marquesas: UTC-09:30
        # 9:00 Pacific/Marquesas -> 18:30 UTC -> rounded to next hour = 19:00 UTC
        assert api._format_publication_date(publication_date, "Pacific/Marquesas") == datetime(2024, 3, 20, 19, 0)


@pytest.mark.usefixtures("db_session")
class UpdateStockQuantityToMatchCinemaVenueProviderRemainingPlacesTest:
    DATETIME_10_DAYS_AFTER = datetime.today() + timedelta(days=10)
    DATETIME_10_DAYS_AGO = datetime.today() - timedelta(days=10)

    @override_features(ENABLE_CDS_IMPLEMENTATION=True)
    @pytest.mark.parametrize(
        "show_id, show_beginning_datetime, api_return_value, expected_remaining_quantity",
        [
            (888, DATETIME_10_DAYS_AFTER, {"888": 10}, 10),
            (888, DATETIME_10_DAYS_AFTER, {"888": 5}, 10),
            (888, DATETIME_10_DAYS_AFTER, {"888": 1}, 1),
            (888, DATETIME_10_DAYS_AFTER, {"888": 0}, 0),
            (123, DATETIME_10_DAYS_AFTER, {"888": 0}, 0),
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
        app,
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
        stock = factories.EventStockFactory(
            offer=offer,
            quantity=10,
            idAtProviders=f"{offer_id_at_provider}#{show_id}",
            beginningDatetime=show_beginning_datetime,
        )

        mocked_get_shows_stock.return_value = api_return_value
        api.update_stock_quantity_to_match_cinema_venue_provider_remaining_places(offer)

        assert stock.remainingQuantity == expected_remaining_quantity
        if expected_remaining_quantity == 0:
            mocked_async_index_offer_ids.assert_called_once_with(
                [offer.id],
                reason=search.IndexationReason.CINEMA_STOCK_QUANTITY_UPDATE,
                log_extra={"sold_out": True},
            )
        else:
            mocked_async_index_offer_ids.assert_not_called()

    @override_features(ENABLE_CDS_IMPLEMENTATION=True)
    def test_cds_with_get_showtimes_stocks_cached(
        self,
        requests_mock,
        app,
    ):
        redis_client = app.redis_client

        movie_id = cds_fixtures.SHOW_1["mediaid"]["id"]
        showtime_id = cds_fixtures.SHOW_1["id"]
        cds_provider = providers_repository.get_provider_by_local_class("CDSStocks")
        venue_provider = providers_factories.VenueProviderFactory(
            provider=cds_provider, venueIdAtOfferProvider="cinema_id_test"
        )
        pivot = providers_factories.CinemaProviderPivotFactory(
            venue=venue_provider.venue,
            provider=venue_provider.provider,
            idAtProvider=venue_provider.venueIdAtOfferProvider,
        )
        cinema = providers_factories.CDSCinemaDetailsFactory(cinemaProviderPivot=pivot)
        offer_id_at_provider = f"{movie_id}%{venue_provider.venue.siret}%CDS"
        offer = factories.EventOfferFactory(
            venue=venue_provider.venue, idAtProvider=offer_id_at_provider, lastProviderId=cds_provider.id
        )
        stock = factories.EventStockFactory(
            offer=offer,
            quantity=10,
            idAtProviders=f"{offer_id_at_provider}#{showtime_id}",
            beginningDatetime=self.DATETIME_10_DAYS_AFTER,
        )

        shows_adapter = requests_mock.get(
            f"https://{cinema.accountId}.test_cds_url/vad/shows?api_token={cinema.cinemaApiToken}",
            json=[cds_fixtures.SHOW_1, cds_fixtures.SHOW_2],
        )  # ggignore
        gauge_adapter = requests_mock.get(
            f"https://{cinema.accountId}.test_cds_url/vad/cinemas?api_token={cinema.cinemaApiToken}",
            json=[cds_fixtures.CINEMA_WITH_INTERNET_SALE_GAUGE_ACTIVE_TRUE],
        )  # ggignore

        api.update_stock_quantity_to_match_cinema_venue_provider_remaining_places(offer)

        assert shows_adapter.call_count == 1
        assert gauge_adapter.call_count == 1

        # Cached call
        api.update_stock_quantity_to_match_cinema_venue_provider_remaining_places(offer)
        api.update_stock_quantity_to_match_cinema_venue_provider_remaining_places(offer)

        assert shows_adapter.call_count == 1
        assert gauge_adapter.call_count == 1

        # Non regression test. The stock SHOULD NOT be sold out
        # as no bookings are created
        # If so, it means we didn’t find the showtime in
        # `update_stock_quantity_to_match_cinema_venue_provider_remaining_places`
        # and therefor the stock is automatically set to sold out.
        # Which means something is probably wrong and should be fixed !
        assert stock.quantity == 10
        assert stock.quantity != stock.dnBookedQuantity

        # One minute into the future
        redis_client.expire("api:cinema_provider:cds:stocks:cinema_id_test:[1]", 0)

        api.update_stock_quantity_to_match_cinema_venue_provider_remaining_places(offer)

        assert shows_adapter.call_count == 2
        assert gauge_adapter.call_count == 2

        assert stock.quantity == 10
        assert stock.quantity != stock.dnBookedQuantity

    @override_features(ENABLE_BOOST_API_INTEGRATION=True)
    @pytest.mark.parametrize(
        "show_id, show_beginning_datetime, api_return_value, expected_remaining_quantity",
        [
            (888, DATETIME_10_DAYS_AFTER, {"888": 10}, 10),
            (888, DATETIME_10_DAYS_AFTER, {"888": 5}, 10),
            (888, DATETIME_10_DAYS_AFTER, {"888": 1}, 1),
            (888, DATETIME_10_DAYS_AFTER, {"888": 0}, 0),
            (123, DATETIME_10_DAYS_AFTER, {"888": 0}, 0),
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
        app,
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
            mocked_async_index_offer_ids.assert_called_once_with(
                [offer.id],
                reason=search.IndexationReason.CINEMA_STOCK_QUANTITY_UPDATE,
                log_extra={"sold_out": True},
            )
        else:
            mocked_async_index_offer_ids.assert_not_called()

    @override_features(ENABLE_BOOST_API_INTEGRATION=True)
    def test_boost_with_get_film_showtimes_stocks_cached(
        self,
        requests_mock,
        app,
    ):
        redis_client = app.redis_client

        movie_id = boost_fixtures.SHOWTIME_15971["film"]["id"]
        shomtime_id = boost_fixtures.SHOWTIME_15971["id"]
        # Call made by get_film_showtimes_stocks
        start_date = date.today()
        end_date = (start_date + timedelta(days=boost_constants.BOOST_SHOWS_INTERVAL_DAYS)).strftime("%Y-%m-%d")
        page_1_adapter = requests_mock.get(
            f"https://cinema-0.example.com/api/showtimes/between/{start_date.strftime('%Y-%m-%d')}/{end_date}?paymentMethod=external%3Acredit%3Apassculture&hideFullReservation=1&film={movie_id}&page=1&per_page=30",
            json=boost_fixtures.ShowtimesWithPaymentMethodFilterEndpointResponse.PAGE_1_JSON_DATA,
        )
        page_2_adapter = requests_mock.get(
            f"https://cinema-0.example.com/api/showtimes/between/{start_date.strftime('%Y-%m-%d')}/{end_date}?paymentMethod=external%3Acredit%3Apassculture&hideFullReservation=1&film={movie_id}&page=2&per_page=30",
            json=boost_fixtures.ShowtimesWithPaymentMethodFilterEndpointResponse.PAGE_2_JSON_DATA,
        )

        boost_provider = providers_repository.get_provider_by_local_class("BoostStocks")
        venue_provider = providers_factories.VenueProviderFactory(provider=boost_provider)
        pivot = cinema_provider_pivot = providers_factories.CinemaProviderPivotFactory(
            venue=venue_provider.venue,
            provider=venue_provider.provider,
            idAtProvider=venue_provider.venueIdAtOfferProvider,
        )
        providers_factories.BoostCinemaDetailsFactory(
            cinemaProviderPivot=cinema_provider_pivot, cinemaUrl="https://cinema-0.example.com/"
        )
        offer_id_at_provider = f"{movie_id}%{venue_provider.venueId}%Boost"
        offer = factories.EventOfferFactory(
            venue=venue_provider.venue, idAtProvider=offer_id_at_provider, lastProviderId=boost_provider.id
        )
        stock = factories.EventStockFactory(
            offer=offer,
            idAtProviders=f"{offer_id_at_provider}#{shomtime_id}",
            beginningDatetime=self.DATETIME_10_DAYS_AFTER,
            quantity=10,
        )

        api.update_stock_quantity_to_match_cinema_venue_provider_remaining_places(offer)

        # Cached calls
        api.update_stock_quantity_to_match_cinema_venue_provider_remaining_places(offer)
        api.update_stock_quantity_to_match_cinema_venue_provider_remaining_places(offer)

        # Non regression test. The stock SHOULD NOT be sold out
        # as no bookings are created
        # If so, it means we didn’t find the showtime in
        # `update_stock_quantity_to_match_cinema_venue_provider_remaining_places`
        # and therefor the stock is automatically set to sold out.
        # Which means something is probably wron and should be fixed !
        assert stock.quantity == 10
        assert stock.quantity != stock.dnBookedQuantity

        assert page_1_adapter.call_count == 1
        assert page_2_adapter.call_count == 1

        # We are now one minutes in the future
        redis_client.expire(f"api:cinema_provider:boost:stocks:{pivot.idAtProvider}:{movie_id}", 0)

        api.update_stock_quantity_to_match_cinema_venue_provider_remaining_places(offer)

        assert page_1_adapter.call_count == 2
        assert page_2_adapter.call_count == 2

        assert stock.quantity == 10
        assert stock.quantity != stock.dnBookedQuantity

    @override_features(ENABLE_CGR_INTEGRATION=True)
    @pytest.mark.parametrize(
        "show_id, show_beginning_datetime, api_return_value, expected_remaining_quantity",
        [
            (888, DATETIME_10_DAYS_AFTER, {"888": 10}, 10),
            (888, DATETIME_10_DAYS_AFTER, {"888": 5}, 10),
            (888, DATETIME_10_DAYS_AFTER, {"888": 1}, 1),
            (888, DATETIME_10_DAYS_AFTER, {"888": 0}, 0),
            (123, DATETIME_10_DAYS_AFTER, {"888": 0}, 0),
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
        app,
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
            mocked_async_index_offer_ids.assert_called_once_with(
                [offer.id],
                reason=search.IndexationReason.CINEMA_STOCK_QUANTITY_UPDATE,
                log_extra={"sold_out": True},
            )
        else:
            mocked_async_index_offer_ids.assert_not_called()

    @override_features(ENABLE_CGR_INTEGRATION=True)
    def test_cgr_with_get_showtimes_stock_cached(
        self,
        requests_mock,
        app,
    ):
        redis_client = app.redis_client

        showtime_id = cgr_fixtures.FILM_138473["Seances"][0]["IDSeance"]
        movie_id = cgr_fixtures.FILM_138473["IDFilm"]
        offer_id_at_provider = f"{movie_id}%12354114%CGR"
        cgr_provider = providers_repository.get_provider_by_local_class("CGRStocks")
        venue_provider = providers_factories.VenueProviderFactory(provider=cgr_provider)
        pivot = cinema_provider_pivot = providers_factories.CinemaProviderPivotFactory(
            venue=venue_provider.venue, provider=cgr_provider, idAtProvider=venue_provider.venueIdAtOfferProvider
        )
        providers_factories.CGRCinemaDetailsFactory(
            cinemaUrl="http://cgr-cinema-0.example.com/web_service", cinemaProviderPivot=cinema_provider_pivot
        )
        offer = factories.EventOfferFactory(
            name="Séance ciné solo",
            venue=venue_provider.venue,
            subcategoryId=subcategories.SEANCE_CINE.id,
            lastProviderId=cinema_provider_pivot.provider.id,
            idAtProvider=offer_id_at_provider,
        )
        stock = factories.EventStockFactory(
            offer=offer, idAtProviders=f"{offer_id_at_provider}#{showtime_id}", quantity=10
        )
        requests_mock.get(
            "http://cgr-cinema-0.example.com/web_service?wsdl", text=soap_definitions.WEB_SERVICE_DEFINITION
        )

        post_adapter = requests_mock.post(
            "http://cgr-cinema-0.example.com/web_service",
            [
                {"text": cgr_fixtures.cgr_response_template([cgr_fixtures.FILM_138473])},
            ],
        )

        # Then
        api.update_stock_quantity_to_match_cinema_venue_provider_remaining_places(offer)

        # Cached calls
        api.update_stock_quantity_to_match_cinema_venue_provider_remaining_places(offer)
        api.update_stock_quantity_to_match_cinema_venue_provider_remaining_places(offer)

        assert post_adapter.call_count == 1

        # Non regression test. The stock SHOULD NOT be sold out
        # as no bookings are created
        # If so, it means we didn’t find the showtime in
        # `update_stock_quantity_to_match_cinema_venue_provider_remaining_places`
        # and therefor the stock is automatically set to sold out.
        # Which means something is probably wron and should be fixed !
        assert stock.quantity == 10
        assert stock.quantity != stock.dnBookedQuantity

        # One minute into the futur
        redis_client.expire(f"api:cinema_provider:cgr:stocks:{pivot.idAtProvider}:{movie_id}", 0)

        api.update_stock_quantity_to_match_cinema_venue_provider_remaining_places(offer)

        assert post_adapter.call_count == 2

    @override_features(ENABLE_EMS_INTEGRATION=True)
    @patch("pcapi.core.search.async_index_offer_ids")
    def test_ems(
        self,
        mocked_async_index_offer_ids,
        requests_mock,
        app,
    ):
        expected_remaining_quantity = 10
        api_return_value = [888]
        ems_provider = providers_repository.get_provider_by_local_class("EMSStocks")
        venue_provider = providers_factories.VenueProviderFactory(provider=ems_provider)
        providers_factories.CinemaProviderPivotFactory(
            venue=venue_provider.venue,
            provider=venue_provider.provider,
            idAtProvider=venue_provider.venueIdAtOfferProvider,
        )
        movie_id = "52F3G"
        offer_id_at_provider = f"{movie_id}%{venue_provider.venueId}%EMS"
        offer = factories.EventOfferFactory(
            venue=venue_provider.venue, idAtProvider=offer_id_at_provider, lastProviderId=ems_provider.id
        )
        stock = factories.EventStockFactory(
            offer=offer,
            quantity=10,
            idAtProviders=f"{offer_id_at_provider}#{888}",
            beginningDatetime=self.DATETIME_10_DAYS_AFTER,
        )
        response_json = {"statut": 1, "seances": api_return_value}
        url_matcher = re.compile("https://fake_url.com/SEANCE/*")
        requests_mock.post(url=url_matcher, json=response_json)

        api.update_stock_quantity_to_match_cinema_venue_provider_remaining_places(offer)

        assert stock.remainingQuantity == expected_remaining_quantity
        mocked_async_index_offer_ids.assert_not_called()

    @override_features(ENABLE_EMS_INTEGRATION=True)
    def test_ems_with_get_film_showtimes_stocks_cached(self, requests_mock, app):
        redis_client = app.redis_client

        api_return_value = [888]
        ems_provider = providers_repository.get_provider_by_local_class("EMSStocks")
        venue_provider = providers_factories.VenueProviderFactory(provider=ems_provider)
        pivot = providers_factories.CinemaProviderPivotFactory(
            venue=venue_provider.venue,
            provider=venue_provider.provider,
            idAtProvider=venue_provider.venueIdAtOfferProvider,
        )
        movie_id = "52F3G"
        offer_id_at_provider = f"{movie_id}%{venue_provider.venueId}%EMS"
        offer = factories.EventOfferFactory(
            venue=venue_provider.venue, idAtProvider=offer_id_at_provider, lastProviderId=ems_provider.id
        )
        stock = factories.EventStockFactory(
            offer=offer,
            quantity=10,
            idAtProviders=f"{offer_id_at_provider}#{888}",
            beginningDatetime=self.DATETIME_10_DAYS_AFTER,
        )
        response_json = {"statut": 1, "seances": api_return_value}
        url_matcher = re.compile("https://fake_url.com/SEANCE/*")
        post_adapter = requests_mock.post(url=url_matcher, json=response_json)

        api.update_stock_quantity_to_match_cinema_venue_provider_remaining_places(offer)

        # Call cached
        api.update_stock_quantity_to_match_cinema_venue_provider_remaining_places(offer)
        api.update_stock_quantity_to_match_cinema_venue_provider_remaining_places(offer)

        assert post_adapter.call_count == 1

        # Non regression test. The stock SHOULD NOT be sold out
        # as no bookings are created
        # If so, it means we didn’t find the showtime in
        # `update_stock_quantity_to_match_cinema_venue_provider_remaining_places`
        # and therefor the stock is automatically set to sold out.
        # Which means something is probably wrong and should be fixed !
        assert stock.quantity == 10
        assert stock.quantity != stock.dnBookedQuantity

        # We are now one minutes in the future
        redis_client.expire(f"api:cinema_provider:ems:stocks:{pivot.idAtProvider}:{movie_id}", 0)

        api.update_stock_quantity_to_match_cinema_venue_provider_remaining_places(offer)

        assert post_adapter.call_count == 2

        assert stock.quantity == 10
        assert stock.quantity != stock.dnBookedQuantity

    @override_features(ENABLE_EMS_INTEGRATION=True)
    @patch("pcapi.core.search.async_index_offer_ids")
    def test_ems_no_remaining_places_case(
        self,
        mocked_async_index_offer_ids,
        requests_mock,
    ):
        ems_provider = providers_repository.get_provider_by_local_class("EMSStocks")
        venue_provider = providers_factories.VenueProviderFactory(provider=ems_provider)
        providers_factories.CinemaProviderPivotFactory(
            venue=venue_provider.venue,
            provider=venue_provider.provider,
            idAtProvider=venue_provider.venueIdAtOfferProvider,
        )
        movie_id = "52F3G"
        offer_id_at_provider = f"{movie_id}%{venue_provider.venueId}%EMS"
        offer = factories.EventOfferFactory(
            venue=venue_provider.venue, idAtProvider=offer_id_at_provider, lastProviderId=ems_provider.id
        )
        stock = factories.EventStockFactory(
            offer=offer,
            quantity=10,
            idAtProviders=f"{offer_id_at_provider}#{888}",
            beginningDatetime=self.DATETIME_10_DAYS_AFTER,
        )
        url_matcher = re.compile("https://fake_url.com/SEANCE/*")
        expected_data = {
            "statut": 0,
            "code_erreur": 104,
            "message_erreur": "Il n'y a plus de séance disponible pour ce film",
        }

        requests_mock.post(url_matcher, json=expected_data)

        api.update_stock_quantity_to_match_cinema_venue_provider_remaining_places(offer)

        assert stock.remainingQuantity == 0
        assert stock.quantity == stock.dnBookedQuantity

        mocked_async_index_offer_ids.assert_called_once_with(
            [offer.id],
            reason=search.IndexationReason.CINEMA_STOCK_QUANTITY_UPDATE,
            log_extra={"sold_out": True},
        )

    @override_features(ENABLE_CGR_INTEGRATION=True)
    @patch("pcapi.core.search.async_index_offer_ids")
    def test_cgr_no_remaining_places_case(
        self,
        mocked_async_index_offer_ids,
        requests_mock,
    ):
        offer_id_at_provider = "123%12354114%CGR"
        cgr_provider = providers_repository.get_provider_by_local_class("CGRStocks")
        venue_provider = providers_factories.VenueProviderFactory(provider=cgr_provider)
        cinema_provider_pivot = providers_factories.CinemaProviderPivotFactory(
            venue=venue_provider.venue, provider=cgr_provider, idAtProvider=venue_provider.venueIdAtOfferProvider
        )
        providers_factories.CGRCinemaDetailsFactory(
            cinemaUrl="http://cgr-cinema-0.example.com/web_service", cinemaProviderPivot=cinema_provider_pivot
        )
        offer = factories.EventOfferFactory(
            name="Séance ciné solo",
            venue=venue_provider.venue,
            subcategoryId=subcategories.SEANCE_CINE.id,
            lastProviderId=cinema_provider_pivot.provider.id,
            idAtProvider=offer_id_at_provider,
        )
        stock = factories.EventStockFactory(offer=offer, idAtProviders=f"{offer_id_at_provider}#1111")
        requests_mock.get(
            "http://cgr-cinema-0.example.com/web_service?wsdl", text=soap_definitions.WEB_SERVICE_DEFINITION
        )

        # The show is sold-out, so there's no film either showtimes returned
        requests_mock.post(
            "http://cgr-cinema-0.example.com/web_service",
            [
                {"text": cgr_fixtures.cgr_response_template([])},
            ],
        )

        # Then
        api.update_stock_quantity_to_match_cinema_venue_provider_remaining_places(offer)

        assert stock.remainingQuantity == 0
        assert stock.quantity == stock.dnBookedQuantity

        mocked_async_index_offer_ids.assert_called_once_with(
            [offer.id],
            reason=search.IndexationReason.CINEMA_STOCK_QUANTITY_UPDATE,
            log_extra={"sold_out": True},
        )

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
        mocked_async_index_offer_ids.assert_called_once_with(
            [offer.id],
            reason=search.IndexationReason.CINEMA_STOCK_QUANTITY_UPDATE,
            log_extra={"sold_out": True},
        )


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
        provider = providers_factories.APIProviderFactory()
        ean = "ean-de-test"
        factories.ThingProductFactory(
            subcategoryId=subcategories.LIVRE_PAPIER.id,
            extraData={"ean": ean},
            lastProvider=provider,
            idAtProviders=ean,
            gcuCompatibilityType=models.GcuCompatibilityType.PROVIDER_INCOMPATIBLE,
        )

        # When
        api.approves_provider_product_and_rejected_offers(ean)

        # Then
        product = models.Product.query.filter(models.Product.extraData["ean"].astext == ean).one()
        assert product.isGcuCompatible

        mocked_async_index_offer_ids.assert_not_called()

    @mock.patch("pcapi.core.search.async_index_offer_ids")
    def test_should_approve_product_and_offers_on_approved_offers(self, mocked_async_index_offer_ids):
        # Given
        provider = providers_factories.APIProviderFactory()
        ean = "ean-de-test"
        product = factories.ThingProductFactory(
            subcategoryId=subcategories.LIVRE_PAPIER.id,
            extraData={"ean": ean},
            lastProvider=provider,
            idAtProviders=ean,
            gcuCompatibilityType=models.GcuCompatibilityType.PROVIDER_INCOMPATIBLE,
        )

        factories.OfferFactory(product=product)
        factories.OfferFactory(product=product)

        # When
        api.approves_provider_product_and_rejected_offers(ean)

        # Then
        product = models.Product.query.filter(models.Product.extraData["ean"].astext == ean).one()
        assert product.isGcuCompatible

        assert models.Offer.query.filter(models.Offer.validation == OfferValidationStatus.APPROVED).count() == 2

        mocked_async_index_offer_ids.assert_not_called()

    @mock.patch("pcapi.core.search.async_index_offer_ids")
    def test_should_approve_product_and_offers_with_one_rejected_offer_for_gcu_inappropriate(
        self, mocked_async_index_offer_ids
    ):
        # Given
        provider = providers_factories.APIProviderFactory()
        ean = "ean-de-test"
        product = factories.ThingProductFactory(
            subcategoryId=subcategories.LIVRE_PAPIER.id,
            extraData={"ean": ean},
            lastProvider=provider,
            idAtProviders=ean,
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
        product = models.Product.query.filter(models.Product.extraData["ean"].astext == ean).one()
        assert product.isGcuCompatible

        assert models.Offer.query.filter(models.Offer.validation == OfferValidationStatus.APPROVED).count() == 2
        assert (
            models.Offer.query.filter(
                models.Offer.id == offert_to_approve.id, models.Offer.lastValidationType == OfferValidationType.AUTO
            ).count()
            == 1
        )

        mocked_async_index_offer_ids.assert_called()
        assert set(mocked_async_index_offer_ids.call_args[0][0]) == set([offert_to_approve.id])

    @mock.patch("pcapi.core.search.async_index_offer_ids")
    def test_should_approve_product_and_offers_with_one_offer_manually_rejected(self, mocked_async_index_offer_ids):
        # Given
        provider = providers_factories.APIProviderFactory()
        ean = "ean-de-test"
        product = factories.ThingProductFactory(
            subcategoryId=subcategories.LIVRE_PAPIER.id,
            extraData={"ean": ean},
            lastProvider=provider,
            idAtProviders=ean,
            gcuCompatibilityType=models.GcuCompatibilityType.PROVIDER_INCOMPATIBLE,
        )

        factories.OfferFactory(
            product=product, validation=OfferValidationStatus.REJECTED, lastValidationType=OfferValidationType.MANUAL
        )

        # When
        api.approves_provider_product_and_rejected_offers(ean)

        # Then
        product = models.Product.query.filter(models.Product.extraData["ean"].astext == ean).one()
        assert product.isGcuCompatible

        assert models.Offer.query.filter(models.Offer.validation == OfferValidationStatus.REJECTED).count() == 1
        mocked_async_index_offer_ids.assert_not_called()

    @mock.patch("pcapi.core.search.async_index_offer_ids")
    def test_should_approve_product_and_offers_with_one_offer_auto_rejected(self, mocked_async_index_offer_ids):
        # Given
        provider = providers_factories.APIProviderFactory()
        ean = "ean-de-test"
        product = factories.ThingProductFactory(
            subcategoryId=subcategories.LIVRE_PAPIER.id,
            extraData={"ean": ean},
            lastProvider=provider,
            idAtProviders=ean,
            gcuCompatibilityType=models.GcuCompatibilityType.PROVIDER_INCOMPATIBLE,
        )

        factories.OfferFactory(
            product=product, validation=OfferValidationStatus.REJECTED, lastValidationType=OfferValidationType.AUTO
        )

        # When
        api.approves_provider_product_and_rejected_offers(ean)

        # Then
        product = models.Product.query.filter(models.Product.extraData["ean"].astext == ean).one()
        assert product.isGcuCompatible

        assert models.Offer.query.filter(models.Offer.validation == OfferValidationStatus.REJECTED).count() == 1
        mocked_async_index_offer_ids.assert_not_called()

    def test_should_approve_product_and_offers_with_update_exception(self):
        # Given
        provider = providers_factories.APIProviderFactory()
        ean = "ean-de-test"
        product = factories.ThingProductFactory(
            subcategoryId=subcategories.LIVRE_PAPIER.id,
            extraData={"ean": ean},
            lastProvider=provider,
            idAtProviders=ean,
            gcuCompatibilityType=models.GcuCompatibilityType.PROVIDER_INCOMPATIBLE,
        )

        factories.OfferFactory(
            product=product,
            validation=OfferValidationStatus.REJECTED,
            lastValidationType=OfferValidationType.CGU_INCOMPATIBLE_PRODUCT,
        )

        # When
        with pytest.raises(NotUpdateProductOrOffers):
            with patch("pcapi.models.db.session.commit", side_effect=Exception):
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
class FillOffersExtraDataFromProductExtraDataTest:
    @mock.patch("pcapi.core.search.async_index_offer_ids")
    def test_should_no_fill_offer_extra_data_from_product_data_with_unknown_product(self, mocked_async_index_offer_ids):
        # Given
        product_id = 404

        # When
        with pytest.raises(ProductNotFound):
            api.fill_offer_extra_data_from_product_data(product_id)

        # Then
        mocked_async_index_offer_ids.assert_not_called()

    @mock.patch("pcapi.core.search.async_index_offer_ids")
    def test_should_fill_offer_extra_data_from_product_data_with_no_offers(self, mocked_async_index_offer_ids):
        # Given
        provider = providers_factories.APIProviderFactory()
        ean = "ean-de-test"
        product = factories.ThingProductFactory(
            subcategoryId=subcategories.LIVRE_PAPIER.id,
            extraData={"gtl_id": "12345678"},
            lastProvider=provider,
            idAtProviders=ean,
        )

        # When
        api.fill_offer_extra_data_from_product_data(product.id)

        # Then
        mocked_async_index_offer_ids.assert_not_called()

    @mock.patch("pcapi.core.search.async_index_offer_ids")
    def test_should_fill_offer_extra_data_from_product_data_when_offer_not_have_extra_data(
        self, mocked_async_index_offer_ids
    ):
        # Given
        provider = providers_factories.APIProviderFactory()
        ean = "ean-de-test"
        product = factories.ThingProductFactory(
            subcategoryId=subcategories.LIVRE_PAPIER.id,
            extraData={
                "gtl_id": "12345678",
                "csr_id": "1901",
                "code_clil": "4300",
                "isbn": None,
                "dewey": None,
                "rayon": "Bandes dessinées adultes / Comics",
                "author": "Collectif",
                "bookFormat": "BEAUX LIVRES",
                "prix_livre": "4.90",
                "editeur": "Panini Comics Mag",
                "comic_series": None,
                "distributeur": "Makassar",
                "date_parution": "24/12/2015",
            },
            lastProvider=provider,
            idAtProviders=ean,
            name="title",
        )
        offer = factories.OfferFactory(product=product)

        # When
        api.fill_offer_extra_data_from_product_data(product.id)

        # Then
        offer = models.Offer.query.filter_by(id=offer.id).one()
        assert offer.name == "title"
        assert offer.extraData["gtl_id"] == "12345678"
        assert offer.extraData["csr_id"] == "1901"
        assert offer.extraData["code_clil"] == "4300"
        assert not offer.extraData["isbn"]
        assert not offer.extraData["dewey"]
        assert offer.extraData["rayon"] == "Bandes dessinées adultes / Comics"
        assert offer.extraData["author"] == "Collectif"
        assert offer.extraData["bookFormat"] == "BEAUX LIVRES"
        assert offer.extraData["prix_livre"] == "4.90"
        assert offer.extraData["editeur"] == "Panini Comics Mag"
        assert not offer.extraData["comic_series"]
        assert offer.extraData["distributeur"] == "Makassar"
        assert offer.extraData["date_parution"] == "24/12/2015"

        mocked_async_index_offer_ids.assert_called()
        assert set(mocked_async_index_offer_ids.call_args[0][0]) == set([offer.id])

    @mock.patch("pcapi.core.search.async_index_offer_ids")
    def test_should_fill_offer_extra_data_from_product_data_when_offer_have_empty_extra_data(
        self, mocked_async_index_offer_ids
    ):
        # Given
        provider = providers_factories.APIProviderFactory()
        ean = "ean-de-test"
        product = factories.ThingProductFactory(
            subcategoryId=subcategories.LIVRE_PAPIER.id,
            extraData={
                "gtl_id": "12345678",
                "csr_id": "1901",
                "code_clil": "4300",
                "isbn": None,
                "dewey": None,
                "rayon": "Bandes dessinées adultes / Comics",
                "author": "Collectif",
                "bookFormat": "BEAUX LIVRES",
                "prix_livre": "4.90",
                "editeur": "Panini Comics Mag",
                "comic_series": None,
                "distributeur": "Makassar",
                "date_parution": "24/12/2015",
            },
            lastProvider=provider,
            idAtProviders=ean,
            name="title",
        )
        offer = factories.OfferFactory(product=product, extraData={})

        # When
        api.fill_offer_extra_data_from_product_data(product.id)

        # Then
        offer = models.Offer.query.filter_by(id=offer.id).one()
        assert offer.name == "title"
        assert offer.extraData["gtl_id"] == "12345678"
        assert offer.extraData["csr_id"] == "1901"
        assert offer.extraData["code_clil"] == "4300"
        assert not offer.extraData["isbn"]
        assert not offer.extraData["dewey"]
        assert offer.extraData["rayon"] == "Bandes dessinées adultes / Comics"
        assert offer.extraData["author"] == "Collectif"
        assert offer.extraData["bookFormat"] == "BEAUX LIVRES"
        assert offer.extraData["prix_livre"] == "4.90"
        assert offer.extraData["editeur"] == "Panini Comics Mag"
        assert not offer.extraData["comic_series"]
        assert offer.extraData["distributeur"] == "Makassar"
        assert offer.extraData["date_parution"] == "24/12/2015"

        mocked_async_index_offer_ids.assert_called()
        assert set(mocked_async_index_offer_ids.call_args[0][0]) == set([offer.id])

    @mock.patch("pcapi.core.search.async_index_offer_ids")
    def test_should_fill_offer_extra_data_from_product_data_when_offer_have_gtl(self, mocked_async_index_offer_ids):
        # Given
        provider = providers_factories.APIProviderFactory()
        ean = "ean-de-test"
        product = factories.ThingProductFactory(
            name="title2",
            subcategoryId=subcategories.LIVRE_PAPIER.id,
            extraData={
                "gtl_id": "12345678",
                "csr_id": "1901",
                "code_clil": "4300",
                "isbn": None,
                "dewey": None,
                "rayon": "Bandes dessinées adultes / Comics",
                "author": "Collectif",
                "bookFormat": "BEAUX LIVRES",
                "prix_livre": "4.90",
                "editeur": "Panini Comics Mag",
                "comic_series": None,
                "distributeur": "Makassar",
                "date_parution": "24/12/2015",
            },
            lastProvider=provider,
            idAtProviders=ean,
        )

        offer = factories.OfferFactory(
            product=product,
            name="title",
            extraData={
                "gtl_id": "10000000",
                "csr_id": "1661",
                "code_clil": "5000",
                "isbn": "dd",
                "dewey": "1",
                "rayon": "Adultes / Comics",
                "author": "Lectif",
                "bookFormat": "LIVRES",
                "prix_livre": "66.90",
                "editeur": "Comics Mag",
                "comic_series": None,
                "distributeur": "LaRkassar",
                "date_parution": "30/12/2010",
            },
        )

        # When
        api.fill_offer_extra_data_from_product_data(product.id)

        # Then
        offer = models.Offer.query.filter_by(id=offer.id).one()
        assert offer.extraData["gtl_id"] == "12345678"
        assert offer.name == "title2"
        assert offer.extraData["gtl_id"] == "12345678"
        assert offer.extraData["csr_id"] == "1901"
        assert offer.extraData["code_clil"] == "4300"
        assert not offer.extraData["isbn"]
        assert not offer.extraData["dewey"]
        assert offer.extraData["rayon"] == "Bandes dessinées adultes / Comics"
        assert offer.extraData["author"] == "Collectif"
        assert offer.extraData["bookFormat"] == "BEAUX LIVRES"
        assert offer.extraData["prix_livre"] == "4.90"
        assert offer.extraData["editeur"] == "Panini Comics Mag"
        assert not offer.extraData["comic_series"]
        assert offer.extraData["distributeur"] == "Makassar"
        assert offer.extraData["date_parution"] == "24/12/2015"

        mocked_async_index_offer_ids.assert_called()
        assert set(mocked_async_index_offer_ids.call_args[0][0]) == set([offer.id])

    @mock.patch("pcapi.core.search.async_index_offer_ids")
    def test_should_fill_offer_extra_data_from_product_data_when_many_offers(self, mocked_async_index_offer_ids):
        # Given
        provider = providers_factories.APIProviderFactory()
        ean = "ean-de-test"
        product = factories.ThingProductFactory(
            subcategoryId=subcategories.LIVRE_PAPIER.id,
            extraData={"gtl_id": "12345678"},
            lastProvider=provider,
            idAtProviders=ean,
        )

        offer = factories.OfferFactory(product=product, extraData={"gtl_id": "10000000"})
        offer2 = factories.OfferFactory(product=product, extraData={"gtl_id": "12000000"})

        # When
        api.fill_offer_extra_data_from_product_data(product.id)

        # Then
        offers = models.Offer.query.filter_by(productId=product.id).all()
        assert all(offer.extraData["gtl_id"] == "12345678" for offer in offers)

        mocked_async_index_offer_ids.assert_called()
        assert set(mocked_async_index_offer_ids.call_args[0][0]) == set([offer.id, offer2.id])

    def test_should_fill_offer_extra_data_from_product_data_with_update_exception(self):
        # Given
        provider = providers_factories.APIProviderFactory()
        ean = "ean-de-test"
        product = factories.ThingProductFactory(
            subcategoryId=subcategories.LIVRE_PAPIER.id,
            extraData={"gtl_id": "12345678"},
            lastProvider=provider,
            idAtProviders=ean,
        )

        factories.OfferFactory(product=product, extraData={"gtl_id": "10000000"})

        # When
        with pytest.raises(NotUpdateProductOrOffers):
            with patch("pcapi.models.db.session.commit", side_effect=Exception):
                api.fill_offer_extra_data_from_product_data(product.id)


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
        assert finance_models.Pricing.query.filter_by(id=later_pricing_id).count() == 0

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
class CreateMovieProductFromProviderTest:
    @classmethod
    def setup_class(cls):
        cls.allocine_provider = get_allocine_products_provider()
        cls.allocine_stocks_provider = providers_repository.get_provider_by_local_class("AllocineStocks")
        cls.boost_provider = providers_repository.get_provider_by_local_class("BoostStocks")

    def setup_method(self):
        models.Product.query.delete()

    def teardown_method(self):
        models.Product.query.delete()

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
        # Given
        movie = self._get_movie(allocine_id="12345")

        # When
        product = api.upsert_movie_product_from_provider(movie, self.allocine_provider, "idAllocine")

        # Then
        assert product.extraData["allocineId"] == 12345
        assert product.extraData.get("visa") is None

    def test_do_nothing_if_no_allocine_id_and_no_visa(self):
        # Given
        movie = self._get_movie(allocine_id=None, visa=None)

        # When
        with assert_num_queries(0):
            product = api.upsert_movie_product_from_provider(movie, self.allocine_provider, "idAllocine")

        # Then
        assert product is None

    def test_does_not_create_product_if_exists(self):
        # Given
        product = factories.ProductFactory(extraData={"allocineId": 12345})
        movie = self._get_movie(allocine_id="12345")

        # When
        new_product = api.upsert_movie_product_from_provider(movie, self.allocine_provider, "idAllocine")

        # Then
        assert product.id == new_product.id

    def test_updates_product_if_exists(self):
        # Given
        product = factories.ProductFactory(extraData={"allocineId": 12345})
        movie = self._get_movie(allocine_id="12345")

        # When
        api.upsert_movie_product_from_provider(movie, self.allocine_provider, "idAllocine")

        # Then
        assert product.lastProvider.id == self.allocine_provider.id

    def test_does_not_update_allocine_product_from_non_allocine_synchro(self):
        # Given
        product = factories.ProductFactory(
            idAtProviders="idAllocine", lastProviderId=self.allocine_provider.id, extraData={"allocineId": 12345}
        )
        movie = self._get_movie(allocine_id="12345")

        # When
        api.upsert_movie_product_from_provider(movie, self.boost_provider, "idBoost")

        # Then
        assert product.idAtProviders == "idAllocine"
        assert product.lastProvider.id == self.allocine_provider.id

    def test_updates_allocine_product_from_allocine_stocks_synchro(self):
        # Given
        product = factories.ProductFactory(
            idAtProviders="idAllocine", lastProviderId=self.allocine_provider.id, extraData={"allocineId": 12345}
        )
        movie = self._get_movie(allocine_id="12345")

        # When
        api.upsert_movie_product_from_provider(movie, self.allocine_stocks_provider, "idAllocineStocks")

        # Then
        assert product.idAtProviders == "idAllocineStocks"
        assert product.lastProvider.id == self.allocine_stocks_provider.id

    def test_updates_product_from_same_synchro(self):
        # Given
        product = factories.ProductFactory(
            idAtProviders="idBoost1", lastProviderId=self.boost_provider.id, extraData={"allocineId": 12345}
        )
        movie = self._get_movie(allocine_id="12345")

        # When
        api.upsert_movie_product_from_provider(movie, self.boost_provider, "idBoost2")

        # Then
        assert product.idAtProviders == "idBoost2"
        assert product.lastProvider.id == self.boost_provider.id

    def test_updates_allocine_id_when_updates_product_by_visa(self):
        # Given
        product = factories.ProductFactory(
            idAtProviders="idBoost", lastProviderId=self.boost_provider.id, extraData={"visa": "54321"}
        )
        movie = self._get_movie(allocine_id="12345", visa="54321")

        # When
        api.upsert_movie_product_from_provider(movie, self.allocine_stocks_provider, "idAllocine")

        # Then
        assert product.idAtProviders == "idAllocine"
        assert product.extraData["allocineId"] == 12345

    def test_updates_visa_when_updating_with_visa_provided(self):
        # Given
        product = factories.ProductFactory(
            idAtProviders="idBoost",
            lastProviderId=self.boost_provider.id,
            extraData={"allocineId": 12345, "visa": "54321"},
        )
        movie = self._get_movie(allocine_id="12345", visa="54322")

        # When
        api.upsert_movie_product_from_provider(movie, self.allocine_stocks_provider, "idAllocine")

        # Then
        assert product.idAtProviders == "idAllocine"
        assert product.extraData["allocineId"] == 12345
        assert product.extraData["visa"] == "54322"

    def test_keep_visa_when_updating_with_no_visa_provided(self):
        # Given
        product = factories.ProductFactory(
            idAtProviders="idBoost",
            lastProviderId=self.boost_provider.id,
            extraData={"allocineId": 12345, "visa": "54321"},
        )
        movie = self._get_movie(allocine_id="12345", visa=None)

        # When
        api.upsert_movie_product_from_provider(movie, self.allocine_stocks_provider, "idAllocine")

        # Then
        assert product.idAtProviders == "idAllocine"
        assert product.extraData["allocineId"] == 12345
        assert product.extraData["visa"] == "54321"

    def test_does_not_update_data_when_provided_data_is_none(self):
        # Given
        product = factories.ProductFactory(
            idAtProviders="idBoost",
            lastProviderId=self.boost_provider.id,
            extraData={"allocineId": 12345, "title": "Mon vieux film"},
        )
        movie = self._get_movie(allocine_id="12345", visa=None)
        movie.extra_data = None

        # When
        api.upsert_movie_product_from_provider(movie, self.allocine_stocks_provider, "idAllocine")

        # Then
        assert product.idAtProviders == "idAllocine"
        assert product.extraData == {"allocineId": 12345, "title": "Mon vieux film"}
