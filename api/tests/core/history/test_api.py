import pytest

from pcapi.core.criteria import factories as criteria_factories
from pcapi.core.history import api as history_api
from pcapi.core.history import models as history_models
from pcapi.core.offerers import api as offerers_api
from pcapi.core.offerers import factories as offerers_factories
from pcapi.core.offerers import models as offerers_models
from pcapi.core.users import factories as users_factories


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


class ObjectUpdateSnapshotTest:
    def test_trace_update(self):
        author = users_factories.UserFactory()
        offerer = offerers_factories.OffererFactory()

        new_name = offerer.name + " New"
        new_siren = "987654321234"

        snapshot = history_api.ObjectUpdateSnapshot(offerer, author)
        snapshot.trace_update({"name": new_name, "siren": new_siren}).log_update(save=True)

        action = history_models.ActionHistory.query.one()

        assert action.actionType == history_models.ActionType.INFO_MODIFIED
        assert action.offererId == offerer.id
        assert action.authorUser.id == author.id
        assert action.extraData == {
            "modified_info": {
                "name": {"old_info": offerer.name, "new_info": new_name},
                "siren": {"old_info": offerer.siren, "new_info": new_siren},
            }
        }

    def test_trace_update_with_no_modification(self):
        author = users_factories.UserFactory()
        venue = offerers_factories.VenueFactory()

        # Reproduce the same process as through the form
        longitude = float(str(venue.longitude))
        latitude = float(str(venue.latitude))
        venue_type_code = venue.venueTypeCode.name

        attrs = {
            "longitude": longitude,
            "latitude": latitude,
            "venueTypeCode": venue_type_code,
        }
        offerers_api.update_venue(venue, author=author, contact_data=None, **attrs)

        assert history_models.ActionHistory.query.count() == 0

    def test_log_update_without_saving(self):
        author = users_factories.UserFactory()
        offerer = offerers_factories.OffererFactory()

        new_name = offerer.name + " New"
        new_siren = "987654321234"

        snapshot = history_api.ObjectUpdateSnapshot(offerer, author)
        action = snapshot.trace_update({"name": new_name, "siren": new_siren}).log_update(save=False)

        assert not action.id

        assert action.offerer.id == offerer.id
        assert action.authorUser.id == author.id
        assert action.extraData == {
            "modified_info": {
                "name": {"old_info": offerer.name, "new_info": new_name},
                "siren": {"old_info": offerer.siren, "new_info": new_siren},
            }
        }

    def test_trace_update_without_custom_target(self):
        author = users_factories.UserFactory()
        venue = offerers_factories.VenueFactory()

        new_email = venue.contact.email + ".update"

        snapshot = history_api.ObjectUpdateSnapshot(venue, author)
        snapshot.trace_update({"email": new_email}, target=venue.contact, field_name_template="contact.{}").log_update(
            save=True
        )

        action = history_models.ActionHistory.query.one()

        assert action.actionType == history_models.ActionType.INFO_MODIFIED
        assert action.venueId == venue.id
        assert action.authorUser.id == author.id
        assert action.extraData == {
            "modified_info": {
                "contact.email": {"old_info": venue.contact.email, "new_info": new_email},
            }
        }


class SerializeFieldsTest:
    def test_serialize_basic_fields(self):
        input_data = {"a": 1, "b": "str"}
        res = history_api.serialize_fields(input_data)
        assert res == {"a": "1", "b": "str"}

    def test_serialize_fields(self):
        criteria = criteria_factories.CriterionFactory.build_batch(3)
        input_data = {"int": 1, "str": "str", "list": [1, 2, 3], "set": {4, 5, 6}, "list_of_objects": criteria}

        res = history_api.serialize_fields(input_data)

        assert res == {
            "int": "1",
            "str": "str",
            "list": ["1", "2", "3"],
            "set": ["4", "5", "6"],
            "list_of_objects": [str(criterion) for criterion in criteria],
        }
