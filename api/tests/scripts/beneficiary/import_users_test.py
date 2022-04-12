import datetime
import io

from dateutil.relativedelta import relativedelta
import pytest

from pcapi.core.offerers.models import Offerer
import pcapi.core.users.factories as users_factories
from pcapi.core.users.models import User
from pcapi.scripts.beneficiary import import_users


AGE18_ELIGIBLE_BIRTH_DATE = datetime.datetime.utcnow() - relativedelta(years=18, months=4)

CSV = f"""Nom,Prénom,Mail,Téléphone,Département,Code postal,Date de naissance,Role,SIREN,Type
Doux,Jeanne,jeanne.doux@example.com,0102030405,86,86140,{AGE18_ELIGIBLE_BIRTH_DATE:%Y-%m-%d},BENEFICIARY,,interne:test
Smisse,Jean,jean.smisse@example.com,0102030406,44,44000,{AGE18_ELIGIBLE_BIRTH_DATE:%Y-%m-%d},BENEFICIARY,,interne:test
Pro,Pierre,pro@example.com,0123456789,06,06000,2000-01-01,PRO,111222333,interne:test
"""


@pytest.mark.usefixtures("db_session")
class ReadFileTest:
    def test_read_file(self):
        jean = users_factories.BeneficiaryGrant18Factory(email="jean.smisse@example.com", lastName="Old name")
        assert len(jean.deposits) == 1

        csv_file = io.StringIO(CSV)
        users = import_users._read_file(csv_file)

        assert len(users) == 3

        jeanne = users[0]
        assert jeanne.firstName == "Jeanne"
        assert jeanne.lastName == "Doux"
        assert jeanne.publicName == "Jeanne Doux"
        assert jeanne.dateOfBirth.date() == AGE18_ELIGIBLE_BIRTH_DATE.date()
        assert jeanne.email == "jeanne.doux@example.com"
        assert jeanne.phoneNumber == "0102030405"
        assert jeanne.departementCode == "86"
        assert jeanne.postalCode == "86140"
        assert jeanne.has_beneficiary_role
        assert len(jeanne.deposits) == 1

        jean = users[1]
        assert jean.lastName == "Smisse"
        assert len(jean.deposits) == 1

        pierre = users[2]
        assert pierre.firstName == "Pierre"
        assert pierre.lastName == "Pro"
        assert pierre.publicName == "Pierre Pro"
        assert pierre.email == "pro@example.com"
        assert pierre.phoneNumber == "0123456789"
        assert pierre.departementCode == "06"
        assert pierre.postalCode == "06000"
        assert pierre.isEmailValidated
        assert pierre.has_pro_role
        assert not pierre.has_beneficiary_role
        assert len(pierre.deposits) == 0

        offerer = Offerer.query.one()
        assert offerer.siren == "111222333"
        assert offerer.isValidated

        admin = User.query.filter_by(email="admin@example.com").one()
        assert admin.has_admin_role
        assert not admin.has_beneficiary_role
