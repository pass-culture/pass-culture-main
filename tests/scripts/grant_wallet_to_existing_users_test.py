from datetime import datetime

from dateutil.relativedelta import relativedelta

from pcapi.core.payments.models import Deposit
from pcapi.core.users import factories as users_factories
from pcapi.core.users import models as users_models
from pcapi.repository import repository
from pcapi.scripts.grant_wallet_to_existing_users import grant_wallet_to_existing_users


def test_should_grant_wallet_to_existing_users(app, db_session):
    # given
    # The build method is explicitly called to avoid the deposit generation
    # which is done if the Factory saves the object.
    eighteen_years_in_the_past = datetime.now() - relativedelta(years=18, months=4)
    beneficiary = users_factories.UserFactory.build(dateOfBirth=eighteen_years_in_the_past, email="email@example.com")
    beneficiary_2 = users_factories.UserFactory.build(
        dateOfBirth=eighteen_years_in_the_past, email="email2@example.com"
    )
    repository.save(beneficiary, beneficiary_2)

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
