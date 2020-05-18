import pytest

from domain.password import _check_new_password_validity, _check_password_strength, validate_change_password_request, \
    check_password_validity
from models import UserSQLEntity, ApiErrors


class ValidateChangePasswordRequestTest:
    def test_change_password_raises_an_error_if_old_password_is_not_given_as_key_in_json(self):
        # given
        user = UserSQLEntity()
        user.setPassword('0ld__p455w0rd')
        json = {
            "newPassword": "N3w__p455w0rd"
        }

        # when
        with pytest.raises(ApiErrors) as api_errors:
            validate_change_password_request(json)

        # then
        assert api_errors.value.errors['oldPassword'] == ['Ancien mot de passe manquant']

    def test_change_password_raises_an_error_if_new_password_is_not_given_as_key_in_json(self):
        # given
        user = UserSQLEntity()
        user.setPassword('0ld__p455w0rd')
        json = {
            "oldPassword": "0ld__p455w0rd"
        }

        # when
        with pytest.raises(ApiErrors) as api_errors:
            validate_change_password_request(json)

        # then
        assert api_errors.value.errors['newPassword'] == ['Nouveau mot de passe manquant']

    def test_change_password_raises_an_error_if_old_password_has_no_value_in_json(self):
        # given
        user = UserSQLEntity()
        user.setPassword('0ld__p455w0rd')
        json = {
            "oldPassword": "",
            "newPassword": "N3w__p455w0rd"
        }

        # when
        with pytest.raises(ApiErrors) as api_errors:
            validate_change_password_request(json)

        # then
        assert api_errors.value.errors['oldPassword'] == ['Ancien mot de passe manquant']

    def test_change_password_raises_an_error_if_new_password_has_no_value_in_json(self):
        # given
        user = UserSQLEntity()
        user.setPassword('0ld__p455w0rd')
        json = {
            "oldPassword": "0ld__p455w0rd",
            "newPassword": ""
        }

        # when
        with pytest.raises(ApiErrors) as api_errors:
            validate_change_password_request(json)

        # then
        assert api_errors.value.errors['newPassword'] == ['Nouveau mot de passe manquant']

    def test_change_password_raises_an_error_if_no_password_is_provided(self):
        # given
        user = UserSQLEntity()
        user.setPassword('0ld__p455w0rd')
        json = {}

        # when
        with pytest.raises(ApiErrors) as api_errors:
            validate_change_password_request(json)

        # then
        assert api_errors.value.errors['newPassword'] == ['Nouveau mot de passe manquant']
        assert api_errors.value.errors['oldPassword'] == ['Ancien mot de passe manquant']


class CheckPasswordValidityTest:
    def test_should_raise_multiple_errors_at_once(self):
        # given
        user = UserSQLEntity()
        user.setPassword('weakpassword')
        new_password = 'weakpassword'
        old_password = 'weakpassword'

        # when
        with pytest.raises(ApiErrors) as api_errors:
            check_password_validity(new_password, old_password, user)

        # then
        assert api_errors.value.errors['newPassword'] == ['Ton mot de passe doit contenir au moins :\n'
                                                          '- 12 caractères\n'
                                                          '- Un chiffre\n'
                                                          '- Une majuscule et une minuscule\n'
                                                          '- Un caractère spécial',
                                                          'Ton nouveau mot de passe est identique à l’ancien.']


class CheckPasswordStrengthTest:
    @pytest.mark.parametrize('newPassword', [
        '_v4l1dP455sw0rd',
        '-v4l1dP455sw0rd',
        '&v4l1dP455sw0rd',
        '?v4l1dP455sw0rd',
        '~v4l1dP455sw0rd',
        '#v4l1dP455sw0rd',
        '|v4l1dP455sw0rd',
        '^v4l1dP455sw0rd',
        '@v4l1dP455sw0rd',
        '=v4l1dP455sw0rd',
        '+v4l1dP455sw0rd',
        '$v4l1dP455sw0rd',
        '<v4l1dP455sw0rd',
        '>v4l1dP455sw0rd',
        '%v4l1dP455sw0rd',
        '*v4l1dP455sw0rd',
        '!v4l1dP455sw0rd',
        ':v4l1dP455sw0rd',
        ';v4l1dP455sw0rd',
        ',v4l1dP455sw0rd',
        '.v4l1dP455sw0rd'
    ])
    def test_should_not_add_errors_when_password_is_valid(self, newPassword):
        api_errors = ApiErrors()
        _check_password_strength('newPassword', newPassword, api_errors)
        assert len(api_errors.errors) is 0

    @pytest.mark.parametrize('newPassword', [
        't00::5H0rt@',
        'n0upper_c4s3^letter',
        'NO-LOWER_CASE.L3TT3R',
        'MIXED.case-WITHOUT_digits',
        'MIXEDcaseWITHOUTSP3C14lchars'
    ])
    def test_should_add_errors_when_password_is_not_valid(self, newPassword):
        # given
        api_errors = ApiErrors()

        # when
        _check_password_strength('newPassword', newPassword, api_errors)

        # then
        assert api_errors.errors['newPassword'] == [
            'Ton mot de passe doit contenir au moins :\n'
            '- 12 caractères\n'
            '- Un chiffre\n'
            '- Une majuscule et une minuscule\n'
            '- Un caractère spécial'
        ]


class CheckNewPasswordValidityTest:
    def test_change_password_raises_and_error_if_old_password_does_not_match_existing_password(self):
        # given
        api_errors = ApiErrors()
        user = UserSQLEntity()
        user.setPassword('0ld__p455w0rd')
        old_password = 'ra4nd0m_p455w0rd'
        new_password = 'n3w__p455w0rd'

        # when
        _check_new_password_validity(user, old_password, new_password, api_errors)

        # then
        assert api_errors.errors['oldPassword'] == ['Ton ancien mot de passe est incorrect.']

    def test_change_password_raises_and_error_if_old_password_is_the_same_as_the_new_password(self):
        # given
        api_errors = ApiErrors()
        user = UserSQLEntity()
        user.setPassword('0ld__p455w0rd')
        old_password = '0ld__p455w0rd'
        new_password = '0ld__p455w0rd'

        # when
        _check_new_password_validity(user, old_password, new_password, api_errors)

        # then
        assert api_errors.errors['newPassword'] == ['Ton nouveau mot de passe est identique à l’ancien.']
