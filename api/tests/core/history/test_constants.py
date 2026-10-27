from pcapi.core.history import constants as history_constants


def test_action_type_to_string_is_exhaustive():
    assert set(history_constants.ActionType) == set(history_constants.ACTION_TYPE_TO_STRING)
