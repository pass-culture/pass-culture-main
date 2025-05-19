import datetime

import pytest

import pcapi.core.finance.factories as finance_factories
import pcapi.core.finance.models as finance_models
import pcapi.core.offerers.factories as offerers_factories
import pcapi.core.offers.factories as offers_factories
import pcapi.core.users.factories as users_factories
from pcapi.core import testing


class OfferersBankAccountTest:
    @pytest.mark.usefixtures("db_session")
    def test_user_cant_access_bank_accounts_of_offerer_it_doesnt_depends_on(self, client):
        pro_user = users_factories.ProFactory()
        offerer_1 = offerers_factories.OffererFactory()
        offerer_2 = offerers_factories.OffererFactory()
        offerer_2_id = offerer_2.id
        offerers_factories.UserOffererFactory(user=pro_user, offerer=offerer_1)
        finance_factories.BankAccountFactory(offerer=offerer_2, isActive=True)

        http_client = client.with_session_auth(pro_user.email)

        num_queries = testing.AUTHENTICATION_QUERIES
        num_queries += 1  # Check user permission on offerer
        with testing.assert_num_queries(num_queries):
            response = http_client.get(f"/offerers/{offerer_2_id}/bank-accounts")
            assert response.status_code == 403

        assert "Vous n'avez pas les droits d'accès suffisants pour accéder à cette information." in str(response.json)

    @pytest.mark.usefixtures("db_session")
    def test_user_can_access_bank_accounts_page_even_if_it_doesnt_have_any(self, client):
        pro_user = users_factories.ProFactory()
        offerer = offerers_factories.OffererFactory()
        offerers_factories.UserOffererFactory(user=pro_user, offerer=offerer)

        http_client = client.with_session_auth(pro_user.email)

        offerer_id = offerer.id  # avoid extra SQL query below
        num_queries = testing.AUTHENTICATION_QUERIES
        num_queries += 1  # Check user permission on offerer
        num_queries += 1  # Fetch offerer, bank_accounts and related/linked venues
        with testing.assert_num_queries(num_queries):
            response = http_client.get(f"/offerers/{offerer_id}/bank-accounts")
            assert response.status_code == 200

        offerer = response.json
        bank_accounts = offerer["bankAccounts"]
        venues = offerer["managedVenues"]

        assert not bank_accounts
        assert not venues

    @pytest.mark.usefixtures("db_session")
    def test_users_offerer_can_access_its_bank_accounts(self, client):
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
        expected_venue = offerers_factories.VenueFactory(pricing_point="self", managingOfferer=offerer)
        expected_venue_without_siret = offerers_factories.VenueWithoutSiretFactory(managingOfferer=offerer)
        expected_bank_account = finance_factories.BankAccountFactory(offerer=offerer)

        http_client = client.with_session_auth(pro_user.email)

        offerer_id = offerer.id  # avoid extra SQL query below
        num_queries = testing.AUTHENTICATION_QUERIES
        num_queries += 1  # Check user permission on offerer
        num_queries += 1  # Fetch offerer, bank_accounts and related/linked venues
        with testing.assert_num_queries(num_queries):
            response = http_client.get(f"/offerers/{offerer_id}/bank-accounts")
            assert response.status_code == 200

        offerer = response.json
        bank_accounts = offerer["bankAccounts"]
        venues = sorted(offerer["managedVenues"], key=lambda v: v["id"])

        assert len(bank_accounts) == 1
        bank_account = bank_accounts.pop()
        assert bank_account["label"] == expected_bank_account.label
        assert bank_account["obfuscatedIban"] == f"XXXX XXXX XXXX {expected_bank_account.iban[-4:]}"
        assert bank_account["bic"] == expected_bank_account.bic
        assert bank_account["isActive"] is True
        assert bank_account["status"] == "accepte"
        assert not bank_account["linkedVenues"]

        assert len(venues) == 2
        assert venues[0]["id"] == expected_venue.id
        assert venues[0]["commonName"] == expected_venue.common_name
        assert venues[0]["siret"] == expected_venue.siret
        assert venues[0]["hasPricingPoint"] is True
        assert not venues[0]["bankAccountId"]
        assert venues[1]["id"] == expected_venue_without_siret.id
        assert venues[1]["commonName"] == expected_venue_without_siret.common_name
        assert venues[1]["hasPricingPoint"] is False
        assert not venues[1]["siret"]
        assert not venues[1]["bankAccountId"]

    @pytest.mark.usefixtures("db_session")
    def test_linked_venues_to_bank_accounts_are_displayed_to_users(self, client):
        pro_user = users_factories.ProFactory()
        offerer = offerers_factories.OffererFactory()
        offerers_factories.UserOffererFactory(user=pro_user, offerer=offerer)
        expected_venue = offerers_factories.VenueFactory(managingOfferer=offerer)
        non_linked_venue = offerers_factories.VenueFactory(managingOfferer=offerer)
        non_linked_venue_bis = offerers_factories.VenueFactory(managingOfferer=offerer)
        offer = offers_factories.OfferFactory(venue=non_linked_venue)
        offer_bis = offers_factories.OfferFactory(venue=non_linked_venue_bis)
        offers_factories.StockFactory(offer=offer)
        offers_factories.StockFactory(offer=offer_bis)
        expected_bank_account = finance_factories.BankAccountFactory(offerer=offerer)
        offerers_factories.VenueBankAccountLinkFactory(
            venue=expected_venue, bankAccount=expected_bank_account, timespan=(datetime.datetime.utcnow(),)
        )

        http_client = client.with_session_auth(pro_user.email)

        offerer_id = offerer.id  # avoid extra SQL query below
        num_queries = testing.AUTHENTICATION_QUERIES
        num_queries += 1  # Check user permission on offerer
        num_queries += 1  # Fetch offerer, bank_accounts and related/linked venues
        with testing.assert_num_queries(num_queries):
            response = http_client.get(f"/offerers/{offerer_id}/bank-accounts")
            assert response.status_code == 200

        offerer = response.json
        bank_accounts = offerer["bankAccounts"]

        assert len(bank_accounts) == 1
        bank_account = bank_accounts.pop()

        assert len(bank_account["linkedVenues"]) == 1
        linked_venue = bank_account["linkedVenues"].pop()
        assert linked_venue["id"] == expected_venue.id
        assert linked_venue["commonName"] == expected_venue.common_name

    @pytest.mark.usefixtures("db_session")
    def test_user_can_only_see_active_bank_accounts(self, client):
        pro_user = users_factories.ProFactory()
        offerer = offerers_factories.OffererFactory()
        offerers_factories.UserOffererFactory(user=pro_user, offerer=offerer)
        _unexpected_bank_account = finance_factories.BankAccountFactory(offerer=offerer, isActive=False)
        expected_bank_account = finance_factories.BankAccountFactory(offerer=offerer, isActive=True)

        http_client = client.with_session_auth(pro_user.email)

        offerer_id = offerer.id  # avoid extra SQL query below
        num_queries = testing.AUTHENTICATION_QUERIES
        num_queries += 1  # Check user permission on offerer
        num_queries += 1  # Fetch offerer, bank_accounts and related/linked venues
        with testing.assert_num_queries(num_queries):
            response = http_client.get(f"/offerers/{offerer_id}/bank-accounts")
            assert response.status_code == 200

        offerer = response.json
        bank_accounts = offerer["bankAccounts"]

        assert len(bank_accounts) == 1
        bank_account = bank_accounts.pop()
        assert bank_account["label"] == expected_bank_account.label
        assert bank_account["obfuscatedIban"] == f"XXXX XXXX XXXX {expected_bank_account.iban[-4:]}"
        assert bank_account["bic"] == expected_bank_account.bic
        assert bank_account["isActive"] is True

    @pytest.mark.usefixtures("db_session")
    def test_refused_nor_without_continuation_bank_accounts_arent_displayed(self, client):
        pro_user = users_factories.ProFactory()
        offerer = offerers_factories.OffererFactory()
        offerers_factories.UserOffererFactory(user=pro_user, offerer=offerer)
        _refused_bank_account = finance_factories.BankAccountFactory(
            offerer=offerer, status=finance_models.BankAccountApplicationStatus.REFUSED
        )
        _without_continuation_bank_account = finance_factories.BankAccountFactory(
            offerer=offerer, status=finance_models.BankAccountApplicationStatus.REFUSED
        )
        pending_bank_account = finance_factories.BankAccountFactory(
            offerer=offerer, status=finance_models.BankAccountApplicationStatus.ON_GOING
        )

        http_client = client.with_session_auth(pro_user.email)
        offerer_id = offerer.id  # avoid extra SQL query below
        num_queries = testing.AUTHENTICATION_QUERIES
        num_queries += 1  # Check user permission on offerer
        num_queries += 1  # Fetch offerer, bank_accounts and related/linked venues
        with testing.assert_num_queries(num_queries):
            response = http_client.get(f"/offerers/{offerer_id}/bank-accounts")
            assert response.status_code == 200

        offerer = response.json
        assert len(offerer["bankAccounts"]) == 1
        bank_account = offerer["bankAccounts"].pop()
        assert bank_account["id"] == pending_bank_account.id

    @pytest.mark.usefixtures("db_session")
    def test_we_only_display_up_to_date_venue_link_for_a_given_bank_account(self, client):
        pro_user = users_factories.ProFactory()
        offerer = offerers_factories.OffererFactory()
        offerers_factories.UserOffererFactory(user=pro_user, offerer=offerer)

        first_bank_account = finance_factories.BankAccountFactory(
            offerer=offerer, isActive=True, dateCreated=datetime.datetime.utcnow() - datetime.timedelta(days=1)
        )
        second_bank_account = finance_factories.BankAccountFactory(
            offerer=offerer, isActive=True, dateCreated=datetime.datetime.utcnow()
        )

        venue_linked = offerers_factories.VenueFactory(pricing_point="self", managingOfferer=offerer)
        offerers_factories.VenueFactory(pricing_point="self", managingOfferer=offerer)
        offerers_factories.VenueBankAccountLinkFactory(
            venueId=venue_linked.id,
            bankAccountId=first_bank_account.id,
            timespan=(
                datetime.datetime.utcnow() - datetime.timedelta(days=365),
                datetime.datetime.utcnow() - datetime.timedelta(seconds=10),
            ),
        )
        offerers_factories.VenueBankAccountLinkFactory(
            venue=venue_linked, bankAccount=second_bank_account, timespan=(datetime.datetime.utcnow(), None)
        )

        venue_not_linked_with_free_offer = offerers_factories.VenueWithoutSiretFactory(managingOfferer=offerer)
        offer = offers_factories.OfferFactory(venue=venue_not_linked_with_free_offer)
        offers_factories.StockFactory(offer=offer, price=0)

        http_client = client.with_session_auth(pro_user.email)

        offerer_id = offerer.id  # avoid extra SQL query below
        num_queries = testing.AUTHENTICATION_QUERIES
        num_queries += 1  # Check user permission on offerer
        num_queries += 1  # Fetch offerer, bank_accounts and related/linked venues
        with testing.assert_num_queries(num_queries):
            response = http_client.get(f"/offerers/{offerer_id}/bank-accounts")
            assert response.status_code == 200

        offerer = response.json

        bank_accounts = offerer["bankAccounts"]
        managed_venues = sorted(offerer["managedVenues"], key=lambda venue: venue["id"])
        assert len(managed_venues) == 3

        assert len(bank_accounts) == 2
        assert bank_accounts[0]["id"] == second_bank_account.id
        assert bank_accounts[0]["linkedVenues"]
        assert bank_accounts[1]["id"] == first_bank_account.id
        assert not bank_accounts[1]["linkedVenues"]

        assert managed_venues[0]["bankAccountId"] == second_bank_account.id
        assert not managed_venues[1]["bankAccountId"]

        assert managed_venues[0]["hasPricingPoint"] is True
        assert managed_venues[1]["hasPricingPoint"] is True
        assert managed_venues[2]["hasPricingPoint"] is False

    @pytest.mark.usefixtures("db_session")
    def test_user_should_only_see_non_virtual_venue_and_virtual_venues_that_have_at_least_one_offer(self, client):
        pro_user = users_factories.ProFactory()
        offerer = offerers_factories.OffererFactory()
        offerer_id = offerer.id
        offerers_factories.UserOffererFactory(user=pro_user, offerer=offerer)

        non_virtual_venue_with_offer = offerers_factories.VenueFactory(managingOfferer=offerer)
        offers_factories.StockFactory(price=0, offer__venue=non_virtual_venue_with_offer)

        non_virtual_without_any_offer = offerers_factories.VenueFactory(managingOfferer=offerer)

        virtual_venue_with_offer = offerers_factories.VirtualVenueFactory(managingOfferer=offerer)
        offers_factories.StockFactory(price=0, offer__venue=virtual_venue_with_offer)

        _virtual_venue_without_any_offer = offerers_factories.VirtualVenueFactory(managingOfferer=offerer)

        http_client = client.with_session_auth(pro_user.email)

        num_queries = testing.AUTHENTICATION_QUERIES
        num_queries += 1  # Check user permission on offerer
        num_queries += 1  # Fetch offerer, bank_accounts and related/linked venues
        with testing.assert_num_queries(num_queries):
            response = http_client.get(f"/offerers/{offerer_id}/bank-accounts")
            assert response.status_code == 200

        offerer = response.json
        assert not offerer["bankAccounts"]
        managedVenues = sorted(offerer["managedVenues"], key=lambda v: v["id"])
        assert len(managedVenues) == 3
        assert managedVenues[0]["id"] == non_virtual_venue_with_offer.id
        assert managedVenues[1]["id"] == non_virtual_without_any_offer.id
        assert managedVenues[2]["id"] == virtual_venue_with_offer.id
