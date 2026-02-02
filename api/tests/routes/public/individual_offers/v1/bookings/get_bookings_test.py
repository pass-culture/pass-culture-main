import datetime

import pytest
from dateutil.relativedelta import relativedelta

from pcapi.core import testing
from pcapi.core.bookings import factories as bookings_factories
from pcapi.core.offers import factories as offers_factories
from pcapi.utils import date as date_utils

from tests.routes.public.helpers import PublicAPIVenueEndpointHelper


pytestmark = pytest.mark.usefixtures("db_session")


class GetBookingsByOfferTest(PublicAPIVenueEndpointHelper):
    endpoint_url = "/public/bookings/v1/bookings"
    endpoint_method = "get"

    def setup_base_resource(self, venue=None):
        venue = venue or self.setup_venue()
        offer = offers_factories.ThingOfferFactory(
            venue=venue,
            description="Un livre de contrepèterie",
            name="Vieux motard que jamais",
        )
        return offer

    def test_should_raise_404_because_has_no_access_to_venue(self):
        plain_api_key, _ = self.setup_provider()
        offer = self.setup_base_resource()

        offer_id = offer.id
        num_queries = 1  # select api_key, offerer and provider
        num_queries += 1  # select offer
        num_queries += 1  # rollback atomic
        num_queries += 1  # rollback atomic
        with testing.assert_num_queries(num_queries):
            response = self.make_request(plain_api_key=plain_api_key, query_params={"offerId": offer_id})
            assert response.status_code == 404

    def test_should_raise_404_because_venue_provider_is_inactive(self):
        plain_api_key, venue_provider = self.setup_inactive_venue_provider()
        offer = self.setup_base_resource(venue=venue_provider.venue)

        offer_id = offer.id
        num_queries = 1  # select api_key, offerer and provider
        num_queries += 1  # select offer
        num_queries += 1  # rollback atomic
        num_queries += 1  # rollback atomic
        with testing.assert_num_queries(num_queries):
            response = self.make_request(plain_api_key=plain_api_key, query_params={"offerId": offer_id})
            assert response.status_code == 404

    def test_should_raise_404_because_offer_not_found(self):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        product_offer = offers_factories.ThingOfferFactory(
            venue=venue_provider.venue,
            description="Un livre de contrepèterie",
            name="Vieux motard que jamais",
            ean="1234567890123",
        )

        product_offer_id = product_offer.id
        num_queries = 1  # select api_key, offerer and provider
        num_queries += 1  # select offer
        num_queries += 1  # rollback atomic
        num_queries += 1  # rollback atomic
        with testing.assert_num_queries(num_queries):
            response = self.make_request(plain_api_key=plain_api_key, query_params={"offerId": product_offer_id + 1})
            assert response.status_code == 404
        assert response.json == {"offerId": "we could not find this offer"}

    def test_should_raise_404_because_venue_not_found(self):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        product_offer = offers_factories.ThingOfferFactory(
            venue=venue_provider.venue,
            description="Un livre de contrepèterie",
            name="Vieux motard que jamais",
            ean="1234567890123",
        )

        response = self.make_request(plain_api_key=plain_api_key, query_params={"venueId": product_offer.venueId + 1})
        assert response.status_code == 404
        assert response.json == {"venueId": "we could not find this venue"}

    def test_request_not_existing_page(self):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        offer = self.setup_base_resource(venue=venue_provider.venue)
        past = date_utils.get_naive_utc_now() - datetime.timedelta(days=2)
        product_stock = offers_factories.StockFactory(offer=offer, beginningDatetime=past)
        booking = bookings_factories.BookingFactory(
            dateCreated=past - datetime.timedelta(days=2),
            user__email="beneficiary@example.com",
            user__phoneNumber="0101010101",
            user__dateOfBirth=date_utils.get_naive_utc_now() - relativedelta(years=18, months=2),
            stock=product_stock,
        )

        offer_id = offer.id
        num_queries = 1  # select api_key, offerer and provider
        num_queries += 1  # select offer
        num_queries += 1  # select bookings
        booking_id = booking.id
        with testing.assert_num_queries(num_queries):
            response = self.make_request(
                plain_api_key, query_params={"offerId": offer_id, "firstIndex": booking_id + 1}
            )
            assert response.status_code == 200

        assert response.json == {"bookings": []}

    def test_key_has_rights_and_regular_product_offer(self):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        product_offer = offers_factories.ThingOfferFactory(
            venue=venue_provider.venue,
            description="Un livre de contrepèterie",
            name="Vieux motard que jamais",
            ean="1234567890123",
        )
        past = date_utils.get_naive_utc_now() - datetime.timedelta(days=2)
        product_stock = offers_factories.StockFactory(offer=product_offer, beginningDatetime=past)
        booking = bookings_factories.BookingFactory(
            dateCreated=past - datetime.timedelta(days=2),
            user__email="beneficiary@example.com",
            user__phoneNumber="0101010101",
            user__dateOfBirth=date_utils.get_naive_utc_now() - relativedelta(years=18, months=2),
            stock=product_stock,
        )

        product_offer_id = product_offer.id
        num_queries = 1  # select api_key, offerer and provider
        num_queries += 1  # select offer
        num_queries += 1  # select bookings
        num_queries += 1  # select user
        with testing.assert_num_queries(num_queries):
            response = self.make_request(plain_api_key, query_params={"offerId": product_offer_id})
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
                    "userBirthDate": booking.user.birth_date.strftime("%Y-%m-%d"),
                    "userEmail": "beneficiary@example.com",
                    "offerAddress": booking.stock.offer.offererAddress.address.street,
                    "offerDepartmentCode": booking.stock.offer.offererAddress.address.departmentCode,
                    "venueId": venue_provider.venue.id,
                    "venueName": venue_provider.venue.name,
                    "userFirstName": booking.user.firstName,
                    "userLastName": booking.user.lastName,
                    "userPhoneNumber": booking.user.phoneNumber,
                    "userPostalCode": booking.user.postalCode,
                }
            ]
        }

    def test_venue_bookings(self):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        event_offer = offers_factories.EventOfferFactory(
            venue=venue_provider.venue,
            description="De la musique de moustachus!",
            name="Vieux motards rockers",
        )
        event_offer_2 = offers_factories.EventOfferFactory(
            venue=venue_provider.venue,
            description="Du gros SONNNNNN!",
            name="On fait la java",
        )
        past = date_utils.get_naive_utc_now() - datetime.timedelta(weeks=2)
        event_stock = offers_factories.EventStockFactory(offer=event_offer, beginningDatetime=past)
        event_stock_2 = offers_factories.EventStockFactory(offer=event_offer_2, beginningDatetime=past)
        booking = bookings_factories.BookingFactory(
            dateCreated=past - datetime.timedelta(days=2),
            user__email="beneficiary@example.com",
            user__phoneNumber="0101010101",
            user__dateOfBirth=date_utils.get_naive_utc_now() - relativedelta(months=2),
            stock=event_stock,
        )
        booking_2 = bookings_factories.BookingFactory(
            dateCreated=past - datetime.timedelta(days=1),
            user__email="beneficiary-2@example.com",
            user__phoneNumber="0698271625",
            user__dateOfBirth=date_utils.get_naive_utc_now() - relativedelta(years=1),
            stock=event_stock,
        )

        booking_3 = bookings_factories.BookingFactory(
            dateCreated=past - datetime.timedelta(hours=1),
            user__email="beneficiary-3@example.com",
            user__phoneNumber="0698271625",
            user__dateOfBirth=date_utils.get_naive_utc_now() - relativedelta(years=1),
            stock=event_stock_2,
        )

        response = self.make_request(plain_api_key, query_params={"venueId": venue_provider.venueId})
        assert response.status_code == 200

        assert response.json == {
            "bookings": [
                {
                    "confirmationDate": booking.cancellationLimitDate.strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
                    "creationDate": booking.dateCreated.strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
                    "id": booking.id,
                    "offerEan": None,
                    "offerId": event_offer.id,
                    "offerName": "Vieux motards rockers",
                    "price": 1010,
                    "status": "CONFIRMED",
                    "priceCategoryId": event_stock.priceCategory.id,
                    "priceCategoryLabel": event_stock.priceCategory.label,
                    "quantity": 1,
                    "stockId": event_stock.id,
                    "userBirthDate": booking.user.birth_date.strftime("%Y-%m-%d"),
                    "userEmail": "beneficiary@example.com",
                    "offerAddress": booking.stock.offer.offererAddress.address.street,
                    "offerDepartmentCode": booking.stock.offer.offererAddress.address.departmentCode,
                    "venueId": venue_provider.venue.id,
                    "venueName": venue_provider.venue.name,
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
                    "offerName": "Vieux motards rockers",
                    "price": 1010,
                    "status": "CONFIRMED",
                    "priceCategoryId": event_stock.priceCategory.id,
                    "priceCategoryLabel": event_stock.priceCategory.label,
                    "quantity": 1,
                    "stockId": event_stock.id,
                    "userBirthDate": booking_2.user.birth_date.strftime("%Y-%m-%d"),
                    "userEmail": "beneficiary-2@example.com",
                    "offerAddress": booking.stock.offer.offererAddress.address.street,
                    "offerDepartmentCode": booking.stock.offer.offererAddress.address.departmentCode,
                    "venueId": venue_provider.venue.id,
                    "venueName": venue_provider.venue.name,
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
                    "offerId": event_offer_2.id,
                    "offerName": "On fait la java",
                    "price": 1010,
                    "status": "CONFIRMED",
                    "priceCategoryId": event_stock_2.priceCategory.id,
                    "priceCategoryLabel": event_stock_2.priceCategory.label,
                    "quantity": 1,
                    "stockId": event_stock_2.id,
                    "userBirthDate": booking_3.user.birth_date.strftime("%Y-%m-%d"),
                    "userEmail": "beneficiary-3@example.com",
                    "offerAddress": booking.stock.offer.offererAddress.address.street,
                    "offerDepartmentCode": booking.stock.offer.offererAddress.address.departmentCode,
                    "venueId": venue_provider.venue.id,
                    "venueName": venue_provider.venue.name,
                    "userFirstName": booking_3.user.firstName,
                    "userLastName": booking_3.user.lastName,
                    "userPhoneNumber": booking_3.user.phoneNumber,
                    "userPostalCode": booking_3.user.postalCode,
                },
            ]
        }

    def test_multiple_event_bookings(self):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        event_offer = offers_factories.EventOfferFactory(
            venue=venue_provider.venue,
            description="Un livre de contrepèterie",
            name="Vieux motard que jamais",
        )
        past = date_utils.get_naive_utc_now() - datetime.timedelta(weeks=2)
        event_stock = offers_factories.EventStockFactory(offer=event_offer, beginningDatetime=past)
        booking = bookings_factories.BookingFactory(
            dateCreated=past - datetime.timedelta(days=2),
            user__email="beneficiary@example.com",
            user__phoneNumber="0101010101",
            user__dateOfBirth=date_utils.get_naive_utc_now() - relativedelta(months=2),
            stock=event_stock,
        )
        booking_2 = bookings_factories.BookingFactory(
            dateCreated=past - datetime.timedelta(days=1),
            user__email="beneficiary-2@example.com",
            user__phoneNumber="0698271625",
            user__dateOfBirth=date_utils.get_naive_utc_now() - relativedelta(years=1),
            stock=event_stock,
        )

        event_offer_id = event_offer.id
        num_queries = 1  # select api_key, offerer and provider
        num_queries += 1  # select offer
        num_queries += 1  # select bookings
        num_queries += 1  # select user
        num_queries += 1  # select price_category
        num_queries += 1  # select price_category_label
        num_queries += 1  # select second user
        with testing.assert_num_queries(num_queries):
            response = self.make_request(plain_api_key, query_params={"offerId": event_offer_id})
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
                    "userBirthDate": booking.user.birth_date.strftime("%Y-%m-%d"),
                    "userEmail": "beneficiary@example.com",
                    "offerAddress": booking.stock.offer.offererAddress.address.street,
                    "offerDepartmentCode": booking.stock.offer.offererAddress.address.departmentCode,
                    "venueId": venue_provider.venue.id,
                    "venueName": venue_provider.venue.name,
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
                    "userBirthDate": booking_2.user.birth_date.strftime("%Y-%m-%d"),
                    "userEmail": "beneficiary-2@example.com",
                    "offerAddress": booking.stock.offer.offererAddress.address.street,
                    "offerDepartmentCode": booking.stock.offer.offererAddress.address.departmentCode,
                    "venueId": venue_provider.venue.id,
                    "venueName": venue_provider.venue.name,
                    "userFirstName": booking_2.user.firstName,
                    "userLastName": booking_2.user.lastName,
                    "userPhoneNumber": booking_2.user.phoneNumber,
                    "userPostalCode": booking_2.user.postalCode,
                },
            ]
        }

    def test_filter_price_category_event_bookings(self):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        event_offer = offers_factories.EventOfferFactory(
            venue=venue_provider.venue,
            description="Un livre de contrepèterie",
            name="Vieux motard que jamais",
        )
        past = date_utils.get_naive_utc_now() - datetime.timedelta(weeks=2)
        price_category = offers_factories.PriceCategoryFactory(price=1010, offer=event_offer)
        event_stock = offers_factories.EventStockFactory(
            offer=event_offer,
            beginningDatetime=past,
        )
        booking = bookings_factories.BookingFactory(
            dateCreated=past - datetime.timedelta(days=2),
            user__email="beneficiary@example.com",
            user__phoneNumber="0101010101",
            user__dateOfBirth=date_utils.get_naive_utc_now() - relativedelta(months=2),
            stock=event_stock,
        )
        booking_2 = bookings_factories.BookingFactory(
            dateCreated=past - datetime.timedelta(days=1),
            user__email="beneficiary-2@example.com",
            user__phoneNumber="0698271625",
            user__dateOfBirth=date_utils.get_naive_utc_now() - relativedelta(years=1),
            stock=event_stock,
        )

        event_offer_id = event_offer.id
        price_category_id = price_category.id
        num_queries = 1  # select api_key, offerer and provider
        num_queries += 1  # select offer
        num_queries += 1  # select bookings
        num_queries += 1  # select user
        num_queries += 1  # select price_category
        num_queries += 1  # select price_category_label
        num_queries += 1  # select second user
        with testing.assert_num_queries(num_queries):
            response = self.make_request(
                plain_api_key, query_params={"offerId": event_offer_id, "priceCategoryId": price_category_id}
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
                    "userBirthDate": booking.user.birth_date.strftime("%Y-%m-%d"),
                    "userEmail": "beneficiary@example.com",
                    "offerAddress": booking.stock.offer.offererAddress.address.street,
                    "offerDepartmentCode": booking.stock.offer.offererAddress.address.departmentCode,
                    "venueId": venue_provider.venue.id,
                    "venueName": venue_provider.venue.name,
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
                    "userBirthDate": booking_2.user.birth_date.strftime("%Y-%m-%d"),
                    "userEmail": "beneficiary-2@example.com",
                    "offerAddress": booking_2.stock.offer.offererAddress.address.street,
                    "offerDepartmentCode": booking_2.stock.offer.offererAddress.address.departmentCode,
                    "venueId": venue_provider.venue.id,
                    "venueName": venue_provider.venue.name,
                    "userFirstName": booking_2.user.firstName,
                    "userLastName": booking_2.user.lastName,
                    "userPhoneNumber": booking_2.user.phoneNumber,
                    "userPostalCode": booking_2.user.postalCode,
                },
            ]
        }

    def test_filter_stock_event_bookings(self):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        event_offer = offers_factories.EventOfferFactory(
            venue=venue_provider.venue,
            description="Un livre de contrepèterie",
            name="Vieux motard que jamais",
        )
        past = date_utils.get_naive_utc_now() - datetime.timedelta(weeks=2)
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
            user__dateOfBirth=date_utils.get_naive_utc_now() - relativedelta(months=2),
            stock=event_stock,
        )
        bookings_factories.BookingFactory(
            dateCreated=past - datetime.timedelta(days=1),
            user__email="beneficiary-2@example.com",
            user__phoneNumber="0698271625",
            user__dateOfBirth=date_utils.get_naive_utc_now() - relativedelta(years=1),
            stock=event_stock_2,
        )

        event_offer_id = event_offer.id
        event_stock_id = event_stock.id
        num_queries = 1  # select api_key, offerer and provider
        num_queries += 1  # select offer
        num_queries += 1  # select bookings
        num_queries += 1  # select user
        num_queries += 1  # select price_category
        num_queries += 1  # select price_category_label
        with testing.assert_num_queries(num_queries):
            response = self.make_request(
                plain_api_key, query_params={"offerId": event_offer_id, "stockId": event_stock_id}
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
                    "userBirthDate": booking.user.birth_date.strftime("%Y-%m-%d"),
                    "userEmail": "beneficiary@example.com",
                    "offerAddress": booking.stock.offer.offererAddress.address.street,
                    "offerDepartmentCode": booking.stock.offer.offererAddress.address.departmentCode,
                    "venueId": venue_provider.venue.id,
                    "venueName": venue_provider.venue.name,
                    "userFirstName": booking.user.firstName,
                    "userLastName": booking.user.lastName,
                    "userPhoneNumber": booking.user.phoneNumber,
                    "userPostalCode": booking.user.postalCode,
                },
            ]
        }

    def test_filter_stock_begining_datetime_bookings(self):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        event_offer = offers_factories.EventOfferFactory(
            venue=venue_provider.venue,
            description="Un livre de contrepèterie",
            name="Vieux motard que jamais",
        )
        past = date_utils.get_naive_utc_now() - datetime.timedelta(weeks=2)
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
            user__dateOfBirth=date_utils.get_naive_utc_now() - relativedelta(months=2),
            stock=event_stock,
        )
        bookings_factories.BookingFactory(
            dateCreated=past - datetime.timedelta(days=1),
            user__email="beneficiary-2@example.com",
            user__phoneNumber="0698271625",
            user__dateOfBirth=date_utils.get_naive_utc_now() - relativedelta(years=1),
            stock=event_stock_2,
        )

        event_offer_id = event_offer.id
        num_queries = 1  # select api_key, offerer and provider
        num_queries += 1  # select offer
        num_queries += 1  # select bookings
        num_queries += 1  # select user
        num_queries += 1  # select price_category
        num_queries += 1  # select price_category_label
        with testing.assert_num_queries(num_queries):
            response = self.make_request(
                plain_api_key, query_params={"offerId": event_offer_id, "beginningDatetime": past}
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
                    "userBirthDate": booking.user.birth_date.strftime("%Y-%m-%d"),
                    "userEmail": "beneficiary@example.com",
                    "offerAddress": booking.stock.offer.offererAddress.address.street,
                    "offerDepartmentCode": booking.stock.offer.offererAddress.address.departmentCode,
                    "venueId": venue_provider.venue.id,
                    "venueName": venue_provider.venue.name,
                    "userFirstName": booking.user.firstName,
                    "userLastName": booking.user.lastName,
                    "userPhoneNumber": booking.user.phoneNumber,
                    "userPostalCode": booking.user.postalCode,
                },
            ]
        }

    def test_filter_status_event_bookings(self):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        event_offer = offers_factories.EventOfferFactory(
            venue=venue_provider.venue,
            description="Un livre de contrepèterie",
            name="Vieux motard que jamais",
        )
        past = date_utils.get_naive_utc_now() - datetime.timedelta(weeks=2)
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
            user__dateOfBirth=date_utils.get_naive_utc_now() - relativedelta(months=2),
            stock=event_stock,
        )
        bookings_factories.UsedBookingFactory(
            dateCreated=past - datetime.timedelta(days=1),
            user__email="beneficiary-2@example.com",
            user__phoneNumber="0698271625",
            user__dateOfBirth=date_utils.get_naive_utc_now() - relativedelta(years=1),
            stock=event_stock_2,
        )

        num_queries = 1  # select api_key, offerer and provider
        num_queries += 1  # select offer
        num_queries += 1  # select bookings
        num_queries += 1  # select user
        num_queries += 1  # select price_category
        num_queries += 1  # select price_category_label
        event_offer_id = event_offer.id
        with testing.assert_num_queries(num_queries):
            response = self.make_request(
                plain_api_key, query_params={"offerId": event_offer_id, "status": "REIMBURSED"}
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
                    "userBirthDate": booking.user.birth_date.strftime("%Y-%m-%d"),
                    "userEmail": "beneficiary@example.com",
                    "offerAddress": booking.stock.offer.offererAddress.address.street,
                    "offerDepartmentCode": booking.stock.offer.offererAddress.address.departmentCode,
                    "venueId": venue_provider.venue.id,
                    "venueName": venue_provider.venue.name,
                    "userFirstName": booking.user.firstName,
                    "userLastName": booking.user.lastName,
                    "userPhoneNumber": booking.user.phoneNumber,
                    "userPostalCode": booking.user.postalCode,
                },
            ]
        }

    def test_multiple_filters_bookings(self):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        event_offer = offers_factories.EventOfferFactory(
            venue=venue_provider.venue,
            description="Un livre de contrepèterie",
            name="Vieux motard que jamais",
        )
        past = date_utils.get_naive_utc_now() - datetime.timedelta(weeks=2)
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
            user__dateOfBirth=date_utils.get_naive_utc_now() - relativedelta(months=2),
            stock=event_stock,
        )
        bookings_factories.UsedBookingFactory(
            dateCreated=past - datetime.timedelta(days=1),
            user__email="beneficiary-2@example.com",
            user__phoneNumber="0698271625",
            user__dateOfBirth=date_utils.get_naive_utc_now() - relativedelta(years=1),
            stock=event_stock,
        )
        booking = bookings_factories.UsedBookingFactory(
            dateCreated=past - datetime.timedelta(days=1),
            user__email="beneficiary-3@example.com",
            user__phoneNumber="0698273632",
            user__dateOfBirth=date_utils.get_naive_utc_now() - relativedelta(years=2),
            stock=event_stock_2,
        )

        num_queries = 1  # select api_key, offerer and provider
        num_queries += 1  # select offer
        num_queries += 1  # select bookings
        num_queries += 1  # select user
        num_queries += 1  # select price_category
        num_queries += 1  # select price_category_label
        event_offer_id = event_offer.id
        with testing.assert_num_queries(num_queries):
            response = self.make_request(
                plain_api_key,
                query_params={
                    "offerId": event_offer_id,
                    "status": "USED",
                    "beginningDatetime": past + datetime.timedelta(days=2),
                },
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
                    "userBirthDate": booking.user.birth_date.strftime("%Y-%m-%d"),
                    "userEmail": "beneficiary-3@example.com",
                    "offerAddress": booking.stock.offer.offererAddress.address.street,
                    "offerDepartmentCode": booking.stock.offer.offererAddress.address.departmentCode,
                    "venueId": venue_provider.venue.id,
                    "venueName": venue_provider.venue.name,
                    "userFirstName": booking.user.firstName,
                    "userLastName": booking.user.lastName,
                    "userPhoneNumber": booking.user.phoneNumber,
                    "userPostalCode": booking.user.postalCode,
                },
            ]
        }

    def test_multiple_pages(self):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        event_offer = offers_factories.EventOfferFactory(
            venue=venue_provider.venue,
            description="Un livre de contrepèterie",
            name="Vieux motard que jamais",
        )
        past = date_utils.get_naive_utc_now() - datetime.timedelta(weeks=2)
        event_stock = offers_factories.EventStockFactory(offer=event_offer, beginningDatetime=past)
        booking = bookings_factories.BookingFactory(
            dateCreated=past - datetime.timedelta(days=2),
            user__email="beneficiary@example.com",
            user__phoneNumber="0101010101",
            user__dateOfBirth=date_utils.get_naive_utc_now() - relativedelta(months=2),
            stock=event_stock,
        )
        booking_2 = bookings_factories.BookingFactory(
            dateCreated=past - datetime.timedelta(days=1),
            user__email="beneficiary-2@example.com",
            user__phoneNumber="0698271625",
            user__dateOfBirth=date_utils.get_naive_utc_now() - relativedelta(years=1),
            stock=event_stock,
        )
        bookings_factories.BookingFactory(
            dateCreated=past - datetime.timedelta(days=1),
            user__email="beneficiary-3@example.com",
            user__phoneNumber="0698890987",
            user__dateOfBirth=date_utils.get_naive_utc_now() - relativedelta(years=1),
            stock=event_stock,
        )

        num_queries = 1  # select api_key, offerer and provider
        num_queries += 1  # select offer
        num_queries += 1  # select bookings
        num_queries += 1  # select user
        num_queries += 1  # select price_category
        num_queries += 1  # select price_category_label
        num_queries += 1  # select second user
        event_offer_id = event_offer.id
        with testing.assert_num_queries(num_queries):
            response = self.make_request(plain_api_key, query_params={"offerId": event_offer_id, "limit": 2})
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
                    "userBirthDate": booking.user.birth_date.strftime("%Y-%m-%d"),
                    "userEmail": "beneficiary@example.com",
                    "offerAddress": booking.stock.offer.offererAddress.address.street,
                    "offerDepartmentCode": booking.stock.offer.offererAddress.address.departmentCode,
                    "venueId": venue_provider.venue.id,
                    "venueName": venue_provider.venue.name,
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
                    "userBirthDate": booking_2.user.birth_date.strftime("%Y-%m-%d"),
                    "userEmail": "beneficiary-2@example.com",
                    "offerAddress": booking.stock.offer.offererAddress.address.street,
                    "offerDepartmentCode": booking.stock.offer.offererAddress.address.departmentCode,
                    "venueId": venue_provider.venue.id,
                    "venueName": venue_provider.venue.name,
                    "userFirstName": booking_2.user.firstName,
                    "userLastName": booking_2.user.lastName,
                    "userPhoneNumber": booking_2.user.phoneNumber,
                    "userPostalCode": booking_2.user.postalCode,
                },
            ]
        }

    def test_second_page(self):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        event_offer = offers_factories.EventOfferFactory(
            venue=venue_provider.venue,
            description="Un livre de contrepèterie",
            name="Vieux motard que jamais",
        )
        past = date_utils.get_naive_utc_now() - datetime.timedelta(weeks=2)
        event_stock = offers_factories.EventStockFactory(offer=event_offer, beginningDatetime=past)
        bookings_factories.BookingFactory(
            dateCreated=past - datetime.timedelta(days=2),
            user__email="beneficiary@example.com",
            user__phoneNumber="0101010101",
            user__dateOfBirth=date_utils.get_naive_utc_now() - relativedelta(months=2),
            stock=event_stock,
        )
        booking_2 = bookings_factories.BookingFactory(
            dateCreated=past - datetime.timedelta(days=1),
            user__email="beneficiary-2@example.com",
            user__phoneNumber="0698271625",
            user__dateOfBirth=date_utils.get_naive_utc_now() - relativedelta(years=1),
            stock=event_stock,
        )
        booking_3 = bookings_factories.BookingFactory(
            dateCreated=past - datetime.timedelta(days=1),
            user__email="beneficiary-3@example.com",
            user__phoneNumber="0698890987",
            user__dateOfBirth=date_utils.get_naive_utc_now() - relativedelta(years=1),
            stock=event_stock,
        )

        num_queries = 1  # select api_key, offerer and provider
        num_queries += 1  # select offer
        num_queries += 1  # select bookings
        num_queries += 1  # select user
        num_queries += 1  # select price_category
        num_queries += 1  # select price_category_label
        num_queries += 1  # select second user
        event_offer_id = event_offer.id
        booking_2_id = booking_2.id
        with testing.assert_num_queries(num_queries):
            response = self.make_request(
                plain_api_key, query_params={"offerId": event_offer_id, "limit": 2, "firstIndex": booking_2_id}
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
                    "userBirthDate": booking_2.user.birth_date.strftime("%Y-%m-%d"),
                    "userEmail": "beneficiary-2@example.com",
                    "offerAddress": booking_2.stock.offer.offererAddress.address.street,
                    "offerDepartmentCode": booking_2.stock.offer.offererAddress.address.departmentCode,
                    "venueId": venue_provider.venue.id,
                    "venueName": venue_provider.venue.name,
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
                    "userBirthDate": booking_3.user.birth_date.strftime("%Y-%m-%d"),
                    "userEmail": "beneficiary-3@example.com",
                    "offerAddress": booking_3.stock.offer.offererAddress.address.street,
                    "offerDepartmentCode": booking_3.stock.offer.offererAddress.address.departmentCode,
                    "venueId": venue_provider.venue.id,
                    "venueName": venue_provider.venue.name,
                    "userFirstName": booking_3.user.firstName,
                    "userLastName": booking_3.user.lastName,
                    "userPhoneNumber": booking_3.user.phoneNumber,
                    "userPostalCode": booking_3.user.postalCode,
                },
            ]
        }

    def test_offer_has_no_bookings(self):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        product_offer = offers_factories.ThingOfferFactory(
            venue=venue_provider.venue,
            description="Un livre de contrepèterie",
            name="Vieux motard que jamais",
            ean="1234567890123",
        )

        num_queries = 1  # select api_key, offerer and provider
        num_queries += 1  # select offer
        num_queries += 1  # select bookings
        product_offer_id = product_offer.id
        with testing.assert_num_queries(num_queries):
            response = self.make_request(plain_api_key, query_params={"offerId": product_offer_id})

            assert response.status_code == 200

        assert response.json == {"bookings": []}

    def test_should_raise_400_because_no_offer_id_nor_venue_id_provided(self):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        product_offer = offers_factories.ThingOfferFactory(venue=venue_provider.venue)
        product_stock = offers_factories.StockFactory(offer=product_offer)
        bookings_factories.UsedBookingFactory(stock=product_stock)

        num_queries = 1  # select api_key, offerer and provider
        num_queries += 1  # rollback atomic
        num_queries += 1  # rollback atomic
        with testing.assert_num_queries(num_queries):
            response = self.make_request(plain_api_key)

        assert response.json == {"global": ["`offerId` or `venueId` must be set"]}
