"""
A client for VirusTotal URL scanner.
API Documentation: https://docs.virustotal.com/reference/

We do not use vt-py, the officiel client library for VirusTotal, because it raises exceptions when using aiohttp.
Our very basic usage does not really require a module.
"""

import base64
import logging
import time

from pcapi import settings
from pcapi.models.feature import FeatureToggle
from pcapi.utils import module_loading
from pcapi.utils import requests


logger = logging.getLogger(__name__)

RESCAN_DELAY_DEFAULT = 14 * 86400
RESCAN_DELAY_SUSPICIOUS = 3 * 86400


class VirusTotalException(Exception):
    pass  # base class, never raised directly


class VirusTotalApiException(VirusTotalException):
    pass


class NotFoundException(VirusTotalException):
    pass


class MaliciousUrlException(VirusTotalException):
    pass


def url_id(url: str) -> str:
    """Generates the object ID for an URL."""
    return base64.urlsafe_b64encode(url.encode()).decode().strip("=")


def _get_backend() -> "BaseBackend":
    backend_class = module_loading.import_string(settings.VIRUSTOTAL_BACKEND)
    return backend_class()


def check_url_is_safe(url: str) -> None:
    if FeatureToggle.ENABLE_VIRUSTOTAL.is_active():
        _get_backend().check_url_is_safe(url)


def request_url_scan(url: str, skip_if_recent_scan: bool = False) -> None:
    if FeatureToggle.ENABLE_VIRUSTOTAL.is_active():
        _get_backend().request_url_scan(url, skip_if_recent_scan)


class BaseBackend:
    def check_url_is_safe(self, url: str) -> None:
        raise NotImplementedError()

    def request_url_scan(self, url: str, skip_if_recent_scan: bool) -> None:
        raise NotImplementedError()


class LoggerBackend(BaseBackend):
    def check_url_is_safe(self, url: str) -> None:
        logger.info("A request would be sent to VirusTotal to check URL: %s", url)

    def request_url_scan(self, url: str, skip_if_recent_scan: bool) -> None:
        logger.info("A request would be sent to VirusTotal to scan URL: %s", url)


class VirusTotalBackend(BaseBackend):
    base_url = "https://www.virustotal.com/api/v3"
    timeout = 10

    def _make_request(self, method: str, subpath: str, form: dict | None = None) -> dict:
        url = self.base_url + subpath
        try:
            response = getattr(requests, method)(
                url, headers={"x-apikey": settings.VIRUSTOTAL_API_KEY}, data=form, timeout=self.timeout
            )
        except requests.exceptions.RequestException as exc:
            logger.exception(
                "Network error on VirusTotal API",
                extra={"exc": exc, "url": url},
                technical_message_id="virustotal.error",
            )
            raise VirusTotalApiException("Network error on VirusTotal API") from exc
        if response.status_code == 404:
            raise NotFoundException(url)
        if not response.ok:
            logger.error(
                "Error from VirusTotal API",
                extra={"url": url, "status_code": response.status_code},
                technical_message_id="virustotal.error",
            )
            raise VirusTotalApiException(f"Unexpected {response.status_code} response from VirusTotal API: {url}")
        try:
            data = response.json()
        except requests.exceptions.JSONDecodeError:
            raise VirusTotalApiException("Unexpected non-JSON response from VirusTotal API")
        return data

    def _get(self, subpath: str) -> dict:
        return self._make_request("get", subpath)

    def _post(self, subpath: str, form: dict | None = None) -> dict:
        return self._make_request("post", subpath, form=form)

    def check_url_is_safe(self, url: str) -> None:
        """
        Checks if the URL is safe or contains malicious code.
        It does not request for a new scan, but only get results when the URL has already been scanned.

        Any result is logged so that we can:
        - make stats about service usage and detection
        - track who may have been infected in case of late detection
        """
        data = self._get(f"/urls/{url_id(url)}")
        attributes = data["data"]["attributes"]

        log_extra_data = {
            "url": url,
            "last_analysis_stats": attributes["last_analysis_stats"],
            "last_analysis_date": attributes["last_analysis_date"],
        }

        try:
            if attributes["last_analysis_stats"]["malicious"] > 0:
                logger.warning(
                    "Malicious URL detected", extra=log_extra_data, technical_message_id="virustotal.malicious"
                )
                raise MaliciousUrlException()

            logger.info("URL is safe", extra=log_extra_data, technical_message_id="virustotal.ok")
        finally:
            # rescan URL for next time
            if self._needs_rescan(attributes):
                self._request_url_rescan(url)

    @classmethod
    def _needs_rescan(cls, attributes: dict) -> bool:
        last_analysis_stats = attributes["last_analysis_stats"]
        last_submission_date = attributes["last_submission_date"]
        now = int(time.time())

        if last_submission_date < now - RESCAN_DELAY_DEFAULT:
            return True

        if last_submission_date < now - RESCAN_DELAY_SUSPICIOUS and (
            last_analysis_stats["suspicious"] > 0 or last_analysis_stats["malicious"] == 0
        ):
            return True

        return False

    def _request_url_rescan(self, url: str) -> None:
        logger.info("Request URL scan", extra={"url": url}, technical_message_id="virustotal.rescan")
        try:
            self._post(f"/urls/{url_id(url)}/analyse")
        except VirusTotalApiException:
            pass  # error logged, do not make caller fail

    def _request_url_new_scan(self, url: str) -> None:
        logger.info("Request URL scan", extra={"url": url}, technical_message_id="virustotal.scan")
        try:
            self._post("/urls/", form={"url": url})
        except VirusTotalApiException:
            pass  # error logged, do not make caller fail

    def request_url_scan(self, url: str, skip_if_recent_scan: bool) -> None:
        try:
            data = self._get(f"/urls/{url_id(url)}")
        except NotFoundException:
            try:
                self._request_url_new_scan(url)
            except (NotFoundException, VirusTotalApiException):
                pass  # error logged, do not make caller fail
        except VirusTotalApiException:
            pass  # error logged, do not make caller fail
        else:
            if not skip_if_recent_scan or self._needs_rescan(data["data"]["attributes"]):
                self._request_url_rescan(url)
