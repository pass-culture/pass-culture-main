import pytest

from pcapi.core.users import factories as users_factories
from pcapi.domain.users import UnauthorizedForAdminUser
from pcapi.domain.users import check_is_authorized_to_access_bookings_recap


class CheckUserIsNotAdminTest:
    def test_when_user_is_admin_should_prevent_from_accessing_bookings_list(self):
        # Given
        user = users_factories.AdminFactory.build()

        # When
        with pytest.raises(UnauthorizedForAdminUser) as exception:
            check_is_authorized_to_access_bookings_recap(user)

        # Then
        assert exception.value.errors["global"] == [
            "Le statut d'administrateur ne permet pas d'accéder au suivi des réservations"
        ]

    def test_when_user_is_not_admin_should_allow_accessing_bookings_list(self):
        # Given
        user = users_factories.UserFactory.build(isAdmin=False, isBeneficiary=False)

        # When
        check_is_authorized_to_access_bookings_recap(user)

        # Then
        assert True
