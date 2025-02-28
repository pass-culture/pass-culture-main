import threading

from dateutil.relativedelta import relativedelta
import flask
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session
from sqlalchemy.orm import sessionmaker

from pcapi import settings
from pcapi.core.finance import models as finance_models
from pcapi.core.subscription import api as subscription_api
from pcapi.core.users import factories as users_factories
from pcapi.core.users import models as users_models
from pcapi.models import db
from pcapi.repository import transaction


def activate_beneficiary_thread_safely(
    app: flask.Flask,
    user_id: int,
    barrier: threading.Barrier,
    event_to_set: threading.Event | None = None,
    event_to_wait: threading.Event | None = None,
) -> None:
    with app.app_context():
        # Flask-SQLAlchemy sessions are already thread-safe because they are scoped to the current Flask context
        user = users_models.User.query.filter(users_models.User.id == user_id).one()

        barrier.wait()  # both threads must fetch the user before their activation

        if event_to_wait:
            event_to_wait.wait(2)

        is_user_activated = subscription_api.activate_beneficiary_if_no_missing_step(user)

        if event_to_set:
            event_to_set.set()


@pytest.mark.usefixtures("clean_database")
class EligibilityActivationRaceConditionTest:
    def test_pre_decree_18_eligibility(self, app):
        before_decree = settings.CREDIT_V3_DECREE_DATETIME - relativedelta(days=1)
        birth_date = before_decree - relativedelta(years=18)
        user = users_factories.HonorStatementValidatedUserFactory(
            validatedBirthDate=birth_date, beneficiaryFraudChecks__dateCreated=before_decree
        )

        barrier = threading.Barrier(2)
        first_activation_event = threading.Event()

        first_thread = threading.Thread(
            target=activate_beneficiary_thread_safely,
            args=[app, user.id, barrier],
            kwargs={"event_to_set": first_activation_event},
        )
        second_thread = threading.Thread(
            target=activate_beneficiary_thread_safely,
            args=[app, user.id, barrier],
            kwargs={"event_to_wait": first_activation_event},
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
