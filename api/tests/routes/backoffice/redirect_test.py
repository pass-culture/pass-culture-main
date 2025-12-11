import logging
from unittest.mock import patch

import pytest
from flask import url_for

from pcapi.connectors import virustotal
from pcapi.core.testing import assert_num_queries

from .helpers import html_parser


pytestmark = [
    pytest.mark.usefixtures("db_session"),
    pytest.mark.backoffice,
]


class SafeRedirectTest:
    # - session
    expected_num_queries = 1

    def test_redirect_as_anonymous(self, client):
        response = client.get(url_for("backoffice_web.safe_redirect", url="https://example.com"))
        assert response.status_code == 302
        assert response.location == url_for("backoffice_web.home")

    @patch("pcapi.connectors.virustotal.request_url_scan")
    @patch("pcapi.connectors.virustotal.check_url_is_safe")
    def test_redirect_safe_url(self, mock_check_url_is_safe, mock_request_url_scan, authenticated_client):
        url = "https://safe.example.com"

        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for("backoffice_web.safe_redirect", url=url))
            assert response.status_code == 303

        assert response.location == url
        mock_check_url_is_safe.assert_called_once_with(url)
        mock_request_url_scan.assert_not_called()

    @patch("pcapi.connectors.virustotal.request_url_scan")
    @patch("pcapi.connectors.virustotal.check_url_is_safe", side_effect=virustotal.MaliciousUrlException)
    def test_redirect_malicious_url(self, mock_check_url_is_safe, mock_request_url_scan, authenticated_client):
        url = "https://malicious.example.com"

        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for("backoffice_web.safe_redirect", url=url))
            assert response.status_code == 200

        assert f"L'analyse de l'adresse {url} a détecté un risque de sécurité." in html_parser.content_as_text(
            response.data
        )
        mock_check_url_is_safe.assert_called_once_with(url)
        mock_request_url_scan.assert_not_called()

    @patch("pcapi.connectors.virustotal.request_url_scan")
    @patch("pcapi.connectors.virustotal.check_url_is_safe", side_effect=virustotal.NotFoundException)
    def test_redirect_unknown_url(self, mock_check_url_is_safe, mock_request_url_scan, authenticated_client):
        url = "https://unknown.example.com"

        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for("backoffice_web.safe_redirect", url=url))
            assert response.status_code == 200

        content = html_parser.content_as_text(response.data)
        assert f"L'adresse {url} n'a pas encore été analysée" in content
        assert "une analyse vient d'être demandée" in content
        mock_check_url_is_safe.assert_called_once_with(url)
        mock_request_url_scan.assert_called_once_with(url)

    @patch("pcapi.connectors.virustotal.request_url_scan")
    @patch("pcapi.connectors.virustotal.check_url_is_safe", side_effect=virustotal.PendingAnalysisException)
    def test_redirect_pending_url(self, mock_check_url_is_safe, mock_request_url_scan, authenticated_client):
        url = "https://pending.example.com"

        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for("backoffice_web.safe_redirect", url=url))
            assert response.status_code == 200

        content = html_parser.content_as_text(response.data)
        assert f"L'adresse {url} n'a pas encore été analysée" in content
        assert "une analyse a été demandée" in content
        mock_check_url_is_safe.assert_called_once_with(url)
        mock_request_url_scan.assert_not_called()

    @patch("pcapi.connectors.virustotal.request_url_scan")
    @patch("pcapi.connectors.virustotal.check_url_is_safe", side_effect=virustotal.VirusTotalApiException)
    def test_redirect_api_error(self, mock_check_url_is_safe, mock_request_url_scan, authenticated_client):
        url = "https://unknown.example.com"

        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for("backoffice_web.safe_redirect", url=url))
            assert response.status_code == 200

        assert "Une erreur s'est produite lors de la vérification du lien." in html_parser.content_as_text(
            response.data
        )
        mock_check_url_is_safe.assert_called_once_with(url)
        mock_request_url_scan.assert_not_called()

    @pytest.mark.parametrize(
        "exception,reason",
        [
            (virustotal.NotFoundException, "NOT_FOUND"),
            (virustotal.PendingAnalysisException, "PENDING"),
            (virustotal.MaliciousUrlException, "MALICIOUS"),
            (virustotal.VirusTotalApiException, "ERROR"),
        ],
    )
    def test_force_redirect(self, authenticated_client, caplog, exception, reason):
        url = "https://www.example.com"

        with patch("pcapi.connectors.virustotal.check_url_is_safe", side_effect=exception):
            with caplog.at_level(logging.INFO):
                response = authenticated_client.get(url_for("backoffice_web.safe_redirect", url=url, ignore=reason))
            assert response.status_code == 303

        assert response.location == url
        assert caplog.records[-2].message == "Forced redirection"
        assert caplog.records[-2].extra == {"url": url, "ignore": reason}
