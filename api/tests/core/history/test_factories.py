import pytest
from sqlalchemy.exc import IntegrityError

from pcapi.core.history import factories
from pcapi.core.history import models
from pcapi.core.offerers import factories as offerers_factories
from pcapi.core.users import factories as users_factories


class HistoryFactoriesTest:
    def test_action_history_factory(self):
        author = users_factories.AdminFactory()
        user = users_factories.UserFactory()
        offerer = offerers_factories.OffererFactory()
        venue = offerers_factories.VenueFactory(managingOfferer=offerer)
        action: models.ActionHistory = factories.ActionHistoryFactory(
            authorUser=author, user=user, offerer=offerer, venue=venue, extraData={"test": "ok"}
        )

        assert action.actionType == models.ActionType.COMMENT
        assert action.actionDate is not None
        assert action.authorUserId == author.id
        assert action.authorUser == author
        assert action.userId == user.id
        assert action.user == user
        assert action.offererId == offerer.id
        assert action.offerer == offerer
        assert action.venueId == venue.id
        assert action.venue == venue
        assert "created by factory" in action.comment
        assert action.extraData == {"test": "ok"}

    def test_action_history_factory_without_resource(self):
        with pytest.raises(IntegrityError) as err:
            factories.ActionHistoryFactory()
        assert "check_at_least_one_resource" in str(err.value)
