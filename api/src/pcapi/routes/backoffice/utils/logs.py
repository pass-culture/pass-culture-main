import logging
from urllib.parse import urlparse

from flask import request

from .request import rule_for_url


logger = logging.getLogger(__name__)


def log_backoffice_tracking_data(
    event_name: str,
    extra_data: dict | None = None,
) -> None:
    if extra_data is None:
        extra_data = {}

    logger.info(
        event_name,
        extra={"analyticsSource": "backoffice", **extra_data},
        technical_message_id="backoffice_analytics_event",
    )


def log_backoffice_referrer_tracking_data() -> None:
    page_rule = request.url_rule
    assert page_rule is not None  # helps mypy
    page = page_rule.endpoint
    referrer = request.referrer
    origin = ""

    rule = rule_for_url(referrer, method="GET")
    rule = rule or rule_for_url(referrer, method="POST")  # sometime we get redirected from POST from
    if rule:
        origin = rule.endpoint

    if not origin:  # link from external tool
        origin = urlparse(referrer).netloc or "origine inconnue"

    log_backoffice_tracking_data(
        event_name="Analytics event",
        extra_data={
            "eventOrigin": origin,
            "eventName": page,
            "eventType": "loadPage",
        },
    )
