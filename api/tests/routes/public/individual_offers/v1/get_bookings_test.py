import datetime

from dateutil.relativedelta import relativedelta
import pytest

from pcapi.core import testing
from pcapi.core.bookings import factories as bookings_factories
from pcapi.core.offerers import factories as offerers_factories
from pcapi.core.offers import factories as offers_factories

from . import utils


pytestmark = pytest.mark.usefixtures("db_session")


class GetBookingsByOfferReturns200Test:
    def test_request_inexisting_page(self, client):
        venue, _ = utils.create_offerer_provider_linked_to_venue()
        product_offer = offers_factories.ThingOfferFactory(
            venue=venue,
            description="Un livre de contrepèterie",
            name="Vieux motard que jamais",
        )
        past = datetime.datetime.utcnow() - datetime.timedelta(days=2)
        product_stock = offers_factories.StockFactory(offer=product_offer, beginningDatetime=past)
        booking = bookings_factories.BookingFactory(
            dateCreated=past - datetime.timedelta(days=2),
            user__email="beneficiary@example.com",
            user__phoneNumber="0101010101",
            user__dateOfBirth=datetime.datetime.utcnow() - relativedelta(years=18, months=2),
            stock=product_stock,
        )

        client = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY)
        with testing.assert_num_queries(6):
            response = client.get(
                f"/public/bookings/v1/bookings?offer_id={product_offer.id}&firstIndex={booking.id + 1}",
            )
            assert response.status_code == 200
            assert response.json == {"bookings": []}

    def test_key_has_rights_and_regular_product_offer(self, client):
        venue, _ = utils.create_offerer_provider_linked_to_venue()
        product_offer = offers_factories.ThingOfferFactory(
            venue=venue,
            description="Un livre de contrepèterie",
            name="Vieux motard que jamais",
            extraData={"ean": "1234567890123"},
        )
        past = datetime.datetime.utcnow() - datetime.timedelta(days=2)
        product_stock = offers_factories.StockFactory(offer=product_offer, beginningDatetime=past)
        booking = bookings_factories.BookingFactory(
            dateCreated=past - datetime.timedelta(days=2),
            user__email="beneficiary@example.com",
            user__phoneNumber="0101010101",
            user__dateOfBirth=datetime.datetime.utcnow() - relativedelta(years=18, months=2),
            stock=product_stock,
        )

        client = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY)
        with testing.assert_num_queries(8):
            response = client.get(
                f"/public/bookings/v1/bookings?offer_id={product_offer.id}",
            )
            assert response.status_code == 200
            assert response.json == {
                "bookings": [
                    {
                        "confirmationDate": booking.cancellationLimitDate.strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
                        "creationDate": booking.dateCreated.strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
                        "id": booking.id,
                        "offerEan": "1234567890123",
                        "offerId": product_offer.id,
                        "offerName": "Vieux motard que jamais",
                        "price": 1010,
                        "status": "CONFIRMED",
                        "priceCategoryId": None,
                        "priceCategoryLabel": None,
                        "quantity": 1,
                        "stockId": product_stock.id,
                        "userBirthDate": booking.user.dateOfBirth.strftime("%Y-%m-%d"),
                        "userEmail": "beneficiary@example.com",
                        "venueAddress": "1 boulevard Poissonnière",
                        "venueDepartementCode": "75",
                        "venueId": venue.id,
                        "venueName": venue.name,
                        "userFirstName": booking.user.firstName,
                        "userLastName": booking.user.lastName,
                        "userPhoneNumber": booking.user.phoneNumber,
                        "userPostalCode": booking.user.postalCode,
                    }
                ]
            }

    def test_multiple_event_bookings(self, client):
        venue, _ = utils.create_offerer_provider_linked_to_venue()
        event_offer = offers_factories.EventOfferFactory(
            venue=venue,
            description="Un livre de contrepèterie",
            name="Vieux motard que jamais",
        )
        past = datetime.datetime.utcnow() - datetime.timedelta(weeks=2)
        event_stock = offers_factories.EventStockFactory(offer=event_offer, beginningDatetime=past)
        booking = bookings_factories.BookingFactory(
            dateCreated=past - datetime.timedelta(days=2),
            user__email="beneficiary@example.com",
            user__phoneNumber="0101010101",
            user__dateOfBirth=datetime.datetime.utcnow() - relativedelta(months=2),
            stock=event_stock,
        )
        booking_2 = bookings_factories.BookingFactory(
            dateCreated=past - datetime.timedelta(days=1),
            user__email="beneficiary-2@example.com",
            user__phoneNumber="0698271625",
            user__dateOfBirth=datetime.datetime.utcnow() - relativedelta(years=1),
            stock=event_stock,
        )

        client = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY)
        with testing.assert_num_queries(11):
            response = client.get(
                f"/public/bookings/v1/bookings?offer_id={event_offer.id}",
            )

            assert response.status_code == 200
            assert response.json == {
                "bookings": [
                    {
                        "confirmationDate": booking.cancellationLimitDate.strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
                        "creationDate": booking.dateCreated.strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
                        "id": booking.id,
                        "offerEan": None,
                        "offerId": event_offer.id,
                        "offerName": "Vieux motard que jamais",
                        "price": 1010,
                        "status": "CONFIRMED",
                        "priceCategoryId": event_stock.priceCategory.id,
                        "priceCategoryLabel": event_stock.priceCategory.label,
                        "quantity": 1,
                        "stockId": event_stock.id,
                        "userBirthDate": booking.user.dateOfBirth.strftime("%Y-%m-%d"),
                        "userEmail": "beneficiary@example.com",
                        "venueAddress": "1 boulevard Poissonnière",
                        "venueDepartementCode": "75",
                        "venueId": venue.id,
                        "venueName": venue.name,
                        "userFirstName": booking.user.firstName,
                        "userLastName": booking.user.lastName,
                        "userPhoneNumber": booking.user.phoneNumber,
                        "userPostalCode": booking.user.postalCode,
                    },
                    {
                        "confirmationDate": booking_2.cancellationLimitDate.strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
                        "creationDate": booking_2.dateCreated.strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
                        "id": booking_2.id,
                        "offerEan": None,
                        "offerId": event_offer.id,
                        "offerName": "Vieux motard que jamais",
                        "price": 1010,
                        "status": "CONFIRMED",
                        "priceCategoryId": event_stock.priceCategory.id,
                        "priceCategoryLabel": event_stock.priceCategory.label,
                        "quantity": 1,
                        "stockId": event_stock.id,
                        "userBirthDate": booking_2.user.dateOfBirth.strftime("%Y-%m-%d"),
                        "userEmail": "beneficiary-2@example.com",
                        "venueAddress": "1 boulevard Poissonnière",
                        "venueDepartementCode": "75",
                        "venueId": venue.id,
                        "venueName": venue.name,
                        "userFirstName": booking_2.user.firstName,
                        "userLastName": booking_2.user.lastName,
                        "userPhoneNumber": booking_2.user.phoneNumber,
                        "userPostalCode": booking_2.user.postalCode,
                    },
                ]
            }

    def test_filter_price_category_event_bookings(self, client):
        venue, _ = utils.create_offerer_provider_linked_to_venue()
        event_offer = offers_factories.EventOfferFactory(
            venue=venue,
            description="Un livre de contrepèterie",
            name="Vieux motard que jamais",
        )
        past = datetime.datetime.utcnow() - datetime.timedelta(weeks=2)
        price_category = offers_factories.PriceCategoryFactory(price=1010, offer=event_offer)
        event_stock = offers_factories.EventStockFactory(
            offer=event_offer,
            beginningDatetime=past,
        )
        booking = bookings_factories.BookingFactory(
            dateCreated=past - datetime.timedelta(days=2),
            user__email="beneficiary@example.com",
            user__phoneNumber="0101010101",
            user__dateOfBirth=datetime.datetime.utcnow() - relativedelta(months=2),
            stock=event_stock,
        )
        booking_2 = bookings_factories.BookingFactory(
            dateCreated=past - datetime.timedelta(days=1),
            user__email="beneficiary-2@example.com",
            user__phoneNumber="0698271625",
            user__dateOfBirth=datetime.datetime.utcnow() - relativedelta(years=1),
            stock=event_stock,
        )

        client = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY)
        with testing.assert_num_queries(12):
            response = client.get(
                f"/public/bookings/v1/bookings?offer_id={event_offer.id}&price_category_id={price_category.id}",
            )

            assert response.status_code == 200
            assert response.json == {
                "bookings": [
                    {
                        "confirmationDate": booking.cancellationLimitDate.strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
                        "creationDate": booking.dateCreated.strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
                        "id": booking.id,
                        "offerEan": None,
                        "offerId": event_offer.id,
                        "offerName": "Vieux motard que jamais",
                        "price": 1010,
                        "status": "CONFIRMED",
                        "priceCategoryId": event_stock.priceCategory.id,
                        "priceCategoryLabel": event_stock.priceCategory.label,
                        "quantity": 1,
                        "stockId": event_stock.id,
                        "userBirthDate": booking.user.dateOfBirth.strftime("%Y-%m-%d"),
                        "userEmail": "beneficiary@example.com",
                        "venueAddress": "1 boulevard Poissonnière",
                        "venueDepartementCode": "75",
                        "venueId": venue.id,
                        "venueName": venue.name,
                        "userFirstName": booking.user.firstName,
                        "userLastName": booking.user.lastName,
                        "userPhoneNumber": booking.user.phoneNumber,
                        "userPostalCode": booking.user.postalCode,
                    },
                    {
                        "confirmationDate": booking_2.cancellationLimitDate.strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
                        "creationDate": booking_2.dateCreated.strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
                        "id": booking_2.id,
                        "offerEan": None,
                        "offerId": event_offer.id,
                        "offerName": "Vieux motard que jamais",
                        "price": 1010,
                        "status": "CONFIRMED",
                        "priceCategoryId": event_stock.priceCategory.id,
                        "priceCategoryLabel": event_stock.priceCategory.label,
                        "quantity": 1,
                        "stockId": event_stock.id,
                        "userBirthDate": booking_2.user.dateOfBirth.strftime("%Y-%m-%d"),
                        "userEmail": "beneficiary-2@example.com",
                        "venueAddress": "1 boulevard Poissonnière",
                        "venueDepartementCode": "75",
                        "venueId": venue.id,
                        "venueName": venue.name,
                        "userFirstName": booking_2.user.firstName,
                        "userLastName": booking_2.user.lastName,
                        "userPhoneNumber": booking_2.user.phoneNumber,
                        "userPostalCode": booking_2.user.postalCode,
                    },
                ]
            }

    def test_filter_stock_event_bookings(self, client):
        venue, _ = utils.create_offerer_provider_linked_to_venue()
        event_offer = offers_factories.EventOfferFactory(
            venue=venue,
            description="Un livre de contrepèterie",
            name="Vieux motard que jamais",
        )
        past = datetime.datetime.utcnow() - datetime.timedelta(weeks=2)
        event_stock = offers_factories.EventStockFactory(
            offer=event_offer,
            beginningDatetime=past,
        )
        event_stock_2 = offers_factories.EventStockFactory(
            offer=event_offer,
            beginningDatetime=past + datetime.timedelta(days=2),
        )
        booking = bookings_factories.BookingFactory(
            dateCreated=past - datetime.timedelta(days=2),
            user__email="beneficiary@example.com",
            user__phoneNumber="0101010101",
            user__dateOfBirth=datetime.datetime.utcnow() - relativedelta(months=2),
            stock=event_stock,
        )
        bookings_factories.BookingFactory(
            dateCreated=past - datetime.timedelta(days=1),
            user__email="beneficiary-2@example.com",
            user__phoneNumber="0698271625",
            user__dateOfBirth=datetime.datetime.utcnow() - relativedelta(years=1),
            stock=event_stock_2,
        )

        client = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY)
        with testing.assert_num_queries(10):
            response = client.get(
                f"/public/bookings/v1/bookings?offer_id={event_offer.id}&stock_id={event_stock.id}",
            )

            assert response.status_code == 200
            assert response.json == {
                "bookings": [
                    {
                        "confirmationDate": booking.cancellationLimitDate.strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
                        "creationDate": booking.dateCreated.strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
                        "id": booking.id,
                        "offerEan": None,
                        "offerId": event_offer.id,
                        "offerName": "Vieux motard que jamais",
                        "price": 1010,
                        "status": "CONFIRMED",
                        "priceCategoryId": event_stock.priceCategory.id,
                        "priceCategoryLabel": event_stock.priceCategory.label,
                        "quantity": 1,
                        "stockId": event_stock.id,
                        "userBirthDate": booking.user.dateOfBirth.strftime("%Y-%m-%d"),
                        "userEmail": "beneficiary@example.com",
                        "venueAddress": "1 boulevard Poissonnière",
                        "venueDepartementCode": "75",
                        "venueId": venue.id,
                        "venueName": venue.name,
                        "userFirstName": booking.user.firstName,
                        "userLastName": booking.user.lastName,
                        "userPhoneNumber": booking.user.phoneNumber,
                        "userPostalCode": booking.user.postalCode,
                    },
                ]
            }

    def test_filter_stock_begining_datetime_bookings(self, client):
        venue, _ = utils.create_offerer_provider_linked_to_venue()
        event_offer = offers_factories.EventOfferFactory(
            venue=venue,
            description="Un livre de contrepèterie",
            name="Vieux motard que jamais",
        )
        past = datetime.datetime.utcnow() - datetime.timedelta(weeks=2)
        event_stock = offers_factories.EventStockFactory(
            offer=event_offer,
            beginningDatetime=past,
        )
        event_stock_2 = offers_factories.EventStockFactory(
            offer=event_offer,
            beginningDatetime=past + datetime.timedelta(days=2),
        )
        booking = bookings_factories.BookingFactory(
            dateCreated=past - datetime.timedelta(days=2),
            user__email="beneficiary@example.com",
            user__phoneNumber="0101010101",
            user__dateOfBirth=datetime.datetime.utcnow() - relativedelta(months=2),
            stock=event_stock,
        )
        bookings_factories.BookingFactory(
            dateCreated=past - datetime.timedelta(days=1),
            user__email="beneficiary-2@example.com",
            user__phoneNumber="0698271625",
            user__dateOfBirth=datetime.datetime.utcnow() - relativedelta(years=1),
            stock=event_stock_2,
        )

        client = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY)
        with testing.assert_num_queries(10):
            response = client.get(
                f"/public/bookings/v1/bookings?offer_id={event_offer.id}&beginning_datetime={past}",
            )

            assert response.status_code == 200
            assert response.json == {
                "bookings": [
                    {
                        "confirmationDate": booking.cancellationLimitDate.strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
                        "creationDate": booking.dateCreated.strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
                        "id": booking.id,
                        "offerEan": None,
                        "offerId": event_offer.id,
                        "offerName": "Vieux motard que jamais",
                        "price": 1010,
                        "status": "CONFIRMED",
                        "priceCategoryId": event_stock.priceCategory.id,
                        "priceCategoryLabel": event_stock.priceCategory.label,
                        "quantity": 1,
                        "stockId": event_stock.id,
                        "userBirthDate": booking.user.dateOfBirth.strftime("%Y-%m-%d"),
                        "userEmail": "beneficiary@example.com",
                        "venueAddress": "1 boulevard Poissonnière",
                        "venueDepartementCode": "75",
                        "venueId": venue.id,
                        "venueName": venue.name,
                        "userFirstName": booking.user.firstName,
                        "userLastName": booking.user.lastName,
                        "userPhoneNumber": booking.user.phoneNumber,
                        "userPostalCode": booking.user.postalCode,
                    },
                ]
            }

    def test_filter_status_event_bookings(self, client):
        venue, _ = utils.create_offerer_provider_linked_to_venue()
        event_offer = offers_factories.EventOfferFactory(
            venue=venue,
            description="Un livre de contrepèterie",
            name="Vieux motard que jamais",
        )
        past = datetime.datetime.utcnow() - datetime.timedelta(weeks=2)
        event_stock = offers_factories.EventStockFactory(
            offer=event_offer,
            beginningDatetime=past,
        )

        event_stock_2 = offers_factories.EventStockFactory(
            offer=event_offer,
            beginningDatetime=past + datetime.timedelta(days=2),
        )
        booking = bookings_factories.ReimbursedBookingFactory(
            dateCreated=past - datetime.timedelta(days=2),
            user__email="beneficiary@example.com",
            user__phoneNumber="0101010101",
            user__dateOfBirth=datetime.datetime.utcnow() - relativedelta(months=2),
            stock=event_stock,
        )
        bookings_factories.UsedBookingFactory(
            dateCreated=past - datetime.timedelta(days=1),
            user__email="beneficiary-2@example.com",
            user__phoneNumber="0698271625",
            user__dateOfBirth=datetime.datetime.utcnow() - relativedelta(years=1),
            stock=event_stock_2,
        )

        client = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY)
        with testing.assert_num_queries(10):
            response = client.get(
                f"/public/bookings/v1/bookings?offer_id={event_offer.id}&status=REIMBURSED",
            )

            assert response.status_code == 200
            assert response.json == {
                "bookings": [
                    {
                        "confirmationDate": booking.cancellationLimitDate.strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
                        "creationDate": booking.dateCreated.strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
                        "id": booking.id,
                        "offerEan": None,
                        "offerId": event_offer.id,
                        "offerName": "Vieux motard que jamais",
                        "price": 1010,
                        "status": "REIMBURSED",
                        "priceCategoryId": event_stock.priceCategory.id,
                        "priceCategoryLabel": event_stock.priceCategory.label,
                        "quantity": 1,
                        "stockId": event_stock.id,
                        "userBirthDate": booking.user.dateOfBirth.strftime("%Y-%m-%d"),
                        "userEmail": "beneficiary@example.com",
                        "venueAddress": "1 boulevard Poissonnière",
                        "venueDepartementCode": "75",
                        "venueId": venue.id,
                        "venueName": venue.name,
                        "userFirstName": booking.user.firstName,
                        "userLastName": booking.user.lastName,
                        "userPhoneNumber": booking.user.phoneNumber,
                        "userPostalCode": booking.user.postalCode,
                    },
                ]
            }

    def test_multiple_filters_bookings(self, client):
        venue, _ = utils.create_offerer_provider_linked_to_venue()
        event_offer = offers_factories.EventOfferFactory(
            venue=venue,
            description="Un livre de contrepèterie",
            name="Vieux motard que jamais",
        )
        past = datetime.datetime.utcnow() - datetime.timedelta(weeks=2)
        event_stock = offers_factories.EventStockFactory(
            offer=event_offer,
            beginningDatetime=past,
        )
        event_stock_2 = offers_factories.EventStockFactory(
            offer=event_offer,
            beginningDatetime=past + datetime.timedelta(days=2),
        )
        bookings_factories.ReimbursedBookingFactory(
            dateCreated=past - datetime.timedelta(days=2),
            user__email="beneficiary@example.com",
            user__phoneNumber="0101010101",
            user__dateOfBirth=datetime.datetime.utcnow() - relativedelta(months=2),
            stock=event_stock,
        )
        bookings_factories.UsedBookingFactory(
            dateCreated=past - datetime.timedelta(days=1),
            user__email="beneficiary-2@example.com",
            user__phoneNumber="0698271625",
            user__dateOfBirth=datetime.datetime.utcnow() - relativedelta(years=1),
            stock=event_stock,
        )
        booking = bookings_factories.UsedBookingFactory(
            dateCreated=past - datetime.timedelta(days=1),
            user__email="beneficiary-3@example.com",
            user__phoneNumber="0698273632",
            user__dateOfBirth=datetime.datetime.utcnow() - relativedelta(years=2),
            stock=event_stock_2,
        )

        client = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY)
        with testing.assert_num_queries(10):
            response = client.get(
                f"/public/bookings/v1/bookings?offer_id={event_offer.id}&status=USED&beginning_datetime={past + datetime.timedelta(days=2)}",
            )

            assert response.status_code == 200
            assert response.json == {
                "bookings": [
                    {
                        "confirmationDate": booking.cancellationLimitDate.strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
                        "creationDate": booking.dateCreated.strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
                        "id": booking.id,
                        "offerEan": None,
                        "offerId": event_offer.id,
                        "offerName": "Vieux motard que jamais",
                        "price": 1010,
                        "status": "USED",
                        "priceCategoryId": event_stock_2.priceCategory.id,
                        "priceCategoryLabel": event_stock_2.priceCategory.label,
                        "quantity": 1,
                        "stockId": event_stock_2.id,
                        "userBirthDate": booking.user.dateOfBirth.strftime("%Y-%m-%d"),
                        "userEmail": "beneficiary-3@example.com",
                        "venueAddress": "1 boulevard Poissonnière",
                        "venueDepartementCode": "75",
                        "venueId": venue.id,
                        "venueName": venue.name,
                        "userFirstName": booking.user.firstName,
                        "userLastName": booking.user.lastName,
                        "userPhoneNumber": booking.user.phoneNumber,
                        "userPostalCode": booking.user.postalCode,
                    },
                ]
            }

    def test_multiple_pages(self, client):
        venue, _ = utils.create_offerer_provider_linked_to_venue()
        event_offer = offers_factories.EventOfferFactory(
            venue=venue,
            description="Un livre de contrepèterie",
            name="Vieux motard que jamais",
        )
        past = datetime.datetime.utcnow() - datetime.timedelta(weeks=2)
        event_stock = offers_factories.EventStockFactory(offer=event_offer, beginningDatetime=past)
        booking = bookings_factories.BookingFactory(
            dateCreated=past - datetime.timedelta(days=2),
            user__email="beneficiary@example.com",
            user__phoneNumber="0101010101",
            user__dateOfBirth=datetime.datetime.utcnow() - relativedelta(months=2),
            stock=event_stock,
        )
        booking_2 = bookings_factories.BookingFactory(
            dateCreated=past - datetime.timedelta(days=1),
            user__email="beneficiary-2@example.com",
            user__phoneNumber="0698271625",
            user__dateOfBirth=datetime.datetime.utcnow() - relativedelta(years=1),
            stock=event_stock,
        )
        bookings_factories.BookingFactory(
            dateCreated=past - datetime.timedelta(days=1),
            user__email="beneficiary-3@example.com",
            user__phoneNumber="0698890987",
            user__dateOfBirth=datetime.datetime.utcnow() - relativedelta(years=1),
            stock=event_stock,
        )

        client = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY)
        with testing.assert_num_queries(11):
            response = client.get(
                f"/public/bookings/v1/bookings?offer_id={event_offer.id}&limit=2",
            )

            assert response.status_code == 200
            assert response.json == {
                "bookings": [
                    {
                        "confirmationDate": booking.cancellationLimitDate.strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
                        "creationDate": booking.dateCreated.strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
                        "id": booking.id,
                        "offerEan": None,
                        "offerId": event_offer.id,
                        "offerName": "Vieux motard que jamais",
                        "price": 1010,
                        "status": "CONFIRMED",
                        "priceCategoryId": event_stock.priceCategory.id,
                        "priceCategoryLabel": event_stock.priceCategory.label,
                        "quantity": 1,
                        "stockId": event_stock.id,
                        "userBirthDate": booking.user.dateOfBirth.strftime("%Y-%m-%d"),
                        "userEmail": "beneficiary@example.com",
                        "venueAddress": "1 boulevard Poissonnière",
                        "venueDepartementCode": "75",
                        "venueId": venue.id,
                        "venueName": venue.name,
                        "userFirstName": booking.user.firstName,
                        "userLastName": booking.user.lastName,
                        "userPhoneNumber": booking.user.phoneNumber,
                        "userPostalCode": booking.user.postalCode,
                    },
                    {
                        "confirmationDate": booking_2.cancellationLimitDate.strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
                        "creationDate": booking_2.dateCreated.strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
                        "id": booking_2.id,
                        "offerEan": None,
                        "offerId": event_offer.id,
                        "offerName": "Vieux motard que jamais",
                        "price": 1010,
                        "status": "CONFIRMED",
                        "priceCategoryId": event_stock.priceCategory.id,
                        "priceCategoryLabel": event_stock.priceCategory.label,
                        "quantity": 1,
                        "stockId": event_stock.id,
                        "userBirthDate": booking_2.user.dateOfBirth.strftime("%Y-%m-%d"),
                        "userEmail": "beneficiary-2@example.com",
                        "venueAddress": "1 boulevard Poissonnière",
                        "venueDepartementCode": "75",
                        "venueId": venue.id,
                        "venueName": venue.name,
                        "userFirstName": booking_2.user.firstName,
                        "userLastName": booking_2.user.lastName,
                        "userPhoneNumber": booking_2.user.phoneNumber,
                        "userPostalCode": booking_2.user.postalCode,
                    },
                ]
            }

    def test_second_page(self, client):
        venue, _ = utils.create_offerer_provider_linked_to_venue()
        event_offer = offers_factories.EventOfferFactory(
            venue=venue,
            description="Un livre de contrepèterie",
            name="Vieux motard que jamais",
        )
        past = datetime.datetime.utcnow() - datetime.timedelta(weeks=2)
        event_stock = offers_factories.EventStockFactory(offer=event_offer, beginningDatetime=past)
        bookings_factories.BookingFactory(
            dateCreated=past - datetime.timedelta(days=2),
            user__email="beneficiary@example.com",
            user__phoneNumber="0101010101",
            user__dateOfBirth=datetime.datetime.utcnow() - relativedelta(months=2),
            stock=event_stock,
        )
        booking_2 = bookings_factories.BookingFactory(
            dateCreated=past - datetime.timedelta(days=1),
            user__email="beneficiary-2@example.com",
            user__phoneNumber="0698271625",
            user__dateOfBirth=datetime.datetime.utcnow() - relativedelta(years=1),
            stock=event_stock,
        )
        booking_3 = bookings_factories.BookingFactory(
            dateCreated=past - datetime.timedelta(days=1),
            user__email="beneficiary-3@example.com",
            user__phoneNumber="0698890987",
            user__dateOfBirth=datetime.datetime.utcnow() - relativedelta(years=1),
            stock=event_stock,
        )

        client = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY)
        with testing.assert_num_queries(12):
            response = client.get(
                f"/public/bookings/v1/bookings?offer_id={event_offer.id}&limit=2&firstIndex={booking_2.id}",
            )

            assert response.status_code == 200
            assert response.json == {
                "bookings": [
                    {
                        "confirmationDate": booking_2.cancellationLimitDate.strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
                        "creationDate": booking_2.dateCreated.strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
                        "id": booking_2.id,
                        "offerEan": None,
                        "offerId": event_offer.id,
                        "offerName": "Vieux motard que jamais",
                        "price": 1010,
                        "status": "CONFIRMED",
                        "priceCategoryId": event_stock.priceCategory.id,
                        "priceCategoryLabel": event_stock.priceCategory.label,
                        "quantity": 1,
                        "stockId": event_stock.id,
                        "userBirthDate": booking_2.user.dateOfBirth.strftime("%Y-%m-%d"),
                        "userEmail": "beneficiary-2@example.com",
                        "venueAddress": "1 boulevard Poissonnière",
                        "venueDepartementCode": "75",
                        "venueId": venue.id,
                        "venueName": venue.name,
                        "userFirstName": booking_2.user.firstName,
                        "userLastName": booking_2.user.lastName,
                        "userPhoneNumber": booking_2.user.phoneNumber,
                        "userPostalCode": booking_2.user.postalCode,
                    },
                    {
                        "confirmationDate": booking_3.cancellationLimitDate.strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
                        "creationDate": booking_3.dateCreated.strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
                        "id": booking_3.id,
                        "offerEan": None,
                        "offerId": event_offer.id,
                        "offerName": "Vieux motard que jamais",
                        "price": 1010,
                        "status": "CONFIRMED",
                        "priceCategoryId": event_stock.priceCategory.id,
                        "priceCategoryLabel": event_stock.priceCategory.label,
                        "quantity": 1,
                        "stockId": event_stock.id,
                        "userBirthDate": booking_3.user.dateOfBirth.strftime("%Y-%m-%d"),
                        "userEmail": "beneficiary-3@example.com",
                        "venueAddress": "1 boulevard Poissonnière",
                        "venueDepartementCode": "75",
                        "venueId": venue.id,
                        "venueName": venue.name,
                        "userFirstName": booking_3.user.firstName,
                        "userLastName": booking_3.user.lastName,
                        "userPhoneNumber": booking_3.user.phoneNumber,
                        "userPostalCode": booking_3.user.postalCode,
                    },
                ]
            }

    def test_offer_has_no_bookings(self, client):
        venue, _ = utils.create_offerer_provider_linked_to_venue()
        product_offer = offers_factories.ThingOfferFactory(
            venue=venue,
            description="Un livre de contrepèterie",
            name="Vieux motard que jamais",
            extraData={"ean": "1234567890123"},
        )

        client = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY)
        with testing.assert_num_queries(5):
            response = client.get(
                f"/public/bookings/v1/bookings?offer_id={product_offer.id}",
            )
            assert response.status_code == 200
            assert response.json == {"bookings": []}


class GetBookingsByOfferReturns401Test:
    def test_when_user_no_api_key(self, client):
        response = client.get("/public/bookings/v1/bookings?offer_id=1")
        assert response.status_code == 401

    def test_when_user_wrong_api_key(self, client):
        response = client.get(
            "/public/bookings/v1/bookings?offer_id=1", headers={"Authorization": "Bearer WrongApiKey1234567"}
        )
        assert response.status_code == 401


class GetBookingsByOfferReturns400Test:
    def test_no_offer_id_provided(self, client):
        venue, _ = utils.create_offerer_provider_linked_to_venue()
        product_offer = offers_factories.ThingOfferFactory(venue=venue)
        product_stock = offers_factories.StockFactory(offer=product_offer)
        bookings_factories.UsedBookingFactory(stock=product_stock)

        client = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY)
        with testing.assert_num_queries(0):
            response = client.get(
                "/public/bookings/v1/bookings",
            )

            assert response.status_code == 400
            assert response.json == {"offerId": ["field required"]}


class GetBookingsByOfferReturns404Test:
    def test_offer_not_found(self, client):
        venue, _ = utils.create_offerer_provider_linked_to_venue()
        product_offer = offers_factories.ThingOfferFactory(
            venue=venue,
            description="Un livre de contrepèterie",
            name="Vieux motard que jamais",
            extraData={"ean": "1234567890123"},
        )

        client = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY)
        with testing.assert_num_queries(4):
            response = client.get(
                f"/public/bookings/v1/bookings?offer_id={product_offer.id+1}",
            )
            assert response.status_code == 404
            assert response.json == {"offer": "we could not find this offer id"}

    def test_inactive_venue_provider(self, client):
        venue, _ = utils.create_offerer_provider_linked_to_venue(is_venue_provider_active=False)
        product_offer = offers_factories.ThingOfferFactory(venue=venue)
        product_stock = offers_factories.StockFactory(offer=product_offer)
        bookings_factories.BookingFactory(stock=product_stock)

        client = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY)
        with testing.assert_num_queries(4):
            response = client.get(
                f"/public/bookings/v1/bookings?offer_id={product_offer.id}",
            )
            assert response.status_code == 404
