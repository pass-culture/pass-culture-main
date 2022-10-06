import pytest

from pcapi.core.history import api as history_api
from pcapi.core.history import models as history_models
from pcapi.core.offerers import factories as offerers_factories
from pcapi.core.offerers import models as offerers_models
from pcapi.core.users import factories as users_factories


pytestmark = pytest.mark.usefixtures("db_session")


class LogActionTest:
    def test_log_action(self):
        admin = users_factories.AdminFactory()
        user_offerer = offerers_factories.UserOffererFactory()

        returned_action = history_api.log_action(
            history_models.ActionType.OFFERER_REJECTED,
            admin,
            user=user_offerer.user,
            offerer=user_offerer.offerer,
            comment="Test rejected",
            save=True,
            custom_data="Test",
        )

        action = history_models.ActionHistory.query.one()
        assert action.actionType == history_models.ActionType.OFFERER_REJECTED
        assert action.authorUserId == admin.id
        assert action.authorUser == admin
        assert action.userId == user_offerer.user.id
        assert action.user == user_offerer.user
        assert action.offererId == user_offerer.offerer.id
        assert action.offerer == user_offerer.offerer
        assert action.venueId is None
        assert action.venue is None
        assert action.comment == "Test rejected"
        assert action.extraData == {"custom_data": "Test"}

        assert returned_action == action

    def test_log_action_without_resource(self):
        admin = users_factories.AdminFactory()

        with pytest.raises(ValueError) as err:
            history_api.log_action(history_models.ActionType.OFFERER_PENDING, admin)

        assert "No resource" in str(err.value)
        assert history_models.ActionHistory.query.count() == 0

    def test_log_action_do_not_save(self):
        admin = users_factories.AdminFactory()
        user_offerer = offerers_factories.UserOffererFactory()

        action = history_api.log_action(
            history_models.ActionType.OFFERER_VALIDATED,
            admin,
            user=user_offerer.user,
            offerer=user_offerer.offerer,
            save=False,
        )

        assert action.id is None
        assert action.actionType == history_models.ActionType.OFFERER_VALIDATED
        assert action.authorUser == admin
        assert action.user == user_offerer.user
        assert action.offerer == user_offerer.offerer
        assert action.venueId is None

    def test_log_action_unsaved_resource(self):
        admin = users_factories.AdminFactory()
        user = users_factories.UserFactory()
        unsaved_offerer = offerers_models.Offerer()
        unsaved_offerer.siren = "102030405"
        unsaved_offerer.name = "Librairie du pass"
        unsaved_offerer.postalCode = "75018"
        unsaved_offerer.city = "Paris"

        with pytest.raises(RuntimeError):
            history_api.log_action(
                history_models.ActionType.OFFERER_VALIDATED,
                admin,
                user=user,
                offerer=unsaved_offerer,
            )
