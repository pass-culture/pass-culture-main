import dataclasses
import datetime
import logging
from unittest import mock

import pytest
from dateutil.relativedelta import relativedelta

import pcapi.core.mails.testing as mails_testing
import pcapi.core.offerers.factories as offerers_factories
import pcapi.core.offers.factories as offers_factories
import pcapi.core.users.factories as users_factories
from pcapi.core.bookings import factories as bookings_factories
from pcapi.core.bookings import models as bookings_models
from pcapi.core.mails.transactional import sendinblue_template_ids
from pcapi.core.offers import models as offers_models
from pcapi.models import db
from pcapi.utils.date import format_into_utc_date


@pytest.mark.usefixtures("db_session")
class Returns200Test:
    def test_edit_one_stock(self, client):
        offer = offers_factories.EventOfferFactory(isActive=False, validation=offers_models.OfferValidationStatus.DRAFT)
        existing_stock = offers_factories.EventStockFactory(offer=offer, quantity=10)
        price_cat_label = offers_factories.PriceCategoryLabelFactory(venue=offer.venue, label="Carré Or")
        price_category = offers_factories.PriceCategoryFactory(
            offer=offer, price=23, priceCategoryLabel=price_cat_label
        )
        offerers_factories.UserOffererFactory(user__email="user@example.com", offerer=offer.venue.managingOfferer)
        beginning = datetime.datetime.utcnow() + datetime.timedelta(days=1)

        response = client.with_session_auth("user@example.com").patch(
            "/stocks/bulk",
            json={
                "offerId": offer.id,
                "stocks": [
                    {
                        "id": existing_stock.id,
                        "beginningDatetime": format_into_utc_date(beginning),
                        "priceCategoryId": price_category.id,
                        "quantity": 14,
                    }
                ],
            },
        )

        assert response.status_code == 200
        assert response.json == {"stocks_count": 1}

        updated_stock = db.session.query(offers_models.Stock).first()
        assert offer.id == updated_stock.offerId
        assert updated_stock.priceCategoryId == price_category.id
        assert updated_stock.quantity == 14
        assert db.session.query(offers_models.Stock).count() == 1

    def test_do_not_edit_one_stock_when_duplicated(self, client):
        offer = offers_factories.EventOfferFactory()
        beginning = datetime.datetime.utcnow() + datetime.timedelta(days=1)
        tomorrow = beginning + datetime.timedelta(days=1)
        price_cat_label = offers_factories.PriceCategoryLabelFactory(venue=offer.venue, label="Tarif 1")
        price_category = offers_factories.PriceCategoryFactory(
            offer=offer, priceCategoryLabel=price_cat_label, price=10
        )
        existing_stock = offers_factories.EventStockFactory(
            offer=offer,
            beginningDatetime=format_into_utc_date(beginning),
            bookingLimitDatetime=format_into_utc_date(beginning),
            priceCategory=price_category,
            quantity=10,
        )
        offers_factories.EventStockFactory(
            offer=offer,
            beginningDatetime=format_into_utc_date(tomorrow),
            bookingLimitDatetime=format_into_utc_date(beginning),
            priceCategory=price_category,
            quantity=10,
        )
        offerers_factories.UserOffererFactory(user__email="user@example.com", offerer=offer.venue.managingOfferer)

        response = client.with_session_auth("user@example.com").patch(
            "/stocks/bulk",
            json={
                "offerId": offer.id,
                "stocks": [
                    {
                        "id": existing_stock.id,
                        "priceCategoryId": price_category.id,
                        "quantity": 20,
                        "beginningDatetime": format_into_utc_date(tomorrow),
                        "bookingLimitDatetime": format_into_utc_date(beginning),
                    }
                ],
            },
        )

        assert response.status_code == 200
        assert response.json == {"stocks_count": 0}
        assert existing_stock.beginningDatetime == beginning  # didn't change
        assert existing_stock.quantity == 10  # didn't change

    def test_edit_one_event_stock_created_with_price_category(self, client, caplog):
        offer = offers_factories.EventOfferFactory(isActive=False, validation=offers_models.OfferValidationStatus.DRAFT)
        old_price_category = offers_factories.PriceCategoryFactory(offer=offer, priceCategoryLabel__venue=offer.venue)
        new_price_category = offers_factories.PriceCategoryFactory(
            offer=offer, priceCategoryLabel__venue=offer.venue, price=25
        )
        existing_stock = offers_factories.StockFactory(offer=offer, price=10, priceCategory=old_price_category)
        beginning = datetime.datetime.utcnow() + relativedelta(days=10)
        offerers_factories.UserOffererFactory(user__email="user@example.com", offerer=offer.venue.managingOfferer)

        with caplog.at_level(logging.INFO):
            response = client.with_session_auth("user@example.com").patch(
                "/stocks/bulk",
                json={
                    "offerId": offer.id,
                    "stocks": [
                        {
                            "id": existing_stock.id,
                            "beginningDatetime": format_into_utc_date(beginning),
                            "bookingLimitDatetime": format_into_utc_date(beginning),
                            "priceCategoryId": new_price_category.id,
                        }
                    ],
                },
            )

        assert response.status_code == 200
        assert response.json == {"stocks_count": 1}

        edited_stock = db.session.query(offers_models.Stock).first()
        assert offer.id == edited_stock.offerId
        assert db.session.query(offers_models.Stock).count() == 1
        assert edited_stock.priceCategory == new_price_category
        assert edited_stock.price == 25

        target_log_message = "Successfully updated stock"
        log = next(record for record in caplog.records if record.message == target_log_message)

        changes = log.extra["changes"]

        expected_updated_field = {"beginningDatetime", "bookingLimitDatetime", "priceCategory", "price"}
        assert expected_updated_field <= set(changes)

        assert changes["beginningDatetime"]["old_value"] != changes["beginningDatetime"]["new_value"]
        assert changes["beginningDatetime"]["new_value"] == beginning

        assert changes["bookingLimitDatetime"]["old_value"] != changes["bookingLimitDatetime"]["new_value"]
        assert changes["bookingLimitDatetime"]["new_value"] == beginning

        assert changes["priceCategory"]["old_value"] != changes["priceCategory"]["new_value"]
        assert changes["priceCategory"]["new_value"] == new_price_category

    def test_sends_email_if_beginning_date_changes_on_edition(self, client):
        offer = offers_factories.EventOfferFactory(
            venue__bookingEmail="venue@postponed.net", bookingEmail="offer@bookingemail.fr"
        )
        price_cat_label = offers_factories.PriceCategoryLabelFactory(venue=offer.venue, label="Tarif 1")
        price_cat = offers_factories.PriceCategoryFactory(offer=offer, priceCategoryLabel=price_cat_label, price=10)
        existing_stock = offers_factories.EventStockFactory(offer=offer, priceCategory=price_cat)
        beginning = datetime.datetime.utcnow() + relativedelta(days=10)
        offerers_factories.UserOffererFactory(user__email="user@example.com", offerer=offer.venue.managingOfferer)

        bookings_factories.BookingFactory(stock=existing_stock, user__email="beneficiary@bookingEmail.fr")
        bookings_factories.CancelledBookingFactory(stock=existing_stock)

        response = client.with_session_auth("user@example.com").patch(
            "/stocks/bulk",
            json={
                "offerId": offer.id,
                "stocks": [
                    {
                        "id": existing_stock.id,
                        "priceCategoryId": price_cat.id,
                        "beginningDatetime": format_into_utc_date(beginning),
                        "bookingLimitDatetime": format_into_utc_date(beginning),
                    },
                ],
            },
        )

        assert response.status_code == 200
        assert response.json == {"stocks_count": 1}

        stock = db.session.query(offers_models.Stock).one()
        assert stock.beginningDatetime == beginning
        assert stock.bookingLimitDatetime == beginning

        assert len(mails_testing.outbox) == 2
        assert mails_testing.outbox[0]["template"] == dataclasses.asdict(
            sendinblue_template_ids.TransactionalEmail.EVENT_OFFER_POSTPONED_CONFIRMATION_TO_PRO.value
        )
        assert mails_testing.outbox[0]["To"] == "venue@postponed.net"
        assert mails_testing.outbox[1]["template"] == dataclasses.asdict(
            sendinblue_template_ids.TransactionalEmail.BOOKING_POSTPONED_BY_PRO_TO_BENEFICIARY.value
        )
        assert mails_testing.outbox[1]["To"] == "beneficiary@bookingEmail.fr"

    @mock.patch("pcapi.core.bookings.api.update_cancellation_limit_dates")
    def should_update_bookings_cancellation_limit_date_on_delayed_event(
        self, mock_update_cancellation_limit_dates, client
    ):
        now = datetime.datetime.utcnow()
        event_in_4_days = now + relativedelta(days=4)
        event_reported_in_10_days = now + relativedelta(days=10)
        offer = offers_factories.EventOfferFactory(bookingEmail="test@bookingEmail.fr")
        price_cat_label = offers_factories.PriceCategoryLabelFactory(venue=offer.venue, label="Tarif 1")
        price_cat = offers_factories.PriceCategoryFactory(offer=offer, priceCategoryLabel=price_cat_label, price=10)

        existing_stock = offers_factories.EventStockFactory(
            offer=offer, beginningDatetime=event_in_4_days, priceCategory=price_cat
        )
        booking = bookings_factories.BookingFactory(stock=existing_stock, dateCreated=now)
        offerers_factories.UserOffererFactory(user__email="user@example.com", offerer=offer.venue.managingOfferer)

        response = client.with_session_auth("user@example.com").patch(
            "/stocks/bulk",
            json={
                "offerId": offer.id,
                "stocks": [
                    {
                        "id": existing_stock.id,
                        "priceCategoryId": price_cat.id,
                        "beginningDatetime": format_into_utc_date(event_reported_in_10_days),
                        "bookingLimitDatetime": format_into_utc_date(existing_stock.bookingLimitDatetime),
                    },
                ],
            },
        )

        assert response.status_code == 200
        mock_update_cancellation_limit_dates.assert_called_once_with([booking], event_reported_in_10_days)

    def should_invalidate_booking_token_when_event_is_reported(self, client):
        now = datetime.datetime.utcnow()
        booking_made_3_days_ago = now - relativedelta(days=3)
        event_in_4_days = now + relativedelta(days=4)
        event_reported_in_10_days = now + relativedelta(days=10)
        offer = offers_factories.EventOfferFactory(bookingEmail="test@bookingEmail.fr")
        price_cat_label = offers_factories.PriceCategoryLabelFactory(venue=offer.venue, label="Tarif 1")
        price_cat = offers_factories.PriceCategoryFactory(offer=offer, priceCategoryLabel=price_cat_label, price=10)

        existing_stock = offers_factories.EventStockFactory(
            offer=offer, beginningDatetime=event_in_4_days, priceCategory=price_cat
        )
        booking = bookings_factories.UsedBookingFactory(stock=existing_stock, dateCreated=booking_made_3_days_ago)
        offerers_factories.UserOffererFactory(user__email="user@example.com", offerer=offer.venue.managingOfferer)

        response = client.with_session_auth("user@example.com").patch(
            "/stocks/bulk",
            json={
                "offerId": offer.id,
                "stocks": [
                    {
                        "id": existing_stock.id,
                        "priceCategoryId": price_cat.id,
                        "beginningDatetime": format_into_utc_date(event_reported_in_10_days),
                        "bookingLimitDatetime": format_into_utc_date(existing_stock.bookingLimitDatetime),
                    },
                ],
            },
        )

        assert response.status_code == 200
        updated_booking = db.session.get(bookings_models.Booking, booking.id)
        assert updated_booking.status is not bookings_models.BookingStatus.USED
        assert updated_booking.dateUsed is None
        assert updated_booking.cancellationLimitDate == booking.cancellationLimitDate

    def should_not_invalidate_booking_token_when_event_is_reported_in_less_than_48_hours(self, client):
        now = datetime.datetime.utcnow() + relativedelta(hours=4)
        date_used_in_48_hours = now + relativedelta(days=2)
        event_in_3_days = now + relativedelta(days=3)
        event_reported_in_less_48_hours = now + relativedelta(days=1)
        offer = offers_factories.EventOfferFactory(bookingEmail="test@bookingEmail.fr")
        price_cat_label = offers_factories.PriceCategoryLabelFactory(venue=offer.venue, label="Tarif 1")
        price_cat = offers_factories.PriceCategoryFactory(offer=offer, priceCategoryLabel=price_cat_label, price=10)

        existing_stock = offers_factories.EventStockFactory(
            offer=offer,
            beginningDatetime=event_in_3_days,
            priceCategory=price_cat,
            bookingLimitDatetime=now,
        )
        booking = bookings_factories.UsedBookingFactory(
            stock=existing_stock, dateCreated=now, dateUsed=date_used_in_48_hours
        )
        offerers_factories.UserOffererFactory(user__email="user@example.com", offerer=offer.venue.managingOfferer)

        response = client.with_session_auth("user@example.com").patch(
            "/stocks/bulk",
            json={
                "offerId": offer.id,
                "stocks": [
                    {
                        "id": existing_stock.id,
                        "priceCategoryId": price_cat.id,
                        "beginningDatetime": format_into_utc_date(event_reported_in_less_48_hours),
                        "bookingLimitDatetime": format_into_utc_date(existing_stock.bookingLimitDatetime),
                    },
                ],
            },
        )

        assert response.status_code == 200
        updated_booking = db.session.get(bookings_models.Booking, booking.id)
        assert updated_booking.status is bookings_models.BookingStatus.USED
        assert updated_booking.dateUsed == date_used_in_48_hours

    def test_update_event_stock_quantity(self, client):
        beginning = datetime.datetime.utcnow() + datetime.timedelta(days=1)
        offer = offers_factories.EventOfferFactory(isActive=False, validation=offers_models.OfferValidationStatus.DRAFT)
        price_category_1 = offers_factories.PriceCategoryFactory(offer=offer, price=10)
        existing_stock = offers_factories.EventStockFactory(
            offer=offer,
            beginningDatetime=format_into_utc_date(beginning),
            bookingLimitDatetime=format_into_utc_date(beginning),
            priceCategory=price_category_1,
            quantity=20,
        )
        offerers_factories.UserOffererFactory(user__email="user@example.com", offerer=offer.venue.managingOfferer)

        response = client.with_session_auth("user@example.com").patch(
            "/stocks/bulk",
            json={
                "offerId": offer.id,
                "stocks": [
                    {
                        "priceCategoryId": price_category_1.id,
                        "id": existing_stock.id,
                        "quantity": 42,
                        "beginningDatetime": format_into_utc_date(beginning),
                        "bookingLimitDatetime": format_into_utc_date(beginning),
                    }
                ],
            },
        )

        assert response.status_code == 200
        created_stock = db.session.query(offers_models.Stock).first()
        assert offer.id == created_stock.offerId
        assert created_stock.quantity == 42


@pytest.mark.usefixtures("db_session")
class Returns400Test:
    def when_missing_offer_id(self, client):
        offer = offers_factories.EventOfferFactory()
        offerers_factories.UserOffererFactory(user__email="user@example.com", offerer=offer.venue.managingOfferer)
        booking_limit_datetime = datetime.datetime(2019, 2, 14)

        response = client.with_session_auth("user@example.com").patch(
            "/stocks/bulk",
            json={
                "stocks": [
                    {"quantity": -2, "bookingLimitDatetime": format_into_utc_date(booking_limit_datetime)},
                ]
            },
        )

        assert response.status_code == 400
        assert response.json == {
            "offerId": ["Ce champ est obligatoire"],
            "stocks.0.id": ["Ce champ est obligatoire"],
            "stocks.0.beginningDatetime": ["Ce champ est obligatoire"],
            "stocks.0.bookingLimitDatetime": ["The datetime must be in the future."],
            "stocks.0.priceCategoryId": ["Ce champ est obligatoire"],
            "stocks.0.quantity": ["Saisissez un nombre supérieur ou égal à 0"],
        }

    def test_patch_non_approved_offer_fails(self, client):
        offer = offers_factories.EventOfferFactory(validation=offers_models.OfferValidationStatus.PENDING)
        stock = offers_factories.EventStockFactory(offer=offer)
        offerers_factories.UserOffererFactory(user__email="user@example.com", offerer=offer.venue.managingOfferer)

        response = client.with_session_auth("user@example.com").patch(
            "/stocks/bulk",
            json={
                "offerId": offer.id,
                "stocks": [
                    {
                        "id": stock.id,
                        "quantity": 14,
                        "priceCategoryId": stock.priceCategoryId,
                        "beginningDatetime": format_into_utc_date(stock.beginningDatetime),
                    }
                ],
            },
        )

        assert response.status_code == 400
        assert response.json["global"] == ["Les offres refusées ou en attente de validation ne sont pas modifiables"]

    def test_when_stock_does_not_belong_to_offer(self, client):
        offer = offers_factories.EventOfferFactory(isActive=False, validation=offers_models.OfferValidationStatus.DRAFT)
        price_category = offers_factories.PriceCategoryFactory(offer=offer, price=23)
        existing_stock = offers_factories.EventStockFactory()
        offerers_factories.UserOffererFactory(user__email="user@example.com", offerer=offer.venue.managingOfferer)

        response = client.with_session_auth("user@example.com").patch(
            "/stocks/bulk",
            json={
                "offerId": offer.id,
                "stocks": [
                    {
                        "id": existing_stock.id,
                        "quantity": 14,
                        "priceCategoryId": price_category.id,
                        "beginningDatetime": format_into_utc_date(existing_stock.beginningDatetime),
                    }
                ],
            },
        )

        assert response.status_code == 400
        assert response.json == {"stock_id": [f"Pas de stocks avec les ids: {existing_stock.id}"]}

    def test_beginning_datetime_after_booking_limit_datetime(self, client):
        stock = offers_factories.EventStockFactory()
        beginning = datetime.datetime.utcnow() + datetime.timedelta(days=1)
        after_beginning = beginning + datetime.timedelta(days=1)
        offerers_factories.UserOffererFactory(user__email="user@example.com", offerer=stock.offer.venue.managingOfferer)

        response = client.with_session_auth("user@example.com").patch(
            "/stocks/bulk",
            json={
                "offerId": stock.offer.id,
                "stocks": [
                    {
                        "id": stock.id,
                        "beginningDatetime": format_into_utc_date(beginning),
                        "bookingLimitDatetime": format_into_utc_date(after_beginning),
                        "priceCategoryId": stock.priceCategoryId,
                        "quantity": 1000,
                    },
                ],
            },
        )

        assert response.status_code == 400
        assert response.json == {
            "stocks": ["La date limite de réservation ne peut être postérieure à la date de début de l'évènement"]
        }

    def test_cannot_update_event_stock_with_price_higher_than_300_euros(self, client):
        offer = offers_factories.EventOfferFactory(isActive=False, validation=offers_models.OfferValidationStatus.DRAFT)
        positive_price_category = offers_factories.PriceCategoryFactory(
            offer=offer, priceCategoryLabel__label="positive_price", price=10
        )
        too_high_price_category = offers_factories.PriceCategoryFactory(
            offer=offer, priceCategoryLabel__label="too_high_price_category", price=310
        )
        beginning = datetime.datetime.utcnow() + relativedelta(days=10)
        existing_stock = offers_factories.EventStockFactory(
            offer=offer, priceCategoryId=positive_price_category.id, beginningDatetime=beginning
        )
        offerers_factories.UserOffererFactory(user__email="user@example.com", offerer=offer.venue.managingOfferer)

        response = client.with_session_auth("user@example.com").patch(
            "/stocks/bulk",
            json={
                "offerId": offer.id,
                "stocks": [
                    {
                        "id": existing_stock.id,
                        "beginningDatetime": format_into_utc_date(beginning),
                        "bookingLimitDatetime": format_into_utc_date(beginning),
                        "priceCategoryId": too_high_price_category.id,
                    }
                ],
            },
        )

        assert response.status_code == 400
        assert response.json["priceCategoryId"] == ["Le prix d’une offre ne peut excéder 300 euros."]


@pytest.mark.usefixtures("db_session")
class Returns403Test:
    def when_user_has_no_rights_and_creating_stock_from_offer_id(self, client, db_session):
        users_factories.ProFactory(email="wrong@example.com")
        offer = offers_factories.EventOfferFactory()
        booking_datetime = datetime.datetime.utcnow() + relativedelta(hours=4)

        response = client.with_session_auth("wrong@example.com").patch(
            "/stocks/bulk",
            json={
                "offerId": offer.id,
                "stocks": [
                    {
                        "id": 10,
                        "priceCategoryId": 10,
                        "quantity": 10,
                        "beginningDatetime": format_into_utc_date(booking_datetime),
                    },
                ],
            },
        )

        assert response.status_code == 403
        assert response.json == {
            "global": ["Vous n'avez pas les droits d'accès suffisants pour accéder à cette information."]
        }
