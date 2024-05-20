from . import filters


def install_routes(app: Flask) -> None:
    filters.install_template_filters(app)
