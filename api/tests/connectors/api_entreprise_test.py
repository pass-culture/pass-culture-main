import datetime

import pytest
import requests_mock

from pcapi import settings
from pcapi.connectors.entreprise import api
from pcapi.connectors.entreprise import exceptions
from pcapi.core.testing import override_settings

from . import api_entreprise_test_data


@override_settings(ENTREPRISE_BACKEND="pcapi.connectors.entreprise.backends.api_entreprise.EntrepriseBackend")
def test_get_siren_without_address():
    siren = "123456789"
    with requests_mock.Mocker() as mock:
        mock.get(
            f"https://entreprise.api.gouv.fr/v3/insee/sirene/unites_legales/{siren}",
            json=api_entreprise_test_data.RESPONSE_SIREN_COMPANY,
        )
        siren_info = api.get_siren(siren, with_address=False)
        assert siren_info.siren == siren
        assert siren_info.name == "LE PETIT RINTINTIN"
        assert siren_info.head_office_siret == "12345678900012"
        assert siren_info.ape_code == "47.61Z"
        assert siren_info.ape_label == "Commerce de détail de livres en magasin spécialisé"
        assert siren_info.legal_category_code == "5710"
        assert siren_info.address is None
        assert siren_info.active is True
        assert siren_info.diffusible is True


@override_settings(ENTREPRISE_BACKEND="pcapi.connectors.entreprise.backends.api_entreprise.EntrepriseBackend")
def test_get_siren_with_address():
    siren = "123456789"
    with requests_mock.Mocker() as mock:
        mock.get(
            f"https://entreprise.api.gouv.fr/v3/insee/sirene/unites_legales/{siren}/siege_social",
            json=api_entreprise_test_data.RESPONSE_SIRET_COMPANY,
        )
        siren_info = api.get_siren(siren)
        assert siren_info.siren == siren
        assert siren_info.name == "LE PETIT RINTINTIN"
        assert siren_info.head_office_siret == "12345678900012"
        assert siren_info.ape_code == "47.61Z"
        assert siren_info.ape_label == "Commerce de détail de livres en magasin spécialisé"
        assert siren_info.legal_category_code == "5710"
        assert siren_info.address.street == "12 BIS AVENUE DU LIVRE"
        assert siren_info.address.postal_code == "58400"
        assert siren_info.address.city == "LA CHARITE-SUR-LOIRE"
        assert siren_info.active is True
        assert siren_info.diffusible is True

    # Test cache, no HTTP request
    siren_info = api.get_siren(siren)
    assert siren_info.siren == siren


@override_settings(ENTREPRISE_BACKEND="pcapi.connectors.entreprise.backends.api_entreprise.EntrepriseBackend")
def test_get_siren_of_entreprise_individuelle():
    siren = "111222333"
    with requests_mock.Mocker() as mock:
        mock.get(
            f"https://entreprise.api.gouv.fr/v3/insee/sirene/unites_legales/{siren}/siege_social",
            json=api_entreprise_test_data.RESPONSE_SIRET_ENTREPRISE_INDIVIDUELLE,
        )
        siren_info = api.get_siren(siren)
        assert siren_info.siren == siren
        assert siren_info.name == "MARIE SKLODOWSKA CURIE"
        assert siren_info.head_office_siret == "11122233300022"
        assert siren_info.ape_code == "72.19Z"
        assert siren_info.ape_label == "Recherche-développement en autres sciences physiques et naturelles"
        assert siren_info.legal_category_code == "1000"
        assert siren_info.address.street == "36 QUAI DE BETHUNE"
        assert siren_info.address.postal_code == "75004"
        assert siren_info.address.city == "PARIS"
        assert siren_info.active is True
        assert siren_info.diffusible is True


@override_settings(ENTREPRISE_BACKEND="pcapi.connectors.entreprise.backends.api_entreprise.EntrepriseBackend")
def test_get_siren_with_non_public_data():
    siren = "123456789"
    with requests_mock.Mocker() as mock:
        mock.get(
            f"https://entreprise.api.gouv.fr/v3/insee/sirene/unites_legales/{siren}",
            json=api_entreprise_test_data.RESPONSE_SIREN_COMPANY_WITH_NON_PUBLIC_DATA,
        )
        with pytest.raises(exceptions.NonPublicDataException):
            api.get_siren(siren, with_address=False)


@override_settings(ENTREPRISE_BACKEND="pcapi.connectors.entreprise.backends.api_entreprise.EntrepriseBackend")
def test_get_siren_with_non_public_data_do_not_raise():
    siren = "987654321"
    with requests_mock.Mocker() as mock:
        mock.get(
            f"https://entreprise.api.gouv.fr/v3/insee/sirene/unites_legales/{siren}/siege_social",
            json=api_entreprise_test_data.RESPONSE_SIRET_COMPANY_WITH_NON_PUBLIC_DATA,
        )
        siren_info = api.get_siren(siren, raise_if_non_public=False)
        assert siren_info.siren == siren
        assert siren_info.name == "GEORGE DUPIN SAND"
        assert siren_info.head_office_siret == "98765432100016"
        assert siren_info.ape_code == "90.03B"
        assert siren_info.ape_label == "Autre création artistique"
        assert siren_info.legal_category_code == "1000"
        assert siren_info.address.street == "31 RUE DE SEINE"
        assert siren_info.address.postal_code == "75006"
        assert siren_info.address.city == "PARIS"
        assert siren_info.active is True
        assert siren_info.diffusible is False


@override_settings(ENTREPRISE_BACKEND="pcapi.connectors.entreprise.backends.api_entreprise.EntrepriseBackend")
def test_get_siren_of_inactive_company():
    siren = "777888999"
    with requests_mock.Mocker() as mock:
        mock.get(
            f"https://entreprise.api.gouv.fr/v3/insee/sirene/unites_legales/{siren}",
            json=api_entreprise_test_data.RESPONSE_SIREN_INACTIVE_COMPANY,
        )
        siren_info = api.get_siren(siren, with_address=False)
        assert siren_info.siren == siren
        assert siren_info.name == "LE RIDEAU FERME"
        assert siren_info.head_office_siret == "77788899900021"
        assert siren_info.ape_code == "90.01Z"
        assert siren_info.ape_label == "Arts du spectacle vivant"
        assert siren_info.legal_category_code == "5499"
        assert siren_info.address is None
        assert siren_info.active is False
        assert siren_info.diffusible is True


@override_settings(ENTREPRISE_BACKEND="pcapi.connectors.entreprise.backends.api_entreprise.EntrepriseBackend")
def test_get_siren_invalid_parameter():
    siren = settings.PASS_CULTURE_SIRET[:9]
    with requests_mock.Mocker() as mock:
        mock.get(
            f"https://entreprise.api.gouv.fr/v3/insee/sirene/unites_legales/{siren}/siege_social",
            status_code=422,
            json=api_entreprise_test_data.RESPONSE_SIREN_ERROR_422,
        )
        with pytest.raises(exceptions.ApiException) as error:
            api.get_siren(siren)
        assert (
            str(error.value)
            == "Le paramètre recipient est identique au SIRET/SIREN appelé, or ce paramètre de traçabilité doit "
            "correspondre au SIRET de l'organisation publique habilitée à utiliser la donnée. Si vous êtes une "
            "collectivité ou une administration, ce paramètre doit donc être votre numéro de SIRET ; si vous êtes un "
            "éditeur, il s'agit du SIRET de l'organisation publique cliente demandant la donnée."
        )


@override_settings(ENTREPRISE_BACKEND="pcapi.connectors.entreprise.backends.api_entreprise.EntrepriseBackend")
def test_get_siret():
    siret = "12345678900017"
    with requests_mock.Mocker() as mock:
        mock.get(
            f"https://entreprise.api.gouv.fr/v3/insee/sirene/etablissements/{siret}",
            json=api_entreprise_test_data.RESPONSE_SIRET_COMPANY,
        )
        siret_info = api.get_siret(siret)
        assert siret_info.siret == siret
        assert siret_info.name == "LE PETIT RINTINTIN"
        assert siret_info.address.street == "12 BIS AVENUE DU LIVRE"
        assert siret_info.address.postal_code == "58400"
        assert siret_info.address.city == "LA CHARITE-SUR-LOIRE"
        assert siret_info.ape_code == "47.61Z"
        assert siret_info.ape_label == "Commerce de détail de livres en magasin spécialisé"
        assert siret_info.legal_category_code == "5710"
        assert siret_info.active is True
        assert siret_info.diffusible is True

    # Test cache, no HTTP request
    siret_info = api.get_siret(siret)
    assert siret_info.siret == siret


@override_settings(ENTREPRISE_BACKEND="pcapi.connectors.entreprise.backends.api_entreprise.EntrepriseBackend")
def test_get_siret_of_entreprise_individuelle():
    siret = "12345678900045"
    with requests_mock.Mocker() as mock:
        mock.get(
            f"https://entreprise.api.gouv.fr/v3/insee/sirene/etablissements/{siret}",
            json=api_entreprise_test_data.RESPONSE_SIRET_ENTREPRISE_INDIVIDUELLE,
        )
        siret_info = api.get_siret(siret)
        assert siret_info.siret == siret
        assert siret_info.name == "MARIE SKLODOWSKA CURIE"
        assert siret_info.address.street == "36 QUAI DE BETHUNE"
        assert siret_info.address.postal_code == "75004"
        assert siret_info.address.city == "PARIS"
        assert siret_info.ape_code == "72.19Z"
        assert siret_info.ape_label == "Recherche-développement en autres sciences physiques et naturelles"
        assert siret_info.legal_category_code == "1000"
        assert siret_info.active is True
        assert siret_info.diffusible is True


@override_settings(ENTREPRISE_BACKEND="pcapi.connectors.entreprise.backends.api_entreprise.EntrepriseBackend")
def test_get_siret_with_non_public_data():
    siret = "12345678900017"
    with requests_mock.Mocker() as mock:
        mock.get(
            f"https://entreprise.api.gouv.fr/v3/insee/sirene/etablissements/{siret}",
            json=api_entreprise_test_data.RESPONSE_SIRET_COMPANY_WITH_NON_PUBLIC_DATA,
        )
        with pytest.raises(exceptions.NonPublicDataException):
            api.get_siret(siret)


@override_settings(ENTREPRISE_BACKEND="pcapi.connectors.entreprise.backends.api_entreprise.EntrepriseBackend")
def test_get_siret_with_non_public_data_do_not_raise():
    siret = "12345678900017"
    with requests_mock.Mocker() as mock:
        mock.get(
            f"https://entreprise.api.gouv.fr/v3/insee/sirene/etablissements/{siret}",
            json=api_entreprise_test_data.RESPONSE_SIRET_COMPANY_WITH_NON_PUBLIC_DATA,
        )
        siret_info = api.get_siret(siret, raise_if_non_public=False)
        assert siret_info.siret == siret
        assert siret_info.name == "GEORGE DUPIN SAND"
        assert siret_info.address.street == "31 RUE DE SEINE"
        assert siret_info.address.postal_code == "75006"
        assert siret_info.address.city == "PARIS"
        assert siret_info.ape_code == "90.03B"
        assert siret_info.ape_label == "Autre création artistique"
        assert siret_info.legal_category_code == "1000"
        assert siret_info.active is True
        assert siret_info.diffusible is False


@override_settings(ENTREPRISE_BACKEND="pcapi.connectors.entreprise.backends.api_entreprise.EntrepriseBackend")
def test_get_siret_of_inactive_company():
    siret = "77788899900021"
    with requests_mock.Mocker() as mock:
        mock.get(
            f"https://entreprise.api.gouv.fr/v3/insee/sirene/etablissements/{siret}",
            json=api_entreprise_test_data.RESPONSE_SIRET_INACTIVE_COMPANY,
        )
        siret_info = api.get_siret(siret)
        assert siret_info.siret == siret
        assert siret_info.name == "LE RIDEAU FERME"
        assert siret_info.address.street == "OCCI"
        assert siret_info.address.postal_code == "20260"
        assert siret_info.address.city == "LUMIO"
        assert siret_info.ape_code == "90.01Z"
        assert siret_info.ape_label == "Arts du spectacle vivant"
        assert siret_info.legal_category_code == "5499"
        assert siret_info.active is False
        assert siret_info.diffusible is True


@pytest.mark.parametrize(
    "status_code,expected_exception",
    [
        (400, exceptions.ApiException),
        (401, exceptions.ApiException),
        (403, exceptions.ApiException),
        (404, exceptions.UnknownEntityException),
        (422, exceptions.ApiException),
        (429, exceptions.RateLimitExceeded),
        (451, exceptions.NonPublicDataException),
        (500, exceptions.ApiException),
        (502, exceptions.ApiException),
        (503, exceptions.ApiException),
        (504, exceptions.ApiException),
    ],
)
@override_settings(ENTREPRISE_BACKEND="pcapi.connectors.entreprise.backends.api_entreprise.EntrepriseBackend")
def test_error_handling(status_code, expected_exception):
    siret = "invalid"
    with requests_mock.Mocker() as mock:
        mock.get(
            f"https://entreprise.api.gouv.fr/v3/insee/sirene/etablissements/{siret}",
            status_code=status_code,
        )
        with pytest.raises(expected_exception):
            api.get_siret(siret)


@override_settings(ENTREPRISE_BACKEND="pcapi.connectors.entreprise.backends.api_entreprise.EntrepriseBackend")
def test_error_handling_on_non_json_response():
    siret = "anything"
    with requests_mock.Mocker() as mock:
        mock.get(
            f"https://entreprise.api.gouv.fr/v3/insee/sirene/etablissements/{siret}",
            status_code=200,
            text="non-JSON content",
        )
        with pytest.raises(exceptions.ApiException):
            api.get_siret(siret)


@override_settings(ENTREPRISE_BACKEND="pcapi.connectors.entreprise.backends.api_entreprise.EntrepriseBackend")
def test_get_rcs_registered():
    siren = "123456789"
    with requests_mock.Mocker() as mock:
        mock.get(
            f"https://entreprise.api.gouv.fr/v3/infogreffe/rcs/unites_legales/{siren}/extrait_kbis",
            json=api_entreprise_test_data.RESPONSE_RCS_REGISTERED_COMPANY,
        )
        rcs_info = api.get_rcs(siren)
        assert rcs_info.registered is True
        assert rcs_info.registration_date == datetime.date(2024, 1, 1)
        assert rcs_info.deregistration_date is None
        assert rcs_info.head_office_activity == "TESTER L'INTEGRATION D'API ENTREPRISE"
        assert len(rcs_info.corporate_officers) == 1
        assert rcs_info.corporate_officers[0].name == "PIERRE EXEMPLE"
        assert rcs_info.corporate_officers[0].role == "PRESIDENT"
        assert not rcs_info.observations


@override_settings(ENTREPRISE_BACKEND="pcapi.connectors.entreprise.backends.api_entreprise.EntrepriseBackend")
def test_get_rcs_deregistered():
    siren = "123456789"
    with requests_mock.Mocker() as mock:
        mock.get(
            f"https://entreprise.api.gouv.fr/v3/infogreffe/rcs/unites_legales/{siren}/extrait_kbis",
            json=api_entreprise_test_data.RESPONSE_RCS_DEREGISTERED_COMPANY,
        )
        rcs_info = api.get_rcs(siren)
        assert rcs_info.registered is True
        assert rcs_info.registration_date == datetime.date(2024, 1, 1)
        assert rcs_info.deregistration_date == datetime.date(2024, 2, 5)
        assert rcs_info.head_office_activity == "TESTER L'INTEGRATION D'API ENTREPRISE"
        assert len(rcs_info.corporate_officers) == 1
        assert rcs_info.corporate_officers[0].name == "PIERRE EXEMPLE"
        assert rcs_info.corporate_officers[0].role == "PRESIDENT"
        assert len(rcs_info.observations) == 2
        assert rcs_info.observations[0].date == datetime.date(2024, 1, 15)
        assert rcs_info.observations[0].label == "PREMIERE OBSERVATION"
        assert rcs_info.observations[1].date == datetime.date(2024, 2, 3)
        assert rcs_info.observations[1].label == "DEUXIEME OBSERVATION"


@override_settings(ENTREPRISE_BACKEND="pcapi.connectors.entreprise.backends.api_entreprise.EntrepriseBackend")
def test_get_rcs_not_registered():
    siren = "123456789"
    with requests_mock.Mocker() as mock:
        mock.get(
            f"https://entreprise.api.gouv.fr/v3/infogreffe/rcs/unites_legales/{siren}/extrait_kbis",
            status_code=404,
            json=api_entreprise_test_data.RESPONSE_RCS_NOT_REGISTERED_404,
        )
        rcs_info = api.get_rcs(siren)
        assert rcs_info.registered is False


@override_settings(ENTREPRISE_BACKEND="pcapi.connectors.entreprise.backends.api_entreprise.EntrepriseBackend")
def test_get_urssaf_ok():
    siren = "123456789"
    with requests_mock.Mocker() as mock:
        mock.get(
            f"https://entreprise.api.gouv.fr/v4/urssaf/unites_legales/{siren}/attestation_vigilance",
            json=api_entreprise_test_data.RESPONSE_URSSAF_OK,
        )
        urssaf_info = api.get_urssaf(siren)
        assert urssaf_info.attestation_delivered is True
        assert (
            urssaf_info.details
            == "La délivrance de l'attestation de vigilance a été validée par l'Urssaf. L'attestation est délivrée "
            "lorsque l'entité est à jour de ses cotisations et contributions, ou bien dans le cas de situations "
            "spécifiques détaillées dans la documentation métier."
        )
        assert urssaf_info.validity_start_date == datetime.date(2023, 11, 30)
        assert urssaf_info.validity_end_date == datetime.date(2024, 5, 31)
        assert urssaf_info.verification_code == "ABCD1234EFGH567"


@override_settings(ENTREPRISE_BACKEND="pcapi.connectors.entreprise.backends.api_entreprise.EntrepriseBackend")
def test_get_urssaf_refused():
    siren = "123456789"
    with requests_mock.Mocker() as mock:
        mock.get(
            f"https://entreprise.api.gouv.fr/v4/urssaf/unites_legales/{siren}/attestation_vigilance",
            json=api_entreprise_test_data.RESPONSE_URSSAF_REFUSED,
        )
        urssaf_info = api.get_urssaf(siren)
        assert urssaf_info.attestation_delivered is False
        assert (
            urssaf_info.details
            == "La délivrance de l'attestation de vigilance a été refusée par l'Urssaf car l'entité n'est pas à jour "
            "de ses cotisations sociales."
        )
        assert urssaf_info.validity_start_date is None
        assert urssaf_info.validity_end_date is None
        assert urssaf_info.verification_code is None


@override_settings(ENTREPRISE_BACKEND="pcapi.connectors.entreprise.backends.api_entreprise.EntrepriseBackend")
def test_get_urssaf_not_found():
    siren = "123456789"
    with requests_mock.Mocker() as mock:
        mock.get(
            f"https://entreprise.api.gouv.fr/v4/urssaf/unites_legales/{siren}/attestation_vigilance",
            status_code=404,
            json=api_entreprise_test_data.RESPONSE_URSSAF_ERROR_404,
        )
        with pytest.raises(exceptions.UnknownEntityException) as error:
            api.get_urssaf(siren)
        assert str(error.value) == "Le siren est inconnu du SI Attestations, radié ou hors périmètre"


@override_settings(ENTREPRISE_BACKEND="pcapi.connectors.entreprise.backends.api_entreprise.EntrepriseBackend")
def test_get_dgfip_ok():
    siren = "123456789"
    with requests_mock.Mocker() as mock:
        mock.get(
            f"https://entreprise.api.gouv.fr/v4/dgfip/unites_legales/{siren}/attestation_fiscale",
            json=api_entreprise_test_data.RESPONSE_DGFIP_OK,
        )
        dgfip_info = api.get_dgfip(siren)
        assert dgfip_info.attestation_delivered is True


@override_settings(ENTREPRISE_BACKEND="pcapi.connectors.entreprise.backends.api_entreprise.EntrepriseBackend")
def test_get_dgfip_entreprise_individuelle():
    siren = "123456789"
    with requests_mock.Mocker() as mock:
        mock.get(
            f"https://entreprise.api.gouv.fr/v4/dgfip/unites_legales/{siren}/attestation_fiscale",
            status_code=502,
            json=api_entreprise_test_data.RESPONSE_DGFIP_ENTREPRISE_INDIVIDUELLE_502,
        )
        with pytest.raises(exceptions.ApiUnavailable) as error:
            api.get_dgfip(siren)
        assert (
            str(error.value)
            == "La réponse retournée par le fournisseur de données est invalide et inconnue de notre service. L'équipe "
            "technique a été notifiée de cette erreur pour investigation."
        )


@override_settings(ENTREPRISE_BACKEND="pcapi.connectors.entreprise.backends.api_entreprise.EntrepriseBackend")
def test_get_dgfip_inactive_company():
    siren = "123456789"
    with requests_mock.Mocker() as mock:
        mock.get(
            f"https://entreprise.api.gouv.fr/v4/dgfip/unites_legales/{siren}/attestation_fiscale",
            status_code=404,
            json=api_entreprise_test_data.RESPONSE_DGFIP_INACTIVE_COMPANY_404,
        )
        with pytest.raises(exceptions.UnknownEntityException) as error:
            api.get_dgfip(siren)
        assert (
            str(error.value)
            == "L'identifiant indiqué n'existe pas, n'est pas connu ou ne comporte aucune information pour cet appel."
        )
