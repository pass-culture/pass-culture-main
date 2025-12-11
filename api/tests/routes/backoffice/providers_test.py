import re

import pytest
from flask import url_for

from pcapi.core.educational import factories as collective_offers_factories
from pcapi.core.history import models as history_models
from pcapi.core.offerers import api as offerers_api
from pcapi.core.offerers import factories as offerers_factories
from pcapi.core.offerers import models as offerers_models
from pcapi.core.offers import factories as offers_factories
from pcapi.core.permissions import models as perm_models
from pcapi.core.providers import factories as providers_factories
from pcapi.core.providers import models as providers_models
from pcapi.core.testing import assert_num_queries
from pcapi.models import db
from pcapi.models.offer_mixin import OfferValidationStatus
from pcapi.models.validation_status_mixin import ValidationStatus

from .helpers import button as button_helpers
from .helpers import html_parser
from .helpers.get import GetEndpointHelper
from .helpers.post import PostEndpointHelper


pytestmark = [
    pytest.mark.usefixtures("db_session"),
    pytest.mark.backoffice,
]


class ListProvidersTest(GetEndpointHelper):
    endpoint = "backoffice_web.providers.list_providers"
    needed_permission = perm_models.Permissions.READ_TECH_PARTNERS

    # - fetch session + user (1 query)
    # - fetch providers and associated api keys (1 query)
    expected_num_queries = 2

    def test_list_providers(self, authenticated_client):
        offerer = offerers_factories.OffererFactory(name="Aaaaaah je suis au début")
        provider = providers_factories.ProviderFactory(name=offerer.name)
        providers_factories.OffererProviderFactory(offerer=offerer, provider=provider)
        offerers_factories.ApiKeyFactory(provider=provider)

        second_offerer = offerers_factories.OffererFactory(name="Zzzzz je dors à la fin")
        second_provider = providers_factories.ProviderFactory(name=second_offerer.name)
        providers_factories.OffererProviderFactory(offerer=second_offerer, provider=second_provider)
        offerers_factories.ApiKeyFactory(provider=second_provider, prefix="other-prefix")
        providers_factories.VenueProviderFactory(provider=second_provider)
        providers_factories.VenueProviderFactory(provider=second_provider, isActive=False)

        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint))
            assert response.status_code == 200

        rows = html_parser.extract_table_rows(response.data)

        assert rows[0]["ID"] == str(provider.id)
        assert rows[0]["Partenaire technique"] == provider.name
        assert rows[0]["Partenaires culturels synchronisés au partenaire"] == "0 actif / 0 inactif"
        assert rows[0]["SIREN"] == offerer.siren
        assert rows[0]["URL du logo"] == ""
        assert rows[0]["Nombre de clés d'API"] == "1"
        assert rows[0]["Actif pour les pros"] == "Oui"
        assert rows[0]["Actif"] == "Oui"

        assert rows[-1]["ID"] == str(second_provider.id)
        assert rows[-1]["Partenaire technique"] == second_provider.name
        assert rows[-1]["Partenaires culturels synchronisés au partenaire"] == "1 actif / 1 inactif"
        assert rows[-1]["SIREN"] == second_offerer.siren
        assert rows[-1]["URL du logo"] == ""
        assert rows[-1]["Nombre de clés d'API"] == "1"
        assert rows[-1]["Actif pour les pros"] == "Oui"
        assert rows[-1]["Actif"] == "Oui"


class CreateProviderButtonTest(button_helpers.ButtonHelper):
    needed_permission = perm_models.Permissions.MANAGE_TECH_PARTNERS
    button_label = "Créer un partenaire"

    @property
    def path(self):
        return url_for("backoffice_web.providers.list_providers")


class CreateProviderTest(PostEndpointHelper):
    endpoint = "backoffice_web.providers.create_provider"
    needed_permission = perm_models.Permissions.MANAGE_TECH_PARTNERS

    def test_create_provider_and_offerer(self, authenticated_client):
        form_data = {
            "name": "Individual Offer API consumer",
            "siren": "123456789",
            "logo_url": "https://example.org/image.png",
            "booking_external_url": "https://example.org/booking",
            "cancel_external_url": "https://example.org/cancel",
            "notification_external_url": "https://example.org/notify",
            "enabled_for_pro": False,
            "is_active": True,
        }
        response = self.post_to_endpoint(authenticated_client, form_data)
        assert response.status_code == 200

        assert re.search(rf"development{offerers_api.API_KEY_SEPARATOR}\w{{77}}", response.data.decode("utf-8")), (
            "clear api key secret not found"
        )

        created_provider = (
            db.session.query(providers_models.Provider).order_by(providers_models.Provider.id.desc()).first()
        )
        assert created_provider.name == form_data["name"]
        assert created_provider.logoUrl == form_data["logo_url"]
        assert created_provider.enabledForPro == form_data["enabled_for_pro"]
        assert created_provider.isActive == form_data["is_active"]
        assert created_provider.bookingExternalUrl == form_data["booking_external_url"]
        assert created_provider.cancelExternalUrl == form_data["cancel_external_url"]
        assert created_provider.notificationExternalUrl == form_data["notification_external_url"]

        assert created_provider.offererProvider is not None
        created_offerer = created_provider.offererProvider.offerer
        assert created_offerer.name == form_data["name"]
        assert created_offerer.siren == form_data["siren"]
        assert created_offerer.validationStatus == ValidationStatus.VALIDATED
        assert created_offerer.confidenceLevel == offerers_models.OffererConfidenceLevel.MANUAL_REVIEW

        action = (
            db.session.query(history_models.ActionHistory)
            .order_by(history_models.ActionHistory.actionDate.desc())
            .first()
        )
        assert action.actionType == history_models.ActionType.FRAUD_INFO_MODIFIED
        assert action.offerer == created_offerer
        assert action.comment == "Entité juridique de provider créée manuellement depuis le BO"

    def test_create_provider(self, authenticated_client):
        offerer = offerers_factories.OffererFactory()

        form_data = {
            "name": "Individual Offer API consumer",
            "siren": offerer.siren,
            "logo_url": "https://example.org/image.png",
            "booking_external_url": "https://example.org/booking",
            "cancel_external_url": "https://example.org/cancel",
            "notification_external_url": "https://example.org/notify",
            "enabled_for_pro": False,
            "is_active": True,
        }
        response = self.post_to_endpoint(authenticated_client, form_data)
        assert response.status_code == 200

        assert re.search(rf"development{offerers_api.API_KEY_SEPARATOR}\w{{77}}", response.data.decode("utf-8")), (
            "clear api key secret not found"
        )

        created_provider = (
            db.session.query(providers_models.Provider).order_by(providers_models.Provider.id.desc()).first()
        )
        assert created_provider.name == form_data["name"]
        assert created_provider.logoUrl == form_data["logo_url"]
        assert created_provider.enabledForPro == form_data["enabled_for_pro"]
        assert created_provider.isActive == form_data["is_active"]
        assert created_provider.bookingExternalUrl == form_data["booking_external_url"]
        assert created_provider.cancelExternalUrl == form_data["cancel_external_url"]
        assert created_provider.notificationExternalUrl == form_data["notification_external_url"]

        assert db.session.query(offerers_models.Offerer).count() == 1
        assert created_provider.offererProvider.offerer == offerer
        assert offerer.name != form_data["name"]

    def test_create_provider_with_least_data(self, authenticated_client):
        offerer = offerers_factories.OffererFactory()

        form_data = {
            "name": "Individual Offer API consumer",
            "siren": offerer.siren,
            "enabled_for_pro": False,
            "is_active": True,
        }
        response = self.post_to_endpoint(authenticated_client, form_data)
        assert response.status_code == 200

        assert re.search(rf"development{offerers_api.API_KEY_SEPARATOR}\w{{77}}", response.data.decode("utf-8")), (
            "clear api key secret not found"
        )

        created_provider = (
            db.session.query(providers_models.Provider).order_by(providers_models.Provider.id.desc()).first()
        )
        assert created_provider.name == form_data["name"]
        assert created_provider.logoUrl is None
        assert created_provider.enabledForPro == form_data["enabled_for_pro"]
        assert created_provider.isActive == form_data["is_active"]
        assert created_provider.bookingExternalUrl is None
        assert created_provider.cancelExternalUrl is None
        assert created_provider.notificationExternalUrl is None

        assert db.session.query(offerers_models.Offerer).count() == 1
        assert created_provider.offererProvider.offerer == offerer
        assert offerer.name != form_data["name"]


class GetProviderTest(GetEndpointHelper):
    endpoint = "backoffice_web.providers.get_provider"
    endpoint_kwargs = {"provider_id": 1}
    needed_permission = perm_models.Permissions.READ_TECH_PARTNERS

    # get session + user (1 query)
    # get provider (1 query)
    expected_num_queries = 2

    def test_get_provider(self, authenticated_client):
        offerer = offerers_factories.OffererFactory(name="Le videur pro")
        provider = providers_factories.ProviderFactory(
            name=offerer.name,
            logoUrl="www.logo.passculture.exemple.fr",
            bookingExternalUrl="www.booking.passculture.exemple.fr",
            cancelExternalUrl="www.cancel.passculture.exemple.fr",
            notificationExternalUrl="www.notification.passculture.exemple.fr",
        )
        providers_factories.OffererProviderFactory(offerer=offerer, provider=provider)
        offerers_factories.ApiKeyFactory(provider=provider)

        url = url_for(self.endpoint, provider_id=provider.id)

        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url)
            assert response.status_code == 200

        response_text = html_parser.content_as_text(response.data)
        assert provider.name in response_text
        assert f"Provider ID : {provider.id} " in response_text
        assert f"SIREN : {offerer.siren} " in response_text
        assert "Actif : Oui " in response_text
        assert "Actif pour les pros : Oui " in response_text
        assert f"Nombre de clés d'API : {len(provider.apiKeys)} " in response_text
        assert f"URL du logo : {provider.logoUrl} " in response_text
        assert f"URL de réservation : {provider.bookingExternalUrl}" in response_text
        assert f"URL d'annulation : {provider.cancelExternalUrl}" in response_text
        assert f"URL de notification : {provider.notificationExternalUrl}" in response_text


class GetProviderStatsTest(GetEndpointHelper):
    endpoint = "backoffice_web.providers.get_stats"
    endpoint_kwargs = {"provider_id": 1}
    needed_permission = perm_models.Permissions.READ_TECH_PARTNERS

    def test_get_stats(self, authenticated_client):
        offerer = offerers_factories.OffererFactory(name="Le videur pro")
        provider = providers_factories.ProviderFactory(name=offerer.name)
        providers_factories.OffererProviderFactory(offerer=offerer, provider=provider)
        offerers_factories.ApiKeyFactory(provider=provider)

        providers_factories.VenueProviderFactory(provider=provider, isActive=False)
        providers_factories.VenueProviderFactory(provider=provider, isActive=False)

        url = url_for(self.endpoint, provider_id=provider.id)

        # get session + user (1 query)
        # get provider counts (1 query)
        with assert_num_queries(2):
            response = authenticated_client.get(url)
            assert response.status_code == 200

        cards_text = html_parser.extract_cards_text(response.data)
        assert (
            "0 partenaire culturel avec une synchronisation active 2 partenaires culturels avec une synchronisation inactive"
            in cards_text
        )

        providers_factories.VenueProviderFactory(provider=provider, isActive=True)

        url = url_for(self.endpoint, provider_id=provider.id)

        # get session + user (1 query)
        # get provider counts (1 query)
        with assert_num_queries(2):
            response = authenticated_client.get(url)
            assert response.status_code == 200

        cards_text = html_parser.extract_cards_text(response.data)
        assert (
            "1 partenaire culturel avec une synchronisation active 2 partenaires culturels avec une synchronisation inactive"
            in cards_text
        )


class GetProviderVenuesTest(GetEndpointHelper):
    endpoint = "backoffice_web.providers.get_venues"
    endpoint_kwargs = {"provider_id": 1}
    needed_permission = perm_models.Permissions.READ_TECH_PARTNERS

    # - session + authenticated user (1 query)
    # - venues with joined data (1 query)
    expected_num_queries = 2

    def test_get_linked_venues(self, authenticated_client):
        offerer = offerers_factories.OffererFactory(name="Le videur pro")
        provider = providers_factories.ProviderFactory(name=offerer.name)
        providers_factories.OffererProviderFactory(offerer=offerer, provider=provider)
        offerers_factories.ApiKeyFactory(provider=provider)

        venue_1 = offerers_factories.VenueFactory(publicName="À la synchro active")
        providers_factories.VenueProviderFactory(venue=venue_1, provider=provider, isActive=True)
        venue_2 = offerers_factories.VenueFactory(publicName="À la synchro inactive")
        providers_factories.VenueProviderFactory(venue=venue_2, provider=provider, isActive=False)
        venue_with_other_provider = offerers_factories.VenueFactory(name="À la synchro perdue")
        providers_factories.VenueProviderFactory(venue=venue_with_other_provider, isActive=True)

        url = url_for(self.endpoint, provider_id=provider.id)

        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url)
            assert response.status_code == 200

        rows = html_parser.extract_table_rows(response.data)
        assert len(rows) == 2

        # Sort before checking rows data to avoid flaky test
        rows = sorted(rows, key=lambda row: row["Nom"])

        assert rows[0]["ID"] == str(venue_1.id)
        assert rows[0]["Nom"] == venue_1.publicName

        assert rows[1]["ID"] == str(venue_2.id)
        assert rows[1]["Nom"] == venue_2.publicName


class UpdateProviderButtonTest(button_helpers.ButtonHelper):
    needed_permission = perm_models.Permissions.MANAGE_TECH_PARTNERS
    button_label = "Modifier les informations"

    @property
    def path(self):
        provider = providers_factories.ProviderFactory()
        return url_for("backoffice_web.providers.get_provider", provider_id=provider.id)


class UpdateProviderTest(PostEndpointHelper):
    endpoint = "backoffice_web.providers.update_provider"
    endpoint_kwargs = {"provider_id": 1}
    needed_permission = perm_models.Permissions.MANAGE_TECH_PARTNERS

    def test_update_provider(self, authenticated_client):
        provider = providers_factories.ProviderFactory()
        offerer = offerers_factories.OffererFactory()
        providers_factories.OffererProviderFactory(offerer=offerer, provider=provider)

        form_data = {
            "name": "Individual Offer API consumer",
            "logo_url": "https://example.org/image.png",
            "booking_external_url": "https://example.org/booking",
            "cancel_external_url": "https://example.org/cancel",
            "notification_external_url": "https://example.org/notify",
            "enabled_for_pro": False,
            "is_active": True,
        }
        response = self.post_to_endpoint(authenticated_client, form_data, provider_id=provider.id)
        assert response.status_code == 303
        redirected_response = authenticated_client.get(response.headers["location"])

        created_provider_alert = html_parser.extract_alert(redirected_response.data)
        assert created_provider_alert == "Les informations ont été mises à jour"

        updated_provider = db.session.query(providers_models.Provider).filter_by(id=provider.id).one()
        assert updated_provider.name == form_data["name"]
        assert updated_provider.logoUrl == form_data["logo_url"]
        assert updated_provider.enabledForPro == form_data["enabled_for_pro"]
        assert updated_provider.isActive == form_data["is_active"]
        assert updated_provider.bookingExternalUrl == form_data["booking_external_url"]
        assert updated_provider.cancelExternalUrl == form_data["cancel_external_url"]
        assert updated_provider.notificationExternalUrl == form_data["notification_external_url"]
        assert not updated_provider.apiKeys

        assert offerer.name != form_data["name"]

    def test_update_provider_with_minimal_data(self, authenticated_client):
        provider = providers_factories.ProviderFactory()
        offerer = offerers_factories.OffererFactory()
        providers_factories.OffererProviderFactory(offerer=offerer, provider=provider)

        form_data = {
            "name": "Individual Offer API consumer",
            "enabled_for_pro": False,
            "is_active": True,
        }
        response = self.post_to_endpoint(authenticated_client, form_data, provider_id=provider.id)
        assert response.status_code == 303
        redirected_response = authenticated_client.get(response.headers["location"])

        created_provider_alert = html_parser.extract_alert(redirected_response.data)
        assert created_provider_alert == "Les informations ont été mises à jour"

        updated_provider = db.session.query(providers_models.Provider).filter_by(id=provider.id).one()
        assert updated_provider.name == form_data["name"]
        assert updated_provider.logoUrl is None
        assert updated_provider.enabledForPro == form_data["enabled_for_pro"]
        assert updated_provider.isActive == form_data["is_active"]
        assert updated_provider.bookingExternalUrl is None
        assert updated_provider.cancelExternalUrl is None
        assert updated_provider.notificationExternalUrl is None
        assert not updated_provider.apiKeys

        assert offerer.name != form_data["name"]

    def test_disable_offer_when_disabling_provider(self, authenticated_client):
        provider = providers_factories.ProviderFactory()
        offerer = offerers_factories.OffererFactory()
        providers_factories.OffererProviderFactory(offerer=offerer, provider=provider)

        venue_provider_1 = providers_factories.VenueProviderFactory(provider=provider)
        offer_1_1 = offers_factories.OfferFactory(venue=venue_provider_1.venue, lastProvider=provider, isActive=True)

        venue_provider_2 = providers_factories.VenueProviderFactory(provider=provider)
        offer_2_1 = offers_factories.OfferFactory(venue=venue_provider_2.venue, lastProvider=provider, isActive=True)
        offer_2_2 = offers_factories.OfferFactory(venue=venue_provider_2.venue, lastProvider=provider, isActive=True)

        collective_offer_1_1 = collective_offers_factories.CollectiveOfferFactory(
            venue=venue_provider_1.venue, provider=provider, isActive=True, validation=OfferValidationStatus.APPROVED
        )
        collective_offer_1_2 = collective_offers_factories.CollectiveOfferFactory(
            venue=venue_provider_1.venue, provider=provider, isActive=True
        )
        collective_offer_2_1 = collective_offers_factories.CollectiveOfferFactory(
            venue=venue_provider_2.venue, provider=provider, isActive=True
        )

        form_data = {
            "name": "Individual Offer API consumer",
            "enabled_for_pro": False,
        }
        response = self.post_to_endpoint(authenticated_client, form_data, provider_id=provider.id)
        assert response.status_code == 303
        redirected_response = authenticated_client.get(response.headers["location"])

        created_provider_alert = html_parser.extract_alert(redirected_response.data)
        assert created_provider_alert == "Les informations ont été mises à jour"

        updated_provider = db.session.query(providers_models.Provider).filter_by(id=provider.id).one()
        assert updated_provider.isActive == False
        assert venue_provider_1.isActive == False
        assert offer_1_1.isActive == False
        assert venue_provider_2.isActive == False
        assert offer_2_1.isActive == False
        assert offer_2_2.isActive == False
        assert collective_offer_1_1.isActive == False
        assert collective_offer_1_2.isActive == False
        assert collective_offer_2_1.isActive == False
