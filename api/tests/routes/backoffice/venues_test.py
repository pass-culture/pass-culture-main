# pylint: disable=redefined-outer-name
import datetime
from unittest import mock

from flask import url_for
import pytest

from pcapi.core.auth.api import generate_token
from pcapi.core.permissions.models import Permissions
from pcapi.core.testing import override_features
from pcapi.core.users import factories as users_factories

from .fixtures import *  # pylint: disable=wildcard-import, unused-wildcard-import


pytestmark = pytest.mark.usefixtures("db_session")


class GetVenueBasicInfoTest:
    @override_features(ENABLE_BACKOFFICE_API=True)
    def test_venue_detail_payload_structure(
        self,
        client,
        random_venue,
    ):
        # given
        admin = users_factories.UserFactory()
        auth_token = generate_token(admin, [Permissions.READ_PRO_ENTITY])

        # when
        response = client.with_explicit_token(auth_token).get(
            url_for("backoffice_blueprint.get_venue_basic_info", venue_id=random_venue.id)
        )

        # then
        assert response.status_code == 200
        assert "data" in response.json
        payload = response.json["data"]
        assert "id" in payload
        assert "name" in payload
        assert "siret" in payload
        assert "email" in payload
        assert "phoneNumber" in payload
        assert "region" in payload
        assert "hasReimbursementPoint" in payload
        assert "isCollectiveEligible" in payload
        assert "dms" in payload

    @override_features(ENABLE_BACKOFFICE_API=True)
    def test_venue_detail_basic_info(self, client, random_venue):
        # given
        admin = users_factories.UserFactory()
        auth_token = generate_token(admin, [Permissions.READ_PRO_ENTITY])

        # when
        response = client.with_explicit_token(auth_token).get(
            url_for("backoffice_blueprint.get_venue_basic_info", venue_id=random_venue.id)
        )

        # then
        assert response.status_code == 200
        payload = response.json["data"]
        assert payload["id"] == random_venue.id
        assert payload["name"] == random_venue.name
        assert payload["siret"] == random_venue.siret
        assert payload["isCollectiveEligible"] is False
        assert payload["email"] == random_venue.contact.email
        assert payload["phoneNumber"] == random_venue.contact.phone_number
        assert payload["region"] == "Occitanie"
        assert payload["hasReimbursementPoint"] is False

    @override_features(ENABLE_BACKOFFICE_API=True)
    def test_venue_collective_eligibility(
        self,
        client,
        venue_with_educational_status,
    ):
        # given
        admin = users_factories.UserFactory()
        auth_token = generate_token(admin, [Permissions.READ_PRO_ENTITY])

        # when
        response = client.with_explicit_token(auth_token).get(
            url_for("backoffice_blueprint.get_venue_basic_info", venue_id=venue_with_educational_status.id)
        )

        # then
        assert response.status_code == 200
        collective_eligibility = response.json["data"]["isCollectiveEligible"]
        assert collective_eligibility is True

    @override_features(ENABLE_BACKOFFICE_API=True)
    def test_venue_with_booking_email_but_no_contact(
        self,
        client,
        venue_with_no_contact,
    ):
        # given
        admin = users_factories.UserFactory()
        auth_token = generate_token(admin, [Permissions.READ_PRO_ENTITY])

        # when
        response = client.with_explicit_token(auth_token).get(
            url_for("backoffice_blueprint.get_venue_basic_info", venue_id=venue_with_no_contact.id)
        )

        # then
        assert response.status_code == 200
        assert response.json["data"]["email"] == venue_with_no_contact.bookingEmail
        assert response.json["data"]["phoneNumber"] is None

    @override_features(ENABLE_BACKOFFICE_API=True)
    def test_venue_with_nor_booking_email_neither_contact(
        self,
        client,
        venue_with_nor_contact_or_booking_email,
    ):
        # given
        admin = users_factories.UserFactory()
        auth_token = generate_token(admin, [Permissions.READ_PRO_ENTITY])

        # when
        response = client.with_explicit_token(auth_token).get(
            url_for("backoffice_blueprint.get_venue_basic_info", venue_id=venue_with_nor_contact_or_booking_email.id)
        )

        # then
        assert response.status_code == 200
        assert response.json["data"]["email"] is None
        assert response.json["data"]["phoneNumber"] is None

    @override_features(ENABLE_BACKOFFICE_API=True)
    def test_venue_with_self_reimbursement_point(
        self,
        client,
        venue_with_accepted_self_reimbursement_point,
    ):
        # given
        admin = users_factories.UserFactory()
        auth_token = generate_token(admin, [Permissions.READ_PRO_ENTITY])

        # when
        response = client.with_explicit_token(auth_token).get(
            url_for(
                "backoffice_blueprint.get_venue_basic_info", venue_id=venue_with_accepted_self_reimbursement_point.id
            )
        )

        # then
        assert response.status_code == 200
        assert response.json["data"]["hasReimbursementPoint"] is True

    @override_features(ENABLE_BACKOFFICE_API=True)
    def test_venue_with_accepted_reimbursement_point(
        self,
        client,
        venue_with_accepted_reimbursement_point,
    ):
        # given
        admin = users_factories.UserFactory()
        auth_token = generate_token(admin, [Permissions.READ_PRO_ENTITY])

        # when
        response = client.with_explicit_token(auth_token).get(
            url_for("backoffice_blueprint.get_venue_basic_info", venue_id=venue_with_accepted_reimbursement_point.id)
        )

        # then
        assert response.status_code == 200
        assert response.json["data"]["hasReimbursementPoint"] is True

    @override_features(ENABLE_BACKOFFICE_API=True)
    def test_venue_with_expired_reimbursement_point(
        self,
        client,
        venue_with_expired_reimbursement_point,
    ):
        # given
        admin = users_factories.UserFactory()
        auth_token = generate_token(admin, [Permissions.READ_PRO_ENTITY])

        # when
        response = client.with_explicit_token(auth_token).get(
            url_for("backoffice_blueprint.get_venue_basic_info", venue_id=venue_with_expired_reimbursement_point.id)
        )

        # then
        assert response.status_code == 200
        assert response.json["data"]["hasReimbursementPoint"] is False

    @override_features(ENABLE_BACKOFFICE_API=True)
    def test_venue_dms_stats(
        self,
        client,
        venue_with_draft_bank_info,
    ):
        # given
        admin = users_factories.UserFactory()
        auth_token = generate_token(admin, [Permissions.READ_PRO_ENTITY])

        with mock.patch("pcapi.connectors.dms.api.DMSGraphQLClient.get_bank_info_status") as bank_info_mock:
            bank_info_mock.return_value = {
                "dossier": {
                    "state": "en_construction",
                    "dateDepot": "2022-09-21T16:30:22+02:00",
                }
            }
            # when
            response = client.with_explicit_token(auth_token).get(
                url_for("backoffice_blueprint.get_venue_basic_info", venue_id=venue_with_draft_bank_info.id)
            )

        # then
        assert response.status_code == 200
        dms_stats = response.json["data"]["dms"]
        assert dms_stats is not None
        assert dms_stats["status"] == "en_construction"
        assert datetime.datetime.fromisoformat(dms_stats["subscriptionDate"]) == datetime.datetime.fromisoformat(
            "2022-09-21T16:30:22+02:00"
        )
        assert dms_stats["url"] == (
            "https://www.demarches-simplifiees.fr/dossiers/"
            f"{venue_with_draft_bank_info.bankInformation.applicationId}"
        )

    @override_features(ENABLE_BACKOFFICE_API=True)
    def test_venue_none_dms_stats_when_no_application_id(
        self,
        client,
        venue_with_accepted_bank_info,
    ):
        # given
        admin = users_factories.UserFactory()
        auth_token = generate_token(admin, [Permissions.READ_PRO_ENTITY])

        # when
        response = client.with_explicit_token(auth_token).get(
            url_for("backoffice_blueprint.get_venue_basic_info", venue_id=venue_with_accepted_bank_info.id)
        )

        # then
        assert response.status_code == 200
        dms_stats = response.json["data"]["dms"]
        assert dms_stats is None

    @override_features(ENABLE_BACKOFFICE_API=True)
    def test_venue_returns_404_if_venue_is_not_found(self, client):
        # given
        admin = users_factories.UserFactory()
        auth_token = generate_token(admin, [Permissions.READ_PRO_ENTITY])

        # when
        response = client.with_explicit_token(auth_token).get(
            url_for("backoffice_blueprint.get_venue_basic_info", venue_id=42)
        )

        # then
        assert response.status_code == 404

    @override_features(ENABLE_BACKOFFICE_API=True)
    def test_cannot_get_venue_without_permission(self, client, random_venue):
        # given
        user = users_factories.UserFactory()
        auth_token = generate_token(user, [])

        # when
        response = client.with_explicit_token(auth_token).get(
            url_for("backoffice_blueprint.get_venue_basic_info", venue_id=random_venue.id)
        )

        # then
        assert response.status_code == 403

    @override_features(ENABLE_BACKOFFICE_API=True)
    def test_cannot_get_venue_as_anonymous(self, client, random_venue):
        # given
        auth_token = generate_token(users_factories.UserFactory.build(), [Permissions.READ_PRO_ENTITY])

        # when
        response = client.with_explicit_token(auth_token).get(
            url_for("backoffice_blueprint.get_venue_basic_info", venue_id=random_venue.id)
        )

        # then
        assert response.status_code == 403


class GetVenueTotalRevenueTest:
    @override_features(ENABLE_BACKOFFICE_API=True)
    def test_venue_total_revenue(
        self,
        client,
        venue_with_accepted_bank_info,
        individual_offerer_bookings,
        collective_venue_booking,
    ):
        # given
        admin = users_factories.UserFactory()
        auth_token = generate_token(admin, [Permissions.READ_PRO_ENTITY])

        # when
        response = client.with_explicit_token(auth_token).get(
            url_for("backoffice_blueprint.get_venue_total_revenue", venue_id=venue_with_accepted_bank_info.id)
        )

        # then
        assert response.status_code == 200
        assert response.json["data"] == 72.0

    @override_features(ENABLE_BACKOFFICE_API=True)
    def test_venue_total_revenue_individual_bookings_only(
        self,
        client,
        venue_with_accepted_bank_info,
        individual_offerer_bookings,
    ):
        # given
        admin = users_factories.UserFactory()
        auth_token = generate_token(admin, [Permissions.READ_PRO_ENTITY])

        # when
        response = client.with_explicit_token(auth_token).get(
            url_for("backoffice_blueprint.get_venue_total_revenue", venue_id=venue_with_accepted_bank_info.id)
        )

        # then
        assert response.status_code == 200
        assert response.json["data"] == 30.0

    @override_features(ENABLE_BACKOFFICE_API=True)
    def test_venue_total_revenue_collective_bookings_only(
        self,
        client,
        venue_with_accepted_bank_info,
        collective_venue_booking,
    ):
        # given
        admin = users_factories.UserFactory()
        auth_token = generate_token(admin, [Permissions.READ_PRO_ENTITY])

        # when
        response = client.with_explicit_token(auth_token).get(
            url_for("backoffice_blueprint.get_venue_total_revenue", venue_id=venue_with_accepted_bank_info.id)
        )

        # then
        assert response.status_code == 200
        assert response.json["data"] == 42.0

    @override_features(ENABLE_BACKOFFICE_API=True)
    def test_venue_total_revenue_no_booking(
        self,
        client,
        venue_with_accepted_bank_info,
    ):
        # given
        admin = users_factories.UserFactory()
        auth_token = generate_token(admin, [Permissions.READ_PRO_ENTITY])

        # when
        response = client.with_explicit_token(auth_token).get(
            url_for("backoffice_blueprint.get_venue_total_revenue", venue_id=venue_with_accepted_bank_info.id)
        )

        # then
        assert response.status_code == 200
        assert response.json["data"] == 0.0

    @override_features(ENABLE_BACKOFFICE_API=True)
    def test_revenue_returns_0_if_venue_is_not_found(self, client):
        # given
        admin = users_factories.UserFactory()
        auth_token = generate_token(admin, [Permissions.READ_PRO_ENTITY])

        # when
        response = client.with_explicit_token(auth_token).get(
            url_for("backoffice_blueprint.get_venue_total_revenue", venue_id=42)
        )

        # then
        assert response.status_code == 200
        assert response.json["data"] == 0

    @override_features(ENABLE_BACKOFFICE_API=True)
    def test_cannot_get_venue_without_permission(self, client):
        # given
        user = users_factories.UserFactory()
        auth_token = generate_token(user, [])

        # when
        response = client.with_explicit_token(auth_token).get(
            url_for("backoffice_blueprint.get_venue_total_revenue", venue_id=42)
        )

        # then
        assert response.status_code == 403

    @override_features(ENABLE_BACKOFFICE_API=True)
    def test_cannot_get_venue_as_anonymous(self, client, venue_with_accepted_bank_info):
        # given
        auth_token = generate_token(users_factories.UserFactory.build(), [Permissions.READ_PRO_ENTITY])

        # when
        response = client.with_explicit_token(auth_token).get(
            url_for("backoffice_blueprint.get_venue_total_revenue", venue_id=venue_with_accepted_bank_info.id)
        )

        # then
        assert response.status_code == 403


class GetVenueOffersStatsTest:
    @override_features(ENABLE_BACKOFFICE_API=True)
    def test_venue_offers_stats(
        self,
        client,
        venue_with_accepted_bank_info,
        offerer_active_individual_offers,
        offerer_inactive_individual_offers,
        offerer_active_collective_offers,
        offerer_inactive_collective_offers,
    ):
        # given
        admin = users_factories.UserFactory()
        auth_token = generate_token(admin, [Permissions.READ_PRO_ENTITY])

        # when
        response = client.with_explicit_token(auth_token).get(
            url_for("backoffice_blueprint.get_venue_offers_stats", venue_id=venue_with_accepted_bank_info.id)
        )

        # then
        assert response.status_code == 200
        offer_stats = response.json["data"]
        assert offer_stats["active"]["individual"] == 3
        assert offer_stats["active"]["collective"] == 5
        assert offer_stats["inactive"]["individual"] == 4
        assert offer_stats["inactive"]["collective"] == 6
        assert offer_stats["lastSync"]["date"] == None
        assert offer_stats["lastSync"]["provider"] == None

    @override_features(ENABLE_BACKOFFICE_API=True)
    def test_venue_offers_stats_with_sync(
        self,
        client,
        venue_provider_with_last_sync,
        offerer_active_individual_offers,
        offerer_inactive_individual_offers,
        offerer_active_collective_offers,
        offerer_inactive_collective_offers,
    ):
        # given
        admin = users_factories.UserFactory()
        auth_token = generate_token(admin, [Permissions.READ_PRO_ENTITY])

        # when
        response = client.with_explicit_token(auth_token).get(
            url_for("backoffice_blueprint.get_venue_offers_stats", venue_id=venue_provider_with_last_sync.venue.id)
        )

        # then
        assert response.status_code == 200
        offer_stats = response.json["data"]
        assert offer_stats["active"]["individual"] == 3
        assert offer_stats["active"]["collective"] == 5
        assert offer_stats["inactive"]["individual"] == 4
        assert offer_stats["inactive"]["collective"] == 6
        assert offer_stats["lastSync"]["date"] == venue_provider_with_last_sync.lastSyncDate.isoformat()
        assert offer_stats["lastSync"]["provider"] == venue_provider_with_last_sync.provider.name

    @override_features(ENABLE_BACKOFFICE_API=True)
    def test_venue_offers_stats_0_if_no_offer(
        self,
        client,
        venue_with_accepted_bank_info,
    ):
        # given
        admin = users_factories.UserFactory()
        auth_token = generate_token(admin, [Permissions.READ_PRO_ENTITY])

        # when
        response = client.with_explicit_token(auth_token).get(
            url_for("backoffice_blueprint.get_venue_offers_stats", venue_id=venue_with_accepted_bank_info.id)
        )

        # then
        assert response.status_code == 200
        offer_stats = response.json["data"]
        assert offer_stats["active"]["individual"] == 0
        assert offer_stats["active"]["collective"] == 0
        assert offer_stats["inactive"]["individual"] == 0
        assert offer_stats["inactive"]["collective"] == 0
        assert offer_stats["lastSync"]["date"] == None
        assert offer_stats["lastSync"]["provider"] == None

    @override_features(ENABLE_BACKOFFICE_API=True)
    def test_404_if_venue_not_found(
        self,
        client,
    ):
        # given
        admin = users_factories.UserFactory()
        auth_token = generate_token(admin, [Permissions.READ_PRO_ENTITY])

        # when
        response = client.with_explicit_token(auth_token).get(
            url_for("backoffice_blueprint.get_venue_offers_stats", venue_id=42)
        )

        # then
        assert response.status_code == 404

    @override_features(ENABLE_BACKOFFICE_API=True)
    def test_cannot_get_venue_offers_stats_without_permission(self, client):
        # given
        user = users_factories.UserFactory()
        auth_token = generate_token(user, [])

        # when
        response = client.with_explicit_token(auth_token).get(
            url_for("backoffice_blueprint.get_venue_offers_stats", venue_id=42)
        )

        # then
        assert response.status_code == 403

    @override_features(ENABLE_BACKOFFICE_API=True)
    def test_cannot_get_venue_offers_stats_as_anonymous(self, client, random_venue):
        # given
        auth_token = generate_token(users_factories.UserFactory.build(), [Permissions.READ_PRO_ENTITY])

        # when
        response = client.with_explicit_token(auth_token).get(
            url_for("backoffice_blueprint.get_venue_offers_stats", venue_id=random_venue.id)
        )

        # then
        assert response.status_code == 403
