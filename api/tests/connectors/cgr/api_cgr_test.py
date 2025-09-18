from pcapi.connectors.cgr.cgr import get_cgr_service_proxy

from tests.connectors.cgr import soap_definitions


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
