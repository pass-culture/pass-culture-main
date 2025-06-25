import base64
import datetime
import decimal
import pathlib

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

_CATEGORY_ERROR_JSON = {
    "categoryRelatedFields.category": [
        "unexpected value; permitted: 'ABO_BIBLIOTHEQUE'",
        "unexpected value; permitted: 'ABO_CONCERT'",
        "unexpected value; permitted: 'ABO_LIVRE_NUMERIQUE'",
        "unexpected value; permitted: 'ABO_MEDIATHEQUE'",
        "unexpected value; permitted: 'ABO_PLATEFORME_MUSIQUE'",
        "unexpected value; permitted: 'ABO_PLATEFORME_VIDEO'",
        "unexpected value; permitted: 'ABO_PRATIQUE_ART'",
        "unexpected value; permitted: 'ABO_PRESSE_EN_LIGNE'",
        "unexpected value; permitted: 'ABO_SPECTACLE'",
        "unexpected value; permitted: 'ACHAT_INSTRUMENT'",
        "unexpected value; permitted: 'APP_CULTURELLE'",
        "unexpected value; permitted: 'AUTRE_SUPPORT_NUMERIQUE'",
        "unexpected value; permitted: 'CARTE_JEUNES'",
        "unexpected value; permitted: 'CARTE_MUSEE'",
        "unexpected value; permitted: 'LIVRE_AUDIO_PHYSIQUE'",
        "unexpected value; permitted: 'LIVRE_NUMERIQUE'",
        "unexpected value; permitted: 'LOCATION_INSTRUMENT'",
        "unexpected value; permitted: 'PARTITION'",
        "unexpected value; permitted: 'PLATEFORME_PRATIQUE_ARTISTIQUE'",
        "unexpected value; permitted: 'PODCAST'",
        "unexpected value; permitted: 'PRATIQUE_ART_VENTE_DISTANCE'",
        "unexpected value; permitted: 'SPECTACLE_ENREGISTRE'",
        "unexpected value; permitted: 'SUPPORT_PHYSIQUE_FILM'",
        "unexpected value; permitted: 'TELECHARGEMENT_LIVRE_AUDIO'",
        "unexpected value; permitted: 'TELECHARGEMENT_MUSIQUE'",
        "unexpected value; permitted: 'VISITE_VIRTUELLE'",
        "unexpected value; permitted: 'VOD'",
    ],
    "categoryRelatedFields.musicType": ["field required", "field required"],
    "categoryRelatedFields.showType": ["field required", "field required"],
}


@pytest.mark.usefixtures("db_session")
class PostProductTest(PublicAPIVenueEndpointHelper):
    endpoint_url = "/public/offers/v1/products"
    endpoint_method = "post"

    @staticmethod
    def _get_base_payload(venue_id: int) -> dict:
        return {
            "location": {"type": "physical", "venueId": venue_id},
            "categoryRelatedFields": {
                "category": "SUPPORT_PHYSIQUE_FILM",
                "ean": "1234567891234",
            },
            "accessibility": ACCESSIBILITY_FIELDS,
            "name": "Le champ des possibles",
        }

    def test_should_raise_401_because_not_authenticated(self, client):
        response = client.post(self.endpoint_url, json={})
        assert response.status_code == 401

    def test_should_raise_404_because_has_no_access_to_venue(self, client):
        plain_api_key, _ = self.setup_provider()
        venue = self.setup_venue()
        response = client.with_explicit_token(plain_api_key).post(
            self.endpoint_url, json=self._get_base_payload(venue.id)
        )
        assert response.status_code == 404

    def test_should_raise_404_because_venue_provider_is_inactive(self, client):
        plain_api_key, venue_provider = self.setup_inactive_venue_provider()
        response = client.with_explicit_token(plain_api_key).post(
            self.endpoint_url, json=self._get_base_payload(venue_provider.venue.id)
        )
        assert response.status_code == 404

    @time_machine.travel(datetime.datetime(2025, 6, 25, 12, 30, tzinfo=datetime.timezone.utc), tick=False)
    def test_physical_product_minimal_body(self, client):
        plain_api_key, venue_provider = self.setup_active_venue_provider()

        response = client.with_explicit_token(plain_api_key).post(
            self.endpoint_url, json=self._get_base_payload(venue_provider.venueId)
        )

        assert response.status_code == 200
        created_offer = db.session.query(offers_models.Offer).one()
        assert created_offer.name == "Le champ des possibles"
        assert created_offer.venue == venue_provider.venue
        assert created_offer.subcategoryId == "SUPPORT_PHYSIQUE_FILM"
        assert created_offer.audioDisabilityCompliant is True
        assert created_offer.lastProvider.name == venue_provider.provider.name
        assert created_offer.mentalDisabilityCompliant is True
        assert created_offer.motorDisabilityCompliant is True
        assert created_offer.visualDisabilityCompliant is True
        assert created_offer.publicationDatetime == datetime.datetime(2025, 6, 25, 12, 30)
        assert created_offer.finalizationDatetime == datetime.datetime(2025, 6, 25, 12, 30)
        assert not created_offer.bookingAllowedDatetime
        assert not created_offer.isDuo
        assert created_offer.bookingEmail is None
        assert created_offer.description is None
        assert created_offer.status == offer_mixin.OfferStatus.SOLD_OUT
        assert created_offer.offererAddress.id == venue_provider.venue.offererAddress.id

        assert response.json == {
            "bookingAllowedDatetime": None,
            "publicationDatetime": "2025-06-25T12:30:00Z",
            "bookingContact": None,
            "bookingEmail": None,
            "categoryRelatedFields": {
                "category": "SUPPORT_PHYSIQUE_FILM",
                "ean": "1234567891234",
            },
            "description": None,
            "accessibility": {
                "audioDisabilityCompliant": True,
                "mentalDisabilityCompliant": True,
                "motorDisabilityCompliant": True,
                "visualDisabilityCompliant": True,
            },
            "enableDoubleBookings": False,
            "externalTicketOfficeUrl": None,
            "id": created_offer.id,
            "image": None,
            "itemCollectionDetails": None,
            "location": {"type": "physical", "venueId": venue_provider.venue.id},
            "name": "Le champ des possibles",
            "status": "SOLD_OUT",
            "stock": None,
            "idAtProvider": None,
        }

    @time_machine.travel(datetime.datetime(2025, 6, 25, 12, 30, tzinfo=datetime.timezone.utc), tick=False)
    def test_product_creation_with_full_body(self, client, clear_tests_assets_bucket):
        plain_api_key, venue_provider = self.setup_active_venue_provider()

        in_ten_minutes = datetime.datetime.utcnow().replace(second=0, microsecond=0) + datetime.timedelta(minutes=10)
        in_ten_minutes_in_non_utc_tz = date_utils.utc_datetime_to_department_timezone(in_ten_minutes, "973")
        response = client.with_explicit_token(plain_api_key).post(
            self.endpoint_url,
            json={
                "location": {"type": "physical", "venueId": venue_provider.venue.id},
                "enableDoubleBookings": False,
                "bookingContact": "contact@example.com",
                "bookingEmail": "spam@example.com",
                "categoryRelatedFields": {
                    "category": "SUPPORT_PHYSIQUE_FILM",
                    "ean": "1234567891234",
                },
                "description": "Enregistrement pour la nuit des temps",
                "accessibility": {
                    "audioDisabilityCompliant": True,
                    "mentalDisabilityCompliant": True,
                    "motorDisabilityCompliant": False,
                    "visualDisabilityCompliant": False,
                },
                "externalTicketOfficeUrl": "https://maposaic.com",
                "image": {
                    "credit": "Jean-Crédit Photo",
                    "file": image_data.GOOD_IMAGE,
                },
                "itemCollectionDetails": "A retirer au 6ème sous-sol du parking de la gare entre minuit et 2",
                "name": "Le champ des possibles",
                "stock": {
                    "bookingLimitDatetime": in_ten_minutes_in_non_utc_tz.isoformat(),
                    "price": 1234,
                    "quantity": 3,
                },
                "id_at_provider": "l'id du provider",
            },
        )

        assert response.status_code == 200, response.json

        created_offer = db.session.query(offers_models.Offer).one()
        assert created_offer.name == "Le champ des possibles"
        assert created_offer.venue == venue_provider.venue
        assert created_offer.subcategoryId == "SUPPORT_PHYSIQUE_FILM"
        assert created_offer.audioDisabilityCompliant is True
        assert created_offer.lastProvider == venue_provider.provider
        assert created_offer.mentalDisabilityCompliant is True
        assert created_offer.motorDisabilityCompliant is False
        assert created_offer.visualDisabilityCompliant is False
        assert created_offer.publicationDatetime == datetime.datetime(2025, 6, 25, 12, 30)
        assert created_offer.finalizationDatetime == datetime.datetime(2025, 6, 25, 12, 30)
        assert not created_offer.bookingAllowedDatetime
        assert created_offer.isDuo is False
        assert created_offer.bookingEmail == "spam@example.com"
        assert created_offer.description == "Enregistrement pour la nuit des temps"
        assert created_offer.idAtProvider == "l'id du provider"
        assert created_offer.externalTicketOfficeUrl == "https://maposaic.com"
        assert created_offer.status == offer_mixin.OfferStatus.ACTIVE
        assert created_offer.withdrawalDetails == "A retirer au 6ème sous-sol du parking de la gare entre minuit et 2"
        assert created_offer.offererAddress.id == venue_provider.venue.offererAddress.id

        created_stock = db.session.query(offers_models.Stock).one()
        assert created_stock.price == decimal.Decimal("12.34")
        assert created_stock.quantity == 3
        assert created_stock.offer == created_offer
        assert created_stock.bookingLimitDatetime == in_ten_minutes

        created_mediation = db.session.query(offers_models.Mediation).one()
        assert created_mediation.offer == created_offer
        assert created_offer.image.url == created_mediation.thumbUrl
        assert (
            created_offer.image.url
            == f"{settings.OBJECT_STORAGE_URL}/thumbs/mediations/{human_ids.humanize(created_mediation.id)}"
        )

        assert response.json == {
            "bookingAllowedDatetime": None,
            "publicationDatetime": "2025-06-25T12:30:00Z",
            "bookingContact": "contact@example.com",
            "bookingEmail": "spam@example.com",
            "categoryRelatedFields": {
                "ean": "1234567891234",
                "category": "SUPPORT_PHYSIQUE_FILM",
            },
            "description": "Enregistrement pour la nuit des temps",
            "accessibility": {
                "audioDisabilityCompliant": True,
                "mentalDisabilityCompliant": True,
                "motorDisabilityCompliant": False,
                "visualDisabilityCompliant": False,
            },
            "enableDoubleBookings": False,
            "externalTicketOfficeUrl": "https://maposaic.com",
            "id": created_offer.id,
            "idAtProvider": "l'id du provider",
            "image": {
                "credit": "Jean-Crédit Photo",
                "url": f"http://localhost/storage/thumbs/mediations/{human_ids.humanize(created_mediation.id)}",
            },
            "itemCollectionDetails": "A retirer au 6ème sous-sol du parking de la gare entre minuit et 2",
            "location": {"type": "physical", "venueId": venue_provider.venue.id},
            "name": "Le champ des possibles",
            "status": "ACTIVE",
            "stock": {
                "bookedQuantity": 0,
                "bookingLimitDatetime": date_utils.format_into_utc_date(in_ten_minutes),
                "price": 1234,
                "quantity": 3,
            },
        }

    @time_machine.travel(datetime.datetime(2025, 6, 25, 12, 30, tzinfo=datetime.timezone.utc), tick=False)
    @pytest.mark.parametrize(
        "partial_request_json,expected_publication_datetime,expected_response_publication_datetime",
        [
            (
                {"publicationDatetime": "2025-08-01T08:00:00+02:00"},  # tz: Europe/Paris
                datetime.datetime(2025, 8, 1, 6),  # tz: utc
                "2025-08-01T06:00:00Z",
            ),
            (
                {"publicationDatetime": "now"},
                datetime.datetime(2025, 6, 25, 12, 30),
                "2025-06-25T12:30:00Z",
            ),
            # should default to now
            ({}, datetime.datetime(2025, 6, 25, 12, 30), "2025-06-25T12:30:00Z"),
            # draft
            ({"publicationDatetime": None}, None, None),
        ],
    )
    def test_publication_datetime_param(
        self, client, partial_request_json, expected_publication_datetime, expected_response_publication_datetime
    ):
        plain_api_key, venue_provider = self.setup_active_venue_provider()

        payload = self._get_base_payload(venue_provider.venueId)
        payload.update(**partial_request_json)

        response = client.with_explicit_token(plain_api_key).post(self.endpoint_url, json=payload)

        assert response.status_code == 200
        assert response.json["publicationDatetime"] == expected_response_publication_datetime

        created_offer = db.session.query(offers_models.Offer).one()
        assert created_offer.publicationDatetime == expected_publication_datetime

    @time_machine.travel(datetime.datetime(2025, 6, 25, 12, 30, tzinfo=datetime.timezone.utc), tick=False)
    @pytest.mark.parametrize(
        "partial_request_json,expected_booking_allowed_datetime,expected_response_booking_allowed_datetime",
        [
            (
                {"bookingAllowedDatetime": "2025-08-01T08:00:00+02:00"},  # tz: Europe/Paris
                datetime.datetime(2025, 8, 1, 6),  # tz: utc
                "2025-08-01T06:00:00Z",
            ),
            ({"bookingAllowedDatetime": None}, None, None),
            # should default to `None``
            ({}, None, None),
        ],
    )
    def test_booking_allowed_datetime_param(
        self,
        client,
        partial_request_json,
        expected_booking_allowed_datetime,
        expected_response_booking_allowed_datetime,
    ):
        plain_api_key, venue_provider = self.setup_active_venue_provider()

        payload = self._get_base_payload(venue_provider.venueId)
        payload.update(**partial_request_json)

        response = client.with_explicit_token(plain_api_key).post(self.endpoint_url, json=payload)

        assert response.status_code == 200
        assert response.json["bookingAllowedDatetime"] == expected_response_booking_allowed_datetime

        created_offer = db.session.query(offers_models.Offer).one()
        assert created_offer.bookingAllowedDatetime == expected_booking_allowed_datetime

    def test_unlimited_quantity(self, client):
        plain_api_key, venue_provider = self.setup_active_venue_provider()

        response = client.with_explicit_token(plain_api_key).post(
            self.endpoint_url,
            json={
                "location": {"type": "physical", "venueId": venue_provider.venue.id},
                "categoryRelatedFields": {
                    "category": "SUPPORT_PHYSIQUE_FILM",
                    "ean": "1234567891234",
                },
                "accessibility": ACCESSIBILITY_FIELDS,
                "name": "Le champ des possibles",
                "stock": {
                    "bookedQuantity": 0,
                    "price": 1,
                    "quantity": "unlimited",
                },
            },
        )

        assert response.status_code == 200
        created_offer = db.session.query(offers_models.Offer).one()
        assert created_offer.name == "Le champ des possibles"
        assert created_offer.status == offer_mixin.OfferStatus.ACTIVE

        created_stock = db.session.query(offers_models.Stock).one()
        assert created_stock.price == decimal.Decimal("0.01")
        assert created_stock.quantity is None
        assert created_stock.offer == created_offer

    def test_create_allowed_product(self, client):
        plain_api_key, venue_provider = self.setup_active_venue_provider()

        response = client.with_explicit_token(plain_api_key).post(
            self.endpoint_url,
            json={
                "location": {
                    "type": "digital",
                    "url": "https://la-flute-en-chantier.fr",
                    "venue_id": venue_provider.venue.id,
                },
                "categoryRelatedFields": {"category": "SPECTACLE_ENREGISTRE", "showType": "OPERA-GRAND_OPERA"},
                "accessibility": ACCESSIBILITY_FIELDS,
                "name": "La flûte en chantier",
            },
        )

        assert response.status_code == 200
        assert db.session.query(offers_models.Offer).count() == 1

    def test_extra_data_deserialization(self, client):
        plain_api_key, venue_provider = self.setup_active_venue_provider()

        response = client.with_explicit_token(plain_api_key).post(
            self.endpoint_url,
            json={
                "location": {"type": "physical", "venueId": venue_provider.venue.id},
                "categoryRelatedFields": {
                    "category": "SUPPORT_PHYSIQUE_FILM",
                    "ean": "1234567891234",
                },
                "accessibility": ACCESSIBILITY_FIELDS,
                "name": "Le champ des possibles",
            },
        )

        assert response.status_code == 200
        assert response.json["categoryRelatedFields"] == {"category": "SUPPORT_PHYSIQUE_FILM", "ean": "1234567891234"}
        created_offer = db.session.query(offers_models.Offer).one()
        assert created_offer.ean == "1234567891234"
        assert "ean" not in created_offer.extraData

    def test_event_with_custom_address(self, client):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
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

        response = client.with_explicit_token(plain_api_key).post(self.endpoint_url, json=payload)
        assert response.status_code == 200
        assert response.json["location"]["addressId"] == address.id
        assert response.json["location"]["addressLabel"] == "My beautiful address no one knows about"
        created_offer = db.session.query(offers_models.Offer).one()
        assert created_offer.offererAddress == offerer_address

    def test_event_with_custom_address_should_create_offerer_address(self, client):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
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
        response = client.with_explicit_token(plain_api_key).post(self.endpoint_url, json=payload)
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

    def test_event_with_custom_address_should_raiser_404_because_address_does_not_exist(self, client):
        plain_api_key, venue_provider = self.setup_active_venue_provider(provider_has_ticketing_urls=False)
        payload = self._get_base_payload(venue_provider.venueId)
        address = geography_factories.AddressFactory()
        not_existing_address_id = address.id + 1

        payload["location"] = {
            "type": "address",
            "venueId": venue_provider.venueId,
            "addressId": not_existing_address_id,
        }
        response = client.with_explicit_token(plain_api_key).post(self.endpoint_url, json=payload)
        assert response.status_code == 404
        assert response.json == {
            "location.AddressLocation.addressId": [f"There is no address with id {not_existing_address_id}"]
        }

    @pytest.mark.parametrize(
        "partial_request_json, expected_response_json",
        [
            # errors on category
            ({"categoryRelatedFields": {"category": "EVENEMENT_JEU", "ean": "1234567890123"}}, _CATEGORY_ERROR_JSON),
            (  # books are not allowed
                {"categoryRelatedFields": {"category": "LIVRE_PAPIER", "ean": "1234567890123", "author": "Maurice"}},
                _CATEGORY_ERROR_JSON,
            ),
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
            # `enableDoubleBookings` not allowed for category
            (
                {
                    "enableDoubleBookings": True,
                    "categoryRelatedFields": {"category": "SUPPORT_PHYSIQUE_FILM", "ean": "1234567891234"},
                },
                {"enableDoubleBookings": ["the category chosen does not allow double bookings"]},
            ),
            # errors on stock
            (
                {
                    "stock": {"bookingLimitDatetime": "2021-01-01T00:00:00", "price": 10, "quantity": 10},
                },
                {"stock.bookingLimitDatetime": ["The datetime must be timezone-aware."]},
            ),
            (
                {
                    "stock": {"bookingLimitDatetime": "2021-01-01T00:00:00+00:00", "price": 10, "quantity": 10},
                },
                {"stock.bookingLimitDatetime": ["The datetime must be in the future."]},
            ),
            ({"stock": {"price": 12.34, "quantity": "unlimited"}}, {"stock.price": ["value is not a valid integer"]}),
            (
                {"stock": {"price": -1200, "quantity": "unlimited"}},
                {"stock.price": ["ensure this value is greater than or equal to 0"]},
            ),
            (
                {"stock": {"price": 1200, "quantity": -1}},
                {"stock.quantity": ["ensure this value is greater than 0", "unexpected value; permitted: 'unlimited'"]},
            ),
            # `stock.bookingLimitDatetime` and `publicationDatetime` not coherent
            (
                {
                    "stock": {
                        "bookingLimitDatetime": (
                            datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=3)
                        ).isoformat(),
                        "price": 10,
                        "quantity": 10,
                    },
                    "publicationDatetime": (
                        datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=100)
                    ).isoformat(),
                },
                {"__root__": ["`stock.bookingLimitDatetime` must be after `publicationDatetime`"]},
            ),
            # `stock.bookingLimitDatetime` and `bookingLimitDatetime` not coherent
            (
                {
                    "stock": {
                        "bookingLimitDatetime": (
                            datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=3)
                        ).isoformat(),
                        "price": 10,
                        "quantity": 10,
                    },
                    "bookingAllowedDatetime": (
                        datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=100)
                    ).isoformat(),
                },
                {"__root__": ["`stock.bookingLimitDatetime` must be after `bookingAllowedDatetime`"]},
            ),
        ],
    )
    def test_incorrect_payload_should_return_400(self, client, partial_request_json, expected_response_json):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        existing_offer = offers_factories.OfferFactory(venue=venue_provider.venue, idAtProvider="c'est déjà pris :'(")

        payload = self._get_base_payload(venue_provider.venueId)
        payload.update(**partial_request_json)

        response = client.with_explicit_token(plain_api_key).post(self.endpoint_url, json=payload)

        assert response.status_code == 400
        assert response.json == expected_response_json

        assert db.session.query(offers_models.Offer).filter(offers_models.Offer.id != existing_offer.id).first() is None
        assert db.session.query(offers_models.Stock).first() is None

    def test_venue_allowed_should_return_404(self, client):
        not_allowed_venue = offerers_factories.VenueFactory()
        plain_api_key, _ = self.setup_active_venue_provider()

        response = client.with_explicit_token(plain_api_key).post(
            self.endpoint_url,
            json={
                "location": {"type": "physical", "venueId": not_allowed_venue.id},
                "categoryRelatedFields": {
                    "category": "SUPPORT_PHYSIQUE_FILM",
                    "ean": "1234567891234",
                },
                "accessibility": ACCESSIBILITY_FIELDS,
                "name": "Le champ des possibles",
            },
        )

        assert response.status_code == 404
        assert response.json == {"global": "Venue cannot be found"}
        assert db.session.query(offers_models.Offer).first() is None
