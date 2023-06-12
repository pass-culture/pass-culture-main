from flask import url_for
import pytest

import pcapi.core.bookings.factories as bookings_factories
import pcapi.core.bookings.models as bookings_models
import pcapi.core.fraud.factories as fraud_factories
import pcapi.core.fraud.models as fraud_models
import pcapi.core.history.factories as history_factories
import pcapi.core.history.models as history_models
import pcapi.core.permissions.models as perm_models
from pcapi.core.testing import assert_num_queries
import pcapi.core.users.factories as users_factories
from pcapi.models import db
from pcapi.routes.backoffice_v3.fraud import _blacklist_domain_name

from .helpers import html_parser
from .helpers.get import GetEndpointHelper
from .helpers.post import PostEndpointHelper


pytestmark = [
    pytest.mark.usefixtures("db_session"),
    pytest.mark.backoffice_v3,
]


class ListBlacklistedDomainNamesTest(GetEndpointHelper):
    endpoint = "backoffice_v3_web.fraud.list_blacklisted_domain_names"
    needed_permission = perm_models.Permissions.BENEFICIARY_FRAUD_ACTIONS

    def test_list_blacklisted_domain_names(self, authenticated_client):
        user = users_factories.BeneficiaryGrant18Factory(email="user@example.fr")
        domain = "example.fr"

        event_extra = {
            "domain": domain,
            "deactivated_users": [{"user_id": user.id, "email": user.email}],
            "cancelled_bookings_count": 2,
        }
        history_factories.BlacklistDomainNameFactory(extraData=event_extra)
        fraud_factories.BlacklistedDomainNameFactory.create_batch(2)

        url = url_for("backoffice_v3_web.fraud.list_blacklisted_domain_names")

        # get session (1 query)
        # get user with profile and permissions (1 query)
        # get history (1 query)
        # get blacklisted domains (1 query)
        with assert_num_queries(4):
            response = authenticated_client.get(url)
            assert response.status_code == 200

        response_text = html_parser.content_as_text(response.data)

        assert domain in response_text
        assert "Un compte suspendu" in response_text
        assert "2 réservations annulées" in response_text


class PrepareBlacklistDomainNamesTest(GetEndpointHelper):
    endpoint = "backoffice_v3_web.fraud.prepare_blacklist_domain_name"
    needed_permission = perm_models.Permissions.BENEFICIARY_FRAUD_ACTIONS

    def test_prepare_blacklist_domain_name(self, authenticated_client):
        user = users_factories.BeneficiaryGrant18Factory(email="user@example.fr")
        domain = "example.fr"

        url = url_for("backoffice_v3_web.fraud.prepare_blacklist_domain_name", domain=domain)

        # get session (1 query)
        # get user with profile and permissions (1 query)
        # get beneficiary emails (1 query)
        # get pro users emails (1 query)
        with assert_num_queries(4):
            response = authenticated_client.get(url)
            assert response.status_code == 200

        response_text = html_parser.content_as_text(response.data)

        assert user.email in response_text
        assert "un compte sera désactivé" in response_text


class BlacklistDomainNameTest(PostEndpointHelper):
    endpoint = "backoffice_v3_web.fraud.blacklist_domain_name"
    endpoint_kwargs = {"domain": "example.fr"}
    needed_permission = perm_models.Permissions.BENEFICIARY_FRAUD_ACTIONS

    def test_blacklist_domain_name(self, authenticated_client):
        user = bookings_factories.BookingFactory(user__email="user@example.fr").user
        domain = "example.fr"

        response = self.post_to_endpoint(authenticated_client, form={"domain": domain}, domain=domain)

        assert response.status_code == 302

        expected_url = url_for("backoffice_v3_web.fraud.list_blacklisted_domain_names", _external=True)
        assert response.location == expected_url

        db.session.refresh(user)
        assert not user.isActive

        # ensure the suspension action has been logged
        action = history_models.ActionHistory.query.filter_by(actionType=history_models.ActionType.USER_SUSPENDED).one()
        assert action.actionType == history_models.ActionType.USER_SUSPENDED

        fraud_action = history_models.ActionHistory.query.filter_by(
            actionType=history_models.ActionType.BLACKLIST_DOMAIN_NAME
        ).one()
        assert fraud_action.actionType == history_models.ActionType.BLACKLIST_DOMAIN_NAME
        assert fraud_action.extraData["domain"] == domain

        # ensure only those two actions have been logged
        assert history_models.ActionHistory.query.count() == 2

        # all bookings should have been cancelled
        for booking in user.userBookings:
            assert booking.status == bookings_models.BookingStatus.CANCELLED

        # ensure the domain has been blacklisted properly
        domain = fraud_models.BlacklistedDomainName.query.filter_by(domain=domain).first()
        assert domain is not None


class RemoveBlacklistedDomainNameTest(PostEndpointHelper):
    endpoint = "backoffice_v3_web.fraud.remove_blacklisted_domain_name"
    endpoint_kwargs = {"domain": "example.fr"}
    needed_permission = perm_models.Permissions.BENEFICIARY_FRAUD_ACTIONS

    def test_remove_blacklisted_domain(self, authenticated_client):
        domain = fraud_factories.BlacklistedDomainNameFactory().domain
        other_domain = fraud_factories.BlacklistedDomainNameFactory().domain

        response = self.post_to_endpoint(authenticated_client, domain=domain)

        assert response.status_code == 302

        expected_url = url_for("backoffice_v3_web.fraud.list_blacklisted_domain_names", _external=True)
        assert response.location == expected_url

        # domain is not blacklisted anymore
        assert fraud_models.BlacklistedDomainName.query.filter_by(domain=domain).first() is None

        # other domain is still blacklisted
        assert fraud_models.BlacklistedDomainName.query.filter_by(domain=other_domain).first() is not None

        # action has been logged
        action_type = history_models.ActionType.REMOVE_BLACKLISTED_DOMAIN_NAME
        assert history_models.ActionHistory.query.filter_by(actionType=action_type).one() is not None

    def test_unknown_blacklisted_domain(self, authenticated_client):
        response = self.post_to_endpoint(authenticated_client, domain="unknown.domain")
        assert response.status_code == 404


def test_blacklist_domain_name_excludes_pro_users(legit_user):
    beneficiary = users_factories.BeneficiaryGrant18Factory(email="user@example.fr")
    pro_user = users_factories.ProFactory(email="pro@example.fr")

    users, _ = _blacklist_domain_name("example.fr", legit_user)

    assert {user.id for user in users} == {beneficiary.id}

    db.session.refresh(beneficiary)
    db.session.refresh(pro_user)

    assert not beneficiary.isActive
    assert pro_user.isActive
