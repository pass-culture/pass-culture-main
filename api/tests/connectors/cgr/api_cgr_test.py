import json

import pytest

import pcapi.core.external_bookings.cgr.exceptions as cgr_exceptions
import pcapi.core.providers.factories as providers_factories
from pcapi.connectors.cgr.cgr import get_cgr_service_proxy
from pcapi.connectors.cgr.cgr import get_seances_pass_culture
from pcapi.utils.crypto import encrypt

from tests.connectors.cgr import soap_definitions
from tests.local_providers.cinema_providers.cgr import fixtures


class CGRGetServiceProxyTest:
    def test_should_return_service_proxy(self, requests_mock):
        requests_mock.get("http://example.com/web_service?wsdl", text=soap_definitions.WEB_SERVICE_DEFINITION)

        service = get_cgr_service_proxy(cinema_url="http://example.com/web_service")

        assert service._binding_options["address"] == "http://example.com/web_service"
        assert service._operations["GetSeancesPassCulture"]

    def test_cache_wsdl_files(self, requests_mock):
        # Use a different service url than before
        adapter = requests_mock.get(
            "http://example.com/another_web_service?wsdl", text=soap_definitions.WEB_SERVICE_DEFINITION
        )

        get_cgr_service_proxy(cinema_url="http://example.com/another_web_service")
        get_cgr_service_proxy(cinema_url="http://example.com/another_web_service")
        get_cgr_service_proxy(cinema_url="http://example.com/another_web_service")

        assert adapter.call_count == 1


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
    @pytest.mark.settings(CGR_API_USER="pass_user")
    def test_should_return_pass_culture_shows(self, requests_mock):
        requests_mock.get("http://example.com/web_service?wsdl", text=soap_definitions.WEB_SERVICE_DEFINITION)
        requests_mock.post(
            "http://example.com/web_service", text=fixtures.cgr_response_template([fixtures.FILM_138473])
        )
        cgr_cinema_details = providers_factories.CGRCinemaDetailsFactory(cinemaUrl="http://example.com/web_service")

        result = get_seances_pass_culture(cinema_details=cgr_cinema_details, request_timeout=14)

        assert requests_mock.request_history[-1].method == "POST"
        assert requests_mock.request_history[-1].timeout == 14

        assert result.CodeErreur == 0
        assert result.IntituleErreur == ""
        assert result.ObjetRetour.NumCine == 999
        assert isinstance(result.ObjetRetour.Films, list)

    @pytest.mark.settings(CGR_API_USER="pass_user")
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

    @pytest.mark.settings(CGR_API_USER="pass_user")
    def test_should_call_with_the_right_password(self, requests_mock):
        requests_mock.get("http://example.com/web_service?wsdl", text=soap_definitions.WEB_SERVICE_DEFINITION)
        get_seances_adapter = requests_mock.post(
            "http://example.com/web_service", text=fixtures.cgr_response_template([fixtures.FILM_138473])
        )
        cgr_cinema_details = providers_factories.CGRCinemaDetailsFactory(
            cinemaUrl="http://example.com/web_service",
            password=encrypt("theRealPassword"),
        )

        get_seances_pass_culture(cinema_details=cgr_cinema_details)

        assert "<mdp>theRealPassword</mdp>" in get_seances_adapter.last_request.text
