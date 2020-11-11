from io import BytesIO

from PIL import Image

from pcapi.models import ApiErrors


def check_thumb_in_request(files, form):
    missing_image_error = ApiErrors({"thumb": ["Vous devez fournir une image d'accroche"]})

    if "thumb" in files:
        if files["thumb"].filename == "":
            raise missing_image_error

    elif "thumbUrl" not in form:
        raise missing_image_error


def check_thumb_quality(thumb: bytes):
    errors = []

    image = Image.open(BytesIO(thumb))
    if image.width < 400 or image.height < 400:
        errors.append("L'image doit faire 400 * 400 px minimum")

    if errors:
        raise ApiErrors({"thumb": errors})
