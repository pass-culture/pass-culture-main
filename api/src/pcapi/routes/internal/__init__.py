from flask import Flask

from pcapi import settings


def install_routes(app: Flask) -> None:
    # pylint: disable=unused-import
    from . import health_check

    if settings.IS_RUNNING_TESTS or settings.IS_E2E_TESTS:
        from . import e2e_ubble
    if settings.IS_DEV:
        from . import storage
    if settings.ENABLE_TEST_ROUTES and settings.ENABLE_FEATURE_FLAG_PATCHING:
        from . import testing
