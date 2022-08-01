from unittest.mock import MagicMock
from unittest.mock import patch

import pytest

from pcapi.connectors import api_entreprises
from pcapi.connectors.api_entreprises import ApiEntrepriseException
from pcapi.connectors.api_entreprises import get_by_offerer
from pcapi.connectors.api_entreprises import get_offerer_legal_category
from pcapi.connectors.utils.legal_category_code_to_labels import CODE_TO_CATEGORY_MAPPING
import pcapi.core.offerers.factories as offerers_factories
from pcapi.core.testing import override_settings
from pcapi.model_creators.generic_creators import create_offerer


class GetByOffererTest:
    @patch("pcapi.connectors.api_entreprises.requests.get")
    def test_raises_ApiEntrepriseException_when_sirene_api_does_not_respond(self, requests_get):
        # Given
        requests_get.return_value = MagicMock(status_code=400)

        offerer = create_offerer(siren="732075312")

        # When
        with pytest.raises(ApiEntrepriseException) as error:
            get_by_offerer(offerer)

        # Then
        assert "Error getting API entreprise DATA for SIREN" in str(error.value)

    @patch("pcapi.connectors.api_entreprises.requests.get")
    def test_call_sirene_with_offerer_siren(self, requests_get):
        # Given
        offerer = create_offerer(siren="732075312")
        json_response = {
            "unite_legale": {
                "siren": "395251440",
                "denomination": "UGC CINE CITE ILE DE FRANCE",
                "etablissement_siege": {
                    "siren": "395251440",
                    "siret": "39525144000016",
                },
                "etablissements": [],
            }
        }
        mocked_api_response = MagicMock(status_code=200, text="")
        mocked_api_response.json = MagicMock(return_value=json_response)
        requests_get.return_value = mocked_api_response

        # When
        get_by_offerer(offerer)

        # Then
        requests_get.assert_called_once_with("https://entreprise.data.gouv.fr/api/sirene/v3/unites_legales/732075312")

    @patch("pcapi.connectors.api_entreprises.requests.get")
    def test_returns_unite_legale_informations_with_etablissement_siege(self, requests_get):
        # Given
        offerer = create_offerer(siren="732075312")

        mocked_api_response = MagicMock(status_code=200)
        requests_get.return_value = mocked_api_response

        json_response = {
            "unite_legale": {
                "siren": "395251440",
                "denomination": "UGC CINE CITE ILE DE FRANCE",
                "etablissement_siege": {
                    "siren": "395251440",
                    "siret": "39525144000016",
                },
                "etablissements": [],
            }
        }
        mocked_api_response = MagicMock(status_code=200, text="")
        mocked_api_response.json = MagicMock(return_value=json_response)
        requests_get.return_value = mocked_api_response

        # When
        response = get_by_offerer(offerer)

        # Then
        assert response == json_response

    @patch("pcapi.connectors.api_entreprises.requests.get")
    def test_returns_unite_legale_informations_without_etablissements_list(self, requests_get):
        # Given
        offerer = create_offerer(siren="732075312")

        mocked_api_response = MagicMock(status_code=200)
        requests_get.return_value = mocked_api_response

        json_response = {
            "unite_legale": {
                "siren": "395251440",
                "denomination": "UGC CINE CITE ILE DE FRANCE",
                "etablissement_siege": {
                    "siren": "395251440",
                    "siret": "39525144000016",
                    "etablissement_siege": "true",
                },
                "etablissements": [
                    {
                        "siren": "395251440",
                        "siret": "39525144000032",
                        "etablissement_siege": "true",
                        "enseigne_1": "UGC CAFE",
                    }
                ],
            }
        }
        mocked_api_response = MagicMock(status_code=200, text="")
        mocked_api_response.json = MagicMock(return_value=json_response)
        requests_get.return_value = mocked_api_response

        # When
        response = get_by_offerer(offerer)

        # Then
        assert "etablissements" not in response["unite_legale"]

    @patch("pcapi.connectors.api_entreprises.get_by_offerer")
    @patch.dict(CODE_TO_CATEGORY_MAPPING, {5202: "Société en nom collectif"})
    def test_returns_legal_category_code_and_label(self, get_by_offerer_mock):
        offerer = create_offerer(siren="395251440")

        get_by_offerer_mock.return_value = {
            "unite_legale": {
                "siren": "395251440",
                "denomination": "UGC CINE CITE ILE DE FRANCE",
                "categorie_juridique": "5202",
                "etablissement_siege": {
                    "siren": "395251440",
                    "siret": "39525144000016",
                },
                "etablissements": [],
            }
        }

        legal_category = get_offerer_legal_category(offerer)
        assert legal_category["legal_category_code"] == "5202"
        assert legal_category["legal_category_label"] == "Société en nom collectif"

    @patch("pcapi.connectors.api_entreprises.get_by_offerer")
    @patch.dict(CODE_TO_CATEGORY_MAPPING, {5202: "Société en nom collectif"})
    def test_returns_legal_category_code_and_label_when_no_label_matches_to_code(self, get_by_offerer_mock):
        offerer = create_offerer(siren="395251440")

        get_by_offerer_mock.return_value = {
            "unite_legale": {
                "siren": "395251440",
                "denomination": "UGC CINE CITE ILE DE FRANCE",
                "categorie_juridique": "5201",
                "etablissement_siege": {
                    "siren": "395251440",
                    "siret": "39525144000016",
                },
                "etablissements": [],
            }
        }

        legal_category = get_offerer_legal_category(offerer)
        assert legal_category["legal_category_code"] == "5201"
        assert legal_category["legal_category_label"] is None

    @patch("pcapi.connectors.api_entreprises.get_by_offerer")
    @patch.dict(CODE_TO_CATEGORY_MAPPING, {5202: "Société en nom collectif"})
    def test_returns_legal_category_code_and_label_when_code_is_none(self, get_by_offerer_mock):
        offerer = create_offerer(siren="395251440")

        get_by_offerer_mock.return_value = {
            "unite_legale": {
                "siren": "395251440",
                "denomination": "UGC CINE CITE ILE DE FRANCE",
                "categorie_juridique": None,
                "etablissement_siege": {
                    "siren": "395251440",
                    "siret": "39525144000016",
                },
                "etablissements": [],
            }
        }

        legal_category = get_offerer_legal_category(offerer)
        assert legal_category["legal_category_code"] is None
        assert legal_category["legal_category_label"] is None


@pytest.mark.usefixtures("db_session")
class GetOffererLegalCategoryTest:
    @patch("pcapi.connectors.api_entreprises.get_by_offerer")
    def test_successful_get_by_offerer(self, mocked_get_by_offerer):
        mocked_get_by_offerer.return_value = {
            "unite_legale": {
                "categorie_juridique": "5202",
            }
        }
        offerer = offerers_factories.OffererFactory()

        assert get_offerer_legal_category(offerer) == {
            "legal_category_code": "5202",
            "legal_category_label": "Société en nom collectif",
        }

    @patch("pcapi.connectors.api_entreprises.get_by_offerer")
    @override_settings(IS_PROD=True)
    def test_handle_error_get_by_offerer_on_prod_env(self, mocked_get_by_offerer):
        mocked_get_by_offerer.side_effect = [ApiEntrepriseException()]
        offerer = offerers_factories.OffererFactory()

        assert get_offerer_legal_category(offerer) == {
            "legal_category_code": "Donnée indisponible",
            "legal_category_label": "Donnée indisponible",
        }

    @patch("pcapi.connectors.api_entreprises.get_by_offerer")
    def test_handle_error_get_by_offerer_on_non_prod_env(self, mocked_get_by_offerer):
        mocked_get_by_offerer.side_effect = [ApiEntrepriseException]
        offerer = offerers_factories.OffererFactory()

        assert get_offerer_legal_category(offerer) == {
            "legal_category_code": "Donnée indisponible",
            "legal_category_label": "Donnée indisponible",
        }


class CheckSiretIsStillActiveTest:
    @pytest.mark.parametrize("remote_status,expected", [("A", True), ("F", False)])
    def test_check_siret_is_still_active(self, remote_status, expected, requests_mock):
        # Given
        json_response = {"etablissement": {"etat_administratif": remote_status}}
        requests_mock.register_uri(
            "GET",
            "https://entreprise.data.gouv.fr/api/sirene/v3/etablissements/1234567",
            json=json_response,
            status_code=200,
        )

        # When
        result = api_entreprises.check_siret_is_still_active("1234567")

        # Then
        assert result == expected
