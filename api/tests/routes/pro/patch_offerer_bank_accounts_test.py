import datetime

import pytest

import pcapi.core.finance.factories as finance_factories
import pcapi.core.finance.models as finance_models
import pcapi.core.offerers.factories as offerers_factories
import pcapi.core.offerers.models as offerers_models
import pcapi.core.users.factories as users_factories


class OffererPatchBankAccountsTest:
    def test_user_can_link_venue_to_bank_account(self, db_session, client):
        offerer = offerers_factories.OffererFactory()
        pro_user = users_factories.ProFactory()
        offerers_factories.UserOffererFactory(user=pro_user, offerer=offerer)
        bank_account = finance_factories.BankAccountFactory(offerer=offerer)
        venue = offerers_factories.VenueFactory(managingOfferer=offerer)

        assert not bank_account.venueLinks

        http_client = client.with_session_auth(pro_user.email)

        response = http_client.patch(
            f"/offerers/{offerer.id}/bank-accounts/{bank_account.id}", json={"venues_ids": [venue.id]}
        )

        assert response.status_code == 204

        response = http_client.get(f"/offerers/{offerer.id}/bank-accounts/")

        assert response.status_code == 200
        assert len(response.json["bankAccounts"]) == 1
        bank_account_response = response.json["bankAccounts"].pop()
        assert len(bank_account_response["linkedVenues"]) == 1
        linked_venue = bank_account_response["linkedVenues"].pop()
        assert linked_venue["id"] == venue.id
        assert linked_venue["commonName"] == venue.common_name

        db_session.refresh(bank_account)

        assert len(bank_account.venueLinks) == 1

    @pytest.mark.usefixtures("db_session")
    def test_user_cannot_link_venue_to_a_bank_account_that_doesnt_depend_on_its_offerer(self, db_session, client):
        offerer = offerers_factories.OffererFactory()
        another_offerer = offerers_factories.OffererFactory()
        pro_user = users_factories.ProFactory()
        offerers_factories.UserOffererFactory(user=pro_user, offerer=offerer)
        bank_account = finance_factories.BankAccountFactory(offerer=offerer)
        bank_account_of_another_offerer = finance_factories.BankAccountFactory(offerer=another_offerer)
        venue = offerers_factories.VenueFactory(managingOfferer=offerer)

        assert not bank_account.venueLinks

        http_client = client.with_session_auth(pro_user.email)

        response = http_client.patch(
            f"/offerers/{offerer.id}/bank-accounts/{bank_account_of_another_offerer.id}",
            json={"venues_ids": [venue.id]},
        )

        assert response.status_code == 404

        response = http_client.get(f"/offerers/{offerer.id}/bank-accounts/")

        assert response.status_code == 200
        assert len(response.json["bankAccounts"]) == 1
        bank_account_response = response.json["bankAccounts"].pop()
        assert not bank_account_response["linkedVenues"]

        db_session.refresh(bank_account)

        assert not bank_account.venueLinks

    def test_user_cannot_link_venue_that_doesnt_depend_on_its_offerer_to_a_bank_account(self, db_session, client):
        offerer = offerers_factories.OffererFactory()
        another_offerer = offerers_factories.OffererFactory()
        pro_user = users_factories.ProFactory()
        offerers_factories.UserOffererFactory(user=pro_user, offerer=offerer)
        bank_account = finance_factories.BankAccountFactory(offerer=offerer)
        offerers_factories.VenueFactory(managingOfferer=offerer)
        venue_of_another_offerer = offerers_factories.VenueFactory(managingOfferer=another_offerer)

        assert not bank_account.venueLinks

        http_client = client.with_session_auth(pro_user.email)

        response = http_client.patch(
            f"/offerers/{offerer.id}/bank-accounts/{bank_account.id}",
            json={"venues_ids": [venue_of_another_offerer.id]},
        )

        assert response.status_code == 204

        response = http_client.get(f"/offerers/{offerer.id}/bank-accounts/")

        assert response.status_code == 200
        assert len(response.json["bankAccounts"]) == 1
        bank_account_response = response.json["bankAccounts"].pop()
        assert not bank_account_response["linkedVenues"]

        db_session.refresh(bank_account)

        assert not bank_account.venueLinks

    def test_venue_bank_account_link_history_is_kept(self, db_session, client):
        offerer = offerers_factories.OffererFactory()
        pro_user = users_factories.ProFactory()
        offerers_factories.UserOffererFactory(user=pro_user, offerer=offerer)
        bank_account = finance_factories.BankAccountFactory(offerer=offerer)
        first_venue = offerers_factories.VenueFactory(managingOfferer=offerer)
        second_venue = offerers_factories.VenueFactory(managingOfferer=offerer)
        third_venue = offerers_factories.VenueFactory(managingOfferer=offerer)
        offerers_factories.VenueBankAccountLinkFactory(venueId=first_venue.id, bankAccountId=bank_account.id)
        offerers_factories.VenueBankAccountLinkFactory(venueId=second_venue.id, bankAccountId=bank_account.id)
        offerers_factories.VenueBankAccountLinkFactory(venueId=third_venue.id, bankAccountId=bank_account.id)

        assert len(bank_account.venueLinks) == 3
        assert (
            offerers_models.VenueBankAccountLink.query.join(finance_models.BankAccount)
            .filter(
                finance_models.BankAccount.id == bank_account.id,
                offerers_models.VenueBankAccountLink.timespan.contains(datetime.datetime.utcnow()),
            )
            .count()
            == 3
        )

        http_client = client.with_session_auth(pro_user.email)

        response = http_client.patch(f"/offerers/{offerer.id}/bank-accounts/{bank_account.id}", json={"venues_ids": []})

        assert response.status_code == 204

        response = http_client.get(f"/offerers/{offerer.id}/bank-accounts/")

        assert response.status_code == 200
        assert len(response.json["bankAccounts"]) == 1
        bank_account_response = response.json["bankAccounts"].pop()
        assert not bank_account_response["linkedVenues"]

        db_session.refresh(bank_account)

        assert len(bank_account.venueLinks) == 3

        assert (
            not offerers_models.VenueBankAccountLink.query.join(finance_models.BankAccount)
            .filter(
                finance_models.BankAccount.id == bank_account.id,
                offerers_models.VenueBankAccountLink.timespan.contains(datetime.datetime.utcnow()),
            )
            .count()
        )

    def test_adding_new_venue_link_doesnt_alter_historic_links(self, db_session, client):
        offerer = offerers_factories.OffererFactory()
        pro_user = users_factories.ProFactory()
        offerers_factories.UserOffererFactory(user=pro_user, offerer=offerer)
        bank_account = finance_factories.BankAccountFactory(offerer=offerer)
        first_venue = offerers_factories.VenueFactory(managingOfferer=offerer)
        second_venue = offerers_factories.VenueFactory(managingOfferer=offerer)
        third_venue = offerers_factories.VenueFactory(managingOfferer=offerer)
        fourth_venue = offerers_factories.VenueFactory(managingOfferer=offerer)

        first_history_link = offerers_factories.VenueBankAccountLinkFactory(
            venueId=first_venue.id,
            bankAccountId=bank_account.id,
            timespan=(
                datetime.datetime.utcnow() - datetime.timedelta(days=365),
                datetime.datetime.utcnow() - datetime.timedelta(days=10),
            ),
        )
        first_timespan = first_history_link.timespan
        second_history_link = offerers_factories.VenueBankAccountLinkFactory(
            venueId=second_venue.id,
            bankAccountId=bank_account.id,
            timespan=(
                datetime.datetime.utcnow() - datetime.timedelta(days=365),
                datetime.datetime.utcnow() - datetime.timedelta(days=10),
            ),
        )
        second_timespan = second_history_link.timespan

        assert len(bank_account.venueLinks) == 2
        assert (
            not offerers_models.VenueBankAccountLink.query.join(finance_models.BankAccount)
            .filter(
                finance_models.BankAccount.id == bank_account.id,
                offerers_models.VenueBankAccountLink.timespan.contains(datetime.datetime.utcnow()),
            )
            .count()
            == 2
        )

        http_client = client.with_session_auth(pro_user.email)
        response = http_client.patch(
            f"/offerers/{offerer.id}/bank-accounts/{bank_account.id}",
            json={"venues_ids": [third_venue.id, fourth_venue.id]},
        )

        assert response.status_code == 204

        response = http_client.get(f"/offerers/{offerer.id}/bank-accounts/")

        assert response.status_code == 200
        assert len(response.json["bankAccounts"]) == 1
        bank_account_response = response.json["bankAccounts"].pop()
        for linked_venue, venue in zip(
            sorted(bank_account_response["linkedVenues"], key=lambda v: v["id"]), [third_venue, fourth_venue]
        ):
            assert linked_venue["id"] == venue.id
            assert linked_venue["commonName"] == venue.common_name

        db_session.refresh(bank_account)

        assert len(bank_account.venueLinks) == 4
        assert (
            offerers_models.VenueBankAccountLink.query.join(finance_models.BankAccount)
            .filter(
                finance_models.BankAccount.id == bank_account.id,
                offerers_models.VenueBankAccountLink.timespan.contains(datetime.datetime.utcnow()),
            )
            .count()
            == 2
        )

        for link in bank_account.venueLinks:
            if link.id in (first_history_link.id, second_history_link.id):
                assert link.timespan in (
                    first_timespan,
                    second_timespan,
                ), "Already existing and older bank-account-venues links shouldn't changed !"
            else:
                assert link.timespan.upper is None

    @pytest.mark.usefixtures("db_session")
    def test_user_should_be_able_to_add_venues_to_bank_account_without_altering_current_links(self, client):
        offerer = offerers_factories.OffererFactory()
        pro_user = users_factories.ProFactory()
        offerers_factories.UserOffererFactory(user=pro_user, offerer=offerer)
        bank_account = finance_factories.BankAccountFactory(offerer=offerer)
        first_venue = offerers_factories.VenueFactory(managingOfferer=offerer)
        second_venue = offerers_factories.VenueFactory(managingOfferer=offerer)
        third_venue = offerers_factories.VenueFactory(managingOfferer=offerer)
        fourth_venue = offerers_factories.VenueFactory(managingOfferer=offerer)

        first_current_link = offerers_factories.VenueBankAccountLinkFactory(
            venueId=first_venue.id,
            bankAccountId=bank_account.id,
            timespan=(datetime.datetime.utcnow() - datetime.timedelta(days=365),),
        )
        first_timespan = first_current_link.timespan
        second_current_link = offerers_factories.VenueBankAccountLinkFactory(
            venueId=second_venue.id,
            bankAccountId=bank_account.id,
            timespan=(datetime.datetime.utcnow() - datetime.timedelta(days=365),),
        )
        second_timespan = second_current_link.timespan

        assert len(bank_account.venueLinks) == 2
        assert (
            offerers_models.VenueBankAccountLink.query.join(finance_models.BankAccount)
            .filter(
                finance_models.BankAccount.id == bank_account.id,
                offerers_models.VenueBankAccountLink.timespan.contains(datetime.datetime.utcnow()),
            )
            .count()
            == 2
        )

        http_client = client.with_session_auth(pro_user.email)
        response = http_client.patch(
            f"/offerers/{offerer.id}/bank-accounts/{bank_account.id}",
            json={"venues_ids": [first_venue.id, second_venue.id, third_venue.id, fourth_venue.id]},
        )
        assert response.status_code == 204

        response = http_client.get(f"/offerers/{offerer.id}/bank-accounts/")

        assert response.status_code == 200
        assert len(response.json["bankAccounts"]) == 1
        bank_account_response = response.json["bankAccounts"].pop()
        for linked_venue, venue in zip(
            sorted(bank_account_response["linkedVenues"], key=lambda v: v["id"]),
            [first_venue, second_venue, third_venue, fourth_venue],
        ):
            assert linked_venue["id"] == venue.id
            assert linked_venue["commonName"] == venue.common_name

        assert len(bank_account.venueLinks) == 4

        assert (
            offerers_models.VenueBankAccountLink.query.join(finance_models.BankAccount)
            .filter(
                finance_models.BankAccount.id == bank_account.id,
                offerers_models.VenueBankAccountLink.timespan.contains(datetime.datetime.utcnow()),
            )
            .count()
            == 4
        )

        for link in bank_account.venueLinks:
            if link.id in (first_current_link.id, second_current_link.id):
                assert link.timespan in (
                    first_timespan,
                    second_timespan,
                ), "Already existing and current bank-account-venues links shouldn't changed !"
            assert link.timespan.upper is None
