import logging

from flask import current_app as app

from pcapi.core.offers.exceptions import FileSizeExceeded
from pcapi.core.offers.exceptions import ImageTooSmall
from pcapi.core.offers.exceptions import MissingImage
from pcapi.core.offers.exceptions import UnacceptedFileType
from pcapi.routes.error_handlers.utils import generate_error_response


logger = logging.getLogger(__name__)


@app.errorhandler(FileSizeExceeded)  # type: ignore [arg-type]
@app.errorhandler(ImageTooSmall)
@app.errorhandler(UnacceptedFileType)
@app.errorhandler(MissingImage)
def handle_create_a_thumbnail(exception):  # type: ignore [no-untyped-def]
    logger.info("When creating the offer thumbnail, this error was encountered: %s", exception.__class__.__name__)
    return generate_error_response({"errors": [exception.args[0]]}), 400
