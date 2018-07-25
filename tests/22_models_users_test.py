import pytest
from sqlalchemy.exc import IntegrityError

from models import User, PcObject


def test_01_cannot_create_admin_that_can_book(app):
    #Given
    user = User()
    user.publicName = 'Admin CanBook'
    user.email = 'admin_can_book@email.com'
    user.setPassword('testpsswd')
    user.departementCode = '93'
    user.isAdmin = True
    user.canBookFreeOffers = True

    #When
    with pytest.raises(IntegrityError):
        PcObject.check_and_save(user)