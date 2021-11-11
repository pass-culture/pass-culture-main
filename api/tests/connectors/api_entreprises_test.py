from unittest.mock import MagicMock
from unittest.mock import patch

import pytest

from pcapi.connectors.api_entreprises import ApiEntrepriseException
from pcapi.connectors.api_entreprises import get_by_offerer
from pcapi.connectors.api_entreprises import get_offerer_legal_category
from pcapi.connectors.utils.legal_category_code_to_labels import CODE_TO_CATEGORY_MAPPING
from pcapi.core.offers import factories as offers_factories
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
        requests_get.assert_called_once_with(
            "https://entreprise.data.gouv.fr/api/sirene/v3/unites_legales/732075312", verify=False
        )

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

    @patch("pcapi.connectors.api_entreprises.requests.get")
    def test_returns_unite_legale_informations_with_empty_other_etablissements_sirets_when_no_other_etablissements(
        self, requests_get
    ):
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
        assert response["other_etablissements_sirets"] == []

    @patch("pcapi.connectors.api_entreprises.requests.get")
    def test_returns_other_etablissements_sirets_with_all_etablissement_siret(self, requests_get):
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
                        "etablissement_siege": "false",
                        "enseigne_1": "UGC CAFE",
                    },
                    {
                        "siren": "395251440",
                        "siret": "39525144000065",
                        "etablissement_siege": "false",
                        "enseigne_1": "UGC CINE CITE BERCY - UGC CAFE",
                    },
                ],
            }
        }
        mocked_api_response = MagicMock(status_code=200, text="")
        mocked_api_response.json = MagicMock(return_value=json_response)
        requests_get.return_value = mocked_api_response

        # When
        response = get_by_offerer(offerer)

        # Then
        assert set(response["other_etablissements_sirets"]) == {"39525144000032", "39525144000065"}

    @patch("pcapi.connectors.api_entreprises.requests.get")
    def test_returns_other_etablissements_sirets_without_etablissement_siege_siret(self, requests_get):
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
                        "etablissement_siege": "false",
                        "enseigne_1": "UGC CAFE",
                    },
                    {
                        "siren": "395251440",
                        "siret": "39525144000016",
                        "etablissement_siege": "true",
                    },
                ],
            }
        }
        mocked_api_response = MagicMock(status_code=200, text="")
        mocked_api_response.json = MagicMock(return_value=json_response)
        requests_get.return_value = mocked_api_response

        # When
        response = get_by_offerer(offerer)

        # Then
        assert set(response["other_etablissements_sirets"]) == {"39525144000032"}

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
        offerer = offers_factories.OffererFactory()

        assert get_offerer_legal_category(offerer) == {
            "legal_category_code": "5202",
            "legal_category_label": "Société en nom collectif",
        }

    @patch("pcapi.connectors.api_entreprises.get_by_offerer")
    @override_settings(IS_PROD=True)
    def test_error_get_by_offerer_on_prod_env(self, mocked_get_by_offerer):
        mocked_get_by_offerer.side_effect = [
            ApiEntrepriseException("Error getting API entreprise DATA for SIREN : xxx")
        ]
        offerer = offers_factories.OffererFactory()

        with pytest.raises(ApiEntrepriseException) as error:
            get_offerer_legal_category(offerer)

        assert "Error getting API entreprise DATA for SIREN : xxx" in str(error.value)

    @patch("pcapi.connectors.api_entreprises.get_by_offerer")
    def test_error_get_by_offerer_on_non_prod_env(self, mocked_get_by_offerer):
        mocked_get_by_offerer.side_effect = [ApiEntrepriseException]
        offerer = offers_factories.OffererFactory()

        assert get_offerer_legal_category(offerer) == {
            "legal_category_code": "XXXX",
            "legal_category_label": "Catégorie factice (hors Prod)",
        }
