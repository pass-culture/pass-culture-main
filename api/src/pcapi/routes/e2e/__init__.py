from flask import Flask


def install_routes(app: Flask) -> None:
    # pylint: disable=unused-import
    from .routes import sandbox_data
