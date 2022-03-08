import datetime
import re
from unittest.mock import patch

from dateutil.relativedelta import relativedelta
import pytest

from pcapi.core.fraud import factories as fraud_factories
from pcapi.core.fraud import models as fraud_models
from pcapi.core.users import factories as users_factories
from pcapi.core.users import models as users_models
from pcapi.scripts.beneficiary.update_gender_and_married_name_from_ubble import (
    update_gender_and_married_name_from_ubble,
)

from tests.connectors.beneficiaries.ubble_fixtures import UBBLE_IDENTIFICATION_RESPONSE


@pytest.mark.usefixtures("db_session")
class UpdateGenderAndMarriedNameFromUbbleTest:
    def setup(self):
        # Not yet beneficiary
        self.user_not_beneficiary = users_factories.UserFactory(
            dateOfBirth=datetime.datetime.now() - relativedelta(year=18, month=4),
        )
        fraud_factories.BeneficiaryFraudCheckFactory(
            user=self.user_not_beneficiary,
            type=fraud_models.FraudCheckType.UBBLE,
        )

        # Beneficiary with gender
        self.user_beneficiary_up_to_date = users_factories.BeneficiaryGrant18Factory(gender=users_models.GenderEnum.F)

        # Beneficiary with no gender nor married_name
        self.user_beneficiary_to_update = users_factories.BeneficiaryGrant18Factory(gender=None, married_name=None)

        # Beneficiary from DMS
        self.user_beneficiary_dms = users_factories.BeneficiaryGrant18Factory(
            gender=None, married_name=None, beneficiaryFraudChecks__type=fraud_models.FraudCheckType.DMS
        )
        # Beneficiary created before january 1st, 2022
        self.old_user_beneficiary = users_factories.BeneficiaryGrant18Factory(
            gender=None,
            married_name=None,
            beneficiaryFraudChecks__type=fraud_models.FraudCheckType.DMS,
            dateCreated=datetime.datetime(2021, 12, 25),
        )

    @patch("pcapi.scripts.beneficiary.update_gender_and_married_name_from_ubble.logger.info")
    def test_update_gender_and_married_name_from_ubble_dry_run(self, mock_logger, requests_mock):
        response = UBBLE_IDENTIFICATION_RESPONSE
        response["included"][3]["attributes"]["gender"] = "F"
        response["included"][3]["attributes"]["married-name"] = "Kelly"
        requests_mock.register_uri(
            "GET",
            re.compile("/identifications/[a-zA-Z0-9-]+/"),
            status_code=200,
            json=response,
        )

        # Should not update anything
        update_gender_and_married_name_from_ubble()

        assert mock_logger.call_args_list[0].args == ("Would have updated %d users", 1)

        assert self.user_not_beneficiary.gender is None
        assert self.user_not_beneficiary.married_name is None
        assert self.user_beneficiary_up_to_date.gender == users_models.GenderEnum.F
        assert self.user_beneficiary_up_to_date.married_name is None
        assert self.user_beneficiary_dms.gender is None
        assert self.user_beneficiary_dms.married_name is None
        assert self.old_user_beneficiary.gender is None
        assert self.old_user_beneficiary.married_name is None
        assert self.user_beneficiary_to_update.gender is None
        assert self.user_beneficiary_to_update.married_name is None

    def test_update_gender_and_married_name_from_ubble(self, requests_mock):
        response = UBBLE_IDENTIFICATION_RESPONSE
        response["included"][3]["attributes"]["gender"] = "F"
        response["included"][3]["attributes"]["married-name"] = "Kelly"
        requests_mock.register_uri(
            "GET",
            re.compile("/identifications/[a-zA-Z0-9-]+/"),
            status_code=200,
            json=response,
        )

        # Should update user_beneficiary_to_update
        update_gender_and_married_name_from_ubble(dry_run=False)

        assert self.user_not_beneficiary.gender is None
        assert self.user_not_beneficiary.married_name is None
        assert self.user_beneficiary_up_to_date.gender == users_models.GenderEnum.F
        assert self.user_beneficiary_up_to_date.married_name is None
        assert self.user_beneficiary_dms.gender is None
        assert self.user_beneficiary_dms.married_name is None
        assert self.old_user_beneficiary.gender is None
        assert self.old_user_beneficiary.married_name is None

        # Only user to be updated
        assert self.user_beneficiary_to_update.gender == users_models.GenderEnum.F
        assert self.user_beneficiary_to_update.married_name == "Kelly"
