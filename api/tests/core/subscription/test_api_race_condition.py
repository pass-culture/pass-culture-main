import threading

from dateutil.relativedelta import relativedelta
import flask
import pytest
import time_machine

from pcapi import settings
from pcapi.core.finance import deposit_api
from pcapi.core.finance import models as finance_models
from pcapi.core.fraud import factories as fraud_factories
from pcapi.core.subscription import api as subscription_api
from pcapi.core.users import factories as users_factories
from pcapi.core.users import models as users_models
from pcapi.models import db


def activate_beneficiary_thread_safely(
    app: flask.Flask,
    user_id: int,
    barrier: threading.Barrier,
    event_to_set: threading.Event | None = None,
    event_to_wait: threading.Event | None = None,
) -> None:
    with app.app_context():
        # Flask-SQLAlchemy sessions are already thread-safe because they are scoped to the current Flask context
        user = db.session.query(users_models.User).filter(users_models.User.id == user_id).one()

        barrier.wait(2)

        if event_to_wait:
            event_to_wait.wait(2)

        subscription_api.activate_beneficiary_if_no_missing_step(user)

        if event_to_set:
            event_to_set.set()


def recredit_users_thread_safely(
    app: flask.Flask,
    user_id: int,
    barrier: threading.Barrier,
    event_to_wait: threading.Event | None = None,
) -> None:
    with app.app_context():
        # recredit_users fetch the users to be recredited then paginate on the users
        # that means that minutes, or hours, can pass between the user being fetched and them being recredited
        barrier.wait(2)

        if event_to_wait:
            event_to_wait.wait(2)

        deposit_api.recredit_users_by_id([user_id])


@pytest.mark.usefixtures("clean_database")
class EligibilityActivationRaceConditionTest:
    def test_pre_decree_18_eligibility(self, app):
        before_decree = settings.CREDIT_V3_DECREE_DATETIME - relativedelta(days=1)
        birth_date = before_decree - relativedelta(years=18)
        user = users_factories.HonorStatementValidatedUserFactory(
            validatedBirthDate=birth_date, beneficiaryFraudChecks__dateCreated=before_decree
        )

        barrier = threading.Barrier(2)  # both threads must fetch the user before their activation
        first_activation_event = threading.Event()

        first_thread = threading.Thread(
            target=activate_beneficiary_thread_safely,
            args=[app, user.id],
            kwargs={"barrier": barrier, "event_to_set": first_activation_event},
        )
        second_thread = threading.Thread(
            target=activate_beneficiary_thread_safely,
            args=[app, user.id],
            kwargs={"barrier": barrier, "event_to_wait": first_activation_event},
        )

        first_thread.start()
        second_thread.start()

        first_thread.join()
        second_thread.join()

        db.session.refresh(user)
        assert user.is_beneficiary
        assert user.deposit.type == finance_models.DepositType.GRANT_18
        assert user.deposit.amount == 300
        assert not user.deposit.recredits
        assert user.recreditAmountToShow == 300

    def test_pre_decree_underage_to_18_with_recredit(self, app):
        last_year = settings.CREDIT_V3_DECREE_DATETIME - relativedelta(years=1, months=1)
        with time_machine.travel(last_year):
            user = users_factories.BeneficiaryFactory(age=17, deposit__type=finance_models.DepositType.GRANT_15_17)
        # Finish missing steps at 18 years old
        before_decree = settings.CREDIT_V3_DECREE_DATETIME - relativedelta(days=1)
        fraud_factories.ProfileCompletionFraudCheckFactory(
            user=user, eligibilityType=users_models.EligibilityType.AGE18, dateCreated=before_decree
        )
        fraud_factories.PhoneValidationFraudCheckFactory(user=user)
        user.phoneNumber = "+33600000000"
        fraud_factories.HonorStatementFraudCheckFactory(user=user)

        barrier = threading.Barrier(2)
        eighteen_years_old_activation_event = threading.Event()

        eighteen_years_old_activation_thread = threading.Thread(
            target=activate_beneficiary_thread_safely,
            args=[app, user.id],
            kwargs={"barrier": barrier, "event_to_set": eighteen_years_old_activation_event},
        )
        recredit_thread = threading.Thread(
            target=recredit_users_thread_safely,
            args=[app, user.id],
            kwargs={"barrier": barrier, "event_to_wait": eighteen_years_old_activation_event},
        )

        eighteen_years_old_activation_thread.start()
        recredit_thread.start()

        eighteen_years_old_activation_thread.join()
        recredit_thread.join()

        db.session.refresh(user)
        assert user.deposit.type == finance_models.DepositType.GRANT_18
        assert user.deposit.amount == 300
        assert not user.deposit.recredits
        assert user.recreditAmountToShow == 300
