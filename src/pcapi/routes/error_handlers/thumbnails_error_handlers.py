from flask import current_app as app
from flask import jsonify

from pcapi.core.offers.exceptions import FailureToRetrieve
from pcapi.core.offers.exceptions import FileSizeExceeded
from pcapi.core.offers.exceptions import ImageTooSmall
from pcapi.core.offers.exceptions import MissingImage
from pcapi.core.offers.exceptions import UnacceptedFileType


@app.errorhandler(FileSizeExceeded)
@app.errorhandler(ImageTooSmall)
@app.errorhandler(UnacceptedFileType)
@app.errorhandler(FailureToRetrieve)
@app.errorhandler(MissingImage)
def handle_create_a_thumbnail(exception):
    app.logger.info("When creating the offer thumbnail, this error was encountered: %s", exception.__class__.__name__)
    return jsonify({"errors": [exception.args[0]]}), 400
