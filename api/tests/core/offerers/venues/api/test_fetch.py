import pytest

from pcapi.core.offerers import factories
from pcapi.core.offerers.venues import api
from pcapi.core.users import factories as users_factories
from pcapi.models import db


pytestmark = pytest.mark.usefixtures("db_session")


class FetchUserVenuesSplittedBaseOnUserOffererStatusTest:
    def test_user_is_linked_to_no_venues(self):
        user = users_factories.UserFactory()
        splitted = api.fetch_user_venues_splitted_based_on_user_offerer_status(user.id)
        assert not splitted.others
        assert not splitted.with_pending_validation

    def test_user_has_both_pending_and_validated_user_offerer_links(self):
        user = users_factories.UserFactory()

        attached_user_offerer = factories.UserOffererFactory(user=user)
        attached_venue = factories.VenueFactory(managingOfferer=attached_user_offerer.offerer)

        pending_user_offerer = factories.NewUserOffererFactory(user=user)
        pending_venue = factories.VenueFactory(managingOfferer=pending_user_offerer.offerer)

        splitted = api.fetch_user_venues_splitted_based_on_user_offerer_status(user.id)

        assert splitted.others == [attached_venue]
        assert splitted.with_pending_validation == [pending_venue]

    def test_only_valid_or_pending_user_offerer_links_are_searched_for(self):
        user = users_factories.UserFactory()

        rejected_user_offerer = factories.RejectedUserOffererFactory(user=user)
        factories.VenueFactory(managingOfferer=rejected_user_offerer.offerer)

        deleted_user_offerer = factories.DeletedUserOffererFactory(user=user)
        factories.VenueFactory(managingOfferer=deleted_user_offerer.offerer)

        pending_user_offerer = factories.NewUserOffererFactory(user=user)
        pending_venue = factories.VenueFactory(managingOfferer=pending_user_offerer.offerer)

        splitted = api.fetch_user_venues_splitted_based_on_user_offerer_status(user.id)

        assert not splitted.others
        assert splitted.with_pending_validation == [pending_venue]

    def test_only_fetch_from_pending_validated_or_closed_offerers(self):
        user = users_factories.UserFactory()

        rejected_offerer = factories.RejectedOffererFactory()
        factories.VenueFactory(managingOfferer=rejected_offerer)
        factories.UserOffererFactory(offerer=rejected_offerer)

        pending_user_offerer = factories.NewUserOffererFactory(user=user)
        pending_venue = factories.VenueFactory(managingOfferer=pending_user_offerer.offerer)

        splitted = api.fetch_user_venues_splitted_based_on_user_offerer_status(user.id)

        assert not splitted.others
        assert splitted.with_pending_validation == [pending_venue]

    def test_soft_deleted_venues_are_ignored(self):
        user = users_factories.UserFactory()
        pending_user_offerer = factories.NewUserOffererFactory(user=user)
        venue = factories.VenueFactory(managingOfferer=pending_user_offerer.offerer)

        # factories does not seem to work well with `isSoftDeleted`
        venue.isSoftDeleted = True
        db.session.add(venue)
        db.session.flush()

        splitted = api.fetch_user_venues_splitted_based_on_user_offerer_status(user.id)

        assert not splitted.others
        assert not splitted.with_pending_validation
