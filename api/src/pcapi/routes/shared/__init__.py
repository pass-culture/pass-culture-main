# This package contains routes that are used by pro.
# The native app SHOULD NOT use these routes.

from flask import Flask


def install_routes(app: Flask) -> None:
    from . import educational_domains
    from . import passwords
