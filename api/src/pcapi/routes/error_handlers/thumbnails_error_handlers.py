import logging

from flask import Response
from flask import current_app as app

from pcapi.core.offers import exceptions as offers_exceptions


logger = logging.getLogger(__name__)


@app.errorhandler(offers_exceptions.ImageValidationError)
def handle_create_a_thumbnail(exception: Exception) -> tuple[Response, int]:
    error_message = exception.args[0] if exception.args else "L'image n'est pas valide"
    logger.error(
        "When creating the offer thumbnail, this error was encountered: %s: %s",
        exception.__class__.__name__,
        error_message,
    )
    return app.generate_error_response({"errors": [error_message]}), 400  # type: ignore [attr-defined]
