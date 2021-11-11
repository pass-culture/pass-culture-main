from flask import Flask

from pcapi import settings


def install_routes(app: Flask) -> None:
    # pylint: disable=unused-import
    from . import health_check

    if settings.IS_DEV:
        from . import sandboxes
        from . import storage
