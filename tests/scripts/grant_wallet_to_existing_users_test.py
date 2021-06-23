from pcapi.core.testing import override_features
from pcapi.core.users.models import User
from pcapi.model_creators.generic_creators import create_user
from pcapi.models import Deposit
from pcapi.repository import repository
from pcapi.scripts.grant_wallet_to_existing_users import grant_wallet_to_existing_users


def test_should_grant_wallet_to_existing_users(app, db_session):
    # given
    beneficiary = create_user(email="email@example.com")
    beneficiary_2 = create_user(email="email2@example.com")

    repository.save(beneficiary, beneficiary_2)

    # when
    grant_wallet_to_existing_users([beneficiary.id, beneficiary_2.id])

    # then
    users = User.query.join(Deposit).with_entities(Deposit.amount, User.isBeneficiary, User.has_beneficiary_role).all()
    user_1 = users[0]
    user_2 = users[1]

    assert user_1.amount == 300
    assert user_1.isBeneficiary
    assert user_1.has_beneficiary_role
    assert user_2.amount == 300
    assert user_2.isBeneficiary
    assert user_2.has_beneficiary_role


@override_features(APPLY_BOOKING_LIMITS_V2=False)
def test_should_grant_wallet_to_existing_users_with_v1_deposit(app, db_session):
    # given
    beneficiary = create_user(email="email@example.com")
    beneficiary_2 = create_user(email="email2@example.com")

    repository.save(beneficiary, beneficiary_2)

    # when
    grant_wallet_to_existing_users([beneficiary.id, beneficiary_2.id])

    # then
    users = User.query.join(Deposit).with_entities(Deposit.amount, User.isBeneficiary, User.has_beneficiary_role).all()
    user_1 = users[0]
    user_2 = users[1]

    assert user_1.amount == 500
    assert user_1.isBeneficiary
    assert user_1.has_beneficiary_role
    assert user_2.amount == 500
    assert user_2.isBeneficiary
    assert user_2.has_beneficiary_role
