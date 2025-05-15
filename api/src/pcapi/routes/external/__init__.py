from flask import Flask


def install_routes(app: Flask) -> None:
    from . import sendinblue, users_subscription, zendesk
