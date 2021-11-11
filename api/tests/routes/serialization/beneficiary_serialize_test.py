from freezegun import freeze_time

from pcapi.core.users.factories import UserFactory
from pcapi.routes.serialization.beneficiaries import BeneficiaryAccountResponse

from tests.conftest import clean_database


class BeneficiaryAccountResponseTest:
    @freeze_time("2019-1-1")
    @clean_database
    def should_humanize_the_user_id(self, app):
        # Given
        beneficiary = UserFactory(id=1)

        # When
        response = BeneficiaryAccountResponse.from_orm(beneficiary)

        # Then
        assert response.pk == 1
        assert response.id == "AE"
