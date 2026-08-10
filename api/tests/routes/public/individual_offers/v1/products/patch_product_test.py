import datetime
import decimal
from unittest import mock

import pytest
import time_machine

from pcapi import settings
from pcapi.core.bookings import factories as bookings_factories
from pcapi.core.bookings import models as bookings_models
from pcapi.core.categories import subcategories
from pcapi.core.geography import factories as geography_factories
from pcapi.core.offerers import models as offerers_models
from pcapi.core.offers import factories as offers_factories
from pcapi.core.offers import models as offers_models
from pcapi.core.providers import factories as providers_factories
from pcapi.models import db
from pcapi.routes.public.individual_offers.v1 import serialization as v1_serialization
from pcapi.utils import human_ids

from tests.routes import image_data
from tests.routes.public.helpers import PublicAPIVenueEndpointHelper


FROZEN_NOW = datetime.datetime(2026, 6, 25, 12, 30, tzinfo=datetime.timezone.utc)


def has_log(caplog: pytest.LogCaptureFixture, technical_message_id: str) -> bool:
    return any(getattr(record, "technical_message_id", None) == technical_message_id for record in caplog.records)


class PatchProductEndpointHelper(PublicAPIVenueEndpointHelper):
    endpoint_url = "/public/offers/v1/products"
    endpoint_method = "patch"

    DEFAULT_PRODUCT_DATA = {
        # ABO_CONCERT is in `ALLOWED_PRODUCT_SUBCATEGORIES` and offline
        "subcategoryId": subcategories.ABO_CONCERT.id,
        "name": "Abonnement saison jazz",
        "description": "Six concerts de jazz sur la saison, au tarif abonné.",
        "bookingEmail": "notify@salle-de-concert.example.com",
        "bookingContact": "contact@salle-de-concert.example.com",
        "withdrawalDetails": "À retirer au guichet",
        "externalTicketOfficeUrl": "https://salle-de-concert.example.com/reservations",
        # `musicType`is one of the product conditional field this endpoint can actually write
        "extraData": {"musicType": "501", "musicSubType": "-1", "gtl_id": "02000000"},
        "audioDisabilityCompliant": True,
        "mentalDisabilityCompliant": False,
        "motorDisabilityCompliant": True,
        "visualDisabilityCompliant": False,
        # in the past relative to `FROZEN_NOW`, so the base product is published
        "publicationDatetime": datetime.datetime(2026, 1, 15, 10, 0),
        # in the past relative to `FROZEN_NOW`, so the base product is bookable
        "bookingAllowedDatetime": datetime.datetime(2026, 2, 1, 10, 0),
    }

    def setup_base_resource(self, venue=None, provider=None, **kwargs) -> offers_models.Offer:
        return offers_factories.ThingOfferFactory(
            venue=venue or self.setup_venue(),
            lastProvider=provider,
            # `kwargs` always wins over `DEFAULT_PRODUCT_DATA`, including when it passes `None`
            **{**self.DEFAULT_PRODUCT_DATA, **kwargs},
        )

    test_should_raise_404_because_has_no_access_to_venue = None
    test_should_raise_404_because_venue_provider_is_inactive = None
    test_should_raise_401_because_not_authenticated = None


@pytest.mark.usefixtures("db_session")
class Returns200Test(PatchProductEndpointHelper):
    """A product offer without a stock is an ordinary state: `stock` is `null` in most answers."""

    # --- Plain fields

    @pytest.mark.parametrize(
        "request_field,column,new_value",
        [
            ("name", "name", "Abonnement saison classique"),
            ("description", "description", "Six concerts de musique de chambre sur la saison."),
            ("bookingEmail", "bookingEmail", "nouvelle-adresse@salle-de-concert.example.com"),
            ("bookingContact", "bookingContact", "nouveau-contact@salle-de-concert.example.com"),
            ("itemCollectionDetails", "withdrawalDetails", "À retirer au vestiaire"),
            (
                "externalTicketOfficeUrl",
                "externalTicketOfficeUrl",
                "https://salle-de-concert.example.com/billetterie",
            ),
            ("idAtProvider", "idAtProvider", "abonnement-jazz-2026"),
        ],
    )
    def test_should_update_a_single_field(self, request_field, column, new_value):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        product = self.setup_base_resource(venue=venue_provider.venue, provider=venue_provider.provider)
        assert getattr(product, column) != new_value

        response = self.make_request(plain_api_key, json_body={"offerId": product.id, request_field: new_value})

        assert response.status_code == 200, response.json
        assert response.json[request_field] == new_value

        db.session.refresh(product)
        assert getattr(product, column) == new_value

    @pytest.mark.parametrize(
        "request_field,column",
        [
            ("description", "description"),
            ("bookingEmail", "bookingEmail"),
            ("bookingContact", "bookingContact"),
            ("itemCollectionDetails", "withdrawalDetails"),
            ("externalTicketOfficeUrl", "externalTicketOfficeUrl"),
            # the factory fills `idAtProvider` with a uuid as soon as the offer has a `lastProvider`
            ("idAtProvider", "idAtProvider"),
            ("publicationDatetime", "publicationDatetime"),
            ("bookingAllowedDatetime", "bookingAllowedDatetime"),
        ],
    )
    def test_should_clear_a_field_sent_as_null(self, request_field, column):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        product = self.setup_base_resource(venue=venue_provider.venue, provider=venue_provider.provider)
        assert getattr(product, column) is not None

        response = self.make_request(plain_api_key, json_body={"offerId": product.id, request_field: None})

        assert response.status_code == 200, response.json
        assert response.json[request_field] is None

        db.session.refresh(product)
        assert getattr(product, column) is None


    @time_machine.travel(FROZEN_NOW, tick=False)
    def test_should_update_many_fields_at_once(self):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        product = self.setup_base_resource(venue=venue_provider.venue, provider=venue_provider.provider)

        response = self.make_request(
            plain_api_key,
            json_body={
                "offerId": product.id,
                "name": "Abonnement saison classique",
                "description": "Six concerts de musique de chambre sur la saison.",
                "bookingEmail": "nouvelle-adresse@salle-de-concert.example.com",
                "bookingContact": "nouveau-contact@salle-de-concert.example.com",
                "itemCollectionDetails": "À retirer au vestiaire",
                "externalTicketOfficeUrl": "https://salle-de-concert.example.com/billetterie",
                "idAtProvider": "abonnement-classique-2026",
                "accessibility": {
                    "audioDisabilityCompliant": False,
                    "mentalDisabilityCompliant": True,
                    "motorDisabilityCompliant": False,
                    "visualDisabilityCompliant": True,
                },
                "categoryRelatedFields": {"category": "ABO_CONCERT", "musicType": "MUSIQUE_CLASSIQUE"},
                # sent in Europe/Paris
                "publicationDatetime": "2026-08-01T08:00:00+02:00",
                "bookingAllowedDatetime": "2026-07-15T10:00:00+02:00",
            },
        )

        assert response.status_code == 200, response.json

        db.session.refresh(product)
        expected = {
            "name": "Abonnement saison classique",
            "description": "Six concerts de musique de chambre sur la saison.",
            "bookingEmail": "nouvelle-adresse@salle-de-concert.example.com",
            "bookingContact": "nouveau-contact@salle-de-concert.example.com",
            "withdrawalDetails": "À retirer au vestiaire",
            "externalTicketOfficeUrl": "https://salle-de-concert.example.com/billetterie",
            "idAtProvider": "abonnement-classique-2026",
            "audioDisabilityCompliant": False,
            "mentalDisabilityCompliant": True,
            "motorDisabilityCompliant": False,
            "visualDisabilityCompliant": True,
        }
        assert {column: getattr(product, column) for column in expected} == expected
        assert product.extraData["gtl_id"] == "01000000"
        # stored in UTC
        assert product.publicationDatetime == datetime.datetime(2026, 8, 1, 6, 0, tzinfo=datetime.UTC)
        assert product.bookingAllowedDatetime == datetime.datetime(2026, 7, 15, 8, 0, tzinfo=datetime.UTC)

    # --- `accessibility`


    def test_should_update_accessibility_partially_and_leave_the_other_ones_unchanged(self):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        product = self.setup_base_resource(venue=venue_provider.venue, provider=venue_provider.provider)
        assert product.audioDisabilityCompliant is True

        response = self.make_request(
            plain_api_key,
            json_body={"offerId": product.id, "accessibility": {"audioDisabilityCompliant": False}},
        )

        assert response.status_code == 200, response.json
        assert response.json["accessibility"] == {
            "audioDisabilityCompliant": False,
            "mentalDisabilityCompliant": self.DEFAULT_PRODUCT_DATA["mentalDisabilityCompliant"],
            "motorDisabilityCompliant": self.DEFAULT_PRODUCT_DATA["motorDisabilityCompliant"],
            "visualDisabilityCompliant": self.DEFAULT_PRODUCT_DATA["visualDisabilityCompliant"],
        }

        db.session.refresh(product)
        assert product.audioDisabilityCompliant is False

    # --- `publicationDatetime`

    @time_machine.travel(FROZEN_NOW, tick=False)
    @pytest.mark.parametrize(
        "partial_body,expected_stored,expected_returned",
        [
            # sent in Europe/Paris, read back in UTC
            (
                {"publicationDatetime": "2026-08-01T08:00:00+02:00"},
                datetime.datetime(2026, 8, 1, 6, 0, tzinfo=datetime.UTC),
                "2026-08-01T06:00:00Z",
            ),
            # the `now` literal resolves to the current instant
            (
                {"publicationDatetime": "now"},
                datetime.datetime(2026, 6, 25, 12, 30, tzinfo=datetime.UTC),
                "2026-06-25T12:30:00Z",
            ),
        ],
        ids=["explicit datetime", "now literal"],
    )
    def test_should_publish_the_product_at_the_requested_datetime(
        self, partial_body, expected_stored, expected_returned
    ):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        product = self.setup_base_resource(venue=venue_provider.venue, provider=venue_provider.provider)

        response = self.make_request(plain_api_key, json_body={"offerId": product.id, **partial_body})

        assert response.status_code == 200, response.json
        assert response.json["publicationDatetime"] == expected_returned

        db.session.refresh(product)
        assert product.publicationDatetime == expected_stored

    # --- `isActive` (deprecated)


    def test_should_deactivate_with_deprecated_is_active_false(self):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        product = self.setup_base_resource(venue=venue_provider.venue, provider=venue_provider.provider)
        assert product.publicationDatetime is not None

        response = self.make_request(plain_api_key, json_body={"offerId": product.id, "isActive": False})

        assert response.status_code == 200, response.json
        assert response.json["publicationDatetime"] is None
        assert response.json["status"] == "INACTIVE"

        db.session.refresh(product)
        assert product.publicationDatetime is None


    # --- `bookingAllowedDatetime`

    @time_machine.travel(FROZEN_NOW, tick=False)
    @mock.patch("pcapi.core.reminders.external.reminders_notifications.notify_users_offer_is_bookable")
    def test_should_delay_bookings_until_the_booking_allowed_datetime(self, notify_mock):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        product = self.setup_base_resource(venue=venue_provider.venue, provider=venue_provider.provider)

        response = self.make_request(
            # sent in Europe/Paris, read back in UTC
            plain_api_key,
            json_body={"offerId": product.id, "bookingAllowedDatetime": "2026-07-15T10:00:00+02:00"},
        )

        assert response.status_code == 200, response.json
        assert response.json["bookingAllowedDatetime"] == "2026-07-15T08:00:00Z"
        # bookings are not open yet: users are notified when the datetime is reached
        notify_mock.assert_not_called()

        db.session.refresh(product)
        assert product.bookingAllowedDatetime == datetime.datetime(2026, 7, 15, 8, 0, tzinfo=datetime.UTC)

    @time_machine.travel(FROZEN_NOW, tick=False)
    @mock.patch("pcapi.core.reminders.external.reminders_notifications.notify_users_offer_is_bookable")
    def test_should_notify_users_when_bookings_are_opened_immediately(self, notify_mock):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        product = self.setup_base_resource(venue=venue_provider.venue, provider=venue_provider.provider)

        response = self.make_request(plain_api_key, json_body={"offerId": product.id, "bookingAllowedDatetime": None})

        assert response.status_code == 200, response.json
        assert response.json["bookingAllowedDatetime"] is None
        assert notify_mock.call_count == 1

        db.session.refresh(product)
        assert product.bookingAllowedDatetime is None

    # --- `location`

    def test_should_move_the_product_to_another_venue_with_a_physical_location(self):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        product = self.setup_base_resource(venue=venue_provider.venue, provider=venue_provider.provider)

        # a venue of another offerer: the only requirement is that it is linked to the calling provider
        other_venue = providers_factories.VenueProviderFactory(provider=venue_provider.provider).venue
        assert other_venue.managingOffererId != venue_provider.venue.managingOffererId
        offerer_address_id = product.offererAddressId

        response = self.make_request(
            plain_api_key,
            json_body={"offerId": product.id, "location": {"type": "physical", "venueId": other_venue.id}},
        )

        assert response.status_code == 200, response.json
        # the flush means the answer already names the new venue
        assert response.json["location"] == {"type": "physical", "venueId": other_venue.id}

        db.session.refresh(product)
        assert product.offererAddress.addressId == other_venue.offererAddress.addressId
        assert product.offererAddress.label is None

        assert product.venueId == other_venue.id
        assert product.venue.managingOffererId == other_venue.managingOffererId

        assert product.offererAddressId != offerer_address_id


    @pytest.mark.parametrize("address_label", [None, "Salle Gaveau"])
    def test_should_update_the_offerer_address_with_an_address_location(self, address_label):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        venue = venue_provider.venue
        product = self.setup_base_resource(venue=venue, provider=venue_provider.provider)
        address = geography_factories.AddressFactory(street="28 boulevard des Capucines")
        assert address.id != venue.offererAddress.addressId
        offerer_address_id = product.offererAddressId

        location = {"type": "address", "venueId": venue.id, "addressId": address.id}
        if address_label is not None:
            location["addressLabel"] = address_label

        response = self.make_request(plain_api_key, json_body={"offerId": product.id, "location": location})

        assert response.status_code == 200, response.json
        # `get_location` reports an address location because the offerer address differs from
        # the venue one and its label differs from the venue public name
        assert response.json["location"] == {
            "type": "address",
            "venueId": venue.id,
            "addressId": address.id,
            "addressLabel": address_label,
        }

        db.session.refresh(product)
        assert product.offererAddress.addressId == address.id
        assert product.offererAddress.label == address_label
        assert product.offererAddress.type is offerers_models.LocationType.OFFER_LOCATION

        assert product.offererAddressId != offerer_address_id

    def test_should_drop_the_address_label_when_the_address_and_label_match_the_venue_ones(self):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        venue = venue_provider.venue
        product = self.setup_base_resource(venue=venue, provider=venue_provider.provider)
        offerer_address_id = product.offererAddressId
        before_update = product.dateUpdated

        response = self.make_request(
            plain_api_key,
            json_body={
                "offerId": product.id,
                "location": {
                    "type": "address",
                    "venueId": venue.id,
                    "addressId": venue.offererAddress.addressId,
                    "addressLabel": venue.publicName,
                },
            },
        )

        assert response.status_code == 200, response.json

        db.session.refresh(product)
        assert product.offererAddress.label is None
        assert product.offererAddress.addressId == venue.offererAddress.addressId
        assert product.offererAddress.type is offerers_models.LocationType.OFFER_LOCATION
        assert product.offererAddress.id != venue.offererAddress.id
        assert product.offererAddressId == offerer_address_id
        assert product.dateUpdated == before_update


    def test_should_ignore_the_url_of_a_digital_location(self):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        product = self.setup_base_resource(venue=venue_provider.venue, provider=venue_provider.provider)
        assert product.url is None

        response = self.make_request(
            plain_api_key,
            json_body={
                "offerId": product.id,
                "location": {
                    "type": "digital",
                    "venueId": venue_provider.venueId,
                    "url": "https://salle-de-concert.example.com/en-ligne",
                },
            },
        )

        assert response.status_code == 200, response.json
        assert response.json["location"] == {"type": "physical", "venueId": venue_provider.venueId}

        db.session.refresh(product)
        assert product.url is None

    # --- `image`

    def test_should_add_an_image(self, clear_tests_assets_bucket):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        product = self.setup_base_resource(venue=venue_provider.venue, provider=venue_provider.provider)
        assert product.image is None
        before_update = product.dateUpdated

        response = self.make_request(
            plain_api_key,
            json_body={
                "offerId": product.id,
                "image": {"file": image_data.GOOD_IMAGE, "credit": "Archives de la salle"},
            },
        )

        assert response.status_code == 200, response.json

        db.session.refresh(product)
        mediation = db.session.query(offers_models.Mediation).one()
        expected_url = f"{settings.OBJECT_STORAGE_URL}/thumbs/mediations/{human_ids.humanize(mediation.id)}"
        assert product.image.url == expected_url
        assert response.json["image"] == {"url": expected_url, "credit": "Archives de la salle"}
        # the image lives in its own Mediation row: the offer itself is left untouched
        assert product.dateUpdated == before_update


    # --- `stock`

    def test_should_create_a_stock_when_the_product_has_none(self):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        product = self.setup_base_resource(venue=venue_provider.venue, provider=venue_provider.provider)
        assert not product.activeStocks

        response = self.make_request(
            plain_api_key,
            # a price with non-zero cents on purpose, so that a rounding mistake would be visible
            json_body={"offerId": product.id, "stock": {"price": 1234, "quantity": 12}},
        )

        assert response.status_code == 200, response.json
        assert response.json["stock"] == {
            "bookedQuantity": 0,
            "bookingLimitDatetime": None,
            "price": 1234,
            "quantity": 12,
        }

        db.session.refresh(product)
        [stock] = product.activeStocks
        # `Stock.price` is stored in euros, the API speaks cents
        assert stock.price == decimal.Decimal("12.34")
        assert stock.quantity == 12
        assert stock.bookingLimitDatetime is None


    def test_should_add_the_booked_quantity_to_the_quantity_sent(self):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        product = self.setup_base_resource(venue=venue_provider.venue, provider=venue_provider.provider)
        stock = offers_factories.StockFactory(offer=product, price=decimal.Decimal("10.00"), quantity=12)
        bookings_factories.BookingFactory(stock=stock)
        bookings_factories.BookingFactory(stock=stock)
        assert stock.dnBookedQuantity == 2

        response = self.make_request(plain_api_key, json_body={"offerId": product.id, "stock": {"quantity": 20}})

        assert response.status_code == 200, response.json
        assert response.json["stock"]["quantity"] == 22
        assert response.json["stock"]["bookedQuantity"] == 2

        db.session.refresh(product)
        [updated_stock] = product.activeStocks
        assert updated_stock.quantity == 22


    @time_machine.travel(FROZEN_NOW, tick=False)
    def test_should_update_the_stock_booking_limit_datetime(self):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        product = self.setup_base_resource(venue=venue_provider.venue, provider=venue_provider.provider)
        offers_factories.StockFactory(
            offer=product, price=decimal.Decimal("10.00"), quantity=12, bookingLimitDatetime=None
        )

        response = self.make_request(
            # sent in Europe/Paris, read back in UTC
            plain_api_key,
            json_body={"offerId": product.id, "stock": {"bookingLimitDatetime": "2026-09-01T10:00:00+02:00"}},
        )

        assert response.status_code == 200, response.json
        assert response.json["stock"]["bookingLimitDatetime"] == "2026-09-01T08:00:00Z"

        db.session.refresh(product)
        [stock] = product.activeStocks
        # the timezone is stripped on the way in: the column holds a naive UTC datetime
        assert stock.bookingLimitDatetime == datetime.datetime(2026, 9, 1, 8, 0)

    def test_should_clear_the_stock_booking_limit_datetime(self):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        product = self.setup_base_resource(venue=venue_provider.venue, provider=venue_provider.provider)
        stock = offers_factories.StockFactory(
            offer=product,
            price=decimal.Decimal("10.00"),
            quantity=12,
            bookingLimitDatetime=datetime.datetime(2026, 9, 1, 8, 0),
        )

        response = self.make_request(
            plain_api_key, json_body={"offerId": product.id, "stock": {"bookingLimitDatetime": None}}
        )

        assert response.status_code == 200, response.json
        assert response.json["stock"]["bookingLimitDatetime"] is None

        db.session.refresh(product)
        [updated_stock] = product.activeStocks
        # the row is edited, not replaced
        assert updated_stock.id == stock.id
        assert updated_stock.bookingLimitDatetime is None

    def test_should_cancel_the_confirmed_bookings_when_the_stock_is_deleted(self):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        product = self.setup_base_resource(venue=venue_provider.venue, provider=venue_provider.provider)
        stock = offers_factories.StockFactory(offer=product, price=decimal.Decimal("10.00"), quantity=12)
        confirmed_booking = bookings_factories.BookingFactory(
            stock=stock, status=bookings_models.BookingStatus.CONFIRMED
        )
        used_booking = bookings_factories.BookingFactory(stock=stock, status=bookings_models.BookingStatus.USED)

        response = self.make_request(plain_api_key, json_body={"offerId": product.id, "stock": None})

        assert response.status_code == 200, response.json
        assert response.json["stock"] is None

        db.session.refresh(product)
        db.session.refresh(confirmed_booking)
        db.session.refresh(used_booking)
        assert not product.activeStocks
        assert confirmed_booking.status == bookings_models.BookingStatus.CANCELLED
        assert used_booking.status == bookings_models.BookingStatus.USED


@pytest.mark.usefixtures("db_session")
class Returns401Test(PatchProductEndpointHelper):
    def test_should_raise_401_because_not_authenticated(self):
        _, venue_provider = self.setup_active_venue_provider()
        product = self.setup_base_resource(venue=venue_provider.venue, provider=venue_provider.provider)
        before_update = product.dateUpdated

        response = self.make_request(json_body={"offerId": product.id, "name": "Abonnement saison classique"})

        assert response.status_code == 401
        assert response.json == {"auth": "API key required"}

        db.session.refresh(product)
        assert product.dateUpdated == before_update


@pytest.mark.usefixtures("db_session")
class Returns400Test(PatchProductEndpointHelper):
    # --- Request body schema


    def test_should_raise_400_because_an_unknown_field_is_sent(self):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        product = self.setup_base_resource(venue=venue_provider.venue, provider=venue_provider.provider)

        response = self.make_request(
            plain_api_key,
            json_body={"offerId": product.id, "withdrawalDetails": "À retirer au vestiaire"},
        )

        assert response.status_code == 400
        assert response.json == {"withdrawalDetails": ["extra fields not permitted"]}

    @pytest.mark.parametrize(
        "request_field,value,expected_error",
        [
            ("name", "", "ensure this value has at least 1 characters"),
            ("name", "a" * 141, "ensure this value has at most 140 characters"),
            ("description", "a" * 10_001, "ensure this value has at most 10000 characters"),
            ("idAtProvider", "a" * 71, "ensure this value has at most 70 characters"),
        ],
        ids=["name empty", "name too long", "description too long", "idAtProvider too long"],
    )
    def test_should_raise_400_because_a_text_field_length_is_out_of_bounds(self, request_field, value, expected_error):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        product = self.setup_base_resource(venue=venue_provider.venue, provider=venue_provider.provider)

        response = self.make_request(plain_api_key, json_body={"offerId": product.id, request_field: value})

        assert response.status_code == 400
        assert response.json == {request_field: [expected_error]}


    @time_machine.travel(FROZEN_NOW, tick=False)
    @pytest.mark.parametrize("request_field", ["publicationDatetime", "bookingAllowedDatetime"])
    def test_should_raise_400_because_the_datetime_is_not_timezone_aware(self, request_field):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        product = self.setup_base_resource(venue=venue_provider.venue, provider=venue_provider.provider)

        response = self.make_request(
            plain_api_key, json_body={"offerId": product.id, request_field: "2027-01-01T00:00:00"}
        )

        assert response.status_code == 400
        assert response.json == {request_field: ["The datetime must be timezone-aware."]}

    @pytest.mark.parametrize("request_field", ["publicationDatetime", "bookingAllowedDatetime"])
    def test_should_raise_400_because_the_datetime_is_in_the_past(self, request_field):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        product = self.setup_base_resource(venue=venue_provider.venue, provider=venue_provider.provider)

        response = self.make_request(
            plain_api_key, json_body={"offerId": product.id, request_field: "2021-01-01T00:00:00+00:00"}
        )

        assert response.status_code == 400
        assert response.json == {request_field: ["The datetime must be in the future."]}

    def test_should_raise_400_because_publication_datetime_literal_is_not_lowercase_now(self):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        product = self.setup_base_resource(venue=venue_provider.venue, provider=venue_provider.provider)

        response = self.make_request(plain_api_key, json_body={"offerId": product.id, "publicationDatetime": "NOW"})

        assert response.status_code == 400
        assert response.json == {
            "publicationDatetime": ["invalid datetime format", "unexpected value; permitted: 'now'"]
        }


    # --- Subcategory

    @pytest.mark.parametrize(
        "partial_body",
        [
            {"name": "Abonnement saison classique"},
            {"categoryRelatedFields": {"category": "ABO_SPECTACLE"}},
        ],
        ids=["plain field", "another category"],
    )
    def test_should_raise_400_because_the_subcategory_cannot_be_edited(self, partial_body):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        product = self.setup_base_resource(
            venue=venue_provider.venue,
            provider=venue_provider.provider,
            subcategoryId=subcategories.LIVRE_PAPIER.id,
            extraData=None,
        )

        response = self.make_request(plain_api_key, json_body={"offerId": product.id, **partial_body})

        assert response.status_code == 400
        allowed = ", ".join(subcategory.id for subcategory in v1_serialization.ALLOWED_PRODUCT_SUBCATEGORIES)
        assert response.json == {"product.subcategory": [f"Only {allowed} products can be edited"]}

    # --- `stock`


    @pytest.mark.parametrize(
        "price,expected_error",
        [
            (-1200, "ensure this value is greater than or equal to 0"),
            (30_001, "ensure this value is less than or equal to 30000"),
            (12.34, "value is not a valid integer"),
            ("1000", "value is not a valid integer"),
        ],
        ids=["negative", "above the ceiling", "float", "numeric string"],
    )
    def test_should_raise_400_because_stock_price_is_invalid(self, price, expected_error):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        product = self.setup_base_resource(venue=venue_provider.venue, provider=venue_provider.provider)

        response = self.make_request(
            plain_api_key, json_body={"offerId": product.id, "stock": {"price": price, "quantity": 1}}
        )

        assert response.status_code == 400
        assert response.json == {"stock.price": [expected_error]}

    @pytest.mark.parametrize(
        "quantity,expected_errors",
        [
            (-1, ["ensure this value is greater than or equal to 0", "unexpected value; permitted: 'unlimited'"]),
            (
                offers_models.Stock.MAX_STOCK_QUANTITY + 1,
                [f"Value must be less than {offers_models.Stock.MAX_STOCK_QUANTITY}"],
            ),
            ("beaucoup", ["value is not a valid integer", "unexpected value; permitted: 'unlimited'"]),
        ],
        ids=["negative", "above the ceiling", "unknown literal"],
    )
    def test_should_raise_400_because_stock_quantity_is_invalid(self, quantity, expected_errors):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        product = self.setup_base_resource(venue=venue_provider.venue, provider=venue_provider.provider)

        response = self.make_request(
            plain_api_key, json_body={"offerId": product.id, "stock": {"price": 1000, "quantity": quantity}}
        )

        assert response.status_code == 400
        assert response.json == {"stock.quantity": expected_errors}

    @time_machine.travel(FROZEN_NOW, tick=False)
    @pytest.mark.parametrize(
        "booking_limit_datetime,expected_error",
        [
            ("2027-01-01T00:00:00", "The datetime must be timezone-aware."),
            ("2021-01-01T00:00:00+00:00", "The datetime must be in the future."),
        ],
        ids=["not timezone aware", "in the past"],
    )
    def test_should_raise_400_because_stock_booking_limit_datetime_is_invalid(
        self, booking_limit_datetime, expected_error
    ):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        product = self.setup_base_resource(venue=venue_provider.venue, provider=venue_provider.provider)

        response = self.make_request(
            plain_api_key,
            json_body={
                "offerId": product.id,
                "stock": {"price": 1000, "quantity": 1, "bookingLimitDatetime": booking_limit_datetime},
            },
        )

        assert response.status_code == 400
        assert response.json == {"stock.bookingLimitDatetime": [expected_error]}

    @time_machine.travel(FROZEN_NOW, tick=False)
    @pytest.mark.parametrize(
        "offer_datetime_field",
        ["publicationDatetime", "bookingAllowedDatetime"],
    )
    def test_should_raise_400_because_stock_booking_limit_datetime_is_before_a_datetime_sent_in_the_same_request(
        self, offer_datetime_field
    ):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        product = self.setup_base_resource(venue=venue_provider.venue, provider=venue_provider.provider)

        response = self.make_request(
            plain_api_key,
            json_body={
                "offerId": product.id,
                offer_datetime_field: "2026-09-01T00:00:00+00:00",
                "stock": {"price": 1000, "quantity": 1, "bookingLimitDatetime": "2026-07-01T00:00:00+00:00"},
            },
        )

        assert response.status_code == 400
        assert response.json == {"__root__": [f"`stock.bookingLimitDatetime` must be after `{offer_datetime_field}`"]}


    # --- `image`

    def test_should_raise_400_because_the_image_is_invalid(self):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        product = self.setup_base_resource(venue=venue_provider.venue, provider=venue_provider.provider)
        before_update = product.dateUpdated

        response = self.make_request(
            plain_api_key,
            json_body={
                "offerId": product.id,
                "name": "Abonnement saison classique",
                "image": {"file": image_data.WRONG_IMAGE_SIZE},
            },
        )

        assert response.status_code == 400
        assert response.json == {"imageFile": "The image is too small. It must be above 400x600 pixels."}

        db.session.refresh(product)
        assert product.name == "Abonnement saison jazz"
        assert product.dateUpdated == before_update
        assert not db.session.query(offers_models.Mediation).all()

    # --- `name`


    def test_should_raise_400_because_name_contains_an_ean(self):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        product = self.setup_base_resource(venue=venue_provider.venue, provider=venue_provider.provider)

        response = self.make_request(
            plain_api_key,
            json_body={"offerId": product.id, "name": "Abonnement saison jazz - 9782070286256"},
        )

        assert response.status_code == 400
        assert response.json == {"name": ["Le titre d'une offre ne peut contenir l'EAN"]}

    # --- `idAtProvider`

    def test_should_raise_400_because_id_at_provider_is_already_taken_by_another_offer_of_the_venue(self):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        product = self.setup_base_resource(venue=venue_provider.venue, provider=venue_provider.provider)
        id_at_provider = "abonnement-jazz-2026"
        offers_factories.OfferFactory(venue=venue_provider.venue, idAtProvider=id_at_provider)

        response = self.make_request(plain_api_key, json_body={"offerId": product.id, "idAtProvider": id_at_provider})

        assert response.status_code == 400
        assert response.json == {"idAtProvider": [f"`{id_at_provider}` is already taken by another venue offer"]}


@pytest.mark.usefixtures("db_session")
class Returns404Test(PatchProductEndpointHelper):
    PRODUCT_NOT_FOUND = {"offerId": ["The product offer could not be found"]}
    VENUE_NOT_FOUND = {"global": "Venue cannot be found"}

    # --- The product

    def test_should_raise_404_because_product_does_not_exist(self):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        product = self.setup_base_resource(venue=venue_provider.venue, provider=venue_provider.provider)

        response = self.make_request(
            plain_api_key, json_body={"offerId": product.id + 1, "name": "Abonnement saison classique"}
        )

        assert response.status_code == 404
        assert response.json == self.PRODUCT_NOT_FOUND


    def test_should_raise_404_because_has_no_access_to_venue(self):
        plain_api_key, _ = self.setup_provider()
        product = self.setup_base_resource()

        response = self.make_request(
            plain_api_key, json_body={"offerId": product.id, "name": "Abonnement saison classique"}
        )

        assert response.status_code == 404
        assert response.json == self.PRODUCT_NOT_FOUND

    def test_should_raise_404_because_venue_provider_is_inactive(self):
        plain_api_key, venue_provider = self.setup_inactive_venue_provider()
        product = self.setup_base_resource(venue=venue_provider.venue, provider=venue_provider.provider)

        response = self.make_request(
            plain_api_key, json_body={"offerId": product.id, "name": "Abonnement saison classique"}
        )

        assert response.status_code == 404
        assert response.json == self.PRODUCT_NOT_FOUND


    # --- `location`

    def test_should_raise_404_because_venue_in_location_is_not_linked_to_provider(self):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        product = self.setup_base_resource(venue=venue_provider.venue, provider=venue_provider.provider)
        other_venue = self.setup_venue()
        before_update = product.dateUpdated

        response = self.make_request(
            plain_api_key,
            json_body={"offerId": product.id, "location": {"type": "physical", "venueId": other_venue.id}},
        )

        assert response.status_code == 404
        assert response.json == self.VENUE_NOT_FOUND

        db.session.refresh(product)
        assert product.dateUpdated == before_update


