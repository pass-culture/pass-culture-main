import pytest

from pcapi.core.offerers import factories as offerers_factories
from pcapi.core.offers import factories as offers_factories
from pcapi.core.offers import models as offers_models
from pcapi.core.testing import override_features

from . import utils


@pytest.mark.usefixtures("db_session")
class PatchEventTest:
    def test_edit_product_offer_returns_404(self, client):
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

    @override_features(WIP_ENABLE_EVENTS_WITH_TICKETS_FOR_PUBLIC_API=True)
    def test_patch_all_fields(self, client):
        venue, api_key = utils.create_offerer_provider_linked_to_venue()
        event_offer = offers_factories.EventOfferFactory(
            venue=venue,
            bookingContact="contact@example.com",
            bookingEmail="notify@passq.com",
            subcategoryId="CONCERT",
            durationMinutes=20,
            isDuo=False,
            lastProvider=api_key.provider,
            withdrawalType=offers_models.WithdrawalTypeEnum.BY_EMAIL,
            withdrawalDelay=86400,
            withdrawalDetails="Around there",
        )

        response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).patch(
            f"/public/offers/v1/events/{event_offer.id}",
            json={
                "ticketCollection": {"way": "on_site", "minutesBeforeEvent": 60},
                "bookingContact": "test@myemail.com",
                "bookingEmail": "test@myemail.com",
                "eventDuration": 40,
                "enableDoubleBookings": "true",
                "itemCollectionDetails": "Here !",
            },
        )
        assert response.status_code == 200
        assert event_offer.withdrawalType == offers_models.WithdrawalTypeEnum.ON_SITE
        assert event_offer.withdrawalDelay == 3600
        assert event_offer.durationMinutes == 40
        assert event_offer.isDuo is True
        assert event_offer.bookingContact == "test@myemail.com"
        assert event_offer.bookingEmail == "test@myemail.com"
        assert event_offer.withdrawalDetails == "Here !"

    def test_cannot_edit_event_with_ticket_if_FF_not_active(self, client):
        # This test can be deleted with FF WIP_ENABLE_EVENTS_WITH_TICKETS_FOR_PUBLIC_API
        venue, api_key = utils.create_offerer_provider_linked_to_venue()
        event_offer = offers_factories.EventOfferFactory(
            venue=venue,
            bookingContact="contact@example.com",
            bookingEmail="notify@passq.com",
            subcategoryId="CONCERT",
            durationMinutes=20,
            isDuo=False,
            lastProvider=api_key.provider,
            withdrawalType=offers_models.WithdrawalTypeEnum.BY_EMAIL,
            withdrawalDelay=86400,
            withdrawalDetails="Around there",
        )

        response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).patch(
            f"/public/offers/v1/events/{event_offer.id}",
            json={
                "ticketCollection": {"way": "on_site", "minutesBeforeEvent": 60},
                "bookingContact": "test@myemail.com",
                "bookingEmail": "test@myemail.com",
                "eventDuration": 40,
                "enableDoubleBookings": "true",
                "itemCollectionDetails": "Here !",
            },
        )
        assert response.status_code == 400
