from pcapi.core.testing import override_features
from pcapi.core.users import factories as users_factories
from pcapi.core.users import models as users_models
from pcapi.models import Deposit
from pcapi.scripts.grant_wallet_to_existing_users import grant_wallet_to_existing_users


def test_should_grant_wallet_to_existing_users(app, db_session):
    # given
    beneficiary = users_factories.BeneficiaryFactory(email="email@example.com")
    beneficiary_2 = users_factories.BeneficiaryFactory(email="email2@example.com")

    # when
    grant_wallet_to_existing_users([beneficiary.id, beneficiary_2.id])

    # then
    users = (
        users_models.User.query.join(Deposit)
        .with_entities(Deposit.amount, users_models.User.isBeneficiary, users_models.User.has_beneficiary_role)
        .all()
    )
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
    beneficiary = users_factories.BeneficiaryFactory(email="email@example.com")
    beneficiary_2 = users_factories.BeneficiaryFactory(email="email2@example.com")

    # when
    grant_wallet_to_existing_users([beneficiary.id, beneficiary_2.id])

    # then
    users = (
        users_models.User.query.join(Deposit)
        .with_entities(Deposit.amount, users_models.User.isBeneficiary, users_models.User.has_beneficiary_role)
        .all()
    )
    user_1 = users[0]
    user_2 = users[1]

    assert user_1.amount == 500
    assert user_1.isBeneficiary
    assert user_1.has_beneficiary_role
    assert user_2.amount == 500
    assert user_2.isBeneficiary
    assert user_2.has_beneficiary_role
