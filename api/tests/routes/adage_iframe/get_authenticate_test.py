import datetime

import pytest
from flask import url_for

import pcapi.utils.db as db_utils
from pcapi.core.educational import factories as educational_factories
from pcapi.core.educational import models
from pcapi.core.educational.api.institution import get_educational_institution_department_code
from pcapi.core.testing import assert_num_queries
from pcapi.utils import date as date_utils

from tests.routes.adage_iframe.utils_create_test_token import DEFAULT_LAT
from tests.routes.adage_iframe.utils_create_test_token import DEFAULT_LON
from tests.routes.adage_iframe.utils_create_test_token import create_adage_jwt_default_fake_valid_token
from tests.routes.adage_iframe.utils_create_test_token import create_adage_jwt_fake_invalid_token
from tests.routes.adage_iframe.utils_create_test_token import create_adage_jwt_fake_valid_token


pytestmark = pytest.mark.usefixtures("db_session")


DEFAULT_UAI = "EAU123"
DEFAULT_RURAL_LEVEL = models.InstitutionRuralLevel.GRANDS_CENTRES_URBAINS


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
        "canPrebook": True,
    }


class AuthenticateTest:
    def test_should_authenticate_redactor(self, client, valid_user):
        redactor = educational_factories.EducationalRedactorFactory(email=valid_user.get("mail"))
        program = educational_factories.EducationalInstitutionProgramFactory()
        institution = educational_factories.EducationalInstitutionFactory(
            institutionId=DEFAULT_UAI,
            programAssociations=[
                educational_factories.EducationalInstitutionProgramAssociationFactory(program=program)
            ],
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

    def test_should_authenticate_redactor_when_program_is_not_associated_to_institution_anymore(
        self, client, valid_user
    ):
        redactor = educational_factories.EducationalRedactorFactory(email=valid_user.get("mail"))
        program = educational_factories.EducationalInstitutionProgramFactory()
        institution = educational_factories.EducationalInstitutionFactory(
            institutionId=DEFAULT_UAI,
            ruralLevel=DEFAULT_RURAL_LEVEL,
        )
        educational_factories.EducationalInstitutionProgramAssociationFactory(
            institutionId=institution.id,
            program=program,
            timespan=db_utils.make_timerange(
                start=date_utils.get_naive_utc_now() - datetime.timedelta(days=2 * 365),
                end=date_utils.get_naive_utc_now() - datetime.timedelta(days=365),
            ),
        )

        valid_encoded_token = self._create_adage_valid_token(valid_user, uai_code=DEFAULT_UAI)

        response = client.with_explicit_token(valid_encoded_token).get("/adage-iframe/authenticate")

        assert response.status_code == 200
        assert response.json == {
            **expected_serialized_auth_base(redactor, institution),
            "institutionRuralLevel": DEFAULT_RURAL_LEVEL.value,
            "programs": [],
        }

    def test_should_return_redactor_role_when_token_has_an_uai_code(self, client, valid_user) -> None:
        # Given
        redactor = educational_factories.EducationalRedactorFactory(email=valid_user.get("mail"))
        institution = educational_factories.EducationalInstitutionFactory(institutionId=valid_user.get("uai"))
        educational_factories.CollectiveStockFactory(
            collectiveOffer__institution=institution,
        )
        educational_factories.CollectiveStockFactory(
            startDatetime=date_utils.get_naive_utc_now() - datetime.timedelta(days=5),
            collectiveOffer__institution=institution,
        )

        valid_encoded_token = self._create_adage_valid_token(valid_user, uai_code=valid_user.get("uai"))

        # When
        response = client.with_explicit_token(valid_encoded_token).get("/adage-iframe/authenticate")

        # Then
        assert response.status_code == 200
        assert response.json == {**expected_serialized_auth_base(redactor, institution), "offersCount": 1}

    def test_favorites_count(self, client) -> None:
        redactor = educational_factories.EducationalRedactorFactory(
            favoriteCollectiveOfferTemplates=[educational_factories.CollectiveOfferTemplateFactory()],
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
        educational_institution = educational_factories.EducationalInstitutionFactory()
        educational_redactor = educational_factories.EducationalRedactorFactory(
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
            "canPrebook": False,
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
        now = date_utils.get_naive_utc_now()
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

    def _create_adage_valid_token(self, valid_user, uai_code: str | None, can_prebook: bool | None = True) -> bytes:
        return create_adage_jwt_default_fake_valid_token(
            civility=valid_user.get("civilite"),
            lastname=valid_user.get("nom"),
            firstname=valid_user.get("prenom"),
            email=valid_user.get("mail"),
            uai=uai_code,
            lat=DEFAULT_LAT,
            lon=DEFAULT_LON,
            can_prebook=can_prebook,
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
