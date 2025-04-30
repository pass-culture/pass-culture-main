from flask import Flask


def install_routes(app: Flask) -> None:
    from . import sendinblue
    from . import users_subscription
    from . import zendesk
