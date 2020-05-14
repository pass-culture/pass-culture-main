import pytest

from domain.password import check_new_password_validity, check_password_strength
from models import UserSQLEntity, ApiErrors


def test_change_password_raises_and_error_if_old_password_does_not_match_existing_password():
    # given
    user = UserSQLEntity()
    user.setPassword('0ld__p455w0rd')
    old_password = 'ra4nd0m_p455w0rd'
    new_password = 'n3w__p455w0rd'

    # when
    with pytest.raises(ApiErrors) as api_errors:
        check_new_password_validity(user, old_password, new_password)

    # then
    assert api_errors.value.errors['oldPassword'] == ['Ton ancien mot de passe est incorrect.']


def test_change_password_raises_and_error_if_old_password_is_the_same_as_the_new_password():
    # given
    user = UserSQLEntity()
    user.setPassword('0ld__p455w0rd')
    old_password = '0ld__p455w0rd'
    new_password = '0ld__p455w0rd'

    # when
    with pytest.raises(ApiErrors) as api_errors:
        check_new_password_validity(user, old_password, new_password)

    # then
    assert api_errors.value.errors['newPassword'] == ['Ton nouveau mot de passe est identique à l’ancien.']


@pytest.mark.parametrize('password', [
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
def test_valid_passwords(password):
    try:
        check_password_strength('password', password)
    except ApiErrors:
        assert False, 'This password=\'%s\' should be valid' % password


@pytest.mark.parametrize('password', [
    't00::5H0rt@',
    'n0upper_c4s3^letter',
    'NO-LOWER_CASE.L3TT3R',
    'MIXED.case-WITHOUT_digits',
    'MIXEDcaseWITHOUTSP3C14lchars'
])
def test_invalid_passwords(password):
    # when
    with pytest.raises(ApiErrors) as api_errors:
        check_password_strength('password', password)

    # then
    assert api_errors.value.errors['password'] == [
        'Ton mot de passe doit contenir au moins :\n'
        '- 12 caractères\n'
        '- Un chiffre\n'
        '- Une majuscule et une minuscule\n'
        '- Un caractère spécial'
    ]
