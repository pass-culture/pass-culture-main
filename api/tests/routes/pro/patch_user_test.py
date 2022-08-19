from pydantic import ValidationError
import pytest

from pcapi.core.users import testing as sendinblue_testing
import pcapi.core.users.factories as users_factories
from pcapi.core.users.models import User
from pcapi.routes.serialization.users import PatchProUserBodyModel

from tests.conftest import TestClient


@pytest.mark.usefixtures("db_session")
def test_patch_user(app):
    pro = users_factories.ProFactory(email="ma.librairie@example.com")
    data = {"firstName": "John", "lastName": "Doe", "email": "new@example.com", "phoneNumber": "+33999999999"}

    client = TestClient(app.test_client()).with_session_auth(email=pro.email)
    response = client.patch("/users/current", json=data)

    assert response.status_code == 200
    pro = User.query.get(pro.id)
    assert pro.firstName == "John"
    assert pro.lastName == "Doe"
    assert pro.email == "new@example.com"
    assert pro.phoneNumber == "+33999999999"

    assert len(sendinblue_testing.sendinblue_requests) == 2
    assert {req.get("email") for req in sendinblue_testing.sendinblue_requests} == {
        "ma.librairie@example.com",
        "new@example.com",
    }
    assert len(sendinblue_testing.sendinblue_requests) == 2


@pytest.mark.usefixtures("db_session")
def test_reject_beneficiary(app):
    beneficiary = users_factories.BeneficiaryGrant18Factory()
    initial = {
        "email": beneficiary.email,
        "publicName": beneficiary.publicName,
    }
    data = {
        "email": "new@example.com",
        "publicName": "New name",
    }
    client = TestClient(app.test_client()).with_session_auth(email=beneficiary.email)
    response = client.patch("/users/current", json=data)

    assert response.status_code == 400
    beneficiary = User.query.get(beneficiary.id)
    assert beneficiary.email == initial["email"]
    assert beneficiary.publicName == initial["publicName"]


@pytest.mark.usefixtures("db_session")
def test_forbid_some_attributes(app):
    pro = users_factories.ProFactory()
    # It's tedious to test all attributes. We focus on the most sensitive ones.
    forbidden_attributes = {"dateCreated": "2018-08-01 12:00:00", "roles": ["BENEFICIARY"]}

    client = TestClient(app.test_client()).with_session_auth(email=pro.email)

    data = {"publicName": "Name"}
    for attribute, value in forbidden_attributes.items():
        response = client.patch("/users/current", json={**data, attribute: value})
        assert response.status_code == 400
        assert response.json[attribute] == ["Vous ne pouvez pas changer cette information"]
        pro = User.query.get(pro.id)
        assert getattr(pro, attribute) != value


class PatchProUserBodyModelTest:
    def test_empty_first_name(self):
        try:
            PatchProUserBodyModel(firstName="")
        except ValidationError as err:
            assert err.errors()[0]["loc"][0] == "firstName"

    def test_empty_last_name(self):
        try:
            PatchProUserBodyModel(lastName="")
        except ValidationError as err:
            assert err.errors()[0]["loc"][0] == "lastName"

    def test_empty_email(self):
        try:
            PatchProUserBodyModel(email="")
        except ValidationError as err:
            assert err.errors()[0]["loc"][0] == "email"

    def test_empty_phone_number(self):
        try:
            PatchProUserBodyModel(phoneNumber="")
        except ValidationError as err:
            assert err.errors()[0]["loc"][0] == "phoneNumber"

    def test_phone_number_wrong_format(self):
        try:
            PatchProUserBodyModel(phoneNumber="not a phone number")
        except ValidationError as err:
            assert err.errors()[0]["loc"][0] == "phoneNumber"
