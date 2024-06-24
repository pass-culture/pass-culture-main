from flask import Flask

from pcapi import settings


def install_routes(app: Flask) -> None:
    # pylint: disable=unused-import
    from . import health_check

    if settings.ENABLE_UBBLE_E2E_TESTING or settings.IS_E2E_TESTS:
        from . import e2e_ubble
    if settings.ENABLE_LOCAL_DEV_MODE_FOR_STORAGE:
        from . import storage
    if settings.ENABLE_TEST_ROUTES:
        from . import e2e
        from . import testing
