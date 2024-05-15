import datetime

from flask import url_for
import pytest

from pcapi.core.educational import models
from pcapi.core.educational.api.institution import get_educational_institution_department_code
from pcapi.core.educational.factories import CollectiveOfferTemplateFactory
from pcapi.core.educational.factories import CollectiveStockFactory
from pcapi.core.educational.factories import EducationalInstitutionFactory
from pcapi.core.educational.factories import EducationalInstitutionProgramFactory
from pcapi.core.educational.factories import EducationalRedactorFactory
from pcapi.core.testing import assert_num_queries

from tests.routes.adage_iframe.utils_create_test_token import DEFAULT_LAT
from tests.routes.adage_iframe.utils_create_test_token import DEFAULT_LON
from tests.routes.adage_iframe.utils_create_test_token import create_adage_jwt_default_fake_valid_token
from tests.routes.adage_iframe.utils_create_test_token import create_adage_jwt_fake_invalid_token
from tests.routes.adage_iframe.utils_create_test_token import create_adage_jwt_fake_valid_token


pytestmark = pytest.mark.usefixtures("db_session")


DEFAULT_UAI = "EAU123"
DEFAULT_RURAL_LEVEL = models.InstitutionRuralLevel.URBAIN_DENSE


@pytest.fixture(name="valid_user", scope="module")
def valid_user_fixture():
    return {
        "civilite": "Mme.",
        "nom": "LAPROF",
        "prenom": "Sabine",
        "mail": "sabine.laprof@example.com",
        "uai": DEFAULT_UAI,
    }


def expected_serialized_auth_base(redactor, institution):
    return {
        "role": "redactor",
        "uai": institution.institutionId,
        "departmentCode": get_educational_institution_department_code(institution),
        "institutionName": institution.full_name,
        "institutionCity": institution.city,
        "email": redactor.email,
        "preferences": {
            "feedback_form_closed": redactor.preferences.get("feedback_form_closed"),
            "broadcast_help_closed": redactor.preferences.get("broadcast_help_closed"),
        },
        "lat": DEFAULT_LAT,
        "lon": DEFAULT_LON,
        "favoritesCount": 0,
        "offersCount": 0,
        "institutionRuralLevel": None,
        "programs": [],
    }


class AuthenticateTest:
    def test_should_authenticate_redactor(self, client, valid_user):
        redactor = EducationalRedactorFactory(email=valid_user.get("mail"))
        program = EducationalInstitutionProgramFactory()
        institution = EducationalInstitutionFactory(
            institutionId=DEFAULT_UAI,
            programs=[program],
            ruralLevel=DEFAULT_RURAL_LEVEL,
        )

        valid_encoded_token = self._create_adage_valid_token(valid_user, uai_code=DEFAULT_UAI)

        response = client.with_explicit_token(valid_encoded_token).get("/adage-iframe/authenticate")

        assert response.status_code == 200
        assert response.json == {
            **expected_serialized_auth_base(redactor, institution),
            "institutionRuralLevel": DEFAULT_RURAL_LEVEL.value,
            "programs": [{"name": program.name, "label": program.label, "description": program.description}],
        }

    def test_should_return_redactor_role_when_token_has_an_uai_code(self, client, valid_user) -> None:
        # Given
        redactor = EducationalRedactorFactory(email=valid_user.get("mail"))
        institution = EducationalInstitutionFactory(institutionId=valid_user.get("uai"))
        CollectiveStockFactory(
            collectiveOffer__institution=institution,
        )
        CollectiveStockFactory(
            startDatetime=datetime.datetime.utcnow() - datetime.timedelta(days=5),
            endDatetime=datetime.datetime.utcnow() - datetime.timedelta(days=5),
            collectiveOffer__institution=institution,
        )

        valid_encoded_token = self._create_adage_valid_token(valid_user, uai_code=valid_user.get("uai"))

        # When
        response = client.with_explicit_token(valid_encoded_token).get("/adage-iframe/authenticate")

        # Then
        assert response.status_code == 200
        assert response.json == {**expected_serialized_auth_base(redactor, institution), "offersCount": 1}

    def test_favorites_count(self, client) -> None:
        redactor = EducationalRedactorFactory(
            favoriteCollectiveOfferTemplates=[CollectiveOfferTemplateFactory()],
        )

        client = client.with_adage_token(email=redactor.email, uai="someuai")

        # fetch the institution
        # fetch the redactor
        # count the redactor's favorites (templates only)
        # count the offers linked to institution uai
        with assert_num_queries(4):
            response = client.get(url_for("adage_iframe.authenticate"))

        assert response.status_code == 200
        assert response.json["favoritesCount"] == 1

    def test_preferences_are_correctly_serialized(self, client) -> None:
        educational_institution = EducationalInstitutionFactory()
        educational_redactor = EducationalRedactorFactory(
            preferences={"feedback_form_closed": True, "broadcast_help_closed": True}
        )

        client = client.with_adage_token(email=educational_redactor.email, uai=educational_institution.institutionId)
        response = client.get("/adage-iframe/authenticate")

        assert response.status_code == 200
        assert response.json["preferences"] == {"broadcast_help_closed": True, "feedback_form_closed": True}

    def test_should_return_readonly_role_when_token_has_no_uai_code(self, client, valid_user) -> None:
        # Given
        valid_encoded_token = self._create_adage_valid_token(valid_user, uai_code=None)

        # When
        response = client.with_explicit_token(valid_encoded_token).get("/adage-iframe/authenticate")

        # Then
        assert response.status_code == 200
        assert response.json == {
            "role": "readonly",
            "uai": None,
            "departmentCode": None,
            "institutionName": None,
            "institutionCity": None,
            "email": None,
            "preferences": None,
            "lat": None,
            "lon": None,
            "favoritesCount": 0,
            "offersCount": 0,
            "institutionRuralLevel": None,
            "programs": [],
        }

    def test_should_return_error_response_when_jwt_invalid(self, client):
        # Given
        corrupted_token = self._create_adage_invalid_token()

        # When
        response = client.with_explicit_token(corrupted_token).get("/adage-iframe/authenticate")

        # Then
        assert response.status_code == 401
        assert "Unrecognized token" in response.json["msg"]

    def test_should_return_error_response_when_jwt_expired(self, client, valid_user):
        # Given
        now = datetime.datetime.utcnow()
        expired_token = self._create_adage_valid_token_from_expiration_date(
            valid_user, expiration_date=now - datetime.timedelta(days=1)
        )

        # When
        response = client.with_explicit_token(expired_token).get("/adage-iframe/authenticate")

        # Then
        assert response.status_code == 401
        assert "Token expired" in response.json["msg"]

    def test_should_return_error_response_when_no_expiration_date_in_token(self, client, valid_user):
        # Given
        no_expiration_date_token = self._create_adage_valid_token_from_expiration_date(valid_user, expiration_date=None)

        # When
        response = client.with_explicit_token(no_expiration_date_token).get("/adage-iframe/authenticate")

        # Then
        assert response.status_code == 401
        assert "No expiration date provided" in response.json["msg"]

    def _create_adage_valid_token(self, valid_user, uai_code: str | None) -> bytes:
        return create_adage_jwt_default_fake_valid_token(
            civility=valid_user.get("civilite"),
            lastname=valid_user.get("nom"),
            firstname=valid_user.get("prenom"),
            email=valid_user.get("mail"),
            uai=uai_code,
            lat=DEFAULT_LAT,
            lon=DEFAULT_LON,
        )

    def _create_adage_valid_token_from_expiration_date(
        self, valid_user, expiration_date: datetime.datetime | None
    ) -> bytes:
        return create_adage_jwt_fake_valid_token(
            civility=valid_user.get("civilite"),
            lastname=valid_user.get("nom"),
            firstname=valid_user.get("prenom"),
            email=valid_user.get("mail"),
            uai=valid_user.get("uai"),
            expiration_date=expiration_date,
            lat=DEFAULT_LAT,
            lon=DEFAULT_LON,
        )

    @staticmethod
    def _create_adage_invalid_token() -> bytes:
        return create_adage_jwt_fake_invalid_token(
            civility="M.", lastname="TESTABLE", firstname="Pascal", email="pascal.testable@example.com", uai="321UAE"
        )
