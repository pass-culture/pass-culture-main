import pytest

from models import ApiErrors, User, PcObject
from tests.conftest import clean_database


@pytest.mark.standalone
@clean_database
def test_cannot_create_admin_that_can_book(app):
    #Given
    user = User()
    user.publicName = 'Admin CanBook'
    user.email = 'admin_can_book@email.com'
    user.setPassword('testpsswd')
    user.departementCode = '93'
    user.isAdmin = True
    user.canBookFreeOffers = True

    #When
    with pytest.raises(ApiErrors):
        PcObject.check_and_save(user)
