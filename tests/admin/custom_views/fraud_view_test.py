import pytest

from pcapi import settings
import pcapi.core.fraud.factories as fraud_factories
import pcapi.core.fraud.models as fraud_models
import pcapi.core.mails.testing as mails_testing
from pcapi.core.testing import override_features
from pcapi.core.testing import override_settings
import pcapi.core.users.factories as users_factories
import pcapi.core.users.models as users_models
import pcapi.models


@pytest.mark.usefixtures("db_session")
class BeneficiaryFraudListViewTest:
    def test_list_view(self, client):
        admin = users_factories.UserFactory(email="admin@example.com", isAdmin=True)
        client.with_auth(admin.email)

        for review_status in fraud_models.FraudReviewStatus:
            user = users_factories.UserFactory()
            fraud_factories.BeneficiaryFraudCheckFactory(user=user)
            fraud_factories.BeneficiaryFraudResultFactory(user=user)
            fraud_factories.BeneficiaryFraudReviewFactory(user=user, review=review_status)
        response = client.get("/pc/back-office/beneficiary_fraud/")
        assert response.status_code == 200


@pytest.mark.usefixtures("db_session")
class BeneficiaryFraudDetailViewTest:
    def test_detail_view(self, client):
        admin = users_factories.UserFactory(email="admin@example.com", isAdmin=True)
        user = users_factories.UserFactory()
        fraud_factories.BeneficiaryFraudCheckFactory(user=user)
        fraud_factories.BeneficiaryFraudResultFactory(user=user)
        client.with_auth(admin.email)
        response = client.get("/pc/back-office/beneficiary_fraud/?id={user.id}")
        assert response.status_code == 200


@pytest.mark.usefixtures("db_session")
class BeneficiaryFraudValidationViewTest:
    @override_features(BENEFICIARY_VALIDATION_AFTER_FRAUD_CHECKS=True)
    def test_validation_view_auth_required(self, client):
        user = users_factories.UserFactory()
        response = client.post(f"/pc/back-office/beneficiary_fraud/validate/beneficiary/{user.id}")
        assert response.status_code == 302
        assert response.headers["Location"] == "http://localhost/pc/back-office/"

    @override_features(BENEFICIARY_VALIDATION_AFTER_FRAUD_CHECKS=True)
    def test_validation_view_validate_user_staging(self, client):
        user = users_factories.UserFactory(isBeneficiary=False)
        check = fraud_factories.BeneficiaryFraudCheckFactory(user=user, type=fraud_models.FraudCheckType.JOUVE)
        admin = users_factories.UserFactory(isAdmin=True)
        client.with_auth(admin.email)

        response = client.post(
            f"/pc/back-office/beneficiary_fraud/validate/beneficiary/{user.id}",
            form={"user_id": user.id, "reason": "User is granted", "review": "OK"},
        )
        assert response.status_code == 302

        review = fraud_models.BeneficiaryFraudReview.query.filter_by(user=user, author=admin).one()
        assert review.review == fraud_models.FraudReviewStatus.OK
        assert review.reason == "User is granted"
        user = users_models.User.query.get(user.id)
        assert user.isBeneficiary is True
        assert len(user.deposits) == 1

        jouve_content = fraud_models.JouveContent(**check.resultContent)
        assert user.firstName == jouve_content.firstName
        assert user.lastName == jouve_content.lastName

    @override_features(BENEFICIARY_VALIDATION_AFTER_FRAUD_CHECKS=True)
    def test_validation_view_validate_user_wrong_args(self, client):
        user = users_factories.UserFactory(isBeneficiary=False)
        admin = users_factories.UserFactory(isAdmin=True)

        client.with_auth(admin.email)

        response = client.post(
            f"/pc/back-office/beneficiary_fraud/validate/beneficiary/{user.id}",
            form={"user_id": user.id, "badkey": "User is granted", "review": "OK"},
        )
        assert response.status_code == 302
        review = fraud_models.BeneficiaryFraudReview.query.filter_by(user=user, author=admin).one_or_none()
        assert review is None

        user = users_models.User.query.get(user.id)
        assert user.isBeneficiary is False
        assert user.deposits == []

    @override_features(BENEFICIARY_VALIDATION_AFTER_FRAUD_CHECKS=True)
    def test_validation_view_validate_user_already_reviewed(self, client):
        user = users_factories.UserFactory(isBeneficiary=False)
        admin = users_factories.UserFactory(isAdmin=True)
        expected_review = fraud_factories.BeneficiaryFraudReviewFactory(user=user, author=admin)
        client.with_auth(admin.email)

        response = client.post(
            f"/pc/back-office/beneficiary_fraud/validate/beneficiary/{user.id}",
            form={"user_id": user.id, "reason": "User is granted", "review": "OK"},
        )
        assert response.status_code == 302
        review = fraud_models.BeneficiaryFraudReview.query.filter_by(user=user, author=admin).one()
        assert review.reason == expected_review.reason

    @override_features(BENEFICIARY_VALIDATION_AFTER_FRAUD_CHECKS=True)
    def test_validation_view_validate_not_super_user_fails(self, client):
        user = users_factories.UserFactory(isBeneficiary=False)
        admin = users_factories.UserFactory(isAdmin=True)
        client.with_auth(admin.email)

        with override_settings(IS_PROD=True):
            response = client.post(
                f"/pc/back-office/beneficiary_fraud/validate/beneficiary/{user.id}",
                form={"user_id": user.id, "reason": "User is granted", "review": "OK"},
            )
        assert response.status_code == 302
        review = fraud_models.BeneficiaryFraudReview.query.filter_by(user=user, author=admin).one_or_none()
        assert review is None
        assert user.isBeneficiary is False

    @override_features(BENEFICIARY_VALIDATION_AFTER_FRAUD_CHECKS=True)
    def test_validation_prod_requires_super_admin(self, client):
        user = users_factories.UserFactory(isBeneficiary=False)
        check = fraud_factories.BeneficiaryFraudCheckFactory(user=user, type=fraud_models.FraudCheckType.JOUVE)
        admin = users_factories.UserFactory(isAdmin=True)
        client.with_auth(admin.email)

        with override_settings(IS_PROD=True, SUPER_ADMIN_EMAIL_ADDRESSES=[admin.email]):
            response = client.post(
                f"/pc/back-office/beneficiary_fraud/validate/beneficiary/{user.id}",
                form={"user_id": user.id, "reason": "User is granted", "review": "OK"},
            )
        assert response.status_code == 302
        review = fraud_models.BeneficiaryFraudReview.query.filter_by(user=user, author=admin).one_or_none()
        assert review is not None
        assert review.author == admin
        assert user.isBeneficiary is True

        jouve_content = fraud_models.JouveContent(**check.resultContent)
        assert user.firstName == jouve_content.firstName
        assert user.lastName == jouve_content.lastName

    @override_features(BENEFICIARY_VALIDATION_AFTER_FRAUD_CHECKS=True)
    def test_validation_from_jouve_admin(self, client):
        user = users_factories.UserFactory(isBeneficiary=False)
        check = fraud_factories.BeneficiaryFraudCheckFactory(user=user, type=fraud_models.FraudCheckType.JOUVE)
        jouve_admin = users_factories.UserFactory(isAdmin=False, roles=[users_models.UserRole.JOUVE])
        client.with_auth(jouve_admin.email)

        response = client.post(
            f"/pc/back-office/beneficiary_fraud/validate/beneficiary/{user.id}",
            form={"user_id": user.id, "reason": "User is granted", "review": "OK"},
        )
        assert response.status_code == 302
        review = fraud_models.BeneficiaryFraudReview.query.filter_by(user=user, author=jouve_admin).one_or_none()
        assert review is not None
        assert review.author == jouve_admin
        assert user.isBeneficiary is True

        jouve_content = fraud_models.JouveContent(**check.resultContent)
        assert user.firstName == jouve_content.firstName
        assert user.lastName == jouve_content.lastName

    def test_review_ko_does_not_activate_the_beneficiary(self, client):
        user = users_factories.UserFactory(isBeneficiary=False)
        fraud_factories.BeneficiaryFraudCheckFactory(user=user, type=fraud_models.FraudCheckType.JOUVE)
        admin = users_factories.UserFactory(isAdmin=True)
        client.with_auth(admin.email)

        with override_settings(IS_PROD=True, SUPER_ADMIN_EMAIL_ADDRESSES=[admin.email]):
            response = client.post(
                f"/pc/back-office/beneficiary_fraud/validate/beneficiary/{user.id}",
                form={"user_id": user.id, "reason": "User is denied", "review": "KO"},
            )
        assert response.status_code == 302
        review = fraud_models.BeneficiaryFraudReview.query.filter_by(user=user, author=admin).one_or_none()
        assert review is not None
        assert review.author == admin
        assert review.review == fraud_models.FraudReviewStatus.KO
        assert user.isBeneficiary is False

    def test_return_to_dms(self, client):
        user = users_factories.UserFactory(isBeneficiary=False)
        fraud_factories.BeneficiaryFraudCheckFactory(user=user, type=fraud_models.FraudCheckType.JOUVE)
        jouve_admin = users_factories.UserFactory(isAdmin=False, roles=[users_models.UserRole.JOUVE])
        client.with_auth(jouve_admin.email)

        client.post(
            f"/pc/back-office/beneficiary_fraud/validate/beneficiary/{user.id}",
            form={"user_id": user.id, "reason": "User is granted", "review": "REDIRECTED_TO_DMS"},
        )

        review = fraud_models.BeneficiaryFraudReview.query.filter_by(user=user, author=jouve_admin).one_or_none()
        assert review is not None
        assert review.author == jouve_admin
        assert review.review == fraud_models.FraudReviewStatus.REDIRECTED_TO_DMS
        assert "; Redirigé vers DMS" in review.reason
        assert user.isBeneficiary is False

        assert len(mails_testing.outbox) == 1
        sent_data = mails_testing.outbox[0].sent_data

        assert sent_data["Vars"]["url"] == settings.DMS_USER_URL
        assert sent_data["MJ-TemplateID"] == 2958557


@pytest.mark.usefixtures("db_session")
class JouveUpdateIDPieceNumberTest:
    def setup_method(self, method):
        self.jouve_admin = users_factories.UserFactory(isAdmin=False, roles=[users_models.UserRole.JOUVE])

    def test_update_beneficiary_id_piece_number(self, client):
        user = users_factories.UserFactory(isAdmin=False, isBeneficiary=False)
        content = fraud_factories.JouveContentFactory(
            birthLocationCtrl="OK",
            bodyBirthDateCtrl="OK",
            bodyBirthDateLevel=100,
            bodyFirstnameCtrl="OK",
            bodyFirstnameLevel=100,
            bodyNameLevel=100,
            bodyNameCtrl="OK",
            bodyPieceNumber="wrong-id-piece-number",
            bodyPieceNumberCtrl="KO",  # ensure we correctly update this field later in the test
            bodyPieceNumberLevel=100,
            creatorCtrl="OK",
            initialSizeCtrl="OK",
        )
        fraud_check = fraud_factories.BeneficiaryFraudCheckFactory(
            user=user, type=fraud_models.FraudCheckType.JOUVE, resultContent=content
        )
        fraud_factories.BeneficiaryFraudResultFactory(user=user, status=fraud_models.FraudStatus.SUSPICIOUS)

        client.with_auth(self.jouve_admin.email)
        response = client.post(
            f"/pc/back-office/beneficiary_fraud/update/beneficiary/id_piece_number/{user.id}",
            form={"id_piece_number": "123123123123"},
        )

        assert response.status_code == 302

        assert user.beneficiaryFraudResult.status == fraud_models.FraudStatus.OK
        assert fraud_check.resultContent["bodyPieceNumberCtrl"] == "OK"
        assert fraud_check.resultContent["bodyPieceNumber"] == "123123123123"
        assert user.isBeneficiary
        assert len(user.beneficiaryImports) == 1
        assert user.beneficiaryImports[0].currentStatus == pcapi.models.ImportStatus.CREATED

    def test_jouve_specific_query_filter(self, client):
        client.with_auth(self.jouve_admin.email)

        fraud_factories.BeneficiaryFraudCheckFactory(type=fraud_models.FraudCheckType.JOUVE)
        fraud_factories.BeneficiaryFraudCheckFactory(type=fraud_models.FraudCheckType.DMS)
        response = client.get("/pc/back-office/beneficiary_fraud")
        assert "<ul><li>dms</li></ul>" not in response.data.decode()

    def test_admin_can_update_id_piece_number(self, client):
        admin = users_factories.AdminFactory()
        user = users_factories.UserFactory(isAdmin=False, isBeneficiary=False, idPieceNumber=None)
        content = fraud_factories.JouveContentFactory(
            birthLocationCtrl="OK",
            bodyBirthDateCtrl="OK",
            bodyBirthDateLevel=100,
            bodyFirstnameCtrl="OK",
            bodyFirstnameLevel=100,
            bodyNameLevel=100,
            bodyNameCtrl="OK",
            bodyPieceNumber="wrong-id-piece-number",
            bodyPieceNumberCtrl="KO",  # ensure we correctly update this field later in the test
            bodyPieceNumberLevel=100,
            creatorCtrl="OK",
            initialSizeCtrl="OK",
        )
        fraud_check = fraud_factories.BeneficiaryFraudCheckFactory(
            user=user, type=fraud_models.FraudCheckType.JOUVE, resultContent=content
        )
        fraud_factories.BeneficiaryFraudResultFactory(user=user, status=fraud_models.FraudStatus.SUSPICIOUS)

        client.with_auth(admin.email)
        client.post(
            f"/pc/back-office/beneficiary_fraud/update/beneficiary/id_piece_number/{user.id}",
            form={"id_piece_number": "123123123123"},
        )

        assert fraud_check.resultContent["bodyPieceNumberCtrl"] == "OK"
        assert fraud_check.resultContent["bodyPieceNumber"] == "123123123123"
        assert user.isBeneficiary
        assert len(user.beneficiaryImports) == 1
        assert user.beneficiaryImports[0].currentStatus == pcapi.models.ImportStatus.CREATED


@pytest.mark.usefixtures("db_session")
class JouveAccessTest:
    """Specific tests to ensure JOUVE does not access anything else"""

    def test_access_index(self, client):
        user = users_factories.UserFactory(isAdmin=False, roles=[users_models.UserRole.JOUVE])
        client.with_auth(user.email)
        response = client.get("/pc/back-office/")
        assert response.status_code == 200

    def test_access_fraud_views(self, client):
        user = users_factories.UserFactory(isAdmin=False, roles=[users_models.UserRole.JOUVE])
        client.with_auth(user.email)
        response = client.get("/pc/back-office/beneficiary_fraud")
        assert response.status_code == 200

    @pytest.mark.parametrize(
        "url",
        [
            "/pc/back-office/pro_users",
            "/pc/back-office/admin_users",
            "/pc/back-office/beneficiary_users",
        ],
    )
    def test_access_forbidden_views(self, client, url):
        user = users_factories.UserFactory(isAdmin=False, roles=[users_models.UserRole.JOUVE])
        client.with_auth(user.email)
        response = client.get(url)
        assert response.status_code == 302
        assert response.headers["Location"] == "http://localhost/pc/back-office/"
