import pytest

from pcapi.core.offerers import schemas as offerers_schemas
from pcapi.core.offerers.structure_signup_api import EligibilityDocuments


pytestmark = pytest.mark.usefixtures("db_session")


class Returns200Test:
    collective_message = {
        "importance_level": offerers_schemas.ImportanceLevelMessageSignupSimulation.ALERT.value,
        "content": offerers_schemas.ContentMessageSignupSimulation.COLLECTIVE.value,
    }
    unusual_ape_code = {
        "importance_level": offerers_schemas.ImportanceLevelMessageSignupSimulation.ALERT.value,
        "content": offerers_schemas.ContentMessageSignupSimulation.UNUSUAL_APE_CODE.value,
    }
    bookstore_message = {
        "importance_level": offerers_schemas.ImportanceLevelMessageSignupSimulation.ALERT.value,
        "content": offerers_schemas.ContentMessageSignupSimulation.BOOKSTORE.value,
    }

    def test_nominal(self, client):
        """structure sans message specifique et sans document supplementaire"""
        data = {
            "siret": "11151111111111",
            "isOpenToPublic": True,
            "targets": ["INDIVIDUAL"],
            "activity": "MUSEUM",
        }
        response = client.post("/structure/signup_simulation", json=data)
        assert response.json["eligibilityDocuments"] == [
            EligibilityDocuments.WEBSITE.value,
            EligibilityDocuments.DESCRIPTION.value,
        ]
        assert response.json["messages"] == []

    def test_cas_avec_warnings(self, client):
        """librairie uninomiale a code ape suspect, qui fait du collectf"""
        data = {
            "siret": "11111111111111",
            "isOpenToPublic": True,
            "targets": ["EDUCATIONAL"],
            "activity": "BOOKSTORE",
        }
        response = client.post("/structure/signup_simulation", json=data)
        assert response.json["eligibilityDocuments"] == [
            EligibilityDocuments.WEBSITE.value,
            EligibilityDocuments.DESCRIPTION.value,
            EligibilityDocuments.RESUME_OR_PORTFOLIO.value,
            EligibilityDocuments.DIPLOMAS.value,
            EligibilityDocuments.SHOP_PICTURES.value,
        ]
        assert self.bookstore_message in response.json["messages"]
        assert self.unusual_ape_code in response.json["messages"]
        assert self.collective_message in response.json["messages"]
