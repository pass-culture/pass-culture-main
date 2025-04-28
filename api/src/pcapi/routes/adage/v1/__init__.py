from flask import Flask


def install_routes(app: Flask) -> None:

    from . import educational_deposit
    from . import educational_institution
    from . import prebooking
    from . import venue
