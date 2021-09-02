import datetime
import io

from dateutil.relativedelta import relativedelta
import pytest

import pcapi.core.users.factories as users_factories
from pcapi.core.users.models import User
from pcapi.scripts.beneficiary import import_users


eighteen_years_in_the_past = datetime.datetime.now() - relativedelta(years=18, months=4)

CSV = f"""Nom,Prénom,Mail,Téléphone,Département,Code postal,Date de naissance
Doux,Jeanne,jeanne.doux@example.com,0102030405,86,86140,{eighteen_years_in_the_past:%Y-%m-%d}
Smisse,Jean,jean.smisse@example.com,0102030406,44,44000,{eighteen_years_in_the_past:%Y-%m-%d}
"""


@pytest.mark.usefixtures("db_session")
class ReadFileTest:
    def test_read_file(self):
        jean = users_factories.BeneficiaryFactory(email="jean.smisse@example.com", lastName="Old name")
        assert len(jean.deposits) == 1

        csv_file = io.StringIO(CSV)
        users = import_users._read_file(csv_file)

        assert len(users) == 2

        jeanne = users[0]
        assert jeanne.firstName == "Jeanne"
        assert jeanne.lastName == "Doux"
        assert jeanne.publicName == "Jeanne Doux"
        assert jeanne.dateOfBirth.date() == eighteen_years_in_the_past.date()
        assert jeanne.email == "jeanne.doux@example.com"
        assert jeanne.phoneNumber == "0102030405"
        assert jeanne.departementCode == "86"
        assert jeanne.postalCode == "86140"
        assert jeanne.isBeneficiary
        assert jeanne.has_beneficiary_role
        assert len(jeanne.deposits) == 1

        jean = users[1]
        assert jean.lastName == "Smisse"
        assert len(jean.deposits) == 1

        admin = User.query.filter_by(email="admin@example.com").one()
        assert admin.isAdmin
        assert admin.has_admin_role
        assert not admin.has_beneficiary_role
