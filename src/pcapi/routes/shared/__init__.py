# This package contains routes that are used by both webapp and pro.
# The native app SHOULD NOT use these routes.

from flask import Flask


def install_routes(app: Flask) -> None:
    # pylint: disable=unused-import
    from . import features
    from . import passwords
    from . import users
