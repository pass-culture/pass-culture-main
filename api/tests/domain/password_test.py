import pytest

from pcapi.core.users.models import User
from pcapi.domain.password import compute_confirmation_password_violations
from pcapi.domain.password import compute_different_password_violations
from pcapi.domain.password import compute_old_password_valid_violations
from pcapi.domain.password import compute_password_rule_violations
from pcapi.domain.password import compute_password_strength_violations
from pcapi.domain.password import random_password
from pcapi.models.api_errors import ApiErrors


class RandomPasswordTest:
    def test_generate_a_valid_password(self):
        # Given
        password = random_password()

        # When
        violations = compute_password_strength_violations("password", password)

        # Then
        assert not violations


class CheckPasswordValidityTest:
    def test_should_raise_multiple_errors_at_once(self):
        # given
        user = User()
        user.setPassword("weakpassword")
        new_password = "weakpassword"
        new_confirmation_password = "weakConfirmationPassword"
        old_password = "weakpassword"

        # when
        violations = compute_password_rule_violations(new_password, new_confirmation_password, old_password, user)

        # then
        assert violations == {
            "newPassword": [
                "Le mot de passe doit contenir au moins :\n"
                "- 12 caractères\n"
                "- Un chiffre\n"
                "- Une majuscule et une minuscule\n"
                "- Un caractère spécial",
                "Le nouveau mot de passe est identique à l’ancien.",
            ],
            "newConfirmationPassword": ["Les deux mots de passe ne sont pas identiques."],
        }


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
            "]v4l1dP455sw0rd",
        ],
    )
    def test_should_not_add_errors_when_password_is_valid(self, newPassword):
        violations = compute_password_strength_violations("newPassword", newPassword)

        assert not violations

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
        # when
        violations = compute_password_strength_violations("newPassword", newPassword)

        # then
        assert violations == {
            "newPassword": [
                "Le mot de passe doit contenir au moins :\n"
                "- 12 caractères\n"
                "- Un chiffre\n"
                "- Une majuscule et une minuscule\n"
                "- Un caractère spécial"
            ]
        }


class EnsureConfirmationPasswordIsSameAsNewPasswordTest:
    def test_should_add_an_error_when_new_passwords_are_not_equals(self):
        # when
        violations = compute_confirmation_password_violations("goodNewPassword", "wrongNewConfirmationPassword")

        # then
        assert violations == {"newConfirmationPassword": ["Les deux mots de passe ne sont pas identiques."]}

    def test_should_not_add_an_error_when_new_passwords_are_equals(self):
        # when
        violations = compute_confirmation_password_violations("goodNewPassword", "goodNewPassword")

        # then
        assert not violations


class EnsureGivenOldPasswordIsCorrectTest:
    def test_change_password_should_add_an_error_if_old_password_does_not_match_existing_password(self):
        # given
        user = User()
        user.setPassword("0ld__p455w0rd")
        old_password = "ra4nd0m_p455w0rd"

        # when
        violations = compute_old_password_valid_violations(user, old_password)

        # then
        assert violations == {"oldPassword": ["Le mot de passe actuel est incorrect."]}


class EnsureNewPasswordIsDifertFromOldTest:
    def test_change_password_should_add_an_error_if_old_password_is_the_same_as_the_new_password(self):
        # given
        user = User()
        user.setPassword("0ld__p455w0rd")  # ggignore
        new_password = "0ld__p455w0rd"  # ggignore

        # when
        violations = compute_different_password_violations(user, new_password)

        # then
        assert violations == {"newPassword": ["Le nouveau mot de passe est identique à l’ancien."]}
