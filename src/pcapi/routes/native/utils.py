from decimal import Decimal
from typing import Optional

import flask
import semver

from pcapi import settings
from pcapi.models.api_errors import ForbiddenError


def convert_to_cent(amount: Optional[Decimal]) -> Optional[int]:
    if amount is None:
        return None
    return int(amount * 100)


def check_client_version() -> None:
    client_version_header = flask.request.headers.get("app-version", None)
    if not client_version_header:
        return
    try:
        client_version = semver.VersionInfo.parse(client_version_header)
    except ValueError:
        raise ForbiddenError(errors={"code": "UPGRADE_REQUIRED"})

    if client_version < settings.NATIVE_APP_MINIMAL_CLIENT_VERSION:
        raise ForbiddenError(errors={"code": "UPGRADE_REQUIRED"})
