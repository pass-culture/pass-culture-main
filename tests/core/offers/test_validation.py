import pytest

from pcapi.model_creators.generic_creators import (
    create_user,
    create_offerer,
    create_user_offerer,
)
from pcapi.core.offers.validation import check_user_has_rights_on_offerer
from pcapi.models.api_errors import ApiErrors


class CheckUserHasRightsOnOffererTest:
    def test_should_raise_errors_when_user_offerer_is_not_validated(self):
        # Given
        user = create_user(is_admin=False)
        offerer = create_offerer()
        user_offerer = create_user_offerer(
            user=user, offerer=offerer, validation_token="ABCD"
        )

        # When
        with pytest.raises(ApiErrors) as errors:
            check_user_has_rights_on_offerer(user_offerer=user_offerer)

        # Then
        assert errors.value.errors == {
            "global": [
                "Vous n'avez pas les droits d'accès"
                " suffisant pour accéder à cette information."
            ]
        }

    def test_should_raise_errors_when_no_user_offerer(self):
        # Given
        user_offerer = None

        # When
        with pytest.raises(ApiErrors) as errors:
            check_user_has_rights_on_offerer(user_offerer=user_offerer)

        # Then
        assert errors.value.errors == {
            "global": [
                "Vous n'avez pas les droits d'accès"
                " suffisant pour accéder à cette information."
            ]
        }
