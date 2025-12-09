import pathlib
from io import BytesIO
from unittest.mock import patch

import pytest
import sqlalchemy as sa

from pcapi.core.subscription import models as subscription_models
from pcapi.core.subscription.factories import BeneficiaryFraudCheckFactory
from pcapi.core.subscription.factories import UbbleContentFactory
from pcapi.core.subscription.ubble import schemas as ubble_schemas
from pcapi.core.subscription.ubble import tasks as ubble_tasks
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
