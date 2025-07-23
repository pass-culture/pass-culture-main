import base64
import decimal
import logging
import pathlib
from datetime import datetime
from datetime import timedelta
from datetime import timezone

import pytest
import time_machine

from pcapi import settings
from pcapi.core.geography import factories as geography_factories
from pcapi.core.offerers import factories as offerers_factories
from pcapi.core.offerers import models as offerers_models
from pcapi.core.offers import factories as offers_factories
from pcapi.core.offers import models as offers_models
from pcapi.models import db
from pcapi.models import offer_mixin
from pcapi.utils import date as date_utils
from pcapi.utils import human_ids

import tests
from tests.routes import image_data
from tests.routes.public.helpers import PublicAPIVenueEndpointHelper


ACCESSIBILITY_FIELDS = {
    "audioDisabilityCompliant": True,
    "mentalDisabilityCompliant": True,
    "motorDisabilityCompliant": True,
    "visualDisabilityCompliant": True,
}

now_datetime_with_tz = datetime.now(timezone.utc)


@pytest.mark.usefixtures("db_session")
class PostEventTest(PublicAPIVenueEndpointHelper):
    endpoint_url = "/public/offers/v1/events"
    endpoint_method = "post"

    @staticmethod
    def _get_base_payload(venue_id: int) -> dict:
        return {
            "categoryRelatedFields": {"category": "RENCONTRE"},
            "accessibility": ACCESSIBILITY_FIELDS,
            "location": {"type": "physical", "venueId": venue_id},
            "name": "Le champ des possibles",
            "hasTicket": False,
        }

    def test_should_raise_404_because_has_no_access_to_venue(self):
        plain_api_key, _ = self.setup_provider()
        venue = self.setup_venue()

        response = self.make_request(plain_api_key, json_body=self._get_base_payload(venue_id=venue.id))
        assert response.status_code == 404

    def test_should_raise_404_because_venue_provider_is_inactive(self):
        plain_api_key, venue_provider = self.setup_inactive_venue_provider()
        response = self.make_request(plain_api_key, json_body=self._get_base_payload(venue_id=venue_provider.venue.id))

        assert response.status_code == 404

    @time_machine.travel(now_datetime_with_tz, tick=False)
    def test_event_minimal_body(self):
        plain_api_key, venue_provider = self.setup_active_venue_provider()

        response = self.make_request(plain_api_key, json_body=self._get_base_payload(venue_id=venue_provider.venue.id))

        assert response.status_code == 200
        created_offer = db.session.query(offers_models.Offer).one()
        assert created_offer.name == "Le champ des possibles"
        assert created_offer.venue == venue_provider.venue
        assert created_offer.subcategoryId == "RENCONTRE"
        assert created_offer.audioDisabilityCompliant is True
        assert created_offer.lastProvider.name == venue_provider.provider.name
        assert created_offer.mentalDisabilityCompliant is True
        assert created_offer.motorDisabilityCompliant is True
        assert created_offer.visualDisabilityCompliant is True
        assert created_offer.isDuo
        assert created_offer.extraData == {}
        assert created_offer.bookingEmail is None

        assert created_offer.description is None
        assert created_offer.publicationDatetime == now_datetime_with_tz.replace(second=0, microsecond=0, tzinfo=None)
        assert created_offer.finalizationDatetime == now_datetime_with_tz.replace(tzinfo=None)
        assert not created_offer.bookingAllowedDatetime
        assert created_offer.status == offer_mixin.OfferStatus.DRAFT
        assert created_offer.withdrawalDetails is None
        assert created_offer.withdrawalType is None
        assert created_offer.withdrawalDelay is None

    def test_event_with_deprecated_music_type_triggers_warning_log(self, caplog):
        # TODO(jbaudet-pass): remove test once the deprecated enum
        # music type is not allowed anymore
        plain_api_key, venue_provider = self.setup_active_venue_provider()

        payload = self._get_base_payload(venue_provider.venueId)
        payload["categoryRelatedFields"] = {"category": "CONCERT", "musicType": "METAL-DOOM_METAL"}
        payload["bookingContact"] = "booking@test.com"

        with caplog.at_level(logging.INFO):
            response = self.make_request(plain_api_key, json_body=payload)

        assert response.status_code == 200
        assert next(rec for rec in caplog.records if rec.msg == "offer: using old music type")

    def test_event_with_new_and_expected_music_type_does_not_trigger_warning_log(self, caplog):
        # TODO(jbaudet-pass): remove test once the deprecated enum
        # music type is not allowed anymore
        plain_api_key, venue_provider = self.setup_active_venue_provider()

        payload = self._get_base_payload(venue_provider.venueId)
        payload["categoryRelatedFields"] = {"category": "CONCERT", "musicType": "METAL"}
        payload["bookingContact"] = "booking@test.com"

        with caplog.at_level(logging.INFO):
            response = self.make_request(plain_api_key, json_body=payload)

        assert response.status_code == 200
        assert not [rec for rec in caplog.records if rec.msg == "offer: using old music type"]

    @time_machine.travel(now_datetime_with_tz, tick=False)
    def test_future_event(self):
        plain_api_key, venue_provider = self.setup_active_venue_provider()

        payload = self._get_base_payload(venue_provider.venueId)
        publication_date = datetime.utcnow().replace(minute=0, second=0) + timedelta(days=30)
        payload["publicationDate"] = publication_date.isoformat()
        response = self.make_request(plain_api_key, json_body=payload)

        assert response.status_code == 200
        created_offer = db.session.query(offers_models.Offer).one()

        assert created_offer.publicationDatetime == date_utils.local_datetime_to_default_timezone(
            publication_date, "Europe/Paris"
        ).replace(microsecond=0, tzinfo=None)
        assert created_offer.finalizationDatetime == now_datetime_with_tz.replace(tzinfo=None)
        assert not created_offer.bookingAllowedDatetime

    @time_machine.travel(datetime(2025, 6, 26, tzinfo=timezone.utc), tick=False)
    @pytest.mark.parametrize(
        "request_publication_date,address_tz,expected_publication_date,response_publication_date",
        [
            # request publication date has tz
            (
                "2025-06-26T14:30:00+02:00",
                "Europe/Paris",
                datetime(2025, 6, 26, 12, 30, tzinfo=None),
                "2025-06-26T12:30:00Z",
            ),
            (
                "2025-06-26T14:30:00Z",
                "America/Cayenne",
                datetime(2025, 6, 26, 14, 30, tzinfo=None),
                "2025-06-26T14:30:00Z",
            ),
            # request publication date does NOT have tz
            (
                "2025-06-26T14:30:00",
                "America/Cayenne",
                datetime(2025, 6, 26, 17, 30, tzinfo=None),
                "2025-06-26T17:30:00Z",
            ),
        ],
    )
    def test_publication_date_with_and_without_tz(
        self, request_publication_date, address_tz, expected_publication_date, response_publication_date
    ):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        venue_provider.venue.offererAddress.address.timezone = address_tz

        payload = self._get_base_payload(venue_provider.venueId)
        payload["publicationDate"] = request_publication_date
        response = self.make_request(plain_api_key, json_body=payload)

        assert response.status_code == 200
        assert response.json["publicationDatetime"] == response_publication_date
        created_offer = db.session.query(offers_models.Offer).one()

        assert created_offer.publicationDatetime == expected_publication_date
        assert created_offer.finalizationDatetime == datetime(2025, 6, 26)

        assert not created_offer.bookingAllowedDatetime

    @time_machine.travel(datetime(2025, 6, 25, 12, 30, tzinfo=timezone.utc), tick=False)
    @pytest.mark.parametrize(
        "partial_request_json,expected_publication_datetime,expected_response_publication_datetime",
        [
            (
                {"publicationDatetime": "2025-08-01T08:00:00+02:00"},  # tz: Europe/Paris
                datetime(2025, 8, 1, 6),  # tz: utc
                "2025-08-01T06:00:00Z",
            ),
            (
                {"publicationDatetime": "now"},
                datetime(2025, 6, 25, 12, 30),
                "2025-06-25T12:30:00Z",
            ),
            # should default to now
            ({}, datetime(2025, 6, 25, 12, 30), "2025-06-25T12:30:00Z"),
            # draft
            ({"publicationDatetime": None}, None, None),
        ],
    )
    def test_publication_datetime_param(
        self, partial_request_json, expected_publication_datetime, expected_response_publication_datetime
    ):
        plain_api_key, venue_provider = self.setup_active_venue_provider()

        payload = self._get_base_payload(venue_provider.venueId)
        payload.update(**partial_request_json)

        response = self.make_request(plain_api_key, json_body=payload)

        assert response.status_code == 200
        assert response.json["publicationDatetime"] == expected_response_publication_datetime

        created_offer = db.session.query(offers_models.Offer).one()
        assert created_offer.publicationDatetime == expected_publication_datetime

    @time_machine.travel(datetime(2025, 6, 25, 12, 30, tzinfo=timezone.utc), tick=False)
    @pytest.mark.parametrize(
        "partial_request_json,expected_booking_allowed_datetime,expected_response_booking_allowed_datetime",
        [
            (
                {"bookingAllowedDatetime": "2025-08-01T08:00:00+02:00"},  # tz: Europe/Paris
                datetime(2025, 8, 1, 6),  # tz: utc
                "2025-08-01T06:00:00Z",
            ),
            ({"bookingAllowedDatetime": None}, None, None),
            # should default to `None``
            ({}, None, None),
        ],
    )
    def test_booking_allowed_datetime_param(
        self,
        partial_request_json,
        expected_booking_allowed_datetime,
        expected_response_booking_allowed_datetime,
    ):
        plain_api_key, venue_provider = self.setup_active_venue_provider()

        payload = self._get_base_payload(venue_provider.venueId)
        payload.update(**partial_request_json)

        response = self.make_request(plain_api_key, json_body=payload)

        assert response.status_code == 200
        assert response.json["bookingAllowedDatetime"] == expected_response_booking_allowed_datetime

        created_offer = db.session.query(offers_models.Offer).one()
        assert created_offer.bookingAllowedDatetime == expected_booking_allowed_datetime

    @time_machine.travel(datetime(2025, 6, 25, 12, 30, tzinfo=timezone.utc), tick=False)
    def test_event_creation_with_full_body(self, clear_tests_assets_bucket):
        plain_api_key, venue_provider = self.setup_active_venue_provider()

        payload = {
            "enableDoubleBookings": True,
            "bookingContact": "contact@example.com",
            "bookingEmail": "nicoj@example.com",
            "categoryRelatedFields": {
                "author": "Ray Charles",
                "category": "CONCERT",
                "musicType": "ELECTRO-HOUSE",
                "performer": "Nicolas Jaar",
                "stageDirector": "Alfred",  # field not applicable
            },
            "description": "Space is only noise if you can see",
            "eventDuration": 120,
            "accessibility": {
                "audioDisabilityCompliant": False,
                "mentalDisabilityCompliant": True,
                "motorDisabilityCompliant": True,
                "visualDisabilityCompliant": True,
            },
            "externalTicketOfficeUrl": "https://maposaic.com",
            "image": {
                "credit": "Jean-Crédit Photo",
                "file": image_data.GOOD_IMAGE,
            },
            "itemCollectionDetails": "A retirer au 6ème sous-sol du parking de la gare entre minuit et 2",
            "location": {"type": "physical", "venueId": venue_provider.venueId},
            "name": "Nicolas Jaar dans ton salon",
            "priceCategories": [{"price": 30000, "label": "triangle or", "idAtProvider": "gold_triangle"}],
            "hasTicket": True,
            "idAtProvider": "T'as un bel id tu sais",
        }

        response = self.make_request(plain_api_key, json_body=payload)

        assert response.status_code == 200
        created_offer = db.session.query(offers_models.Offer).one()
        assert created_offer.lastProvider.name == venue_provider.provider.name
        assert created_offer.name == "Nicolas Jaar dans ton salon"
        assert created_offer.venue == venue_provider.venue
        assert created_offer.subcategoryId == "CONCERT"
        assert created_offer.audioDisabilityCompliant is False
        assert created_offer.mentalDisabilityCompliant is True
        assert created_offer.motorDisabilityCompliant is True
        assert created_offer.visualDisabilityCompliant is True
        assert created_offer.isDuo is True
        assert created_offer.extraData == {
            "author": "Ray Charles",
            "musicType": "880",
            "musicSubType": "894",
            "gtl_id": "04000000",
            "performer": "Nicolas Jaar",
        }
        assert created_offer.bookingEmail == "nicoj@example.com"

        assert created_offer.finalizationDatetime == datetime(2025, 6, 25, 12, 30)
        assert created_offer.publicationDatetime == datetime(2025, 6, 25, 12, 30)

        assert not created_offer.bookingAllowedDatetime
        assert created_offer.description == "Space is only noise if you can see"
        assert created_offer.externalTicketOfficeUrl == "https://maposaic.com"
        assert created_offer.status == offer_mixin.OfferStatus.DRAFT
        assert created_offer.withdrawalDetails == "A retirer au 6ème sous-sol du parking de la gare entre minuit et 2"
        assert created_offer.withdrawalType == offers_models.WithdrawalTypeEnum.IN_APP
        assert created_offer.withdrawalDelay == None
        assert created_offer.idAtProvider == "T'as un bel id tu sais"

        created_mediation = db.session.query(offers_models.Mediation).one()
        assert created_mediation.offer == created_offer
        assert created_offer.image.url == created_mediation.thumbUrl
        assert (
            created_offer.image.url
            == f"{settings.OBJECT_STORAGE_URL}/thumbs/mediations/{human_ids.humanize(created_mediation.id)}"
        )

        created_price_category = db.session.query(offers_models.PriceCategory).one()
        assert created_price_category.price == decimal.Decimal("300")
        assert created_price_category.label == "triangle or"
        assert created_price_category.idAtProvider == "gold_triangle"

        assert response.json == {
            "bookingAllowedDatetime": None,
            "publicationDatetime": "2025-06-25T12:30:00Z",
            "accessibility": {
                "audioDisabilityCompliant": False,
                "mentalDisabilityCompliant": True,
                "motorDisabilityCompliant": True,
                "visualDisabilityCompliant": True,
            },
            "bookingContact": "contact@example.com",
            "bookingEmail": "nicoj@example.com",
            "categoryRelatedFields": {
                "author": "Ray Charles",
                "category": "CONCERT",
                "musicType": "ELECTRO-HOUSE",
                "performer": "Nicolas Jaar",
            },
            "description": "Space is only noise if you can see",
            "enableDoubleBookings": True,
            "eventDuration": 120,
            "externalTicketOfficeUrl": "https://maposaic.com",
            "id": created_offer.id,
            "idAtProvider": "T'as un bel id tu sais",
            "image": {
                "credit": "Jean-Crédit Photo",
                "url": f"http://localhost/storage/thumbs/mediations/{human_ids.humanize(created_mediation.id)}",
            },
            "itemCollectionDetails": "A retirer au 6ème sous-sol du parking de la gare entre minuit et 2",
            "location": {"type": "physical", "venueId": venue_provider.venueId},
            "name": "Nicolas Jaar dans ton salon",
            "status": "DRAFT",
            "priceCategories": [
                {
                    "id": created_price_category.id,
                    "price": 30000,
                    "label": "triangle or",
                    "idAtProvider": "gold_triangle",
                }
            ],
            "hasTicket": True,
        }

    def test_event_creation_with_titelive_type(self, clear_tests_assets_bucket):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        payload = {
            "bookingContact": "contact@example.com",
            "categoryRelatedFields": {
                "author": "Ray Charles",
                "category": "CONCERT",
                "musicType": "MUSIQUE_CLASSIQUE",
                "performer": "Nicolas Jaar",
            },
            "accessibility": {
                "audioDisabilityCompliant": False,
                "mentalDisabilityCompliant": True,
                "motorDisabilityCompliant": True,
                "visualDisabilityCompliant": True,
            },
            "location": {"type": "physical", "venueId": venue_provider.venueId},
            "name": "Nicolas Jaar dans ton salon",
            "priceCategories": [{"price": 0, "label": "triangle or"}],
            "hasTicket": False,
        }
        response = self.make_request(plain_api_key, json_body=payload)

        assert response.status_code == 200
        created_offer = db.session.query(offers_models.Offer).one()
        assert created_offer.subcategoryId == "CONCERT"
        assert created_offer.extraData == {
            "author": "Ray Charles",
            "gtl_id": "01000000",
            "musicType": "600",
            "musicSubType": "-1",
            "performer": "Nicolas Jaar",
        }
        assert response.json["categoryRelatedFields"] == {
            "author": "Ray Charles",
            "category": "CONCERT",
            "musicType": "MUSIQUE_CLASSIQUE",
            "performer": "Nicolas Jaar",
        }

    def test_event_creation_with_titelive_type_with_active_serialization(self, clear_tests_assets_bucket):
        plain_api_key, venue_provider = self.setup_active_venue_provider()

        payload = {
            "bookingContact": "contact@example.com",
            "bookingEmail": "nicoj@example.com",
            "categoryRelatedFields": {
                "author": "Ray Charles",
                "category": "CONCERT",
                "musicType": "JAZZ-BLUES",
                "performer": "Nicolas Jaar",
                "stageDirector": "Alfred",  # field not applicable
            },
            "eventDuration": 120,
            "accessibility": {
                "audioDisabilityCompliant": False,
                "mentalDisabilityCompliant": True,
                "motorDisabilityCompliant": True,
                "visualDisabilityCompliant": True,
            },
            "externalTicketOfficeUrl": "https://maposaic.com",
            "itemCollectionDetails": "A retirer au 6ème sous-sol du parking de la gare entre minuit et 2",
            "location": {"type": "physical", "venueId": venue_provider.venueId},
            "name": "Nicolas Jaar dans ton salon",
            "priceCategories": [{"price": 30000, "label": "triangle or"}],
            "hasTicket": True,
        }
        response = self.make_request(plain_api_key, json_body=payload)

        assert response.status_code == 200
        created_offer = db.session.query(offers_models.Offer).one()
        assert created_offer.subcategoryId == "CONCERT"
        assert created_offer.extraData == {
            "author": "Ray Charles",
            "gtl_id": "02000000",
            "musicType": "501",
            "musicSubType": "-1",
            "performer": "Nicolas Jaar",
        }
        assert created_offer.externalTicketOfficeUrl == "https://maposaic.com"
        assert created_offer.withdrawalDetails == "A retirer au 6ème sous-sol du parking de la gare entre minuit et 2"
        assert created_offer.withdrawalType == offers_models.WithdrawalTypeEnum.IN_APP

        assert response.json["categoryRelatedFields"] == {
            "author": "Ray Charles",
            "category": "CONCERT",
            "musicType": "JAZZ-BLUES",
            "performer": "Nicolas Jaar",
        }

    @pytest.mark.usefixtures("db_session")
    def test_other_music_type_serialization(self):
        plain_api_key, venue_provider = self.setup_active_venue_provider()

        payload = {
            "categoryRelatedFields": {"category": "CONCERT", "musicType": "OTHER"},
            "accessibility": ACCESSIBILITY_FIELDS,
            "location": {"type": "physical", "venueId": venue_provider.venueId},
            "name": "Le champ des possibles",
            "hasTicket": False,
            "bookingContact": "booking@conta.ct",
        }

        response = self.make_request(plain_api_key, json_body=payload)

        assert response.status_code == 200
        created_offer = db.session.query(offers_models.Offer).one()
        assert created_offer.extraData == {"musicType": "-1", "musicSubType": "-1", "gtl_id": "19000000"}

        assert response.json["categoryRelatedFields"] == {
            "author": None,
            "category": "CONCERT",
            "musicType": "AUTRES",  # The music type is inferred from gtl_id
            "performer": None,
        }

    def test_event_with_custom_address(self):
        plain_api_key, venue_provider = self.setup_active_venue_provider(provider_has_ticketing_urls=False)
        payload = self._get_base_payload(venue_provider.venueId)
        address = geography_factories.AddressFactory()
        offerer_address = offerers_factories.OffererAddressFactory(
            address=address,
            offerer=venue_provider.venue.managingOfferer,
            label="My beautiful address no one knows about",
        )
        payload["location"] = {
            "type": "address",
            "venueId": venue_provider.venueId,
            "addressId": address.id,
            "addressLabel": "My beautiful address no one knows about",
        }

        response = self.make_request(plain_api_key, json_body=payload)
        assert response.status_code == 200
        assert response.json["location"]["addressId"] == address.id
        assert response.json["location"]["addressLabel"] == "My beautiful address no one knows about"
        created_offer = db.session.query(offers_models.Offer).one()
        assert created_offer.offererAddress == offerer_address

    def test_event_with_custom_address_should_create_offerer_address(self):
        plain_api_key, venue_provider = self.setup_active_venue_provider(provider_has_ticketing_urls=False)
        payload = self._get_base_payload(venue_provider.venueId)
        address = geography_factories.AddressFactory()

        assert (
            not db.session.query(offerers_models.OffererAddress)
            .filter(
                offerers_models.OffererAddress.addressId == address.id,
                offerers_models.OffererAddress.label == "My beautiful address no one knows about",
            )
            .one_or_none()
        )

        payload["location"] = {
            "type": "address",
            "venueId": venue_provider.venueId,
            "addressId": address.id,
            "addressLabel": "My beautiful address no one knows about",
        }
        response = self.make_request(plain_api_key, json_body=payload)
        assert response.status_code == 200
        created_offer = db.session.query(offers_models.Offer).one()
        offerer_address = (
            db.session.query(offerers_models.OffererAddress)
            .filter(
                offerers_models.OffererAddress.addressId == address.id,
                offerers_models.OffererAddress.label == "My beautiful address no one knows about",
            )
            .one()
        )
        assert created_offer.offererAddress == offerer_address

    def test_event_with_custom_address_should_raiser_404_because_address_does_not_exist(self):
        plain_api_key, venue_provider = self.setup_active_venue_provider(provider_has_ticketing_urls=False)
        payload = self._get_base_payload(venue_provider.venueId)
        address = geography_factories.AddressFactory()
        not_existing_address_id = address.id + 1

        payload["location"] = {
            "type": "address",
            "venueId": venue_provider.venueId,
            "addressId": not_existing_address_id,
        }
        response = self.make_request(plain_api_key, json_body=payload)
        assert response.status_code == 404
        assert response.json == {
            "location.AddressLocation.addressId": [f"There is no address with id {not_existing_address_id}"]
        }

    def test_event_without_ticket(self):
        plain_api_key, venue_provider = self.setup_active_venue_provider(provider_has_ticketing_urls=False)

        payload = {
            "categoryRelatedFields": {"category": "FESTIVAL_ART_VISUEL"},
            "accessibility": ACCESSIBILITY_FIELDS,
            "location": {"type": "physical", "venueId": venue_provider.venueId},
            "name": "Le champ des possibles",
            "hasTicket": False,
            "bookingContact": "booking@conta.ct",
        }

        response = self.make_request(plain_api_key, json_body=payload)

        assert response.status_code == 200
        created_offer = db.session.query(offers_models.Offer).one()
        assert created_offer.withdrawalType == offers_models.WithdrawalTypeEnum.NO_TICKET

    def test_event_with_has_ticket_to_true_and_ticketing_service_at_provider_level(self):
        plain_api_key, venue_provider = self.setup_active_venue_provider()

        payload = {
            "categoryRelatedFields": {"category": "FESTIVAL_ART_VISUEL"},
            "accessibility": ACCESSIBILITY_FIELDS,
            "location": {"type": "physical", "venueId": venue_provider.venueId},
            "name": "Le champ des possibles",
            "hasTicket": True,
            "bookingContact": "booking@conta.ct",
        }

        response = self.make_request(plain_api_key, json_body=payload)
        assert response.status_code == 200
        created_offer = db.session.query(offers_models.Offer).one()
        assert created_offer.withdrawalType == offers_models.WithdrawalTypeEnum.IN_APP

    def test_event_with_has_ticket_to_true_and_ticketing_service_at_venue_level(self):
        plain_api_key, venue_provider = self.setup_active_venue_provider()

        payload = {
            "categoryRelatedFields": {"category": "FESTIVAL_ART_VISUEL"},
            "accessibility": ACCESSIBILITY_FIELDS,
            "location": {"type": "physical", "venueId": venue_provider.venueId},
            "name": "Le champ des possibles",
            "hasTicket": True,
            "bookingContact": "booking@conta.ct",
        }

        response = self.make_request(plain_api_key, json_body=payload)

        assert response.status_code == 200
        created_offer = db.session.query(offers_models.Offer).one()
        assert created_offer.withdrawalType == offers_models.WithdrawalTypeEnum.IN_APP

    @pytest.mark.parametrize(
        "partial_request_json, expected_response_json",
        [
            # errors on name
            (
                {"name": "Le Visible et l'invisible - Suivi de notes de travail - 9782070286256"},
                {"name": ["Le titre d'une offre ne peut contenir l'EAN"]},
            ),
            (
                {"name": "Jean Tartine est de retour", "description": "A" * 10_001},
                {"description": ["ensure this value has at most 10000 characters"]},
            ),
            ({"name": None}, {"name": ["none is not an allowed value"]}),
            # errors on datetimes
            (
                {"bookingAllowedDatetime": "2021-01-01T00:00:00"},
                {"bookingAllowedDatetime": ["The datetime must be timezone-aware."]},
            ),
            (
                {"bookingAllowedDatetime": "2021-01-01T00:00:00+00:00"},
                {"bookingAllowedDatetime": ["The datetime must be in the future."]},
            ),
            (
                {"publicationDatetime": "2021-01-01T00:00:00"},
                {"publicationDatetime": ["The datetime must be timezone-aware."]},
            ),
            (
                {"publicationDatetime": "2021-01-01T00:00:00+00:00"},
                {"publicationDatetime": ["The datetime must be in the future."]},
            ),
            (
                {"publicationDatetime": "NOW"},
                {"publicationDatetime": ["invalid datetime format", "unexpected value; permitted: 'now'"]},
            ),
            # `publicationDate` & `publicationDatetime` are both set
            (
                {
                    "publicationDatetime": "2021-01-01T00:00:00+00:00",
                    "publicationDate": "2021-01-01T00:00:00+00:00",
                },
                {
                    "__root__": [
                        "You cannot set both `publicationDate` and `publicationDatetime`. `publicationDate` is deprecated, please only use `publicationDatetime`."
                    ]
                },
            ),
            # errors on idAtProvider
            (
                {"idAtProvider": "a" * 71},
                {"idAtProvider": ["ensure this value has at most 70 characters"]},
            ),
            (
                {"idAtProvider": "c'est déjà pris :'("},
                {"idAtProvider": ["`c'est déjà pris :'(` is already taken by another venue offer"]},
            ),
            # errors on image
            (
                {
                    "image": {
                        "file": base64.b64encode(
                            (pathlib.Path(tests.__path__[0]) / "files" / "mouette_square.jpg").read_bytes()
                        ).decode()
                    }
                },
                {"imageFile": "Bad image ratio: expected 0.66, found 1.0"},
            ),
            (
                {"image": {"file": image_data.WRONG_IMAGE_SIZE}},
                {"imageFile": "The image is too small. It must be above 400x600 pixels."},
            ),
            # error on location
            (
                {"location": {"type": "address", "venueId": 1, "addressId": "coucou"}},
                {"location.AddressLocation.addressId": ["value is not a valid integer"]},
            ),
            (
                {"location": {"type": "address", "venueId": 1, "addressId": 1, "addressLabel": ""}},
                {"location.AddressLocation.addressLabel": ["ensure this value has at least 1 characters"]},
            ),
            (
                {"location": {"type": "address", "venueId": 1, "addressId": 1, "addressLabel": "a" * 201}},
                {"location.AddressLocation.addressLabel": ["ensure this value has at most 200 characters"]},
            ),
            # error on price categories
            (
                {"priceCategories": [{"price": i * 100, "label": f"Tarif {i}"} for i in range(51)]},
                {"priceCategories": ["ensure this value has at most 50 items"]},
            ),
            (
                {
                    "priceCategories": [
                        {"price": 2500, "label": "triangle or"},
                        {"price": 12, "label": "triangle argent"},
                        {"price": 100, "label": "triangle bronze"},
                        {"price": 2500, "label": "triangle or"},
                    ]
                },
                {"priceCategories": ["Price categories must be unique"]},
            ),
            (
                {
                    "priceCategories": [
                        {"price": 30000, "label": "triangle or", "idAtProvider": "comment_ça_ça_ne_marche_pas?"},
                        {"price": 15000, "label": "rond d'argent", "idAtProvider": "comment_ça_ça_ne_marche_pas?"},
                    ]
                },
                {
                    "priceCategories": [
                        "Price category `idAtProvider` must be unique. Duplicated value : comment_ça_ça_ne_marche_pas?"
                    ]
                },
            ),
            (
                {
                    "categoryRelatedFields": {"category": "FESTIVAL_ART_VISUEL"},
                    "accessibility": ACCESSIBILITY_FIELDS,
                    "name": "Le champ des possibles",
                    "hasTicket": True,
                },
                {"offer": ["Une offre qui a un ticket retirable doit avoir l'email du contact de réservation"]},
            ),
            # additional properties not allowed
            ({"tkilol": ""}, {"tkilol": ["extra fields not permitted"]}),
        ],
    )
    def test_incorrect_payload_should_return_400(self, partial_request_json, expected_response_json):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        existing_offer = offers_factories.OfferFactory(venue=venue_provider.venue, idAtProvider="c'est déjà pris :'(")

        payload = self._get_base_payload(venue_provider.venueId)

        payload.update(**partial_request_json)

        response = self.make_request(plain_api_key, json_body=payload)

        assert response.status_code == 400
        assert response.json == expected_response_json

        assert db.session.query(offers_models.Offer).filter(offers_models.Offer.id != existing_offer.id).first() is None
        assert db.session.query(offers_models.Stock).first() is None

    def test_error_when_event_with_has_ticket_to_true_and_no_ticketing_service_set(self):
        plain_api_key, venue_provider = self.setup_active_venue_provider(provider_has_ticketing_urls=False)

        payload = {
            "categoryRelatedFields": {"category": "FESTIVAL_ART_VISUEL"},
            "accessibility": ACCESSIBILITY_FIELDS,
            "location": {"type": "physical", "venueId": venue_provider.venueId},
            "name": "Le champ des possibles",
            "hasTicket": True,
            "bookingContact": "booking@conta.ct",
        }

        response = self.make_request(plain_api_key, json_body=payload)
        assert response.status_code == 400
        assert response.json == {
            "global": "You cannot create an event with `has_ticket=true` because you dont have a ticketing service enabled (neither at provider level nor at venue level)."
        }

    def test_should_not_raise_if_id_at_provider_is_none(self):
        plain_api_key, venue_provider = self.setup_active_venue_provider()

        payload = self._get_base_payload(venue_provider.venueId)
        payload["priceCategories"] = [
            {"price": 30000, "label": "triangle or", "idAtProvider": None},
            {"price": 15000, "label": "rond d'argent", "idAtProvider": None},
        ]

        response = self.make_request(plain_api_key, json_body=payload)
        assert response.status_code == 200
