import datetime
from typing import Optional

from flask import url_for
import pytest

from pcapi.core.educational.factories import CollectiveOfferTemplateFactory
from pcapi.core.educational.factories import CollectiveStockFactory
from pcapi.core.educational.factories import EducationalInstitutionFactory
from pcapi.core.educational.factories import EducationalRedactorFactory
from pcapi.core.testing import assert_num_queries

from tests.routes.adage_iframe.utils_create_test_token import DEFAULT_LAT
from tests.routes.adage_iframe.utils_create_test_token import DEFAULT_LON
from tests.routes.adage_iframe.utils_create_test_token import create_adage_jwt_default_fake_valid_token
from tests.routes.adage_iframe.utils_create_test_token import create_adage_jwt_fake_invalid_token
from tests.routes.adage_iframe.utils_create_test_token import create_adage_jwt_fake_valid_token


@pytest.mark.usefixtures("db_session")
class AuthenticateTest:
    valid_user = {
        "mail": "sabine.laprof@example.com",
        "uai": "EAU123",
    }

    def _create_adage_valid_token(self, uai_code: Optional[str]) -> bytes:
        return create_adage_jwt_default_fake_valid_token(
            civility=self.valid_user.get("civilite"),
            lastname=self.valid_user.get("nom"),
            firstname=self.valid_user.get("prenom"),
            email=self.valid_user.get("mail"),
            uai=uai_code,
            lat=DEFAULT_LAT,
            lon=DEFAULT_LON,
        )

    def test_should_return_redactor_role_when_token_has_an_uai_code(self, client) -> None:
        # Given
        EducationalRedactorFactory(email=self.valid_user.get("mail"))
        educational_institution = EducationalInstitutionFactory(
            institutionId=self.valid_user.get("uai"),
            name="BELLEVUE",
            institutionType="COLLEGE",
            postalCode="30100",
            city="Ales",
        )
        CollectiveStockFactory(
            collectiveOffer__institution=educational_institution,
            collectiveOffer__teacher=EducationalRedactorFactory(),
        )
        CollectiveStockFactory(
            beginningDatetime=datetime.datetime.utcnow() - datetime.timedelta(days=5),
            collectiveOffer__institution=educational_institution,
            collectiveOffer__teacher=EducationalRedactorFactory(),
        )

        valid_encoded_token = self._create_adage_valid_token(uai_code=self.valid_user.get("uai"))

        # When
        response = client.with_explicit_token(valid_encoded_token).get("/adage-iframe/authenticate")

        # Then
        assert response.status_code == 200
        assert response.json == {
            "role": "redactor",
            "uai": "EAU123",
            "departmentCode": "30",
            "institutionName": "COLLEGE BELLEVUE",
            "institutionCity": "Ales",
            "email": "sabine.laprof@example.com",
            "preferences": {
                "feedback_form_closed": None,
                "broadcast_help_closed": None,
            },
            "lat": DEFAULT_LAT,
            "lon": DEFAULT_LON,
            "favoritesCount": 0,
            "offersCount": 1,
        }

    def test_favorites_count(self, client) -> None:
        redactor = EducationalRedactorFactory(
            favoriteCollectiveOffers=[CollectiveStockFactory().collectiveOffer],
            favoriteCollectiveOfferTemplates=[CollectiveOfferTemplateFactory()],
        )

        client = client.with_adage_token(email=redactor.email, uai="someuai")

        # fetch the institution
        # fetch the redactor
        # count the redactor's favorites (2 requests: offers and templates)
        # count the offers linked to institution uai
        with assert_num_queries(5):
            response = client.get(url_for("adage_iframe.authenticate"))

        assert response.status_code == 200
        assert response.json["favoritesCount"] == 2

    def test_preferences_are_correctly_serialized(self, client) -> None:
        educational_institution = EducationalInstitutionFactory()
        educational_redactor = EducationalRedactorFactory(
            preferences={"feedback_form_closed": True, "broadcast_help_closed": True}
        )

        client = client.with_adage_token(email=educational_redactor.email, uai=educational_institution.institutionId)
        response = client.get("/adage-iframe/authenticate")

        # Then
        assert response.status_code == 200
        assert response.json["preferences"] == {"broadcast_help_closed": True, "feedback_form_closed": True}

    def test_should_return_readonly_role_when_token_has_no_uai_code(self, client) -> None:
        # Given
        valid_encoded_token = self._create_adage_valid_token(uai_code=None)

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
        }

    valid_user = {
        "civilite": "Mme.",
        "nom": "LAPROF",
        "prenom": "Sabine",
        "mail": "sabine.laprof@example.com",
        "uai": "EAU123",
    }

    def _create_adage_valid_token_from_expiration_date(self, expiration_date: Optional[datetime.datetime]) -> bytes:
        return create_adage_jwt_fake_valid_token(
            civility=self.valid_user.get("civilite"),
            lastname=self.valid_user.get("nom"),
            firstname=self.valid_user.get("prenom"),
            email=self.valid_user.get("mail"),
            uai=self.valid_user.get("uai"),
            expiration_date=expiration_date,
            lat=DEFAULT_LAT,
            lon=DEFAULT_LON,
        )

    @staticmethod
    def _create_adage_invalid_token() -> bytes:
        return create_adage_jwt_fake_invalid_token(
            civility="M.", lastname="TESTABLE", firstname="Pascal", email="pascal.testable@example.com", uai="321UAE"
        )

    def test_should_return_error_response_when_jwt_invalid(self, client):
        # Given
        corrupted_token = self._create_adage_invalid_token()

        # When
        response = client.with_explicit_token(corrupted_token).get("/adage-iframe/authenticate")

        # Then
        assert response.status_code == 403
        assert "Unrecognized token" in response.json["Authorization"]

    def test_should_return_error_response_when_jwt_expired(self, client):
        # Given
        now = datetime.datetime.utcnow()
        expired_token = self._create_adage_valid_token_from_expiration_date(
            expiration_date=now - datetime.timedelta(days=1)
        )

        # When
        response = client.with_explicit_token(expired_token).get("/adage-iframe/authenticate")

        # Then
        assert response.status_code == 422
        assert "Token expired" in response.json["msg"]

    def test_should_return_error_response_when_no_expiration_date_in_token(self, client):
        # Given
        no_expiration_date_token = self._create_adage_valid_token_from_expiration_date(expiration_date=None)

        # When
        response = client.with_explicit_token(no_expiration_date_token).get("/adage-iframe/authenticate")

        # Then
        assert response.status_code == 422
        assert "No expiration date provided" in response.json["msg"]
