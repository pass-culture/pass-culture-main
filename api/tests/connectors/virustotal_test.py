import pytest
import requests_mock

from pcapi.connectors import virustotal
from pcapi.core.testing import override_features

from . import virustotal_test_data


class CheckUrlIsSafeTest:
    @override_features(ENABLE_VIRUSTOTAL=0)
    def test_with_feature_flag_disabled(self):
        with requests_mock.Mocker():
            # not request called
            virustotal.check_url_is_safe("https://example.com")

    @override_features(ENABLE_VIRUSTOTAL=1)
    @pytest.mark.settings(VIRUSTOTAL_BACKEND="pcapi.connectors.virustotal.VirusTotalBackend")
    def test_safe_url(self):
        url = "https://passculture.pro"
        url_id = "aHR0cHM6Ly9wYXNzY3VsdHVyZS5wcm8"
        with requests_mock.Mocker() as mock:
            mock.get(
                f"https://www.virustotal.com/api/v3/urls/{url_id}",
                json=virustotal_test_data.RESPONSE_SAFE_URL,
            )
            mock.post(f"https://www.virustotal.com/api/v3/urls/{url_id}/analyse")
            virustotal.check_url_is_safe(url)

    @override_features(ENABLE_VIRUSTOTAL=1)
    @pytest.mark.settings(VIRUSTOTAL_BACKEND="pcapi.connectors.virustotal.VirusTotalBackend")
    def test_malicious_url(self):
        url = "https://malicious.com"
        url_id = "aHR0cHM6Ly9tYWxpY2lvdXMuY29t"
        with requests_mock.Mocker() as mock:
            mock.get(
                f"https://www.virustotal.com/api/v3/urls/{url_id}",
                json=virustotal_test_data.RESPONSE_MALICIOUS_URL,
            )
            mock.post(f"https://www.virustotal.com/api/v3/urls/{url_id}/analyse")
            with pytest.raises(virustotal.MaliciousUrlException):
                virustotal.check_url_is_safe(url)

    @override_features(ENABLE_VIRUSTOTAL=1)
    @pytest.mark.settings(VIRUSTOTAL_BACKEND="pcapi.connectors.virustotal.VirusTotalBackend")
    def test_url_not_found(self):
        url = "https://www.not-found.com"
        url_id = "aHR0cHM6Ly93d3cubm90LWZvdW5kLmNvbQ"
        with requests_mock.Mocker() as mock:
            mock.get(
                f"https://www.virustotal.com/api/v3/urls/{url_id}",
                status_code=404,
                json=virustotal_test_data.RESPONSE_URL_NOT_FOUND,
            )
            with pytest.raises(virustotal.NotFoundException):
                virustotal.check_url_is_safe(url)


class CheckRequestUrlScanTest:
    @override_features(ENABLE_VIRUSTOTAL=0)
    def test_with_feature_flag_disabled(self):
        with requests_mock.Mocker():
            # not request called
            virustotal.request_url_scan("https://example.com")

    @override_features(ENABLE_VIRUSTOTAL=1)
    @pytest.mark.settings(VIRUSTOTAL_BACKEND="pcapi.connectors.virustotal.VirusTotalBackend")
    def test_rescan_url(self):
        url = "https://passculture.pro"
        url_id = "aHR0cHM6Ly9wYXNzY3VsdHVyZS5wcm8"
        with requests_mock.Mocker() as mock:
            mock.get(
                f"https://www.virustotal.com/api/v3/urls/{url_id}",
                json=virustotal_test_data.RESPONSE_SAFE_URL,
            )
            mock.post(
                f"https://www.virustotal.com/api/v3/urls/{url_id}/analyse",
                json=virustotal_test_data.RESPONSE_URL_ANALYSE,
            )
            virustotal.request_url_scan(url)

    @override_features(ENABLE_VIRUSTOTAL=1)
    @pytest.mark.settings(VIRUSTOTAL_BACKEND="pcapi.connectors.virustotal.VirusTotalBackend")
    def test_scan_new_url(self):
        url = "https://www.not-found.com"
        url_id = "aHR0cHM6Ly93d3cubm90LWZvdW5kLmNvbQ"
        with requests_mock.Mocker() as mock:
            mock.get(
                f"https://www.virustotal.com/api/v3/urls/{url_id}",
                status_code=404,
                json=virustotal_test_data.RESPONSE_URL_NOT_FOUND,
            )
            mock.post(
                "https://www.virustotal.com/api/v3/urls/",
                json=virustotal_test_data.RESPONSE_URL_ANALYSE,
            )
            with pytest.raises(virustotal.NotFoundException):
                virustotal.check_url_is_safe(url)
