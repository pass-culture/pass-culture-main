from io import BytesIO
from typing import Any

from PIL import Image

from pcapi.models import ApiErrors
from pcapi.routes.serialization.mediations_serialize import CreateMediationBodyModel


def check_thumb_in_request(files: Any, form: CreateMediationBodyModel) -> None:
    missing_image_error = ApiErrors({"thumb": ["Vous devez fournir une image d'accroche"]})

    if "thumb" in files:
        if files["thumb"].filename == "":
            raise missing_image_error

    elif form.thumb_url is None:
        raise missing_image_error


def check_thumb_quality(thumb: bytes):
    errors = []

    image = Image.open(BytesIO(thumb))
    if image.width < 400 or image.height < 400:
        errors.append("L'image doit faire 400 * 400 px minimum")

    if errors:
        raise ApiErrors({"thumb": errors})
