import datetime

import pytest

import pcapi.core.finance.factories as finance_factories
import pcapi.core.finance.models as finance_models
import pcapi.core.offerers.factories as offerers_factories
from pcapi.core.testing import assert_num_queries
import pcapi.core.users.factories as users_factories


class OfferersBankAccountTest:
    @pytest.mark.usefixtures("db_session")
    def test_user_cant_access_bank_accounts_of_offerer_it_doesnt_depends_on(self, client):
        # Given
        pro_user = users_factories.ProFactory()
        offerer_1 = offerers_factories.OffererFactory()
        offerer_2 = offerers_factories.OffererFactory()
        offerer_2_id = offerer_2.id
        offerers_factories.UserOffererFactory(user=pro_user, offerer=offerer_1)
        finance_factories.BankAccountFactory(offerer=offerer_2, isActive=True)

        # When
        http_client = client.with_session_auth(pro_user.email)

        # Fetch the session
        # Fetch the user
        # Check user permission on offerer
        with assert_num_queries(3):
            response = http_client.get(f"/offerers/{offerer_2_id}/bank-accounts")

        # Then
        assert response.status_code == 403
        assert "Vous n'avez pas les droits d'accès suffisant pour accéder à cette information." in str(response.json)

    @pytest.mark.usefixtures("db_session")
    def test_accessing_inexisting_offerer_return_proper_404_error(self, client):
        # This is a special test case for admin users as pro users would instead get a 403

        # Given
        admin = users_factories.AdminFactory()

        # When
        http_client = client.with_session_auth(admin.email)

        response = http_client.get("/offerers/42/bank-accounts")

        # Then
        assert response.status_code == 404

    @pytest.mark.usefixtures("db_session")
    def test_user_can_access_bank_accounts_page_even_if_it_doesnt_have_any(self, client):
        # Given
        pro_user = users_factories.ProFactory()
        offerer = offerers_factories.OffererFactory()
        offerers_factories.UserOffererFactory(user=pro_user, offerer=offerer)

        # When
        http_client = client.with_session_auth(pro_user.email)

        # Fetch the session
        # Fetch the user
        # Check user permission on offerer
        # Fetch offerer, bank_accounts and related/linked venues
        with assert_num_queries(4):
            response = http_client.get(f"/offerers/{offerer.id}/bank-accounts")

        # Then
        assert response.status_code == 200
        offerer_response = response.json

        bank_accounts = offerer_response["bankAccounts"]
        venues = offerer_response["managedVenues"]

        assert not bank_accounts
        assert not venues

    @pytest.mark.usefixtures("db_session")
    def test_users_offerer_can_access_its_bank_accounts(self, client):
        # Given
        _another_pro_user = users_factories.ProFactory()
        another_offerer = offerers_factories.OffererFactory()
        another_bank_account = finance_factories.BankAccountFactory(offerer=another_offerer)
        another_venue = offerers_factories.VenueFactory(managingOfferer=another_offerer)
        _another_link = offerers_factories.VenueBankAccountLinkFactory(
            venue=another_venue, bankAccount=another_bank_account
        )

        pro_user = users_factories.ProFactory()
        offerer = offerers_factories.OffererFactory()
        offerers_factories.UserOffererFactory(user=pro_user, offerer=offerer)
        expected_venue = offerers_factories.VenueFactory(managingOfferer=offerer)
        expected_bank_account = finance_factories.BankAccountFactory(offerer=offerer)

        # When
        http_client = client.with_session_auth(pro_user.email)

        # Fetch the session
        # Fetch the user
        # Check user permission on offerer
        # Fetch offerer, bank_accounts and related/linked venues
        with assert_num_queries(4):
            response = http_client.get(f"/offerers/{offerer.id}/bank-accounts")

        # Then
        assert response.status_code == 200
        offerer_response = response.json

        bank_accounts = offerer_response["bankAccounts"]
        venues = offerer_response["managedVenues"]

        assert len(bank_accounts) == 1
        bank_account = bank_accounts.pop()
        assert bank_account["label"] == expected_bank_account.label
        assert bank_account["obfuscatedIban"] == f"XXXX XXXX XXXX {expected_bank_account.iban[-4:]}"
        assert bank_account["bic"] == expected_bank_account.bic
        assert bank_account["isActive"] is True
        assert bank_account["status"] == "accepte"
        assert not bank_account["linkedVenues"]

        assert len(venues) == 1
        venue = venues.pop()
        assert venue["id"] == expected_venue.id
        assert venue["commonName"] == expected_venue.common_name
        assert venue["siret"] == expected_venue.siret
        assert not venue["bankAccountId"]

    @pytest.mark.usefixtures("db_session")
    def test_linked_venues_to_bank_accounts_are_displayed_to_users(self, client):
        # Given
        pro_user = users_factories.ProFactory()
        offerer = offerers_factories.OffererFactory()
        offerers_factories.UserOffererFactory(user=pro_user, offerer=offerer)
        expected_venue = offerers_factories.VenueFactory(managingOfferer=offerer)
        expected_bank_account = finance_factories.BankAccountFactory(offerer=offerer)
        offerers_factories.VenueBankAccountLinkFactory(
            venueId=expected_venue.id, bankAccountId=expected_bank_account.id, timespan=(datetime.datetime.utcnow(),)
        )

        # When
        http_client = client.with_session_auth(pro_user.email)

        # Fetch the session
        # Fetch the user
        # Check user permission on offerer
        # Fetch offerer, bank_accounts and related/linked venues
        with assert_num_queries(4):
            response = http_client.get(f"/offerers/{offerer.id}/bank-accounts")

        # Then
        assert response.status_code == 200
        offerer_response = response.json

        bank_accounts = offerer_response["bankAccounts"]

        assert len(bank_accounts) == 1
        bank_account = bank_accounts.pop()

        assert len(bank_account["linkedVenues"]) == 1
        linked_venue = bank_account["linkedVenues"].pop()
        assert linked_venue["id"] == expected_venue.id
        assert linked_venue["commonName"] == expected_venue.common_name

    @pytest.mark.usefixtures("db_session")
    def test_user_can_only_see_active_bank_accounts(self, client):
        # Given
        pro_user = users_factories.ProFactory()
        offerer = offerers_factories.OffererFactory()
        offerers_factories.UserOffererFactory(user=pro_user, offerer=offerer)
        _unexpected_bank_account = finance_factories.BankAccountFactory(offerer=offerer, isActive=False)
        expected_bank_account = finance_factories.BankAccountFactory(offerer=offerer, isActive=True)

        # When
        http_client = client.with_session_auth(pro_user.email)

        # Fetch the session
        # Fetch the user
        # Check user permission on offerer
        # Fetch offerer, bank_accounts and related/linked venues
        with assert_num_queries(4):
            response = http_client.get(f"/offerers/{offerer.id}/bank-accounts")

        # Then
        assert response.status_code == 200
        offerer_response = response.json

        bank_accounts = offerer_response["bankAccounts"]

        assert len(bank_accounts) == 1
        bank_account = bank_accounts.pop()
        assert bank_account["label"] == expected_bank_account.label
        assert bank_account["obfuscatedIban"] == f"XXXX XXXX XXXX {expected_bank_account.iban[-4:]}"
        assert bank_account["bic"] == expected_bank_account.bic
        assert bank_account["isActive"] is True

    @pytest.mark.usefixtures("db_session")
    def test_refused_nor_without_continuation_bank_accounts_arent_displayed(self, client):
        # Given
        pro_user = users_factories.ProFactory()
        offerer = offerers_factories.OffererFactory()
        offerers_factories.UserOffererFactory(user=pro_user, offerer=offerer)
        _refused_bank_account = finance_factories.BankAccountFactory(
            offerer=offerer, status=finance_models.BankAccountApplicationStatus.REFUSED
        )
        _without_continuation_bank_account = finance_factories.BankAccountFactory(
            offerer=offerer, status=finance_models.BankAccountApplicationStatus.REFUSED
        )

        expected_bank_account = finance_factories.BankAccountFactory(offerer=offerer, isActive=True)

        # When
        http_client = client.with_session_auth(pro_user.email)

        # Fetch the session
        # Fetch the user
        # Check user permission on offerer
        # Fetch offerer, bank_accounts and related/linked venues
        with assert_num_queries(4):
            response = http_client.get(f"/offerers/{offerer.id}/bank-accounts")

        # Then
        assert response.status_code == 200
        offerer_response = response.json

        bank_accounts = offerer_response["bankAccounts"]

        assert len(bank_accounts) == 1
        bank_account = bank_accounts.pop()
        assert bank_account["label"] == expected_bank_account.label
        assert bank_account["obfuscatedIban"] == f"XXXX XXXX XXXX {expected_bank_account.iban[-4:]}"
        assert bank_account["bic"] == expected_bank_account.bic
        assert bank_account["isActive"] is True

    @pytest.mark.usefixtures("db_session")
    def test_we_only_display_up_to_date_venue_link_for_a_given_bank_account(self, client):
        # Given
        pro_user = users_factories.ProFactory()
        offerer = offerers_factories.OffererFactory()
        offerers_factories.UserOffererFactory(user=pro_user, offerer=offerer)

        first_bank_account = finance_factories.BankAccountFactory(
            offerer=offerer, isActive=True, dateCreated=datetime.datetime.utcnow() - datetime.timedelta(days=1)
        )
        second_bank_account = finance_factories.BankAccountFactory(
            offerer=offerer, isActive=True, dateCreated=datetime.datetime.utcnow()
        )

        venue_linked = offerers_factories.VenueFactory(managingOfferer=offerer)
        offerers_factories.VenueFactory(managingOfferer=offerer)
        offerers_factories.VenueBankAccountLinkFactory(
            venueId=venue_linked.id,
            bankAccountId=first_bank_account.id,
            timespan=(
                datetime.datetime.utcnow() - datetime.timedelta(days=365),
                datetime.datetime.utcnow() - datetime.timedelta(seconds=10),
            ),
        )
        offerers_factories.VenueBankAccountLinkFactory(
            venueId=venue_linked.id, bankAccountId=second_bank_account.id, timespan=(datetime.datetime.utcnow(), None)
        )

        # When
        http_client = client.with_session_auth(pro_user.email)

        # Fetch the session
        # Fetch the user
        # Check user permission on offerer
        # Fetch offerer, bank_accounts and related/linked venues
        with assert_num_queries(4):
            response = http_client.get(f"/offerers/{offerer.id}/bank-accounts")

        # Then
        assert response.status_code == 200
        offerer_response = response.json

        bank_accounts = offerer_response["bankAccounts"]
        managed_venues = sorted(offerer_response["managedVenues"], key=lambda venue: venue["id"])

        assert len(bank_accounts) == 2
        assert bank_accounts[0]["id"] == first_bank_account.id
        assert not bank_accounts[0]["linkedVenues"]
        assert bank_accounts[1]["id"] == second_bank_account.id
        assert bank_accounts[1]["linkedVenues"]

        assert managed_venues[0]["bankAccountId"] == second_bank_account.id
        assert not managed_venues[1]["bankAccountId"]
