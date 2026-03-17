import datetime
import pathlib
from io import BytesIO
from unittest.mock import patch
from uuid import uuid4

import pytest
import sqlalchemy as sa

from pcapi.core.subscription import models as subscription_models
from pcapi.core.subscription.factories import BeneficiaryFraudCheckFactory
from pcapi.core.subscription.factories import UbbleContentFactory
from pcapi.core.subscription.ubble import schemas as ubble_schemas
from pcapi.core.subscription.ubble import tasks as ubble_tasks
from pcapi.core.users import factories as users_factories
from pcapi.core.users import models as users_models
from pcapi.models import db

import tests


IMAGES_DIR = pathlib.Path(tests.__path__[0]) / "files"


@pytest.mark.usefixtures("db_session")
class StoreIdPictureTaskTest:
    front_picture_url = "https://storage.ubble.ai/front-picture.png?response-content-type=image%2Fpng"
    back_picture_url = "https://storage.ubble.ai/back-picture.png?response-content-type=image%2Fpng"

    @patch("botocore.session.Session.create_client")
    def test_store_id_picture_task(self, mocked_storage_client, requests_mock):
        fraud_check = BeneficiaryFraudCheckFactory(
            status=subscription_models.FraudCheckStatus.OK,
            type=subscription_models.FraudCheckType.UBBLE,
            resultContent=UbbleContentFactory(
                status=ubble_schemas.UbbleIdentificationStatus.PENDING,
                signed_image_front_url=self.front_picture_url,
                signed_image_back_url=self.back_picture_url,
            ),
        )
        fraud_check_id = fraud_check.id

        with open(f"{IMAGES_DIR}/carte_identite_front.png", "rb") as img_front:
            identity_file_picture_front = BytesIO(img_front.read())
        with open(f"{IMAGES_DIR}/carte_identite_back.png", "rb") as img_back:
            identity_file_picture_back = BytesIO(img_back.read())

        requests_mock.register_uri(
            "GET",
            self.front_picture_url,
            status_code=200,
            headers={"content-type": "image/png"},
            body=identity_file_picture_front,
        )
        requests_mock.register_uri(
            "GET",
            self.back_picture_url,
            status_code=200,
            headers={"content-type": "image/png"},
            body=identity_file_picture_back,
        )

        ubble_tasks.store_id_pictures_task.delay({"identification_id": fraud_check.thirdPartyId})

        fraud_check = db.session.scalar(
            sa.select(subscription_models.BeneficiaryFraudCheck).where(
                subscription_models.BeneficiaryFraudCheck.id == fraud_check_id
            )
        )
        assert fraud_check.idPicturesStored
        assert mocked_storage_client.return_value.upload_file.call_count == 2


@pytest.mark.usefixtures("db_session")
class IncompleteUbbleRecoveryTaskTest:
    @patch("pcapi.core.subscription.ubble.api.recover_ubble_verification_data")
    def test_recovery_task(self, mock_recovery):
        user = users_factories.UserFactory()
        fraud_check = BeneficiaryFraudCheckFactory(
            user=user,
            type=subscription_models.FraudCheckType.UBBLE,
            thirdPartyId="idv_qwerty1234",
            status=subscription_models.FraudCheckStatus.OK,
        )

        ubble_tasks.recover_incomplete_ubble_verification_task.delay(
            payload={"beneficiary_fraud_check_id": fraud_check.id}
        )

        mock_recovery.assert_called_with(fraud_check)

    @patch("pcapi.core.subscription.ubble.tasks.recover_incomplete_ubble_verification_task.delay")
    def test_recovery_command(self, mock_recovery_task):
        user = users_factories.UserFactory()
        fraud_check = BeneficiaryFraudCheckFactory(
            user=user,
            type=subscription_models.FraudCheckType.UBBLE,
            thirdPartyId="idv_qwerty1234",
            status=subscription_models.FraudCheckStatus.OK,
            eligibilityType=users_models.EligibilityType.AGE17_18,
            updatedAt=datetime.datetime(2026, 1, 1),
        )

        ubble_tasks.recover_incomplete_ubble_verification()

        mock_recovery_task.assert_called_with(payload={"beneficiary_fraud_check_id": fraud_check.id})

    @pytest.mark.parametrize("eligibility", [users_models.EligibilityType.AGE18, users_models.EligibilityType.UNDERAGE])
    @patch("pcapi.core.subscription.ubble.tasks.recover_incomplete_ubble_verification_task.delay")
    def test_recovery_command_ignores_pre_decree_eligibility(self, mock_recovery_task, eligibility):
        user = users_factories.UserFactory()
        BeneficiaryFraudCheckFactory(
            user=user,
            type=subscription_models.FraudCheckType.UBBLE,
            thirdPartyId="idv_qwerty1234",
            status=subscription_models.FraudCheckStatus.OK,
            eligibilityType=eligibility,
        )

        ubble_tasks.recover_incomplete_ubble_verification()

        mock_recovery_task.assert_not_called()

    @patch("pcapi.core.subscription.ubble.tasks.recover_incomplete_ubble_verification_task.delay")
    def test_recovery_command_ignores_ubble_v1(self, mock_recovery_task):
        user = users_factories.UserFactory()
        BeneficiaryFraudCheckFactory(
            user=user,
            type=subscription_models.FraudCheckType.UBBLE,
            thirdPartyId=str(uuid4()),
            status=subscription_models.FraudCheckStatus.OK,
            eligibilityType=users_models.EligibilityType.AGE17_18,
        )

        ubble_tasks.recover_incomplete_ubble_verification()

        mock_recovery_task.assert_not_called()

    @pytest.mark.parametrize(
        "type", [subscription_models.FraudCheckType.DMS, subscription_models.FraudCheckType.EDUCONNECT]
    )
    @patch("pcapi.core.subscription.ubble.tasks.recover_incomplete_ubble_verification_task.delay")
    def test_recovery_command_ignores_not_ubble(self, mock_recovery_task, type):
        user = users_factories.UserFactory()
        BeneficiaryFraudCheckFactory(
            user=user,
            type=type,
            thirdPartyId="idv_qwerty1234",
            status=subscription_models.FraudCheckStatus.OK,
            eligibilityType=users_models.EligibilityType.AGE17_18,
        )

        ubble_tasks.recover_incomplete_ubble_verification()

        mock_recovery_task.assert_not_called()

    @pytest.mark.parametrize(
        "status",
        [
            subscription_models.FraudCheckStatus.CANCELED,
            subscription_models.FraudCheckStatus.ERROR,
            subscription_models.FraudCheckStatus.KO,
            subscription_models.FraudCheckStatus.PENDING,
            subscription_models.FraudCheckStatus.SUSPICIOUS,
            subscription_models.FraudCheckStatus.MOCK_CONFIG,
        ],
    )
    @patch("pcapi.core.subscription.ubble.tasks.recover_incomplete_ubble_verification_task.delay")
    def test_recovery_command_ignores_not_ok(self, mock_recovery_task, status):
        user = users_factories.UserFactory()
        BeneficiaryFraudCheckFactory(
            user=user,
            type=subscription_models.FraudCheckType.UBBLE,
            status=status,
            thirdPartyId="idv_qwerty1234",
            eligibilityType=users_models.EligibilityType.AGE17_18,
        )

        ubble_tasks.recover_incomplete_ubble_verification()

        mock_recovery_task.assert_not_called()

    @patch("pcapi.core.subscription.ubble.tasks.recover_incomplete_ubble_verification_task.delay")
    def test_recovery_command_ignores_complete_ubble(self, mock_recovery_task):
        user = users_factories.UserFactory()
        BeneficiaryFraudCheckFactory(
            user=user,
            type=subscription_models.FraudCheckType.UBBLE,
            status=subscription_models.FraudCheckStatus.OK,
            thirdPartyId="idv_qwerty1234",
            eligibilityType=users_models.EligibilityType.AGE17_18,
            resultContent={
                "birth_place": "paris",
                "last_name_at_birth": "lyon",
                "document_issuing_country": "vietnam",
                "nationality": "espagnol",
            },
        )

        ubble_tasks.recover_incomplete_ubble_verification()

        mock_recovery_task.assert_not_called()

    @patch("pcapi.core.subscription.ubble.tasks.recover_incomplete_ubble_verification_task.delay")
    def test_recovery_command_ignores_recently_updated_partial_identification(self, mock_recovery_task):
        user = users_factories.UserFactory()
        BeneficiaryFraudCheckFactory(
            user=user,
            type=subscription_models.FraudCheckType.UBBLE,
            thirdPartyId="idv_qwerty1234",
            status=subscription_models.FraudCheckStatus.OK,
            eligibilityType=users_models.EligibilityType.AGE17_18,
            updatedAt=datetime.datetime(2026, 12, 12),
        )

        ubble_tasks.recover_incomplete_ubble_verification()

        mock_recovery_task.assert_not_called()
