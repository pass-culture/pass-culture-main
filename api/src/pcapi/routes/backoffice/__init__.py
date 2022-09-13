from flask import Flask


def install_routes(app: Flask) -> None:
    # pylint: disable=unused-import
    from . import accounts
    from . import auth
    from . import offerers
    from . import permissions
    from . import pro
