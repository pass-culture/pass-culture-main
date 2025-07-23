import base64
import datetime
import pathlib

import pytest
import time_machine

from pcapi import settings
from pcapi.core.geography import factories as geography_factories
from pcapi.core.offerers import factories as offerers_factories
from pcapi.core.offers import factories as offers_factories
from pcapi.core.offers import models as offers_models
from pcapi.core.providers import factories as providers_factories
from pcapi.models import db
from pcapi.utils import human_ids

import tests
from tests.routes import image_data
from tests.routes.public.helpers import PublicAPIVenueEndpointHelper


@pytest.mark.usefixtures("db_session")
class PatchEventTest(PublicAPIVenueEndpointHelper):
    endpoint_url = "/public/offers/v1/events/{offer_id}"
    endpoint_method = "patch"
    default_path_params = {"offer_id": 1}

    def setup_base_resource(
        self,
        venue=None,
        provider=None,
        digital=False,
        booking_allowed_datetime=None,
        publication_datetime=None,
    ) -> offers_models.Offer:
        venue = venue or self.setup_venue()
        shared_data = {
            "venue": venue,
            "withdrawalDetails": "Des conditions de retrait sur la sellette",
            "withdrawalType": offers_models.WithdrawalTypeEnum.BY_EMAIL,
            "withdrawalDelay": 86400,
            "bookingContact": "contact@example.com",
            "bookingEmail": "notify@example.com",
            "lastProvider": provider,
        }

        if booking_allowed_datetime:
            shared_data["bookingAllowedDatetime"] = booking_allowed_datetime

        if publication_datetime:
            shared_data["publicationDatetime"] = publication_datetime

        if digital:
            return offers_factories.DigitalOfferFactory(**shared_data, subcategoryId="LIVESTREAM_MUSIQUE")
        return offers_factories.EventOfferFactory(
            **shared_data, subcategoryId="CONCERT", extraData={"gtl_id": "02000000"}
        )

    def test_should_raise_404_because_has_no_access_to_venue(self):
        plain_api_key, _ = self.setup_provider()
        offer = self.setup_base_resource()
        response = self.make_request(plain_api_key, {"offer_id": offer.id})
        assert response.status_code == 404

    def test_should_raise_404_because_venue_provider_is_inactive(self):
        plain_api_key, venue_provider = self.setup_inactive_venue_provider()
        offer = self.setup_base_resource(venue=venue_provider.venue, provider=venue_provider.provider)
        response = self.make_request(plain_api_key, {"offer_id": offer.id})
        assert response.status_code == 404

    def test_deactivate_offer(self):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        offer = self.setup_base_resource(venue=venue_provider.venue, provider=venue_provider.provider)

        response = self.make_request(plain_api_key, {"offer_id": offer.id}, json_body={"isActive": False})

        assert response.status_code == 200
        assert response.json["status"] == "INACTIVE"
        assert offer.isActive is False

    def test_sets_field_to_none_and_leaves_other_unchanged(self):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        offer = offers_factories.EventOfferFactory(
            subcategoryId="CONCERT",
            venue=venue_provider.venue,
            withdrawalDetails="Des conditions de retrait sur la sellette",
            withdrawalType=offers_models.WithdrawalTypeEnum.BY_EMAIL,
            withdrawalDelay=86400,
            bookingContact="contact@example.com",
            bookingEmail="notify@example.com",
            lastProvider=venue_provider.provider,
            extraData={"gtl_id": "03000000"},
        )

        response = self.make_request(plain_api_key, {"offer_id": offer.id}, json_body={"itemCollectionDetails": None})

        assert response.status_code == 200
        assert response.json["itemCollectionDetails"] is None
        assert offer.withdrawalDetails is None
        assert offer.bookingEmail == "notify@example.com"
        assert offer.withdrawalType == offers_models.WithdrawalTypeEnum.BY_EMAIL
        assert offer.withdrawalDelay == 86400

    def test_sets_accessibility_partially(self):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        offer = offers_factories.EventOfferFactory(
            venue=venue_provider.venue,
            audioDisabilityCompliant=True,
            mentalDisabilityCompliant=True,
            motorDisabilityCompliant=True,
            visualDisabilityCompliant=True,
            lastProvider=venue_provider.provider,
        )

        response = self.make_request(
            plain_api_key,
            {"offer_id": offer.id},
            json_body={"accessibility": {"audioDisabilityCompliant": False}},
        )

        assert response.status_code == 200
        assert response.json["accessibility"] == {
            "audioDisabilityCompliant": False,
            "mentalDisabilityCompliant": True,
            "motorDisabilityCompliant": True,
            "visualDisabilityCompliant": True,
        }
        assert offer.audioDisabilityCompliant is False
        assert offer.mentalDisabilityCompliant is True
        assert offer.motorDisabilityCompliant is True
        assert offer.visualDisabilityCompliant is True

    def test_update_extra_data_partially(self):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        offer = offers_factories.EventOfferFactory(
            venue=venue_provider.venue,
            subcategoryId="FESTIVAL_ART_VISUEL",
            extraData={
                "author": "Maurice",
                "stageDirector": "Robert",
                "performer": "Pink Pâtisserie",
            },
            lastProvider=venue_provider.provider,
            withdrawalDelay=86400,
            withdrawalType=offers_models.WithdrawalTypeEnum.BY_EMAIL,
            bookingContact="contact@example.com",
            bookingEmail="notify@example.com",
        )

        response = self.make_request(
            plain_api_key,
            {"offer_id": offer.id},
            json_body={
                "categoryRelatedFields": {
                    "category": "FESTIVAL_ART_VISUEL",
                    "author": "Maurice",
                    "stageDirector": "Robert",
                    "performer": "Pink Pâtisserie",
                }
            },
        )

        assert response.status_code == 200
        assert response.json["categoryRelatedFields"] == {
            "author": "Maurice",
            "category": "FESTIVAL_ART_VISUEL",
            "performer": "Pink Pâtisserie",
        }
        assert offer.extraData == {
            "author": "Maurice",
            "performer": "Pink Pâtisserie",
            "stageDirector": "Robert",
        }

    def test_should_update_extra_data_even_if_extra_data_has_an_empty_stage_director(self):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        offer = offers_factories.EventOfferFactory(
            venue=venue_provider.venue,
            subcategoryId="FESTIVAL_ART_VISUEL",
            extraData={
                "author": "Maurice",
                "stageDirector": "",  # faulty stageDirector
                "performer": "Pink Pâtisserie",
            },
            lastProvider=venue_provider.provider,
            withdrawalDelay=86400,
            withdrawalType=offers_models.WithdrawalTypeEnum.BY_EMAIL,
            bookingContact="contact@example.com",
            bookingEmail="notify@example.com",
        )

        response = self.make_request(
            plain_api_key,
            {"offer_id": offer.id},
            json_body={
                "categoryRelatedFields": {
                    "category": "FESTIVAL_ART_VISUEL",
                    "author": "Maurice",
                    "performer": "Pink Pâtisserie",
                }
            },
        )

        assert response.status_code == 200
        assert response.json["categoryRelatedFields"] == {
            "author": "Maurice",
            "category": "FESTIVAL_ART_VISUEL",
            "performer": "Pink Pâtisserie",
        }
        assert offer.extraData == {
            "author": "Maurice",
            "performer": "Pink Pâtisserie",
            "stageDirector": "",
        }
        assert not offer.ean

    def test_patch_all_fields(self):
        plain_api_key, venue_provider = self.setup_active_venue_provider(provider_has_ticketing_urls=True)
        offer = offers_factories.EventOfferFactory(
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
            extraData={"gtl_id": "02000000"},
        )

        new_name = offer.name + "_updated"
        response = self.make_request(
            plain_api_key,
            {"offer_id": offer.id},
            json_body={
                "bookingContact": "test@myemail.com",
                "bookingEmail": "test@myemail.com",
                "eventDuration": 40,
                "enableDoubleBookings": "true",
                "itemCollectionDetails": "Here !",
                "description": "A new description",
                "image": {"file": image_data.GOOD_IMAGE},
                "idAtProvider": "oh it has been updated",
                "name": new_name,
            },
        )

        assert response.status_code == 200
        assert offer.withdrawalType == offers_models.WithdrawalTypeEnum.IN_APP
        assert offer.durationMinutes == 40
        assert offer.isDuo is True
        assert offer.bookingContact == "test@myemail.com"
        assert offer.bookingEmail == "test@myemail.com"
        assert offer.withdrawalDetails == "Here !"
        assert offer.description == "A new description"
        assert offer.idAtProvider == "oh it has been updated"
        assert offer.name == new_name

        assert db.session.query(offers_models.Mediation).one()
        assert (
            offer.image.url
            == f"{settings.OBJECT_STORAGE_URL}/thumbs/mediations/{human_ids.humanize(offer.activeMediation.id)}"
        )

    @time_machine.travel(datetime.datetime(2025, 6, 25, 12, 30, tzinfo=datetime.timezone.utc), tick=False)
    @pytest.mark.parametrize(
        "partial_request_json,expected_publication_datetime,expected_response_publication_datetime",
        [
            # should set new value
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
            # should unset previous value
            ({"publicationDatetime": None}, None, None),
            # should keep previous value
            ({}, datetime.datetime(2025, 5, 1, 3), "2025-05-01T03:00:00Z"),
        ],
    )
    def test_publication_datetime_param(
        self, partial_request_json, expected_publication_datetime, expected_response_publication_datetime
    ):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        offer = self.setup_base_resource(
            venue=venue_provider.venue,
            provider=venue_provider.provider,
            publication_datetime=datetime.datetime(2025, 5, 1, 3),
        )

        response = self.make_request(plain_api_key, {"offer_id": offer.id}, json_body=partial_request_json)

        assert response.status_code == 200
        assert response.json["publicationDatetime"] == expected_response_publication_datetime

        update_offer = db.session.query(offers_models.Offer).filter_by(id=offer.id).one()
        assert update_offer.publicationDatetime == expected_publication_datetime

    @time_machine.travel(datetime.datetime(2025, 6, 25, 12, 30, tzinfo=datetime.timezone.utc), tick=False)
    @pytest.mark.parametrize(
        "partial_request_json,expected_booking_allowed_datetime,expected_response_booking_allowed_datetime",
        [
            # should set new value
            (
                {"bookingAllowedDatetime": "2025-08-01T08:00:00+02:00"},  # tz: Europe/Paris
                datetime.datetime(2025, 8, 1, 6),  # tz: utc
                "2025-08-01T06:00:00Z",
            ),
            # should unset value
            ({"bookingAllowedDatetime": None}, None, None),
            # should keep previous value
            ({}, datetime.datetime(2025, 5, 1, 3), "2025-05-01T03:00:00Z"),
        ],
    )
    def test_booking_allowed_datetime_param(
        self, partial_request_json, expected_booking_allowed_datetime, expected_response_booking_allowed_datetime
    ):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        offer = self.setup_base_resource(
            venue=venue_provider.venue,
            provider=venue_provider.provider,
            booking_allowed_datetime=datetime.datetime(2025, 5, 1, 3),
        )

        response = self.make_request(plain_api_key, {"offer_id": offer.id}, json_body=partial_request_json)

        assert response.status_code == 200
        assert response.json["bookingAllowedDatetime"] == expected_response_booking_allowed_datetime

        update_offer = db.session.query(offers_models.Offer).filter_by(id=offer.id).one()
        assert update_offer.bookingAllowedDatetime == expected_booking_allowed_datetime

    def test_update_with_non_nullable_fields_does_not_update_them(self):
        plain_api_key, venue_provider = self.setup_active_venue_provider(provider_has_ticketing_urls=True)
        offer = offers_factories.EventOfferFactory(
            venue=venue_provider.venue,
            lastProvider=venue_provider.provider,
            publicationDatetime=datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=None)
            - datetime.timedelta(days=1),
        )

        response = self.make_request(plain_api_key, {"offer_id": offer.id}, json_body={"isActive": None})
        assert response.status_code == 200

        db.session.refresh(offer)
        assert offer.isActive

    def test_update_location_with_physical_location(self):
        plain_api_key, venue_provider = self.setup_active_venue_provider(provider_has_ticketing_urls=True)
        offer = self.setup_base_resource(venue=venue_provider.venue, provider=venue_provider.provider)

        other_venue = providers_factories.VenueProviderFactory(provider=venue_provider.provider).venue
        json_data = {"location": {"type": "physical", "venueId": other_venue.id}}

        response = self.make_request(plain_api_key, {"offer_id": offer.id}, json_body=json_data)
        assert response.status_code == 200

        assert offer.venueId == other_venue.id
        assert offer.venue.offererAddress.id == other_venue.offererAddress.id

    def test_update_location_with_digital_location(self):
        plain_api_key, venue_provider = self.setup_active_venue_provider(provider_has_ticketing_urls=True)
        venue = venue_provider.venue
        offer = self.setup_base_resource(venue=venue, provider=venue_provider.provider, digital=True)

        other_venue = offerers_factories.VirtualVenueFactory(managingOfferer=venue.managingOfferer)
        providers_factories.VenueProviderFactory(provider=venue_provider.provider, venue=other_venue)
        json_data = {"location": {"type": "digital", "venueId": other_venue.id, "url": "https://oops.fr"}}

        response = self.make_request(plain_api_key, {"offer_id": offer.id}, json_body=json_data)
        assert response.status_code == 200

        assert offer.url == "https://oops.fr"
        assert offer.venueId == other_venue.id
        assert not offer.offererAddress

    def test_update_location_with_address(self):
        plain_api_key, venue_provider = self.setup_active_venue_provider(provider_has_ticketing_urls=True)
        venue = venue_provider.venue
        offer = self.setup_base_resource(venue=venue, provider=venue_provider.provider)

        other_venue = offerers_factories.VenueFactory(managingOfferer=venue.managingOfferer)
        address = geography_factories.AddressFactory(
            latitude=50.63153,
            longitude=3.06089,
            postalCode=59000,
            city="Lille",
        )

        providers_factories.VenueProviderFactory(provider=venue_provider.provider, venue=other_venue)
        json_data = {"location": {"type": "address", "venueId": other_venue.id, "addressId": address.id}}

        response = self.make_request(plain_api_key, {"offer_id": offer.id}, json_body=json_data)
        assert response.status_code == 200

        assert offer.offererAddress.addressId == address.id

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
            ({"name": None}, {"name": ["cannot be null"]}),
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
            # additional properties not allowed
            ({"tkilol": ""}, {"tkilol": ["extra fields not permitted"]}),
        ],
    )
    def test_incorrect_payload_should_return_400(self, partial_request_json, expected_response_json):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        offers_factories.OfferFactory(venue=venue_provider.venue, idAtProvider="c'est déjà pris :'(")
        offer = self.setup_base_resource(venue=venue_provider.venue, provider=venue_provider.provider)

        response = self.make_request(plain_api_key, {"offer_id": offer.id}, json_body=partial_request_json)

        assert response.status_code == 400
        assert response.json == expected_response_json
