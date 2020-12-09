from datetime import datetime

import pcapi.core.users.factories as users_factories
from pcapi.models.user_sql_entity import UserSQLEntity

from tests.conftest import TestClient
from tests.conftest import clean_database


class CustomViewsTest:
    @clean_database
    def test_beneficiary_user_creation(self, app):
        users_factories.UserFactory(email="user@example.com", isAdmin=True, isBeneficiary=False)

        data = dict(
            email="toto@email.fr",
            firstName="Serge",
            lastName="Lama",
            publicName="SergeLeLama",
            dateOfBirth="2002-07-13 10:05:00",
            departementCode="93",
            postalCode="93000",
            isBeneficiary="y",
        )

        client = TestClient(app.test_client()).with_auth("user@example.com")
        response = client.post("/pc/back-office/beneficiary_users/new", form=data)

        assert response.status_code == 302

        user_created = UserSQLEntity.query.filter_by(email="toto@email.fr").one()
        assert user_created.firstName == "Serge"
        assert user_created.lastName == "Lama"
        assert user_created.publicName == "SergeLeLama"
        assert user_created.dateOfBirth == datetime(2002, 7, 13, 10, 5)
        assert user_created.departementCode == "93"
        assert user_created.postalCode == "93000"
        assert user_created.isBeneficiary is True
        assert len(user_created.deposits) == 1
        assert user_created.deposits[0].source == "pass-culture-admin"
        assert user_created.deposits[0].amount == 500
