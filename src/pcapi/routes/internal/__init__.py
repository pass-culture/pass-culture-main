from flask import Flask

from pcapi.utils.config import IS_DEV


def install_routes(app: Flask) -> None:
    # pylint: disable=unused-import
    from . import health_check

    if IS_DEV:
        from . import sandboxes
        from . import storage
