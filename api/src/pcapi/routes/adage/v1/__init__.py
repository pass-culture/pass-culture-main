from flask import Flask


def install_routes(app: Flask) -> None:
    from . import educational_deposit, educational_institution, prebooking, venue
