from datetime import datetime
from datetime import timedelta
import decimal
import logging

import pytest

from pcapi import settings
from pcapi.core.geography import factories as geography_factories
from pcapi.core.offerers import factories as offerers_factories
from pcapi.core.offerers import models as offerers_models
from pcapi.core.offers import factories as offers_factories
from pcapi.core.offers import models as offers_models
from pcapi.models import db
from pcapi.models import offer_mixin
from pcapi.utils import human_ids
from pcapi.utils.date import local_datetime_to_default_timezone

from tests.conftest import TestClient
from tests.routes import image_data
from tests.routes.public.helpers import PublicAPIVenueEndpointHelper

from . import utils


@pytest.mark.usefixtures("db_session")
class PostEventTest(PublicAPIVenueEndpointHelper):
    endpoint_url = "/public/offers/v1/events"
    endpoint_method = "post"

    @staticmethod
    def _get_base_payload(venue_id: int) -> dict:
        return {
            "categoryRelatedFields": {"category": "RENCONTRE"},
            "accessibility": utils.ACCESSIBILITY_FIELDS,
            "location": {"type": "physical", "venueId": venue_id},
            "name": "Le champ des possibles",
            "hasTicket": False,
        }

    def test_should_raise_404_because_has_no_access_to_venue(self, client: TestClient):
        plain_api_key, _ = self.setup_provider()
        venue = self.setup_venue()
        response = client.with_explicit_token(plain_api_key).post(
            self.endpoint_url, json=self._get_base_payload(venue_id=venue.id)
        )
        assert response.status_code == 404

    def test_should_raise_404_because_venue_provider_is_inactive(self, client: TestClient):
        plain_api_key, venue_provider = self.setup_inactive_venue_provider()
        response = client.with_explicit_token(plain_api_key).post(
            self.endpoint_url, json=self._get_base_payload(venue_id=venue_provider.venue.id)
        )
        assert response.status_code == 404

    def test_event_minimal_body(self, client):
        plain_api_key, venue_provider = self.setup_active_venue_provider()

        response = client.with_explicit_token(plain_api_key).post(
            self.endpoint_url,
            json=self._get_base_payload(venue_provider.venueId),
        )

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
        assert created_offer.publicationDate is None
        assert created_offer.description is None
        assert created_offer.status == offer_mixin.OfferStatus.DRAFT
        assert created_offer.withdrawalDetails is None
        assert created_offer.withdrawalType is None
        assert created_offer.withdrawalDelay is None
        assert not created_offer.futureOffer

    def test_event_with_depreacted_music_type_triggers_warning_log(self, client, caplog):
        # TODO(jbaudet-pass): remove test once the deprecated enum
        # music type is not allowed anymore
        plain_api_key, venue_provider = self.setup_active_venue_provider()

        payload = self._get_base_payload(venue_provider.venueId)
        payload["categoryRelatedFields"] = {"category": "CONCERT", "musicType": "METAL-DOOM_METAL"}
        payload["bookingContact"] = "booking@test.com"

        with caplog.at_level(logging.INFO):
            response = client.with_explicit_token(plain_api_key).post(self.endpoint_url, json=payload)

        assert response.status_code == 200
        assert next(rec for rec in caplog.records if rec.msg == "offer: using old music type")

    def test_event_with_new_and_expected_music_type_does_not_trigger_warning_log(self, client, caplog):
        # TODO(jbaudet-pass): remove test once the deprecated enum
        # music type is not allowed anymore
        plain_api_key, venue_provider = self.setup_active_venue_provider()

        payload = self._get_base_payload(venue_provider.venueId)
        payload["categoryRelatedFields"] = {"category": "CONCERT", "musicType": "METAL"}
        payload["bookingContact"] = "booking@test.com"

        with caplog.at_level(logging.INFO):
            response = client.with_explicit_token(plain_api_key).post(self.endpoint_url, json=payload)

        assert response.status_code == 200
        assert not [rec for rec in caplog.records if rec.msg == "offer: using old music type"]

    def test_future_event(self, client):
        plain_api_key, venue_provider = self.setup_active_venue_provider()

        payload = self._get_base_payload(venue_provider.venueId)
        publication_date = datetime.utcnow().replace(minute=0, second=0) + timedelta(days=30)
        payload["publicationDate"] = publication_date.isoformat()
        response = client.with_explicit_token(plain_api_key).post(self.endpoint_url, json=payload)

        assert response.status_code == 200
        created_offer = db.session.query(offers_models.Offer).one()
        assert created_offer.publicationDate == local_datetime_to_default_timezone(
            publication_date, "Europe/Paris"
        ).replace(microsecond=0, tzinfo=None)
        assert created_offer.futureOffer.isWaitingForPublication

    def test_event_creation_should_return_400_because_id_at_provider_is_taken(self, client):
        plain_api_key, venue_provider = self.setup_active_venue_provider(provider_has_ticketing_urls=True)

        id_at_provider = "rolala"
        # existing offer with id_at_provider
        offers_factories.EventOfferFactory(
            venue=venue_provider.venue,
            bookingContact="contact@example.com",
            bookingEmail="notify@passq.com",
            subcategoryId="CONCERT",
            durationMinutes=20,
            isDuo=False,
            lastProvider=venue_provider.provider,
            withdrawalType=offers_models.WithdrawalTypeEnum.IN_APP,
            withdrawalDelay=86400,
            withdrawalDetails="Around there",
            description="A description",
            idAtProvider=id_at_provider,
        )

        payload = self._get_base_payload(venue_provider.venueId)
        payload["idAtProvider"] = id_at_provider

        response = client.with_explicit_token(plain_api_key).post(
            self.endpoint_url,
            json=payload,
        )

        assert response.status_code == 400
        assert response.json == {"idAtProvider": ["`rolala` is already taken by another venue offer"]}

    def test_event_creation_with_full_body(self, client, clear_tests_assets_bucket):
        plain_api_key, venue_provider = self.setup_active_venue_provider(provider_has_ticketing_urls=True)

        response = client.with_explicit_token(plain_api_key).post(
            self.endpoint_url,
            json={
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
            },
        )

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
        assert created_offer.publicationDate is None
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
            "publicationDate": None,
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

    def test_event_creation_with_titelive_type(self, client, clear_tests_assets_bucket):
        plain_api_key, venue_provider = self.setup_active_venue_provider(provider_has_ticketing_urls=True)
        response = client.with_explicit_token(plain_api_key).post(
            self.endpoint_url,
            json={
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
            },
        )
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
            "musicType": "OTHER",
            "performer": "Nicolas Jaar",
        }

    @pytest.mark.features(ENABLE_TITELIVE_MUSIC_TYPES_IN_API_OUTPUT=True)
    def test_event_creation_with_titelive_type_with_active_serialization(self, client, clear_tests_assets_bucket):
        plain_api_key, venue_provider = self.setup_active_venue_provider(provider_has_ticketing_urls=True)

        response = client.with_explicit_token(plain_api_key).post(
            self.endpoint_url,
            json={
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
            },
        )

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
    def test_other_music_type_serialization(self, client):
        plain_api_key, venue_provider = self.setup_active_venue_provider()

        response = client.with_explicit_token(plain_api_key).post(
            self.endpoint_url,
            json={
                "categoryRelatedFields": {"category": "CONCERT", "musicType": "OTHER"},
                "accessibility": utils.ACCESSIBILITY_FIELDS,
                "location": {"type": "physical", "venueId": venue_provider.venueId},
                "name": "Le champ des possibles",
                "hasTicket": False,
                "bookingContact": "booking@conta.ct",
            },
        )

        assert response.status_code == 200
        created_offer = db.session.query(offers_models.Offer).one()
        assert created_offer.extraData == {"musicType": "-1", "musicSubType": "-1", "gtl_id": "19000000"}

        assert response.json["categoryRelatedFields"] == {
            "author": None,
            "category": "CONCERT",
            "musicType": "OTHER",
            "performer": None,
        }

    def test_event_with_custom_address(self, client):
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

        response = client.with_explicit_token(plain_api_key).post(self.endpoint_url, json=payload)
        assert response.status_code == 200
        assert response.json["location"]["addressId"] == address.id
        assert response.json["location"]["addressLabel"] == "My beautiful address no one knows about"
        created_offer = db.session.query(offers_models.Offer).one()
        assert created_offer.offererAddress == offerer_address

    def test_event_with_custom_address_should_create_offerer_address(self, client):
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
            "location.AddressLocation.addressId": [f"There is no venue with id {not_existing_address_id}"]
        }

    @pytest.mark.parametrize(
        "partial_location,expected_json",
        [
            ({"addressId": "coucou"}, {"location.AddressLocation.addressId": ["value is not a valid integer"]}),
            (
                {"addressLabel": ""},
                {"location.AddressLocation.addressLabel": ["ensure this value has at least 1 characters"]},
            ),
            (
                {"addressLabel": "a" * 201},
                {"location.AddressLocation.addressLabel": ["ensure this value has at most 200 characters"]},
            ),
        ],
    )
    def test_event_with_custom_address_should_raiser_400_because_address_location_params_are_incorrect(
        self, client, partial_location, expected_json
    ):
        plain_api_key, venue_provider = self.setup_active_venue_provider(provider_has_ticketing_urls=False)
        payload = self._get_base_payload(venue_provider.venueId)
        address = geography_factories.AddressFactory()
        base_location_object = {
            "type": "address",
            "venueId": venue_provider.venueId,
            "addressId": address.id,
            "addressLabel": "My beautiful address no one knows about",
        }
        payload["location"] = dict(base_location_object, **partial_location)
        response = client.with_explicit_token(plain_api_key).post(self.endpoint_url, json=payload)
        assert response.status_code == 400
        assert response.json == expected_json

    def test_event_without_ticket(self, client):
        plain_api_key, venue_provider = self.setup_active_venue_provider(provider_has_ticketing_urls=False)

        response = client.with_explicit_token(plain_api_key).post(
            self.endpoint_url,
            json={
                "categoryRelatedFields": {"category": "FESTIVAL_ART_VISUEL"},
                "accessibility": utils.ACCESSIBILITY_FIELDS,
                "location": {"type": "physical", "venueId": venue_provider.venueId},
                "name": "Le champ des possibles",
                "hasTicket": False,
                "bookingContact": "booking@conta.ct",
            },
        )

        assert response.status_code == 200
        created_offer = db.session.query(offers_models.Offer).one()
        assert created_offer.withdrawalType == offers_models.WithdrawalTypeEnum.NO_TICKET

    def test_event_with_has_ticket_to_true_and_ticketing_service_at_provider_level(self, client):
        plain_api_key, venue_provider = self.setup_active_venue_provider(provider_has_ticketing_urls=True)

        response = client.with_explicit_token(plain_api_key).post(
            self.endpoint_url,
            json={
                "categoryRelatedFields": {"category": "FESTIVAL_ART_VISUEL"},
                "accessibility": utils.ACCESSIBILITY_FIELDS,
                "location": {"type": "physical", "venueId": venue_provider.venueId},
                "name": "Le champ des possibles",
                "hasTicket": True,
                "bookingContact": "booking@conta.ct",
            },
        )
        assert response.status_code == 200
        created_offer = db.session.query(offers_models.Offer).one()
        assert created_offer.withdrawalType == offers_models.WithdrawalTypeEnum.IN_APP

    def test_event_with_has_ticket_to_true_and_ticketing_service_at_venue_level(self, client):
        plain_api_key, venue_provider = self.setup_active_venue_provider(provider_has_ticketing_urls=True)

        response = client.with_explicit_token(plain_api_key).post(
            self.endpoint_url,
            json={
                "categoryRelatedFields": {"category": "FESTIVAL_ART_VISUEL"},
                "accessibility": utils.ACCESSIBILITY_FIELDS,
                "location": {"type": "physical", "venueId": venue_provider.venueId},
                "name": "Le champ des possibles",
                "hasTicket": True,
                "bookingContact": "booking@conta.ct",
            },
        )
        assert response.status_code == 200
        created_offer = db.session.query(offers_models.Offer).one()
        assert created_offer.withdrawalType == offers_models.WithdrawalTypeEnum.IN_APP

    def test_error_when_event_with_has_ticket_to_true_and_no_ticketing_service_set(self, client):
        plain_api_key, venue_provider = self.setup_active_venue_provider(provider_has_ticketing_urls=False)

        response = client.with_explicit_token(plain_api_key).post(
            self.endpoint_url,
            json={
                "categoryRelatedFields": {"category": "FESTIVAL_ART_VISUEL"},
                "accessibility": utils.ACCESSIBILITY_FIELDS,
                "location": {"type": "physical", "venueId": venue_provider.venueId},
                "name": "Le champ des possibles",
                "hasTicket": True,
                "bookingContact": "booking@conta.ct",
            },
        )
        assert response.status_code == 400
        assert response.json == {
            "global": "You cannot create an event with `has_ticket=true` because you dont have a ticketing service enabled (neither at provider level nor at venue level)."
        }

    def test_error_when_withdrawable_event_but_no_booking_contact(self, client):
        plain_api_key, venue_provider = self.setup_active_venue_provider(provider_has_ticketing_urls=True)

        response = client.with_explicit_token(plain_api_key).post(
            self.endpoint_url,
            json={
                "categoryRelatedFields": {"category": "FESTIVAL_ART_VISUEL"},
                "accessibility": utils.ACCESSIBILITY_FIELDS,
                "location": {"type": "physical", "venueId": venue_provider.venueId},
                "name": "Le champ des possibles",
                "hasTicket": True,
            },
        )

        assert response.status_code == 400
        assert db.session.query(offers_models.Offer).count() == 0
        assert response.json == {
            "offer": ["Une offre qui a un ticket retirable doit avoir l'email du contact de réservation"]
        }

    def test_error_when_duplicate_price_categories(self, client):
        plain_api_key, venue_provider = self.setup_active_venue_provider(provider_has_ticketing_urls=True)

        response = client.with_explicit_token(plain_api_key).post(
            self.endpoint_url,
            json={
                "enableDoubleBookings": True,
                "bookingContact": "contact@example.com",
                "bookingEmail": "nicoj@example.com",
                "accessibility": utils.ACCESSIBILITY_FIELDS,
                "location": {"type": "physical", "venueId": venue_provider.venueId},
                "name": "Le champ des possibles",
                "categoryRelatedFields": {
                    "author": "Ray Charles",
                    "category": "CONCERT",
                    "musicType": "ELECTRO-HOUSE",
                    "gtl_id": "04030000",
                    "performer": "Nicolas Jaar",
                    "stageDirector": "Alfred",  # field not applicable
                },
                "hasTicket": True,
                "priceCategories": [
                    {"price": 2500, "label": "triangle or"},
                    {"price": 12, "label": "triangle argent"},
                    {"price": 100, "label": "triangle bronze"},
                    {"price": 2500, "label": "triangle or"},
                ],
            },
        )

        assert response.status_code == 400
        assert response.json == {"priceCategories": ["Price categories must be unique"]}

    def test_future_event_400(self, client):
        plain_api_key, venue_provider = self.setup_active_venue_provider(provider_has_ticketing_urls=True)

        publication_date = datetime.utcnow().replace(minute=0, second=0) - timedelta(days=30)
        response = client.with_explicit_token(plain_api_key).post(
            self.endpoint_url,
            json={
                "categoryRelatedFields": {"category": "RENCONTRE"},
                "accessibility": utils.ACCESSIBILITY_FIELDS,
                "location": {"type": "physical", "venueId": venue_provider.venueId},
                "name": "Le champ des possibles",
                "hasTicket": False,
                "publicationDate": publication_date.isoformat(),
            },
        )

        assert response.status_code == 400
        assert response.json["publication_date"] == ["Impossible de sélectionner une date de publication dans le passé"]

    def test_should_raise_400_because_of_duplicated_price_category_ids_at_provider(self, client):
        plain_api_key, venue_provider = self.setup_active_venue_provider(provider_has_ticketing_urls=True)

        payload = self._get_base_payload(venue_provider.venueId)
        payload["priceCategories"] = [
            {"price": 30000, "label": "triangle or", "idAtProvider": "comment_ça_ça_ne_marche_pas?"},
            {"price": 15000, "label": "rond d'argent", "idAtProvider": "comment_ça_ça_ne_marche_pas?"},
        ]

        response = client.with_explicit_token(plain_api_key).post(
            self.endpoint_url,
            json=payload,
        )
        assert response.status_code == 400
        assert response.json == {
            "priceCategories": [
                "Price category `idAtProvider` must be unique. Duplicated value : comment_ça_ça_ne_marche_pas?"
            ]
        }

    def test_should_not_raise_if_id_at_provider_is_none(self, client):
        plain_api_key, venue_provider = self.setup_active_venue_provider(provider_has_ticketing_urls=True)

        payload = self._get_base_payload(venue_provider.venueId)
        payload["priceCategories"] = [
            {"price": 30000, "label": "triangle or", "idAtProvider": None},
            {"price": 15000, "label": "rond d'argent", "idAtProvider": None},
        ]

        response = client.with_explicit_token(plain_api_key).post(
            self.endpoint_url,
            json=payload,
        )
        assert response.status_code == 200
