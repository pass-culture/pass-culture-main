from collections import namedtuple
import datetime

import pytest

from pcapi.core import token
import pcapi.core.finance.factories as finance_factories
import pcapi.core.finance.models as finance_models
import pcapi.core.history.models as history_models
import pcapi.core.mails.testing as mails_testing
import pcapi.core.offerers.factories as offerers_factories
import pcapi.core.offerers.models as offerers_models
import pcapi.core.token.serialization as token_serialization
import pcapi.core.users.factories as users_factories
from pcapi.models import db


ActionOccurred = namedtuple("ActionOccurred", ["type", "authorUserId", "venueId", "offererId", "bankAccountId"])


class OffererPatchBankAccountsTest:
    def test_user_can_link_venue_to_bank_account(self, db_session, client):
        actions_occured = []

        offerer = offerers_factories.OffererFactory()
        pro_user = users_factories.ProFactory()
        offerers_factories.UserOffererFactory(user=pro_user, offerer=offerer)
        bank_account = finance_factories.BankAccountFactory(offerer=offerer)
        venue = offerers_factories.VenueFactory(managingOfferer=offerer, pricing_point="self")

        assert not bank_account.venueLinks

        http_client = client.with_session_auth(pro_user.email)

        response = http_client.patch(
            f"/offerers/{offerer.id}/bank-accounts/{bank_account.id}", json={"venues_ids": [venue.id]}
        )

        assert response.status_code == 204

        actions_occured.append(
            ActionOccurred(
                type=history_models.ActionType.LINK_VENUE_BANK_ACCOUNT_CREATED,
                authorUserId=pro_user.id,
                venueId=venue.id,
                offererId=offerer.id,
                bankAccountId=bank_account.id,
            )
        )

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

        actions_logged = (
            db.session.query(history_models.ActionHistory).order_by(history_models.ActionHistory.venueId).all()
        )

        assert len(actions_logged) == len(actions_occured)

        for action_logged, action_occurred in zip(actions_logged, sorted(actions_occured, key=lambda a: a.venueId)):
            assert action_logged.actionType == action_occurred.type
            assert action_logged.authorUserId == action_occurred.authorUserId
            assert action_logged.venueId == action_occurred.venueId
            assert action_logged.bankAccountId == action_occurred.bankAccountId

    def test_impersonated_user_can_link_venue_to_bank_account(self, db_session, client):
        offerer = offerers_factories.OffererFactory()
        impersonator = users_factories.AdminFactory()
        pro_user = users_factories.ProFactory()
        offerers_factories.UserOffererFactory(user=pro_user, offerer=offerer)
        bank_account = finance_factories.BankAccountFactory(offerer=offerer)
        venue = offerers_factories.VenueFactory(managingOfferer=offerer, pricing_point="self")
        # impersonate pro user
        secure_token = token.SecureToken(
            data=token_serialization.ConnectAsInternalModel(
                redirect_link="http://example.com",
                user_id=pro_user.id,
                internal_admin_email=impersonator.email,
                internal_admin_id=impersonator.id,
            ).dict(),
        )

        client.get(f"/users/connect-as/{secure_token.token}")

        assert not bank_account.venueLinks

        response = client.patch(
            f"/offerers/{offerer.id}/bank-accounts/{bank_account.id}", json={"venues_ids": [venue.id]}
        )

        assert response.status_code == 204

        response = client.get(f"/offerers/{offerer.id}/bank-accounts/")

        assert response.status_code == 200

        db_session.refresh(bank_account)

        assert len(bank_account.venueLinks) == 1

        action_logged = (
            db.session.query(history_models.ActionHistory)
            .filter(
                history_models.ActionHistory.actionType == history_models.ActionType.LINK_VENUE_BANK_ACCOUNT_CREATED,
            )
            .one()
        )

        assert action_logged.authorUserId == impersonator.id
        assert action_logged.venueId == venue.id
        assert action_logged.bankAccountId == bank_account.id

    def test_user_cannot_link_venue_to_a_bank_account_that_doesnt_depend_on_its_offerer(self, db_session, client):
        actions_occured = []

        offerer = offerers_factories.OffererFactory()
        another_offerer = offerers_factories.OffererFactory()
        pro_user = users_factories.ProFactory()
        offerers_factories.UserOffererFactory(user=pro_user, offerer=offerer)
        bank_account = finance_factories.BankAccountFactory(offerer=offerer)
        bank_account_of_another_offerer = finance_factories.BankAccountFactory(offerer=another_offerer)
        bank_account_of_another_offerer_id = bank_account_of_another_offerer.id
        venue = offerers_factories.VenueFactory(managingOfferer=offerer, pricing_point="self")

        assert not bank_account.venueLinks

        http_client = client.with_session_auth(pro_user.email)

        response = http_client.patch(
            f"/offerers/{offerer.id}/bank-accounts/{bank_account_of_another_offerer_id}",
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

        actions_logged = (
            db.session.query(history_models.ActionHistory).order_by(history_models.ActionHistory.venueId).all()
        )

        assert len(actions_logged) == len(actions_occured) == 0

    def test_user_cannot_link_venue_that_doesnt_depend_on_its_offerer_to_a_bank_account(self, db_session, client):
        actions_occured = []

        offerer = offerers_factories.OffererFactory()
        another_offerer = offerers_factories.OffererFactory()
        pro_user = users_factories.ProFactory()
        offerers_factories.UserOffererFactory(user=pro_user, offerer=offerer)
        bank_account = finance_factories.BankAccountFactory(offerer=offerer)
        bank_account_id = bank_account.id
        offerers_factories.VenueFactory(managingOfferer=offerer)
        venue_of_another_offerer = offerers_factories.VenueFactory(
            managingOfferer=another_offerer, pricing_point="self"
        )
        venue_of_another_offerer_id = venue_of_another_offerer.id

        assert not bank_account.venueLinks

        http_client = client.with_session_auth(pro_user.email)

        response = http_client.patch(
            f"/offerers/{offerer.id}/bank-accounts/{bank_account_id}",
            json={"venues_ids": [venue_of_another_offerer_id]},
        )

        assert response.status_code == 204

        response = http_client.get(f"/offerers/{offerer.id}/bank-accounts/")

        assert response.status_code == 200
        assert len(response.json["bankAccounts"]) == 1
        bank_account_response = response.json["bankAccounts"].pop()
        assert not bank_account_response["linkedVenues"]

        db_session.refresh(bank_account)

        assert not bank_account.venueLinks

        actions_logged = (
            db.session.query(history_models.ActionHistory).order_by(history_models.ActionHistory.venueId).all()
        )

        assert len(actions_logged) == len(actions_occured) == 0

    def test_venue_bank_account_link_history_is_kept(self, db_session, client):
        actions_occured = []

        offerer = offerers_factories.OffererFactory()
        pro_user = users_factories.ProFactory()
        offerers_factories.UserOffererFactory(user=pro_user, offerer=offerer)
        bank_account = finance_factories.BankAccountFactory(offerer=offerer)
        bank_account_id = bank_account.id
        first_venue, second_venue, third_venue = offerers_factories.VenueFactory.create_batch(
            3, managingOfferer=offerer, pricing_point="self"
        )
        offerers_factories.VenueBankAccountLinkFactory(venue=first_venue, bankAccount=bank_account)
        offerers_factories.VenueBankAccountLinkFactory(venue=second_venue, bankAccount=bank_account)
        offerers_factories.VenueBankAccountLinkFactory(venue=third_venue, bankAccount=bank_account)

        assert len(bank_account.venueLinks) == 3
        assert (
            db.session.query(offerers_models.VenueBankAccountLink)
            .join(finance_models.BankAccount)
            .filter(
                finance_models.BankAccount.id == bank_account.id,
                offerers_models.VenueBankAccountLink.timespan.contains(datetime.datetime.utcnow()),
            )
            .count()
            == 3
        )

        http_client = client.with_session_auth(pro_user.email)

        response = http_client.patch(f"/offerers/{offerer.id}/bank-accounts/{bank_account_id}", json={"venues_ids": []})

        actions_occured.extend(
            [
                ActionOccurred(
                    type=history_models.ActionType.LINK_VENUE_BANK_ACCOUNT_DEPRECATED,
                    authorUserId=pro_user.id,
                    venueId=first_venue.id,
                    offererId=offerer.id,
                    bankAccountId=bank_account.id,
                ),
                ActionOccurred(
                    type=history_models.ActionType.LINK_VENUE_BANK_ACCOUNT_DEPRECATED,
                    authorUserId=pro_user.id,
                    venueId=second_venue.id,
                    offererId=offerer.id,
                    bankAccountId=bank_account.id,
                ),
                ActionOccurred(
                    type=history_models.ActionType.LINK_VENUE_BANK_ACCOUNT_DEPRECATED,
                    authorUserId=pro_user.id,
                    venueId=third_venue.id,
                    offererId=offerer.id,
                    bankAccountId=bank_account.id,
                ),
            ]
        )

        assert response.status_code == 204

        response = http_client.get(f"/offerers/{offerer.id}/bank-accounts/")

        assert response.status_code == 200
        assert len(response.json["bankAccounts"]) == 1
        bank_account_response = response.json["bankAccounts"].pop()
        assert not bank_account_response["linkedVenues"]

        db_session.refresh(bank_account)

        assert len(bank_account.venueLinks) == 3

        assert (
            not db.session.query(offerers_models.VenueBankAccountLink)
            .join(finance_models.BankAccount)
            .filter(
                finance_models.BankAccount.id == bank_account.id,
                offerers_models.VenueBankAccountLink.timespan.contains(datetime.datetime.utcnow()),
            )
            .count()
        )

        actions_logged = (
            db.session.query(history_models.ActionHistory).order_by(history_models.ActionHistory.venueId).all()
        )

        assert len(actions_logged) == len(actions_occured)

        for action_logged, action_occurred in zip(actions_logged, sorted(actions_occured, key=lambda a: a.venueId)):
            assert action_logged.actionType == action_occurred.type
            assert action_logged.authorUserId == action_occurred.authorUserId
            assert action_logged.venueId == action_occurred.venueId
            assert action_logged.bankAccountId == action_occurred.bankAccountId

        expected_data = [
            {
                "VENUE_NAME": first_venue.common_name,
                "BANK_ACCOUNT_LABEL": bank_account.label,
            },
            {
                "VENUE_NAME": second_venue.common_name,
                "BANK_ACCOUNT_LABEL": bank_account.label,
            },
            {
                "VENUE_NAME": third_venue.common_name,
                "BANK_ACCOUNT_LABEL": bank_account.label,
            },
        ]

        assert len(mails_testing.outbox) == len(expected_data)

        for mail_sent in mails_testing.outbox:
            assert mail_sent["params"] in expected_data

    def test_adding_new_venue_link_doesnt_alter_historic_links(self, db_session, client):
        actions_occured = []

        offerer = offerers_factories.OffererFactory()
        pro_user = users_factories.ProFactory()
        offerers_factories.UserOffererFactory(user=pro_user, offerer=offerer)
        bank_account = finance_factories.BankAccountFactory(offerer=offerer)
        first_venue, second_venue, third_venue, fourth_venue = offerers_factories.VenueFactory.create_batch(
            4, managingOfferer=offerer, pricing_point="self"
        )

        first_history_link = offerers_factories.VenueBankAccountLinkFactory(
            venue=first_venue,
            bankAccount=bank_account,
            timespan=(
                datetime.datetime.utcnow() - datetime.timedelta(days=365),
                datetime.datetime.utcnow() - datetime.timedelta(days=10),
            ),
        )
        first_timespan = first_history_link.timespan
        second_history_link = offerers_factories.VenueBankAccountLinkFactory(
            venue=second_venue,
            bankAccount=bank_account,
            timespan=(
                datetime.datetime.utcnow() - datetime.timedelta(days=365),
                datetime.datetime.utcnow() - datetime.timedelta(days=10),
            ),
        )
        second_timespan = second_history_link.timespan

        assert len(bank_account.venueLinks) == 2
        assert (
            not db.session.query(offerers_models.VenueBankAccountLink)
            .join(finance_models.BankAccount)
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

        actions_occured.extend(
            [
                ActionOccurred(
                    type=history_models.ActionType.LINK_VENUE_BANK_ACCOUNT_CREATED,
                    authorUserId=pro_user.id,
                    venueId=third_venue.id,
                    offererId=offerer.id,
                    bankAccountId=bank_account.id,
                ),
                ActionOccurred(
                    type=history_models.ActionType.LINK_VENUE_BANK_ACCOUNT_CREATED,
                    authorUserId=pro_user.id,
                    venueId=fourth_venue.id,
                    offererId=offerer.id,
                    bankAccountId=bank_account.id,
                ),
            ]
        )

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
            db.session.query(offerers_models.VenueBankAccountLink)
            .join(finance_models.BankAccount)
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

        actions_logged = (
            db.session.query(history_models.ActionHistory).order_by(history_models.ActionHistory.venueId).all()
        )

        assert len(actions_logged) == len(actions_occured)

        for action_logged, action_occurred in zip(actions_logged, sorted(actions_occured, key=lambda a: a.venueId)):
            assert action_logged.actionType == action_occurred.type
            assert action_logged.authorUserId == action_occurred.authorUserId
            assert action_logged.venueId == action_occurred.venueId
            assert action_logged.bankAccountId == action_occurred.bankAccountId

    @pytest.mark.usefixtures("db_session")
    def test_user_should_be_able_to_add_venues_to_bank_account_without_altering_current_links(self, client):
        actions_occured = []

        offerer = offerers_factories.OffererFactory()
        pro_user = users_factories.ProFactory()
        offerers_factories.UserOffererFactory(user=pro_user, offerer=offerer)
        bank_account = finance_factories.BankAccountFactory(offerer=offerer)
        first_venue, second_venue, third_venue, fourth_venue = offerers_factories.VenueFactory.create_batch(
            4, managingOfferer=offerer, pricing_point="self"
        )

        first_current_link = offerers_factories.VenueBankAccountLinkFactory(
            venue=first_venue,
            bankAccount=bank_account,
            timespan=(datetime.datetime.utcnow() - datetime.timedelta(days=365),),
        )
        first_timespan = first_current_link.timespan
        second_current_link = offerers_factories.VenueBankAccountLinkFactory(
            venue=second_venue,
            bankAccount=bank_account,
            timespan=(datetime.datetime.utcnow() - datetime.timedelta(days=365),),
        )
        second_timespan = second_current_link.timespan

        assert len(bank_account.venueLinks) == 2
        assert (
            db.session.query(offerers_models.VenueBankAccountLink)
            .join(finance_models.BankAccount)
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

        actions_occured.extend(
            [
                ActionOccurred(
                    type=history_models.ActionType.LINK_VENUE_BANK_ACCOUNT_CREATED,
                    authorUserId=pro_user.id,
                    venueId=third_venue.id,
                    offererId=offerer.id,
                    bankAccountId=bank_account.id,
                ),
                ActionOccurred(
                    type=history_models.ActionType.LINK_VENUE_BANK_ACCOUNT_CREATED,
                    authorUserId=pro_user.id,
                    venueId=fourth_venue.id,
                    offererId=offerer.id,
                    bankAccountId=bank_account.id,
                ),
            ]
        )

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
            db.session.query(offerers_models.VenueBankAccountLink)
            .join(finance_models.BankAccount)
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

        actions_logged = (
            db.session.query(history_models.ActionHistory).order_by(history_models.ActionHistory.venueId).all()
        )

        assert len(actions_logged) == len(actions_occured)

        for action_logged, action_occurred in zip(actions_logged, sorted(actions_occured, key=lambda a: a.venueId)):
            assert action_logged.actionType == action_occurred.type
            assert action_logged.authorUserId == action_occurred.authorUserId
            assert action_logged.venueId == action_occurred.venueId
            assert action_logged.bankAccountId == action_occurred.bankAccountId

    def test_user_linking_venue_to_bank_account_doesnt_alter_foreign_offerers(self, db_session, client):
        actions_occured = []

        offerer = offerers_factories.OffererFactory()
        pro_user = users_factories.ProFactory()
        offerers_factories.UserOffererFactory(user=pro_user, offerer=offerer)
        bank_account = finance_factories.BankAccountFactory(offerer=offerer)
        venue = offerers_factories.VenueFactory(managingOfferer=offerer, pricing_point="self")

        foreign_offerer = offerers_factories.OffererFactory()
        foreign_bank_account = finance_factories.BankAccountFactory(offerer=foreign_offerer)
        foreign_venue = offerers_factories.VenueFactory(managingOfferer=foreign_offerer, pricing_point="self")
        foreign_link = offerers_factories.VenueBankAccountLinkFactory(
            venue=foreign_venue, bankAccount=foreign_bank_account, timespan=(datetime.datetime.utcnow(),)
        )

        assert not bank_account.venueLinks

        http_client = client.with_session_auth(pro_user.email)

        response = http_client.patch(
            f"/offerers/{offerer.id}/bank-accounts/{bank_account.id}", json={"venues_ids": [venue.id]}
        )

        assert response.status_code == 204

        actions_occured.append(
            ActionOccurred(
                type=history_models.ActionType.LINK_VENUE_BANK_ACCOUNT_CREATED,
                authorUserId=pro_user.id,
                venueId=venue.id,
                offererId=offerer.id,
                bankAccountId=bank_account.id,
            )
        )

        response = http_client.get(f"/offerers/{offerer.id}/bank-accounts/")

        assert response.status_code == 200
        assert len(response.json["bankAccounts"]) == 1
        bank_account_response = response.json["bankAccounts"].pop()
        assert len(bank_account_response["linkedVenues"]) == 1
        linked_venue = bank_account_response["linkedVenues"].pop()
        assert linked_venue["id"] == venue.id
        assert linked_venue["commonName"] == venue.common_name

        # Should not alter any other offerer data
        db_session.refresh(foreign_link)
        assert foreign_link.timespan.upper is None
        assert foreign_link.bankAccount == foreign_bank_account

        db_session.refresh(bank_account)

        assert len(bank_account.venueLinks) == 1

        actions_logged = (
            db.session.query(history_models.ActionHistory).order_by(history_models.ActionHistory.venueId).all()
        )

        assert len(actions_logged) == len(actions_occured)

        for action_logged, action_occurred in zip(actions_logged, sorted(actions_occured, key=lambda a: a.venueId)):
            assert action_logged.actionType == action_occurred.type
            assert action_logged.authorUserId == action_occurred.authorUserId
            assert action_logged.venueId == action_occurred.venueId
            assert action_logged.bankAccountId == action_occurred.bankAccountId

    def test_user_cannot_link_venue_to_bank_account_if_no_pricing_point(self, db_session, client):
        offerer = offerers_factories.OffererFactory()
        pro_user = users_factories.ProFactory()
        offerers_factories.UserOffererFactory(user=pro_user, offerer=offerer)
        bank_account = finance_factories.BankAccountFactory(offerer=offerer)
        bank_account_id = bank_account.id
        venue = offerers_factories.VenueFactory(managingOfferer=offerer)
        venue_id = venue.id
        venue_with_pp = offerers_factories.VenueFactory(managingOfferer=offerer, pricing_point="self")
        venue_with_pp_id = venue_with_pp.id

        assert not bank_account.venueLinks

        http_client = client.with_session_auth(pro_user.email)

        response = http_client.patch(
            f"/offerers/{offerer.id}/bank-accounts/{bank_account_id}",
            json={"venues_ids": [venue_id, venue_with_pp_id]},
        )

        assert response.status_code == 204

        response = http_client.get(f"/offerers/{offerer.id}/bank-accounts/")

        assert response.status_code == 200
        assert len(response.json["bankAccounts"]) == 1
        bank_account_response = response.json["bankAccounts"].pop()
        assert bank_account_response["linkedVenues"] == [
            {"commonName": venue_with_pp.commonName, "id": venue_with_pp_id}
        ]

    def test_user_cannot_link_venue_to_bank_account_if_not_right_status(self, db_session, client):
        offerer = offerers_factories.OffererFactory()
        pro_user = users_factories.ProFactory()
        offerers_factories.UserOffererFactory(user=pro_user, offerer=offerer)
        bank_account = finance_factories.BankAccountFactory(
            offerer=offerer, status=finance_models.BankAccountApplicationStatus.DRAFT
        )
        bank_account_id = bank_account.id
        venue = offerers_factories.VenueFactory(managingOfferer=offerer)
        venue_id = venue.id

        assert not bank_account.venueLinks

        http_client = client.with_session_auth(pro_user.email)

        response = http_client.patch(
            f"/offerers/{offerer.id}/bank-accounts/{bank_account_id}",
            json={"venues_ids": [venue_id]},
        )

        assert response.status_code == 404

        response = http_client.get(f"/offerers/{offerer.id}/bank-accounts/")

        assert response.status_code == 200
        assert len(response.json["bankAccounts"]) == 1
        bank_account_response = response.json["bankAccounts"].pop()
        assert not bank_account_response["linkedVenues"]

    @pytest.mark.usefixtures("db_session")
    def test_cannot_link_venue_to_multiple_bank_accounts_at_same_time(self, client):
        offerer = offerers_factories.OffererFactory()
        pro_user = users_factories.ProFactory()
        offerers_factories.UserOffererFactory(user=pro_user, offerer=offerer)
        first_bank_account = finance_factories.BankAccountFactory(offerer=offerer)
        second_bank_account = finance_factories.BankAccountFactory(offerer=offerer)
        venue = offerers_factories.VenueFactory(managingOfferer=offerer, pricing_point="self")
        offerers_factories.VenueBankAccountLinkFactory(venue=venue, bankAccount=first_bank_account)

        assert venue.current_bank_account_link.bankAccountId == first_bank_account.id

        http_client = client.with_session_auth(pro_user.email)

        response = http_client.patch(
            f"/offerers/{offerer.id}/bank-accounts/{second_bank_account.id}",
            json={"venues_ids": [venue.id]},
        )

        assert response.status_code == 400
        assert response.json == {
            "code": "VENUE_ALREADY_LINKED_TO_ANOTHER_BANK_ACCOUNT",
            "message": f"At least one venue ({venue.id},) is already linked to another bank account",
        }
        assert len(venue.bankAccountLinks) == 1
        assert venue.current_bank_account_link.bankAccountId == first_bank_account.id

    @pytest.mark.usefixtures("db_session")
    def test_send_deprecation_link_mail_fail_silently_when_no_email(self, client):
        offerer = offerers_factories.OffererFactory()
        pro_user = users_factories.ProFactory()
        offerers_factories.UserOffererFactory(user=pro_user, offerer=offerer)
        bank_account = finance_factories.BankAccountFactory(offerer=offerer)
        offerers_factories.VenueFactory(
            managingOfferer=offerer,
            pricing_point="self",
            bank_account=bank_account,
            bookingEmail=None,
        )

        http_client = client.with_session_auth(pro_user.email)

        response = http_client.patch(f"/offerers/{offerer.id}/bank-accounts/{bank_account.id}", json={"venues_ids": []})

        assert response.status_code == 204
