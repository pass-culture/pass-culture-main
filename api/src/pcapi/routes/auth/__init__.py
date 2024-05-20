from flask import Flask

from . import filters


def install_routes(app: Flask) -> None:
    # pylint: disable=unused-import
    from . import discord

    filters.install_template_filters(app)
