import pytest

from pcapi import settings
from pcapi.core.offerers import factories as offerers_factories
from pcapi.core.offers import factories as offers_factories
from pcapi.core.offers import models as offers_models
from pcapi.utils import human_ids

from tests.routes import image_data

from . import utils


@pytest.mark.usefixtures("db_session")
class PatchEventTest:
    def test_deactivate_offer(self, client):
        venue, api_key = utils.create_offerer_provider_linked_to_venue()
        event_offer = offers_factories.EventOfferFactory(venue=venue, isActive=True, lastProvider=api_key.provider)

        response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).patch(
            f"/public/offers/v1/events/{event_offer.id}",
            json={"isActive": False},
        )

        assert response.status_code == 200
        assert response.json["status"] == "INACTIVE"
        assert event_offer.isActive is False

    def test_sets_field_to_none_and_leaves_other_unchanged(self, client):
        venue, api_key = utils.create_offerer_provider_linked_to_venue()
        event_offer = offers_factories.EventOfferFactory(
            subcategoryId="CONCERT",
            venue=venue,
            withdrawalDetails="Des conditions de retrait sur la sellette",
            withdrawalType=offers_models.WithdrawalTypeEnum.BY_EMAIL,
            withdrawalDelay=86400,
            bookingContact="contact@example.com",
            bookingEmail="notify@example.com",
            lastProvider=api_key.provider,
        )

        response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).patch(
            f"/public/offers/v1/events/{event_offer.id}",
            json={"itemCollectionDetails": None},
        )

        assert response.status_code == 200
        assert response.json["itemCollectionDetails"] is None
        assert event_offer.withdrawalDetails is None
        assert event_offer.bookingEmail == "notify@example.com"
        assert event_offer.withdrawalType == offers_models.WithdrawalTypeEnum.BY_EMAIL
        assert event_offer.withdrawalDelay == 86400

    def test_sets_accessibility_partially(self, client):
        venue, api_key = utils.create_offerer_provider_linked_to_venue()
        event_offer = offers_factories.EventOfferFactory(
            venue=venue,
            audioDisabilityCompliant=True,
            mentalDisabilityCompliant=True,
            motorDisabilityCompliant=True,
            visualDisabilityCompliant=True,
            lastProvider=api_key.provider,
        )

        response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).patch(
            f"/public/offers/v1/events/{event_offer.id}",
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
        venue, api_key = utils.create_offerer_provider_linked_to_venue()
        event_offer = offers_factories.EventOfferFactory(
            venue=venue,
            subcategoryId="FESTIVAL_ART_VISUEL",
            extraData={
                "author": "Maurice",
                "stageDirector": "Robert",
                "performer": "Pink Pâtisserie",
            },
            lastProvider=api_key.provider,
        )

        response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).patch(
            f"/public/offers/v1/events/{event_offer.id}",
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

    def test_patch_all_fields(self, client):
        venue, api_key = utils.create_offerer_provider_linked_to_venue(with_ticketing_service_at_provider_level=True)
        event_offer = offers_factories.EventOfferFactory(
            venue=venue,
            bookingContact="contact@example.com",
            bookingEmail="notify@passq.com",
            subcategoryId="CONCERT",
            durationMinutes=20,
            isDuo=False,
            lastProvider=api_key.provider,
            withdrawalType=offers_models.WithdrawalTypeEnum.IN_APP,
            withdrawalDelay=86400,
            withdrawalDetails="Around there",
            description="A description",
        )

        response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).patch(
            f"/public/offers/v1/events/{event_offer.id}",
            json={
                "bookingContact": "test@myemail.com",
                "bookingEmail": "test@myemail.com",
                "eventDuration": 40,
                "enableDoubleBookings": "true",
                "itemCollectionDetails": "Here !",
                "description": "A new description",
                "image": {"file": image_data.GOOD_IMAGE},
                "idAtProvider": "oh it has been updated",
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

        assert offers_models.Mediation.query.one()
        assert (
            event_offer.image.url
            == f"{settings.OBJECT_STORAGE_URL}/thumbs/mediations/{human_ids.humanize(event_offer.activeMediation.id)}"
        )


@pytest.mark.usefixtures("db_session")
class PatchEventReturns404Test:
    def test_edit_product_offer(self, client):
        _, api_key = utils.create_offerer_provider_linked_to_venue()
        thing_offer = offers_factories.ThingOfferFactory(
            venue__managingOfferer=api_key.offerer, isActive=True, lastProvider=api_key.provider
        )

        response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).patch(
            f"/public/offers/v1/events/{thing_offer.id}",
            json={"isActive": False},
        )

        assert response.status_code == 404
        assert thing_offer.isActive is True

    def test_edit_inactive_venue_provider(self, client):
        _, api_key = utils.create_offerer_provider_linked_to_venue(is_venue_provider_active=False)
        event_offer = offers_factories.EventOfferFactory(
            venue__managingOfferer=api_key.offerer, lastProvider=api_key.provider
        )

        response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).patch(
            f"/public/offers/v1/events/{event_offer.id}",
            json={"isActive": True},
        )

        assert response.status_code == 404


@pytest.mark.usefixtures("db_session")
class PatchEventReturns400Test:
    def test_edit_product_offer_with_long_description(self, client):
        _, api_key = utils.create_offerer_provider_linked_to_venue()
        thing_offer = offers_factories.ThingOfferFactory(
            venue__managingOfferer=api_key.offerer, isActive=True, lastProvider=api_key.provider
        )

        response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).patch(
            f"/public/offers/v1/events/{thing_offer.id}",
            json={"desciption": "A" * 1001},
        )

        assert response.status_code == 400
        assert response.json == {"desciption": ["extra fields not permitted"]}
