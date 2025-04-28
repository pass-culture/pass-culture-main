from flask import Flask

from pcapi import settings


def install_routes(app: Flask) -> None:

    from . import playlist
