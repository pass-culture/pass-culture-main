import pytest
import sqlalchemy
from sqlalchemy.sql import text

import pcapi.core.users.api as users_api
import pcapi.core.users.factories as users_factories
import pcapi.core.users.models as users_models
from pcapi.models import ImportStatus

from tests.conftest import clean_database


class ConcurrencyUpdateBeneficiaryMandatoryInformationTest:
    @clean_database
    def test_all_steps_to_become_beneficiary_with_lock(self, app):
        """
        Test that the user's id check profile information are updated and that
        it becomes beneficiary (and therefore has a deposit)
        """
        user = users_factories.UserFactory(
            phoneValidationStatus=users_models.PhoneValidationStatusType.VALIDATED,
            hasCompletedIdCheck=False,
        )
        beneficiary_import = users_factories.BeneficiaryImportFactory(beneficiary=user)
        beneficiary_import.setStatus(ImportStatus.CREATED)

        new_address = f"{user.address}_test"
        new_city = f"{user.city}_test"
        # open a second connection on purpose and lock the user
        engine = sqlalchemy.create_engine(app.config["SQLALCHEMY_DATABASE_URI"])
        with engine.connect() as connection:
            connection.execute(text("""SELECT * FROM "user" WHERE "user".id = :user_id FOR UPDATE"""), user_id=user.id)

            with pytest.raises(sqlalchemy.exc.OperationalError):
                users_api.update_beneficiary_mandatory_information(
                    user=user,
                    address=new_address,
                    city=new_city,
                    postal_code="93000",
                    activity=user.activity,
                )
        user = users_models.User.query.get(user.id)

        assert not user.hasCompletedIdCheck
        assert not user.isBeneficiary
        assert not user.deposit
