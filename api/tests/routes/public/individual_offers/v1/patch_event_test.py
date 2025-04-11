import pytest

from pcapi import settings
from pcapi.core.geography import factories as geography_factories
from pcapi.core.offerers import factories as offerers_factories
from pcapi.core.offers import factories as offers_factories
from pcapi.core.offers import models as offers_models
from pcapi.core.providers import factories as providers_factories
from pcapi.models import db
from pcapi.utils import human_ids

from tests.conftest import TestClient
from tests.routes import image_data
from tests.routes.public.helpers import PublicAPIVenueEndpointHelper


@pytest.mark.usefixtures("db_session")
class PatchEventTest(PublicAPIVenueEndpointHelper):
    endpoint_url = "/public/offers/v1/events/{event_id}"
    endpoint_method = "patch"
    default_path_params = {"event_id": 1}

    def setup_base_resource(self, venue=None, provider=None, digital=False) -> offers_models.Offer:
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

        if digital:
            return offers_factories.DigitalOfferFactory(
                **shared_data,
                subcategoryId="LIVESTREAM_MUSIQUE",
            )
        return offers_factories.EventOfferFactory(
            **shared_data,
            subcategoryId="CONCERT",
            extraData={"gtl_id": "02000000"},
        )

    def test_should_raise_404_because_has_no_access_to_venue(self, client: TestClient):
        plain_api_key, _ = self.setup_provider()
        event_offer = self.setup_base_resource()
        response = client.with_explicit_token(plain_api_key).patch(self.endpoint_url.format(event_id=event_offer.id))
        assert response.status_code == 404

    def test_should_raise_404_because_venue_provider_is_inactive(self, client: TestClient):
        plain_api_key, venue_provider = self.setup_inactive_venue_provider()
        event_offer = self.setup_base_resource(venue=venue_provider.venue, provider=venue_provider.provider)
        response = client.with_explicit_token(plain_api_key).patch(self.endpoint_url.format(event_id=event_offer.id))
        assert response.status_code == 404

    def test_deactivate_offer(self, client):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        event_offer = self.setup_base_resource(venue=venue_provider.venue, provider=venue_provider.provider)

        response = client.with_explicit_token(plain_api_key).patch(
            self.endpoint_url.format(event_id=event_offer.id),
            json={"isActive": False},
        )

        assert response.status_code == 200
        assert response.json["status"] == "INACTIVE"
        assert event_offer.isActive is False

    def test_sets_field_to_none_and_leaves_other_unchanged(self, client):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        event_offer = offers_factories.EventOfferFactory(
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

        response = client.with_explicit_token(plain_api_key).patch(
            self.endpoint_url.format(event_id=event_offer.id),
            json={"itemCollectionDetails": None},
        )

        assert response.status_code == 200
        assert response.json["itemCollectionDetails"] is None
        assert event_offer.withdrawalDetails is None
        assert event_offer.bookingEmail == "notify@example.com"
        assert event_offer.withdrawalType == offers_models.WithdrawalTypeEnum.BY_EMAIL
        assert event_offer.withdrawalDelay == 86400

    def test_sets_accessibility_partially(self, client):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        event_offer = offers_factories.EventOfferFactory(
            venue=venue_provider.venue,
            audioDisabilityCompliant=True,
            mentalDisabilityCompliant=True,
            motorDisabilityCompliant=True,
            visualDisabilityCompliant=True,
            lastProvider=venue_provider.provider,
        )

        response = client.with_explicit_token(plain_api_key).patch(
            self.endpoint_url.format(event_id=event_offer.id),
            json={"accessibility": {"audioDisabilityCompliant": False}},
        )

        assert response.status_code == 200
        assert response.json["accessibility"] == {
            "audioDisabilityCompliant": False,
            "mentalDisabilityCompliant": True,
            "motorDisabilityCompliant": True,
            "visualDisabilityCompliant": True,
        }
        assert event_offer.audioDisabilityCompliant is False
        assert event_offer.mentalDisabilityCompliant is True
        assert event_offer.motorDisabilityCompliant is True
        assert event_offer.visualDisabilityCompliant is True

    def test_update_extra_data_partially(self, client):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        event_offer = offers_factories.EventOfferFactory(
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

        response = client.with_explicit_token(plain_api_key).patch(
            self.endpoint_url.format(event_id=event_offer.id),
            json={
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
        assert event_offer.extraData == {
            "author": "Maurice",
            "performer": "Pink Pâtisserie",
            "stageDirector": "Robert",
        }

    def test_should_update_extra_data_even_if_extra_data_has_an_empty_stage_director(self, client):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        event_offer = offers_factories.EventOfferFactory(
            venue=venue_provider.venue,
            subcategoryId="FESTIVAL_ART_VISUEL",
            extraData={
                "author": "Maurice",
                "stageDirector": "",
                "performer": "Pink Pâtisserie",
            },
            lastProvider=venue_provider.provider,
            withdrawalDelay=86400,
            withdrawalType=offers_models.WithdrawalTypeEnum.BY_EMAIL,
            bookingContact="contact@example.com",
            bookingEmail="notify@example.com",
        )

        response = client.with_explicit_token(plain_api_key).patch(
            self.endpoint_url.format(event_id=event_offer.id),
            json={
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
        assert event_offer.extraData == {
            "author": "Maurice",
            "performer": "Pink Pâtisserie",
            "stageDirector": "",
        }
        assert not event_offer.ean

    def test_patch_all_fields(self, client):
        plain_api_key, venue_provider = self.setup_active_venue_provider(provider_has_ticketing_urls=True)
        event_offer = offers_factories.EventOfferFactory(
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

        new_name = event_offer.name + "_updated"
        response = client.with_explicit_token(plain_api_key).patch(
            self.endpoint_url.format(event_id=event_offer.id),
            json={
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
        assert event_offer.withdrawalType == offers_models.WithdrawalTypeEnum.IN_APP
        assert event_offer.durationMinutes == 40
        assert event_offer.isDuo is True
        assert event_offer.bookingContact == "test@myemail.com"
        assert event_offer.bookingEmail == "test@myemail.com"
        assert event_offer.withdrawalDetails == "Here !"
        assert event_offer.description == "A new description"
        assert event_offer.idAtProvider == "oh it has been updated"
        assert event_offer.name == new_name

        assert offers_models.Mediation.query.one()
        assert (
            event_offer.image.url
            == f"{settings.OBJECT_STORAGE_URL}/thumbs/mediations/{human_ids.humanize(event_offer.activeMediation.id)}"
        )

    def test_should_return_400_because_of_invalid_fields_name(self, client):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        event_offer = self.setup_base_resource(venue=venue_provider.venue, provider=venue_provider.provider)

        response = client.with_explicit_token(plain_api_key).patch(
            self.endpoint_url.format(event_id=event_offer.id), json={"desciption": "A"}
        )

        assert response.status_code == 400
        assert response.json == {"desciption": ["extra fields not permitted"]}

    def test_should_return_400_because_id_at_provider_already_taken(self, client):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        event_offer = self.setup_base_resource(venue=venue_provider.venue, provider=venue_provider.provider)
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

        response = client.with_explicit_token(plain_api_key).patch(
            self.endpoint_url.format(event_id=event_offer.id), json={"idAtProvider": id_at_provider}
        )

        assert response.status_code == 400
        assert response.json == {"idAtProvider": ["`rolala` is already taken by another venue offer"]}

    def test_update_with_non_nullable_fields_does_not_update_them(self, client):
        plain_api_key, venue_provider = self.setup_active_venue_provider(provider_has_ticketing_urls=True)
        event_offer = offers_factories.EventOfferFactory(
            venue=venue_provider.venue,
            lastProvider=venue_provider.provider,
            isActive=True,
        )

        response = client.with_explicit_token(plain_api_key).patch(
            self.endpoint_url.format(event_id=event_offer.id),
            json={"isActive": None},
        )

        assert response.status_code == 200

        db.session.refresh(event_offer)
        assert event_offer.isActive

    def test_update_location_with_physical_location(self, client):
        plain_api_key, venue_provider = self.setup_active_venue_provider(provider_has_ticketing_urls=True)
        event = self.setup_base_resource(venue=venue_provider.venue, provider=venue_provider.provider)

        other_venue = providers_factories.VenueProviderFactory(provider=venue_provider.provider).venue
        json_data = {"location": {"type": "physical", "venueId": other_venue.id}}

        response = self.send_update_request(client, plain_api_key, event, json_data)
        assert response.status_code == 200

        db.session.refresh(event)

        assert event.venueId == other_venue.id
        assert event.venue.offererAddress.id == other_venue.offererAddress.id

    def test_update_location_with_digital_location(self, client):
        plain_api_key, venue_provider = self.setup_active_venue_provider(provider_has_ticketing_urls=True)
        venue = venue_provider.venue
        event = self.setup_base_resource(venue=venue, provider=venue_provider.provider, digital=True)

        other_venue = offerers_factories.VirtualVenueFactory(managingOfferer=venue.managingOfferer)
        providers_factories.VenueProviderFactory(provider=venue_provider.provider, venue=other_venue)
        json_data = {"location": {"type": "digital", "venueId": other_venue.id, "url": "https://oops.fr"}}

        response = self.send_update_request(client, plain_api_key, event, json_data)
        assert response.status_code == 200

        db.session.refresh(event)

        assert event.url == "https://oops.fr"
        assert event.venueId == other_venue.id
        assert not event.offererAddress

    def test_update_location_with_address(self, client):
        plain_api_key, venue_provider = self.setup_active_venue_provider(provider_has_ticketing_urls=True)
        venue = venue_provider.venue
        event = self.setup_base_resource(venue=venue, provider=venue_provider.provider)

        other_venue = offerers_factories.VenueFactory(managingOfferer=venue.managingOfferer)
        address = geography_factories.AddressFactory(
            latitude=50.63153,
            longitude=3.06089,
            postalCode=59000,
            city="Lille",
        )

        providers_factories.VenueProviderFactory(provider=venue_provider.provider, venue=other_venue)
        json_data = {
            "location": {
                "type": "address",
                "venueId": other_venue.id,
                "addressId": address.id,
            }
        }

        response = self.send_update_request(client, plain_api_key, event, json_data)
        assert response.status_code == 200

        db.session.refresh(event)
        assert event.offererAddress.addressId == address.id

    def send_update_request(self, client, plain_api_key, event, json_data):
        url = self.endpoint_url.format(event_id=event.id)
        return client.with_explicit_token(plain_api_key).patch(
            url,
            json=json_data,
        )
