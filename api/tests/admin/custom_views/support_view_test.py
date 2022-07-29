from datetime import datetime
import logging
from unittest.mock import patch

from dateutil.relativedelta import relativedelta
import freezegun
import pytest

from pcapi.admin.custom_views.support_view.api import BeneficiaryActivationStatus
from pcapi.admin.custom_views.support_view.api import get_beneficiary_activation_status
import pcapi.core.fraud.factories as fraud_factories
import pcapi.core.fraud.models as fraud_models
import pcapi.core.fraud.ubble.models as ubble_models
from pcapi.core.subscription import models as subscription_models
from pcapi.core.testing import override_features
from pcapi.core.testing import override_settings
import pcapi.core.users.factories as users_factories
import pcapi.core.users.models as users_models


AGE18_ELIGIBLE_BIRTH_DATE = datetime.utcnow() - relativedelta(years=18, months=4)


@pytest.mark.usefixtures("db_session")
class BeneficiaryListViewTest:
    def test_list_view(self, client):
        admin = users_factories.AdminFactory(email="admin@example.com")
        client.with_session_auth(admin.email)

        for review_status in fraud_models.FraudReviewStatus:
            user = users_factories.UserFactory(civility="M.")
            fraud_factories.BeneficiaryFraudCheckFactory(user=user)
            fraud_factories.BeneficiaryFraudReviewFactory(user=user, review=review_status)
        response = client.get(f"/pc/back-office/support_beneficiary/?search={user.id}")
        assert response.status_code == 200


@pytest.mark.usefixtures("db_session")
class BeneficiaryDetailViewTest:
    def test_detail_view(self, client):
        admin = users_factories.AdminFactory(email="admin@example.com")
        user = users_factories.UserFactory()
        fraud_factories.BeneficiaryFraudCheckFactory(user=user)
        client.with_session_auth(admin.email)
        response = client.get("/pc/back-office/support_beneficiary/?id={user.id}")
        assert response.status_code == 200

    def test_detail_view_with_new_fraud_error_reason_codes(self, client):
        admin = users_factories.AdminFactory(email="admin@example.com")
        user = users_factories.UserFactory()
        fraud_factories.BeneficiaryFraudCheckFactory(
            user=user,
            reasonCodes=[
                fraud_models.FraudReasonCode.DUPLICATE_ID_PIECE_NUMBER,
                fraud_models.FraudReasonCode.DUPLICATE_INE,
            ],
        )
        client.with_session_auth(admin.email)
        response = client.get("/pc/back-office/support_beneficiary/?id={user.id}")
        assert response.status_code == 200


@pytest.mark.usefixtures("db_session")
class BeneficiaryValidationViewTest:
    @override_features(BENEFICIARY_VALIDATION_AFTER_FRAUD_CHECKS=True)
    def test_validation_view_auth_required(self, client):
        user = users_factories.UserFactory()
        response = client.post(f"/pc/back-office/support_beneficiary/validate/beneficiary/{user.id}")
        assert response.status_code == 302
        assert response.headers["Location"] == "http://localhost/pc/back-office/"

    @override_features(BENEFICIARY_VALIDATION_AFTER_FRAUD_CHECKS=True)
    def test_override_validation_for_fraud_check_is_ko(self, client):
        user = users_factories.UserFactory(dateOfBirth=datetime.utcnow() - relativedelta(years=18, months=2))
        check = fraud_factories.BeneficiaryFraudCheckFactory(
            user=user, type=fraud_models.FraudCheckType.DMS, status=fraud_models.FraudCheckStatus.KO
        )
        admin = users_factories.AdminFactory()
        client.with_session_auth(admin.email)

        response = client.post(
            f"/pc/back-office/support_beneficiary/validate/beneficiary/{user.id}",
            form={"user_id": user.id, "reason": "User is granted", "review": "OK", "eligibility": "Par défaut"},
        )
        assert response.status_code == 302
        review = fraud_models.BeneficiaryFraudReview.query.filter_by(user=user, author=admin).first()
        assert review.review == fraud_models.FraudReviewStatus.OK
        assert review.reason == "User is granted"
        user = users_models.User.query.get(user.id)
        assert user.has_beneficiary_role is True

        dms_content = fraud_models.DMSContent(**check.resultContent)
        assert user.firstName == dms_content.first_name
        assert user.lastName == dms_content.last_name
        assert user.idPieceNumber == dms_content.id_piece_number

        fraud_check = fraud_models.BeneficiaryFraudCheck.query.filter_by(user=user).first()
        assert fraud_check.status == check.status

    @override_features(BENEFICIARY_VALIDATION_AFTER_FRAUD_CHECKS=True)
    def test_validation_view_validate_user_from_dms_data_staging(self, client):
        user = users_factories.UserFactory(dateOfBirth=datetime.utcnow() - relativedelta(years=18, months=2))
        check = fraud_factories.BeneficiaryFraudCheckFactory(user=user, type=fraud_models.FraudCheckType.DMS)
        admin = users_factories.AdminFactory()
        client.with_session_auth(admin.email)

        response = client.post(
            f"/pc/back-office/support_beneficiary/validate/beneficiary/{user.id}",
            form={"user_id": user.id, "reason": "User is granted", "review": "OK", "eligibility": "Par défaut"},
        )
        assert response.status_code == 302
        review = fraud_models.BeneficiaryFraudReview.query.filter_by(user=user, author=admin).first()
        assert review.review == fraud_models.FraudReviewStatus.OK
        assert review.reason == "User is granted"
        user = users_models.User.query.get(user.id)
        assert user.has_beneficiary_role is True
        assert len(user.deposits) == 1

        dms_content = fraud_models.DMSContent(**check.resultContent)
        assert user.firstName == dms_content.first_name
        assert user.lastName == dms_content.last_name
        assert user.idPieceNumber == dms_content.id_piece_number

    @override_features(BENEFICIARY_VALIDATION_AFTER_FRAUD_CHECKS=True)
    def test_validation_view_validate_user_from_educonnect(self, client):
        user = users_factories.UserFactory(dateOfBirth=datetime.utcnow() - relativedelta(years=15, months=2))
        check = fraud_factories.BeneficiaryFraudCheckFactory(
            user=user,
            type=fraud_models.FraudCheckType.EDUCONNECT,
            eligibilityType=users_models.EligibilityType.UNDERAGE,
        )
        admin = users_factories.AdminFactory()
        client.with_session_auth(admin.email)

        response = client.post(
            f"/pc/back-office/support_beneficiary/validate/beneficiary/{user.id}",
            form={"user_id": user.id, "reason": "User is granted", "review": "OK", "eligibility": "Par défaut"},
        )
        assert response.status_code == 302

        review = fraud_models.BeneficiaryFraudReview.query.filter_by(user=user, author=admin).one()
        assert review.review == fraud_models.FraudReviewStatus.OK
        assert review.reason == "User is granted"
        user = users_models.User.query.get(user.id)
        assert user.has_underage_beneficiary_role
        assert len(user.deposits) == 1

        educonnect_content = fraud_models.EduconnectContent(**check.resultContent)
        assert user.firstName == educonnect_content.get_first_name()
        assert user.lastName == educonnect_content.get_last_name()
        assert user.idPieceNumber == educonnect_content.get_id_piece_number()

    @override_features(BENEFICIARY_VALIDATION_AFTER_FRAUD_CHECKS=True)
    def test_validation_view_validate_user_from_ubble(self, client):
        user = users_factories.UserFactory(dateOfBirth=datetime.utcnow() - relativedelta(years=18, months=2))
        check = fraud_factories.BeneficiaryFraudCheckFactory(user=user, type=fraud_models.FraudCheckType.UBBLE)
        admin = users_factories.AdminFactory()
        client.with_session_auth(admin.email)

        response = client.post(
            f"/pc/back-office/support_beneficiary/validate/beneficiary/{user.id}",
            form={"user_id": user.id, "reason": "User is granted", "review": "OK", "eligibility": "Par défaut"},
        )
        assert response.status_code == 302

        review = fraud_models.BeneficiaryFraudReview.query.filter_by(user=user, author=admin).one()
        assert review.review == fraud_models.FraudReviewStatus.OK
        assert review.reason == "User is granted"
        user = users_models.User.query.get(user.id)
        assert user.has_beneficiary_role
        assert len(user.deposits) == 1

        ubble_content = fraud_models.ubble_fraud_models.UbbleContent(**check.resultContent)
        assert user.firstName == ubble_content.get_first_name()
        assert user.lastName == ubble_content.get_last_name()
        assert user.idPieceNumber == ubble_content.get_id_piece_number()

    @override_features(BENEFICIARY_VALIDATION_AFTER_FRAUD_CHECKS=True)
    @patch("flask.flash")
    def test_ine_hash_duplicate(self, flash_mock, client):
        other_user_with_same_ine = users_factories.UserFactory(ineHash="shotgun")
        user = users_factories.UserFactory(dateOfBirth=datetime.utcnow() - relativedelta(years=15, months=2))
        fraud_factories.BeneficiaryFraudCheckFactory(
            user=user,
            type=fraud_models.FraudCheckType.EDUCONNECT,
            eligibilityType=users_models.EligibilityType.UNDERAGE,
            resultContent=fraud_factories.EduconnectContentFactory(ine_hash="shotgun"),
        )
        admin = users_factories.AdminFactory()
        client.with_session_auth(admin.email)

        response = client.post(
            f"/pc/back-office/support_beneficiary/validate/beneficiary/{user.id}",
            form={"user_id": user.id, "reason": "User is granted", "review": "OK", "eligibility": "Par défaut"},
        )
        assert response.status_code == 302

        assert not user.has_underage_beneficiary_role
        assert len(user.deposits) == 0
        flash_mock.assert_called_once_with(
            f"Le numéro INE shotgun est déjà utilisé par l'utilisateur {other_user_with_same_ine.id}", "error"
        )

    @override_features(BENEFICIARY_VALIDATION_AFTER_FRAUD_CHECKS=True)
    @patch("flask.flash")
    def test_id_piece_number_duplicate(self, flash_mock, client):
        other_user_with_same_id = users_factories.UserFactory(idPieceNumber="123456")
        user = users_factories.UserFactory(dateOfBirth=datetime.utcnow() - relativedelta(years=15, months=2))
        fraud_factories.BeneficiaryFraudCheckFactory(
            user=user,
            type=fraud_models.FraudCheckType.DMS,
            eligibilityType=users_models.EligibilityType.UNDERAGE,
            resultContent=fraud_factories.DMSContentFactory(id_piece_number="123456"),
        )
        admin = users_factories.AdminFactory()
        client.with_session_auth(admin.email)

        response = client.post(
            f"/pc/back-office/support_beneficiary/validate/beneficiary/{user.id}",
            form={"user_id": user.id, "reason": "User is granted", "review": "OK", "eligibility": "Par défaut"},
        )
        assert response.status_code == 302

        assert not user.has_underage_beneficiary_role
        assert len(user.deposits) == 0
        flash_mock.assert_called_once_with(
            f"Le numéro de CNI 123456 est déjà utilisé par l'utilisateur {other_user_with_same_id.id}", "error"
        )

    @patch("flask.flash")
    @override_features(BENEFICIARY_VALIDATION_AFTER_FRAUD_CHECKS=True)
    def test_validation_view_no_age_found(self, flash_mock, client):
        birth_date_15_yo = datetime.utcnow() - relativedelta(years=15, months=2)
        user = users_factories.UserFactory(dateOfBirth=birth_date_15_yo)
        fraud_factories.BeneficiaryFraudCheckFactory(
            user=user,
            type=fraud_models.FraudCheckType.UBBLE,
            eligibilityType=None,
            resultContent=fraud_factories.UbbleContentFactory(birth_date=birth_date_15_yo.date().isoformat()),
        )
        admin = users_factories.AdminFactory()
        client.with_session_auth(admin.email)

        response = client.post(
            f"/pc/back-office/support_beneficiary/validate/beneficiary/{user.id}",
            form={"user_id": user.id, "reason": "User is granted", "review": "OK", "eligibility": "Par défaut"},
        )
        assert response.status_code == 302

        assert user.deposit is None
        flash_mock.assert_called_once_with("L'âge de l'utilisateur à l'inscription n'a pas pu être déterminé", "error")

    @override_features(BENEFICIARY_VALIDATION_AFTER_FRAUD_CHECKS=True)
    def test_validation_view_validate_user_wrong_args(self, client):
        user = users_factories.UserFactory()
        admin = users_factories.AdminFactory()

        client.with_session_auth(admin.email)

        response = client.post(
            f"/pc/back-office/support_beneficiary/validate/beneficiary/{user.id}",
            form={"user_id": user.id, "badkey": "User is granted", "review": "OK", "eligibility": "Par défaut"},
        )
        assert response.status_code == 302
        review = fraud_models.BeneficiaryFraudReview.query.filter_by(user=user, author=admin).one_or_none()
        assert review is None

        user = users_models.User.query.get(user.id)
        assert user.has_beneficiary_role is False
        assert user.deposits == []

    @override_features(BENEFICIARY_VALIDATION_AFTER_FRAUD_CHECKS=True)
    def test_validation_view_validate_user_already_reviewed(self, client):
        user = users_factories.UserFactory()
        admin = users_factories.AdminFactory()
        expected_review = fraud_factories.BeneficiaryFraudReviewFactory(user=user, author=admin)
        client.with_session_auth(admin.email)

        response = client.post(
            f"/pc/back-office/support_beneficiary/validate/beneficiary/{user.id}",
            form={"user_id": user.id, "reason": "User is granted", "review": "OK"},
        )
        assert response.status_code == 302
        review = fraud_models.BeneficiaryFraudReview.query.filter_by(user=user, author=admin).one()
        assert review.reason == expected_review.reason

    @override_features(BENEFICIARY_VALIDATION_AFTER_FRAUD_CHECKS=True)
    def test_validation_view_validate_not_super_user_fails(self, client):
        user = users_factories.UserFactory()
        admin = users_factories.AdminFactory()
        client.with_session_auth(admin.email)

        with override_settings(IS_PROD=True):
            response = client.post(
                f"/pc/back-office/support_beneficiary/validate/beneficiary/{user.id}",
                form={"user_id": user.id, "reason": "User is granted", "review": "OK", "eligibility": "Par défaut"},
            )
        assert response.status_code == 302
        review = fraud_models.BeneficiaryFraudReview.query.filter_by(user=user, author=admin).one_or_none()
        assert review is None
        assert user.has_beneficiary_role is False

    @override_features(BENEFICIARY_VALIDATION_AFTER_FRAUD_CHECKS=True)
    def test_validation_prod_requires_super_admin(self, client):
        user = users_factories.UserFactory()
        check = fraud_factories.BeneficiaryFraudCheckFactory(user=user, type=fraud_models.FraudCheckType.UBBLE)
        admin = users_factories.AdminFactory()
        client.with_session_auth(admin.email)

        with override_settings(IS_PROD=True, SUPER_ADMIN_EMAIL_ADDRESSES=[admin.email]):
            response = client.post(
                f"/pc/back-office/support_beneficiary/validate/beneficiary/{user.id}",
                form={"user_id": user.id, "reason": "User is granted", "review": "OK", "eligibility": "Par défaut"},
            )
        assert response.status_code == 302
        review = fraud_models.BeneficiaryFraudReview.query.filter_by(user=user, author=admin).one_or_none()
        assert review is not None
        assert review.author == admin
        assert user.has_beneficiary_role is True

        ubble_content = ubble_models.UbbleContent(**check.resultContent)
        assert user.firstName == ubble_content.get_first_name()
        assert user.lastName == ubble_content.get_last_name()

    def test_review_ko_does_not_activate_the_beneficiary(self, client):
        user = users_factories.UserFactory()
        fraud_factories.BeneficiaryFraudCheckFactory(user=user, type=fraud_models.FraudCheckType.UBBLE)
        admin = users_factories.AdminFactory()
        client.with_session_auth(admin.email)

        with override_settings(IS_PROD=True, SUPER_ADMIN_EMAIL_ADDRESSES=[admin.email]):
            response = client.post(
                f"/pc/back-office/support_beneficiary/validate/beneficiary/{user.id}",
                form={"user_id": user.id, "reason": "User is denied", "review": "KO", "eligibility": "Par défaut"},
            )
        assert response.status_code == 302
        review = fraud_models.BeneficiaryFraudReview.query.filter_by(user=user, author=admin).one_or_none()
        assert review is not None
        assert review.author == admin
        assert review.review == fraud_models.FraudReviewStatus.KO
        assert user.has_beneficiary_role is False

        assert subscription_models.SubscriptionMessage.query.count() == 1
        message = subscription_models.SubscriptionMessage.query.first()
        assert message.popOverIcon == subscription_models.PopOverIcon.ERROR
        assert message.userMessage == "Ton dossier a été rejeté. Tu n'es malheureusement pas éligible au pass culture."

    @override_features(BENEFICIARY_VALIDATION_AFTER_FRAUD_CHECKS=True)
    def test_validation_view_validate_user_with_non_default_eligibility(self, client):
        user = users_factories.UserFactory(dateOfBirth=datetime.utcnow() - relativedelta(years=18, months=2))
        check = fraud_factories.BeneficiaryFraudCheckFactory(user=user, type=fraud_models.FraudCheckType.DMS)
        admin = users_factories.AdminFactory()
        client.with_session_auth(admin.email)

        response = client.post(
            f"/pc/back-office/support_beneficiary/validate/beneficiary/{user.id}",
            form={"user_id": user.id, "reason": "User is granted", "review": "OK", "eligibility": "AGE18"},
        )
        assert response.status_code == 302
        review = fraud_models.BeneficiaryFraudReview.query.filter_by(user=user, author=admin).first()
        assert review.review == fraud_models.FraudReviewStatus.OK
        assert review.reason == "User is granted"
        user = users_models.User.query.get(user.id)
        assert user.has_beneficiary_role is True
        assert len(user.deposits) == 1

        dms_content = fraud_models.DMSContent(**check.resultContent)
        assert user.firstName == dms_content.first_name
        assert user.lastName == dms_content.last_name
        assert user.idPieceNumber == dms_content.id_piece_number


@pytest.mark.usefixtures("db_session")
class ValidatePhoneNumberTest:
    def test_phone_validation(self, client, caplog):
        admin = users_factories.AdminFactory()
        user = users_factories.UserFactory(phoneValidationStatus=None)
        client.with_session_auth(admin.email)
        with caplog.at_level(logging.INFO):
            response = client.post(f"/pc/back-office/support_beneficiary/validate/beneficiary/phone_number/{user.id}")
        assert response.status_code == 302
        assert (
            response.headers["Location"] == f"http://localhost/pc/back-office/support_beneficiary/details/?id={user.id}"
        )

        assert user.phoneValidationStatus == users_models.PhoneValidationStatusType.VALIDATED
        assert "flask-admin: Manual phone validation" in caplog.messages


@pytest.mark.usefixtures("db_session")
class BeneficiaryActivationStatusTest:
    def test_not_eligible(self):
        user = users_factories.UserFactory(dateOfBirth=datetime.utcnow() - relativedelta(years=25))
        assert get_beneficiary_activation_status(user) == BeneficiaryActivationStatus.NOT_APPLICABLE

    def test_beneficiary(self):
        user = users_factories.BeneficiaryGrant18Factory()
        # even if there was a passed fraud_check ko
        fraud_factories.BeneficiaryFraudCheckFactory(user=user, status=fraud_models.FraudCheckStatus.KO)
        assert get_beneficiary_activation_status(user) == BeneficiaryActivationStatus.OK

    def test_ex_underage(self):
        with freezegun.freeze_time(datetime.utcnow() - relativedelta(years=3)):
            user = users_factories.UnderageBeneficiaryFactory(
                dateOfBirth=datetime.utcnow() - relativedelta(years=15, months=5),
            )
        assert get_beneficiary_activation_status(user) == BeneficiaryActivationStatus.INCOMPLETE

    def test_ex_underage_with_some_fraud_check_ko(self):
        with freezegun.freeze_time(datetime.utcnow() - relativedelta(years=3)):
            user = users_factories.UnderageBeneficiaryFactory(
                dateOfBirth=datetime.utcnow() - relativedelta(years=15, months=5),
            )
        fraud_factories.BeneficiaryFraudCheckFactory(
            user=user, type=fraud_models.FraudCheckType.HONOR_STATEMENT, status=fraud_models.FraudCheckStatus.OK
        )
        fraud_factories.BeneficiaryFraudCheckFactory(
            user=user, type=fraud_models.FraudCheckType.UBBLE, status=fraud_models.FraudCheckStatus.KO
        )
        assert get_beneficiary_activation_status(user) == BeneficiaryActivationStatus.KO
