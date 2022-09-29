from flask import Flask


def install_routes(app: Flask) -> None:
    # pylint: disable=unused-import
    from . import accounts
    from . import auth
    from . import filters
    from . import home
    from . import i18n
    from . import offerers
    from . import pro

    filters.install_template_filters(app)
    i18n.install_template_filters(app)
