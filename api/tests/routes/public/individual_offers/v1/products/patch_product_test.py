import datetime
import decimal
import logging
from unittest import mock

import pytest
import time_machine

from pcapi import settings
from pcapi.core import testing
from pcapi.core.bookings import factories as bookings_factories
from pcapi.core.bookings import models as bookings_models
from pcapi.core.categories import subcategories
from pcapi.core.geography import factories as geography_factories
from pcapi.core.offerers import models as offerers_models
from pcapi.core.offers import factories as offers_factories
from pcapi.core.offers import models as offers_models
from pcapi.core.providers import factories as providers_factories
from pcapi.core.search.models import IndexationReason
from pcapi.models import db
from pcapi.routes.public.individual_offers.v1 import serialization as v1_serialization
from pcapi.utils import human_ids

from tests.routes import image_data
from tests.routes.public.helpers import PublicAPIVenueEndpointHelper
from tests.routes.public.individual_offers.v1 import utils as test_utils


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

    @pytest.mark.parametrize("new_value", [True, False], ids=["enable", "disable"])
    def test_should_toggle_double_bookings(self, new_value):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        product = self.setup_base_resource(
            venue=venue_provider.venue,
            provider=venue_provider.provider,
            # CARTE_MUSEE is the only allowed product subcategory accepting double bookings
            subcategoryId=subcategories.CARTE_MUSEE.id,
            extraData=None,
            isDuo=not new_value,
        )

        response = self.make_request(
            plain_api_key, json_body={"offerId": product.id, "enableDoubleBookings": new_value}
        )

        assert response.status_code == 200, response.json
        assert response.json["enableDoubleBookings"] is new_value

        db.session.refresh(product)
        assert product.isDuo is new_value

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

    # --- Field name spellings

    @time_machine.travel(FROZEN_NOW, tick=False)
    def test_should_accept_a_snake_case_body(self):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        product = self.setup_base_resource(venue=venue_provider.venue, provider=venue_provider.provider)
        offers_factories.StockFactory(offer=product, price=10, quantity=5)
        address = geography_factories.AddressFactory(street="28 boulevard des Capucines")

        response = self.make_request(
            plain_api_key,
            json_body={
                "offerId": product.id,
                # `ProductOfferEdition`
                "booking_email": "nouvelle-adresse@salle-de-concert.example.com",
                # the only field with an explicit alias: `itemCollectionDetails`
                "withdrawal_details": "À retirer au vestiaire",
                # `PartialAccessibility`
                "accessibility": {"audio_disability_compliant": False},
                # `AddressLocation`
                "location": {"type": "address", "venue_id": venue_provider.venueId, "address_id": address.id},
                # `StockEdition`
                "stock": {"booking_limit_datetime": "2026-09-01T10:00:00+02:00"},
                # the per-category model, whose only aliased field is `subcategory_id` -> `category`
                "category_related_fields": {"subcategory_id": "ABO_CONCERT", "musicType": "MUSIQUE_CLASSIQUE"},
            },
        )

        assert response.status_code == 200, response.json
        assert response.json["bookingEmail"] == "nouvelle-adresse@salle-de-concert.example.com"
        assert response.json["stock"]["bookingLimitDatetime"] == "2026-09-01T08:00:00Z"

        db.session.refresh(product)
        expected = {
            "bookingEmail": "nouvelle-adresse@salle-de-concert.example.com",
            "withdrawalDetails": "À retirer au vestiaire",
            "audioDisabilityCompliant": False,
        }
        assert {column: getattr(product, column) for column in expected} == expected
        assert product.offererAddress.addressId == address.id
        assert product.extraData["gtl_id"] == "01000000"

    # --- Type coercion

    def test_should_accept_an_offer_id_sent_as_a_string(self):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        product = self.setup_base_resource(venue=venue_provider.venue, provider=venue_provider.provider)

        response = self.make_request(
            plain_api_key, json_body={"offerId": str(product.id), "name": "Abonnement saison classique"}
        )

        assert response.status_code == 200, response.json
        assert response.json["id"] == product.id

        db.session.refresh(product)
        assert product.name == "Abonnement saison classique"

    # --- `idAtProvider`

    def test_should_accept_an_id_at_provider_already_used_by_an_offer_of_another_venue(self):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        product = self.setup_base_resource(venue=venue_provider.venue, provider=venue_provider.provider)
        id_at_provider = "abonnement-jazz-2026"
        offers_factories.OfferFactory(venue=self.setup_venue(), idAtProvider=id_at_provider)

        response = self.make_request(plain_api_key, json_body={"offerId": product.id, "idAtProvider": id_at_provider})

        assert response.status_code == 200, response.json
        assert response.json["idAtProvider"] == id_at_provider

        db.session.refresh(product)
        assert product.idAtProvider == id_at_provider

    # --- `accessibility`

    def test_should_update_every_accessibility_field(self):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        product = self.setup_base_resource(venue=venue_provider.venue, provider=venue_provider.provider)
        flipped = {
            "audioDisabilityCompliant": False,
            "mentalDisabilityCompliant": True,
            "motorDisabilityCompliant": False,
            "visualDisabilityCompliant": True,
        }

        response = self.make_request(plain_api_key, json_body={"offerId": product.id, "accessibility": flipped})

        assert response.status_code == 200, response.json
        assert response.json["accessibility"] == flipped

        db.session.refresh(product)
        assert {column: getattr(product, column) for column in flipped} == flipped

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

    # --- `categoryRelatedFields`

    def test_should_store_the_music_type_as_codes_and_return_it_as_a_slug(self):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        product = self.setup_base_resource(
            venue=venue_provider.venue,
            provider=venue_provider.provider,
            extraData={"musicType": "900", "musicSubType": "901", "gtl_id": "01000000"},
        )

        response = self.make_request(
            plain_api_key,
            json_body={
                "offerId": product.id,
                "categoryRelatedFields": {"category": "ABO_CONCERT", "musicType": "JAZZ-BLUES"},
            },
        )

        assert response.status_code == 200, response.json
        assert response.json["categoryRelatedFields"] == {"category": "ABO_CONCERT", "musicType": "JAZZ-BLUES"}

        db.session.refresh(product)
        assert product.extraData == {"musicType": "501", "musicSubType": "-1", "gtl_id": "02000000"}

    def test_should_store_the_show_type_as_codes_and_return_it_as_a_slug(self):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        product = self.setup_base_resource(
            venue=venue_provider.venue,
            provider=venue_provider.provider,
            subcategoryId=subcategories.ABO_SPECTACLE.id,
            extraData={"showType": "1510", "showSubType": "1512"},
        )

        response = self.make_request(
            plain_api_key,
            json_body={
                "offerId": product.id,
                "categoryRelatedFields": {"category": "ABO_SPECTACLE", "showType": "OPERA-SINGSPIEL"},
            },
        )

        assert response.status_code == 200, response.json
        assert response.json["categoryRelatedFields"] == {
            "category": "ABO_SPECTACLE",
            "showType": "OPERA-SINGSPIEL",
        }

        db.session.refresh(product)
        assert product.extraData == {"showType": "1510", "showSubType": "1516"}

    def test_should_keep_the_extra_data_subfields_that_are_not_sent(self):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        product = self.setup_base_resource(
            venue=venue_provider.venue,
            provider=venue_provider.provider,
            extraData={"author": "Bill Evans", "musicType": "900", "musicSubType": "901", "gtl_id": "01000000"},
        )

        response = self.make_request(
            plain_api_key,
            json_body={
                "offerId": product.id,
                "categoryRelatedFields": {"category": "ABO_CONCERT", "musicType": "JAZZ-BLUES"},
            },
        )

        assert response.status_code == 200, response.json
        # `author` is not part of the ABO_CONCERT model, so it is stored but never returned
        assert response.json["categoryRelatedFields"] == {"category": "ABO_CONCERT", "musicType": "JAZZ-BLUES"}

        db.session.refresh(product)
        assert product.extraData == {
            "author": "Bill Evans",
            "musicType": "501",
            "musicSubType": "-1",
            "gtl_id": "02000000",
        }

    def test_should_store_an_empty_category_related_field_as_an_empty_string(self):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        product = self.setup_base_resource(
            venue=venue_provider.venue,
            provider=venue_provider.provider,
            subcategoryId=subcategories.LIVRE_NUMERIQUE.id,
            url="https://librairie.example.com/a-la-recherche-du-temps-perdu",
            offererAddress=None,
            extraData={"author": "Marcel Proust"},
        )

        response = self.make_request(
            plain_api_key,
            json_body={
                "offerId": product.id,
                "categoryRelatedFields": {"category": "LIVRE_NUMERIQUE", "author": ""},
            },
        )

        assert response.status_code == 200, response.json
        assert response.json["categoryRelatedFields"]["author"] == ""

        db.session.refresh(product)
        assert product.extraData == {"author": ""}

    @pytest.mark.parametrize(
        "category_related_fields",
        [None, {"category": "ABO_CONCERT"}],
        ids=["null", "category only"],
    )
    def test_should_keep_extra_data_when_no_subfield_is_sent(self, category_related_fields):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        product = self.setup_base_resource(venue=venue_provider.venue, provider=venue_provider.provider)
        before_update = product.dateUpdated

        response = self.make_request(
            plain_api_key,
            json_body={"offerId": product.id, "categoryRelatedFields": category_related_fields},
        )

        assert response.status_code == 200, response.json

        db.session.refresh(product)
        assert product.dateUpdated == before_update

    def test_should_ignore_an_unknown_category_related_field(self):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        product = self.setup_base_resource(
            venue=venue_provider.venue,
            provider=venue_provider.provider,
            extraData={"musicType": "900", "musicSubType": "901", "gtl_id": "01000000"},
        )

        response = self.make_request(
            plain_api_key,
            json_body={
                "offerId": product.id,
                "categoryRelatedFields": {
                    "category": "ABO_CONCERT",
                    "musicType": "JAZZ-BLUES",
                    "producteur": "Marcel Berbert",
                },
            },
        )

        assert response.status_code == 200, response.json
        assert "producteur" not in response.json["categoryRelatedFields"]

        db.session.refresh(product)
        assert product.extraData == {"musicType": "501", "musicSubType": "-1", "gtl_id": "02000000"}

    def test_should_ignore_the_ean_sent_in_the_category_related_fields(self):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        product = self.setup_base_resource(
            venue=venue_provider.venue,
            provider=venue_provider.provider,
            subcategoryId=subcategories.LIVRE_NUMERIQUE.id,
            url="https://librairie.example.com/a-la-recherche-du-temps-perdu",
            offererAddress=None,
            ean="9782070100002",
            extraData={"author": "Marcel Proust"},
        )

        response = self.make_request(
            plain_api_key,
            json_body={
                "offerId": product.id,
                "categoryRelatedFields": {
                    "category": "LIVRE_NUMERIQUE",
                    "author": "Marcel Proust, édition annotée",
                    "ean": "9782070100019",
                },
            },
        )

        assert response.status_code == 200, response.json
        # the answer echoes the stored `ean`, not the one just sent
        assert response.json["categoryRelatedFields"] == {
            "category": "LIVRE_NUMERIQUE",
            "author": "Marcel Proust, édition annotée",
            "ean": "9782070100002",
        }

        db.session.refresh(product)
        assert product.ean == "9782070100002"
        assert product.extraData == {"author": "Marcel Proust, édition annotée"}

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

    def test_should_ignore_deprecated_is_active_when_it_is_none(self):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        product = self.setup_base_resource(venue=venue_provider.venue, provider=venue_provider.provider)
        before_update = product.dateUpdated
        assert product.isActive is True

        response = self.make_request(plain_api_key, json_body={"offerId": product.id, "isActive": None})

        assert response.status_code == 200, response.json

        db.session.refresh(product)
        assert product.dateUpdated == before_update
        # `isActive` is derived from `publicationDatetime`, which was left untouched
        assert product.isActive is True

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

    @time_machine.travel(FROZEN_NOW, tick=False)
    def test_should_activate_with_deprecated_is_active_true(self):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        product = self.setup_base_resource(
            venue=venue_provider.venue, provider=venue_provider.provider, publicationDatetime=None
        )
        assert product.isActive is False

        response = self.make_request(plain_api_key, json_body={"offerId": product.id, "isActive": True})

        assert response.status_code == 200, response.json
        assert response.json["publicationDatetime"] == "2026-06-25T12:30:00Z"

        db.session.refresh(product)
        assert product.publicationDatetime == datetime.datetime(2026, 6, 25, 12, 30, tzinfo=datetime.UTC)
        assert product.isActive is True

    @time_machine.travel(FROZEN_NOW, tick=False)
    def test_should_let_publication_datetime_win_over_deprecated_is_active(self):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        product = self.setup_base_resource(venue=venue_provider.venue, provider=venue_provider.provider)

        response = self.make_request(
            plain_api_key,
            json_body={
                "offerId": product.id,
                "isActive": False,
                "publicationDatetime": "2026-08-01T08:00:00+02:00",
            },
        )

        assert response.status_code == 200, response.json
        assert response.json["publicationDatetime"] == "2026-08-01T06:00:00Z"
        assert response.json["status"] == "SCHEDULED"

        db.session.refresh(product)
        assert product.publicationDatetime == datetime.datetime(2026, 8, 1, 6, 0, tzinfo=datetime.UTC)

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

    def test_should_move_the_product_to_another_venue_with_an_address_location(self):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        product = self.setup_base_resource(venue=venue_provider.venue, provider=venue_provider.provider)

        other_venue = providers_factories.VenueProviderFactory(provider=venue_provider.provider).venue
        address = geography_factories.AddressFactory(street="28 boulevard des Capucines")

        response = self.make_request(
            plain_api_key,
            json_body={
                "offerId": product.id,
                "location": {"type": "address", "venueId": other_venue.id, "addressId": address.id},
            },
        )

        assert response.status_code == 200, response.json
        assert response.json["location"] == {
            "type": "address",
            "venueId": other_venue.id,
            "addressId": address.id,
            "addressLabel": None,
        }

        db.session.refresh(product)
        assert product.venueId == other_venue.id
        assert product.offererAddress.addressId == address.id
        assert product.offererAddress.type is offerers_models.LocationType.OFFER_LOCATION
        # the offerer address is attached to the venue the product moves to, not to the one it leaves
        assert product.offererAddress.offererId == other_venue.managingOffererId

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

    def test_should_keep_the_address_label_when_it_differs_from_the_venue_public_name(self):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        venue = venue_provider.venue
        product = self.setup_base_resource(venue=venue, provider=venue_provider.provider)
        assert venue.publicName != "Salle Gaveau"
        offerer_address_id = product.offererAddressId

        response = self.make_request(
            plain_api_key,
            json_body={
                "offerId": product.id,
                "location": {
                    "type": "address",
                    "venueId": venue.id,
                    "addressId": venue.offererAddress.addressId,
                    "addressLabel": "Salle Gaveau",
                },
            },
        )

        assert response.status_code == 200, response.json

        db.session.refresh(product)
        assert product.offererAddress.label == "Salle Gaveau"
        assert product.offererAddress.addressId == venue.offererAddress.addressId

        assert product.offererAddressId != offerer_address_id

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

    def test_should_keep_the_image_when_it_is_explicitly_sent_as_none(self, clear_tests_assets_bucket):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        product = self.setup_base_resource(venue=venue_provider.venue, provider=venue_provider.provider)
        self.make_request(plain_api_key, json_body={"offerId": product.id, "image": {"file": image_data.GOOD_IMAGE}})
        mediation_id = db.session.query(offers_models.Mediation).one().id
        before_update = product.dateUpdated

        response = self.make_request(plain_api_key, json_body={"offerId": product.id, "image": None})

        assert response.status_code == 200, response.json

        db.session.refresh(product)
        assert db.session.query(offers_models.Mediation).one().id == mediation_id
        assert product.dateUpdated == before_update

    @mock.patch("pcapi.core.search.async_index_offer_ids")
    def test_should_reindex_the_product_when_an_image_is_added(
        self, mocked_async_index_offer_ids, clear_tests_assets_bucket
    ):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        product = self.setup_base_resource(venue=venue_provider.venue, provider=venue_provider.provider)

        response = self.make_request(
            plain_api_key, json_body={"offerId": product.id, "image": {"file": image_data.GOOD_IMAGE}}
        )

        assert response.status_code == 200, response.json
        mocked_async_index_offer_ids.assert_called_once_with([product.id], reason=IndexationReason.MEDIATION_CREATION)

    def test_should_not_log_an_offer_update_when_only_the_image_changed(self, caplog, clear_tests_assets_bucket):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        product = self.setup_base_resource(venue=venue_provider.venue, provider=venue_provider.provider)

        with caplog.at_level(logging.INFO):
            response = self.make_request(
                plain_api_key, json_body={"offerId": product.id, "image": {"file": image_data.GOOD_IMAGE}}
            )

        assert response.status_code == 200, response.json
        assert not has_log(caplog, "offer.updated")

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

    @pytest.mark.parametrize(
        "stock_body",
        [{"price": 1000, "quantity": "unlimited"}, {"price": 1000}],
        ids=["explicit", "omitted"],
    )
    def test_should_create_an_unlimited_stock(self, stock_body):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        product = self.setup_base_resource(venue=venue_provider.venue, provider=venue_provider.provider)

        response = self.make_request(plain_api_key, json_body={"offerId": product.id, "stock": stock_body})

        assert response.status_code == 200, response.json
        assert response.json["stock"]["quantity"] == "unlimited"

        db.session.refresh(product)
        [stock] = product.activeStocks
        assert stock.quantity is None

    @time_machine.travel(FROZEN_NOW, tick=False)
    def test_should_create_a_stock_with_a_booking_limit_datetime(self):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        product = self.setup_base_resource(venue=venue_provider.venue, provider=venue_provider.provider)

        response = self.make_request(
            plain_api_key,
            json_body={
                "offerId": product.id,
                # sent in Europe/Paris, read back in UTC
                "stock": {"price": 1000, "quantity": 1, "bookingLimitDatetime": "2026-09-01T10:00:00+02:00"},
            },
        )

        assert response.status_code == 200, response.json
        assert response.json["stock"]["bookingLimitDatetime"] == "2026-09-01T08:00:00Z"

        db.session.refresh(product)
        [stock] = product.activeStocks
        assert stock.bookingLimitDatetime == datetime.datetime(2026, 9, 1, 8, 0)

    @pytest.mark.parametrize(
        "stock_body,expected_stock",
        [
            (
                {"price": 2000},
                {"bookedQuantity": 0, "bookingLimitDatetime": "2026-09-01T08:00:00Z", "price": 2000, "quantity": 12},
            ),
            (
                {"quantity": 20},
                {"bookedQuantity": 0, "bookingLimitDatetime": "2026-09-01T08:00:00Z", "price": 1000, "quantity": 20},
            ),
        ],
        ids=["price only", "quantity only"],
    )
    def test_should_update_one_stock_field_and_keep_the_others(self, stock_body, expected_stock):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        product = self.setup_base_resource(venue=venue_provider.venue, provider=venue_provider.provider)
        stock = offers_factories.StockFactory(
            offer=product,
            price=decimal.Decimal("10.00"),
            quantity=12,
            bookingLimitDatetime=datetime.datetime(2026, 9, 1, 8, 0),
        )

        response = self.make_request(plain_api_key, json_body={"offerId": product.id, "stock": stock_body})

        assert response.status_code == 200, response.json
        assert response.json["stock"] == expected_stock

        db.session.refresh(product)
        [updated_stock] = product.activeStocks
        assert updated_stock.id == stock.id

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

    def test_should_make_the_stock_unlimited(self):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        product = self.setup_base_resource(venue=venue_provider.venue, provider=venue_provider.provider)
        stock = offers_factories.StockFactory(offer=product, price=decimal.Decimal("10.00"), quantity=12)
        bookings_factories.BookingFactory(stock=stock)

        response = self.make_request(
            plain_api_key, json_body={"offerId": product.id, "stock": {"quantity": "unlimited"}}
        )

        assert response.status_code == 200, response.json
        assert response.json["stock"]["quantity"] == "unlimited"

        db.session.refresh(product)
        [updated_stock] = product.activeStocks
        assert updated_stock.quantity is None

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

    @pytest.mark.parametrize(
        "with_existing_stock,stock_body,expected_message_id",
        [
            (False, {"price": 1000, "quantity": 1}, "stock.created"),
            (True, {"price": 2000}, "stock.updated"),
            (True, None, "stock.deleted"),
        ],
        ids=["created", "updated", "deleted"],
    )
    def test_should_log_the_stock_upsert(self, caplog, with_existing_stock, stock_body, expected_message_id):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        product = self.setup_base_resource(venue=venue_provider.venue, provider=venue_provider.provider)
        if with_existing_stock:
            offers_factories.StockFactory(offer=product, price=decimal.Decimal("10.00"), quantity=12)

        with caplog.at_level(logging.INFO):
            response = self.make_request(plain_api_key, json_body={"offerId": product.id, "stock": stock_body})

        assert response.status_code == 200, response.json
        assert has_log(caplog, expected_message_id)

    @pytest.mark.parametrize(
        "with_existing_stock,stock_body,expected_call",
        [
            (False, {"price": 1000, "quantity": 1}, {"reason": IndexationReason.STOCK_CREATION}),
            (
                True,
                {"price": 2000},
                {"reason": IndexationReason.STOCK_UPDATE, "log_extra": {"changes": {"price"}}},
            ),
        ],
        ids=["created", "edited"],
    )
    @mock.patch("pcapi.core.search.async_index_offer_ids")
    def test_should_reindex_the_product_when_the_stock_changes(
        self, mocked_async_index_offer_ids, with_existing_stock, stock_body, expected_call
    ):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        product = self.setup_base_resource(venue=venue_provider.venue, provider=venue_provider.provider)
        if with_existing_stock:
            offers_factories.StockFactory(offer=product, price=decimal.Decimal("10.00"), quantity=12)

        response = self.make_request(plain_api_key, json_body={"offerId": product.id, "stock": stock_body})

        assert response.status_code == 200, response.json
        # only the edition carries the changed field names
        mocked_async_index_offer_ids.assert_called_once_with([product.id], **expected_call)

    def test_should_not_log_an_offer_update_when_only_the_stock_changed(self, caplog):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        product = self.setup_base_resource(venue=venue_provider.venue, provider=venue_provider.provider)
        offers_factories.StockFactory(offer=product, price=decimal.Decimal("10.00"), quantity=12)

        with caplog.at_level(logging.INFO):
            response = self.make_request(plain_api_key, json_body={"offerId": product.id, "stock": {"price": 2000}})

        assert response.status_code == 200, response.json
        # the stock did change, so the absence of `offer.updated` is not merely a no-op request
        assert has_log(caplog, "stock.updated")
        assert not has_log(caplog, "offer.updated")

    # --- Products the calling provider did not create

    def test_should_update_a_product_created_on_the_pro_interface(self):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        product = self.setup_base_resource(venue=venue_provider.venue, provider=None)
        assert product.lastProvider is None

        response = self.make_request(
            plain_api_key,
            json_body={"offerId": product.id, "itemCollectionDetails": "À retirer au vestiaire"},
        )

        assert response.status_code == 200, response.json
        assert response.json["itemCollectionDetails"] == "À retirer au vestiaire"

        db.session.refresh(product)
        assert product.withdrawalDetails == "À retirer au vestiaire"

    @pytest.mark.parametrize(
        "partial_body,expected_changes",
        [
            ({"name": "Abonnement saison classique"}, {"name": "Abonnement saison classique"}),
            (
                {"description": "Six concerts de musique de chambre sur la saison."},
                {"description": "Six concerts de musique de chambre sur la saison."},
            ),
            (
                {"externalTicketOfficeUrl": "https://salle-de-concert.example.com/billetterie"},
                {"externalTicketOfficeUrl": "https://salle-de-concert.example.com/billetterie"},
            ),
            ({"accessibility": {"audioDisabilityCompliant": False}}, {"audioDisabilityCompliant": False}),
        ],
    )
    def test_should_update_a_product_synchronized_by_another_provider(self, partial_body, expected_changes):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        synchronizing_provider = providers_factories.ProviderFactory()
        product = self.setup_base_resource(venue=venue_provider.venue, provider=synchronizing_provider)
        assert not product.lastProvider.isAllocine
        assert not product.lastProvider.hasOffererProvider

        response = self.make_request(plain_api_key, json_body={"offerId": product.id, **partial_body})

        assert response.status_code == 200, response.json

        db.session.refresh(product)
        assert {column: getattr(product, column) for column in expected_changes} == expected_changes

    def test_should_update_a_product_synchronized_by_another_public_api_provider(self):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        other_provider = providers_factories.PublicApiProviderFactory()
        providers_factories.OffererProviderFactory(provider=other_provider)
        product = self.setup_base_resource(venue=venue_provider.venue, provider=other_provider)
        assert product.lastProvider.hasOffererProvider

        response = self.make_request(
            plain_api_key,
            json_body={"offerId": product.id, "itemCollectionDetails": "À retirer au vestiaire"},
        )

        assert response.status_code == 200, response.json

        db.session.refresh(product)
        assert product.withdrawalDetails == "À retirer au vestiaire"

    def test_should_accept_resending_the_current_value_of_a_field_locked_by_the_provider(self):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        synchronizing_provider = providers_factories.ProviderFactory()
        product = self.setup_base_resource(venue=venue_provider.venue, provider=synchronizing_provider)
        assert not product.lastProvider.hasOffererProvider
        before_update = product.dateUpdated

        # `bookingEmail` is outside this provider's editable set
        response = self.make_request(
            plain_api_key, json_body={"offerId": product.id, "bookingEmail": product.bookingEmail}
        )

        assert response.status_code == 200, response.json

        db.session.refresh(product)
        assert product.dateUpdated == before_update

    # --- Response

    def test_should_return_the_updated_product(self):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        product = self.setup_base_resource(
            venue=venue_provider.venue, provider=venue_provider.provider, idAtProvider="abonnement-jazz-2026"
        )

        response = self.make_request(
            plain_api_key, json_body={"offerId": product.id, "name": "Abonnement saison classique"}
        )

        assert response.status_code == 200, response.json
        assert response.json == {
            "id": product.id,
            "name": "Abonnement saison classique",
            "description": "Six concerts de jazz sur la saison, au tarif abonné.",
            "accessibility": {
                "audioDisabilityCompliant": True,
                "mentalDisabilityCompliant": False,
                "motorDisabilityCompliant": True,
                "visualDisabilityCompliant": False,
            },
            "bookingContact": "contact@salle-de-concert.example.com",
            "bookingEmail": "notify@salle-de-concert.example.com",
            "categoryRelatedFields": {"category": "ABO_CONCERT", "musicType": "JAZZ-BLUES"},
            "enableDoubleBookings": False,
            "externalTicketOfficeUrl": "https://salle-de-concert.example.com/reservations",
            "idAtProvider": "abonnement-jazz-2026",
            "image": None,
            "itemCollectionDetails": "À retirer au guichet",
            "location": {"type": "physical", "venueId": venue_provider.venueId},
            "publicationDatetime": "2026-01-15T10:00:00Z",
            "bookingAllowedDatetime": "2026-02-01T10:00:00Z",
            # published and bookable, but with no stock
            "status": "SOLD_OUT",
            "stock": None,
        }

    @time_machine.travel(FROZEN_NOW, tick=False)
    @pytest.mark.parametrize(
        "partial_body,expected_status",
        [
            ({"publicationDatetime": None}, "INACTIVE"),
            ({"publicationDatetime": "2026-08-01T08:00:00+02:00"}, "SCHEDULED"),
            ({"bookingAllowedDatetime": "2026-08-01T08:00:00+02:00"}, "PUBLISHED"),
            ({"name": "Abonnement saison classique"}, "ACTIVE"),
        ],
        ids=["inactive", "scheduled", "published", "active"],
    )
    def test_should_return_the_new_status(self, partial_body, expected_status):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        product = self.setup_base_resource(venue=venue_provider.venue, provider=venue_provider.provider)
        offers_factories.StockFactory(offer=product, price=decimal.Decimal("10.00"), quantity=12)

        response = self.make_request(plain_api_key, json_body={"offerId": product.id, **partial_body})

        assert response.status_code == 200, response.json
        assert response.json["status"] == expected_status

    # --- Side effects

    @mock.patch("pcapi.core.search.async_index_offer_ids")
    def test_should_reindex_the_product(self, mocked_async_index_offer_ids):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        product = self.setup_base_resource(venue=venue_provider.venue, provider=venue_provider.provider)

        response = self.make_request(
            plain_api_key,
            json_body={
                "offerId": product.id,
                "name": "Abonnement saison classique",
                "bookingEmail": "nouvelle-adresse@salle-de-concert.example.com",
            },
        )

        assert response.status_code == 200, response.json
        mocked_async_index_offer_ids.assert_called_once_with(
            [product.id],
            reason=IndexationReason.OFFER_UPDATE,
            log_extra={"changes": {"name", "bookingEmail"}},
        )

    def test_should_log_the_update_with_its_changes(self, caplog):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        product = self.setup_base_resource(venue=venue_provider.venue, provider=venue_provider.provider)

        with caplog.at_level(logging.INFO):
            response = self.make_request(
                plain_api_key,
                json_body={
                    "offerId": product.id,
                    "name": "Abonnement saison classique",
                    "bookingEmail": "nouvelle-adresse@salle-de-concert.example.com",
                },
            )

        assert response.status_code == 200, response.json
        [update_log] = [
            record for record in caplog.records if getattr(record, "technical_message_id", None) == "offer.updated"
        ]
        assert update_log.extra == {
            "offer_id": product.id,
            "venue_id": product.venueId,
            "product_id": None,
            "changes": {
                "name": {"oldValue": "Abonnement saison jazz", "newValue": "Abonnement saison classique"},
                "bookingEmail": {
                    "oldValue": "notify@salle-de-concert.example.com",
                    "newValue": "nouvelle-adresse@salle-de-concert.example.com",
                },
            },
        }

    @mock.patch("pcapi.core.search.async_index_offer_ids")
    def test_should_change_nothing_when_only_the_offer_id_is_sent(self, mocked_async_index_offer_ids, caplog):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        product = self.setup_base_resource(venue=venue_provider.venue, provider=venue_provider.provider)
        before_update = product.dateUpdated

        with caplog.at_level(logging.INFO):
            response = self.make_request(plain_api_key, json_body={"offerId": product.id})

        assert response.status_code == 200, response.json
        mocked_async_index_offer_ids.assert_not_called()
        assert not has_log(caplog, "offer.updated")

        db.session.refresh(product)
        assert product.dateUpdated == before_update

    @pytest.mark.parametrize(
        "with_existing_stock,partial_body,expected_stock_extra",
        [
            (False, {"name": "Abonnement saison classique"}, {}),
            (False, {"stock": {"price": 1000, "quantity": 1}}, {"stock_price": 1000, "stock_quantity": 1}),
            (True, {"stock": None}, {}),
        ],
        ids=["no stock in the body", "stock sent", "stock deleted"],
    )
    def test_should_log_the_offer_and_stock_details_in_the_api_call_log(
        self, caplog, with_existing_stock, partial_body, expected_stock_extra
    ):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        product = self.setup_base_resource(venue=venue_provider.venue, provider=venue_provider.provider)
        if with_existing_stock:
            offers_factories.StockFactory(offer=product, price=decimal.Decimal("10.00"), quantity=12)

        with caplog.at_level(logging.INFO):
            response = self.make_request(plain_api_key, json_body={"offerId": product.id, **partial_body})

        assert response.status_code == 200, response.json

        db.session.refresh(product)
        test_utils.assert_public_api_data_logs_have_been_recorded(
            caplog,
            self._api_key,
            module="products",
            function="edit_product",
            venue=venue_provider.venueId,
            publication_datetime=product.publicationDatetime,
            # the price is logged in cents, as it was sent
            **expected_stock_extra,
        )

    def test_should_not_issue_more_queries_than_expected(self):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        product = self.setup_base_resource(venue=venue_provider.venue, provider=venue_provider.provider)
        product_id = product.id

        num_queries = 1  # retrieve the API key, joining its provider
        num_queries += 1  # retrieve the product, joining its metadata, product, venue, addresses and provider
        num_queries += 1  # selectinload the stocks
        num_queries += 1  # selectinload the mediations
        num_queries += 1  # selectinload the price categories
        num_queries += 1  # update the offer

        with testing.assert_num_queries(num_queries):
            response = self.make_request(
                plain_api_key, json_body={"offerId": product_id, "name": "Abonnement saison classique"}
            )
            assert response.status_code == 200, response.json


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
class Returns403Test(PatchProductEndpointHelper):
    def test_should_raise_403_because_the_provider_is_inactive(self):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        product = self.setup_base_resource(venue=venue_provider.venue, provider=venue_provider.provider)
        before_update = product.dateUpdated
        venue_provider.provider.isActive = False
        db.session.flush()

        response = self.make_request(
            plain_api_key, json_body={"offerId": product.id, "name": "Abonnement saison classique"}
        )

        assert response.status_code == 403
        assert response.json == {"auth": ["Inactive provider"]}

        db.session.refresh(product)
        assert product.dateUpdated == before_update


@pytest.mark.usefixtures("db_session")
class Returns400Test(PatchProductEndpointHelper):
    # --- Request body schema

    def test_should_raise_400_because_offer_id_is_missing(self):
        plain_api_key, _ = self.setup_active_venue_provider()

        response = self.make_request(plain_api_key, json_body={"name": "Abonnement saison classique"})

        assert response.status_code == 400
        assert response.json == {"offerId": ["field required"]}

    def test_should_raise_400_because_offer_id_is_not_an_integer(self):
        plain_api_key, _ = self.setup_active_venue_provider()

        response = self.make_request(plain_api_key, json_body={"offerId": "not-an-integer"})

        assert response.status_code == 400
        assert response.json == {"offerId": ["value is not a valid integer"]}

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

    @pytest.mark.parametrize("request_field", ["bookingEmail", "bookingContact"])
    def test_should_raise_400_because_an_email_field_is_invalid(self, request_field):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        product = self.setup_base_resource(venue=venue_provider.venue, provider=venue_provider.provider)

        response = self.make_request(plain_api_key, json_body={"offerId": product.id, request_field: "pas-une-adresse"})

        assert response.status_code == 400
        assert response.json == {request_field: ["value is not a valid email address"]}

    @pytest.mark.parametrize(
        "url,expected_error",
        [
            ("https:bloup.com", "invalid or missing URL scheme"),
            (5, "invalid or missing URL scheme"),
            ("", "ensure this value has at least 1 characters"),
        ],
        ids=["missing scheme", "not a string", "empty"],
    )
    def test_should_raise_400_because_external_ticket_office_url_is_invalid(self, url, expected_error):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        product = self.setup_base_resource(venue=venue_provider.venue, provider=venue_provider.provider)

        response = self.make_request(plain_api_key, json_body={"offerId": product.id, "externalTicketOfficeUrl": url})

        assert response.status_code == 400
        assert response.json == {"externalTicketOfficeUrl": [expected_error]}

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

    def test_should_raise_400_because_booking_allowed_datetime_does_not_accept_the_now_literal(self):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        product = self.setup_base_resource(venue=venue_provider.venue, provider=venue_provider.provider)

        response = self.make_request(plain_api_key, json_body={"offerId": product.id, "bookingAllowedDatetime": "now"})

        assert response.status_code == 400
        assert response.json == {"bookingAllowedDatetime": ["invalid datetime format"]}

    # --- `location`

    def test_should_raise_400_because_location_type_is_unknown(self):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        product = self.setup_base_resource(venue=venue_provider.venue, provider=venue_provider.provider)

        response = self.make_request(
            plain_api_key,
            json_body={"offerId": product.id, "location": {"type": "hologram", "venueId": venue_provider.venueId}},
        )

        assert response.status_code == 400
        assert response.json == {
            "location": [
                "No match for discriminator 'type' and value 'hologram' "
                "(allowed values: 'physical', 'digital', 'address')"
            ]
        }

    def test_should_raise_400_because_address_location_address_id_is_not_an_integer(self):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        product = self.setup_base_resource(venue=venue_provider.venue, provider=venue_provider.provider)

        response = self.make_request(
            plain_api_key,
            json_body={
                "offerId": product.id,
                "location": {"type": "address", "venueId": venue_provider.venueId, "addressId": "coucou"},
            },
        )

        assert response.status_code == 400
        assert response.json == {"location.AddressLocation.addressId": ["value is not a valid integer"]}

    @pytest.mark.parametrize(
        "address_label,expected_error",
        [
            ("", "ensure this value has at least 1 characters"),
            ("a" * 201, "ensure this value has at most 200 characters"),
        ],
        ids=["empty", "too long"],
    )
    def test_should_raise_400_because_address_location_label_length_is_out_of_bounds(
        self, address_label, expected_error
    ):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        product = self.setup_base_resource(venue=venue_provider.venue, provider=venue_provider.provider)
        address = geography_factories.AddressFactory(street="6 rue de la Paix")

        response = self.make_request(
            plain_api_key,
            json_body={
                "offerId": product.id,
                "location": {
                    "type": "address",
                    "venueId": venue_provider.venueId,
                    "addressId": address.id,
                    "addressLabel": address_label,
                },
            },
        )

        assert response.status_code == 400
        assert response.json == {"location.AddressLocation.addressLabel": [expected_error]}

    def test_should_raise_400_because_location_has_an_extra_field(self):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        product = self.setup_base_resource(venue=venue_provider.venue, provider=venue_provider.provider)
        address = geography_factories.AddressFactory(street="6 rue de la Paix")

        response = self.make_request(
            plain_api_key,
            json_body={
                "offerId": product.id,
                "location": {
                    "type": "address",
                    "venueId": venue_provider.venueId,
                    "addressId": address.id,
                    "adressLabel": "un seul d",
                },
            },
        )

        assert response.status_code == 400
        assert response.json == {"location.AddressLocation.adressLabel": ["extra fields not permitted"]}

    @pytest.mark.parametrize(
        "location,model",
        [
            ({"type": "physical"}, "PhysicalLocation"),
            ({"type": "digital", "url": "https://salle-de-concert.example.com/en-ligne"}, "DigitalLocation"),
            ({"type": "address", "addressId": 1}, "AddressLocation"),
        ],
        ids=["physical", "digital", "address"],
    )
    def test_should_raise_400_because_location_has_no_venue_id(self, location, model):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        product = self.setup_base_resource(venue=venue_provider.venue, provider=venue_provider.provider)

        response = self.make_request(plain_api_key, json_body={"offerId": product.id, "location": location})

        assert response.status_code == 400
        assert response.json == {f"location.{model}.venueId": ["field required"]}

    # --- Online / offline coherence

    def test_should_raise_400_because_an_online_product_cannot_have_an_address(self):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        product = self.setup_base_resource(
            venue=venue_provider.venue,
            provider=venue_provider.provider,
            subcategoryId=subcategories.LIVRE_NUMERIQUE.id,
            url="https://librairie.example.com/a-la-recherche-du-temps-perdu",
            offererAddress=None,
            extraData={"author": "Marcel Proust"},
        )
        before_update = product.dateUpdated

        response = self.make_request(
            plain_api_key,
            json_body={
                "offerId": product.id,
                "name": "Abonnement saison classique",
                "location": {
                    "type": "digital",
                    "venueId": venue_provider.venueId,
                    "url": "https://librairie.example.com/du-cote-de-chez-swann",
                },
            },
        )

        assert response.status_code == 400
        assert response.json == {"offererAddress": ["Une offre numérique ne peut pas avoir d'adresse"]}

        db.session.refresh(product)
        assert product.name == "Abonnement saison jazz"
        assert product.dateUpdated == before_update

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

    # --- `categoryRelatedFields`

    def test_should_raise_400_because_the_category_cannot_be_changed(self):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        product = self.setup_base_resource(venue=venue_provider.venue, provider=venue_provider.provider)

        response = self.make_request(
            plain_api_key,
            json_body={"offerId": product.id, "categoryRelatedFields": {"category": "ABO_SPECTACLE"}},
        )

        assert response.status_code == 400
        assert response.json == {"categoryRelatedFields.category": ["The category cannot be changed"]}

    @pytest.mark.parametrize("extra_data", [{}, {"musicType": ""}], ids=["missing", "empty"])
    def test_should_raise_400_because_a_mandatory_category_related_field_is_missing(self, extra_data):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        product = self.setup_base_resource(
            venue=venue_provider.venue,
            provider=venue_provider.provider,
            subcategoryId=subcategories.TELECHARGEMENT_MUSIQUE.id,
            url="https://plateforme.example.com/album",
            offererAddress=None,
            extraData=extra_data,
        )

        response = self.make_request(
            plain_api_key,
            json_body={
                "offerId": product.id,
                "categoryRelatedFields": {"category": "TELECHARGEMENT_MUSIQUE", "author": "Miles Davis"},
            },
        )

        assert response.status_code == 400
        assert response.json == {"musicType": ["Ce champ est obligatoire"]}

    def test_should_raise_400_because_the_category_of_a_non_selectable_product_cannot_be_sent(self):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        product = self.setup_base_resource(
            venue=venue_provider.venue,
            provider=venue_provider.provider,
            subcategoryId=subcategories.CAPTATION_MUSIQUE.id,
            extraData={"musicType": "501", "musicSubType": "-1", "gtl_id": "02000000"},
        )

        response = self.make_request(
            plain_api_key,
            json_body={
                "offerId": product.id,
                "categoryRelatedFields": {"category": "CAPTATION_MUSIQUE", "author": "Miles Davis"},
            },
        )

        assert response.status_code == 400
        # every selectable product category is permitted, and the offer's own is not among them
        assert response.json == {
            "categoryRelatedFields.category": [
                f"unexpected value; permitted: '{subcategory.id}'"
                for subcategory in v1_serialization.ALLOWED_PRODUCT_SUBCATEGORIES
                if subcategory.is_selectable
            ]
        }

    def test_should_raise_400_when_sending_category_related_fields_on_a_subcategory_that_requires_an_ean(
        self,
    ):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        product = self.setup_base_resource(
            venue=venue_provider.venue,
            provider=venue_provider.provider,
            subcategoryId=subcategories.SUPPORT_PHYSIQUE_FILM.id,
            ean="9782070100002",
            extraData=None,
        )
        # the offer does have an ean: it is the request that cannot carry one
        assert product.ean == "9782070100002"

        response = self.make_request(
            plain_api_key,
            json_body={
                "offerId": product.id,
                "categoryRelatedFields": {"category": "SUPPORT_PHYSIQUE_FILM", "ean": "9782070100002"},
            },
        )

        assert response.status_code == 400
        assert response.json == {"ean": ["Ce champ est obligatoire"]}

    # --- `stock`

    def test_should_raise_400_because_stock_has_an_extra_field(self):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        product = self.setup_base_resource(venue=venue_provider.venue, provider=venue_provider.provider)

        response = self.make_request(
            plain_api_key,
            json_body={"offerId": product.id, "stock": {"price": 1000, "quantity": 1, "priceCategoryId": 3}},
        )

        assert response.status_code == 400
        assert response.json == {"stock.priceCategoryId": ["extra fields not permitted"]}

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

    @time_machine.travel(FROZEN_NOW, tick=False)
    @pytest.mark.parametrize(
        "offer_datetime_field,expected_error",
        [
            (
                "publicationDatetime",
                "the stock will not be published before its `bookingLimitDatetime`. Either change "
                "`bookingLimitDatetime` to a later date, or update the offer `publicationDatetime`",
            ),
            (
                "bookingAllowedDatetime",
                "the stock will not be bookable before its `bookingLimitDatetime`. Either change "
                "`bookingLimitDatetime` to a later date, or update the offer `bookingAllowedDatetime`",
            ),
        ],
        ids=["published after", "bookable after"],
    )
    def test_should_raise_400_because_the_stock_would_close_before_the_product_opens(
        self, offer_datetime_field, expected_error
    ):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        product = self.setup_base_resource(
            venue=venue_provider.venue,
            provider=venue_provider.provider,
            **{offer_datetime_field: datetime.datetime(2026, 12, 1, 0, 0)},
        )

        response = self.make_request(
            plain_api_key,
            json_body={
                "offerId": product.id,
                "stock": {"price": 1000, "quantity": 1, "bookingLimitDatetime": "2026-09-01T00:00:00+00:00"},
            },
        )

        assert response.status_code == 400
        assert response.json == {"bookingLimitDatetime": [expected_error]}

    @pytest.mark.parametrize("stock_body", [{}, {"quantity": 1}], ids=["empty object", "quantity only"])
    def test_should_raise_400_because_stock_price_is_missing_when_creating_a_stock(self, stock_body):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        product = self.setup_base_resource(venue=venue_provider.venue, provider=venue_provider.provider)
        before_update = product.dateUpdated
        assert not product.activeStocks

        response = self.make_request(
            plain_api_key,
            json_body={"offerId": product.id, "name": "Abonnement saison classique", "stock": stock_body},
        )

        assert response.status_code == 400
        assert response.json == {"stock.price": ["Required"]}

        db.session.refresh(product)
        assert product.name == "Abonnement saison jazz"
        assert product.dateUpdated == before_update
        assert not product.activeStocks

    def test_should_raise_400_because_a_stock_cannot_be_created_on_a_product_synchronized_by_another_provider(
        self,
    ):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        product = self.setup_base_resource(venue=venue_provider.venue, provider=providers_factories.ProviderFactory())

        response = self.make_request(
            plain_api_key, json_body={"offerId": product.id, "stock": {"price": 1000, "quantity": 1}}
        )

        assert response.status_code == 400
        assert response.json == {"global": ["Les offres importées ne sont pas modifiables"]}

    @pytest.mark.parametrize("stock_body", [{"price": 2000}, {"quantity": 20}], ids=["price", "quantity only"])
    def test_should_raise_400_because_a_stock_cannot_be_edited_on_a_product_synchronized_by_another_provider(
        self, stock_body
    ):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        product = self.setup_base_resource(venue=venue_provider.venue, provider=providers_factories.ProviderFactory())
        stock = offers_factories.StockFactory(offer=product, price=decimal.Decimal("10.00"), quantity=12)

        response = self.make_request(plain_api_key, json_body={"offerId": product.id, "stock": stock_body})

        assert response.status_code == 400
        assert response.json == {"global": ["Les offres importées ne sont pas modifiables"]}

        db.session.refresh(product)
        assert stock.price == decimal.Decimal("10.00")
        assert stock.quantity == 12

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

    def test_should_raise_400_because_name_is_null(self):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        product = self.setup_base_resource(venue=venue_provider.venue, provider=venue_provider.provider)

        response = self.make_request(plain_api_key, json_body={"offerId": product.id, "name": None})

        assert response.status_code == 400
        assert response.json == {"name": ["cannot be null"]}

    def test_should_raise_400_because_name_contains_an_ean(self):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        product = self.setup_base_resource(venue=venue_provider.venue, provider=venue_provider.provider)

        response = self.make_request(
            plain_api_key,
            json_body={"offerId": product.id, "name": "Abonnement saison jazz - 9782070286256"},
        )

        assert response.status_code == 400
        assert response.json == {"name": ["Le titre d'une offre ne peut contenir l'EAN"]}

    # --- `accessibility`

    def test_should_raise_400_because_an_accessibility_field_is_null(self):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        product = self.setup_base_resource(venue=venue_provider.venue, provider=venue_provider.provider)

        response = self.make_request(
            plain_api_key,
            json_body={"offerId": product.id, "accessibility": {"audioDisabilityCompliant": None}},
        )

        assert response.status_code == 400
        assert response.json == {"global": ["L’accessibilité de l’offre doit être définie"]}

    # --- `enableDoubleBookings`

    def test_should_raise_400_because_the_category_does_not_allow_double_bookings(self):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        product = self.setup_base_resource(venue=venue_provider.venue, provider=venue_provider.provider)
        assert not subcategories.ABO_CONCERT.can_be_duo

        response = self.make_request(plain_api_key, json_body={"offerId": product.id, "enableDoubleBookings": True})

        assert response.status_code == 400
        assert response.json == {"enableDoubleBookings": ["the category chosen does not allow double bookings"]}

    # --- `idAtProvider`

    def test_should_raise_400_because_id_at_provider_is_already_taken_by_another_offer_of_the_venue(self):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        product = self.setup_base_resource(venue=venue_provider.venue, provider=venue_provider.provider)
        id_at_provider = "abonnement-jazz-2026"
        offers_factories.OfferFactory(venue=venue_provider.venue, idAtProvider=id_at_provider)

        response = self.make_request(plain_api_key, json_body={"offerId": product.id, "idAtProvider": id_at_provider})

        assert response.status_code == 400
        assert response.json == {"idAtProvider": [f"`{id_at_provider}` is already taken by another venue offer"]}

    def test_should_raise_400_because_id_at_provider_is_set_on_a_product_without_provider(self):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        product = self.setup_base_resource(venue=venue_provider.venue, provider=None)
        assert product.lastProvider is None

        response = self.make_request(
            plain_api_key, json_body={"offerId": product.id, "idAtProvider": "abonnement-jazz-2026"}
        )

        assert response.status_code == 400
        assert response.json == {
            "idAtProvider": ["Une offre ne peut être créée ou éditée avec un idAtProvider si elle n'a pas de provider"]
        }

    # --- Offer validation status

    @pytest.mark.parametrize(
        "validation_status",
        [offers_models.OfferValidationStatus.PENDING, offers_models.OfferValidationStatus.REJECTED],
        ids=["pending", "rejected"],
    )
    def test_should_raise_400_because_the_product_is_pending_or_rejected(self, validation_status):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        product = self.setup_base_resource(
            venue=venue_provider.venue, provider=venue_provider.provider, validation=validation_status
        )

        response = self.make_request(
            plain_api_key, json_body={"offerId": product.id, "name": "Abonnement saison classique"}
        )

        assert response.status_code == 400
        assert response.json == {"global": ["Les offres refusées ou en attente de validation ne sont pas modifiables"]}

    # --- Fields locked by the provider

    def test_should_raise_400_because_the_item_collection_details_cannot_be_changed_on_a_synchronized_product(
        self,
    ):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        product = self.setup_base_resource(venue=venue_provider.venue, provider=providers_factories.ProviderFactory())

        response = self.make_request(
            plain_api_key,
            json_body={"offerId": product.id, "itemCollectionDetails": "À retirer au vestiaire"},
        )

        assert response.status_code == 400
        assert response.json == {"withdrawalDetails": ["Vous ne pouvez pas modifier ce champ"]}

    def test_should_list_every_rejected_field_when_several_are_not_editable(self):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        product = self.setup_base_resource(venue=venue_provider.venue, provider=providers_factories.ProviderFactory())
        before_update = product.dateUpdated

        response = self.make_request(
            plain_api_key,
            json_body={
                "offerId": product.id,
                "itemCollectionDetails": "À retirer au vestiaire",
                "bookingEmail": "nouvelle-adresse@salle-de-concert.example.com",
                # allowed for this provider, and still not applied
                "name": "Abonnement saison classique",
            },
        )

        assert response.status_code == 400
        assert response.json == {
            "withdrawalDetails": ["Vous ne pouvez pas modifier ce champ"],
            "bookingEmail": ["Vous ne pouvez pas modifier ce champ"],
        }

        db.session.refresh(product)
        assert product.name == "Abonnement saison jazz"
        assert product.dateUpdated == before_update


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

    def test_should_raise_404_because_offer_is_an_event(self):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        event_offer = offers_factories.EventOfferFactory(
            venue=venue_provider.venue, lastProvider=venue_provider.provider
        )

        response = self.make_request(
            plain_api_key, json_body={"offerId": event_offer.id, "name": "Abonnement saison classique"}
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

    def test_should_raise_404_because_product_belongs_to_another_provider(self):
        plain_api_key, _ = self.setup_active_venue_provider()
        other_venue_provider = providers_factories.VenueProviderFactory()
        product = self.setup_base_resource(venue=other_venue_provider.venue, provider=other_venue_provider.provider)

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

    def test_should_raise_404_because_venue_provider_of_venue_in_location_is_inactive(self):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        product = self.setup_base_resource(venue=venue_provider.venue, provider=venue_provider.provider)
        inactive_link = providers_factories.VenueProviderFactory(provider=venue_provider.provider, isActive=False)

        response = self.make_request(
            plain_api_key,
            json_body={"offerId": product.id, "location": {"type": "physical", "venueId": inactive_link.venue.id}},
        )

        assert response.status_code == 404
        assert response.json == self.VENUE_NOT_FOUND

    def test_should_raise_404_because_address_in_location_does_not_exist(self):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        venue = venue_provider.venue
        product = self.setup_base_resource(venue=venue, provider=venue_provider.provider)
        unknown_address_id = geography_factories.AddressFactory(street="6 rue de la Paix").id + 1
        before_update = product.dateUpdated

        response = self.make_request(
            plain_api_key,
            json_body={
                "offerId": product.id,
                "location": {"type": "address", "venueId": venue.id, "addressId": unknown_address_id},
            },
        )

        assert response.status_code == 404
        assert response.json == {
            "location.AddressLocation.addressId": [f"There is no address with id {unknown_address_id}"]
        }

        db.session.refresh(product)
        assert product.dateUpdated == before_update
