import pytest

from pcapi.core.users.models import User
from pcapi.domain.password import _ensure_confirmation_password_is_same_as_new_password
from pcapi.domain.password import _ensure_given_old_password_is_correct
from pcapi.domain.password import _ensure_new_password_is_different_from_old
from pcapi.domain.password import _ensure_new_password_is_strong_enough
from pcapi.domain.password import check_password_validity
from pcapi.domain.password import random_password
from pcapi.models.api_errors import ApiErrors


class RandomPasswordTest:
    def test_generate_a_valid_password(self):
        # Given
        errors = ApiErrors()

        # When
        password = random_password()

        # Then
        _ensure_new_password_is_strong_enough("password", password, errors)
        assert len(errors.errors) == 0


class CheckPasswordValidityTest:
    def test_should_raise_multiple_errors_at_once(self):
        # given
        user = User()
        user.setPassword("weakpassword")
        new_password = "weakpassword"
        new_confirmation_password = "weakConfirmationPassword"
        old_password = "weakpassword"

        # when
        with pytest.raises(ApiErrors) as api_errors:
            check_password_validity(new_password, new_confirmation_password, old_password, user)

        # then
        assert api_errors.value.errors["newPassword"] == [
            "Ton mot de passe doit contenir au moins :\n"
            "- 12 caractères\n"
            "- Un chiffre\n"
            "- Une majuscule et une minuscule\n"
            "- Un caractère spécial",
            "Ton nouveau mot de passe est identique à l’ancien.",
        ]

        assert api_errors.value.errors["newConfirmationPassword"] == ["Les deux mots de passe ne sont pas identiques."]


class EnsureNewPasswordIsStrongEnoughTest:
    @pytest.mark.parametrize(
        "newPassword",
        [
            "_v4l1dP455sw0rd",
            "-v4l1dP455sw0rd",
            "&v4l1dP455sw0rd",
            "?v4l1dP455sw0rd",
            "~v4l1dP455sw0rd",
            "#v4l1dP455sw0rd",
            "|v4l1dP455sw0rd",
            "^v4l1dP455sw0rd",
            "@v4l1dP455sw0rd",
            "=v4l1dP455sw0rd",
            "+v4l1dP455sw0rd",
            "$v4l1dP455sw0rd",
            "<v4l1dP455sw0rd",
            ">v4l1dP455sw0rd",
            "%v4l1dP455sw0rd",
            "*v4l1dP455sw0rd",
            "!v4l1dP455sw0rd",
            ":v4l1dP455sw0rd",
            ";v4l1dP455sw0rd",
            ",v4l1dP455sw0rd",
            ".v4l1dP455sw0rd",
            "{v4l1dP455sw0rd",
            "}v4l1dP455sw0rd",
            "(v4l1dP455sw0rd",
            ")v4l1dP455sw0rd",
            "\\v4l1dP455sw0rd",
            "/v4l1dP455sw0rd",
            '"v4l1dP455sw0rd',
            "'v4l1dP455sw0rd",
            "[v4l1dP455sw0rd",
            "`v4l1dP455sw0rd",
        ],
    )
    def test_should_not_add_errors_when_password_is_valid(self, newPassword):
        api_errors = ApiErrors()

        _ensure_new_password_is_strong_enough("newPassword", newPassword, api_errors)

        assert not api_errors.errors

    def test_should_not_add_errors_when_password_is_valid_2(self):
        api_errors = ApiErrors()

        _ensure_new_password_is_strong_enough("newPassword", "]v4l1dP455sw0rd", api_errors)

        assert not api_errors.errors

    @pytest.mark.parametrize(
        "newPassword",
        [
            "t00::5H0rt@",
            "n0upper_c4s3^letter",
            "NO-LOWER_CASE.L3TT3R",
            "MIXED.case-WITHOUT_digits",
            "MIXEDcaseWITHOUTSP3C14lchars",
        ],
    )
    def test_should_add_errors_when_password_is_not_valid(self, newPassword):
        # given
        api_errors = ApiErrors()

        # when
        _ensure_new_password_is_strong_enough("newPassword", newPassword, api_errors)

        # then
        assert api_errors.errors["newPassword"] == [
            "Ton mot de passe doit contenir au moins :\n"
            "- 12 caractères\n"
            "- Un chiffre\n"
            "- Une majuscule et une minuscule\n"
            "- Un caractère spécial"
        ]


class EnsureConfirmationPasswordIsSameAsNewPasswordTest:
    def test_should_add_an_error_when_new_passwords_are_not_equals(self):
        # given
        api_errors = ApiErrors()

        # when
        _ensure_confirmation_password_is_same_as_new_password(
            "goodNewPassword", "wrongNewConfirmationPassword", api_errors
        )

        # then
        assert api_errors.errors["newConfirmationPassword"] == ["Les deux mots de passe ne sont pas identiques."]

    def test_should_not_add_an_error_when_new_passwords_are_equals(self):
        # given
        api_errors = ApiErrors()

        # when
        _ensure_confirmation_password_is_same_as_new_password("goodNewPassword", "goodNewPassword", api_errors)

        # then
        assert not api_errors.errors


class EnsureGivenOldPasswordIsCorrectTest:
    def test_change_password_should_add_an_error_if_old_password_does_not_match_existing_password(self):
        # given
        api_errors = ApiErrors()
        user = User()
        user.setPassword("0ld__p455w0rd")
        old_password = "ra4nd0m_p455w0rd"

        # when
        _ensure_given_old_password_is_correct(user, old_password, api_errors)

        # then
        assert api_errors.errors["oldPassword"] == ["Ton ancien mot de passe est incorrect."]


class EnsureNewPasswordIsDifertFromOldTest:
    def test_change_password_should_add_an_error_if_old_password_is_the_same_as_the_new_password(self):
        # given
        api_errors = ApiErrors()
        user = User()
        user.setPassword("0ld__p455w0rd")
        new_password = "0ld__p455w0rd"

        # when
        _ensure_new_password_is_different_from_old(user, new_password, api_errors)

        # then
        assert api_errors.errors["newPassword"] == ["Ton nouveau mot de passe est identique à l’ancien."]
