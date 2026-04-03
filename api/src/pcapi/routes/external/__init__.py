from flask import Flask


def install_routes(app: Flask) -> None:
    from . import brevo
    from . import users_subscription
    from . import zendesk
