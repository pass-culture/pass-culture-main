import pytest

import pcapi.core.history.factories as history_factories
import pcapi.core.history.models as history_models
import pcapi.core.history.repository as history_repository
import pcapi.core.offerers.api as offerers_api
import pcapi.core.offerers.factories as offerers_factories
import pcapi.core.users.factories as users_factories


pytestmark = pytest.mark.usefixtures("db_session")


def test_get_closing_user_when_the_venue_is_closed():
    venue = offerers_factories.VenueFactory()
    closing_user = users_factories.ProFactory()
    offerers_factories.UserOffererFactory(user=closing_user, offerer=venue.managingOfferer)
    offerers_api.close_venue(venue, closing_user)

    # Doesn't make sense to add a venue created log after the closing it but it's for making
    # sure that we do filter on the event type for that venue.
    other_user = users_factories.ProFactory()
    offerers_factories.UserOffererFactory(user=other_user, offerer=venue.managingOfferer)
    history_factories.ActionHistoryFactory(
        actionType=history_models.ActionType.VENUE_CREATED,
        authorUser=other_user,
        venue=venue,
    )

    fetched_user = history_repository.get_latest_venue_closure_user(venue.id)

    assert fetched_user.id == closing_user.id


def test_get_closing_user_when_the_venue_has_not_been_closed():
    venue = offerers_factories.VenueFactory()
    user = users_factories.ProFactory()
    offerers_factories.UserOffererFactory(user=user, offerer=venue.managingOfferer)

    fetched_user = history_repository.get_latest_venue_closure_user(venue.id)

    assert not fetched_user


def test_get_latest_closing_user_when_the_venue_is_closed_several_times():
    venue = offerers_factories.VenueFactory()
    closing_users = sorted(users_factories.ProFactory.create_batch(size=3), key=lambda u: u.id)
    for user in closing_users:
        offerers_factories.UserOffererFactory(user=user, offerer=venue.managingOfferer)
        history_factories.ActionHistoryFactory(
            actionType=history_models.ActionType.VENUE_CLOSED,
            authorUser=user,
            venue=venue,
        )

    fetched_user = history_repository.get_latest_venue_closure_user(venue.id)

    # Should return the last user from the list
    assert fetched_user.id == closing_users[-1].id
