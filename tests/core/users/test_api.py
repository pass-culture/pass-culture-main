from datetime import date
from datetime import datetime
from datetime import time
from datetime import timedelta
from decimal import Decimal
from pathlib import Path
from unittest.mock import patch

from dateutil.relativedelta import relativedelta
from freezegun import freeze_time
import jwt
import pytest
import requests_mock

from pcapi import settings
from pcapi.core.bookings import factories as bookings_factories
from pcapi.core.bookings.models import BookingStatus
from pcapi.core.categories import subcategories
import pcapi.core.fraud.factories as fraud_factories
import pcapi.core.fraud.models as fraud_models
from pcapi.core.mails import testing as mails_testing
from pcapi.core.offers import factories as offers_factories
from pcapi.core.payments.conf import GRANT_18_VALIDITY_IN_YEARS
from pcapi.core.subscription import api as subscription_api
from pcapi.core.subscription import models as subscription_models
from pcapi.core.testing import override_features
from pcapi.core.testing import override_settings
from pcapi.core.users import api as users_api
from pcapi.core.users import constants as users_constants
from pcapi.core.users import factories as users_factories
from pcapi.core.users import testing as sendinblue_testing
from pcapi.core.users.api import BeneficiaryValidationStep
from pcapi.core.users.api import _set_offerer_departement_code
from pcapi.core.users.api import asynchronous_identity_document_verification
from pcapi.core.users.api import count_existing_id_check_tokens
from pcapi.core.users.api import create_id_check_token
from pcapi.core.users.api import create_pro_user
from pcapi.core.users.api import delete_expired_tokens
from pcapi.core.users.api import fulfill_account_password
from pcapi.core.users.api import fulfill_beneficiary_data
from pcapi.core.users.api import generate_and_save_token
from pcapi.core.users.api import get_domains_credit
from pcapi.core.users.api import set_pro_tuto_as_seen
from pcapi.core.users.api import steps_to_become_beneficiary
from pcapi.core.users.api import update_beneficiary_mandatory_information
from pcapi.core.users.exceptions import CloudTaskCreationException
from pcapi.core.users.exceptions import IdentityDocumentUploadException
from pcapi.core.users.factories import BeneficiaryImportFactory
from pcapi.core.users.factories import UserFactory
from pcapi.core.users.models import Credit
from pcapi.core.users.models import DomainsCredit
from pcapi.core.users.models import PhoneValidationStatusType
from pcapi.core.users.models import Token
from pcapi.core.users.models import TokenType
from pcapi.core.users.models import User
from pcapi.core.users.repository import get_user_with_valid_token
from pcapi.core.users.utils import encode_jwt_payload
from pcapi.model_creators.generic_creators import create_offerer
from pcapi.models import BeneficiaryImport
from pcapi.models import ImportStatus
from pcapi.models import db
from pcapi.models.beneficiary_import import BeneficiaryImportSources
from pcapi.models.user_session import UserSession
from pcapi.notifications.push import testing as batch_testing
from pcapi.routes.serialization.users import ProUserCreationBodyModel
from pcapi.tasks.account import VerifyIdentityDocumentRequest

import tests


pytestmark = pytest.mark.usefixtures("db_session")


class GenerateAndSaveTokenTest:
    def test_generate_and_save_token(self, app):
        user = users_factories.UserFactory(email="py@test.com")
        token_type = TokenType.RESET_PASSWORD
        life_time = timedelta(hours=24)

        generated_token = generate_and_save_token(user, token_type, life_time)

        saved_token = Token.query.filter_by(user=user).first()

        assert generated_token.id == saved_token.id
        assert saved_token.type == token_type

    def test_generate_and_save_token_without_expiration_date(self):
        user = users_factories.UserFactory(email="py@test.com")
        token_type = TokenType.RESET_PASSWORD

        generate_and_save_token(user, token_type)

        generated_token = Token.query.filter_by(user=user).first()

        assert generated_token.type == token_type
        assert generated_token.expirationDate is None

    def test_generate_and_save_token_with_wrong_type(self):
        user = users_factories.UserFactory(email="py@test.com")
        token_type = "not-enum-type"

        with pytest.raises(AttributeError):
            generate_and_save_token(user, token_type)


class ValidateJwtTokenTest:
    token_value = encode_jwt_payload({"pay": "load"})

    def test_get_user_with_valid_token(self):
        user = users_factories.UserFactory()
        token_type = TokenType.RESET_PASSWORD
        expiration_date = datetime.now() + timedelta(hours=24)

        saved_token = users_factories.TokenFactory(
            user=user, value=self.token_value, type=token_type, expirationDate=expiration_date
        )

        associated_user = get_user_with_valid_token(self.token_value, [token_type, "other-allowed-type"])

        assert associated_user.id == user.id
        assert Token.query.get(saved_token.id)

    def test_get_user_and_mark_token_as_used(self):
        user = users_factories.UserFactory()
        token_type = TokenType.RESET_PASSWORD
        expiration_date = datetime.now() + timedelta(hours=24)

        saved_token = users_factories.TokenFactory(
            user=user, value=self.token_value, type=token_type, expirationDate=expiration_date
        )

        associated_user = get_user_with_valid_token(self.token_value, [token_type])

        assert associated_user.id == user.id

        token = Token.query.get(saved_token.id)
        assert token.isUsed

    def test_get_user_with_valid_token_without_expiration_date(self):
        user = users_factories.UserFactory()
        token_type = TokenType.RESET_PASSWORD

        users_factories.TokenFactory(user=user, value=self.token_value, type=token_type)

        associated_user = get_user_with_valid_token(self.token_value, [token_type])

        assert associated_user.id == user.id

    def test_get_user_with_valid_token_wrong_token(self):
        user = users_factories.UserFactory()
        token_type = TokenType.RESET_PASSWORD

        users_factories.TokenFactory(user=user, value=self.token_value, type=token_type)

        associated_user = get_user_with_valid_token("wrong-token-value", [token_type])

        assert associated_user is None

    def test_get_user_with_valid_token_wrong_type(self):
        user = users_factories.UserFactory()
        token_type = TokenType.RESET_PASSWORD

        users_factories.TokenFactory(user=user, value=self.token_value, type=token_type)

        assert Token.query.filter_by(value=self.token_value).first() is not None

        associated_user = get_user_with_valid_token(self.token_value, ["other_type"])

        assert associated_user is None

    def test_get_user_with_valid_token_with_expired_date(self):
        user = users_factories.UserFactory()
        token_type = TokenType.RESET_PASSWORD

        expiration_date = datetime.now() - timedelta(hours=24)
        users_factories.TokenFactory(user=user, value=self.token_value, type=token_type, expirationDate=expiration_date)

        assert Token.query.filter_by(value=self.token_value).first() is not None

        associated_user = get_user_with_valid_token(self.token_value, [token_type])

        assert associated_user is None


class GenerateIdCheckTokenIfEligibleTest:
    @freeze_time("2018-06-01")
    def test_when_elible(self):
        user = users_factories.UserFactory(dateOfBirth=datetime(2000, 1, 1), departementCode="93")
        token = create_id_check_token(user)
        assert token

    @freeze_time("2018-06-01")
    def test_when_not_elible_above_age(self):
        # user is 19 years old
        user = users_factories.UserFactory(dateOfBirth=datetime(1999, 5, 1))
        token = create_id_check_token(user)
        assert not token


class CountIdCheckTokenTest:
    def test_count_no_token(self):
        user = users_factories.UserFactory(dateOfBirth=datetime(1999, 5, 1))
        assert count_existing_id_check_tokens(user) == 0

    def test_count_one_unused_token(self):
        user = users_factories.UserFactory(dateOfBirth=datetime(1999, 5, 1))

        users_factories.IdCheckToken(user=user, expirationDate=datetime.now() + timedelta(hours=2))
        assert count_existing_id_check_tokens(user) == 1

    def test_count_multiple_mixed_token(self):
        user = users_factories.UserFactory(dateOfBirth=datetime(1999, 5, 1))

        past_expiration_date = datetime.now() - timedelta(hours=2)
        future_expiration_date = datetime.now() + timedelta(hours=2)

        users_factories.IdCheckToken.create_batch(3, user=user, expirationDate=past_expiration_date)
        users_factories.IdCheckToken.create_batch(2, user=user, expirationDate=future_expiration_date)

        assert count_existing_id_check_tokens(user) == 2


class DeleteExpiredTokensTest:
    def test_deletion(self):
        user = users_factories.UserFactory()
        token_type = TokenType.RESET_PASSWORD
        life_time = timedelta(hours=24)

        never_expire_token = generate_and_save_token(user, token_type)
        not_expired_token = generate_and_save_token(user, token_type, life_time=life_time)
        # Generate an expired token
        with freeze_time(datetime.now() - life_time):
            generate_and_save_token(user, token_type, life_time=life_time)

        delete_expired_tokens()

        assert set(Token.query.all()) == {never_expire_token, not_expired_token}


class DeleteUserTokenTest:
    def test_delete_user_token(self):
        user = users_factories.UserFactory()
        users_factories.ResetPasswordToken(user=user)
        users_factories.EmailValidationToken(user=user)

        other_user = users_factories.BeneficiaryGrant18Factory()
        other_token = users_factories.EmailValidationToken(user=other_user)

        users_api.delete_all_users_tokens(user)

        assert Token.query.one_or_none() == other_token


class SuspendAccountTest:
    def test_suspend_admin(self):
        user = users_factories.AdminFactory()
        users_factories.UserSessionFactory(user=user)
        reason = users_constants.SuspensionReason.FRAUD
        actor = users_factories.AdminFactory()

        users_api.suspend_account(user, reason, actor)

        assert user.suspensionReason == str(reason)
        assert not user.isActive
        assert not user.isAdmin
        assert not user.has_admin_role
        assert not UserSession.query.filter_by(userId=user.id).first()
        assert actor.isActive

    def test_suspend_beneficiary(self):
        user = users_factories.BeneficiaryGrant18Factory()
        cancellable_booking = bookings_factories.BookingFactory(user=user)
        yesterday = datetime.now() - timedelta(days=1)
        confirmed_booking = bookings_factories.BookingFactory(
            user=user, cancellation_limit_date=yesterday, status=BookingStatus.CONFIRMED
        )
        used_booking = bookings_factories.UsedBookingFactory(user=user)
        actor = users_factories.AdminFactory()

        users_api.suspend_account(user, users_constants.SuspensionReason.FRAUD, actor)

        assert not user.isActive
        assert cancellable_booking.isCancelled
        assert cancellable_booking.status is BookingStatus.CANCELLED
        assert confirmed_booking.isCancelled
        assert confirmed_booking.status is BookingStatus.CANCELLED
        assert not used_booking.isCancelled
        assert used_booking.status is BookingStatus.USED

    def test_suspend_pro(self):
        booking = bookings_factories.BookingFactory()
        pro = offers_factories.UserOffererFactory(offerer=booking.offerer).user
        actor = users_factories.AdminFactory()

        users_api.suspend_account(pro, users_constants.SuspensionReason.FRAUD, actor)

        assert not pro.isActive
        assert booking.isCancelled
        assert booking.status is BookingStatus.CANCELLED

    def test_suspend_pro_with_other_offerer_users(self):
        booking = bookings_factories.BookingFactory()
        pro = offers_factories.UserOffererFactory(offerer=booking.offerer).user
        offers_factories.UserOffererFactory(offerer=booking.offerer)
        actor = users_factories.AdminFactory()

        users_api.suspend_account(pro, users_constants.SuspensionReason.FRAUD, actor)

        assert not pro.isActive
        assert not booking.isCancelled
        assert booking.status is not BookingStatus.CANCELLED


class UnsuspendAccountTest:
    def test_unsuspend_account(self):
        user = users_factories.UserFactory(isActive=False, suspensionReason="User not cool")
        actor = users_factories.AdminFactory()

        users_api.unsuspend_account(user, actor)

        assert not user.suspensionReason
        assert user.isActive

    def test_bulk_unsuspend_account(self):
        user1 = users_factories.UserFactory(isActive=False, suspensionReason="User not cool")
        user2 = users_factories.UserFactory(isActive=False, suspensionReason="User not cool")
        user3 = users_factories.UserFactory(isActive=False, suspensionReason="User not cool")
        actor = users_factories.AdminFactory()

        users_api.bulk_unsuspend_account([user1.id, user2.id, user3.id], actor)

        for user in [user1, user2, user3]:
            assert not user.suspensionReason
            assert user.isActive


@pytest.mark.usefixtures("db_session")
class ChangeUserEmailTest:
    @freeze_time("2020-10-15 09:00:00")
    def test_change_user_email(self):
        # Given
        user = users_factories.UserFactory(email="oldemail@mail.com", firstName="UniqueNameForEmailChangeTest")
        users_factories.UserSessionFactory(user=user)
        expiration_date = datetime.now() + timedelta(hours=1)
        token_payload = dict(current_email="oldemail@mail.com", new_email="newemail@mail.com")
        token = encode_jwt_payload(token_payload, expiration_date)

        # When
        users_api.change_user_email(token)

        # Then
        assert user.email == "newemail@mail.com"
        new_user = User.query.filter_by(email="newemail@mail.com").first()
        assert new_user is not None
        assert new_user.firstName == "UniqueNameForEmailChangeTest"
        old_user = User.query.filter_by(email="oldemail@mail.com").first()
        assert old_user is None
        assert UserSession.query.filter_by(userId=user.id).first() is None

    def test_change_user_email_undecodable_token(self):
        # Given
        users_factories.UserFactory(email="oldemail@mail.com", firstName="UniqueNameForEmailChangeTest")
        token = "wtftokenwhatareyoutryingtodo"

        # When
        with pytest.raises(jwt.exceptions.InvalidTokenError):
            users_api.change_user_email(token)

        # Then
        old_user = User.query.filter_by(email="oldemail@mail.com").first()
        assert old_user is not None
        new_user = User.query.filter_by(email="newemail@mail.com").first()
        assert new_user is None

    @freeze_time("2020-10-15 09:00:00")
    def test_change_user_email_expired_token(self):
        # Given
        users_factories.UserFactory(email="oldemail@mail.com", firstName="UniqueNameForEmailChangeTest")
        expiration_date = datetime.now() - timedelta(hours=1)
        token_payload = dict(current_email="oldemail@mail.com", new_email="newemail@mail.com")
        token = encode_jwt_payload(token_payload, expiration_date)

        # When
        with pytest.raises(jwt.exceptions.InvalidTokenError):
            users_api.change_user_email(token)

        # Then
        old_user = User.query.filter_by(email="oldemail@mail.com").first()
        assert old_user is not None
        new_user = User.query.filter_by(email="newemail@mail.com").first()
        assert new_user is None

    @freeze_time("2020-10-15 09:00:00")
    def test_change_user_email_missing_argument_in_token(self):
        # Given
        users_factories.UserFactory(email="oldemail@mail.com", firstName="UniqueNameForEmailChangeTest")
        expiration_date = datetime.now() + timedelta(hours=1)
        missing_current_email_token_payload = dict(new_email="newemail@mail.com")
        missing_current_email_token = encode_jwt_payload(missing_current_email_token_payload, expiration_date)

        missing_new_email_token_payload = dict(current_email="oldemail@mail.com")
        missing_new_email_token = encode_jwt_payload(missing_new_email_token_payload, expiration_date)

        missing_exp_token_payload = dict(new_email="newemail@mail.com")
        missing_exp_token = encode_jwt_payload(missing_exp_token_payload)

        # When
        with pytest.raises(jwt.exceptions.InvalidTokenError):
            users_api.change_user_email(missing_current_email_token)
            users_api.change_user_email(missing_new_email_token)
            users_api.change_user_email(missing_exp_token)

        # Then
        old_user = User.query.filter_by(email="oldemail@mail.com").first()
        assert old_user is not None
        new_user = User.query.filter_by(email="newemail@mail.com").first()
        assert new_user is None

    @freeze_time("2020-10-15 09:00:00")
    def test_change_user_email_new_email_already_existing(self):
        # Given
        users_factories.UserFactory(email="newemail@mail.com", firstName="UniqueNameForEmailChangeTest")
        expiration_date = datetime.now() + timedelta(hours=1)
        token_payload = dict(current_email="oldemail@mail.com", new_email="newemail@mail.com")
        token = encode_jwt_payload(token_payload, expiration_date)

        # When
        users_api.change_user_email(token)

        # Then
        old_user = User.query.filter_by(email="oldemail@mail.com").first()
        assert old_user is None
        new_user = User.query.filter_by(email="newemail@mail.com").first()
        assert new_user is not None

    @freeze_time("2020-10-15 09:00:00")
    def test_change_user_email_current_email_not_existing_anymore(self):
        # Given
        expiration_date = datetime.now() + timedelta(hours=1)
        token_payload = dict(current_email="oldemail@mail.com", new_email="newemail@mail.com")
        token = encode_jwt_payload(token_payload, expiration_date)

        # When
        users_api.change_user_email(token)

        # Then
        old_user = User.query.filter_by(email="oldemail@mail.com").first()
        assert old_user is None
        new_user = User.query.filter_by(email="newemail@mail.com").first()
        assert new_user is None


class CreateBeneficiaryTest:
    AGE18_ELIGIBLE_BIRTH_DATE = datetime.now() - relativedelta(years=18, months=4)

    def test_with_eligible_user(self):
        user = users_factories.UserFactory(roles=[], dateOfBirth=self.AGE18_ELIGIBLE_BIRTH_DATE)
        user = subscription_api.activate_beneficiary(user, "test")
        assert user.has_beneficiary_role
        assert len(user.deposits) == 1

    def test_apps_flyer_called(self):
        apps_flyer_data = {"apps_flyer": {"user": "some-user-id", "platform": "ANDROID"}}
        user = users_factories.UserFactory(dateOfBirth=self.AGE18_ELIGIBLE_BIRTH_DATE, externalIds=apps_flyer_data)

        expected = {
            "customer_user_id": str(user.id),
            "appsflyer_id": "some-user-id",
            "eventName": "af_complete_beneficiary_registration",
            "eventValue": {"af_user_id": str(user.id)},
        }

        with requests_mock.Mocker() as mock:
            posted = mock.post("https://api2.appsflyer.com/inappevent/app.passculture.webapp")
            user = subscription_api.activate_beneficiary(user, "test")

            assert posted.last_request.json() == expected

            assert user.has_beneficiary_role
            assert len(user.deposits) == 1

    def test_external_users_updated(self):
        user = users_factories.UserFactory(roles=[], dateOfBirth=self.AGE18_ELIGIBLE_BIRTH_DATE)
        subscription_api.activate_beneficiary(user, "test")

        assert len(batch_testing.requests) == 1
        assert len(sendinblue_testing.sendinblue_requests) == 1


class StepsToBecomeBeneficiaryTest:
    AGE18_ELIGIBLE_BIRTH_DATE = datetime.now() - relativedelta(years=18, months=4)

    def eligible_user(self, validate_phone: bool):
        phone_validation_status = PhoneValidationStatusType.VALIDATED if validate_phone else None
        return users_factories.UserFactory(
            dateOfBirth=self.AGE18_ELIGIBLE_BIRTH_DATE, phoneValidationStatus=phone_validation_status
        )

    def set_beneficiary_import(self, user, status: str = ImportStatus.CREATED) -> BeneficiaryImport:
        beneficiary_import = BeneficiaryImportFactory(beneficiary=user, source=BeneficiaryImportSources.jouve)
        beneficiary_import.setStatus(status, author=user)

        return beneficiary_import

    def test_no_missing_step(self):
        user = self.eligible_user(validate_phone=True)

        beneficiary_import = BeneficiaryImportFactory(
            applicationId=0, beneficiary=user, source=BeneficiaryImportSources.jouve.value
        )
        beneficiary_import.setStatus(ImportStatus.CREATED, author=user)
        user.hasCompletedIdCheck = True

        assert steps_to_become_beneficiary(user) == []

    @override_features(FORCE_PHONE_VALIDATION=True)
    def test_missing_step(self):
        user = self.eligible_user(validate_phone=False)

        beneficiary_import = BeneficiaryImportFactory(beneficiary=user)
        beneficiary_import.setStatus(ImportStatus.CREATED, author=user)
        user.hasCompletedIdCheck = True

        assert steps_to_become_beneficiary(user) == [BeneficiaryValidationStep.PHONE_VALIDATION]
        assert not user.has_beneficiary_role

    @override_features(FORCE_PHONE_VALIDATION=True)
    def test_rejected_import(self):
        user = self.eligible_user(validate_phone=False)

        beneficiary_import = BeneficiaryImportFactory(beneficiary=user)
        beneficiary_import.setStatus(ImportStatus.REJECTED, author=user)

        expected = [
            BeneficiaryValidationStep.PHONE_VALIDATION,
            BeneficiaryValidationStep.ID_CHECK,
            BeneficiaryValidationStep.BENEFICIARY_INFORMATION,
        ]
        assert steps_to_become_beneficiary(user) == expected
        assert not user.has_beneficiary_role

    @override_features(FORCE_PHONE_VALIDATION=True)
    def test_missing_all(self):
        user = self.eligible_user(validate_phone=False)

        expected = [
            BeneficiaryValidationStep.PHONE_VALIDATION,
            BeneficiaryValidationStep.ID_CHECK,
            BeneficiaryValidationStep.BENEFICIARY_INFORMATION,
        ]
        assert steps_to_become_beneficiary(user) == expected
        assert not user.has_beneficiary_role


class FulfillBeneficiaryDataTest:
    AGE18_ELIGIBLE_BIRTH_DATE = datetime.now() - relativedelta(years=18, months=4)

    def test_fill_user_with_password_token_and_deposit(self):
        # given
        user = users_factories.UserFactory(dateOfBirth=self.AGE18_ELIGIBLE_BIRTH_DATE)

        # when
        user = fulfill_beneficiary_data(user, "deposit_source", None)

        # then
        assert isinstance(user, User)
        assert user.password is not None
        assert len(user.deposits) == 1

    def test_fill_user_with_specific_deposit_version(self):
        # given
        user = users_factories.UserFactory(dateOfBirth=self.AGE18_ELIGIBLE_BIRTH_DATE)

        # when
        user = fulfill_beneficiary_data(user, "deposit_source", 2)

        # then
        assert isinstance(user, User)
        assert user.password is not None
        assert len(user.deposits) == 1
        assert user.deposit_version == 2


class FulfillAccountPasswordTest:
    def test_fill_user_with_password_token(self):
        # given
        user = User()

        # when
        user = fulfill_account_password(user)

        # then
        assert isinstance(user, User)
        assert user.password is not None
        assert len(user.deposits) == 0


class SetOffererDepartementCodeTest:
    def should_set_user_department_to_undefined_department_code_when_offerer_has_none(self):
        # Given
        new_user = users_factories.ProFactory.build()
        offerer = create_offerer(postal_code=None)

        # When
        updated_user = _set_offerer_departement_code(new_user, offerer)

        # Then
        assert updated_user.departementCode == None

    def should_set_user_department_code_based_on_offerer(self):
        # Given
        new_user = users_factories.ProFactory.build()
        offerer = create_offerer(postal_code="75019")

        # When
        updated_user = _set_offerer_departement_code(new_user, offerer)

        # Then
        assert updated_user.departementCode == "75"


@pytest.mark.usefixtures("db_session")
class SetProTutoAsSeenTest:
    def should_set_has_seen_pro_tutorials_to_true_for_user(self):
        # Given
        user = users_factories.UserFactory(hasSeenProTutorials=False)

        # When
        set_pro_tuto_as_seen(user)

        # Then
        assert User.query.one().hasSeenProTutorials == True


@pytest.mark.usefixtures("db_session")
class UpdateUserInfoTest:
    def test_update_user_info(self):
        user = users_factories.UserFactory(email="initial@example.com")

        users_api.update_user_info(user, public_name="New Name")
        user = User.query.one()
        assert user.email == "initial@example.com"
        assert user.publicName == "New Name"

        users_api.update_user_info(user, email="new@example.com")
        user = User.query.one()
        assert user.email == "new@example.com"
        assert user.publicName == "New Name"

    def test_update_user_info_sanitizes_email(self):
        user = users_factories.UserFactory(email="initial@example.com")

        users_api.update_user_info(user, email="  NEW@example.com   ")
        user = User.query.one()
        assert user.email == "new@example.com"


@pytest.mark.usefixtures("db_session")
class DomainsCreditTest:
    def test_get_domains_credit_v1(self):
        user = users_factories.BeneficiaryGrant18Factory(deposit__version=1)

        # booking only in all domains
        bookings_factories.IndividualBookingFactory(
            individualBooking__user=user,
            amount=50,
            stock__offer__subcategoryId=subcategories.SEANCE_CINE.id,
        )
        bookings_factories.IndividualBookingFactory(
            individualBooking__user=user,
            amount=5,
            stock__offer__subcategoryId=subcategories.SEANCE_CINE.id,
        )

        # booking in digital domain
        bookings_factories.IndividualBookingFactory(
            individualBooking__user=user,
            amount=80,
            stock__offer__subcategoryId=subcategories.JEU_EN_LIGNE.id,
            stock__offer__url="http://on.line",
        )

        # booking in physical domain
        bookings_factories.IndividualBookingFactory(
            individualBooking__user=user,
            amount=150,
            stock__offer__subcategoryId=subcategories.JEU_SUPPORT_PHYSIQUE.id,
        )

        # cancelled booking
        bookings_factories.CancelledIndividualBookingFactory(
            individualBooking__user=user,
            amount=150,
            stock__offer__subcategoryId=subcategories.JEU_SUPPORT_PHYSIQUE.id,
        )

        assert get_domains_credit(user) == DomainsCredit(
            all=Credit(initial=Decimal(500), remaining=Decimal(215)),
            digital=Credit(initial=Decimal(200), remaining=Decimal(120)),
            physical=Credit(initial=Decimal(200), remaining=Decimal(50)),
        )

    def test_get_domains_credit(self):
        user = users_factories.BeneficiaryGrant18Factory()

        # booking in physical domain
        bookings_factories.IndividualBookingFactory(
            individualBooking__user=user,
            amount=250,
            stock__offer__subcategoryId=subcategories.JEU_SUPPORT_PHYSIQUE.id,
        )

        assert get_domains_credit(user) == DomainsCredit(
            all=Credit(initial=Decimal(300), remaining=Decimal(50)),
            digital=Credit(initial=Decimal(100), remaining=Decimal(50)),
            physical=None,
        )

    def test_get_domains_credit_deposit_expired(self):
        user = users_factories.BeneficiaryGrant18Factory(deposit__version=2)
        bookings_factories.IndividualBookingFactory(
            individualBooking__user=user,
            amount=250,
            stock__offer__subcategoryId=subcategories.JEU_SUPPORT_PHYSIQUE.id,
        )

        with freeze_time(datetime.now() + relativedelta(years=GRANT_18_VALIDITY_IN_YEARS, days=2)):
            assert get_domains_credit(user) == DomainsCredit(
                all=Credit(initial=Decimal(300), remaining=Decimal(0)),
                digital=Credit(initial=Decimal(100), remaining=Decimal(0)),
                physical=None,
            )

    def test_get_domains_credit_no_deposit(self):
        user = users_factories.UserFactory()

        assert not get_domains_credit(user)


@pytest.mark.usefixtures("db_session")
class UpdateBeneficiaryMandatoryInformationTest:
    def test_all_steps_to_become_beneficiary(self):
        """
        Test that the user's id check profile information are updated and that
        it becomes beneficiary (and therefore has a deposit)
        """
        AGE18_ELIGIBLE_BIRTH_DATE = datetime.now() - relativedelta(years=18, months=4)
        user = users_factories.UserFactory(
            phoneValidationStatus=PhoneValidationStatusType.VALIDATED, dateOfBirth=AGE18_ELIGIBLE_BIRTH_DATE
        )
        fraud_factories.BeneficiaryFraudResultFactory(user=user, status=fraud_models.FraudStatus.OK)
        beneficiary_import = BeneficiaryImportFactory(beneficiary=user)
        beneficiary_import.setStatus(ImportStatus.CREATED)

        new_address = f"{user.address}_test"
        new_city = f"{user.city}_test"
        update_beneficiary_mandatory_information(
            user=user,
            address=new_address,
            city=new_city,
            postal_code="93000",
            activity=user.activity,
        )

        user = User.query.get(user.id)

        assert user.address == new_address
        assert user.city == new_city

        assert user.hasCompletedIdCheck
        assert user.has_beneficiary_role
        assert user.deposit

    @override_features(FORCE_PHONE_VALIDATION=True)
    def test_missing_step_to_become_beneficiary(self):
        """
        Test that a user with no an unverified phone number does not become
        beneficiary, even if the identity document has been successfully
        imported
        """
        user = users_factories.UserFactory(
            phoneValidationStatus=None,  # missing step to become beneficiary
        )
        beneficiary_import = BeneficiaryImportFactory(beneficiary=user)
        beneficiary_import.setStatus(ImportStatus.CREATED)

        new_address = f"{user.address}_test"
        new_city = f"{user.city}_test"
        update_beneficiary_mandatory_information(
            user=user,
            address=new_address,
            city=new_city,
            postal_code="93000",
            activity=user.activity,
        )

        user = User.query.get(user.id)

        assert user.address == new_address
        assert user.city == new_city

        assert user.hasCompletedIdCheck
        assert not user.has_beneficiary_role
        assert not user.deposit

    def test_user_has_not_passed_fraud_checks(self):
        user = users_factories.UserFactory()
        users_api.update_beneficiary_mandatory_information(
            user=user,
            address=f"{user.address}_test",
            city=f"{user.city}_test",
            postal_code="93000",
            activity=user.activity,
        )
        assert not user.has_beneficiary_role
        assert not user.deposit

    def test_user_is_fraudster(self):
        user = users_factories.UserFactory()
        fraud_factories.BeneficiaryFraudResultFactory(user=user, status=fraud_models.FraudStatus.OK)
        users_api.update_beneficiary_mandatory_information(
            user=user,
            address=f"{user.address}_test",
            city=f"{user.city}_test",
            postal_code="93000",
            activity=user.activity,
        )
        assert not user.has_beneficiary_role
        assert not user.deposit


class CreateProUserTest:
    def test_create_pro_user(self):
        pro_user_creation_body = ProUserCreationBodyModel(
            email="prouser@example.com", password="P@ssword12345", phoneNumber="0666666666"
        )

        pro_user = create_pro_user(pro_user_creation_body)

        assert pro_user.email == "prouser@example.com"
        assert not pro_user.isAdmin
        assert not pro_user.needsToFillCulturalSurvey
        assert not pro_user.has_pro_role
        assert not pro_user.has_admin_role
        assert not pro_user.has_beneficiary_role
        assert pro_user.deposits == []

    @override_settings(IS_INTEGRATION=True)
    def test_create_pro_user_in_integration(self):
        pro_user_creation_body = ProUserCreationBodyModel(
            email="prouser@example.com", password="P@ssword12345", phoneNumber="0666666666"
        )

        pro_user = create_pro_user(pro_user_creation_body)

        assert pro_user.email == "prouser@example.com"
        assert not pro_user.isAdmin
        assert not pro_user.needsToFillCulturalSurvey
        assert not pro_user.has_pro_role
        assert not pro_user.has_admin_role
        assert pro_user.has_beneficiary_role
        assert pro_user.deposits != []


class AsynchronousIdentityDocumentVerificationTest:
    IMAGES_DIR = Path(tests.__path__[0]) / "files"

    @patch("pcapi.core.users.api.store_object")
    @patch("pcapi.core.users.api.random_token")
    @patch("pcapi.core.users.api.verify_identity_document")
    def test_upload_identity_document_successful(
        self,
        mocked_verify_identity_document,
        mocked_random_token,
        mocked_store_object,
        app,
    ):
        # Given
        identity_document = (self.IMAGES_DIR / "pixel.png").read_bytes()
        mocked_random_token.return_value = "a_very_random_secret"

        # When
        asynchronous_identity_document_verification(identity_document, "toto@example.com")

        # Then
        mocked_store_object.assert_called_once_with(
            "identity_documents",
            "a_very_random_secret.jpg",
            identity_document,
            content_type="image/jpeg",
            metadata={"email": "toto@example.com"},
        )
        mocked_verify_identity_document.delay.assert_called_once_with(
            VerifyIdentityDocumentRequest(image_storage_path="identity_documents/a_very_random_secret.jpg")
        )

    @patch("pcapi.core.users.api.store_object")
    def test_upload_identity_document_fails_on_upload(
        self,
        mocked_store_object,
        app,
    ):
        # Given
        mocked_store_object.side_effect = Exception
        identity_document = (self.IMAGES_DIR / "mouette_small.jpg").read_bytes()

        # Then
        with pytest.raises(IdentityDocumentUploadException):
            asynchronous_identity_document_verification(identity_document, "toto@example.com")

    @patch("pcapi.core.users.api.delete_object")
    @patch("pcapi.core.users.api.store_object")
    @patch("pcapi.core.users.api.random_token")
    @patch("pcapi.core.users.api.verify_identity_document")
    def test_cloud_task_creation_fails(
        self,
        mocked_verify_identity_document,
        mocked_random_token,
        mocked_store_object,
        mocked_delete_object,
        app,
    ):
        # Given
        identity_document = (self.IMAGES_DIR / "pixel.png").read_bytes()
        mocked_random_token.return_value = "a_very_random_secret"
        mocked_verify_identity_document.delay.side_effect = Exception

        # When
        with pytest.raises(CloudTaskCreationException):
            asynchronous_identity_document_verification(identity_document, "toto@example.com")

        # Then
        mocked_delete_object.assert_called_once_with("identity_documents/a_very_random_secret.jpg")


class VerifyIdentityDocumentInformationsTest:
    @patch("pcapi.core.users.api.delete_object")
    @patch("pcapi.core.users.api.ask_for_identity_document_verification")
    @patch("pcapi.core.users.api._get_identity_document_informations")
    def test_email_sent_when_document_is_invalid(
        self, mocked_get_identity_informations, mocked_ask_for_identity, mocked_delete_object, app, caplog
    ):
        # Given
        mocked_get_identity_informations.return_value = ("py@test.com", b"")
        mocked_ask_for_identity.return_value = (False, "invalid-document-date")

        users_api.verify_identity_document_informations("some_path")

        assert len(mails_testing.outbox) == 1
        sent_data = mails_testing.outbox[0].sent_data

        assert sent_data["Vars"]["url"] == settings.DMS_USER_URL
        assert sent_data["MJ-TemplateID"] == 2958563
        assert caplog.records[0].message == "fraud internal validation : Cannot find user with email py@test.com"

    @patch("pcapi.core.users.api.delete_object")
    @patch("pcapi.core.users.api.ask_for_identity_document_verification")
    @patch("pcapi.core.users.api._get_identity_document_informations")
    @freeze_time("2021-10-30 09:00:00")
    def test_messages_when_age_is_invalid(
        self, mocked_get_identity_informations, mocked_ask_for_identity, mocked_delete_object, app, caplog
    ):
        # Given
        user = users_factories.UserFactory()
        mocked_get_identity_informations.return_value = (user.email, b"")
        mocked_ask_for_identity.return_value = (False, "invalid-age")

        users_api.verify_identity_document_informations("some_path")

        assert subscription_models.SubscriptionMessage.query.count() == 1
        message = subscription_models.SubscriptionMessage.query.first()
        assert not message.popOverIcon
        assert (
            message.userMessage
            == "Ton dossier a été refusé : ton document indique que tu n’as pas 18 ans. Consulte l’e-mail envoyé le 30/10/2021 pour plus d’informations."
        )

    @patch("pcapi.core.users.api.delete_object")
    @patch("pcapi.core.users.api.ask_for_identity_document_verification")
    @patch("pcapi.core.users.api._get_identity_document_informations")
    @freeze_time("2021-10-30 09:00:00")
    def test_known_user_email_sent_when_document_has_invalid_date(
        self, mocked_get_identity_informations, mocked_ask_for_identity, mocked_delete_object, app
    ):
        # Given
        existing_user = users_factories.UserFactory()
        mocked_get_identity_informations.return_value = (existing_user.email, b"")
        mocked_ask_for_identity.return_value = (False, "invalid-document-date")

        users_api.verify_identity_document_informations("some_path")

        assert len(mails_testing.outbox) == 1
        sent_data = mails_testing.outbox[0].sent_data

        assert sent_data["Vars"]["url"] == settings.DMS_USER_URL
        assert sent_data["MJ-TemplateID"] == 2958563

        assert len(existing_user.beneficiaryFraudChecks) == 1
        fraud_check = existing_user.beneficiaryFraudChecks[0]
        assert fraud_check.type == fraud_models.FraudCheckType.INTERNAL_REVIEW
        assert fraud_check.resultContent["message"] == "Erreur de lecture du document : invalid-document-date"
        assert fraud_check.resultContent["source"] == fraud_models.InternalReviewSource.DOCUMENT_VALIDATION_ERROR.value

        assert subscription_models.SubscriptionMessage.query.count() == 1
        message = subscription_models.SubscriptionMessage.query.first()
        assert not message.popOverIcon
        assert (
            message.userMessage
            == "Ton dossier a été refusé : le document que tu as transmis est expiré. Consulte l’e-mail envoyé le 30/10/2021 pour plus d’informations."
        )

    @patch("pcapi.core.users.api.delete_object")
    @patch("pcapi.core.users.api.ask_for_identity_document_verification")
    @patch("pcapi.core.users.api._get_identity_document_informations")
    @freeze_time("2021-10-30 09:00:00")
    def test_known_user_email_sent_when_document_is_unreadable(
        self, mocked_get_identity_informations, mocked_ask_for_identity, mocked_delete_object, app
    ):
        # Given
        eligible_date_of_birth = datetime.combine(date.today(), time.min) - relativedelta(
            years=users_constants.ELIGIBILITY_AGE_18, months=1
        )
        existing_user = users_factories.UserFactory(dateOfBirth=eligible_date_of_birth)
        mocked_get_identity_informations.return_value = (existing_user.email, b"")
        mocked_ask_for_identity.return_value = (False, "unread-document")

        users_api.verify_identity_document_informations("some_path")

        assert len(existing_user.beneficiaryFraudChecks) == 1
        fraud_check = existing_user.beneficiaryFraudChecks[0]
        assert fraud_check.type == fraud_models.FraudCheckType.INTERNAL_REVIEW
        assert fraud_check.resultContent["message"] == "Erreur de lecture du document : unread-document"
        assert fraud_check.resultContent["source"] == fraud_models.InternalReviewSource.DOCUMENT_VALIDATION_ERROR.value

        assert subscription_models.SubscriptionMessage.query.count() == 1
        message = subscription_models.SubscriptionMessage.query.first()
        assert not message.popOverIcon
        assert (
            message.userMessage
            == "Nous n'arrivons pas à traiter ton document. Consulte l'e-mail envoyé le 30/10/2021 pour plus d'informations."
        )

    @patch("pcapi.core.users.api.delete_object")
    @patch("pcapi.core.users.api.ask_for_identity_document_verification")
    @patch("pcapi.core.users.api._get_identity_document_informations")
    @freeze_time("2021-10-30 09:00:00")
    def test_when_document_has_unread_mrz(
        self, mocked_get_identity_informations, mocked_ask_for_identity, mocked_delete_object, app
    ):
        # Given
        existing_user = users_factories.UserFactory()
        mocked_get_identity_informations.return_value = (existing_user.email, b"")
        mocked_ask_for_identity.return_value = (False, "unread-mrz-document")

        users_api.verify_identity_document_informations("some_path")

        assert len(mails_testing.outbox) == 1
        sent_data = mails_testing.outbox[0].sent_data

        assert sent_data["MJ-TemplateID"] == 3188025

        assert len(existing_user.beneficiaryFraudChecks) == 1
        fraud_check = existing_user.beneficiaryFraudChecks[0]
        assert fraud_check.type == fraud_models.FraudCheckType.INTERNAL_REVIEW
        assert fraud_check.resultContent["message"] == "Erreur de lecture du document : unread-mrz-document"
        assert fraud_check.resultContent["source"] == fraud_models.InternalReviewSource.DOCUMENT_VALIDATION_ERROR.value

        assert subscription_models.SubscriptionMessage.query.count() == 1
        message = subscription_models.SubscriptionMessage.query.first()
        assert not message.popOverIcon
        assert (
            message.userMessage
            == "Nous n'arrivons pas à traiter ton document. Consulte l'e-mail envoyé le 30/10/2021 pour plus d'informations."
        )

    @patch("pcapi.core.users.api.delete_object")
    @patch("pcapi.core.users.api.ask_for_identity_document_verification")
    @patch("pcapi.core.users.api._get_identity_document_informations")
    @freeze_time("2021-10-30 09:00:00")
    def test_known_user_email_sent_when_document_is_invalid(
        self, mocked_get_identity_informations, mocked_ask_for_identity, mocked_delete_object, app
    ):
        # Given
        existing_user = users_factories.UserFactory()
        mocked_get_identity_informations.return_value = (existing_user.email, b"")
        mocked_ask_for_identity.return_value = (False, "invalid-document")

        users_api.verify_identity_document_informations("some_path")

        assert len(mails_testing.outbox) == 1
        sent_data = mails_testing.outbox[0].sent_data

        assert sent_data["MJ-TemplateID"] == 2958584

        assert len(existing_user.beneficiaryFraudChecks) == 1
        fraud_check = existing_user.beneficiaryFraudChecks[0]
        assert fraud_check.type == fraud_models.FraudCheckType.INTERNAL_REVIEW
        assert fraud_check.resultContent["message"] == "Erreur de lecture du document : invalid-document"
        assert fraud_check.resultContent["source"] == fraud_models.InternalReviewSource.DOCUMENT_VALIDATION_ERROR.value

        assert subscription_models.SubscriptionMessage.query.count() == 1
        message = subscription_models.SubscriptionMessage.query.first()
        assert not message.popOverIcon
        assert (
            message.userMessage
            == "Ton dossier a été refusé : le document transmis est invalide. Consulte l’e-mail envoyé le 30/10/2021 pour plus d’informations."
        )

    @patch("pcapi.core.users.api.delete_object")
    @patch("pcapi.core.users.api.ask_for_identity_document_verification")
    @patch("pcapi.core.users.api._get_identity_document_informations")
    def test_email_sent_with_default_template(
        self, mocked_get_identity_informations, mocked_ask_for_identity, mocked_delete_object, app
    ):
        # Given
        mocked_get_identity_informations.return_value = ("py@test.com", b"")
        mocked_ask_for_identity.return_value = (False, "unknown-error-code")

        users_api.verify_identity_document_informations("some_path")

        assert len(mails_testing.outbox) == 1
        sent_data = mails_testing.outbox[0].sent_data

        assert sent_data["Vars"]["url"] == settings.DMS_USER_URL
        assert sent_data["MJ-TemplateID"] == 2958557  # default email template used

    @patch("pcapi.core.users.api.delete_object")
    @patch("pcapi.core.users.api.ask_for_identity_document_verification")
    @patch("pcapi.core.users.api._get_identity_document_informations")
    def test_no_email_sent_when_document_is_valid(
        self, mocked_get_identity_informations, mocked_ask_for_identity, mocked_delete_object, app
    ):
        # Given
        mocked_get_identity_informations.return_value = ("py@test.com", b"")
        mocked_ask_for_identity.return_value = (True, "registration:completed")

        users_api.verify_identity_document_informations("some_path")

        assert not mails_testing.outbox


class BeneficairyInformationUpdateTest:
    def test_update_user_information_from_dms(self):
        user = UserFactory(
            activity=None,
            address=None,
            city=None,
            departementCode=None,
            firstName=None,
            lastName=None,
            postalCode=None,
            publicName="UNSET",
        )
        dms_data = fraud_factories.DMSContentFactory()
        new_user = users_api.update_user_information_from_external_source(user, dms_data)
        assert new_user.activity == dms_data.activity
        assert new_user.address == dms_data.address
        assert new_user.departementCode == dms_data.department
        assert new_user.postalCode == dms_data.postal_code
        assert new_user.firstName == dms_data.first_name
        assert new_user.lastName == dms_data.last_name

    def test_update_user_information_from_jouve(self):
        user = UserFactory(
            activity=None,
            address=None,
            city=None,
            departementCode=None,
            firstName=None,
            lastName=None,
            postalCode=None,
            publicName="UNSET",
        )
        jouve_data = fraud_factories.JouveContentFactory()
        new_user = users_api.update_user_information_from_external_source(user, jouve_data)

        assert new_user.activity == jouve_data.activity
        assert new_user.address == jouve_data.address
        assert new_user.city == jouve_data.city
        assert new_user.firstName == jouve_data.firstName
        assert new_user.lastName == jouve_data.lastName

    def test_update_user_information_from_educonnect(self):
        user = UserFactory(
            firstName=None,
            lastName=None,
        )
        educonnect_data = fraud_factories.EduconnectContentFactory(
            first_name="Raoul",
            last_name="Dufy",
            birth_date=date(2000, 5, 1),
            ine_hash="identifiantnati0naleleve",
        )
        new_user = users_api.update_user_information_from_external_source(user, educonnect_data)

        assert new_user.firstName == "Raoul"
        assert new_user.lastName == "Dufy"
        assert new_user.dateOfBirth == datetime(2000, 5, 1, 0, 0)
        assert new_user.ineHash == "identifiantnati0naleleve"

    def test_update_user_information_from_jouve_empty_source(self):
        user = UserFactory(activity="Etudiant", postalCode="75001")
        jouve_data = fraud_factories.JouveContentFactory(
            activity=None,
            address=None,
            city=None,
            departementCode=None,
            firstName=None,
            lastName=None,
            postalCode=None,
        )
        new_user = users_api.update_user_information_from_external_source(user, jouve_data)

        assert new_user.activity is not None
        assert new_user.address is not None
        assert new_user.city is not None
        assert new_user.firstName is not None
        assert new_user.lastName is not None

    def test_update_id_piece_number(self):
        user = UserFactory(activity="Etudiant", postalCode="75001", idPieceNumber=None)
        jouve_data = fraud_factories.JouveContentFactory(bodyPieceNumber="140767100016")

        users_api.update_user_information_from_external_source(user, jouve_data)
        assert user.idPieceNumber == "140767100016"

    def test_update_id_piece_number_duplicate(self):
        user = UserFactory(activity="Etudiant", postalCode="75001", idPieceNumber="140767100016")
        jouve_data = fraud_factories.JouveContentFactory(bodyPieceNumber=user.idPieceNumber)
        new_user = UserFactory(activity="Etudiant", postalCode="75001", idPieceNumber=None)

        users_api.update_user_information_from_external_source(user, jouve_data)
        assert new_user.idPieceNumber is None

    def test_update_id_piece_number_invalid_format(self):
        user = UserFactory(activity="Etudiant", postalCode="75001", idPieceNumber=None)
        jouve_data = fraud_factories.JouveContentFactory(bodyPieceNumber="ITT T TITITT")
        users_api.update_user_information_from_external_source(user, jouve_data)
        assert user.idPieceNumber is None

    def test_update_postal_code_from_empty_value(self):
        # when jouve sends the value, and it has not been updated from elsewhere we want to update it
        user = UserFactory(postalCode=None)
        jouve_data = fraud_factories.JouveContentFactory(postalCode="22620")
        users_api.update_user_information_from_external_source(user, jouve_data)

        assert user.postalCode == jouve_data.postalCode

    def test_postal_code_not_updated(self):
        # when jouve sends the value, and it has not been updated from elsewhere we want to update it
        user = UserFactory(postalCode="75009")
        jouve_data = fraud_factories.JouveContentFactory()
        users_api.update_user_information_from_external_source(user, jouve_data)

        assert user.postalCode != jouve_data.postalCode

    @override_features(ENABLE_PHONE_VALIDATION=True)
    def test_phone_number_does_not_update_from_jouve(self):

        user = UserFactory(phoneNumber="+33611111111")
        jouve_data = fraud_factories.JouveContentFactory(phoneNumber="+33622222222")

        users_api.update_user_information_from_external_source(user, jouve_data)

        assert user.phoneNumber == "+33611111111"

    @override_features(ENABLE_PHONE_VALIDATION=False)
    def test_phone_number_update_from_jouve_if_empty(self):

        user = UserFactory(phoneNumber=None)
        jouve_data = fraud_factories.JouveContentFactory(phoneNumber="+33622222222")

        users_api.update_user_information_from_external_source(user, jouve_data)

        assert user.phoneNumber == "+33622222222"

    @override_features(ENABLE_PHONE_VALIDATION=False)
    def test_phone_number_does_not_update_from_jouve_if_not_empty(self):

        user = UserFactory(phoneNumber="+33611111111")
        jouve_data = fraud_factories.JouveContentFactory(phoneNumber="+33622222222")

        users_api.update_user_information_from_external_source(user, jouve_data)

        assert user.phoneNumber == "+33611111111"


class UpdateUserLastConnectionDateTest:
    @freeze_time("2021-9-20 11:11:11")
    def test_first_update(self):
        user = UserFactory()

        users_api.update_last_connection_date(user)

        db.session.refresh(user)

        assert user.lastConnectionDate == datetime(2021, 9, 20, 11, 11, 11)
        assert len(sendinblue_testing.sendinblue_requests) == 1

    @freeze_time("2021-9-20 01:11:11")
    def test_update_day_after(self):
        user = UserFactory(lastConnectionDate=datetime(2021, 9, 19, 23, 00, 11))

        users_api.update_last_connection_date(user)

        db.session.refresh(user)

        assert user.lastConnectionDate == datetime(2021, 9, 20, 1, 11, 11)
        assert len(sendinblue_testing.sendinblue_requests) == 1

    @freeze_time("2021-9-20 11:11:11")
    def test_update_same_day(self):
        user = UserFactory(lastConnectionDate=datetime(2021, 9, 20, 9, 0))

        users_api.update_last_connection_date(user)

        db.session.refresh(user)

        assert user.lastConnectionDate == datetime(2021, 9, 20, 11, 11, 11)
        assert len(sendinblue_testing.sendinblue_requests) == 0

    @freeze_time("2021-9-20 11:11:11")
    def test_no_update(self):
        user = UserFactory(lastConnectionDate=datetime(2021, 9, 20, 11, 00, 11))

        users_api.update_last_connection_date(user)

        db.session.refresh(user)

        assert user.lastConnectionDate == datetime(2021, 9, 20, 11, 00, 11)
        assert len(sendinblue_testing.sendinblue_requests) == 0
