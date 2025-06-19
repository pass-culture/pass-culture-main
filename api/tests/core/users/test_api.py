import dataclasses
import datetime
import json
import logging
import os
import pathlib
import zipfile
from decimal import Decimal
from unittest import mock

import fakeredis
import pytest
import time_machine
from dateutil.relativedelta import relativedelta
from flask import current_app
from flask_jwt_extended.utils import decode_token

import pcapi.core.fraud.factories as fraud_factories
import pcapi.core.fraud.models as fraud_models
import pcapi.core.mails.testing as mails_testing
from pcapi import settings
from pcapi.connectors.dms import models as dms_models
from pcapi.core import token as token_utils
from pcapi.core.bookings import api as bookings_api
from pcapi.core.bookings import factories as bookings_factories
from pcapi.core.bookings import models as bookings_models
from pcapi.core.bookings.models import BookingStatus
from pcapi.core.categories import subcategories
from pcapi.core.chronicles import factories as chronicles_factories
from pcapi.core.chronicles import models as chronicles_models
from pcapi.core.finance import api as finance_api
from pcapi.core.finance import factories as finance_factories
from pcapi.core.finance import models as finance_models
from pcapi.core.geography import api as geography_api
from pcapi.core.geography import models as geography_models
from pcapi.core.history import factories as history_factories
from pcapi.core.history import models as history_models
from pcapi.core.mails.transactional.sendinblue_template_ids import TransactionalEmail
from pcapi.core.offerers import factories as offerers_factories
from pcapi.core.offers import factories as offers_factories
from pcapi.core.subscription import api as subscription_api
from pcapi.core.testing import assert_num_queries
from pcapi.core.users import api as users_api
from pcapi.core.users import constants as users_constants
from pcapi.core.users import exceptions as users_exceptions
from pcapi.core.users import factories as users_factories
from pcapi.core.users import models as users_models
from pcapi.core.users import testing as sendinblue_testing
from pcapi.core.users.email import update as email_update
from pcapi.models import db
from pcapi.models.validation_status_mixin import ValidationStatus
from pcapi.notifications.push import testing as batch_testing
from pcapi.routes.native.v1.serialization import account as account_serialization
from pcapi.routes.serialization import users as users_serialization

import tests
from tests.test_utils import StorageFolderManager


DATA_DIR = pathlib.Path(tests.__path__[0]) / "files"
pytestmark = pytest.mark.usefixtures("db_session")


def _datetime_within_last_5sec(when: datetime.datetime) -> bool:
    return datetime.datetime.utcnow() - relativedelta(seconds=5) < when < datetime.datetime.utcnow()


def _assert_user_action_history_as_expected(
    action: history_models.ActionHistory,
    user: users_models.User,
    author: users_models.User,
    actionType: history_models.ActionType,
    reason: users_constants.SuspensionReason,
    comment: str | None = None,
):
    assert action.user == user
    assert action.authorUser == author
    assert action.actionType == actionType
    if reason:
        assert action.extraData["reason"] == reason.value
    else:
        assert action.extraData == {}
    assert action.comment == comment


def _assert_user_is_anonymized(user):
    assert user.email == f"anonymous_{user.id}@anonymized.passculture"
    assert user.password == b"Anonymized"
    assert user.firstName is None
    assert user.lastName is None
    assert user.married_name is None
    assert user.postalCode is None
    assert user.phoneNumber is None
    assert user.address is None
    assert user.city is None
    assert user.externalIds == []
    assert user.idPieceNumber is None
    assert user.login_device_history == []
    assert user.email_history == []
    assert user.trusted_devices == []
    assert user.roles == [users_models.UserRole.ANONYMIZED]
    assert len(user.action_history) == 1
    assert user.action_history[0].actionType == history_models.ActionType.USER_ANONYMIZED
    assert user.action_history[0].authorUserId is None


@pytest.mark.usefixtures("db_session")
class CancelBeneficiaryBookingsOnSuspendAccountTest:
    @pytest.mark.parametrize(
        "reason,is_backoffice_action",
        [
            (users_constants.SuspensionReason.UPON_USER_REQUEST, False),
            (users_constants.SuspensionReason.FRAUD_RESELL_PRODUCT, True),
            (users_constants.SuspensionReason.FRAUD_SUSPICION, True),
            (users_constants.SuspensionReason.FRAUD_USURPATION, True),
        ],
    )
    def should_cancel_booking_when_the_offer_is_a_thing(self, reason, is_backoffice_action):
        booking_thing = bookings_factories.BookingFactory(
            stock__offer__subcategoryId=subcategories.CARTE_CINE_ILLIMITE.id,
            status=BookingStatus.CONFIRMED,
        )

        author = users_factories.AdminFactory()

        users_api.suspend_account(
            booking_thing.user, reason=reason, actor=author, is_backoffice_action=is_backoffice_action
        )

        assert booking_thing.status is BookingStatus.CANCELLED

    @pytest.mark.parametrize(
        "reason", [users_constants.SuspensionReason.FRAUD_SUSPICION, users_constants.SuspensionReason.FRAUD_USURPATION]
    )
    def should_not_cancel_booking_on_suspicion_when_the_offer_is_an_event(self, reason):
        booking_thing = bookings_factories.BookingFactory(stock=offers_factories.EventStockFactory())

        author = users_factories.AdminFactory()

        users_api.suspend_account(booking_thing.user, reason=reason, actor=author, is_backoffice_action=True)

        assert booking_thing.status is BookingStatus.CONFIRMED

    @pytest.mark.parametrize(
        "reason,is_backoffice_action",
        [
            (users_constants.SuspensionReason.UPON_USER_REQUEST, False),
            (users_constants.SuspensionReason.FRAUD_RESELL_PRODUCT, True),
        ],
    )
    def should_cancel_booking_when_event_is_still_cancellable(self, reason, is_backoffice_action):
        """
        ---[        cancellable       ][         not cancellable        ]-->
        ---|---------------------------|--------------------------------|-->
        booking date         date cancellation limit                event date

        -----------------|------------------------------------------------->
                        now
        """
        in_the_past = datetime.datetime.utcnow() - relativedelta(days=1)
        in_the_future = datetime.datetime.utcnow() + relativedelta(days=1)
        booking_event = bookings_factories.BookingFactory(
            stock__offer__subcategoryId=subcategories.SEANCE_CINE.id,
            status=BookingStatus.CONFIRMED,
            dateCreated=in_the_past,
            cancellationLimitDate=in_the_future,
        )

        author = users_factories.AdminFactory()

        users_api.suspend_account(
            booking_event.user, reason=reason, actor=author, is_backoffice_action=is_backoffice_action
        )

        assert booking_event.status is BookingStatus.CANCELLED

    def should_not_cancel_event_when_cancellation_limit_date_is_past(self):
        """
        ---[        cancellable       ][         not cancellable        ]-->
        ---|---------------------------|--------------------------------|-->
        booking date         date cancellation limit                event date

        -------------------------------------------------|----------------->
                                                        now
        """
        in_the_past = datetime.datetime.utcnow() - relativedelta(seconds=1)
        further_in_the_past = datetime.datetime.utcnow() - relativedelta(days=3)
        booking_event = bookings_factories.BookingFactory(
            stock__offer__subcategoryId=subcategories.SEANCE_CINE.id,
            status=BookingStatus.CONFIRMED,
            dateCreated=further_in_the_past,
            cancellationLimitDate=in_the_past,
        )

        author = users_factories.AdminFactory()
        reason = users_constants.SuspensionReason.UPON_USER_REQUEST

        users_api.suspend_account(booking_event.user, reason=reason, actor=author)

        assert booking_event.status is BookingStatus.CONFIRMED


@pytest.mark.usefixtures("db_session")
class SuspendAccountTest:
    def test_suspend_admin(self):
        user = users_factories.AdminFactory()
        users_factories.UserSessionFactory(user=user)
        reason = users_constants.SuspensionReason.FRAUD_RESELL_PRODUCT
        author = users_factories.AdminFactory()

        users_api.suspend_account(user, reason=reason, actor=author, is_backoffice_action=True)

        assert user.suspension_reason == reason
        assert _datetime_within_last_5sec(user.suspension_date)
        assert not user.isActive
        assert not user.has_admin_role
        assert not db.session.query(users_models.UserSession).filter_by(userId=user.id).first()
        assert author.isActive

        history = db.session.query(history_models.ActionHistory).filter_by(userId=user.id).all()
        assert len(history) == 1
        _assert_user_action_history_as_expected(
            history[0], user, author, history_models.ActionType.USER_SUSPENDED, reason
        )

        assert len(sendinblue_testing.sendinblue_requests) == 1
        assert sendinblue_testing.sendinblue_requests[0]["email"] == user.email
        assert sendinblue_testing.sendinblue_requests[0]["action"] == "delete"

    def test_suspend_beneficiary(self):
        user = users_factories.BeneficiaryGrant18Factory()
        cancellable_booking = bookings_factories.BookingFactory(user=user)
        yesterday = datetime.datetime.utcnow() - datetime.timedelta(days=1)
        confirmed_booking = bookings_factories.BookingFactory(
            user=user, cancellation_limit_date=yesterday, status=BookingStatus.CONFIRMED
        )
        used_booking = bookings_factories.UsedBookingFactory(user=user)
        author = users_factories.AdminFactory()
        reason = users_constants.SuspensionReason.FRAUD_RESELL_PRODUCT
        comment = "Dossier n°12345"
        old_password_hash = user.password

        users_api.suspend_account(user, reason=reason, actor=author, comment=comment, is_backoffice_action=True)

        db.session.refresh(user)

        assert not user.isActive
        assert user.password == old_password_hash
        assert user.suspension_reason == reason
        assert _datetime_within_last_5sec(user.suspension_date)

        assert cancellable_booking.status is BookingStatus.CANCELLED
        assert confirmed_booking.status is BookingStatus.CONFIRMED
        assert used_booking.status is BookingStatus.USED

        history = db.session.query(history_models.ActionHistory).filter_by(userId=user.id).all()
        assert len(history) == 1
        _assert_user_action_history_as_expected(
            history[0], user, author, history_models.ActionType.USER_SUSPENDED, reason, comment
        )

        assert len(sendinblue_testing.sendinblue_requests) == 2
        # update venue attributes after booking is canceled
        assert sendinblue_testing.sendinblue_requests[0]["email"] == cancellable_booking.venue.bookingEmail
        assert len(sendinblue_testing.sendinblue_requests[0]["attributes"]) > 0
        # delete suspended user contact
        assert sendinblue_testing.sendinblue_requests[1]["email"] == user.email
        assert sendinblue_testing.sendinblue_requests[1]["action"] == "delete"

    def test_suspend_pro(self):
        booking = bookings_factories.BookingFactory()
        pro = offerers_factories.UserOffererFactory(offerer=booking.offerer).user
        author = users_factories.AdminFactory()
        reason = users_constants.SuspensionReason.END_OF_CONTRACT

        users_api.suspend_account(pro, reason=reason, actor=author, is_backoffice_action=True)

        assert not pro.isActive
        assert booking.status is BookingStatus.CONFIRMED  # not canceled

        history = db.session.query(history_models.ActionHistory).filter_by(userId=pro.id).all()
        assert len(history) == 1
        _assert_user_action_history_as_expected(
            history[0], pro, author, history_models.ActionType.USER_SUSPENDED, reason
        )

        assert len(sendinblue_testing.sendinblue_requests) == 1
        assert sendinblue_testing.sendinblue_requests[0]["email"] == pro.email
        assert sendinblue_testing.sendinblue_requests[0]["action"] == "delete"

    def should_change_password_when_user_is_suspended_for_suspicious_login(self):
        user = users_factories.UserFactory()
        old_password_hash = user.password

        users_api.suspend_account(
            user, reason=users_constants.SuspensionReason.SUSPICIOUS_LOGIN_REPORTED_BY_USER, actor=user
        )

        assert user.password != old_password_hash

    @pytest.mark.parametrize(
        "reason",
        [
            users_constants.SuspensionReason.FRAUD_SUSPICION,
            users_constants.SuspensionReason.UPON_USER_REQUEST,
            users_constants.SuspensionReason.SUSPENSION_FOR_INVESTIGATION_TEMP,
            users_constants.SuspensionReason.FRAUD_USURPATION,
        ],
    )
    def should_not_change_password_when_user_is_suspended_for_reason_other_than_suspicious_login(self, reason):
        user = users_factories.UserFactory()
        old_password_hash = user.password

        users_api.suspend_account(user, reason=reason, actor=user)

        assert user.password == old_password_hash


class UnsuspendAccountTest:
    def test_unsuspend_account(self):
        user = users_factories.UserFactory(isActive=False)
        author = users_factories.AdminFactory()

        comment = "Confusion avec un homonyme"
        users_api.unsuspend_account(user, author, comment=comment)

        assert not user.suspension_reason
        assert not user.suspension_date
        assert user.isActive

        history = db.session.query(history_models.ActionHistory).filter_by(userId=user.id).all()
        assert len(history) == 1
        _assert_user_action_history_as_expected(
            history[0], user, author, history_models.ActionType.USER_UNSUSPENDED, reason=None, comment=comment
        )

        assert len(sendinblue_testing.sendinblue_requests) == 1
        assert sendinblue_testing.sendinblue_requests[0]["email"] == user.email
        assert len(sendinblue_testing.sendinblue_requests[0]["attributes"]) > 0

    def should_send_reset_password_email_when_user_is_suspended_for_suspicious_login(self):
        user = users_factories.UserFactory(isActive=False)
        history_factories.SuspendedUserActionHistoryFactory(
            user=user, reason=users_constants.SuspensionReason.SUSPICIOUS_LOGIN_REPORTED_BY_USER
        )
        author = users_factories.AdminFactory()

        users_api.unsuspend_account(user, author)

        assert len(mails_testing.outbox) == 1
        assert mails_testing.outbox[0]["template"] == dataclasses.asdict(
            TransactionalEmail.NEW_PASSWORD_REQUEST_FOR_SUSPICIOUS_LOGIN.value
        )
        assert mails_testing.outbox[0]["params"]["RESET_PASSWORD_LINK"]

    @pytest.mark.parametrize(
        "reason",
        [
            users_constants.SuspensionReason.FRAUD_SUSPICION,
            users_constants.SuspensionReason.UPON_USER_REQUEST,
            users_constants.SuspensionReason.SUSPENSION_FOR_INVESTIGATION_TEMP,
            users_constants.SuspensionReason.FRAUD_FAKE_DOCUMENT,
        ],
    )
    def should_not_send_reset_password_email_when_user_is_suspended_for_reason_other_than_suspicious_login(
        self, reason
    ):
        user = users_factories.UserFactory(isActive=False)
        history_factories.SuspendedUserActionHistoryFactory(user=user, reason=reason)
        author = users_factories.AdminFactory()

        users_api.unsuspend_account(user, author)

        assert len(mails_testing.outbox) == 0


@pytest.mark.usefixtures("db_session")
class ChangeUserEmailTest:
    old_email = "oldemail@mail.com"
    new_email = "newemail@mail.com"
    mock_redis_client = fakeredis.FakeStrictRedis()

    def _init_token(self, user):
        return token_utils.Token.create(
            token_utils.TokenType.EMAIL_CHANGE_VALIDATION,
            users_constants.EMAIL_CHANGE_TOKEN_LIFE_TIME,
            user.id,
            {"new_email": self.new_email},
        ).encoded_token

    def test_change_user_email(self):
        # Given
        user = users_factories.UserFactory(email=self.old_email, firstName="UniqueNameForEmailChangeTest")
        users_factories.SingleSignOnFactory(user=user)
        users_factories.UserSessionFactory(user=user)

        token = self._init_token(user)
        # When
        returned_user = email_update.validate_email_update_request(token)

        # Then
        reloaded_user = db.session.get(users_models.User, user.id)
        assert returned_user == reloaded_user
        assert reloaded_user.email == self.new_email
        assert db.session.query(users_models.User).filter_by(email=self.old_email).first() is None
        assert db.session.query(users_models.UserSession).filter_by(userId=reloaded_user.id).first() is None
        assert db.session.query(users_models.SingleSignOn).filter_by(userId=reloaded_user.id).first() is None

        assert len(reloaded_user.email_history) == 1

        history = reloaded_user.email_history[0]
        assert history.oldEmail == self.old_email
        assert history.newEmail == self.new_email
        assert history.eventType == users_models.EmailHistoryEventTypeEnum.VALIDATION
        assert history.id is not None

    def test_change_user_email_new_email_already_existing(self):
        # Given
        user = users_factories.UserFactory(email=self.old_email, firstName="UniqueNameForEmailChangeTest")
        users_factories.SingleSignOnFactory(user=user)
        other_user = users_factories.UserFactory(email=self.new_email)
        token = self._init_token(user)

        # When
        with pytest.raises(users_exceptions.EmailExistsError):
            email_update.validate_email_update_request(token)

        # Then
        user = db.session.get(users_models.User, user.id)
        assert user.email == "oldemail@mail.com"

        other_user = db.session.get(users_models.User, other_user.id)
        assert other_user.email == self.new_email

        single_sign_on = (
            db.session.query(users_models.SingleSignOn)
            .filter(users_models.SingleSignOn.userId == user.id)
            .one_or_none()
        )
        assert single_sign_on is not None

    def test_change_user_email_expired_token(self, app):
        # Given
        user = users_factories.UserFactory(email=self.old_email, firstName="UniqueNameForEmailChangeTest")
        users_factories.UserSessionFactory(user=user)
        with mock.patch("flask.current_app.redis_client", self.mock_redis_client):
            with time_machine.travel("2021-01-01"):
                token = self._init_token(user)

            # When
            with time_machine.travel("2021-01-03"):
                with pytest.raises(users_exceptions.InvalidToken):
                    email_update.validate_email_update_request(token)

                # Then
                user = db.session.get(users_models.User, user.id)
                assert user.email == self.old_email

    def test_change_user_email_twice(self):
        """
        Test that when the function is called twice:
            1. no error is raised
            2. no email updated is performed (email history stays the
               same)
        Update has been done, no need to panic.
        """

        user = users_factories.UserFactory(email=self.old_email)
        users_factories.UserSessionFactory(user=user)
        token = self._init_token(user)

        # first call, email is updated as expected
        returned_user = email_update.validate_email_update_request(token)

        reloaded_user = db.session.get(users_models.User, user.id)
        assert returned_user == reloaded_user
        assert reloaded_user.email == self.new_email

        # second call, no error, no update
        returned_user = email_update.validate_email_update_request(token)
        reloaded_user = db.session.get(users_models.User, user.id)
        assert returned_user == reloaded_user
        assert reloaded_user.email == self.new_email

    def test_validating_email_updates_external_contact(self):
        # Given
        user = users_factories.UserFactory(email=self.old_email, firstName="UniqueNameForEmailChangeTest")
        users_factories.UserSessionFactory(user=user)

        token = self._init_token(user)
        # When
        email_update.validate_email_update_request(token)

        assert sendinblue_testing.sendinblue_requests == [
            {
                "email": self.old_email,
                "attributes": {"EMAIL": self.new_email},
                "emailBlacklisted": False,
                "use_pro_subaccount": False,
            }
        ]


class CreateBeneficiaryTest:
    def test_with_eligible_user(self):
        user = users_factories.UserFactory(roles=[])
        fraud_check = fraud_factories.BeneficiaryFraudCheckFactory(
            user=user, type=fraud_models.FraudCheckType.UBBLE, status=fraud_models.FraudCheckStatus.OK
        )
        user = subscription_api.activate_beneficiary_for_eligibility(
            user, fraud_check.get_detailed_source(), users_models.EligibilityType.AGE18
        )
        assert user.has_beneficiary_role
        assert len(user.deposits) == 1

    def test_with_eligible_underage_user(self):
        user = users_factories.UserFactory(
            roles=[], validatedBirthDate=datetime.date.today() - relativedelta(years=16, months=4)
        )
        fraud_check = fraud_factories.BeneficiaryFraudCheckFactory(
            user=user,
            type=fraud_models.FraudCheckType.EDUCONNECT,
            status=fraud_models.FraudCheckStatus.OK,
            eligibilityType=users_models.EligibilityType.UNDERAGE,
            resultContent=fraud_factories.EduconnectContentFactory(registration_datetime=datetime.datetime.utcnow()),
        )
        user = subscription_api.activate_beneficiary_for_eligibility(
            user, fraud_check.get_detailed_source(), users_models.EligibilityType.UNDERAGE
        )
        assert user.has_underage_beneficiary_role
        assert len(user.deposits) == 1
        assert user.has_active_deposit
        assert user.deposit.amount == 30

    def test_apps_flyer_called_for_underage_beneficiary(self, requests_mock):
        apps_flyer_data = {
            "apps_flyer": {"user": "some-user-id", "platform": "ANDROID"},
            "firebase_pseudo_id": "firebase_pseudo_id",
        }
        user = users_factories.UserFactory(
            externalIds=apps_flyer_data, validatedBirthDate=datetime.date.today() - relativedelta(years=16, months=4)
        )
        fraud_check = fraud_factories.BeneficiaryFraudCheckFactory(
            user=user,
            type=fraud_models.FraudCheckType.UBBLE,
            status=fraud_models.FraudCheckStatus.OK,
            eligibilityType=users_models.EligibilityType.UNDERAGE,
        )
        posted = requests_mock.post("https://api2.appsflyer.com/inappevent/app.passculture.webapp")
        user = subscription_api.activate_beneficiary_for_eligibility(
            user, fraud_check.get_detailed_source(), users_models.EligibilityType.UNDERAGE
        )

        first_request, second_request, third_request = posted.request_history
        assert first_request.json() == {
            "appsflyer_id": "some-user-id",
            "eventName": "af_complete_beneficiary",
            "eventValue": {
                "af_user_id": str(user.id),
                "af_firebase_pseudo_id": "firebase_pseudo_id",
                "type": "GRANT_15_17",
            },
        }
        assert second_request.json() == {
            "appsflyer_id": "some-user-id",
            "eventName": "af_complete_beneficiary_underage",
            "eventValue": {
                "af_user_id": str(user.id),
                "af_firebase_pseudo_id": "firebase_pseudo_id",
                "type": "GRANT_15_17",
            },
        }
        assert third_request.json() == {
            "appsflyer_id": "some-user-id",
            "eventName": "af_complete_beneficiary_16",
            "eventValue": {
                "af_user_id": str(user.id),
                "af_firebase_pseudo_id": "firebase_pseudo_id",
                "type": "GRANT_15_17",
            },
        }

        assert user.has_underage_beneficiary_role
        assert len(user.deposits) == 1

    def test_apps_flyer_called_for_eighteen_beneficiary(self, requests_mock):
        apps_flyer_data = {
            "apps_flyer": {"user": "some-user-id", "platform": "ANDROID"},
            "firebase_pseudo_id": "firebase_pseudo_id",
        }
        user = users_factories.UserFactory(externalIds=apps_flyer_data)
        fraud_check = fraud_factories.BeneficiaryFraudCheckFactory(
            user=user, type=fraud_models.FraudCheckType.UBBLE, status=fraud_models.FraudCheckStatus.OK
        )
        posted = requests_mock.post("https://api2.appsflyer.com/inappevent/app.passculture.webapp")
        user = subscription_api.activate_beneficiary_for_eligibility(
            user, fraud_check.get_detailed_source(), users_models.EligibilityType.AGE18
        )

        first_request, second_request = posted.request_history
        assert first_request.json() == {
            "appsflyer_id": "some-user-id",
            "eventName": "af_complete_beneficiary",
            "eventValue": {
                "af_user_id": str(user.id),
                "af_firebase_pseudo_id": "firebase_pseudo_id",
                "type": "GRANT_18",
            },
        }
        assert second_request.json() == {
            "appsflyer_id": "some-user-id",
            "eventName": "af_complete_beneficiary_18",
            "eventValue": {
                "af_user_id": str(user.id),
                "af_firebase_pseudo_id": "firebase_pseudo_id",
                "type": "GRANT_18",
            },
        }

        assert user.has_beneficiary_role
        assert len(user.deposits) == 1

    def test_external_users_updated(self):
        user = users_factories.UserFactory(roles=[])
        fraud_check = fraud_factories.BeneficiaryFraudCheckFactory(
            user=user, type=fraud_models.FraudCheckType.UBBLE, status=fraud_models.FraudCheckStatus.OK
        )
        subscription_api.activate_beneficiary_for_eligibility(
            user, fraud_check.get_detailed_source(), users_models.EligibilityType.AGE18
        )

        assert len(batch_testing.requests) == 3
        assert len(sendinblue_testing.sendinblue_requests) == 1

        trigger_event_log = batch_testing.requests[2]
        assert trigger_event_log["user_id"] == user.id
        assert trigger_event_log["event_name"] == "user_deposit_activated"
        assert trigger_event_log["event_payload"] == {"deposit_type": "GRANT_18", "deposit_amount": 300}

    def test_15yo_that_started_at_14_is_activated(self):
        fifteen_years_and_one_week_ago = datetime.datetime.utcnow() - relativedelta(years=15, weeks=1)
        one_month_ago = datetime.datetime.utcnow() - relativedelta(months=1)

        fifteen_year_old = users_factories.UserFactory(validatedBirthDate=fifteen_years_and_one_week_ago)

        fraud_check = fraud_factories.BeneficiaryFraudCheckFactory(
            user=fifteen_year_old,
            type=fraud_models.FraudCheckType.EDUCONNECT,
            status=fraud_models.FraudCheckStatus.OK,
            eligibilityType=users_models.EligibilityType.UNDERAGE,
            resultContent=fraud_factories.EduconnectContentFactory(registration_datetime=one_month_ago),
        )

        subscription_api.activate_beneficiary_for_eligibility(
            fifteen_year_old, fraud_check.get_detailed_source(), users_models.EligibilityType.UNDERAGE
        )

        assert fifteen_year_old.is_beneficiary
        assert fifteen_year_old.deposit.amount == 20

    def test_user_ex_underage_gets_remaining_amount_transferred_even_if_expired(self):
        # No time_travel for user creation here, because there is a call to get_wallet_ballance (which is a database function) in activate_beneficiary_for_eligibility.
        # The database has its own time, ignoring all time_travel shenanigans.
        a_year_go = datetime.datetime.utcnow() - relativedelta(years=1)
        user = users_factories.BeneficiaryFactory(
            validatedBirthDate=a_year_go - relativedelta(years=17),
            roles=[users_models.UserRole.UNDERAGE_BENEFICIARY],
            dateCreated=a_year_go,
            deposit__type=finance_models.DepositType.GRANT_15_17,
            deposit__amount=30,
            deposit__dateCreated=a_year_go,
        )
        bookings_factories.BookingFactory(user=user, amount=20)

        # Mock an expired deposit
        user.deposit.expirationDate = datetime.datetime.utcnow() - relativedelta(days=1)

        # Finish steps for 18yo user
        id_fraud_check = fraud_factories.BeneficiaryFraudCheckFactory(
            user=user, status=fraud_models.FraudCheckStatus.OK, type=fraud_models.FraudCheckType.UBBLE
        )
        user.phoneNumber = "+33612345678"
        fraud_factories.HonorStatementFraudCheckFactory(user=user)

        subscription_api.activate_beneficiary_for_eligibility(
            user, id_fraud_check.get_detailed_source(), users_models.EligibilityType.AGE17_18
        )

        assert user.deposit.type == finance_models.DepositType.GRANT_17_18
        assert user.deposit.amount == 150 + 30
        assert len(user.deposit.bookings) == 1  # The booking was transferred


@pytest.mark.usefixtures("db_session")
class SetProTutoAsSeenTest:
    def should_set_has_seen_pro_tutorials_to_true_for_user(self):
        # Given
        user = users_factories.UserFactory(hasSeenProTutorials=False)

        # When
        users_api.set_pro_tuto_as_seen(user)

        # Then
        assert db.session.query(users_models.User).one().hasSeenProTutorials is True


@pytest.mark.usefixtures("db_session")
class SetProRgsAsSeenTest:
    def should_set_has_seen_pro_rgs_to_true_for_user(self):
        # Given
        user = users_factories.UserFactory(hasSeenProRgs=False)

        # When
        users_api.set_pro_rgs_as_seen(user)

        # Then
        assert db.session.query(users_models.User).one().hasSeenProRgs is True


@pytest.mark.usefixtures("db_session")
class UpdateUserInfoTest:
    def test_update_user_info(self):
        user = users_factories.UserFactory(email="initial@example.com")

        users_api.update_user_info(user, author=user, first_name="New", last_name="Name")
        user = db.session.query(users_models.User).one()
        assert user.email == "initial@example.com"
        assert user.full_name == "New Name"

        users_api.update_user_info(user, author=user, email="new@example.com")
        user = db.session.query(users_models.User).one()
        assert user.email == "new@example.com"
        assert user.full_name == "New Name"

    def test_update_user_info_sanitizes_email(self):
        user = users_factories.UserFactory(email="initial@example.com")

        users_api.update_user_info(user, author=user, email="  NEW@example.com   ")
        user = db.session.query(users_models.User).one()
        assert user.email == "new@example.com"

    def test_update_user_info_returns_modified_info(self):
        user = users_factories.UserFactory(firstName="Noël", lastName="Flantier")

        modified_info = users_api.update_user_info(
            user, author=user, first_name="Hubert", last_name="Bonisseur de la Bath", commit=False
        )
        assert modified_info.to_dict() == {
            "firstName": {"new_info": "Hubert", "old_info": "Noël"},
            "lastName": {"new_info": "Bonisseur de la Bath", "old_info": "Flantier"},
        }

    def test_update_user_info_also_updates_underage_deposit_expiration_date(self):
        # Given a user with an underage deposit
        underaged_beneficiary_birthday = datetime.datetime.utcnow() - relativedelta(years=17, months=4)
        underaged_beneficiary_expiration_date = underaged_beneficiary_birthday + relativedelta(
            years=21, hour=0, minute=0, second=0, microsecond=0
        )
        user = users_factories.BeneficiaryFactory(age=17)
        users_api.update_user_info(user, author=user, validated_birth_date=underaged_beneficiary_birthday)

        assert user.deposits[0].expirationDate == underaged_beneficiary_expiration_date

    def test_update_user_info_also_updates_deposit_expiration_date(self):
        user = users_factories.BeneficiaryFactory()
        previous_deposit_expiration_date = user.deposit.expirationDate
        users_api.update_user_info(user, author=user, validated_birth_date=user.birth_date - relativedelta(years=1))

        new_deposit_expiration_date = user.deposit.expirationDate
        assert new_deposit_expiration_date == previous_deposit_expiration_date - relativedelta(years=1)


@pytest.mark.usefixtures("db_session")
class DomainsCreditTest:
    def test_get_domains_credit_v1(self):
        user = users_factories.BeneficiaryFactory(
            deposit__version=1, deposit__amount=500, deposit__type=finance_models.DepositType.GRANT_18
        )

        # booking only in all domains
        bookings_factories.BookingFactory(
            user=user,
            amount=50,
            stock__offer__subcategoryId=subcategories.SEANCE_CINE.id,
        )
        bookings_factories.BookingFactory(
            user=user,
            amount=5,
            stock__offer__subcategoryId=subcategories.SEANCE_CINE.id,
        )

        # booking in digital domain
        bookings_factories.BookingFactory(
            user=user,
            amount=80,
            stock__offer__subcategoryId=subcategories.JEU_EN_LIGNE.id,
            stock__offer__url="http://on.line",
        )

        # booking in physical domain
        bookings_factories.BookingFactory(
            user=user,
            amount=150,
            stock__offer__subcategoryId=subcategories.JEU_SUPPORT_PHYSIQUE.id,
        )

        # cancelled booking
        bookings_factories.CancelledBookingFactory(
            user=user,
            amount=150,
            stock__offer__subcategoryId=subcategories.JEU_SUPPORT_PHYSIQUE.id,
        )

        assert users_api.get_domains_credit(user) == users_models.DomainsCredit(
            all=users_models.Credit(initial=Decimal(500), remaining=Decimal(215)),
            digital=users_models.Credit(initial=Decimal(200), remaining=Decimal(120)),
            physical=users_models.Credit(initial=Decimal(200), remaining=Decimal(50)),
        )

    def test_get_domains_credit(self):
        user = users_factories.BeneficiaryFactory(deposit__type=finance_models.DepositType.GRANT_18)

        # booking in physical domain
        bookings_factories.BookingFactory(
            user=user,
            amount=250,
            stock__offer__subcategoryId=subcategories.JEU_SUPPORT_PHYSIQUE.id,
        )

        assert users_api.get_domains_credit(user) == users_models.DomainsCredit(
            all=users_models.Credit(initial=Decimal(300), remaining=Decimal(50)),
            digital=users_models.Credit(initial=Decimal(100), remaining=Decimal(50)),
            physical=None,
        )

    def test_get_domains_credit_deposit_expired(self):
        user = users_factories.BeneficiaryFactory()
        deposit_expiration_date = user.deposit.expirationDate
        deposit_initial_amount = user.deposit.amount
        bookings_factories.BookingFactory(
            user=user,
            amount=deposit_initial_amount - 10,
            stock__offer__subcategoryId=subcategories.JEU_SUPPORT_PHYSIQUE.id,
        )

        with time_machine.travel(deposit_expiration_date):
            assert users_api.get_domains_credit(user) == users_models.DomainsCredit(
                all=users_models.Credit(initial=Decimal(deposit_initial_amount), remaining=Decimal(0)),
                digital=users_models.Credit(initial=Decimal(100), remaining=Decimal(0)),
                physical=None,
            )

    def test_get_domains_credit_no_deposit(self):
        user = users_factories.UserFactory()

        assert not users_api.get_domains_credit(user)

    @staticmethod
    def _price_booking(booking):
        bookings_api.mark_as_used(
            booking=booking,
            validation_author_type=bookings_models.BookingValidationAuthorType.OFFERER,
        )
        finance_events = booking.finance_events
        assert len(finance_events) == 1
        finance_api.price_event(finance_events[0])

    @staticmethod
    def _price_incident(incident):
        assert len(incident.booking_finance_incidents) == 1
        booking_finance_incident = incident.booking_finance_incidents[0]
        for finance_event in booking_finance_incident.finance_events:
            finance_api.price_event(finance_event)

    def test_get_domains_regular_credit_with_finance_incidents(self):
        offerer = offerers_factories.OffererFactory(name="Association de coiffeurs", siren="853318959")
        bank_account = finance_factories.BankAccountFactory(offerer=offerer)
        venue = offerers_factories.VenueFactory(
            pricing_point="self",
            managingOfferer=offerer,
            bank_account=bank_account,
            siret="85331845900023",
        )
        author_user = users_factories.UserFactory()
        user = users_factories.BeneficiaryGrant18Factory(
            deposit__version=1, deposit__amount=500, deposit__type=finance_models.DepositType.GRANT_18
        )

        # booking1 (20€ → 20€) + booking2 (6€ → 0€) + booking3 (15€ → 10€) = 30€

        booking1 = bookings_factories.BookingFactory(
            user=user,
            cancellation_limit_date=datetime.datetime.utcnow() - datetime.timedelta(days=4),
            quantity=4,
            stock__price=Decimal("5.0"),
            stock__offer__venue=venue,
            stock__beginningDatetime=datetime.datetime.utcnow() - datetime.timedelta(days=5),
            stock__offer__subcategoryId=subcategories.SEANCE_CINE.id,
        )  # 20€
        self._price_booking(booking1)

        # Booking to cancel totally
        booking2 = bookings_factories.BookingFactory(
            user=user,
            cancellation_limit_date=datetime.datetime.utcnow() - datetime.timedelta(days=4),
            quantity=2,
            stock__price=Decimal("3.0"),
            stock__offer__venue=venue,
            stock__beginningDatetime=datetime.datetime.utcnow() - datetime.timedelta(days=5),
            stock__offer__subcategoryId=subcategories.SEANCE_CINE.id,
        )  # 6€ → 0€
        self._price_booking(booking2)

        # Booking to cancel partially
        booking3 = bookings_factories.BookingFactory(
            user=user,
            cancellation_limit_date=datetime.datetime.utcnow() - datetime.timedelta(days=4),
            quantity=5,
            stock__price=Decimal("3.0"),
            stock__offer__venue=venue,
            stock__beginningDatetime=datetime.datetime.utcnow() - datetime.timedelta(days=5),
            stock__offer__subcategoryId=subcategories.SEANCE_CINE.id,
        )  # 15€ → 10€
        self._price_booking(booking3)

        # Mark all pricings as invoiced
        cutoff = datetime.datetime.utcnow()
        batch = finance_api.generate_cashflows(cutoff)
        assert len(batch.cashflows) == 1
        cashflow = batch.cashflows[0]
        cashflow.status = finance_models.CashflowStatus.UNDER_REVIEW
        db.session.add(cashflow)
        db.session.flush()
        finance_api._generate_invoice_legacy(
            bank_account_id=bank_account.id, cashflow_ids=[c.id for c in batch.cashflows]
        )

        # Create the finance incidents and validate them
        #  - For booking2 → cancelled totally
        incident2 = finance_api.create_overpayment_finance_incident(
            bookings=[booking2],
            author=author_user,
            origin=finance_models.FinanceIncidentRequestOrigin.SUPPORT_PRO,
            comment="BO",
            amount=Decimal("6.0"),
        )
        finance_api.validate_finance_overpayment_incident(
            finance_incident=incident2,
            force_debit_note=False,
            author=author_user,
        )
        self._price_incident(incident2)

        #  - For booking3 → cancelled partially: get back 5€
        incident3 = finance_api.create_overpayment_finance_incident(
            bookings=[booking3],
            author=author_user,
            origin=finance_models.FinanceIncidentRequestOrigin.SUPPORT_PRO,
            comment="BO",
            amount=Decimal("5.0"),
        )
        finance_api.validate_finance_overpayment_incident(
            finance_incident=incident3,
            force_debit_note=False,
            author=author_user,
        )
        self._price_incident(incident3)

        assert users_api.get_domains_credit(user) == users_models.DomainsCredit(
            all=users_models.Credit(initial=Decimal("500"), remaining=Decimal("470")),
            digital=users_models.Credit(initial=Decimal("200"), remaining=Decimal("200")),
            physical=users_models.Credit(initial=Decimal("200"), remaining=Decimal("200")),
        )

    def test_get_domains_regular_credit_with_finance_incidents_in_case_of_v3_deposit_transition(self):
        offerer = offerers_factories.OffererFactory(name="Association de coiffeurs", siren="853318959")
        bank_account = finance_factories.BankAccountFactory(offerer=offerer)
        venue = offerers_factories.VenueFactory(
            pricing_point="self",
            managingOfferer=offerer,
            bank_account=bank_account,
            siret="85331845900023",
        )
        author_user = users_factories.UserFactory()
        user = users_factories.BeneficiaryGrant18Factory(
            deposit__type=finance_models.DepositType.GRANT_15_17,
            deposit__expirationDate=datetime.datetime.utcnow() + datetime.timedelta(days=2),
            deposit__amount=70,
        )

        # booking1 (20€ → 20€) + booking2 (6€ → 0€) + booking3 (15€ → 10€) = 30€
        booking1 = bookings_factories.BookingFactory(
            user=user,
            cancellation_limit_date=datetime.datetime.utcnow() - datetime.timedelta(days=4),
            quantity=4,
            stock__price=Decimal("5.0"),
            stock__offer__venue=venue,
            stock__beginningDatetime=datetime.datetime.utcnow() - datetime.timedelta(days=5),
            stock__offer__subcategoryId=subcategories.SEANCE_CINE.id,
        )  # 20€
        self._price_booking(booking1)

        # Booking to cancel totally
        booking2 = bookings_factories.BookingFactory(
            user=user,
            cancellation_limit_date=datetime.datetime.utcnow() - datetime.timedelta(days=4),
            quantity=2,
            stock__price=Decimal("3.0"),
            stock__offer__venue=venue,
            stock__beginningDatetime=datetime.datetime.utcnow() - datetime.timedelta(days=5),
            stock__offer__subcategoryId=subcategories.SEANCE_CINE.id,
        )  # 6€ → 0€
        self._price_booking(booking2)

        # Booking to cancel partially
        booking3 = bookings_factories.BookingFactory(
            user=user,
            cancellation_limit_date=datetime.datetime.utcnow() - datetime.timedelta(days=4),
            quantity=5,
            stock__price=Decimal("3.0"),
            stock__offer__venue=venue,
            stock__beginningDatetime=datetime.datetime.utcnow() - datetime.timedelta(days=5),
            stock__offer__subcategoryId=subcategories.SEANCE_CINE.id,
        )  # 15€ → 10€
        self._price_booking(booking3)

        # the old deposit expires and is replaced by a 17_18 one
        user.deposit.expirationDate = datetime.datetime.utcnow() - datetime.timedelta(days=5)
        users_factories.DepositGrantFactory(
            user=user,
            type=finance_models.DepositType.GRANT_17_18,
            expirationDate=datetime.datetime.utcnow() + datetime.timedelta(days=5),
            amount=50,
        )
        booking4 = bookings_factories.BookingFactory(
            user=user,
            cancellation_limit_date=datetime.datetime.utcnow() - datetime.timedelta(days=4),
            quantity=4,
            stock__price=Decimal("5.0"),
            stock__offer__venue=venue,
            stock__offer__subcategoryId=subcategories.SEANCE_CINE.id,
        )  # 20€
        self._price_booking(booking4)

        # Mark all pricings as invoiced
        cutoff = datetime.datetime.utcnow()
        batch = finance_api.generate_cashflows(cutoff)
        assert len(batch.cashflows) == 1
        cashflow = batch.cashflows[0]
        cashflow.status = finance_models.CashflowStatus.UNDER_REVIEW
        db.session.add(cashflow)
        db.session.flush()
        finance_api._generate_invoice_legacy(
            bank_account_id=bank_account.id, cashflow_ids=[c.id for c in batch.cashflows]
        )

        # Create the finance incidents and validate them
        #  - For booking2 → cancelled totally
        incident2 = finance_api.create_overpayment_finance_incident(
            bookings=[booking2],
            author=author_user,
            origin=finance_models.FinanceIncidentRequestOrigin.SUPPORT_PRO,
            comment="BO",
            amount=Decimal("6.0"),
        )
        finance_api.validate_finance_overpayment_incident(
            finance_incident=incident2,
            force_debit_note=False,
            author=author_user,
        )
        self._price_incident(incident2)

        #  - For booking3 → cancelled partially: get back 5€
        incident3 = finance_api.create_overpayment_finance_incident(
            bookings=[booking3],
            author=author_user,
            origin=finance_models.FinanceIncidentRequestOrigin.SUPPORT_PRO,
            comment="BO",
            amount=Decimal("5.0"),
        )
        finance_api.validate_finance_overpayment_incident(
            finance_incident=incident3,
            force_debit_note=False,
            author=author_user,
        )
        self._price_incident(incident3)

        # initial amount of active deposit + incidents amounts = 50 + (6 + 5) = 61
        # 20€ are used with booking4 => remaining = 61 - 20 = 41€
        assert users_api.get_domains_credit(user).all == users_models.Credit(
            initial=Decimal("61"), remaining=Decimal("41")
        )

    def test_get_domains_digital_credit_with_finance_incidents(self):
        offerer = offerers_factories.OffererFactory(name="Association de coiffeurs", siren="853318959")
        bank_account = finance_factories.BankAccountFactory(offerer=offerer)
        venue = offerers_factories.VenueFactory(
            pricing_point="self",
            managingOfferer=offerer,
            bank_account=bank_account,
            siret="85331845900023",
        )
        author_user = users_factories.UserFactory()
        user = users_factories.BeneficiaryFactory(
            deposit__version=1, deposit__amount=500, deposit__type=finance_models.DepositType.GRANT_18
        )

        # booking1 (9€ → 9€) + booking2 (45€ → 0€) + booking3 (24€ → 15€) = 24€

        booking1 = bookings_factories.BookingFactory(
            user=user,
            quantity=2,
            stock__price=Decimal("4.5"),
            stock__offer__venue=venue,
            stock__offer__subcategoryId=subcategories.JEU_EN_LIGNE.id,
            stock__offer__url="http://on.line",
        )  # 9€
        self._price_booking(booking1)

        # Booking to cancel totally
        booking2 = bookings_factories.BookingFactory(
            user=user,
            quantity=1,
            stock__price=Decimal("45.0"),
            stock__offer__venue=venue,
            stock__offer__subcategoryId=subcategories.JEU_EN_LIGNE.id,
            stock__offer__url="http://on.line",
        )  # 45€ → 0€
        self._price_booking(booking2)

        # Booking to cancel partially
        booking3 = bookings_factories.BookingFactory(
            user=user,
            quantity=3,
            stock__price=Decimal("8.0"),
            stock__offer__venue=venue,
            stock__offer__subcategoryId=subcategories.JEU_EN_LIGNE.id,
            stock__offer__url="http://on.line",
        )  # 24€ → 15€
        self._price_booking(booking3)

        # Mark all pricings as invoiced
        cutoff = datetime.datetime.utcnow()
        batch = finance_api.generate_cashflows(cutoff)
        assert len(batch.cashflows) == 1
        cashflow = batch.cashflows[0]
        cashflow.status = finance_models.CashflowStatus.UNDER_REVIEW
        db.session.add(cashflow)
        db.session.flush()
        finance_api._generate_invoice_legacy(
            bank_account_id=bank_account.id, cashflow_ids=[c.id for c in batch.cashflows]
        )

        # Create the finance incidents and validate them
        #  - For booking2 → cancelled totally
        incident2 = finance_api.create_overpayment_finance_incident(
            bookings=[booking2],
            author=author_user,
            origin=finance_models.FinanceIncidentRequestOrigin.SUPPORT_PRO,
            comment="BO",
            amount=Decimal("45.0"),
        )
        finance_api.validate_finance_overpayment_incident(
            finance_incident=incident2,
            force_debit_note=False,
            author=author_user,
        )
        self._price_incident(incident2)

        #  - For booking3 → cancelled partially: get back 9€
        incident3 = finance_api.create_overpayment_finance_incident(
            bookings=[booking3],
            author=author_user,
            origin=finance_models.FinanceIncidentRequestOrigin.SUPPORT_PRO,
            comment="BO",
            amount=Decimal("9.0"),
        )
        finance_api.validate_finance_overpayment_incident(
            finance_incident=incident3,
            force_debit_note=False,
            author=author_user,
        )
        self._price_incident(incident3)

        assert users_api.get_domains_credit(user) == users_models.DomainsCredit(
            all=users_models.Credit(initial=Decimal("500"), remaining=Decimal("476")),
            digital=users_models.Credit(initial=Decimal("200"), remaining=Decimal("176")),
            physical=users_models.Credit(initial=Decimal("200"), remaining=Decimal("200")),
        )

    def test_get_domains_physical_credit_with_finance_incidents(self):
        offerer = offerers_factories.OffererFactory(name="Association de coiffeurs", siren="853318959")
        bank_account = finance_factories.BankAccountFactory(offerer=offerer)
        venue = offerers_factories.VenueFactory(
            pricing_point="self",
            managingOfferer=offerer,
            bank_account=bank_account,
            siret="85331845900023",
        )
        author_user = users_factories.UserFactory()
        user = users_factories.BeneficiaryFactory(
            deposit__version=1, deposit__amount=500, deposit__type=finance_models.DepositType.GRANT_18
        )

        # booking1 (68€ → 68€) + booking2 (32€ → 0€) + booking3 (39€ → 27€) = 95€

        booking1 = bookings_factories.BookingFactory(
            user=user,
            quantity=4,
            stock__price=Decimal("17"),
            stock__offer__venue=venue,
            stock__offer__subcategoryId=subcategories.JEU_SUPPORT_PHYSIQUE.id,
        )  # 68€
        self._price_booking(booking1)

        # booking to cancel totally
        booking2 = bookings_factories.BookingFactory(
            user=user,
            quantity=2,
            stock__price=Decimal("16"),
            stock__offer__venue=venue,
            stock__offer__subcategoryId=subcategories.JEU_SUPPORT_PHYSIQUE.id,
        )  # 32€ → 0€
        self._price_booking(booking2)

        # booking in physical domain to cancel totally
        booking3 = bookings_factories.BookingFactory(
            user=user,
            quantity=3,
            stock__price=Decimal("13"),
            stock__offer__venue=venue,
            stock__offer__subcategoryId=subcategories.JEU_SUPPORT_PHYSIQUE.id,
        )  # 39€ → 27€
        self._price_booking(booking3)

        # Mark all pricings as invoiced
        cutoff = datetime.datetime.utcnow()
        batch = finance_api.generate_cashflows(cutoff)
        assert len(batch.cashflows) == 1
        cashflow = batch.cashflows[0]
        cashflow.status = finance_models.CashflowStatus.UNDER_REVIEW
        db.session.add(cashflow)
        db.session.flush()
        finance_api._generate_invoice_legacy(
            bank_account_id=bank_account.id, cashflow_ids=[c.id for c in batch.cashflows]
        )

        # Create the finance incidents and validate them
        #  - For booking2 → cancelled totally
        incident2 = finance_api.create_overpayment_finance_incident(
            bookings=[booking2],
            author=author_user,
            origin=finance_models.FinanceIncidentRequestOrigin.SUPPORT_PRO,
            comment="BO",
            amount=Decimal("45.0"),
        )
        finance_api.validate_finance_overpayment_incident(
            finance_incident=incident2,
            force_debit_note=False,
            author=author_user,
        )
        self._price_incident(incident2)

        #  - For booking3 → cancelled partially: get back 9€
        incident3 = finance_api.create_overpayment_finance_incident(
            bookings=[booking3],
            author=author_user,
            origin=finance_models.FinanceIncidentRequestOrigin.SUPPORT_PRO,
            comment="BO",
            amount=Decimal("12.0"),
        )
        finance_api.validate_finance_overpayment_incident(
            finance_incident=incident3,
            force_debit_note=False,
            author=author_user,
        )
        self._price_incident(incident3)

        assert users_api.get_domains_credit(user) == users_models.DomainsCredit(
            all=users_models.Credit(initial=Decimal("500"), remaining=Decimal("405")),
            digital=users_models.Credit(initial=Decimal("200"), remaining=Decimal("200")),
            physical=users_models.Credit(initial=Decimal("200"), remaining=Decimal("105")),
        )


class CreateProUserTest:
    data = {
        "email": "prouser@example.com",
        "firstName": "Jean",
        "lastName": "Test",
        "password": "P@ssword12345",
        "phoneNumber": "0666666666",
        "contactOk": False,
        "token": "token",
    }

    def test_create_pro_user(self):
        pro_user_creation_body = users_serialization.ProUserCreationBodyV2Model(**self.data)

        pro_user = users_api.create_pro_user(pro_user_creation_body)

        assert pro_user.email == "prouser@example.com"
        assert not pro_user.has_admin_role
        assert not pro_user.needsToFillCulturalSurvey
        assert not pro_user.has_pro_role
        assert not pro_user.has_admin_role
        assert not pro_user.has_beneficiary_role
        assert not pro_user.deposits

    @pytest.mark.settings(MAKE_PROS_BENEFICIARIES_IN_APP=True)
    def test_create_pro_user_in_integration(self):
        pro_user_creation_body = users_serialization.ProUserCreationBodyV2Model(**self.data)

        pro_user = users_api.create_pro_user(pro_user_creation_body)

        assert pro_user.email == "prouser@example.com"
        assert not pro_user.has_admin_role
        assert not pro_user.needsToFillCulturalSurvey
        assert not pro_user.has_pro_role
        assert not pro_user.has_admin_role
        assert pro_user.has_beneficiary_role
        assert pro_user.deposits


class BeneficiaryInformationUpdateTest:
    def test_update_user_information_from_dms(self):
        declared_on_signup_date_of_birth = datetime.datetime(2000, 1, 1, 0, 0)
        declared_on_dms_date_of_birth = datetime.date(2000, 5, 1)
        user = users_factories.UserFactory(
            activity=None,
            address=None,
            city=None,
            firstName=None,
            lastName=None,
            postalCode=None,
            dateOfBirth=declared_on_signup_date_of_birth,
        )
        beneficiary_information = fraud_models.DMSContent(
            last_name="Doe",
            first_name="Jane",
            activity="Lycéen",
            civility=users_models.GenderEnum.F,
            birth_date=declared_on_dms_date_of_birth,
            email="jane.doe@test.com",
            phone="0612345678",
            postal_code="67200",
            address="11 Rue du Test",
            application_number=123,
            procedure_number=98012,
            registration_datetime=datetime.datetime(2020, 5, 1),
        )

        # when
        beneficiary = users_api.update_user_information_from_external_source(user, beneficiary_information)

        # Then
        assert beneficiary.lastName == "Doe"
        assert beneficiary.firstName == "Jane"
        assert beneficiary.postalCode == "67200"
        assert beneficiary.address == "11 Rue du Test"
        assert beneficiary.validatedBirthDate == declared_on_dms_date_of_birth
        assert beneficiary.dateOfBirth == declared_on_signup_date_of_birth
        assert not beneficiary.has_beneficiary_role
        assert not beneficiary.has_admin_role
        assert beneficiary.password is not None
        assert beneficiary.activity == "Lycéen"
        assert beneficiary.civility == "Mme"
        assert not beneficiary.deposits

    def test_update_user_information_from_educonnect(self):
        user = users_factories.UserFactory(
            firstName=None,
            lastName=None,
        )
        educonnect_data = fraud_factories.EduconnectContentFactory(
            first_name="Raoul",
            last_name="Dufy",
            birth_date=datetime.date(2000, 5, 1),
            ine_hash="identifiantnati0naleleve",
        )
        new_user = users_api.update_user_information_from_external_source(user, educonnect_data)

        assert new_user.firstName == "Raoul"
        assert new_user.lastName == "Dufy"
        assert new_user.validatedBirthDate == datetime.date(2000, 5, 1)
        assert new_user.ineHash == "identifiantnati0naleleve"

    def test_update_user_information_from_ubble(self):
        user = users_factories.UserFactory(civility=None)
        ubble_data = fraud_factories.UbbleContentFactory(
            first_name="Raoul",
            last_name="Dufy",
            birth_date=datetime.date(2000, 5, 1).isoformat(),
            id_document_number="123456789",
            gender=users_models.GenderEnum.M,
        )
        new_user = users_api.update_user_information_from_external_source(user, ubble_data)

        assert new_user.firstName == "Raoul"
        assert new_user.lastName == "Dufy"
        assert new_user.validatedBirthDate == datetime.date(2000, 5, 1)
        assert new_user.idPieceNumber == "123456789"
        assert new_user.civility == "M."

    def test_update_user_information_from_ubble_with_married_name(self):
        user = users_factories.UserFactory(civility=None)
        ubble_data = fraud_factories.UbbleContentFactory(married_name="Flouz")
        new_user = users_api.update_user_information_from_external_source(user, ubble_data)

        assert new_user.married_name == "Flouz"

    def test_update_id_piece_number(self):
        user = users_factories.UserFactory(activity="Etudiant", postalCode="75001", idPieceNumber=None)
        dms_data = fraud_factories.DMSContentFactory(id_piece_number="140 767100 016")

        users_api.update_user_information_from_external_source(user, dms_data)
        assert user.idPieceNumber == "140767100016"

    @pytest.mark.features(ENABLE_PHONE_VALIDATION=True)
    def test_phone_number_does_not_update(self):
        user = users_factories.UserFactory(phoneNumber="+33611111111")
        dms_data = fraud_factories.DMSContentFactory(phoneNumber="+33622222222")

        users_api.update_user_information_from_external_source(user, dms_data)

        assert user.phoneNumber == "+33611111111"

    @pytest.mark.features(ENABLE_PHONE_VALIDATION=False)
    def test_phone_number_does_not_update_if_not_empty(self):
        user = users_factories.UserFactory(phoneNumber="+33611111111")
        dms_data = fraud_factories.DMSContentFactory(phone="+33622222222")

        users_api.update_user_information_from_external_source(user, dms_data)

        assert user.phoneNumber == "+33611111111"

    def test_incomplete_data(self):
        user = users_factories.UserFactory(firstName="Julie")
        dms_data = fraud_factories.DMSContentFactory(birth_date=None)

        with pytest.raises(users_exceptions.IncompleteDataException):
            users_api.update_user_information_from_external_source(user, dms_data)

        assert user.firstName == "Julie"

    def should_not_update_date_of_birth_if_already_validated(self):
        # Given
        user = users_factories.UserFactory(
            dateOfBirth=datetime.date(2000, 1, 1),
            validatedBirthDate=datetime.date(2000, 1, 1),
        )

        # When
        users_api.update_user_information_from_external_source(user, fraud_factories.DMSContentFactory())

        # Then
        assert user.birth_date == datetime.date(2000, 1, 1)


class UpdateUserLastConnectionDateTest:
    @time_machine.travel("2021-9-20 11:11:11", tick=False)
    def test_first_update(self):
        user = users_factories.UserFactory()

        users_api.update_last_connection_date(user)

        db.session.refresh(user)

        assert user.lastConnectionDate == datetime.datetime(2021, 9, 20, 11, 11, 11)
        assert len(sendinblue_testing.sendinblue_requests) == 1

    @time_machine.travel("2021-9-20 01:11:11", tick=False)
    def test_update_day_after(self):
        user = users_factories.UserFactory(lastConnectionDate=datetime.datetime(2021, 9, 19, 23, 00, 11))

        users_api.update_last_connection_date(user)

        db.session.refresh(user)

        assert user.lastConnectionDate == datetime.datetime(2021, 9, 20, 1, 11, 11)
        assert len(sendinblue_testing.sendinblue_requests) == 1

    @time_machine.travel("2021-9-20 11:11:11", tick=False)
    def test_update_same_day(self):
        user = users_factories.UserFactory(lastConnectionDate=datetime.datetime(2021, 9, 20, 9, 0))

        users_api.update_last_connection_date(user)

        db.session.refresh(user)

        assert user.lastConnectionDate == datetime.datetime(2021, 9, 20, 11, 11, 11)
        assert len(sendinblue_testing.sendinblue_requests) == 0

    @time_machine.travel("2021-9-20 11:11:11", tick=False)
    def test_no_update(self):
        user = users_factories.UserFactory(lastConnectionDate=datetime.datetime(2021, 9, 20, 11, 00, 11))

        users_api.update_last_connection_date(user)

        db.session.refresh(user)

        assert user.lastConnectionDate == datetime.datetime(2021, 9, 20, 11, 00, 11)
        assert len(sendinblue_testing.sendinblue_requests) == 0


class UserEmailValidationTest:
    def test_validate_pro_user_email_from_pro_ff_on(self):
        user_offerer = offerers_factories.UserOffererFactory(user__isEmailValidated=False)

        users_api.validate_pro_user_email(user_offerer.user)

        assert db.session.query(history_models.ActionHistory).count() == 0
        assert user_offerer.user.isEmailValidated is True
        assert len(mails_testing.outbox) == 0

    def test_validate_pro_user_email_from_backoffice_ff_on(self):
        backoffice_user = users_factories.AdminFactory()
        user_offerer = offerers_factories.UserOffererFactory(user__isEmailValidated=False)

        users_api.validate_pro_user_email(user_offerer.user, backoffice_user)

        assert db.session.query(history_models.ActionHistory).count() == 1
        action = db.session.query(history_models.ActionHistory).one()
        assert action.actionType == history_models.ActionType.USER_EMAIL_VALIDATED
        assert action.user == user_offerer.user
        assert action.authorUser == backoffice_user

        assert user_offerer.user.isEmailValidated is True
        assert len(mails_testing.outbox) == 0


class SearchPublicAccountTest:
    def test_current_email(self):
        user = users_factories.BeneficiaryGrant18Factory(email="current@email.com")
        users_factories.EmailValidationEntryFactory(user=user)

        query = users_api.search_public_account("current@email.com")
        users = query.all()

        assert len(users) == 1
        assert users[0].id == user.id

    def test_current_domain(self):
        user = users_factories.BeneficiaryGrant18Factory(email="current@domain.com")
        users_factories.EmailValidationEntryFactory(user=user)

        query = users_api.search_public_account("@domain.com")
        users = query.all()

        assert len(users) == 1
        assert users[0].id == user.id

    def test_email_not_in_known_users(self):
        users_factories.BeneficiaryGrant18Factory(email="current@domain.com")

        query = users_api.search_public_account("another@email.com")

        assert not query.all()

    def test_domain_not_in_known_users(self):
        users_factories.BeneficiaryGrant18Factory(email="current@domain.com")

        query = users_api.search_public_account("@email.com")

        assert not query.all()

    def test_old_email(self):
        event = users_factories.EmailValidationEntryFactory()
        event.user.email = event.newEmail

        query = users_api.search_public_account_in_history_email(event.oldEmail)
        users = query.all()

        assert len(users) == 1
        assert users[0].id == event.user.id

    def test_old_email_but_not_validated(self):
        user = users_factories.BeneficiaryGrant18Factory(email="current@domain.com")
        event = users_factories.EmailUpdateEntryFactory(user=user)
        # ensure that the current email is different from the event's
        # old one
        event.user.email = event.newEmail

        query = users_api.search_public_account_in_history_email(event.oldEmail)
        assert not query.all()

    def test_unknown_email(self):
        query = users_api.search_public_account("no@user.com")
        assert not query.all()

    def test_unknown_email_in_history_email(self):
        query = users_api.search_public_account_in_history_email("no@user.com")
        assert not query.all()


class SaveTrustedDeviceTest:
    def should_not_save_trusted_device_when_no_device_id_provided(self):
        user = users_factories.UserFactory()
        device_info = account_serialization.TrustedDevice(
            deviceId="",
            source="iPhone 13",
            os="iOS",
        )

        users_api.save_trusted_device(device_info=device_info, user=user)

        assert db.session.query(users_models.TrustedDevice).count() == 0

    def test_can_save_trusted_device(self):
        user = users_factories.UserFactory()
        device_info = account_serialization.TrustedDevice(
            deviceId="2E429592-2446-425F-9A62-D6983F375B3B",
            source="iPhone 13",
            os="iOS",
        )

        users_api.save_trusted_device(device_info=device_info, user=user)

        trusted_device = db.session.query(users_models.TrustedDevice).one()

        assert trusted_device.deviceId == device_info.device_id
        assert trusted_device.source == "iPhone 13"
        assert trusted_device.os == "iOS"

    def test_can_access_trusted_devices_from_user(self):
        user = users_factories.UserFactory()
        device_info = account_serialization.TrustedDevice(
            deviceId="2E429592-2446-425F-9A62-D6983F375B3B",
            source="iPhone 13",
            os="iOS",
        )

        users_api.save_trusted_device(device_info=device_info, user=user)

        trusted_device = db.session.query(users_models.TrustedDevice).one()

        assert user.trusted_devices == [trusted_device]

    def should_log_when_no_device_id(self, caplog):
        user = users_factories.UserFactory()
        device_info = account_serialization.TrustedDevice(
            deviceId="",
            source="iPhone 13",
            os="iOS",
        )

        with caplog.at_level(logging.INFO):
            users_api.save_trusted_device(device_info=device_info, user=user)

        assert caplog.messages == ["Invalid deviceId was provided for trusted device"]
        assert caplog.records[0].extra == {
            "deviceId": "",
            "os": "iOS",
            "source": "iPhone 13",
        }


class UpdateLoginDeviceHistoryTest:
    def should_not_save_login_device_when_no_device_id_provided(self):
        user = users_factories.UserFactory()
        device_info = account_serialization.TrustedDevice(
            deviceId="",
            source="iPhone 13",
            os="iOS",
        )

        users_api.update_login_device_history(device_info=device_info, user=user)

        assert db.session.query(users_models.LoginDeviceHistory).count() == 0

    def test_can_save_login_device(self):
        user = users_factories.UserFactory()
        device_info = account_serialization.TrustedDevice(
            deviceId="2E429592-2446-425F-9A62-D6983F375B3B",
            source="iPhone 13",
            os="iOS",
        )

        users_api.update_login_device_history(device_info=device_info, user=user)

        login_device = db.session.query(users_models.LoginDeviceHistory).one()

        assert login_device.deviceId == device_info.device_id
        assert login_device.source == "iPhone 13"
        assert login_device.os == "iOS"
        assert login_device.location is None

    def should_return_login_history(self):
        user = users_factories.UserFactory()
        device_info = account_serialization.TrustedDevice(
            deviceId="2E429592-2446-425F-9A62-D6983F375B3B",
            source="iPhone 13",
            os="iOS",
        )

        login_history = users_api.update_login_device_history(device_info=device_info, user=user)

        login_device = db.session.query(users_models.LoginDeviceHistory).one()

        assert login_history == login_device

    def test_can_access_login_device_history_from_user(self):
        user = users_factories.UserFactory()
        device_info = account_serialization.TrustedDevice(
            deviceId="2E429592-2446-425F-9A62-D6983F375B3B",
            source="iPhone 13",
            os="iOS",
        )

        users_api.update_login_device_history(device_info=device_info, user=user)

        login_device = db.session.query(users_models.LoginDeviceHistory).one()

        assert user.login_device_history == [login_device]

    def should_log_when_no_device_id(self, caplog):
        user = users_factories.UserFactory()
        device_info = account_serialization.TrustedDevice(
            deviceId="",
            source="iPhone 13",
            os="iOS",
        )

        with caplog.at_level(logging.INFO):
            users_api.update_login_device_history(device_info=device_info, user=user)

        assert caplog.messages == ["Invalid deviceId was provided for login device"]
        assert caplog.records[0].extra == {
            "deviceId": "",
            "os": "iOS",
            "source": "iPhone 13",
        }


class ShouldSaveLoginDeviceAsTrustedDeviceTest:
    device_info = account_serialization.TrustedDevice(
        deviceId="2E429592-2446-425F-9A62-D6983F375B3B", os="iOS", source="iPhone 13"
    )

    def should_be_false_when_no_device_id(self):
        user = users_factories.UserFactory()
        device_without_id = account_serialization.TrustedDevice(deviceId="", os="iOS", source="iPhone 13")

        assert users_api.should_save_login_device_as_trusted_device(device_info=device_without_id, user=user) is False

    def should_be_false_when_no_device_history_for_user(self):
        user = users_factories.UserFactory()

        assert users_api.should_save_login_device_as_trusted_device(device_info=self.device_info, user=user) is False

    def should_be_true_when_user_has_device_history_matching_device_id(self):
        user = users_factories.UserFactory()
        users_factories.LoginDeviceHistoryFactory(deviceId=self.device_info.device_id, user=user)

        assert users_api.should_save_login_device_as_trusted_device(device_info=self.device_info, user=user) is True

    def should_be_false_when_user_has_device_history_for_different_device(self):
        user = users_factories.UserFactory()
        users_factories.LoginDeviceHistoryFactory(deviceId=self.device_info.device_id, user=user)

        other_device_info = account_serialization.TrustedDevice(deviceId="other_id", os="iOS", source="iPhone 13")
        assert users_api.should_save_login_device_as_trusted_device(device_info=other_device_info, user=user) is False

    def should_be_false_when_device_id_matches_different_user(self):
        user = users_factories.UserFactory()
        second_user = users_factories.UserFactory(email="py2@test.com")
        users_factories.LoginDeviceHistoryFactory(deviceId=self.device_info.device_id, user=second_user)

        assert users_api.should_save_login_device_as_trusted_device(device_info=self.device_info, user=user) is False

    def should_be_true_when_device_id_matches_multiple_users_including_current_user(self):
        user = users_factories.UserFactory()
        second_user = users_factories.UserFactory(email="py2@test.com")
        users_factories.LoginDeviceHistoryFactory(deviceId=self.device_info.device_id, user=second_user)
        users_factories.LoginDeviceHistoryFactory(deviceId=self.device_info.device_id, user=user)

        assert users_api.should_save_login_device_as_trusted_device(device_info=self.device_info, user=user) is True

    def should_be_false_when_login_device_is_already_trusted_device(self):
        user = users_factories.UserFactory()
        users_factories.TrustedDeviceFactory(deviceId=self.device_info.device_id, user=user)
        users_factories.LoginDeviceHistoryFactory(deviceId=self.device_info.device_id, user=user)

        assert users_api.should_save_login_device_as_trusted_device(device_info=self.device_info, user=user) is False


class IsLoginDeviceTrustedDeviceTest:
    def should_not_be_trusted_when_user_has_no_trusted_device(self):
        user = users_factories.UserFactory()
        device_info = account_serialization.TrustedDevice(
            deviceId="2E429592-2446-425F-9A62-D6983F375B3B", os="iOS", source="iPhone 13"
        )

        assert user.trusted_devices == []
        assert users_api.is_login_device_a_trusted_device(device_info=device_info, user=user) is False

    def should_not_be_trusted_when_no_device_info(self):
        user = users_factories.UserFactory()

        assert users_api.is_login_device_a_trusted_device(device_info=None, user=user) is False

    def should_not_be_trusted_when_no_device_id(self):
        user = users_factories.UserFactory()
        device_without_id = account_serialization.TrustedDevice(deviceId="", os="iOS", source="iPhone 13")

        assert users_api.is_login_device_a_trusted_device(device_info=device_without_id, user=user) is False

    def should_be_trusted_when_device_is_a_trusted_device(self):
        user = users_factories.UserFactory()
        trusted_device = users_factories.TrustedDeviceFactory(user=user)
        users_factories.TrustedDeviceFactory(deviceId="3A44812-5776-235D-8E31-G4361H987A1A", user=user)
        device_info = account_serialization.TrustedDevice(
            deviceId=trusted_device.deviceId, os="iOS", source="iPhone 13"
        )

        assert users_api.is_login_device_a_trusted_device(device_info=device_info, user=user) is True

    def should_not_be_trusted_when_device_is_not_a_trusted_device(self):
        user = users_factories.UserFactory()
        users_factories.TrustedDeviceFactory(user=user)
        device_info = account_serialization.TrustedDevice(deviceId="other-device-id", os="iOS", source="iPhone 13")

        assert users_api.is_login_device_a_trusted_device(device_info=device_info, user=user) is False


class RecentSuspiciousLoginsTest:
    def should_ignore_trusted_device_logins(self):
        user = users_factories.UserFactory()
        trusted_device = users_factories.TrustedDeviceFactory(user=user)
        _trusted_login = users_factories.LoginDeviceHistoryFactory(user=user, deviceId=trusted_device.deviceId)

        assert not users_api.get_recent_suspicious_logins(user)

    def should_ignore_old_suspicious_device_logins(self):
        user = users_factories.UserFactory()
        _untrusted_login = users_factories.LoginDeviceHistoryFactory(
            user=user, dateCreated=datetime.datetime.utcnow() - relativedelta(hours=25)
        )

        assert not users_api.get_recent_suspicious_logins(user)

    def should_detect_suspicious_login(self):
        user = users_factories.UserFactory()
        untrusted_login = users_factories.LoginDeviceHistoryFactory(user=user)

        assert users_api.get_recent_suspicious_logins(user) == [untrusted_login]

    def should_detect_suspicious_login_before_trusted_device_addition(self):
        user = users_factories.UserFactory()
        untrusted_login = users_factories.LoginDeviceHistoryFactory(user=user)
        _trusted_device = users_factories.TrustedDeviceFactory(user=user, deviceId=untrusted_login.deviceId)

        assert users_api.get_recent_suspicious_logins(user) == [untrusted_login]


class CreateSuspiciousLoginEmailTokenTest:
    @time_machine.travel("2023-06-19 10:30:00", tick=False)
    def should_encode_login_info_in_token(self):
        with mock.patch("flask.current_app.redis_client", fakeredis.FakeStrictRedis()):
            user = users_factories.UserFactory()
            login_info = users_models.LoginDeviceHistory(
                deviceId="2E429592-2446-425F-9A62-D6983F375B3B",
                source="iPhone 13",
                os="iOS",
                location="Paris",
                dateCreated=datetime.datetime(2023, 6, 19, 10, 30),
            )

            token = users_api.create_suspicious_login_email_token(login_info, user.id)

            assert token.data == {
                "dateCreated": "2023-06-19T10:30:00.000000Z",
                "location": "Paris",
                "source": "iPhone 13",
                "os": "iOS",
            }
            assert token.get_expiration_date_from_token() == datetime.datetime(2023, 6, 26, 10, 30)

            assert token.user_id == user.id

    @time_machine.travel("2023-06-02 16:10:00", tick=False)
    def should_encode_date_and_user_id_in_token_when_no_login_info(self):
        user = users_factories.UserFactory()

        token = users_api.create_suspicious_login_email_token(None, user.id)

        assert token.data == {
            "dateCreated": "2023-06-02T16:10:00.000000Z",
        }
        assert token.user_id == user.id


class DeleteOldTrustedDevicesTest:
    def should_delete_trusted_devices_older_than_five_years_ago(self):
        five_years_ago = datetime.datetime.utcnow() - relativedelta(years=5)
        six_years_ago = datetime.datetime.utcnow() - relativedelta(years=6)
        users_factories.TrustedDeviceFactory(dateCreated=five_years_ago)
        users_factories.TrustedDeviceFactory(dateCreated=six_years_ago)

        users_api.delete_old_trusted_devices()

        assert db.session.query(users_models.TrustedDevice).count() == 0

    def should_not_delete_trusted_devices_created_less_than_five_years_ago(self):
        less_than_five_years_ago = datetime.datetime.utcnow() - relativedelta(years=5) + datetime.timedelta(days=1)
        users_factories.TrustedDeviceFactory(dateCreated=less_than_five_years_ago)

        users_api.delete_old_trusted_devices()

        assert db.session.query(users_models.TrustedDevice).count() == 1


class DeleteOldLoginDeviceHistoryTest:
    def should_delete_device_history_older_than_thirteen_months_ago(self):
        thirteen_months_ago = datetime.datetime.utcnow() - relativedelta(months=13)
        fourteen_months_ago = datetime.datetime.utcnow() - relativedelta(months=14)
        users_factories.LoginDeviceHistoryFactory(dateCreated=thirteen_months_ago)
        users_factories.LoginDeviceHistoryFactory(dateCreated=fourteen_months_ago)

        users_api.delete_old_login_device_history()

        assert db.session.query(users_models.LoginDeviceHistory).count() == 0

    def should_not_delete_device_history_created_less_than_thirteen_months_ago(self):
        less_than_thirteen_months_ago = (
            datetime.datetime.utcnow() - relativedelta(months=13) + datetime.timedelta(days=1)
        )
        users_factories.LoginDeviceHistoryFactory(dateCreated=less_than_thirteen_months_ago)

        users_api.delete_old_login_device_history()

        assert db.session.query(users_models.LoginDeviceHistory).count() == 1


class RefreshAccessTokenTest:
    def should_create_access_token_with_default_lifetime_when_no_device_info(self):
        user = users_factories.UserFactory()

        refresh_token = users_api.create_user_refresh_token(user=user, device_info=None)
        decoded_refresh_token = decode_token(refresh_token)

        token_issue_date = decoded_refresh_token["iat"]
        token_expiration_date = decoded_refresh_token["exp"]
        refresh_token_lifetime = token_expiration_date - token_issue_date

        assert refresh_token_lifetime == settings.JWT_REFRESH_TOKEN_EXPIRES

    def should_create_access_token_with_default_lifetime_when_device_is_not_a_trusted_device(self):
        user = users_factories.UserFactory()
        users_factories.TrustedDeviceFactory(user=user)
        other_device = account_serialization.TrustedDevice(deviceId="other-device-id", os="iOS", source="iPhone 13")

        refresh_token = users_api.create_user_refresh_token(user=user, device_info=other_device)
        decoded_refresh_token = decode_token(refresh_token)

        token_issue_date = decoded_refresh_token["iat"]
        token_expiration_date = decoded_refresh_token["exp"]
        refresh_token_lifetime = token_expiration_date - token_issue_date

        assert refresh_token_lifetime == settings.JWT_REFRESH_TOKEN_EXPIRES

    def should_create_access_token_with_extended_lifetime_when_device_is_a_trusted_device(self):
        user = users_factories.UserFactory()
        trusted_device = users_factories.TrustedDeviceFactory(user=user)
        device_info = account_serialization.TrustedDevice(
            deviceId=trusted_device.deviceId, os="iOS", source="iPhone 13"
        )

        refresh_token = users_api.create_user_refresh_token(user=user, device_info=device_info)
        decoded_refresh_token = decode_token(refresh_token)

        token_issue_date = decoded_refresh_token["iat"]
        token_expiration_date = decoded_refresh_token["exp"]
        refresh_token_lifetime = token_expiration_date - token_issue_date

        assert refresh_token_lifetime == settings.JWT_REFRESH_TOKEN_EXTENDED_EXPIRES


class NotifyUserBeforeDeletionUponSuspensionTest:
    def test_get_users_with_suspended_account_to_notify(self):
        delta_time = 5
        exact_time = datetime.datetime.utcnow() - datetime.timedelta(days=delta_time)
        suspension_to_be_detected = history_factories.SuspendedUserActionHistoryFactory(
            actionDate=exact_time, reason=users_constants.SuspensionReason.UPON_USER_REQUEST
        )

        # not suspended upon user request: should be ignored
        history_factories.SuspendedUserActionHistoryFactory(
            actionDate=exact_time, reason=users_constants.SuspensionReason.FRAUD_SUSPICION
        )

        # suspended one day after: should be ignored
        history_factories.SuspendedUserActionHistoryFactory(
            actionDate=exact_time + datetime.timedelta(days=1),
            reason=users_constants.SuspensionReason.UPON_USER_REQUEST,
        )

        # suspended one day before: should be ignored
        history_factories.SuspendedUserActionHistoryFactory(
            actionDate=exact_time - datetime.timedelta(days=1),
            reason=users_constants.SuspensionReason.UPON_USER_REQUEST,
        )

        # should not be notified because unsuspended
        user = users_factories.UserFactory(isActive=False)
        history_factories.SuspendedUserActionHistoryFactory(
            user=user, actionDate=exact_time, reason=users_constants.SuspensionReason.FRAUD_SUSPICION
        )
        history_factories.UnsuspendedUserActionHistoryFactory(user=user, actionDate=datetime.datetime.utcnow())

        expected_user_ids = {suspension_to_be_detected.userId}

        with assert_num_queries(1):
            query = users_api._get_users_with_suspended_account_to_notify(delta_time)
            user_ids = {user.id for user in query}
            assert user_ids == expected_user_ids

    def test_notify_user_before_deletion_upon_suspension(self, app):
        # given
        exact_time = datetime.datetime.utcnow() - datetime.timedelta(
            days=settings.DELETE_SUSPENDED_ACCOUNTS_SINCE - settings.NOTIFY_X_DAYS_BEFORE_DELETION
        )
        suspension_to_be_detected = history_factories.SuspendedUserActionHistoryFactory(
            actionDate=exact_time, reason=users_constants.SuspensionReason.UPON_USER_REQUEST
        )

        # not suspended upon user request: should be ignored
        history_factories.SuspendedUserActionHistoryFactory(
            actionDate=exact_time, reason=users_constants.SuspensionReason.FRAUD_SUSPICION
        )

        # suspended one day after: should be ignored
        history_factories.SuspendedUserActionHistoryFactory(
            actionDate=exact_time + datetime.timedelta(days=1),
            reason=users_constants.SuspensionReason.UPON_USER_REQUEST,
        )

        # suspended one day before: should be ignored
        history_factories.SuspendedUserActionHistoryFactory(
            actionDate=exact_time - datetime.timedelta(days=1),
            reason=users_constants.SuspensionReason.UPON_USER_REQUEST,
        )

        # should not be notified because unsuspended
        user = users_factories.UserFactory(isActive=False)
        history_factories.SuspendedUserActionHistoryFactory(
            user=user, actionDate=exact_time, reason=users_constants.SuspensionReason.FRAUD_SUSPICION
        )
        history_factories.UnsuspendedUserActionHistoryFactory(user=user, actionDate=datetime.datetime.utcnow())

        # when
        users_api.notify_users_before_deletion_of_suspended_account()

        # then
        user = db.session.get(users_models.User, suspension_to_be_detected.userId)
        assert len(mails_testing.outbox) == 1
        assert mails_testing.outbox[0]["params"]["FIRSTNAME"] == user.firstName
        assert mails_testing.outbox[0]["To"] == user.email

    def test_multiple_suspensions_different_reason(self):
        exact_time = datetime.datetime.utcnow() - datetime.timedelta(
            days=settings.DELETE_SUSPENDED_ACCOUNTS_SINCE - settings.NOTIFY_X_DAYS_BEFORE_DELETION
        )
        user = users_factories.UserFactory(isActive=False)
        history_factories.SuspendedUserActionHistoryFactory(
            user=user, actionDate=exact_time, reason=users_constants.SuspensionReason.UPON_USER_REQUEST
        )
        history_factories.UnsuspendedUserActionHistoryFactory(
            user=user, actionDate=exact_time + datetime.timedelta(minutes=1)
        )
        history_factories.SuspendedUserActionHistoryFactory(
            user=user,
            actionDate=exact_time + datetime.timedelta(minutes=2),
            reason=users_constants.SuspensionReason.FRAUD_SUSPICION,
        )

        # when
        users_api.notify_users_before_deletion_of_suspended_account()

        # then
        assert len(mails_testing.outbox) == 0

    def test_multiple_suspensions_different_date(self):
        exact_time = datetime.datetime.utcnow() - datetime.timedelta(
            days=settings.DELETE_SUSPENDED_ACCOUNTS_SINCE - settings.NOTIFY_X_DAYS_BEFORE_DELETION
        )
        user = users_factories.UserFactory(isActive=False)
        history_factories.SuspendedUserActionHistoryFactory(
            user=user, actionDate=exact_time, reason=users_constants.SuspensionReason.UPON_USER_REQUEST
        )
        history_factories.UnsuspendedUserActionHistoryFactory(
            user=user, actionDate=exact_time + datetime.timedelta(minutes=1)
        )
        history_factories.SuspendedUserActionHistoryFactory(
            user=user,
            actionDate=exact_time + datetime.timedelta(days=1),
            reason=users_constants.SuspensionReason.UPON_USER_REQUEST,
        )

        # when
        users_api.notify_users_before_deletion_of_suspended_account()

        # then
        assert len(mails_testing.outbox) == 0


@pytest.mark.usefixtures("db_session")
class GetSuspendedAccountsUponUserRequestSinceTest:
    def test_get_suspended_upon_user_request_accounts_since(self) -> None:
        one_week_ago = datetime.datetime.utcnow() - datetime.timedelta(days=7)
        something = history_factories.SuspendedUserActionHistoryFactory(
            actionDate=one_week_ago, reason=users_constants.SuspensionReason.UPON_USER_REQUEST
        )

        # not suspended upon user request: should be ignored
        history_factories.SuspendedUserActionHistoryFactory(
            actionDate=one_week_ago, reason=users_constants.SuspensionReason.FRAUD_SUSPICION
        )

        # suspended less than 5 days ago (see below): should be ignored
        yesterday = datetime.datetime.utcnow() - datetime.timedelta(days=1)
        history_factories.SuspendedUserActionHistoryFactory(
            actionDate=yesterday, reason=users_constants.SuspensionReason.UPON_USER_REQUEST
        )

        expected_user_ids = {something.userId}

        with assert_num_queries(1):
            query = users_api.get_suspended_upon_user_request_accounts_since(5)
            user_ids = {user.id for user in query}
            assert user_ids == expected_user_ids

    def test_unsuspended_account(self) -> None:
        """
        Test that an unsuspended account is ignored, even if the
        suspension event occurred more than N days ago.
        """
        one_week_ago = datetime.datetime.utcnow() - datetime.timedelta(days=7)
        user = users_factories.UserFactory(isActive=False)
        history_factories.SuspendedUserActionHistoryFactory(
            user=user, actionDate=one_week_ago, reason=users_constants.SuspensionReason.FRAUD_SUSPICION
        )

        yesterday = datetime.datetime.utcnow() - datetime.timedelta(days=1)
        history_factories.UnsuspendedUserActionHistoryFactory(user=user, actionDate=yesterday)

        with assert_num_queries(1):
            assert not list(users_api.get_suspended_upon_user_request_accounts_since(5))


class AnonymizeNonProNonBeneficiaryUsersTest:
    def import_iris(self):
        path = DATA_DIR / "iris_min.7z"
        geography_api.import_iris_from_7z(str(path))

    def test_anonymize_non_pro_non_beneficiary_users(self) -> None:
        user_to_anonymize = users_factories.UserFactory(
            firstName="user_to_anonymize",
            lastConnectionDate=datetime.datetime.utcnow() - relativedelta(years=3, days=1),
            validatedBirthDate=datetime.date.today(),
        )
        user_too_new = users_factories.UserFactory(
            firstName="user_too_new",
            lastConnectionDate=datetime.datetime.utcnow() - relativedelta(years=3, days=-11),
        )
        user_never_connected = users_factories.UserFactory(firstName="user_never_connected", lastConnectionDate=None)
        user_beneficiary = users_factories.BeneficiaryGrant18Factory(
            firstName="user_beneficiary",
        )
        user_underage_beneficiary = users_factories.UnderageBeneficiaryFactory(
            firstName="user_underage_beneficiary",
        )
        user_pro = users_factories.ProFactory(
            firstName="user_pro",
        )
        user_pass_culture = users_factories.ProFactory(
            firstName="user_pass_culture", email="user_pass_culture@passculture.app"
        )
        user_anonymized = users_factories.ProFactory(
            firstName="user_anonymized", email="user_anonymized@anonymized.passculture"
        )

        self.import_iris()
        iris = db.session.query(geography_models.IrisFrance).first()

        with mock.patch("pcapi.core.users.api.get_iris_from_address", return_value=iris):
            users_api.anonymize_non_pro_non_beneficiary_users()

        db.session.refresh(user_to_anonymize)
        db.session.refresh(user_too_new)
        db.session.refresh(user_never_connected)
        db.session.refresh(user_beneficiary)
        db.session.refresh(user_underage_beneficiary)
        db.session.refresh(user_pro)
        db.session.refresh(user_pass_culture)
        db.session.refresh(user_anonymized)

        assert len(sendinblue_testing.sendinblue_requests) == 1
        assert len(batch_testing.requests) == 1
        assert batch_testing.requests[0]["user_id"] == user_to_anonymize.id

        # these profiles should not have been anonymized
        assert user_too_new.firstName == "user_too_new"
        assert user_never_connected.firstName == "user_never_connected"
        assert user_beneficiary.firstName == "user_beneficiary"
        assert user_underage_beneficiary.firstName == "user_underage_beneficiary"
        assert user_pro.firstName == "user_pro"
        assert user_pass_culture.firstName == "user_pass_culture"
        assert user_anonymized.firstName == "user_anonymized"

        # only one profile should have been anonymized
        for beneficiary_fraud_check in user_to_anonymize.beneficiaryFraudChecks:
            assert beneficiary_fraud_check.resultContent is None
            assert beneficiary_fraud_check.reason == "Anonymized"
            assert beneficiary_fraud_check.dateCreated.day == 1
            assert beneficiary_fraud_check.dateCreated.month == 1
            assert beneficiary_fraud_check.updatedAt.day == 1
            assert beneficiary_fraud_check.updatedAt.month == 1

        for beneficiary_fraud_review in user_to_anonymize.beneficiaryFraudReviews:
            assert beneficiary_fraud_review.reason == "Anonymized"
            assert beneficiary_fraud_review.dateReviewed.day == 1
            assert beneficiary_fraud_review.dateReviewed.month == 1

        assert user_to_anonymize.email == f"anonymous_{user_to_anonymize.id}@anonymized.passculture"
        assert user_to_anonymize.password == b"Anonymized"
        assert user_to_anonymize.firstName is None
        assert user_to_anonymize.lastName is None
        assert user_to_anonymize.married_name is None
        assert user_to_anonymize.postalCode is None
        assert user_to_anonymize.phoneNumber is None
        assert user_to_anonymize.dateOfBirth.day == 1
        assert user_to_anonymize.dateOfBirth.month == 1
        assert user_to_anonymize.address is None
        assert user_to_anonymize.city is None
        assert user_to_anonymize.externalIds == []
        assert user_to_anonymize.idPieceNumber is None
        assert user_to_anonymize.login_device_history == []
        assert user_to_anonymize.user_email_history == []
        assert user_to_anonymize.irisFrance == iris
        assert user_to_anonymize.validatedBirthDate.day == 1
        assert user_to_anonymize.validatedBirthDate.month == 1
        assert user_to_anonymize.roles == [users_models.UserRole.ANONYMIZED]
        assert user_to_anonymize.login_device_history == []
        assert user_to_anonymize.trusted_devices == []
        assert len(user_to_anonymize.action_history) == 1
        assert user_to_anonymize.action_history[0].actionType == history_models.ActionType.USER_ANONYMIZED
        assert user_to_anonymize.action_history[0].authorUserId is None

    def test_anonymize_non_pro_non_beneficiary_user_force_iris_not_found(self) -> None:
        user_to_anonymize = users_factories.UserFactory(
            firstName="user_to_anonymize",
            lastConnectionDate=datetime.datetime.utcnow() - relativedelta(years=3, days=1),
        )

        users_api.anonymize_non_pro_non_beneficiary_users()

        db.session.refresh(user_to_anonymize)

        assert len(sendinblue_testing.sendinblue_requests) == 1
        assert len(batch_testing.requests) == 1
        assert batch_testing.requests[0]["user_id"] == user_to_anonymize.id
        assert user_to_anonymize.firstName is None

    def test_anonymize_non_pro_non_beneficiary_user_keep_history_on_offerer(self) -> None:
        user_to_anonymize = users_factories.UserFactory(
            firstName="user_to_anonymize",
            lastConnectionDate=datetime.datetime.utcnow() - relativedelta(years=3, days=1),
        )
        history_factories.ActionHistoryFactory(
            authorUser=user_to_anonymize,
            user=user_to_anonymize,
            offerer=offerers_factories.OffererFactory(),
            actionType=history_models.ActionType.OFFERER_VALIDATED,
        )

        users_api.anonymize_non_pro_non_beneficiary_users()

        db.session.refresh(user_to_anonymize)

        assert user_to_anonymize.firstName is None
        assert (
            db.session.query(history_models.ActionHistory)
            .filter(history_models.ActionHistory.userId == user_to_anonymize.id)
            .count()
            == 2
        )

    def test_anonymize_non_pro_non_beneficiary_user_keep_email_in_brevo_if_used_for_venue(self) -> None:
        user_to_anonymize = users_factories.UserFactory(
            firstName="user_to_anonymize",
            lastConnectionDate=datetime.datetime.utcnow() - relativedelta(years=3, days=1),
        )
        offerers_factories.VenueFactory(bookingEmail=user_to_anonymize.email)

        users_api.anonymize_non_pro_non_beneficiary_users()
        db.session.refresh(user_to_anonymize)

        assert user_to_anonymize.firstName is None
        assert user_to_anonymize.email == f"anonymous_{user_to_anonymize.id}@anonymized.passculture"
        assert sendinblue_testing.sendinblue_requests[0]["attributes"]["FIRSTNAME"] == ""

    @pytest.mark.parametrize(
        "reason",
        [
            users_constants.SuspensionReason.FRAUD_BOOKING_CANCEL,
            users_constants.SuspensionReason.FRAUD_CREATION_PRO,
            users_constants.SuspensionReason.FRAUD_DUPLICATE,
            users_constants.SuspensionReason.FRAUD_FAKE_DOCUMENT,
            users_constants.SuspensionReason.FRAUD_HACK,
            users_constants.SuspensionReason.FRAUD_RESELL_PASS,
            users_constants.SuspensionReason.FRAUD_RESELL_PRODUCT,
            users_constants.SuspensionReason.FRAUD_SUSPICION,
            users_constants.SuspensionReason.FRAUD_USURPATION,
            users_constants.SuspensionReason.FRAUD_USURPATION_PRO,
            users_constants.SuspensionReason.SUSPICIOUS_LOGIN_REPORTED_BY_USER,
            users_constants.SuspensionReason.SUSPENSION_FOR_INVESTIGATION_TEMP,
        ],
    )
    def test_anonymize_non_pro_non_beneficiary_user_recently_suspended_with_fraud(self, reason) -> None:
        user_to_anonymize = users_factories.UserFactory(
            firstName="user_to_anonymize",
            lastConnectionDate=datetime.datetime.utcnow() - relativedelta(years=3, days=1),
            isActive=False,
        )
        history_factories.SuspendedUserActionHistoryFactory(
            actionDate=datetime.datetime.utcnow() - relativedelta(years=3, days=1),
            actionType=history_models.ActionType.USER_SUSPENDED,
            reason=reason,
            user=user_to_anonymize,
        )

        users_api.anonymize_non_pro_non_beneficiary_users()

        db.session.refresh(user_to_anonymize)

        assert len(sendinblue_testing.sendinblue_requests) == 0
        assert user_to_anonymize.firstName == "user_to_anonymize"

    def test_anonymize_non_pro_non_beneficiary_user_suspended_5_years_ago_with_fraud(self) -> None:
        user_to_anonymize = users_factories.UserFactory(
            firstName="user_to_anonymize",
            lastConnectionDate=datetime.datetime.utcnow() - relativedelta(years=3, days=1),
            isActive=False,
        )
        history_factories.SuspendedUserActionHistoryFactory(
            actionDate=datetime.datetime.utcnow() - relativedelta(years=5, days=1),
            actionType=history_models.ActionType.USER_SUSPENDED,
            reason=users_constants.SuspensionReason.FRAUD_RESELL_PRODUCT,
            user=user_to_anonymize,
        )

        users_api.anonymize_non_pro_non_beneficiary_users()

        db.session.refresh(user_to_anonymize)

        assert len(sendinblue_testing.sendinblue_requests) == 1
        assert user_to_anonymize.firstName != "user_to_anonymize"

    def test_anonymize_non_pro_non_beneficiary_user_recently_suspended_without_fraud(self) -> None:
        user_to_anonymize = users_factories.UserFactory(
            firstName="user_to_anonymize",
            lastConnectionDate=datetime.datetime.utcnow() - relativedelta(years=3, days=1),
            isActive=False,
        )
        history_factories.SuspendedUserActionHistoryFactory(
            actionDate=datetime.datetime.utcnow() - relativedelta(years=3, days=1),
            actionType=history_models.ActionType.USER_SUSPENDED,
            reason=users_constants.SuspensionReason.DEVICE_AT_RISK,
            user=user_to_anonymize,
        )

        users_api.anonymize_non_pro_non_beneficiary_users()

        db.session.refresh(user_to_anonymize)

        assert len(sendinblue_testing.sendinblue_requests) == 1
        assert user_to_anonymize.firstName != "user_to_anonymize"


class NotifyProUsersBeforeAnonymizationTest:
    # users and joined data
    expected_num_queries = 1

    last_connection_date = datetime.datetime.utcnow() - relativedelta(years=3, days=-30)

    @pytest.mark.parametrize(
        "offerer_validation_status,user_offerer_validation_status",
        [
            (ValidationStatus.NEW, ValidationStatus.REJECTED),
            (ValidationStatus.PENDING, ValidationStatus.REJECTED),
            (ValidationStatus.VALIDATED, ValidationStatus.REJECTED),
            (ValidationStatus.VALIDATED, ValidationStatus.DELETED),
            (ValidationStatus.REJECTED, ValidationStatus.VALIDATED),
            (ValidationStatus.REJECTED, ValidationStatus.REJECTED),
            (ValidationStatus.CLOSED, ValidationStatus.VALIDATED),
            (ValidationStatus.CLOSED, ValidationStatus.DELETED),
        ],
    )
    def test_notify(self, offerer_validation_status, user_offerer_validation_status):
        user_offerer = offerers_factories.NonAttachedUserOffererFactory(
            user__email="test@example.com",
            user__lastConnectionDate=self.last_connection_date,
            offerer__validationStatus=offerer_validation_status,
            validationStatus=user_offerer_validation_status,
        )
        offerers_factories.NonAttachedUserOffererFactory(
            offerer=user_offerer.offerer,
            user__lastConnectionDate=self.last_connection_date - datetime.timedelta(days=1),
            validationStatus=user_offerer_validation_status,
        )
        offerers_factories.NonAttachedUserOffererFactory(
            offerer=user_offerer.offerer,
            user__lastConnectionDate=datetime.datetime.utcnow() - relativedelta(years=2, months=8),
            validationStatus=user_offerer_validation_status,
        )

        with assert_num_queries(self.expected_num_queries):
            users_api.notify_pro_users_before_anonymization()

        assert len(mails_testing.outbox) == 1
        assert mails_testing.outbox[0]["To"] == "test@example.com"
        assert mails_testing.outbox[0]["template"] == dataclasses.asdict(TransactionalEmail.PRO_PRE_ANONYMIZATION.value)

    def test_notify_non_attached_pro_user(self):
        user_to_notify = users_factories.NonAttachedProFactory(
            lastConnectionDate=self.last_connection_date,
        )
        users_factories.NonAttachedProFactory(lastConnectionDate=datetime.datetime.utcnow())

        with assert_num_queries(self.expected_num_queries):
            users_api.notify_pro_users_before_anonymization()

        assert len(mails_testing.outbox) == 1
        assert mails_testing.outbox[0]["To"] == user_to_notify.email
        assert mails_testing.outbox[0]["template"] == dataclasses.asdict(TransactionalEmail.PRO_PRE_ANONYMIZATION.value)

    def test_notify_never_connected_pro(self):
        user_to_notify = users_factories.NonAttachedProFactory(dateCreated=self.last_connection_date)
        users_factories.NonAttachedProFactory()

        with assert_num_queries(self.expected_num_queries):
            users_api.notify_pro_users_before_anonymization()

        assert len(mails_testing.outbox) == 1
        assert mails_testing.outbox[0]["To"] == user_to_notify.email
        assert mails_testing.outbox[0]["template"] == dataclasses.asdict(TransactionalEmail.PRO_PRE_ANONYMIZATION.value)

    def test_do_not_notify(self):
        users = []

        for offerer_validation_status, user_offerer_validation_status in [
            (ValidationStatus.NEW, ValidationStatus.VALIDATED),
            (ValidationStatus.PENDING, ValidationStatus.VALIDATED),
            (ValidationStatus.VALIDATED, ValidationStatus.NEW),
            (ValidationStatus.VALIDATED, ValidationStatus.VALIDATED),
        ]:
            users.append(
                offerers_factories.NonAttachedUserOffererFactory(
                    user__lastConnectionDate=self.last_connection_date,
                    offerer__validationStatus=offerer_validation_status,
                    validationStatus=user_offerer_validation_status,
                ).user
            )

        # Less than three years
        users.extend(
            [
                users_factories.NonAttachedProFactory(
                    lastConnectionDate=self.last_connection_date - datetime.timedelta(days=1)
                ),
                users_factories.NonAttachedProFactory(lastConnectionDate=datetime.datetime.utcnow()),
            ]
        )

        # Also beneficiary or candidate to become beneficiary
        users.append(
            offerers_factories.DeletedUserOffererFactory(
                user=users_factories.BeneficiaryGrant18Factory(
                    roles=[users_models.UserRole.NON_ATTACHED_PRO, users_models.UserRole.BENEFICIARY],
                    lastConnectionDate=self.last_connection_date,
                )
            ).user
        )
        users.append(
            offerers_factories.RejectedUserOffererFactory(
                user=users_factories.UnderageBeneficiaryFactory(
                    roles=[users_models.UserRole.NON_ATTACHED_PRO, users_models.UserRole.UNDERAGE_BENEFICIARY],
                    lastConnectionDate=self.last_connection_date,
                )
            ).user
        )
        users.append(
            fraud_factories.BeneficiaryFraudCheckFactory(
                user=offerers_factories.RejectedUserOffererFactory(
                    user__lastConnectionDate=self.last_connection_date,
                ).user
            ).user
        )

        # Attached to another active offerer
        user_offerer = offerers_factories.DeletedUserOffererFactory(
            user__lastConnectionDate=self.last_connection_date,
        )
        offerers_factories.NewUserOffererFactory(user=user_offerer.user)
        users.append(user_offerer.user)

        with assert_num_queries(self.expected_num_queries):
            users_api.notify_pro_users_before_anonymization()

        for user in users:
            assert user.has_any_pro_role
        assert len(mails_testing.outbox) == 0


class AnonymizeProUserTest:
    @pytest.mark.features(WIP_ENABLE_PRO_ANONYMIZATION=True)
    @pytest.mark.parametrize(
        "offerer_validation_status,user_offerer_validation_status",
        [
            (ValidationStatus.NEW, ValidationStatus.REJECTED),
            (ValidationStatus.PENDING, ValidationStatus.REJECTED),
            (ValidationStatus.VALIDATED, ValidationStatus.REJECTED),
            (ValidationStatus.VALIDATED, ValidationStatus.DELETED),
            (ValidationStatus.REJECTED, ValidationStatus.VALIDATED),
            (ValidationStatus.REJECTED, ValidationStatus.REJECTED),
            (ValidationStatus.CLOSED, ValidationStatus.VALIDATED),
            (ValidationStatus.CLOSED, ValidationStatus.DELETED),
        ],
    )
    @mock.patch("pcapi.core.users.api.delete_beamer_user")
    def test_anonymize_pro_user(
        self, delete_beamer_user_mock, offerer_validation_status, user_offerer_validation_status
    ):
        user_offerer_to_anonymize = offerers_factories.NonAttachedUserOffererFactory(
            user__lastConnectionDate=datetime.datetime.utcnow() - datetime.timedelta(days=366 * 3),
            offerer__validationStatus=offerer_validation_status,
            validationStatus=user_offerer_validation_status,
        )
        user_offerer_to_keep = offerers_factories.NonAttachedUserOffererFactory(
            offerer=user_offerer_to_anonymize.offerer,
            user__lastConnectionDate=datetime.datetime.utcnow(),
        )

        users_api.anonymize_pro_users()

        _assert_user_is_anonymized(user_offerer_to_anonymize.user)
        assert user_offerer_to_keep.user.has_non_attached_pro_role
        delete_beamer_user_mock.assert_called_once_with(user_offerer_to_anonymize.user.id)

    @pytest.mark.features(WIP_ENABLE_PRO_ANONYMIZATION=True)
    @mock.patch("pcapi.core.users.api.delete_beamer_user")
    def test_keep_pro_users_with_activity_less_than_three_years(self, delete_beamer_user_mock):
        users_factories.NonAttachedProFactory(
            lastConnectionDate=datetime.datetime.utcnow() - relativedelta(years=3, days=-1)
        )
        users_factories.NonAttachedProFactory(lastConnectionDate=datetime.datetime.utcnow())

        users_api.anonymize_pro_users()

        assert db.session.query(users_models.User).filter(users_models.User.has_non_attached_pro_role).count() == 2
        delete_beamer_user_mock.assert_not_called()

    @pytest.mark.features(WIP_ENABLE_PRO_ANONYMIZATION=True)
    @mock.patch("pcapi.core.users.api.delete_beamer_user")
    def test_keep_pro_users_also_beneficiariy_or_candidate(self, delete_beamer_user_mock):
        offerers_factories.DeletedUserOffererFactory(
            user=users_factories.BeneficiaryGrant18Factory(
                roles=[users_models.UserRole.NON_ATTACHED_PRO, users_models.UserRole.BENEFICIARY],
                lastConnectionDate=datetime.datetime.utcnow() - relativedelta(years=4),
            )
        )
        offerers_factories.RejectedUserOffererFactory(
            user=users_factories.UnderageBeneficiaryFactory(
                roles=[users_models.UserRole.NON_ATTACHED_PRO, users_models.UserRole.UNDERAGE_BENEFICIARY],
                lastConnectionDate=datetime.datetime.utcnow() - relativedelta(years=4),
            )
        )
        fraud_factories.BeneficiaryFraudCheckFactory(
            user=offerers_factories.RejectedUserOffererFactory(
                user__lastConnectionDate=datetime.datetime.utcnow() - relativedelta(years=4),
            ).user
        )

        users_api.anonymize_pro_users()

        assert db.session.query(users_models.User).filter(users_models.User.has_non_attached_pro_role).count() == 3
        delete_beamer_user_mock.assert_not_called()

    @pytest.mark.features(WIP_ENABLE_PRO_ANONYMIZATION=True)
    @mock.patch("pcapi.core.users.api.delete_beamer_user")
    def test_keep_when_attached_to_another_active_offerer(self, delete_beamer_user_mock):
        user_offerer = offerers_factories.DeletedUserOffererFactory(
            user__lastConnectionDate=datetime.datetime.utcnow() - relativedelta(years=4),
        )
        offerers_factories.NewUserOffererFactory(user=user_offerer.user)

        users_api.anonymize_pro_users()

        assert user_offerer.user.has_any_pro_role
        delete_beamer_user_mock.assert_not_called()

    @pytest.mark.features(WIP_ENABLE_PRO_ANONYMIZATION=True)
    @mock.patch("pcapi.core.users.api.delete_beamer_user")
    def test_anonymize_non_attached_pro_user(self, delete_beamer_user_mock):
        user_to_anonymize = users_factories.NonAttachedProFactory(
            lastConnectionDate=datetime.datetime.utcnow() - datetime.timedelta(days=366 * 3)
        )
        user_to_keep1 = users_factories.NonAttachedProFactory(lastConnectionDate=datetime.datetime.utcnow())
        user_to_keep2 = users_factories.NonAttachedProFactory()

        users_api.anonymize_pro_users()

        _assert_user_is_anonymized(user_to_anonymize)
        assert user_to_keep1.has_non_attached_pro_role
        assert user_to_keep2.has_non_attached_pro_role
        delete_beamer_user_mock.assert_called_once_with(user_to_anonymize.id)

    @pytest.mark.features(WIP_ENABLE_PRO_ANONYMIZATION=True)
    @mock.patch("pcapi.core.users.api.delete_beamer_user")
    def test_anonymize_non_attached_never_connected_pro(self, delete_beamer_user_mock):
        user_to_anonymize = users_factories.NonAttachedProFactory(
            dateCreated=datetime.datetime.utcnow() - datetime.timedelta(days=366 * 3)
        )
        user_to_keep = users_factories.NonAttachedProFactory()

        users_api.anonymize_pro_users()

        _assert_user_is_anonymized(user_to_anonymize)
        assert user_to_keep.has_non_attached_pro_role
        delete_beamer_user_mock.assert_called_once_with(user_to_anonymize.id)

    @pytest.mark.features(WIP_ENABLE_PRO_ANONYMIZATION=False)
    def test_feature_disabled(self):
        user = offerers_factories.DeletedUserOffererFactory(
            user__email="test@example.com",
            user__lastConnectionDate=datetime.datetime.utcnow() - relativedelta(years=3, months=1),
        ).user

        users_api.anonymize_pro_users()

        assert user.has_any_pro_role
        assert user.email == "test@example.com"


class AnonymizeBeneficiaryUsersTest(StorageFolderManager):
    storage_folder = settings.LOCAL_STORAGE_DIR / settings.GCP_GDPR_EXTRACT_BUCKET / settings.GCP_GDPR_EXTRACT_FOLDER

    def import_iris(self):
        path = DATA_DIR / "iris_min.7z"
        geography_api.import_iris_from_7z(str(path))

    def test_anonymize_beneficiary_users(self) -> None:
        user_beneficiary_to_anonymize = users_factories.BeneficiaryFactory(
            firstName="user_beneficiary_to_anonymize",
            age=18,
            lastConnectionDate=datetime.datetime.utcnow() - relativedelta(years=3, days=1),
            deposit__expirationDate=datetime.datetime.utcnow() - relativedelta(years=5, days=1),
        )
        user_underage_beneficiary_to_anonymize = users_factories.BeneficiaryFactory(
            firstName="user_underage_beneficiary_to_anonymize",
            age=17,
            lastConnectionDate=datetime.datetime.utcnow() - relativedelta(years=3, days=1),
            deposit__expirationDate=datetime.datetime.utcnow() - relativedelta(years=5, days=1),
        )
        user_with_ready_gdpr_extract_to_anonymize = users_factories.BeneficiaryFactory(
            firstName="user_beneficiary_to_anonymize",
            age=18,
            lastConnectionDate=datetime.datetime.utcnow() - relativedelta(years=3, days=1),
            gdprUserDataExtracts=[
                users_factories.GdprUserDataExtractBeneficiaryFactory(
                    dateProcessed=datetime.datetime.utcnow() - datetime.timedelta(days=1)
                )
            ],
            deposit__expirationDate=datetime.datetime.utcnow() - relativedelta(years=5, days=1),
        )
        user_with_expired_gdpr_extract_to_anonymize = users_factories.BeneficiaryFactory(
            firstName="user_beneficiary_to_anonymize",
            age=18,
            lastConnectionDate=datetime.datetime.utcnow() - relativedelta(years=3, days=1),
            gdprUserDataExtracts=[
                users_factories.GdprUserDataExtractBeneficiaryFactory(
                    dateCreated=datetime.datetime.utcnow() - datetime.timedelta(days=8)
                )
            ],
            deposit__expirationDate=datetime.datetime.utcnow() - relativedelta(years=5, days=1),
        )
        user_too_new = users_factories.BeneficiaryFactory(
            firstName="user_too_new",
            age=18,
            lastConnectionDate=datetime.datetime.utcnow() - relativedelta(years=3, days=-11),
            deposit__expirationDate=datetime.datetime.utcnow() - relativedelta(years=5, days=1),
        )
        user_deposit_too_new = users_factories.BeneficiaryFactory(
            firstName="user_deposit_too_new",
            age=18,
            lastConnectionDate=datetime.datetime.utcnow() - relativedelta(years=3, days=1),
            deposit__expirationDate=datetime.datetime.utcnow() - relativedelta(years=5, days=-11),
        )
        user_never_connected = users_factories.UserFactory(firstName="user_never_connected", lastConnectionDate=None)
        user_no_role = users_factories.UserFactory(
            firstName="user_no_role",
        )
        user_pro = users_factories.ProFactory(
            firstName="user_pro",
        )
        user_pass_culture = users_factories.ProFactory(
            firstName="user_pass_culture", email="user_pass_culture@passculture.app"
        )
        user_anonymized = users_factories.ProFactory(
            firstName="user_anonymized", email="user_anonymized@anonymized.passculture"
        )

        self.import_iris()
        iris = db.session.query(geography_models.IrisFrance).first()

        with open(
            self.storage_folder / f"{user_with_expired_gdpr_extract_to_anonymize.gdprUserDataExtracts[0].id}.zip", "wb"
        ):
            pass

        with mock.patch("pcapi.core.users.api.get_iris_from_address", return_value=iris):
            users_api.anonymize_beneficiary_users()

        db.session.refresh(user_beneficiary_to_anonymize)
        db.session.refresh(user_underage_beneficiary_to_anonymize)
        db.session.refresh(user_with_ready_gdpr_extract_to_anonymize)
        db.session.refresh(user_with_expired_gdpr_extract_to_anonymize)
        db.session.refresh(user_too_new)
        db.session.refresh(user_deposit_too_new)
        db.session.refresh(user_never_connected)
        db.session.refresh(user_no_role)
        db.session.refresh(user_pro)
        db.session.refresh(user_pass_culture)
        db.session.refresh(user_anonymized)

        assert len(sendinblue_testing.sendinblue_requests) == 4
        assert len(batch_testing.requests) == 4
        user_id_set = set(request["user_id"] for request in batch_testing.requests)
        assert user_id_set == {
            user_beneficiary_to_anonymize.id,
            user_underage_beneficiary_to_anonymize.id,
            user_with_ready_gdpr_extract_to_anonymize.id,
            user_with_expired_gdpr_extract_to_anonymize.id,
        }

        # these profiles should not have been anonymized
        assert user_too_new.firstName == "user_too_new"
        assert user_deposit_too_new.firstName == "user_deposit_too_new"
        assert user_never_connected.firstName == "user_never_connected"
        assert user_no_role.firstName == "user_no_role"
        assert user_pro.firstName == "user_pro"
        assert user_pass_culture.firstName == "user_pass_culture"
        assert user_anonymized.firstName == "user_anonymized"
        assert len(os.listdir(self.storage_folder)) == 0

        for user_to_anonymize in [
            user_beneficiary_to_anonymize,
            user_underage_beneficiary_to_anonymize,
            user_with_ready_gdpr_extract_to_anonymize,
            user_with_expired_gdpr_extract_to_anonymize,
        ]:
            for beneficiary_fraud_check in user_to_anonymize.beneficiaryFraudChecks:
                assert beneficiary_fraud_check.resultContent is None
                assert beneficiary_fraud_check.reason == "Anonymized"
                assert beneficiary_fraud_check.dateCreated.day == 1
                assert beneficiary_fraud_check.dateCreated.month == 1

            for beneficiary_fraud_review in user_to_anonymize.beneficiaryFraudReviews:
                assert beneficiary_fraud_review.reason == "Anonymized"
                assert beneficiary_fraud_review.dateReviewed.day == 1
                assert beneficiary_fraud_review.dateReviewed.month == 1

            for deposit in user_to_anonymize.deposits:
                assert deposit.source == "Anonymized"

            assert (
                db.session.query(users_models.GdprUserDataExtract)
                .filter(users_models.GdprUserDataExtract.userId == user_to_anonymize.id)
                .count()
                == 0
            )

            _assert_user_is_anonymized(user_to_anonymize)
            assert user_to_anonymize.dateOfBirth.day == 1
            assert user_to_anonymize.dateOfBirth.month == 1
            assert user_to_anonymize.irisFrance == iris
            assert user_to_anonymize.validatedBirthDate.day == 1
            assert user_to_anonymize.validatedBirthDate.month == 1

    def test_clean_chronicle_on_anonymize_beneficiary_user(self) -> None:
        user_to_anonymize = users_factories.BeneficiaryFactory(
            firstName="user_to_anonymize",
            age=18,
            lastConnectionDate=datetime.datetime.utcnow() - relativedelta(years=3, days=1),
            deposit__expirationDate=datetime.datetime.utcnow() - relativedelta(years=5, days=1),
        )
        chronicle = chronicles_factories.ChronicleFactory(
            user=user_to_anonymize,
            email="radomemail@example.com",
        )

        users_api.anonymize_beneficiary_users()
        db.session.refresh(chronicle)

        assert chronicle.userId is None
        assert chronicle.email == "anonymized_email@anonymized.passculture"

    def test_anonymize_beneficiary_user_force_iris_not_found(self) -> None:
        user_to_anonymize = users_factories.BeneficiaryFactory(
            firstName="user_to_anonymize",
            age=18,
            lastConnectionDate=datetime.datetime.utcnow() - relativedelta(years=3, days=1),
            deposit__expirationDate=datetime.datetime.utcnow() - relativedelta(years=5, days=1),
        )

        users_api.anonymize_beneficiary_users()

        db.session.refresh(user_to_anonymize)

        assert len(sendinblue_testing.sendinblue_requests) == 1
        assert len(batch_testing.requests) == 1
        assert batch_testing.requests[0]["user_id"] == user_to_anonymize.id
        assert user_to_anonymize.firstName is None

    def test_anonymize_beneficiary_user_with_unprocessed_gdpr_extract(self) -> None:
        user_beneficiary_to_anonymize = users_factories.BeneficiaryFactory(
            firstName="user_beneficiary_to_anonymize",
            age=18,
            lastConnectionDate=datetime.datetime.utcnow() - relativedelta(years=3, days=1),
            gdprUserDataExtracts=[users_factories.GdprUserDataExtractBeneficiaryFactory()],
            deposit__expirationDate=datetime.datetime.utcnow() - relativedelta(years=5, days=1),
        )

        self.import_iris()
        iris = db.session.query(geography_models.IrisFrance).first()

        with mock.patch("pcapi.core.users.api.get_iris_from_address", return_value=iris):
            users_api.anonymize_beneficiary_users()

        db.session.refresh(user_beneficiary_to_anonymize)

        assert len(sendinblue_testing.sendinblue_requests) == 0
        assert user_beneficiary_to_anonymize.firstName == "user_beneficiary_to_anonymize"
        assert db.session.query(users_models.GdprUserDataExtract).count() == 1

    def test_anonymize_user_tagged_when_he_is_21(self) -> None:
        user_to_anonymize = users_factories.BeneficiaryFactory(
            validatedBirthDate=datetime.datetime.utcnow() - relativedelta(years=18, days=1),
        )
        users_factories.GdprUserAnonymizationFactory(user=user_to_anonymize)

        when_user_is_21 = datetime.datetime.utcnow() + relativedelta(years=3)
        with time_machine.travel(when_user_is_21):
            users_api.anonymize_beneficiary_users()
            db.session.refresh(user_to_anonymize)

        assert user_to_anonymize.firstName is None
        assert db.session.query(users_models.GdprUserAnonymization).count() == 0

    def test_do_not_anonymize_user_tagged_when_he_is_less_than_21(self) -> None:
        user_to_anonymize = users_factories.BeneficiaryFactory(
            lastConnectionDate=datetime.datetime.utcnow(),
            validatedBirthDate=datetime.datetime.utcnow() - relativedelta(years=18),
        )
        users_factories.GdprUserAnonymizationFactory(user=user_to_anonymize)

        when_user_is_21 = datetime.datetime.utcnow() + relativedelta(years=3)
        with time_machine.travel(when_user_is_21 - relativedelta(days=1)):
            users_api.anonymize_beneficiary_users()
            db.session.refresh(user_to_anonymize)

        assert user_to_anonymize.firstName != f"Anonymous_{user_to_anonymize.id}"
        assert db.session.query(users_models.GdprUserAnonymization).count() == 1

    @pytest.mark.parametrize(
        "reason",
        [
            users_constants.SuspensionReason.FRAUD_BOOKING_CANCEL,
            users_constants.SuspensionReason.FRAUD_CREATION_PRO,
            users_constants.SuspensionReason.FRAUD_DUPLICATE,
            users_constants.SuspensionReason.FRAUD_FAKE_DOCUMENT,
            users_constants.SuspensionReason.FRAUD_HACK,
            users_constants.SuspensionReason.FRAUD_RESELL_PASS,
            users_constants.SuspensionReason.FRAUD_RESELL_PRODUCT,
            users_constants.SuspensionReason.FRAUD_SUSPICION,
            users_constants.SuspensionReason.FRAUD_USURPATION,
            users_constants.SuspensionReason.FRAUD_USURPATION_PRO,
            users_constants.SuspensionReason.SUSPICIOUS_LOGIN_REPORTED_BY_USER,
            users_constants.SuspensionReason.SUSPENSION_FOR_INVESTIGATION_TEMP,
        ],
    )
    def test_do_not_anonymize_user_tagged_when_he_is_21_and_recently_tagged_as_fraud(self, reason) -> None:
        user_to_anonymize = users_factories.BeneficiaryFactory(
            lastConnectionDate=datetime.datetime.utcnow(),
            validatedBirthDate=datetime.datetime.utcnow() - relativedelta(years=21, days=12),
        )
        users_factories.GdprUserAnonymizationFactory(user=user_to_anonymize)
        history_factories.SuspendedUserActionHistoryFactory(
            actionDate=datetime.datetime.utcnow() - relativedelta(years=3, days=1),
            actionType=history_models.ActionType.USER_SUSPENDED,
            reason=reason,
            user=user_to_anonymize,
        )

        users_api.anonymize_beneficiary_users()
        db.session.refresh(user_to_anonymize)

        assert user_to_anonymize.firstName != f"Anonymous_{user_to_anonymize.id}"
        assert db.session.query(users_models.GdprUserAnonymization).count() == 1

    def test_do_not_anonymize_user_tagged_when_he_is_21_and_tagged_as_fraud_5_years_ago(self) -> None:
        user_to_anonymize = users_factories.BeneficiaryFactory(
            lastConnectionDate=datetime.datetime.utcnow(),
            validatedBirthDate=datetime.datetime.utcnow() - relativedelta(years=21, days=12),
        )
        users_factories.GdprUserAnonymizationFactory(user=user_to_anonymize)
        history_factories.SuspendedUserActionHistoryFactory(
            actionDate=datetime.datetime.utcnow() - relativedelta(years=5, days=1),
            actionType=history_models.ActionType.USER_SUSPENDED,
            reason=users_constants.SuspensionReason.FRAUD_RESELL_PRODUCT,
            user=user_to_anonymize,
        )

        users_api.anonymize_beneficiary_users()
        db.session.refresh(user_to_anonymize)

        assert user_to_anonymize.firstName is None
        assert db.session.query(users_models.GdprUserAnonymization).count() == 0

    @pytest.mark.parametrize(
        "reason",
        [
            users_constants.SuspensionReason.FRAUD_BOOKING_CANCEL,
            users_constants.SuspensionReason.FRAUD_CREATION_PRO,
            users_constants.SuspensionReason.FRAUD_DUPLICATE,
            users_constants.SuspensionReason.FRAUD_FAKE_DOCUMENT,
            users_constants.SuspensionReason.FRAUD_HACK,
            users_constants.SuspensionReason.FRAUD_RESELL_PASS,
            users_constants.SuspensionReason.FRAUD_RESELL_PRODUCT,
            users_constants.SuspensionReason.FRAUD_SUSPICION,
            users_constants.SuspensionReason.FRAUD_USURPATION,
            users_constants.SuspensionReason.FRAUD_USURPATION_PRO,
            users_constants.SuspensionReason.SUSPICIOUS_LOGIN_REPORTED_BY_USER,
            users_constants.SuspensionReason.SUSPENSION_FOR_INVESTIGATION_TEMP,
        ],
    )
    def test_anonymize_beneficiary_user_recently_suspended_with_fraud(self, reason) -> None:
        user_to_anonymize = users_factories.BeneficiaryFactory(
            firstName="user_to_anonymize",
            age=18,
            lastConnectionDate=datetime.datetime.utcnow() - relativedelta(years=3, days=1),
            deposit__expirationDate=datetime.datetime.utcnow() - relativedelta(years=5, days=1),
            isActive=False,
        )
        history_factories.SuspendedUserActionHistoryFactory(
            actionDate=datetime.datetime.utcnow() - relativedelta(years=3, days=1),
            actionType=history_models.ActionType.USER_SUSPENDED,
            reason=reason,
            user=user_to_anonymize,
        )

        users_api.anonymize_beneficiary_users()

        db.session.refresh(user_to_anonymize)

        assert len(sendinblue_testing.sendinblue_requests) == 0
        assert user_to_anonymize.firstName == "user_to_anonymize"

    def test_anonymize_beneficiary_user_suspended_5_years_ago_with_fraud(self) -> None:
        user_to_anonymize = users_factories.BeneficiaryFactory(
            firstName="user_to_anonymize",
            age=18,
            lastConnectionDate=datetime.datetime.utcnow() - relativedelta(years=3, days=1),
            deposit__expirationDate=datetime.datetime.utcnow() - relativedelta(years=5, days=1),
            isActive=False,
        )
        history_factories.SuspendedUserActionHistoryFactory(
            actionDate=datetime.datetime.utcnow() - relativedelta(years=5, days=1),
            actionType=history_models.ActionType.USER_SUSPENDED,
            reason=users_constants.SuspensionReason.FRAUD_RESELL_PRODUCT,
            user=user_to_anonymize,
        )

        users_api.anonymize_beneficiary_users()

        db.session.refresh(user_to_anonymize)

        assert len(sendinblue_testing.sendinblue_requests) == 1
        assert user_to_anonymize.firstName != "user_to_anonymize"

    @pytest.mark.parametrize(
        "reason",
        [
            users_constants.SuspensionReason.CLOSED_STRUCTURE_DEFINITIVE,
            users_constants.SuspensionReason.DELETED,
            users_constants.SuspensionReason.DEVICE_AT_RISK,
            users_constants.SuspensionReason.END_OF_CONTRACT,
            users_constants.SuspensionReason.END_OF_ELIGIBILITY,
            users_constants.SuspensionReason.UPON_USER_REQUEST,
            users_constants.SuspensionReason.WAITING_FOR_ANONYMIZATION,
        ],
    )
    def test_anonymize_beneficiary_user_recently_suspended_without_fraud(self, reason) -> None:
        user_to_anonymize = users_factories.BeneficiaryFactory(
            firstName="user_to_anonymize",
            age=18,
            lastConnectionDate=datetime.datetime.utcnow() - relativedelta(years=3, days=1),
            deposit__expirationDate=datetime.datetime.utcnow() - relativedelta(years=5, days=1),
            isActive=False,
        )
        history_factories.SuspendedUserActionHistoryFactory(
            actionDate=datetime.datetime.utcnow() - relativedelta(years=3, days=1),
            actionType=history_models.ActionType.USER_SUSPENDED,
            reason=reason,
            user=user_to_anonymize,
        )

        users_api.anonymize_beneficiary_users()

        db.session.refresh(user_to_anonymize)

        assert len(sendinblue_testing.sendinblue_requests) == 1
        assert user_to_anonymize.firstName != "user_to_anonymize"


class AnonymizeUserDepositsTest:
    def test_anonymize_user_deposits(self) -> None:
        now = datetime.datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        user_recent_deposit = users_factories.BeneficiaryFactory(
            deposit__dateCreated=now - relativedelta(years=6),
            deposit__expirationDate=now - relativedelta(years=5, days=1),
        )
        user_old_deposit = users_factories.BeneficiaryFactory(
            deposit__dateCreated=now - relativedelta(years=11, days=1),
            deposit__expirationDate=now - relativedelta(years=10, days=1),
        )

        users_api.anonymize_user_deposits()

        db.session.refresh(user_recent_deposit)
        db.session.refresh(user_old_deposit)

        for deposit in user_recent_deposit.deposits:
            assert deposit.dateCreated == now - relativedelta(years=6)
            assert deposit.expirationDate == now - relativedelta(years=5, days=1)

        for deposit in user_old_deposit.deposits:
            assert deposit.dateCreated == now - relativedelta(years=11, day=1, month=1)
            assert deposit.expirationDate == now - relativedelta(years=10, day=1, month=1)


class DeleteGdprExtractTest(StorageFolderManager):
    storage_folder = settings.LOCAL_STORAGE_DIR / settings.GCP_GDPR_EXTRACT_BUCKET / settings.GCP_GDPR_EXTRACT_FOLDER

    def test_nominal(self):
        # given
        extract = users_factories.GdprUserDataExtractBeneficiaryFactory(dateProcessed=datetime.datetime.utcnow())
        with open(self.storage_folder / f"{extract.id}.zip", "wb") as fp:
            fp.write(b"[personal data compressed with deflate]")
        # when
        users_api.delete_gdpr_extract(extract.id)

        # then
        assert db.session.query(users_models.GdprUserDataExtract).count() == 0
        assert len(os.listdir(self.storage_folder)) == 0

    def test_extract_file_does_not_exists(self):
        # given
        extract = users_factories.GdprUserDataExtractBeneficiaryFactory(dateProcessed=datetime.datetime.utcnow())
        # when
        users_api.delete_gdpr_extract(extract.id)

        # then
        assert db.session.query(users_models.GdprUserDataExtract).count() == 0


class CleanGdprExtractTest(StorageFolderManager):
    storage_folder = settings.LOCAL_STORAGE_DIR / settings.GCP_GDPR_EXTRACT_BUCKET / settings.GCP_GDPR_EXTRACT_FOLDER

    def test_delete_expired_extracts(self):
        # given
        extract = users_factories.GdprUserDataExtractBeneficiaryFactory(
            dateProcessed=datetime.datetime.utcnow() - datetime.timedelta(days=6),
            dateCreated=datetime.datetime.utcnow() - datetime.timedelta(days=8),
        )
        with open(self.storage_folder / f"{extract.id}.zip", "wb") as fp:
            fp.write(b"[personal data compressed with deflate]")
        # when
        users_api.clean_gdpr_extracts()
        # then
        assert db.session.query(users_models.GdprUserDataExtract).count() == 0
        assert len(os.listdir(self.storage_folder)) == 0

    def test_delete_extracts_files_not_in_db(self):
        # given
        with open(self.storage_folder / "1.zip", "wb") as fp:
            fp.write(b"[personal data compressed with deflate]")
        # when
        users_api.clean_gdpr_extracts()
        # then
        assert len(os.listdir(self.storage_folder)) == 0

    def test_delete_expired_unprocessed_extracts(self):
        # given
        users_factories.GdprUserDataExtractBeneficiaryFactory(
            dateCreated=datetime.datetime.utcnow() - datetime.timedelta(days=8)
        )
        # when
        users_api.clean_gdpr_extracts()
        # then
        assert db.session.query(users_models.GdprUserDataExtract).count() == 0

    def test_keep_unexpired_extracts(self):
        # given
        extract = users_factories.GdprUserDataExtractBeneficiaryFactory(
            dateProcessed=datetime.datetime.utcnow() - datetime.timedelta(days=5),
            dateCreated=datetime.datetime.utcnow() - datetime.timedelta(days=6),
        )
        with open(self.storage_folder / f"{extract.id}.zip", "wb") as fp:
            fp.write(b"[personal data compressed with deflate]")
        # when
        users_api.clean_gdpr_extracts()
        # then
        assert db.session.query(users_models.GdprUserDataExtract).count() == 1
        assert len(os.listdir(self.storage_folder)) == 1


def generate_beneficiary():
    now = datetime.datetime(2024, 1, 1)
    user = users_factories.UserFactory(
        activity="Lycéen",
        address="123 rue du pass",
        civility="M.",
        city="Paris",
        culturalSurveyFilledDate=now,
        departementCode="75",
        dateCreated=now,
        dateOfBirth=datetime.datetime(2010, 1, 1),
        email="valid_email@example.com",
        firstName="Beneficiary",
        isActive=True,
        isEmailValidated=True,
        lastName="bénéficiaire",
        married_name="married_name",
        postalCode="75000",
        schoolType=users_models.SchoolTypeEnum.PUBLIC_SECONDARY_SCHOOL,
        validatedBirthDate=datetime.date(2010, 1, 1),
        notificationSubscriptions={
            "marketing_email": True,
            "marketing_push": False,
        },
        roles=[users_models.UserRole.BENEFICIARY],
    )
    users_factories.LoginDeviceHistoryFactory(
        dateCreated=now - datetime.timedelta(days=2),
        deviceId="anotsorandomdeviceid2",
        location="Lyon",
        source="phone1",
        os="oldOs",
        user=user,
    )
    users_factories.LoginDeviceHistoryFactory(
        dateCreated=now,
        deviceId="anotsorandomdeviceid",
        location="Paris",
        source="phone 2",
        os="os/2",
        user=user,
    )
    users_factories.EmailConfirmationEntryFactory(
        creationDate=now - datetime.timedelta(days=2),
        newUserEmail="intermediary",
        newDomainEmail="example.com",
        oldUserEmail="old",
        oldDomainEmail="example.com",
        user=user,
    )
    users_factories.EmailAdminUpdateEntryFactory(
        creationDate=now,
        newUserEmail="beneficiary",
        newDomainEmail="example.com",
        oldUserEmail="intermediary",
        oldDomainEmail="example.com",
        user=user,
    )
    history_factories.ActionHistoryFactory(
        actionDate=now - datetime.timedelta(days=2),
        actionType=history_models.ActionType.USER_SUSPENDED,
        user=user,
    )
    history_factories.ActionHistoryFactory(
        actionDate=now,
        actionType=history_models.ActionType.USER_UNSUSPENDED,
        user=user,
    )
    fraud_factories.BeneficiaryFraudCheckFactory(
        dateCreated=now,
        eligibilityType=users_models.EligibilityType.AGE18,
        status=fraud_models.FraudCheckStatus.OK,
        type=fraud_models.FraudCheckType.DMS,
        updatedAt=now + datetime.timedelta(days=1),
        user=user,
    )
    users_factories.DepositGrantFactory(
        user=user,
        dateCreated=now - datetime.timedelta(days=2),
        dateUpdated=now + datetime.timedelta(days=1),
        expirationDate=now + datetime.timedelta(days=15000),
        amount=Decimal("300.0"),
        source="source",
        type=finance_models.DepositType.GRANT_18,
    )
    bookings_factories.BookingFactory(
        user=user,
        dateCreated=now,
        dateUsed=now,
        quantity=1,
        amount=Decimal("10.00"),
        status=bookings_models.BookingStatus.CONFIRMED,
        stock__offer__name="offer_name",
        stock__offer__venue__name="venue_name",
        stock__offer__venue__managingOfferer__name="offerer_name",
    )
    bookings_factories.BookingFactory(
        user=user,
        cancellationDate=now,
        dateCreated=now,
        quantity=1,
        amount=Decimal("50.00"),
        status=bookings_models.BookingStatus.CANCELLED,
        stock__offer__name="offer2_name",
        stock__offer__venue__name="venue2_name",
        stock__offer__venue__managingOfferer__name="offerer2_name",
    )
    product = offers_factories.ProductFactory(
        name="my super book",
        ean="1234567890123",
    )
    chronicles_factories.ChronicleFactory(
        user=user,
        products=[product],
        age=17,
        city="Trantor",
        dateCreated=now,
        productIdentifier="1234567890123",
        email="useremail@example.com",
        firstName="Hari",
        isIdentityDiffusible=True,
        isSocialMediaDiffusible=True,
    )
    users_factories.UserAccountUpdateRequestFactory(
        dateCreated=datetime.datetime(2024, 1, 1),
        dateLastStatusUpdate=datetime.datetime(2024, 1, 2),
        user=user,
        firstName=user.firstName,
        lastName=user.lastName,
        email=user.email,
        birthDate=user.birth_date,
        oldEmail="ancien" + user.email,
        newEmail="nouveau" + user.email,
        newFirstName="Nouveau" + user.firstName,
        newLastName="Nouveau" + user.lastName,
        newPhoneNumber="+33000000000",
        allConditionsChecked=True,
        dateLastUserMessage=datetime.datetime(2024, 1, 10),
        dateLastInstructorMessage=datetime.datetime(2024, 1, 20),
        updateTypes=[
            users_models.UserAccountUpdateType.FIRST_NAME,
            users_models.UserAccountUpdateType.LAST_NAME,
            users_models.UserAccountUpdateType.EMAIL,
            users_models.UserAccountUpdateType.PHONE_NUMBER,
        ],
    )
    users_factories.UserAccountUpdateRequestFactory(
        dateCreated=datetime.datetime(2024, 3, 1),
        dateLastStatusUpdate=datetime.datetime(2024, 3, 2),
        user=user,
        firstName=user.firstName,
        lastName=user.lastName,
        email=user.email,
        birthDate=user.birth_date,
        oldEmail="ancien" + user.email,
        newEmail="verynouveau" + user.email,
        newFirstName="Very-Nouveau" + user.firstName,
        newLastName="Very-Nouveau" + user.lastName,
        newPhoneNumber="+33000000001",
        allConditionsChecked=True,
        dateLastUserMessage=datetime.datetime(2024, 3, 10),
        dateLastInstructorMessage=datetime.datetime(2024, 3, 20),
        updateTypes=[
            users_models.UserAccountUpdateType.FIRST_NAME,
            users_models.UserAccountUpdateType.LAST_NAME,
            users_models.UserAccountUpdateType.EMAIL,
            users_models.UserAccountUpdateType.PHONE_NUMBER,
        ],
    )
    return user


def generate_minimal_beneficiary():
    # generate a user with all objects where all optional fields to None
    now = datetime.datetime(2024, 1, 1)
    user = users_models.User(
        dateCreated=now,
        email="empty@example.com",
        hasSeenProTutorials=False,
        hasSeenProRgs=False,
        needsToFillCulturalSurvey=False,
        notificationSubscriptions=None,
        roles=[users_models.UserRole.BENEFICIARY],
    )
    db.session.add(user)
    db.session.flush()
    db.session.add(
        users_models.LoginDeviceHistory(
            user=user,
            deviceId="a device id",
            dateCreated=now,
        )
    )
    db.session.add(
        users_models.UserEmailHistory(
            user=user,
            oldUserEmail="oldUserEmail",
            oldDomainEmail="example.com",
            creationDate=now,
            eventType=users_models.EmailHistoryEventTypeEnum.ADMIN_UPDATE,
        )
    )
    action_history = history_models.ActionHistory(
        user=user,
        actionType=history_models.ActionType.USER_SUSPENDED,
    )
    db.session.add(action_history)
    db.session.flush()
    db.session.query(history_models.ActionHistory).filter(history_models.ActionHistory.id == action_history.id).update(
        {"actionDate": None},
    )
    db.session.add(
        fraud_models.BeneficiaryFraudCheck(
            user=user,
            dateCreated=now,
            thirdPartyId="third_party_id",
            type=fraud_models.FraudCheckType.DMS,
            updatedAt=now,
        )
    )
    deposit = finance_models.Deposit(
        user=user,
        amount=Decimal("300.00"),
        source="démarches simplifiées dossier [1234567]",
        dateCreated=now,
        version=1,
        type=finance_models.DepositType.GRANT_18,
    )
    db.session.add(deposit)
    stock = offers_factories.StockFactory(
        offer__name="offer_name",
        offer__venue__name="venue_name",
        offer__venue__managingOfferer__name="offerer_name",
    )
    db.session.add(
        bookings_models.Booking(
            user=user,
            dateCreated=now,
            stock=stock,
            venue=stock.offer.venue,
            offerer=stock.offer.venue.managingOfferer,
            quantity=1,
            token="token",
            amount=Decimal("13.34"),
            status=bookings_models.BookingStatus.CANCELLED,
            cancellationDate=now,
            deposit=deposit,
        )
    )
    db.session.add(
        chronicles_models.Chronicle(
            user=user,
            dateCreated=now,
            content="",
            email="",
            externalId="",
            productIdentifier="1234567899999",
            productIdentifierType=chronicles_models.ChronicleProductIdentifierType.EAN,
            clubType=chronicles_models.ChronicleClubType.BOOK_CLUB,
        )
    )
    db.session.add(
        users_models.UserAccountUpdateRequest(
            dsApplicationId="111111",
            dsTechnicalId="abc-def-ghi-jkl",
            status=dms_models.GraphQLApplicationStates.on_going,
            dateCreated=now,
            dateLastStatusUpdate=now,
            email="empty@example.com",
            user=user,
            allConditionsChecked=False,
            updateTypes=[],
        )
    )
    db.session.flush()
    db.session.refresh(user)
    return user


class ExtractBeneficiaryDataTest(StorageFolderManager):
    TEST_FILES_PATH = pathlib.Path(tests.__path__[0]) / "files"
    storage_folder = settings.LOCAL_STORAGE_DIR / settings.GCP_GDPR_EXTRACT_BUCKET / settings.GCP_GDPR_EXTRACT_FOLDER
    # 1 select gdpr_user_data_extract
    # 2 update gdpr user data
    # 3 refresh extract_gdpr_user_data
    # 4 select user
    # 5 select login device history
    # 6 select user_email_history
    # 7 select action_history
    # 8 select beneficiary_fraud_check
    # 9 select deposit
    # 10 select bookings
    # 11 select chronicles
    # 12 select user_account_update_request
    # 13 select user (authorUser)
    # 14 insert action history
    expected_queries = 14
    # 1 json
    # 2 pdf
    output_files_count = 2

    @mock.patch("pcapi.core.users.api.generate_pdf_from_html", return_value=b"content of a pdf")
    def test_json_output(self, pdf_generator_mock) -> None:
        user = generate_beneficiary()
        extract = users_factories.GdprUserDataExtractBeneficiaryFactory(
            user=user,
        )
        with assert_num_queries(self.expected_queries):
            users_api.extract_beneficiary_data(extract=extract)

        file_path = self.storage_folder / f"{extract.id}.zip"

        json_file_name = f"{user.email}.json"
        with zipfile.ZipFile(file_path, mode="r") as zip_pointer:
            files = zip_pointer.namelist()
            assert len(files) == self.output_files_count
            assert json_file_name in files
            with zip_pointer.open(json_file_name) as json_pointer:
                raw_data = json_pointer.read()
                json_data = raw_data.decode("utf-8")
                result = json.loads(json_data)

        assert "generationDate" in result
        del result["generationDate"]
        assert result == {
            "external": {
                "brevo": {
                    "attributes": {
                        "ADDRESS": "987 5th avenue",
                        "AREA": "NY",
                        "CITY": "New-York",
                        "CIV": "1",
                        "DOB": "1986-04-13",
                        "FIRST_NAME": "valid",
                        "LAST_NAME": "email",
                        "SMS": "3087433387669",
                        "ZIP_CODE": "87544",
                    },
                    "createdAt": "2017-05-02T16:40:31Z",
                    "email": "valid_email@example.com",
                    "emailBlacklisted": False,
                    "id": 42,
                    "listIds": [40],
                    "modifiedAt": "2017-05-02T16:40:31Z",
                    "smsBlacklisted": False,
                    "statistics": {
                        "clicked": [
                            {
                                "campaignId": 21,
                                "links": [
                                    {
                                        "count": 2,
                                        "eventTime": "2016-05-03T21:25:01Z",
                                        "ip": "66.249.93.118",
                                        "url": "https://url.domain.com/fbe5387ec717e333628380454f68670010b205ff/1/go?uid={EMAIL}&utm_source=brevo&utm_campaign=test_camp&utm_medium=email",
                                    }
                                ],
                            }
                        ],
                        "delivered": [
                            {"campaignId": 21, "count": 2, "eventTime": "2016-05-03T21:24:56Z", "ip": "66.249.93.118"}
                        ],
                        "messagesSent": [
                            {"campaignId": 21, "eventTime": "2016-05-03T20:15:13Z"},
                            {"campaignId": 42, "eventTime": "2016-10-17T10:30:01Z"},
                        ],
                        "opened": [
                            {"campaignId": 21, "count": 2, "eventTime": "2016-05-03T21:24:56Z", "ip": "66.249.93.118"},
                            {"campaignId": 68, "count": 1, "eventTime": "2017-01-30T13:56:40Z", "ip": "66.249.93.217"},
                        ],
                    },
                }
            },
            "internal": {
                "accountUpdateRequests": [
                    {
                        "allConditionsChecked": True,
                        "birthDate": "2010-01-01",
                        "dateCreated": "2024-01-01T00:00:00",
                        "dateLastInstructorMessage": "2024-01-20T00:00:00",
                        "dateLastStatusUpdate": "2024-01-02T00:00:00",
                        "dateLastUserMessage": "2024-01-10T00:00:00",
                        "email": "valid_email@example.com",
                        "firstName": "Beneficiary",
                        "lastName": "bénéficiaire",
                        "newEmail": "nouveauvalid_email@example.com",
                        "newFirstName": "NouveauBeneficiary",
                        "newLastName": "Nouveaubénéficiaire",
                        "newPhoneNumber": "+33000000000",
                        "oldEmail": "ancienvalid_email@example.com",
                        "status": "en_instruction",
                        "updateTypes": [
                            "Prénom",
                            "Nom",
                            "Email",
                            "Numéro de téléphone",
                        ],
                    },
                    {
                        "allConditionsChecked": True,
                        "birthDate": "2010-01-01",
                        "dateCreated": "2024-03-01T00:00:00",
                        "dateLastInstructorMessage": "2024-03-20T00:00:00",
                        "dateLastStatusUpdate": "2024-03-02T00:00:00",
                        "dateLastUserMessage": "2024-03-10T00:00:00",
                        "email": "valid_email@example.com",
                        "firstName": "Beneficiary",
                        "lastName": "bénéficiaire",
                        "newEmail": "verynouveauvalid_email@example.com",
                        "newFirstName": "Very-NouveauBeneficiary",
                        "newLastName": "Very-Nouveaubénéficiaire",
                        "newPhoneNumber": "+33000000001",
                        "oldEmail": "ancienvalid_email@example.com",
                        "status": "en_instruction",
                        "updateTypes": [
                            "Prénom",
                            "Nom",
                            "Email",
                            "Numéro de téléphone",
                        ],
                    },
                ],
                "actionsHistory": [
                    {"actionDate": "2023-12-30T00:00:00", "actionType": "USER_SUSPENDED"},
                    {"actionDate": "2024-01-01T00:00:00", "actionType": "USER_UNSUSPENDED"},
                ],
                "beneficiaryValidations": [
                    {
                        "dateCreated": "2024-01-01T00:00:00",
                        "eligibilityType": "Pass 18",
                        "status": "Succès",
                        "type": "Démarches simplifiées",
                        "updatedAt": "2024-01-02T00:00:00",
                    }
                ],
                "bookings": [
                    {
                        "amount": 10.0,
                        "cancellationDate": None,
                        "dateCreated": "2024-01-01T00:00:00",
                        "dateUsed": "2024-01-01T00:00:00",
                        "name": "offer_name",
                        "offerer": "offerer_name",
                        "quantity": 1,
                        "status": "Réservé",
                        "venue": "venue_name",
                    },
                    {
                        "amount": 50.0,
                        "cancellationDate": "2024-01-01T00:00:00",
                        "dateCreated": "2024-01-01T00:00:00",
                        "dateUsed": None,
                        "name": "offer2_name",
                        "offerer": "offerer2_name",
                        "quantity": 1,
                        "status": "Annulé",
                        "venue": "venue2_name",
                    },
                ],
                "chronicles": [
                    {
                        "age": 17,
                        "allocineId": None,
                        "city": "Trantor",
                        "content": "A small chronicle content.",
                        "dateCreated": "2024-01-01T00:00:00",
                        "ean": "1234567890123",
                        "email": "useremail@example.com",
                        "firstName": "Hari",
                        "isIdentityDiffusible": True,
                        "isSocialMediaDiffusible": True,
                        "productIdentifier": "1234567890123",
                        "productIdentifierType": "EAN",
                        "productName": "my super book",
                        "visa": None,
                    },
                ],
                "deposits": [
                    {
                        "amount": 300.0,
                        "dateCreated": "2023-12-30T00:00:00",
                        "dateUpdated": "2024-01-02T00:00:00",
                        "expirationDate": "2065-01-25T00:00:00",
                        "source": "source",
                        "type": "Pass 18",
                    }
                ],
                "emailsHistory": [
                    {
                        "dateCreated": "2023-12-30T00:00:00",
                        "newEmail": "intermediary@example.com",
                        "oldEmail": "old@example.com",
                    },
                    {
                        "dateCreated": "2024-01-01T00:00:00",
                        "newEmail": "beneficiary@example.com",
                        "oldEmail": "intermediary@example.com",
                    },
                ],
                "loginDevices": [
                    {
                        "dateCreated": "2023-12-30T00:00:00",
                        "deviceId": "anotsorandomdeviceid2",
                        "location": "Lyon",
                        "os": "oldOs",
                        "source": "phone1",
                    },
                    {
                        "dateCreated": "2024-01-01T00:00:00",
                        "deviceId": "anotsorandomdeviceid",
                        "location": "Paris",
                        "os": "os/2",
                        "source": "phone 2",
                    },
                ],
                "marketing": {"marketingEmails": True, "marketingNotifications": False},
                "user": {
                    "activity": "Lycéen",
                    "address": "123 rue du pass",
                    "city": "Paris",
                    "civility": "M.",
                    "culturalSurveyFilledDate": "2024-01-01T00:00:00",
                    "dateCreated": "2024-01-01T00:00:00",
                    "dateOfBirth": "2010-01-01T00:00:00",
                    "departementCode": "75",
                    "email": "valid_email@example.com",
                    "firstName": "Beneficiary",
                    "isActive": True,
                    "isEmailValidated": True,
                    "lastName": "bénéficiaire",
                    "marriedName": "married_name",
                    "postalCode": "75000",
                    "schoolType": "Collège public",
                    "validatedBirthDate": "2010-01-01",
                },
            },
        }

    @mock.patch("pcapi.core.users.api.generate_pdf_from_html", return_value=b"content of a pdf")
    def test_pdf_html(self, pdf_generator_mock) -> None:
        user = generate_beneficiary()
        extract = users_factories.GdprUserDataExtractBeneficiaryFactory(
            user=user,
        )
        with assert_num_queries(self.expected_queries):
            users_api.extract_beneficiary_data(extract=extract)

        file_path = self.storage_folder / f"{extract.id}.zip"

        pdf_file_name = f"{user.email}.pdf"
        with zipfile.ZipFile(file_path, mode="r") as zip_pointer:
            files = zip_pointer.namelist()
            assert len(files) == self.output_files_count
            assert pdf_file_name in files
            with zip_pointer.open(pdf_file_name) as pdf_pointer:
                assert pdf_pointer.read() == b"content of a pdf"

        with open(self.TEST_FILES_PATH / "gdpr" / "rendered_beneficiary_extract.html", "r", encoding="utf-8") as f:
            pdf_generator_mock.assert_called_once_with(html_content=f.read())

    def test_pdf_generated(self, css_font_http_request_mock):
        user = generate_beneficiary()
        extract = users_factories.GdprUserDataExtractBeneficiaryFactory(
            user=user,
        )

        users_api.extract_beneficiary_data(extract)

        file_path = self.storage_folder / f"{extract.id}.zip"
        pdf_file_name = f"{user.email}.pdf"
        with zipfile.ZipFile(file_path, mode="r") as zip_pointer:
            files = zip_pointer.namelist()
            assert len(files) == self.output_files_count
            assert pdf_file_name in files
            with zip_pointer.open(pdf_file_name) as pdf_pointer:
                assert pdf_pointer.read()

    @mock.patch("pcapi.core.users.api.generate_pdf_from_html", return_value=b"content of a pdf")
    def test_pdf_with_empty_user(self, pdf_generator_mock=None) -> None:
        user = users_models.User(
            firstName="firstname",
            lastName="lastName",
            email="firstname.lastname@example.com",
            dateCreated=datetime.datetime(2024, 6, 26, 13, 14, 28),
        )
        extract = users_factories.GdprUserDataExtractBeneficiaryFactory(
            user=user,
        )
        with assert_num_queries(self.expected_queries):
            users_api.extract_beneficiary_data(extract=extract)

        file_path = self.storage_folder / f"{extract.id}.zip"

        pdf_file_name = f"{user.email}.pdf"
        with zipfile.ZipFile(file_path, mode="r") as zip_pointer:
            files = zip_pointer.namelist()
            assert len(files) == self.output_files_count
            assert pdf_file_name in files
            with zip_pointer.open(pdf_file_name) as pdf_pointer:
                assert pdf_pointer.read() == b"content of a pdf"

        with open(
            self.TEST_FILES_PATH / "gdpr" / "rendered_empty_beneficiary_extract.html", "r", encoding="utf-8"
        ) as f:
            pdf_generator_mock.assert_called_once_with(html_content=f.read())

    @mock.patch("pcapi.core.users.api.generate_pdf_from_html", return_value=b"content of a pdf")
    def test_pdf_with_minimal_non_empty_user(self, pdf_generator_mock):
        user = generate_minimal_beneficiary()
        extract = users_factories.GdprUserDataExtractBeneficiaryFactory(
            user=user,
        )
        with assert_num_queries(self.expected_queries):
            users_api.extract_beneficiary_data(extract=extract)

        file_path = self.storage_folder / f"{extract.id}.zip"

        pdf_file_name = f"{user.email}.pdf"
        with zipfile.ZipFile(file_path, mode="r") as zip_pointer:
            files = zip_pointer.namelist()
            assert len(files) == self.output_files_count
            assert pdf_file_name in files
            with zip_pointer.open(pdf_file_name) as pdf_pointer:
                assert pdf_pointer.read() == b"content of a pdf"

        with open(
            self.TEST_FILES_PATH / "gdpr" / "rendered_minimal_beneficiary_extract.html", "r", encoding="utf-8"
        ) as f:
            pdf_generator_mock.assert_called_once_with(html_content=f.read())


class ExtractBeneficiaryDataCommandTest(StorageFolderManager):
    # 1 extract gdpr_user_data + user
    # 2 update gdpr user data
    # 3 login device history
    # 4 user_email_history
    # 5 action_history
    # 6 beneficiary_fraud_check
    # 7 deposit
    # 8 bookings
    # 9 chronicles
    # 10 user_account_update_requests
    # 11 generate action history
    expected_queries = 11
    storage_folder = settings.LOCAL_STORAGE_DIR / settings.GCP_GDPR_EXTRACT_BUCKET / settings.GCP_GDPR_EXTRACT_FOLDER

    @mock.patch("pcapi.core.users.api.generate_pdf_from_html", return_value=b"content of a pdf")
    def test_nominal(self, generate_pdf_mock, clear_redis):
        redis = current_app.redis_client
        redis.set(users_constants.GDPR_EXTRACT_DATA_COUNTER, "3")
        extract = users_factories.GdprUserDataExtractBeneficiaryFactory()
        with time_machine.travel("2023-12-15 10:11:00"):
            with assert_num_queries(self.expected_queries):
                result = users_api.extract_beneficiary_data_command()

        db.session.refresh(extract)
        assert result == True
        assert not redis.exists(users_constants.GDPR_EXTRACT_DATA_LOCK)
        assert redis.get(users_constants.GDPR_EXTRACT_DATA_COUNTER) == "4"
        assert (self.storage_folder / f"{extract.id}.zip").exists()
        assert extract.dateProcessed is not None

    def test_not_processing_expired_extract(self, clear_redis):
        redis = current_app.redis_client
        extract = users_factories.GdprUserDataExtractBeneficiaryFactory(
            dateCreated=datetime.datetime(2023, 12, 5),
        )
        redis.set(users_constants.GDPR_EXTRACT_DATA_COUNTER, "3")
        with time_machine.travel("2023-12-15 10:11:00"):
            with assert_num_queries(1):
                result = users_api.extract_beneficiary_data_command()

        db.session.refresh(extract)
        assert result == False
        assert not redis.exists(users_constants.GDPR_EXTRACT_DATA_LOCK)
        assert redis.get(users_constants.GDPR_EXTRACT_DATA_COUNTER) == "3"
        assert not (self.storage_folder / f"{extract.id}.zip").exists()
        assert extract.dateProcessed is None

    def test_nothing_to_process(self, clear_redis):
        redis = current_app.redis_client
        redis.set(users_constants.GDPR_EXTRACT_DATA_COUNTER, "3")
        with time_machine.travel("2023-12-15 10:11:00"):
            with assert_num_queries(1):
                result = users_api.extract_beneficiary_data_command()

        assert result == False
        assert not redis.exists(users_constants.GDPR_EXTRACT_DATA_LOCK)
        assert redis.get(users_constants.GDPR_EXTRACT_DATA_COUNTER) == "3"

    def test_lock_already_taken(self, clear_redis):
        redis = current_app.redis_client
        redis.set(users_constants.GDPR_EXTRACT_DATA_LOCK, "locked", ex=123)
        redis.set(users_constants.GDPR_EXTRACT_DATA_COUNTER, "3")
        extract = users_factories.GdprUserDataExtractBeneficiaryFactory()
        with time_machine.travel("2023-12-15 10:11:00"):
            with assert_num_queries(0):
                result = users_api.extract_beneficiary_data_command()

        db.session.refresh(extract)
        assert result == False
        assert redis.get(users_constants.GDPR_EXTRACT_DATA_LOCK) == "locked"
        assert 0 < redis.ttl(users_constants.GDPR_EXTRACT_DATA_LOCK) <= 123
        assert redis.get(users_constants.GDPR_EXTRACT_DATA_COUNTER) == "3"
        assert not (self.storage_folder / f"{extract.id}.zip").exists()
        assert extract.dateProcessed is None

    def test_counter_overflow(self, clear_redis):
        redis = current_app.redis_client
        redis.set(users_constants.GDPR_EXTRACT_DATA_COUNTER, settings.GDPR_MAX_EXTRACT_PER_DAY)
        extract = users_factories.GdprUserDataExtractBeneficiaryFactory()
        with time_machine.travel("2023-12-15 10:11:00"):
            with assert_num_queries(0):
                result = users_api.extract_beneficiary_data_command()

        db.session.refresh(extract)
        assert result == False
        assert not redis.exists(users_constants.GDPR_EXTRACT_DATA_LOCK)
        assert redis.get(users_constants.GDPR_EXTRACT_DATA_COUNTER) == str(settings.GDPR_MAX_EXTRACT_PER_DAY)
        assert not (self.storage_folder / f"{extract.id}.zip").exists()
        assert extract.dateProcessed is None

    @mock.patch("pcapi.core.users.api.generate_pdf_from_html", return_value=b"content of a pdf")
    def test_reset_counter_at_midnight(self, generate_pdf_mock, clear_redis):
        redis = current_app.redis_client
        extract = users_factories.GdprUserDataExtractBeneficiaryFactory()
        redis.set(users_constants.GDPR_EXTRACT_DATA_COUNTER, settings.GDPR_MAX_EXTRACT_PER_DAY)

        with time_machine.travel("2023-12-15 00:01:00"):
            with assert_num_queries(self.expected_queries):
                result = users_api.extract_beneficiary_data_command()

        db.session.refresh(extract)
        assert result == True
        assert not redis.exists(users_constants.GDPR_EXTRACT_DATA_LOCK)
        assert redis.get(users_constants.GDPR_EXTRACT_DATA_COUNTER) == "1"
        assert (self.storage_folder / f"{extract.id}.zip").exists()
        assert extract.dateProcessed is not None

    @mock.patch("pcapi.core.users.api.generate_pdf_from_html", side_effect=Exception)
    def test_extract_failed(self, clear_redis):
        redis = current_app.redis_client
        redis.set(users_constants.GDPR_EXTRACT_DATA_COUNTER, "3")
        users_factories.GdprUserDataExtractBeneficiaryFactory()

        with time_machine.travel("2023-12-15 10:11:00"):
            # crashes before writing the log history
            with assert_num_queries(self.expected_queries - 1):
                with pytest.raises(Exception):
                    users_api.extract_beneficiary_data_command()

        assert not redis.exists(users_constants.GDPR_EXTRACT_DATA_LOCK)
        assert redis.get(users_constants.GDPR_EXTRACT_DATA_COUNTER) == "3"


class BypassEmailConfirmationTest:
    @pytest.mark.settings(ENABLE_EMAIL_CONFIRMATION_BYPASS=False)
    def test_send_confirmation_email_if_env_var_is_disabled(self):
        mails_testing.outbox = []

        user = users_api.create_account(
            email="email+e2e@quinousinteresse.fr",
            password="random123",
            birthdate=datetime.date.today() - relativedelta(years=18),
            is_email_validated=False,
        )

        assert len(mails_testing.outbox) == 1
        assert not user.isEmailValidated

    @pytest.mark.settings(ENABLE_EMAIL_CONFIRMATION_BYPASS=True)
    def test_dont_send_confirmation_email_when_e2e_test(self):
        mails_testing.outbox = []

        user = users_api.create_account(
            email="email+e2e@quinousinteresse.fr",
            password="random123",
            birthdate=datetime.date.today() - relativedelta(years=18),
            is_email_validated=False,
        )
        db.session.flush()  # helps teardown session

        assert len(mails_testing.outbox) == 0
        assert user.isEmailValidated

    @pytest.mark.settings(ENABLE_EMAIL_CONFIRMATION_BYPASS=True)
    def test_send_confirmation_with_normal_email(self):
        mails_testing.outbox = []

        user = users_api.create_account(
            email="e2e@quinousinteresse.fr",
            password="random123",
            birthdate=datetime.date.today() - relativedelta(years=18),
            is_email_validated=False,
        )

        assert len(mails_testing.outbox) == 1
        assert not user.isEmailValidated

    @pytest.mark.settings(ENABLE_EMAIL_CONFIRMATION_BYPASS=True)
    def test_dont_confirm_e2e_test_email_when_email_sending_is_not_required(self):
        mails_testing.outbox = []

        user = users_api.create_account(
            email="email+e2e@quinousinteresse.fr",
            password="random123",
            birthdate=datetime.date.today() - relativedelta(years=18),
            is_email_validated=False,
            send_activation_mail=False,
        )

        assert len(mails_testing.outbox) == 0
        assert not user.isEmailValidated

    @pytest.mark.parametrize(
        "age,expected_event_name",
        [
            (15, "af_complete_registration_15"),
            (16, "af_complete_registration_16"),
            (17, "af_complete_registration_17"),
            (18, "af_complete_registration_18"),
            (19, "af_complete_registration_19+"),
            (25, "af_complete_registration_19+"),
        ],
    )
    def test_apps_flyer_called_when_validating_email(self, requests_mock, client, age, expected_event_name):
        apps_flyer_data = {
            "apps_flyer": {"user": "some-user-id", "platform": "ANDROID"},
            "firebase_pseudo_id": "firebase_pseudo_id",
        }
        user = users_factories.UserFactory(
            email="user@example.com",
            isEmailValidated=False,
            externalIds=apps_flyer_data,
            dateOfBirth=datetime.date.today() - relativedelta(years=age),
        )
        token = token_utils.Token.create(
            type_=token_utils.TokenType.SIGNUP_EMAIL_CONFIRMATION,
            ttl=users_constants.EMAIL_VALIDATION_TOKEN_LIFE_TIME,
            user_id=user.id,
        )
        posted = requests_mock.post("https://api2.appsflyer.com/inappevent/app.passculture.webapp")

        response = client.post("/native/v1/validate_email", json={"email_validation_token": token.encoded_token})

        assert response.status_code == 200
        assert posted.call_count == 1
        assert posted.request_history[0].json() == {
            "appsflyer_id": "some-user-id",
            "eventName": expected_event_name,
            "eventValue": {
                "af_user_id": str(user.id),
                "af_firebase_pseudo_id": "firebase_pseudo_id",
                "type": None,
            },
        }
        assert user.isEmailValidated
