import json

import pytest

from pcapi.connectors.cgr.cgr import get_cgr_service_proxy
from pcapi.connectors.cgr.cgr import get_seances_pass_culture
import pcapi.connectors.cgr.exceptions as cgr_exceptions
import pcapi.core.providers.factories as providers_factories
from pcapi.core.testing import override_settings

from tests.connectors.cgr import soap_definitions


class CGRGetServiceProxyTest:
    def test_should_return_service_proxy(self, requests_mock):
        requests_mock.get("http://example.com/web_service?wsdl", text=soap_definitions.WEB_SERVICE_DEFINITION)

        service = get_cgr_service_proxy(cinema_url="http://example.com/web_service")

        assert service._binding_options["address"] == "http://example.com/web_service"
        assert service._operations["GetSeancesPassCulture"]


def _get_seances_pass_culture_xml_response_template(body_response: str) -> str:
    return f"""
       <?xml version="1.0" encoding="UTF-8"?>
        <SOAP-ENV:Envelope
            xmlns:xsd="http://www.w3.org/2001/XMLSchema"
            xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
            xmlns:SOAP-ENV="http://schemas.xmlsoap.org/soap/envelope/">
            <SOAP-ENV:Header/>
            <SOAP-ENV:Body>
                <ns1:GetSeancesPassCultureResponse xmlns:ns1="urn:GestionCinemaWS">
                    <GetSeancesPassCultureResult>
                        {body_response}
                    </GetSeancesPassCultureResult>
                </ns1:GetSeancesPassCultureResponse>
            </SOAP-ENV:Body>
        </SOAP-ENV:Envelope>
        """.strip()


@pytest.mark.usefixtures("db_session")
class CGRGetSeancesPassCultureTest:
    @override_settings(CGR_API_USER="pass_user", CGR_API_PASSWORD="password")
    def test_should_return_pass_culture_shows(self, requests_mock):
        requests_mock.get("http://example.com/web_service?wsdl", text=soap_definitions.WEB_SERVICE_DEFINITION)
        json_response = {
            "CodeErreur": 0,
            "IntituleErreur": "",
            "ObjetRetour": {
                "NumCine": 999,
                "Films": [
                    {
                        "IDFilm": 307554,
                        "IDFilmAlloCine": 307554,
                        "Titre": "André Rieu In Dublin 2023",
                        "NumVisa": 2022006180,
                        "Duree": 138,
                        "Synopsis": "Andr\\u00e9 Rieu est de retour dans les salles obscures pour c\\u00e9l\\u00e9brer la nouvelle ann\\u00e9e !Visitez l'\\u00eele d'Emeraude depuis votre cin\\u00e9ma en compagnie d'Andr\\u00e9 Rieu pour son premier concert film\\u00e9 dans la charmante capitale irlandaise.Rejoignez le maestro et son Johann Strauss Orchestra : des sopranos, des t\\u00e9nors et des invit\\u00e9s pour une f\\u00eate fantastique avec des m\\u00e9lodies romantiques, des classiques populaires, des airs joyeux et des valses entra\\u00eenantes.Un rendez-vous pour toute la famille pour vivre cette exp\\u00e9rience inoubliable de musique et de danse film\\u00e9e \\u00e0 Dublin. C\\u00e9ad M\\u00edle F\\u00e1ilte !",
                        "Affiche": "https://example.com/2022006180.jpg",
                        "TypeFilm": "OPERA",
                        "Seances": [
                            {
                                "IDSeance": 177182,
                                "Date": "2023-01-29",
                                "Heure": "14:00:00.000",
                                "NbPlacesRestantes": 99,
                                "bAvecPlacement": True,
                                "bAvecDuo": True,
                                "bICE": True,
                                "Relief": "2D",
                                "Version": "VF",
                                "bAVP": False,
                                "PrixUnitaire": 11,
                            },
                        ],
                    },
                ],
            },
        }
        response = _get_seances_pass_culture_xml_response_template(json.dumps(json_response))
        requests_mock.post("http://example.com/web_service", text=response)
        cgr_cinema_details = providers_factories.CGRCinemaDetailsFactory(cinemaUrl="http://example.com/web_service")

        result = get_seances_pass_culture(cinema_details=cgr_cinema_details)

        assert result.CodeErreur == 0
        assert result.IntituleErreur == ""
        assert result.ObjetRetour.NumCine == 999
        assert isinstance(result.ObjetRetour.Films, list)

    @override_settings(CGR_API_USER="pass_user", CGR_API_PASSWORD="password")
    def test_should_raise_if_error(self, requests_mock):
        requests_mock.get("http://example.com/web_service?wsdl", text=soap_definitions.WEB_SERVICE_DEFINITION)
        json_response = {"CodeErreur": -1, "IntituleErreur": "Expectation failed", "ObjetRetour": None}
        response = _get_seances_pass_culture_xml_response_template(json.dumps(json_response))
        requests_mock.post("http://example.com/web_service", text=response)
        cgr_cinema_details = providers_factories.CGRCinemaDetailsFactory(cinemaUrl="http://example.com/web_service")

        with pytest.raises(cgr_exceptions.CGRAPIException) as exc:
            get_seances_pass_culture(cinema_details=cgr_cinema_details)

        assert isinstance(exc.value, cgr_exceptions.CGRAPIException)
        assert str(exc.value) == "Error on CGR API on GetSeancesPassCulture : Expectation failed"
