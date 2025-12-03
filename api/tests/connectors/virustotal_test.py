import pytest
import requests_mock

from pcapi.connectors import virustotal

from . import virustotal_test_data


class CheckUrlIsSafeTest:
    @pytest.mark.batch_validate_individual_bookings(ENABLE_VIRUSTOTAL=0)
    def test_with_feature_flag_disabled(self):
        with requests_mock.Mocker():
            # not request called
            virustotal.check_url_is_safe("https://example.com")

    @pytest.mark.settings(VIRUSTOTAL_BACKEND="pcapi.connectors.virustotal.VirusTotalBackend")
    @pytest.mark.features(ENABLE_VIRUSTOTAL=1)
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

    @pytest.mark.settings(VIRUSTOTAL_BACKEND="pcapi.connectors.virustotal.VirusTotalBackend")
    @pytest.mark.features(ENABLE_VIRUSTOTAL=1)
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

    @pytest.mark.settings(VIRUSTOTAL_BACKEND="pcapi.connectors.virustotal.VirusTotalBackend")
    @pytest.mark.features(ENABLE_VIRUSTOTAL=1)
    def test_pending_url(self):
        url = "https://www.example.com"
        url_id = "aHR0cHM6Ly93d3cuZXhhbXBsZS5jb20"
        with requests_mock.Mocker() as mock:
            mock.get(
                f"https://www.virustotal.com/api/v3/urls/{url_id}",
                json=virustotal_test_data.RESPONSE_URL_PENDING,
            )
            mock.post(f"https://www.virustotal.com/api/v3/urls/{url_id}/analyse")
            with pytest.raises(virustotal.PendingAnalysisException):
                virustotal.check_url_is_safe(url)

    @pytest.mark.settings(VIRUSTOTAL_BACKEND="pcapi.connectors.virustotal.VirusTotalBackend")
    @pytest.mark.features(ENABLE_VIRUSTOTAL=1)
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
    @pytest.mark.features(ENABLE_VIRUSTOTAL=0)
    def test_with_feature_flag_disabled(self):
        with requests_mock.Mocker():
            # not request called
            virustotal.request_url_scan("https://example.com")

    @pytest.mark.settings(VIRUSTOTAL_BACKEND="pcapi.connectors.virustotal.VirusTotalBackend")
    @pytest.mark.features(ENABLE_VIRUSTOTAL=1)
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

    @pytest.mark.settings(VIRUSTOTAL_BACKEND="pcapi.connectors.virustotal.VirusTotalBackend")
    @pytest.mark.features(ENABLE_VIRUSTOTAL=1)
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
