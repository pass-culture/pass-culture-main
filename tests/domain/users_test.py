import pytest

from domain.users import check_user_is_not_admin, UnauthorizedForAdminUser
from tests.model_creators.generic_creators import create_user


class CheckUserIsNotAdminTest:
    def test_when_user_is_admin_should_raise_unauthorizedforadminuser(self):
        # Given
        user = create_user(is_admin=True, can_book_free_offers=False)

        # When
        with pytest.raises(UnauthorizedForAdminUser) as exception:
            check_user_is_not_admin(user)

        # Then
        assert exception.value.errors['global'] == ["Le statut d'administrateur ne permet"
                                                    " pas d'accéder au suivi des réservations"]

    def test_when_user_is_not_admin_should_not_raise_unauthorizedforadminuser(self):
        # Given
        user = create_user(is_admin=False, can_book_free_offers=False)

        # When
        check_user_is_not_admin(user)

        # Then
        assert True
