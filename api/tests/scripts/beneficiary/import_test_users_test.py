import datetime
import io

from dateutil.relativedelta import relativedelta
import pytest

from pcapi import settings
from pcapi.core.offerers.models import Offerer
import pcapi.core.users.factories as users_factories
from pcapi.core.users.models import User
from pcapi.scripts.beneficiary import import_test_users


AGE18_ELIGIBLE_BIRTH_DATE = datetime.datetime.utcnow() - relativedelta(years=18, months=4)

CSV = f"""Nom,Prénom,Mail,Téléphone,Département,Code postal,Date de naissance,Role,SIREN,Mot de passe,Type
Doux,Jeanne,jeanne.doux@example.com,0102030405,86,86140,{AGE18_ELIGIBLE_BIRTH_DATE:%Y-%m-%d},BENEFICIARY,,,interne:test
Smisse,Jean,jean.smisse@example.com,0102030406,44,44000,{AGE18_ELIGIBLE_BIRTH_DATE:%Y-%m-%d},BENEFICIARY,,,interne:test
Pro,Pierre,pro@example.com,0123456789,06,06000,2000-01-01,PRO,111222333,PierrePro$123,interne:test
"""


@pytest.mark.usefixtures("db_session")
class ReadFileTest:
    @pytest.mark.parametrize("update_if_exists", [True, False])
    def test_read_file(self, update_if_exists):
        jean = users_factories.BeneficiaryGrant18Factory(email="jean.smisse@example.com", lastName="Old name")
        assert len(jean.deposits) == 1

        csv_file = io.StringIO(CSV)
        users = import_test_users.create_users_from_csv(csv_file, update_if_exists=update_if_exists)

        assert len(users) == 3 if update_if_exists else 2

        jeanne = users[0]
        assert jeanne.firstName == "Jeanne"
        assert jeanne.lastName == "Doux"
        assert jeanne.publicName == "Jeanne Doux"
        assert jeanne.dateOfBirth.date() == AGE18_ELIGIBLE_BIRTH_DATE.date()
        assert jeanne.email == "jeanne.doux@example.com"
        assert jeanne.phoneNumber == "+33102030405"
        assert jeanne.departementCode == "86"
        assert jeanne.postalCode == "86140"
        assert jeanne.comment == "interne:test"
        assert jeanne.isEmailValidated
        assert jeanne.validationToken is None
        assert jeanne.has_beneficiary_role
        assert jeanne.has_test_role
        assert len(jeanne.deposits) == 1

        assert jeanne.checkPassword(settings.TEST_DEFAULT_PASSWORD)

        if update_if_exists:
            jean = users[1]
            assert jean.lastName == "Smisse"
            assert len(jean.deposits) == 1

        pierre = users[-1]
        assert pierre.firstName == "Pierre"
        assert pierre.lastName == "Pro"
        assert pierre.publicName == "Pierre Pro"
        assert pierre.email == "pro@example.com"
        assert pierre.phoneNumber == "+33123456789"
        assert pierre.departementCode == "06"
        assert pierre.postalCode == "06000"
        assert pierre.comment == "interne:test"
        assert pierre.isEmailValidated
        assert pierre.validationToken is None
        assert pierre.has_pro_role
        assert not pierre.has_beneficiary_role
        assert pierre.has_test_role
        assert len(pierre.deposits) == 0

        offerer = Offerer.query.one()
        assert offerer.siren == "111222333"
        assert offerer.isValidated

        assert pierre.checkPassword("PierrePro$123")

        admin = User.query.filter_by(email="admin@example.com").one()
        assert admin.has_admin_role
        assert not admin.has_beneficiary_role
        assert not admin.has_test_role
