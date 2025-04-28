from flask import Flask


def install_routes(app: Flask) -> None:

    from . import account
