from flask import Flask


def install_routes(app: Flask) -> None:
    # pylint: disable=unused-import
    from . import educational_institution
    from . import prebooking
    from . import venue
