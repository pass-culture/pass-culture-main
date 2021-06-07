from flask import Flask


def install_handlers(app: Flask) -> None:
    # pylint: disable=unused-import
    from .account import verify_identity_document
