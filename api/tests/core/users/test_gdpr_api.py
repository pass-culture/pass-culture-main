import dataclasses
import datetime
import json
import os
import pathlib
import zipfile
from decimal import Decimal
from unittest import mock

import pytest
import time_machine
from dateutil.relativedelta import relativedelta
from flask import current_app

import pcapi.core.mails.testing as mails_testing
import pcapi.core.offerers.models as offerers_models
import pcapi.core.subscription.factories as subscription_factories
import pcapi.core.subscription.models as subscription_models
from pcapi import settings
from pcapi.connectors.beamer import BeamerException
from pcapi.connectors.dms import models as dms_models
from pcapi.core import token as token_utils
from pcapi.core.bookings import factories as bookings_factories
from pcapi.core.bookings import models as bookings_models
from pcapi.core.chronicles import factories as chronicles_factories
from pcapi.core.chronicles import models as chronicles_models
from pcapi.core.educational import factories as educational_factories
from pcapi.core.educational import models as educational_models
from pcapi.core.finance import factories as finance_factories
from pcapi.core.finance import models as finance_models
from pcapi.core.geography import api as geography_api
from pcapi.core.geography import models as geography_models
from pcapi.core.history import factories as history_factories
from pcapi.core.history import models as history_models
from pcapi.core.mails.transactional.sendinblue_template_ids import TransactionalEmail
from pcapi.core.offerers import factories as offerers_factories
from pcapi.core.offers import factories as offers_factories
from pcapi.core.offers import models as offers_models
from pcapi.core.testing import assert_num_queries
from pcapi.core.users import api as users_api
from pcapi.core.users import constants as users_constants
from pcapi.core.users import factories as users_factories
from pcapi.core.users import gdpr_api
from pcapi.core.users import models as users_models
from pcapi.core.users import testing as sendinblue_testing
from pcapi.models import db
from pcapi.models.validation_status_mixin import ValidationStatus
from pcapi.notifications.push import testing as batch_testing
from pcapi.utils import date as date_utils

import tests
from tests.test_utils import StorageFolderManager


DATA_DIR = pathlib.Path(tests.__path__[0]) / "files"
pytestmark = pytest.mark.usefixtures("db_session")


class AnonymizeNonProNonBeneficiaryUsersTest:
    def import_iris(self):
        path = DATA_DIR / "iris_min.7z"
        geography_api.import_iris_from_7z(str(path))

    def test_anonymize_non_pro_non_beneficiary_users(self) -> None:
        user_to_anonymize = users_factories.UserFactory(
            firstName="user_to_anonymize",
            lastConnectionDate=date_utils.get_naive_utc_now() - relativedelta(years=3, days=1),
            validatedBirthDate=datetime.date.today(),
        )
        user_too_new = users_factories.UserFactory(
            firstName="user_too_new",
            lastConnectionDate=date_utils.get_naive_utc_now() - relativedelta(years=3, days=-11),
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

        with mock.patch("pcapi.core.users.gdpr_api.get_iris_from_address", return_value=iris):
            gdpr_api.anonymize_non_pro_non_beneficiary_users()

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
        assert user_to_anonymize.externalIds == {}
        assert user_to_anonymize.idPieceNumber is None
        assert user_to_anonymize.login_device_history == []
        assert user_to_anonymize.email_history == []
        assert user_to_anonymize.irisFrance == iris
        assert user_to_anonymize.validatedBirthDate.day == 1
        assert user_to_anonymize.validatedBirthDate.month == 1
        assert user_to_anonymize.roles == [users_models.UserRole.ANONYMIZED]
        assert user_to_anonymize.trusted_devices == []
        assert len(user_to_anonymize.action_history) == 1
        assert user_to_anonymize.action_history[0].actionType == history_models.ActionType.USER_ANONYMIZED
        assert user_to_anonymize.action_history[0].authorUserId is None

    def test_anonymize_non_pro_non_beneficiary_user_force_iris_not_found(self) -> None:
        user_to_anonymize = users_factories.UserFactory(
            firstName="user_to_anonymize",
            lastConnectionDate=date_utils.get_naive_utc_now() - relativedelta(years=3, days=1),
        )

        gdpr_api.anonymize_non_pro_non_beneficiary_users()

        db.session.refresh(user_to_anonymize)

        assert len(sendinblue_testing.sendinblue_requests) == 1
        assert len(batch_testing.requests) == 1
        assert batch_testing.requests[0]["user_id"] == user_to_anonymize.id
        assert user_to_anonymize.firstName is None

    def test_anonymize_non_pro_non_beneficiary_user_keep_history_on_offerer(self) -> None:
        user_to_anonymize = users_factories.UserFactory(
            firstName="user_to_anonymize",
            lastConnectionDate=date_utils.get_naive_utc_now() - relativedelta(years=3, days=1),
        )
        history_factories.ActionHistoryFactory(
            authorUser=user_to_anonymize,
            user=user_to_anonymize,
            offerer=offerers_factories.OffererFactory(),
            actionType=history_models.ActionType.OFFERER_VALIDATED,
        )

        gdpr_api.anonymize_non_pro_non_beneficiary_users()

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
            lastConnectionDate=date_utils.get_naive_utc_now() - relativedelta(years=3, days=1),
        )
        offerers_factories.VenueFactory(bookingEmail=user_to_anonymize.email)

        gdpr_api.anonymize_non_pro_non_beneficiary_users()
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
            lastConnectionDate=date_utils.get_naive_utc_now() - relativedelta(years=3, days=1),
            isActive=False,
        )
        history_factories.SuspendedUserActionHistoryFactory(
            actionDate=date_utils.get_naive_utc_now() - relativedelta(years=3, days=1),
            actionType=history_models.ActionType.USER_SUSPENDED,
            reason=reason,
            user=user_to_anonymize,
        )

        gdpr_api.anonymize_non_pro_non_beneficiary_users()

        db.session.refresh(user_to_anonymize)

        assert len(sendinblue_testing.sendinblue_requests) == 0
        assert user_to_anonymize.firstName == "user_to_anonymize"

    def test_anonymize_non_pro_non_beneficiary_user_suspended_5_years_ago_with_fraud(self) -> None:
        user_to_anonymize = users_factories.UserFactory(
            firstName="user_to_anonymize",
            lastConnectionDate=date_utils.get_naive_utc_now() - relativedelta(years=3, days=1),
            isActive=False,
        )
        history_factories.SuspendedUserActionHistoryFactory(
            actionDate=date_utils.get_naive_utc_now() - relativedelta(years=5, days=1),
            actionType=history_models.ActionType.USER_SUSPENDED,
            reason=users_constants.SuspensionReason.FRAUD_RESELL_PRODUCT,
            user=user_to_anonymize,
        )

        gdpr_api.anonymize_non_pro_non_beneficiary_users()

        db.session.refresh(user_to_anonymize)

        assert len(sendinblue_testing.sendinblue_requests) == 1
        assert user_to_anonymize.firstName != "user_to_anonymize"

    def test_anonymize_non_pro_non_beneficiary_user_recently_suspended_without_fraud(self) -> None:
        user_to_anonymize = users_factories.UserFactory(
            firstName="user_to_anonymize",
            lastConnectionDate=date_utils.get_naive_utc_now() - relativedelta(years=3, days=1),
            isActive=False,
        )
        history_factories.SuspendedUserActionHistoryFactory(
            actionDate=date_utils.get_naive_utc_now() - relativedelta(years=3, days=1),
            actionType=history_models.ActionType.USER_SUSPENDED,
            reason=users_constants.SuspensionReason.DEVICE_AT_RISK,
            user=user_to_anonymize,
        )

        gdpr_api.anonymize_non_pro_non_beneficiary_users()

        db.session.refresh(user_to_anonymize)

        assert len(sendinblue_testing.sendinblue_requests) == 1
        assert user_to_anonymize.firstName != "user_to_anonymize"


class NotifyProUsersBeforeAnonymizationTest:
    # users and joined data
    expected_num_queries = 1

    last_connection_date = date_utils.get_naive_utc_now() - relativedelta(years=3, days=-30)

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
            user__lastConnectionDate=date_utils.get_naive_utc_now() - relativedelta(years=2, months=8),
            validationStatus=user_offerer_validation_status,
        )

        with assert_num_queries(self.expected_num_queries):
            gdpr_api.notify_pro_users_before_anonymization()

        assert len(mails_testing.outbox) == 1
        assert mails_testing.outbox[0]["To"] == "test@example.com"
        assert mails_testing.outbox[0]["template"] == dataclasses.asdict(TransactionalEmail.PRO_PRE_ANONYMIZATION.value)

    def test_notify_non_attached_pro_user(self):
        user_to_notify = users_factories.NonAttachedProFactory(
            lastConnectionDate=self.last_connection_date,
        )
        users_factories.NonAttachedProFactory(lastConnectionDate=date_utils.get_naive_utc_now())

        with assert_num_queries(self.expected_num_queries):
            gdpr_api.notify_pro_users_before_anonymization()

        assert len(mails_testing.outbox) == 1
        assert mails_testing.outbox[0]["To"] == user_to_notify.email
        assert mails_testing.outbox[0]["template"] == dataclasses.asdict(TransactionalEmail.PRO_PRE_ANONYMIZATION.value)

    def test_notify_never_connected_pro(self):
        user_to_notify = users_factories.NonAttachedProFactory(dateCreated=self.last_connection_date)
        users_factories.NonAttachedProFactory()

        with assert_num_queries(self.expected_num_queries):
            gdpr_api.notify_pro_users_before_anonymization()

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
                users_factories.NonAttachedProFactory(lastConnectionDate=date_utils.get_naive_utc_now()),
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
            subscription_factories.BeneficiaryFraudCheckFactory(
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
            gdpr_api.notify_pro_users_before_anonymization()

        for user in users:
            assert user.has_any_pro_role
        assert len(mails_testing.outbox) == 0


def _assert_user_is_anonymized(user, prefix="anonymous"):
    assert user.email == f"{prefix}_{user.id}@anonymized.passculture"
    assert user.password == b"Anonymized"
    assert user.firstName is None
    assert user.lastName is None
    assert user.married_name is None
    assert user.postalCode is None
    assert user.phoneNumber is None
    assert user.address is None
    assert user.city is None
    assert user.externalIds == {}
    assert user.idPieceNumber is None
    assert user.login_device_history == []
    assert user.email_history == []
    assert user.trusted_devices == []
    assert user.roles == [users_models.UserRole.ANONYMIZED]
    assert len(user.action_history) == 1
    assert user.action_history[0].actionType == history_models.ActionType.USER_ANONYMIZED
    assert user.action_history[0].authorUserId is None
    assert user.action_history[0].comment is None
    assert user.backoffice_profile is None


class AnonymizeProUserFunctionTest:
    @pytest.mark.parametrize(
        "user_offerer_factory,expected_status",
        [
            (offerers_factories.UserOffererFactory, ValidationStatus.DELETED),
            (offerers_factories.NewUserOffererFactory, ValidationStatus.REJECTED),
            (offerers_factories.PendingUserOffererFactory, ValidationStatus.REJECTED),
            (offerers_factories.RejectedUserOffererFactory, ValidationStatus.REJECTED),
        ],
    )
    @mock.patch("pcapi.core.users.gdpr_api.delete_beamer_user")
    @mock.patch("pcapi.core.users.gdpr_api.anonymize_user", return_value=True)
    def test_anonymize_pro_user_success(
        self, mock_anonymize_user, mock_delete_beamer_user, user_offerer_factory, expected_status
    ):
        user_offerer = user_offerer_factory()
        user = user_offerer.user

        result = gdpr_api.anonymize_pro_user(user)

        assert result is True
        mock_anonymize_user.assert_called_once_with(user=user, author=None, action_history_comment=None)
        mock_delete_beamer_user.assert_called_once_with(user.id)
        db.session.refresh(user_offerer)
        assert user_offerer.validationStatus == expected_status

    @mock.patch("pcapi.core.users.gdpr_api.delete_beamer_user")
    @mock.patch("pcapi.core.users.gdpr_api.anonymize_user", return_value=False)
    def test_anonymize_pro_user_failure(self, mock_anonymize_user, mock_delete_beamer_user):
        user_offerer = offerers_factories.UserOffererFactory()
        user = user_offerer.user

        result = gdpr_api.anonymize_pro_user(user)

        assert result is False
        mock_anonymize_user.assert_called_once_with(user=user, author=None, action_history_comment=None)
        mock_delete_beamer_user.assert_not_called()
        db.session.refresh(user_offerer)
        assert user_offerer.validationStatus == ValidationStatus.VALIDATED

    @mock.patch("pcapi.core.users.gdpr_api.delete_beamer_user", side_effect=BeamerException())
    @mock.patch("pcapi.core.users.gdpr_api.anonymize_user", return_value=True)
    def test_anonymize_pro_user_beamer_exception(self, mock_anonymize_user, mock_delete_beamer_user, caplog):
        user = users_factories.ProFactory()

        result = gdpr_api.anonymize_pro_user(user)

        assert result is True
        mock_anonymize_user.assert_called_once_with(user=user, author=None, action_history_comment=None)
        mock_delete_beamer_user.assert_called_once_with(user.id)
        assert "Could not delete Beamer user" in caplog.text

    @mock.patch("pcapi.core.users.gdpr_api.delete_beamer_user")
    @mock.patch("pcapi.core.users.gdpr_api.anonymize_user", return_value=True)
    def test_anonymize_pro_user_with_action_history_comment(
        self,
        mock_anonymize_user,
        mock_delete_beamer_user,
    ):
        user_offerer = offerers_factories.UserOffererFactory()
        user = user_offerer.user
        mock_comment = "comment"

        result = gdpr_api.anonymize_pro_user(user=user, action_history_comment=mock_comment)

        assert result is True
        mock_anonymize_user.assert_called_once_with(user=user, author=None, action_history_comment=mock_comment)
        mock_delete_beamer_user.assert_called_once_with(user.id)

    @mock.patch("pcapi.core.users.gdpr_api.delete_beamer_user")
    @mock.patch("pcapi.core.users.gdpr_api.anonymize_user", return_value=True)
    def test_anonymize_pro_user_with_author(
        self,
        mock_anonymize_user,
        mock_delete_beamer_user,
    ):
        user_offerer = offerers_factories.UserOffererFactory()
        user = user_offerer.user
        author = users_factories.ProFactory()

        result = gdpr_api.anonymize_pro_user(user=user, author=author)

        assert result is True
        mock_anonymize_user.assert_called_once_with(user=user, author=author, action_history_comment=None)
        mock_delete_beamer_user.assert_called_once_with(user.id)

    @mock.patch("pcapi.core.users.gdpr_api.delete_beamer_user")
    def test_delete_offerer_invitation_on_anonymize_pro_user(self, mock_delete_beamer_user):
        user_offerer = offerers_factories.UserOffererFactory()
        user = user_offerer.user

        offerers_factories.OffererInvitationFactory(
            email=user.email,
        )
        remaining_invitation = offerers_factories.OffererInvitationFactory(offerer=user_offerer.offerer)

        result = gdpr_api.anonymize_pro_user(user)

        assert result is True
        assert db.session.query(offerers_models.OffererInvitation).all() == [remaining_invitation]


class CanAnonymiseProUserTest:
    @pytest.mark.parametrize(
        "is_only_pro_value,has_suspended_offerer_value,is_sole_user_with_ongoing_activities_value,expected_result",
        [
            (True, False, False, True),  # Eligible
            (False, False, False, False),  # Has non pro account
            (True, True, False, False),  # Has suspended offerer
            (True, False, True, False),  # Has ongoing activities
        ],
    )
    @mock.patch("pcapi.core.users.gdpr_api.is_sole_user_with_ongoing_activities")
    @mock.patch("pcapi.core.users.gdpr_api.has_suspended_offerer")
    @mock.patch("pcapi.core.users.gdpr_api.is_only_pro")
    def test_can_anonymise_pro_user_all_combinations(
        self,
        mock_is_only_pro,
        mock_has_suspended_offerer,
        mock_is_sole_user_with_ongoing_activities,
        is_only_pro_value,
        has_suspended_offerer_value,
        is_sole_user_with_ongoing_activities_value,
        expected_result,
    ):
        user = users_factories.ProFactory()
        mock_is_only_pro.return_value = is_only_pro_value
        mock_has_suspended_offerer.return_value = has_suspended_offerer_value
        mock_is_sole_user_with_ongoing_activities.return_value = is_sole_user_with_ongoing_activities_value

        result = gdpr_api.can_anonymise_pro_user(user)

        assert result is expected_result


class IsOnlyProTest:
    def test_user_with_only_pro_role(self):
        user = users_factories.ProFactory()

        assert gdpr_api.is_only_pro(user) is True

    def test_user_with_non_attached_pro_role(self):
        user = users_factories.NonAttachedProFactory()

        assert gdpr_api.is_only_pro(user) is True

    def test_user_with_pro_and_beneficiary_roles(self):
        user = users_factories.BeneficiaryGrant18Factory(
            roles=[users_models.UserRole.BENEFICIARY, users_models.UserRole.PRO]
        )

        assert gdpr_api.is_only_pro(user) is False

    def test_user_with_pro_role_and_beneficiary_fraud_check(self):
        user = users_factories.ProFactory()
        subscription_factories.BeneficiaryFraudCheckFactory(user=user)

        assert gdpr_api.is_only_pro(user) is False


class HasSuspendedOffererTest:
    def test_user_with_active_offerer(self):
        user_offerer = offerers_factories.UserOffererFactory()

        assert gdpr_api.has_suspended_offerer(user_offerer.user) is False

    def test_user_with_inactive_offerer(self):
        offerer = offerers_factories.OffererFactory(isActive=False)
        user_offerer = offerers_factories.UserOffererFactory(offerer=offerer)

        assert gdpr_api.has_suspended_offerer(user_offerer.user) is True

    def test_user_with_multiple_offerers_one_inactive(self):
        user = users_factories.ProFactory()
        offerers_factories.UserOffererFactory(user=user)  # Active offerer
        offerer_inactive = offerers_factories.OffererFactory(isActive=False)
        offerers_factories.UserOffererFactory(user=user, offerer=offerer_inactive)

        assert gdpr_api.has_suspended_offerer(user) is True

    def test_rejected_user_with_inactive_offerer(self):
        offerer = offerers_factories.OffererFactory(isActive=False)
        user_offerer = offerers_factories.RejectedUserOffererFactory(offerer=offerer)

        assert gdpr_api.has_suspended_offerer(user_offerer.user) is True

    def test_user_with_rejected_inactive_offerer(self):
        offerer = offerers_factories.RejectedOffererFactory()
        user_offerer = offerers_factories.UserOffererFactory(offerer=offerer)

        assert gdpr_api.has_suspended_offerer(user_offerer.user) is False


class IsSoleUserWithOngoingActivitiesTest:
    def test_sole_user_with_active_offer(self):
        user_offerer = offerers_factories.UserOffererFactory()
        offer = offers_factories.OfferFactory(
            venue__managingOfferer=user_offerer.offerer,
        )
        offers_factories.StockFactory(
            offer=offer,
        )

        assert gdpr_api.is_sole_user_with_ongoing_activities(user_offerer.user) is True

    def test_sole_user_with_scheduled_offer(self):
        user_offerer = offerers_factories.UserOffererFactory()
        offer = offers_factories.OfferFactory(
            publicationDatetime=datetime.datetime.now() + datetime.timedelta(days=1),
            venue__managingOfferer=user_offerer.offerer,
        )
        offers_factories.StockFactory(
            offer=offer,
        )

        assert gdpr_api.is_sole_user_with_ongoing_activities(user_offerer.user) is True

    def test_sole_user_with_published_offer(self):
        user_offerer = offerers_factories.UserOffererFactory()
        offer = offers_factories.OfferFactory(
            bookingAllowedDatetime=datetime.datetime.now() + datetime.timedelta(days=1),
            venue__managingOfferer=user_offerer.offerer,
        )
        offers_factories.StockFactory(
            offer=offer,
        )

        assert gdpr_api.is_sole_user_with_ongoing_activities(user_offerer.user) is True

    def test_sole_user_with_inactive_offer(self):
        user_offerer = offerers_factories.UserOffererFactory()
        venue = offerers_factories.VenueFactory(managingOfferer=user_offerer.offerer)
        offers_factories.StockFactory(
            offer__venue=venue,
            offer__validation=offers_models.OfferValidationStatus.DRAFT,
        )

        assert gdpr_api.is_sole_user_with_ongoing_activities(user_offerer.user) is False

    def test_sole_user_with_confirmed_booking(self):
        user_offerer = offerers_factories.UserOffererFactory()
        venue = offerers_factories.VenueFactory(managingOfferer=user_offerer.offerer)
        bookings_factories.BookingFactory(
            stock__offer__venue=venue,
            status=bookings_models.BookingStatus.CONFIRMED,
        )

        assert gdpr_api.is_sole_user_with_ongoing_activities(user_offerer.user) is True

    def test_sole_user_with_used_booking(self):
        user_offerer = offerers_factories.UserOffererFactory()
        venue = offerers_factories.VenueFactory(managingOfferer=user_offerer.offerer)
        bookings_factories.BookingFactory(
            stock__offer__venue=venue,
            status=bookings_models.BookingStatus.USED,
        )

        assert gdpr_api.is_sole_user_with_ongoing_activities(user_offerer.user) is True

    def test_sole_user_with_active_collective_offer(self):
        user_offerer = offerers_factories.UserOffererFactory()
        educational_factories.CollectiveOfferFactory(venue__managingOfferer=user_offerer.offerer, isActive=True)

        assert gdpr_api.is_sole_user_with_ongoing_activities(user_offerer.user) is True

    def test_sole_user_with_inactive_collective_offer(self):
        user_offerer = offerers_factories.UserOffererFactory()
        educational_factories.CollectiveOfferFactory(venue__managingOfferer=user_offerer.offerer, isActive=False)

        assert gdpr_api.is_sole_user_with_ongoing_activities(user_offerer.user) is False

    def test_sole_user_with_active_collective_offer_template(self):
        user_offerer = offerers_factories.UserOffererFactory()
        educational_factories.CollectiveOfferTemplateFactory(venue__managingOfferer=user_offerer.offerer, isActive=True)

        assert gdpr_api.is_sole_user_with_ongoing_activities(user_offerer.user) is True

    def test_sole_user_with_inactive_collective_offer_template(self):
        user_offerer = offerers_factories.UserOffererFactory()
        educational_factories.CollectiveOfferTemplateFactory(
            venue__managingOfferer=user_offerer.offerer, isActive=False
        )

        assert gdpr_api.is_sole_user_with_ongoing_activities(user_offerer.user) is False

    def test_sole_user_with_pending_collective_booking(self):
        user_offerer = offerers_factories.UserOffererFactory()
        educational_factories.CollectiveBookingFactory(
            offerer=user_offerer.offerer,
            status=educational_models.CollectiveBookingStatus.PENDING,
        )

        assert gdpr_api.is_sole_user_with_ongoing_activities(user_offerer.user) is True

    def test_sole_user_with_confirmed_collective_booking(self):
        user_offerer = offerers_factories.UserOffererFactory()
        educational_factories.CollectiveBookingFactory(
            offerer=user_offerer.offerer,
            status=educational_models.CollectiveBookingStatus.CONFIRMED,
        )

        assert gdpr_api.is_sole_user_with_ongoing_activities(user_offerer.user) is True

    def test_sole_user_with_used_collective_booking(self):
        user_offerer = offerers_factories.UserOffererFactory()
        educational_factories.CollectiveBookingFactory(
            offerer=user_offerer.offerer,
            status=educational_models.CollectiveBookingStatus.CONFIRMED,
        )

        assert gdpr_api.is_sole_user_with_ongoing_activities(user_offerer.user) is True

    def test_two_users_with_one_inactive(self):
        user_offerer = offerers_factories.UserOffererFactory()
        offerers_factories.UserOffererFactory(offerer=user_offerer.offerer, user__isActive=False)
        offer = offers_factories.OfferFactory(
            venue__managingOfferer=user_offerer.offerer,
        )
        offers_factories.StockFactory(
            offer=offer,
        )

        assert gdpr_api.is_sole_user_with_ongoing_activities(user_offerer.user) is True

    def test_multiple_users_with_active_offer(self):
        user_offerer = offerers_factories.UserOffererFactory()
        offerers_factories.UserOffererFactory(offerer=user_offerer.offerer)
        offer = offers_factories.OfferFactory(
            venue__managingOfferer=user_offerer.offerer,
        )
        offers_factories.StockFactory(
            offer=offer,
        )

        assert gdpr_api.is_sole_user_with_ongoing_activities(user_offerer.user) is False

    def test_multiple_users_with_active_collective_offer(self):
        user_offerer = offerers_factories.UserOffererFactory()
        offerers_factories.UserOffererFactory(offerer=user_offerer.offerer)
        educational_factories.CollectiveOfferFactory(venue__managingOfferer=user_offerer.offerer, isActive=True)

        assert gdpr_api.is_sole_user_with_ongoing_activities(user_offerer.user) is False

    def test_multiple_users_with_active_collective_offer_template(self):
        user_offerer = offerers_factories.UserOffererFactory()
        offerers_factories.UserOffererFactory(offerer=user_offerer.offerer)
        educational_factories.CollectiveOfferTemplateFactory(venue__managingOfferer=user_offerer.offerer, isActive=True)

        assert gdpr_api.is_sole_user_with_ongoing_activities(user_offerer.user) is False

    def test_user_with_multiple_offerers_one_with_activities(self):
        user = users_factories.ProFactory()

        first_user_offerer = offerers_factories.UserOffererFactory(user=user)
        venue = offerers_factories.VenueFactory(managingOfferer=first_user_offerer.offerer)
        offers_factories.StockFactory(
            offer__venue=venue,
            offer__validation=offers_models.OfferValidationStatus.APPROVED,
        )

        offerers_factories.UserOffererFactory(user=user)

        assert gdpr_api.is_sole_user_with_ongoing_activities(user) is True

    def test_sole_user_with_created_finance_incident(self):
        user_offerer = offerers_factories.UserOffererFactory()
        venue = offerers_factories.VenueFactory(managingOfferer=user_offerer.offerer)
        finance_factories.FinanceIncidentFactory(
            venue=venue,
            status=finance_models.IncidentStatus.CREATED,
        )

        assert gdpr_api.is_sole_user_with_ongoing_activities(user_offerer.user) is True

    def test_sole_user_with_validated_finance_incident(self):
        user_offerer = offerers_factories.UserOffererFactory()
        venue = offerers_factories.VenueFactory(managingOfferer=user_offerer.offerer)
        finance_factories.FinanceIncidentFactory(
            venue=venue,
            status=finance_models.IncidentStatus.VALIDATED,
        )

        assert gdpr_api.is_sole_user_with_ongoing_activities(user_offerer.user) is True


class AnonymizeProUsersTest:
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
    @mock.patch("pcapi.core.users.gdpr_api.anonymize_pro_user", return_value=True)
    def test_anonymize_pro_user(
        self, mock_anonymize_pro_user, offerer_validation_status, user_offerer_validation_status
    ):
        user_offerer_to_anonymize = offerers_factories.NonAttachedUserOffererFactory(
            user__lastConnectionDate=date_utils.get_naive_utc_now() - datetime.timedelta(days=366 * 3),
            offerer__validationStatus=offerer_validation_status,
            validationStatus=user_offerer_validation_status,
        )
        user_offerer_to_keep = offerers_factories.NonAttachedUserOffererFactory(
            offerer=user_offerer_to_anonymize.offerer,
            user__lastConnectionDate=date_utils.get_naive_utc_now(),
        )

        gdpr_api.anonymize_pro_users()

        assert user_offerer_to_keep.user.has_non_attached_pro_role
        mock_anonymize_pro_user.assert_called_once_with(user_offerer_to_anonymize.user)

    @mock.patch("pcapi.core.users.gdpr_api.anonymize_pro_user", return_value=True)
    def test_keep_pro_users_with_activity_less_than_three_years(self, mock_anonymize_pro_user):
        users_factories.NonAttachedProFactory(
            lastConnectionDate=date_utils.get_naive_utc_now() - relativedelta(years=3, days=-1)
        )
        users_factories.NonAttachedProFactory(lastConnectionDate=date_utils.get_naive_utc_now())

        gdpr_api.anonymize_pro_users()

        assert db.session.query(users_models.User).filter(users_models.User.has_non_attached_pro_role).count() == 2
        mock_anonymize_pro_user.assert_not_called()

    @mock.patch("pcapi.core.users.gdpr_api.anonymize_pro_user", return_value=True)
    def test_keep_pro_users_also_beneficiariy_or_candidate(self, mock_anonymize_pro_user):
        offerers_factories.DeletedUserOffererFactory(
            user=users_factories.BeneficiaryGrant18Factory(
                roles=[users_models.UserRole.NON_ATTACHED_PRO, users_models.UserRole.BENEFICIARY],
                lastConnectionDate=date_utils.get_naive_utc_now() - relativedelta(years=4),
            )
        )
        offerers_factories.RejectedUserOffererFactory(
            user=users_factories.UnderageBeneficiaryFactory(
                roles=[users_models.UserRole.NON_ATTACHED_PRO, users_models.UserRole.UNDERAGE_BENEFICIARY],
                lastConnectionDate=date_utils.get_naive_utc_now() - relativedelta(years=4),
            )
        )
        subscription_factories.BeneficiaryFraudCheckFactory(
            user=offerers_factories.RejectedUserOffererFactory(
                user__lastConnectionDate=date_utils.get_naive_utc_now() - relativedelta(years=4),
            ).user
        )

        gdpr_api.anonymize_pro_users()

        assert db.session.query(users_models.User).filter(users_models.User.has_non_attached_pro_role).count() == 3
        mock_anonymize_pro_user.assert_not_called()

    @mock.patch("pcapi.core.users.gdpr_api.anonymize_pro_user", return_value=True)
    def test_keep_when_attached_to_another_active_offerer(self, mock_anonymize_pro_user):
        user_offerer = offerers_factories.DeletedUserOffererFactory(
            user__lastConnectionDate=date_utils.get_naive_utc_now() - relativedelta(years=4),
        )
        offerers_factories.NewUserOffererFactory(user=user_offerer.user)

        gdpr_api.anonymize_pro_users()

        assert user_offerer.user.has_any_pro_role
        mock_anonymize_pro_user.assert_not_called()

    @mock.patch("pcapi.core.users.gdpr_api.anonymize_pro_user", return_value=True)
    def test_anonymize_non_attached_pro_user(self, mock_anonymize_pro_user):
        user_to_anonymize = users_factories.NonAttachedProFactory(
            lastConnectionDate=date_utils.get_naive_utc_now() - datetime.timedelta(days=366 * 3)
        )
        user_to_keep1 = users_factories.NonAttachedProFactory(lastConnectionDate=date_utils.get_naive_utc_now())
        user_to_keep2 = users_factories.NonAttachedProFactory()

        gdpr_api.anonymize_pro_users()

        assert user_to_keep1.has_non_attached_pro_role
        assert user_to_keep2.has_non_attached_pro_role
        mock_anonymize_pro_user.assert_called_once_with(user_to_anonymize)

    @mock.patch("pcapi.core.users.gdpr_api.anonymize_pro_user", return_value=True)
    def test_anonymize_non_attached_never_connected_pro(self, mock_anonymize_pro_user):
        user_to_anonymize = users_factories.NonAttachedProFactory(
            dateCreated=date_utils.get_naive_utc_now() - datetime.timedelta(days=366 * 3)
        )
        user_to_keep = users_factories.NonAttachedProFactory()

        gdpr_api.anonymize_pro_users()

        assert user_to_keep.has_non_attached_pro_role
        mock_anonymize_pro_user.assert_called_once_with(user_to_anonymize)


class AnonymizeInternalUserTest:
    @pytest.mark.parametrize(
        "factory, expected_prefix",
        [
            (users_factories.AdminFactory, "ex_backoffice_user"),
            (users_factories.BeneficiaryFactory, "anonymous"),
            (users_factories.ProFactory, "anonymous"),
        ],
    )
    def test_anonymize_internal_user(self, factory, expected_prefix):
        # check independance with the user role
        user_to_anonymize = factory(
            email="user_to_anonymize@passculture.app",
            isActive=False,
        )
        history_factories.SuspendedUserActionHistoryFactory(
            user=user_to_anonymize,
            actionDate=date_utils.get_naive_utc_now() - datetime.timedelta(days=367),
        )

        gdpr_api.anonymize_internal_users()

        _assert_user_is_anonymized(user_to_anonymize, prefix=expected_prefix)

    def test_anonymize_internal_user_without_action_date(self):
        user_to_anonymize = users_factories.AdminFactory(
            email="user_to_anonymize@passculture.app",
            isActive=False,
        )
        action_history = history_factories.SuspendedUserActionHistoryFactory(
            user=user_to_anonymize,
        )
        action_history.actionDate = None
        db.session.flush()

        gdpr_api.anonymize_internal_users()

        _assert_user_is_anonymized(user_to_anonymize, prefix="ex_backoffice_user")

    def test_keep_recent_internal_user(self):
        user_to_anonymize = users_factories.AdminFactory(
            email="user_to_anonymize@passculture.app",
            isActive=False,
        )
        history_factories.SuspendedUserActionHistoryFactory(
            user=user_to_anonymize,
            actionDate=date_utils.get_naive_utc_now(),
        )

        gdpr_api.anonymize_internal_users()

        assert user_to_anonymize.email == "user_to_anonymize@passculture.app"

    def test_keep_recent_internal_user_with_old_suspension(self):
        user_to_anonymize = users_factories.AdminFactory(
            email="user_to_anonymize@passculture.app",
            isActive=False,
        )
        history_factories.SuspendedUserActionHistoryFactory(
            user=user_to_anonymize,
            actionDate=date_utils.get_naive_utc_now() - datetime.timedelta(days=367),
        )
        history_factories.SuspendedUserActionHistoryFactory(
            user=user_to_anonymize,
            actionDate=date_utils.get_naive_utc_now(),
        )

        gdpr_api.anonymize_internal_users()

        assert user_to_anonymize.email == "user_to_anonymize@passculture.app"

    def test_keep_active_internal_user(self):
        user_to_anonymize = users_factories.AdminFactory(
            email="user_to_anonymize@passculture.app",
            isActive=True,
        )
        history_factories.SuspendedUserActionHistoryFactory(
            user=user_to_anonymize,
            actionDate=date_utils.get_naive_utc_now() - datetime.timedelta(days=367),
        )

        gdpr_api.anonymize_internal_users()

        assert user_to_anonymize.email == "user_to_anonymize@passculture.app"

    def test_keep_external_admin(self):
        user_to_anonymize = users_factories.AdminFactory(
            isActive=False,
        )
        history_factories.SuspendedUserActionHistoryFactory(
            user=user_to_anonymize,
            actionDate=date_utils.get_naive_utc_now() - datetime.timedelta(days=367),
        )

        gdpr_api.anonymize_internal_users()

        assert user_to_anonymize.email.endswith("@example.com")


class AnonymizeBeneficiaryUsersTest(StorageFolderManager):
    storage_folder = settings.LOCAL_STORAGE_DIR / settings.GCP_GDPR_EXTRACT_BUCKET / settings.GCP_GDPR_EXTRACT_FOLDER

    def import_iris(self):
        path = DATA_DIR / "iris_min.7z"
        geography_api.import_iris_from_7z(str(path))

    def test_anonymize_beneficiary_users(self) -> None:
        user_beneficiary_to_anonymize = users_factories.BeneficiaryFactory(
            firstName="user_beneficiary_to_anonymize",
            age=18,
            lastConnectionDate=date_utils.get_naive_utc_now() - relativedelta(years=3, days=1),
            deposit__expirationDate=date_utils.get_naive_utc_now() - relativedelta(years=5, days=1),
        )
        user_underage_beneficiary_to_anonymize = users_factories.BeneficiaryFactory(
            firstName="user_underage_beneficiary_to_anonymize",
            age=17,
            lastConnectionDate=date_utils.get_naive_utc_now() - relativedelta(years=3, days=1),
            deposit__expirationDate=date_utils.get_naive_utc_now() - relativedelta(years=5, days=1),
        )
        user_with_ready_gdpr_extract_to_anonymize = users_factories.BeneficiaryFactory(
            firstName="user_beneficiary_to_anonymize",
            age=18,
            lastConnectionDate=date_utils.get_naive_utc_now() - relativedelta(years=3, days=1),
            gdprUserDataExtracts=[
                users_factories.GdprUserDataExtractBeneficiaryFactory(
                    dateProcessed=date_utils.get_naive_utc_now() - datetime.timedelta(days=1)
                )
            ],
            deposit__expirationDate=date_utils.get_naive_utc_now() - relativedelta(years=5, days=1),
        )
        user_with_expired_gdpr_extract_to_anonymize = users_factories.BeneficiaryFactory(
            firstName="user_beneficiary_to_anonymize",
            age=18,
            lastConnectionDate=date_utils.get_naive_utc_now() - relativedelta(years=3, days=1),
            gdprUserDataExtracts=[
                users_factories.GdprUserDataExtractBeneficiaryFactory(
                    dateCreated=date_utils.get_naive_utc_now() - datetime.timedelta(days=8)
                )
            ],
            deposit__expirationDate=date_utils.get_naive_utc_now() - relativedelta(years=5, days=1),
        )
        user_too_new = users_factories.BeneficiaryFactory(
            firstName="user_too_new",
            age=18,
            lastConnectionDate=date_utils.get_naive_utc_now() - relativedelta(years=3, days=-11),
            deposit__expirationDate=date_utils.get_naive_utc_now() - relativedelta(years=5, days=1),
        )
        user_deposit_too_new = users_factories.BeneficiaryFactory(
            firstName="user_deposit_too_new",
            age=18,
            lastConnectionDate=date_utils.get_naive_utc_now() - relativedelta(years=3, days=1),
            deposit__expirationDate=date_utils.get_naive_utc_now() - relativedelta(years=5, days=-11),
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

        with mock.patch("pcapi.core.users.gdpr_api.get_iris_from_address", return_value=iris):
            gdpr_api.anonymize_beneficiary_users()

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
            lastConnectionDate=date_utils.get_naive_utc_now() - relativedelta(years=3, days=1),
            deposit__expirationDate=date_utils.get_naive_utc_now() - relativedelta(years=5, days=1),
        )
        chronicle = chronicles_factories.ChronicleFactory(
            user=user_to_anonymize,
            email="radomemail@example.com",
        )

        gdpr_api.anonymize_beneficiary_users()
        db.session.refresh(chronicle)

        assert chronicle.userId is None
        assert chronicle.email == "anonymized_email@anonymized.passculture"

    def test_anonymize_beneficiary_user_force_iris_not_found(self) -> None:
        user_to_anonymize = users_factories.BeneficiaryFactory(
            firstName="user_to_anonymize",
            age=18,
            lastConnectionDate=date_utils.get_naive_utc_now() - relativedelta(years=3, days=1),
            deposit__expirationDate=date_utils.get_naive_utc_now() - relativedelta(years=5, days=1),
        )

        gdpr_api.anonymize_beneficiary_users()

        db.session.refresh(user_to_anonymize)

        assert len(sendinblue_testing.sendinblue_requests) == 1
        assert len(batch_testing.requests) == 1
        assert batch_testing.requests[0]["user_id"] == user_to_anonymize.id
        assert user_to_anonymize.firstName is None

    def test_anonymize_beneficiary_user_with_unprocessed_gdpr_extract(self) -> None:
        user_beneficiary_to_anonymize = users_factories.BeneficiaryFactory(
            firstName="user_beneficiary_to_anonymize",
            age=18,
            lastConnectionDate=date_utils.get_naive_utc_now() - relativedelta(years=3, days=1),
            gdprUserDataExtracts=[users_factories.GdprUserDataExtractBeneficiaryFactory()],
            deposit__expirationDate=date_utils.get_naive_utc_now() - relativedelta(years=5, days=1),
        )

        self.import_iris()
        iris = db.session.query(geography_models.IrisFrance).first()

        with mock.patch("pcapi.core.users.gdpr_api.get_iris_from_address", return_value=iris):
            gdpr_api.anonymize_beneficiary_users()

        db.session.refresh(user_beneficiary_to_anonymize)

        assert len(sendinblue_testing.sendinblue_requests) == 0
        assert user_beneficiary_to_anonymize.firstName == "user_beneficiary_to_anonymize"
        assert db.session.query(users_models.GdprUserDataExtract).count() == 1

    def test_anonymize_user_tagged_when_he_is_21(self) -> None:
        user_to_anonymize = users_factories.BeneficiaryFactory(
            validatedBirthDate=date_utils.get_naive_utc_now() - relativedelta(years=18, days=1),
        )
        users_factories.GdprUserAnonymizationFactory(user=user_to_anonymize)

        when_user_is_21 = date_utils.get_naive_utc_now() + relativedelta(years=3)
        with time_machine.travel(when_user_is_21):
            gdpr_api.anonymize_beneficiary_users()
            db.session.refresh(user_to_anonymize)

        assert user_to_anonymize.firstName is None
        assert db.session.query(users_models.GdprUserAnonymization).count() == 0

    def test_do_not_anonymize_user_tagged_when_he_is_less_than_21(self) -> None:
        user_to_anonymize = users_factories.BeneficiaryFactory(
            lastConnectionDate=date_utils.get_naive_utc_now(),
            validatedBirthDate=date_utils.get_naive_utc_now() - relativedelta(years=18),
        )
        users_factories.GdprUserAnonymizationFactory(user=user_to_anonymize)

        when_user_is_21 = date_utils.get_naive_utc_now() + relativedelta(years=3)
        with time_machine.travel(when_user_is_21 - relativedelta(days=1)):
            gdpr_api.anonymize_beneficiary_users()
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
            lastConnectionDate=date_utils.get_naive_utc_now(),
            validatedBirthDate=date_utils.get_naive_utc_now() - relativedelta(years=21, days=12),
        )
        users_factories.GdprUserAnonymizationFactory(user=user_to_anonymize)
        history_factories.SuspendedUserActionHistoryFactory(
            actionDate=date_utils.get_naive_utc_now() - relativedelta(years=3, days=1),
            actionType=history_models.ActionType.USER_SUSPENDED,
            reason=reason,
            user=user_to_anonymize,
        )

        gdpr_api.anonymize_beneficiary_users()
        db.session.refresh(user_to_anonymize)

        assert user_to_anonymize.firstName != f"Anonymous_{user_to_anonymize.id}"
        assert db.session.query(users_models.GdprUserAnonymization).count() == 1

    def test_do_not_anonymize_user_tagged_when_he_is_21_and_tagged_as_fraud_5_years_ago(self) -> None:
        user_to_anonymize = users_factories.BeneficiaryFactory(
            lastConnectionDate=date_utils.get_naive_utc_now(),
            validatedBirthDate=date_utils.get_naive_utc_now() - relativedelta(years=21, days=12),
        )
        users_factories.GdprUserAnonymizationFactory(user=user_to_anonymize)
        history_factories.SuspendedUserActionHistoryFactory(
            actionDate=date_utils.get_naive_utc_now() - relativedelta(years=5, days=1),
            actionType=history_models.ActionType.USER_SUSPENDED,
            reason=users_constants.SuspensionReason.FRAUD_RESELL_PRODUCT,
            user=user_to_anonymize,
        )

        gdpr_api.anonymize_beneficiary_users()
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
            lastConnectionDate=date_utils.get_naive_utc_now() - relativedelta(years=3, days=1),
            deposit__expirationDate=date_utils.get_naive_utc_now() - relativedelta(years=5, days=1),
            isActive=False,
        )
        history_factories.SuspendedUserActionHistoryFactory(
            actionDate=date_utils.get_naive_utc_now() - relativedelta(years=3, days=1),
            actionType=history_models.ActionType.USER_SUSPENDED,
            reason=reason,
            user=user_to_anonymize,
        )

        gdpr_api.anonymize_beneficiary_users()

        db.session.refresh(user_to_anonymize)

        assert len(sendinblue_testing.sendinblue_requests) == 0
        assert user_to_anonymize.firstName == "user_to_anonymize"

    def test_anonymize_beneficiary_user_suspended_5_years_ago_with_fraud(self) -> None:
        user_to_anonymize = users_factories.BeneficiaryFactory(
            firstName="user_to_anonymize",
            age=18,
            lastConnectionDate=date_utils.get_naive_utc_now() - relativedelta(years=3, days=1),
            deposit__expirationDate=date_utils.get_naive_utc_now() - relativedelta(years=5, days=1),
            isActive=False,
        )
        history_factories.SuspendedUserActionHistoryFactory(
            actionDate=date_utils.get_naive_utc_now() - relativedelta(years=5, days=1),
            actionType=history_models.ActionType.USER_SUSPENDED,
            reason=users_constants.SuspensionReason.FRAUD_RESELL_PRODUCT,
            user=user_to_anonymize,
        )

        gdpr_api.anonymize_beneficiary_users()

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
            lastConnectionDate=date_utils.get_naive_utc_now() - relativedelta(years=3, days=1),
            deposit__expirationDate=date_utils.get_naive_utc_now() - relativedelta(years=5, days=1),
            isActive=False,
        )
        history_factories.SuspendedUserActionHistoryFactory(
            actionDate=date_utils.get_naive_utc_now() - relativedelta(years=3, days=1),
            actionType=history_models.ActionType.USER_SUSPENDED,
            reason=reason,
            user=user_to_anonymize,
        )

        gdpr_api.anonymize_beneficiary_users()

        db.session.refresh(user_to_anonymize)

        assert len(sendinblue_testing.sendinblue_requests) == 1
        assert user_to_anonymize.firstName != "user_to_anonymize"

    def test_anonymize_user_without_validated_birth_date(self) -> None:
        user_to_anonymize = users_factories.BeneficiaryFactory(
            firstName="user_to_anonymize",
        )
        user_to_anonymize.validatedBirthDate = None
        user_to_anonymize.dateOfBirth = date_utils.get_naive_utc_now() - relativedelta(years=21, days=3)
        users_factories.GdprUserAnonymizationFactory(user=user_to_anonymize)

        gdpr_api.anonymize_beneficiary_users()

        db.session.refresh(user_to_anonymize)
        assert user_to_anonymize.firstName != "user_to_anonymize"
        assert db.session.query(users_models.GdprUserAnonymization).count() == 0


class AnonymizeUserDepositsTest:
    def test_anonymize_user_deposits(self) -> None:
        now = date_utils.get_naive_utc_now().replace(hour=0, minute=0, second=0, microsecond=0)
        user_recent_deposit = users_factories.BeneficiaryFactory(
            deposit__dateCreated=now - relativedelta(years=6),
            deposit__expirationDate=now - relativedelta(years=5, days=1),
        )
        user_old_deposit = users_factories.BeneficiaryFactory(
            deposit__dateCreated=now - relativedelta(years=11, days=1),
            deposit__expirationDate=now - relativedelta(years=10, days=1),
        )

        gdpr_api.anonymize_user_deposits()

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
        extract = users_factories.GdprUserDataExtractBeneficiaryFactory(dateProcessed=date_utils.get_naive_utc_now())
        with open(self.storage_folder / f"{extract.id}.zip", "wb") as fp:
            fp.write(b"[personal data compressed with deflate]")
        # when
        gdpr_api.delete_gdpr_extract(extract.id)

        # then
        assert db.session.query(users_models.GdprUserDataExtract).count() == 0
        assert len(os.listdir(self.storage_folder)) == 0

    def test_extract_file_does_not_exists(self):
        # given
        extract = users_factories.GdprUserDataExtractBeneficiaryFactory(dateProcessed=date_utils.get_naive_utc_now())
        # when
        gdpr_api.delete_gdpr_extract(extract.id)

        # then
        assert db.session.query(users_models.GdprUserDataExtract).count() == 0


class CleanGdprExtractTest(StorageFolderManager):
    storage_folder = settings.LOCAL_STORAGE_DIR / settings.GCP_GDPR_EXTRACT_BUCKET / settings.GCP_GDPR_EXTRACT_FOLDER

    def test_delete_expired_extracts(self):
        # given
        extract = users_factories.GdprUserDataExtractBeneficiaryFactory(
            dateProcessed=date_utils.get_naive_utc_now() - datetime.timedelta(days=6),
            dateCreated=date_utils.get_naive_utc_now() - datetime.timedelta(days=8),
        )
        with open(self.storage_folder / f"{extract.id}.zip", "wb") as fp:
            fp.write(b"[personal data compressed with deflate]")
        # when
        gdpr_api.clean_gdpr_extracts()
        # then
        assert db.session.query(users_models.GdprUserDataExtract).count() == 0
        assert len(os.listdir(self.storage_folder)) == 0

    def test_delete_extracts_files_not_in_db(self):
        # given
        with open(self.storage_folder / "1.zip", "wb") as fp:
            fp.write(b"[personal data compressed with deflate]")
        # when
        gdpr_api.clean_gdpr_extracts()
        # then
        assert len(os.listdir(self.storage_folder)) == 0

    def test_delete_expired_unprocessed_extracts(self):
        # given
        users_factories.GdprUserDataExtractBeneficiaryFactory(
            dateCreated=date_utils.get_naive_utc_now() - datetime.timedelta(days=8)
        )
        # when
        gdpr_api.clean_gdpr_extracts()
        # then
        assert db.session.query(users_models.GdprUserDataExtract).count() == 0

    def test_keep_unexpired_extracts(self):
        # given
        extract = users_factories.GdprUserDataExtractBeneficiaryFactory(
            dateProcessed=date_utils.get_naive_utc_now() - datetime.timedelta(days=5),
            dateCreated=date_utils.get_naive_utc_now() - datetime.timedelta(days=6),
        )
        with open(self.storage_folder / f"{extract.id}.zip", "wb") as fp:
            fp.write(b"[personal data compressed with deflate]")
        # when
        gdpr_api.clean_gdpr_extracts()
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
    subscription_factories.BeneficiaryFraudCheckFactory(
        dateCreated=now,
        eligibilityType=users_models.EligibilityType.AGE18,
        status=subscription_models.FraudCheckStatus.OK,
        type=subscription_models.FraudCheckType.DMS,
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
        subscription_models.BeneficiaryFraudCheck(
            user=user,
            dateCreated=now,
            thirdPartyId="third_party_id",
            type=subscription_models.FraudCheckType.DMS,
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

    @mock.patch("pcapi.core.users.gdpr_api.generate_pdf_from_html", return_value=b"content of a pdf")
    def test_json_output(self, pdf_generator_mock) -> None:
        user = generate_beneficiary()
        extract = users_factories.GdprUserDataExtractBeneficiaryFactory(
            user=user,
        )
        with assert_num_queries(self.expected_queries):
            gdpr_api.extract_beneficiary_data(extract=extract)

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

    @mock.patch("pcapi.core.users.gdpr_api.generate_pdf_from_html", return_value=b"content of a pdf")
    def test_pdf_html(self, pdf_generator_mock) -> None:
        user = generate_beneficiary()
        extract = users_factories.GdprUserDataExtractBeneficiaryFactory(
            user=user,
        )
        with assert_num_queries(self.expected_queries):
            gdpr_api.extract_beneficiary_data(extract=extract)

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

        gdpr_api.extract_beneficiary_data(extract)

        file_path = self.storage_folder / f"{extract.id}.zip"
        pdf_file_name = f"{user.email}.pdf"
        with zipfile.ZipFile(file_path, mode="r") as zip_pointer:
            files = zip_pointer.namelist()
            assert len(files) == self.output_files_count
            assert pdf_file_name in files
            with zip_pointer.open(pdf_file_name) as pdf_pointer:
                assert pdf_pointer.read()

    @mock.patch("pcapi.core.users.gdpr_api.generate_pdf_from_html", return_value=b"content of a pdf")
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
            gdpr_api.extract_beneficiary_data(extract=extract)

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

    @mock.patch("pcapi.core.users.gdpr_api.generate_pdf_from_html", return_value=b"content of a pdf")
    def test_pdf_with_minimal_non_empty_user(self, pdf_generator_mock):
        user = generate_minimal_beneficiary()
        extract = users_factories.GdprUserDataExtractBeneficiaryFactory(
            user=user,
        )
        with assert_num_queries(self.expected_queries):
            gdpr_api.extract_beneficiary_data(extract=extract)

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

    @mock.patch("pcapi.core.users.gdpr_api.generate_pdf_from_html", return_value=b"content of a pdf")
    def test_nominal(self, generate_pdf_mock, clear_redis):
        redis = current_app.redis_client
        redis.set(users_constants.GDPR_EXTRACT_DATA_COUNTER, "3")
        extract = users_factories.GdprUserDataExtractBeneficiaryFactory()
        with time_machine.travel("2023-12-15 10:11:00"):
            with assert_num_queries(self.expected_queries):
                result = gdpr_api.extract_beneficiary_data_command()

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
                result = gdpr_api.extract_beneficiary_data_command()

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
                result = gdpr_api.extract_beneficiary_data_command()

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
                result = gdpr_api.extract_beneficiary_data_command()

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
                result = gdpr_api.extract_beneficiary_data_command()

        db.session.refresh(extract)
        assert result == False
        assert not redis.exists(users_constants.GDPR_EXTRACT_DATA_LOCK)
        assert redis.get(users_constants.GDPR_EXTRACT_DATA_COUNTER) == str(settings.GDPR_MAX_EXTRACT_PER_DAY)
        assert not (self.storage_folder / f"{extract.id}.zip").exists()
        assert extract.dateProcessed is None

    @mock.patch("pcapi.core.users.gdpr_api.generate_pdf_from_html", return_value=b"content of a pdf")
    def test_reset_counter_at_midnight(self, generate_pdf_mock, clear_redis):
        redis = current_app.redis_client
        extract = users_factories.GdprUserDataExtractBeneficiaryFactory()
        redis.set(users_constants.GDPR_EXTRACT_DATA_COUNTER, settings.GDPR_MAX_EXTRACT_PER_DAY)

        with time_machine.travel("2023-12-15 00:01:00"):
            with assert_num_queries(self.expected_queries):
                result = gdpr_api.extract_beneficiary_data_command()

        db.session.refresh(extract)
        assert result == True
        assert not redis.exists(users_constants.GDPR_EXTRACT_DATA_LOCK)
        assert redis.get(users_constants.GDPR_EXTRACT_DATA_COUNTER) == "1"
        assert (self.storage_folder / f"{extract.id}.zip").exists()
        assert extract.dateProcessed is not None

    @mock.patch("pcapi.core.users.gdpr_api.generate_pdf_from_html", side_effect=Exception)
    def test_extract_failed(self, clear_redis):
        redis = current_app.redis_client
        redis.set(users_constants.GDPR_EXTRACT_DATA_COUNTER, "3")
        users_factories.GdprUserDataExtractBeneficiaryFactory()

        with time_machine.travel("2023-12-15 10:11:00"):
            # crashes before writing the log history
            with assert_num_queries(self.expected_queries - 1):
                with pytest.raises(Exception):
                    gdpr_api.extract_beneficiary_data_command()

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


class AnonymizeUserByIdTest:
    def test_user_found(self):
        email = "email@example.com"
        user = users_factories.UserFactory(email=email)

        gdpr_api.anonymize_user_by_id(user.id)
        db.session.flush()

        assert db.session.query(users_models.User).filter(users_models.User.email == email).count() == 0

    def test_user_not_found(self):
        gdpr_api.anonymize_user_by_id(0)
        assert True
