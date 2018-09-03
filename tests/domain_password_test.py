import pytest

from domain.password import change_password
from models import User, ApiErrors


@pytest.mark.standalone
def test_change_password_raises_and_error_if_old_password_does_not_match_existing_password():
    # given
    user = User()
    user.setPassword('0ld__p455w0rd')
    old_password = 'ra4nd0m_p455w0rd'
    new_password = 'n3w__p455w0rd'

    # when
    with pytest.raises(ApiErrors) as e:
        change_password(user, old_password, new_password)

    # then
    assert e.value.errors['oldPassword'] == ['Votre ancien mot de passe est incorrect']


@pytest.mark.standalone
def test_change_password_raises_and_error_if_old_password_is_the_same_as_the_new_password():
    # given
    user = User()
    user.setPassword('0ld__p455w0rd')
    old_password = '0ld__p455w0rd'
    new_password = '0ld__p455w0rd'

    # when
    with pytest.raises(ApiErrors) as e:
        change_password(user, old_password, new_password)

    # then
    assert e.value.errors['newPassword'] == ['Votre nouveau mot de passe est identique à l\'ancien']


@pytest.mark.standalone
def test_change_password_sets_the_new_password():
    # given
    user = User()
    user.setPassword('0ld__p455w0rd')
    old_password = '0ld__p455w0rd'
    new_password = 'n3w__p455w0rd'

    # when
    change_password(user, old_password, new_password)

    # then
    assert user.checkPassword(new_password) is True
