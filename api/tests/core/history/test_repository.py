from datetime import UTC
from datetime import datetime
from datetime import timedelta

import pytest

import pcapi.core.history.constants as history_constants
import pcapi.core.history.factories as history_factories
import pcapi.core.history.repository as history_repository
import pcapi.core.offerers.api as offerers_api
import pcapi.core.offerers.factories as offerers_factories
import pcapi.core.users.factories as users_factories


pytestmark = pytest.mark.usefixtures("db_session")


def test_get_closing_action_when_the_venue_is_closed():
    venue = offerers_factories.VenueFactory()
    closing_user = users_factories.ProFactory()
    offerers_factories.UserOffererFactory(user=closing_user, offerer=venue.managingOfferer)
    offerers_api.close_venue(venue, closing_user)

    # Doesn't make sense to add a venue created log after the closing it but it's for making
    # sure that we do filter on the event type for that venue.
    other_user = users_factories.ProFactory()
    offerers_factories.UserOffererFactory(user=other_user, offerer=venue.managingOfferer)
    history_factories.ActionHistoryFactory(
        actionType=history_constants.ActionType.VENUE_CREATED,
        authorUser=other_user,
        venue=venue,
    )

    fetched_action = history_repository.get_latest_venue_closure_event(venue.id)

    assert fetched_action.authorUser.id == closing_user.id


def test_get_closing_user_when_the_venue_has_not_been_closed():
    venue = offerers_factories.VenueFactory()
    user = users_factories.ProFactory()
    offerers_factories.UserOffererFactory(user=user, offerer=venue.managingOfferer)

    fetched_action = history_repository.get_latest_venue_closure_event(venue.id)

    assert not fetched_action


def test_get_latest_closing_user_when_the_venue_is_closed_several_times():
    venue = offerers_factories.VenueFactory()
    closing_users = sorted(users_factories.ProFactory.create_batch(size=3), key=lambda u: u.id)
    for user in closing_users:
        offerers_factories.UserOffererFactory(user=user, offerer=venue.managingOfferer)
        history_factories.ActionHistoryFactory(
            actionType=history_constants.ActionType.VENUE_CLOSED,
            authorUser=user,
            venue=venue,
        )

    fetched_action = history_repository.get_latest_venue_closure_event(venue.id)

    # Should return the last user from the list
    assert fetched_action.authorUser.id == closing_users[-1].id


class GetEventsRegardingVenueClosureBeforeTest:
    def test_no_events_at_all_returns_empty_query(self):
        assert history_repository.get_events_regarding_venue_closure_before(30).count() == 0

    def test_not_targetted_action_types_are_ignored(self):
        two_months_ago = datetime.now(UTC) - timedelta(days=60)
        user = users_factories.UserFactory()
        history_factories.ActionHistoryFactory(
            userId=user.id, actionType=history_constants.ActionType.COMMENT, actionDate=two_months_ago
        )
        assert history_repository.get_events_regarding_venue_closure_before(30).count() == 0

    def test_too_close_events_are_ignored(self):
        one_week_ago = datetime.now(UTC) - timedelta(days=7)
        venue = offerers_factories.VenueFactory()
        history_factories.ActionHistoryFactory(
            venueId=venue.id, actionType=history_constants.ActionType.VENUE_ADD_CLOSURE_TAG, actionDate=one_week_ago
        )
        assert history_repository.get_events_regarding_venue_closure_before(30).count() == 0

    def test_expected_add_closure_tag_events_are_fetched(self):
        two_months_ago = datetime.now(UTC) - timedelta(days=60)
        venue = offerers_factories.VenueFactory()
        events = history_factories.ActionHistoryFactory.create_batch(
            3,
            venueId=venue.id,
            actionType=history_constants.ActionType.VENUE_ADD_CLOSURE_TAG,
            actionDate=two_months_ago,
        )

        res = history_repository.get_events_regarding_venue_closure_before(30).all()

        assert len(res) == 3
        assert {found.id for found in res} == {event.id for event in events}
