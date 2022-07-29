from datetime import datetime
from datetime import timedelta

import pytest

import pcapi.core.users.constants as users_constants
import pcapi.core.users.factories as users_factories
import pcapi.core.users.models as users_models
from pcapi.scripts.handle_suspended_accounts_without_suspension_date import (
    get_suspended_users_without_a_suspension_date_query,
)
from pcapi.scripts.handle_suspended_accounts_without_suspension_date import get_users_latest_event_row_id_query
from pcapi.scripts.handle_suspended_accounts_without_suspension_date import mark_accounts_as_deleted


pytestmark = pytest.mark.usefixtures("db_session")


class GetSuspendedUsersWithoutASuspensionDateQueryTest:
    def test_one_user_one_event(self):
        user = users_factories.UserFactory()
        event = users_factories.SuspendedUponUserRequestFactory(user=user)

        # set it manually, otherwise default value would have been used
        event.eventDate = None

        rows = get_suspended_users_without_a_suspension_date_query().all()
        assert rows == [(event.userId,)]

    def test_one_user_latest_event_expected(self):
        """
        Test that a row is returned if the latest event matches all the
        criteria (eventDate and suspended upon user request).
        """
        user = users_factories.UserFactory()
        _, _, event = users_factories.SuspendedUponUserRequestFactory.create_batch(3, user=user)

        # set it manually, otherwise default value would have been used
        event.eventDate = None

        rows = get_suspended_users_without_a_suspension_date_query().all()
        assert rows == [(user.id,)]

    def test_one_user_should_not_find_anything(self):
        """
        Test that when the latest event does not match one of the
        criteria (no eventDate or not suspended upon user request type),
        no row is returned
        """
        user = users_factories.UserFactory()
        _, event, _ = users_factories.SuspendedUponUserRequestFactory.create_batch(3, user=user)

        # set it manually, otherwise default value would have been used
        event.eventDate = None

        rows = get_suspended_users_without_a_suspension_date_query().all()
        assert not rows

    def test_multiple_users(self):
        user1, user2, user3 = users_factories.UserFactory.create_batch(3)

        # user1 should be found inside the result rows: it has a
        # suspension upon user request event with no event date which is
        # the most recent one.
        user1_events = users_factories.SuspendedUponUserRequestFactory.create_batch(3, user=user1)
        user1_events[-1].eventDate = None

        # user2 should not be found inside the result rows: it has a
        # suspension upon user request event with no event date, but it
        # is not the most recent one
        user2_events = users_factories.SuspendedUponUserRequestFactory.create_batch(3, user=user2)
        user2_events[0].eventDate = None

        # user3 should not be found inside the result rows: it has no
        # suspension upon user request events.
        users_factories.UnsuspendedSuspensionFactory.create_batch(3, user=user3)

        rows = get_suspended_users_without_a_suspension_date_query().all()
        rows = sorted(rows, key=lambda row: row[0])

        assert rows == [(user1.id,)]


class GetUsersLatestEventRowIdQueryTest:
    def test_one_user_one_event(self):
        event = users_factories.SuspendedUponUserRequestFactory()

        rows = get_users_latest_event_row_id_query().all()
        assert rows == [(event.userId, event.id)]

    def test_one_user_mutiple_events(self):
        user = users_factories.UserFactory()
        events = users_factories.SuspendedUponUserRequestFactory.create_batch(3, user=user)

        rows = get_users_latest_event_row_id_query().all()
        expected_event = sorted(events, key=lambda event: event.id)[-1]

        assert rows == [(user.id, expected_event.id)]

    def test_multiple_users_multiple_events(self):
        user1, user2, user3 = users_factories.UserFactory.create_batch(3)

        user1_events = users_factories.SuspendedUponUserRequestFactory.create_batch(2, user=user1)
        user2_events = users_factories.UserSuspensionByFraudFactory.create_batch(3, user=user2)
        user3_events = users_factories.UnsuspendedSuspensionFactory.create_batch(2, user=user3)

        rows = get_users_latest_event_row_id_query().all()
        rows = sorted(rows, key=lambda row: row.userId)

        user1_expected_event = sorted(user1_events, key=lambda event: event.id)[-1]
        user2_expected_event = sorted(user2_events, key=lambda event: event.id)[-1]
        user3_expected_event = sorted(user3_events, key=lambda event: event.id)[-1]

        expected_events = [user1_expected_event, user2_expected_event, user3_expected_event]
        expected_events = sorted(expected_events, key=lambda event: event.userId)
        expected_events = [(event.userId, event.id) for event in expected_events]

        assert rows == expected_events


class MarkAccountsAsDeletedTest:
    def test_mark_accounts_as_deleted(self):
        user = users_factories.UserFactory(isActive=False)
        actor = users_factories.UserFactory()

        event = users_factories.SuspendedUponUserRequestFactory(user=user)
        now = datetime.utcnow()

        # set it manually, otherwise default value would have been used
        event.eventDate = None

        mark_accounts_as_deleted(now, actor.id)

        user = users_models.User.query.get(user.id)

        assert user.suspension_date == now
        assert user.suspension_reason == users_constants.SuspensionReason.DELETED

    def test_mark_only_one_account(self):
        actor = users_factories.UserFactory()
        now = datetime.utcnow()

        user1, user2 = users_factories.UserFactory.create_batch(2, isActive=False)

        user1_event = users_factories.SuspendedUponUserRequestFactory(user=user1)

        # set it manually, otherwise default value would have been used
        user1_event.eventDate = None

        yesterday = now - timedelta(days=1)
        users_factories.SuspendedUponUserRequestFactory(user=user2, eventDate=yesterday)

        mark_accounts_as_deleted(now, actor.id)

        user1 = users_models.User.query.get(user1.id)
        user2 = users_models.User.query.get(user2.id)

        assert user1.suspension_date == now
        assert user1.suspension_reason == users_constants.SuspensionReason.DELETED

        # Nothing changed for user2
        assert user2.suspension_date == yesterday
        assert user2.suspension_reason == users_constants.SuspensionReason.UPON_USER_REQUEST

        # Nothing changed for actor
        assert not actor.suspension_date
        assert not actor.suspension_reason
