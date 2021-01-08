from flask import Flask


def install_routes(app: Flask) -> None:
    # pylint: disable=unused-import
    from . import account
    from . import authentication
    from . import offers
    from . import redirection
