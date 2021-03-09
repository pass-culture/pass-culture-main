import datetime
import io

import pytest

import pcapi.core.users.factories as users_factories
from pcapi.core.users.models import User
from pcapi.notifications.push import testing
from pcapi.scripts.beneficiary import import_users


CSV = """Nom,Prénom,Mail,Téléphone,Département,Code postal,Date de naissance
Doux,Jeanne,jeanne.doux@example.com,0102030405,86,86140,2000-01-01
Smisse,Jean,jean.smisse@example.com,0102030406,44,44000,2000-01-02
"""


@pytest.mark.usefixtures("db_session")
class ReadFileTest:
    def test_read_file(self):
        jean = users_factories.UserFactory(email="jean.smisse@example.com", lastName="Old name")
        assert len(jean.deposits) == 1

        csv_file = io.StringIO(CSV)
        users = import_users._read_file(csv_file)

        assert len(users) == 2

        jeanne = users[0]
        assert jeanne.firstName == "Jeanne"
        assert jeanne.lastName == "Doux"
        assert jeanne.publicName == "Jeanne Doux"
        assert jeanne.dateOfBirth == datetime.datetime(2000, 1, 1)
        assert jeanne.email == "jeanne.doux@example.com"
        assert jeanne.phoneNumber == "0102030405"
        assert jeanne.departementCode == "86"
        assert jeanne.postalCode == "86140"
        assert jeanne.isBeneficiary
        assert len(jeanne.deposits) == 1

        jean = users[1]
        assert jean.lastName == "Smisse"
        assert len(jean.deposits) == 1

        admin = User.query.filter_by(email="admin@example.com").one()
        assert admin.isAdmin

        assert testing.requests == [
            {
                "user_id": jeanne.id,
                "attribute_values": {
                    "date(u.date_created)": jeanne.dateCreated.strftime("%Y-%m-%dT%H:%M:%S"),
                    "date(u.date_of_birth)": "2000-01-01T00:00:00",
                    "u.credit": 0,
                    "u.marketing_push_subscription": True,
                    "u.postal_code": None,
                },
            },
            {
                "user_id": admin.id,
                "attribute_values": {
                    "date(u.date_created)": admin.dateCreated.strftime("%Y-%m-%dT%H:%M:%S"),
                    "date(u.date_of_birth)": "1946-12-24T00:00:00",
                    "u.credit": 0,
                    "u.marketing_push_subscription": True,
                    "u.postal_code": None,
                },
            },
        ]
