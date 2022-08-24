from flask import Flask


def install_routes(app: Flask) -> None:
    # pylint: disable=unused-import
    from . import categories
    from . import domains
    from . import educational_institutions
    from . import offers
    from . import students_levels
    from . import venues
