import pytest

from pcapi.domain.users import check_is_authorized_to_access_bookings_recap, UnauthorizedForAdminUser
from pcapi.model_creators.generic_creators import create_user


class CheckUserIsNotAdminTest:
    def test_when_user_is_admin_should_prevent_from_accessing_bookings_list(self):
        # Given
        user = create_user(is_admin=True, can_book_free_offers=False)

        # When
        with pytest.raises(UnauthorizedForAdminUser) as exception:
            check_is_authorized_to_access_bookings_recap(user)

        # Then
        assert exception.value.errors['global'] == ["Le statut d'administrateur ne permet"
                                                    " pas d'accéder au suivi des réservations"]

    def test_when_user_is_not_admin_should_allow_accessing_bookings_list(self):
        # Given
        user = create_user(is_admin=False, can_book_free_offers=False)

        # When
        check_is_authorized_to_access_bookings_recap(user)

        # Then
        assert True
