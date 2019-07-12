from io import BytesIO

from PIL import Image

from models import ApiErrors

MINIMUM_FILE_SIZE = 100 * 1000


def check_thumb_in_request(files, form):
    if 'thumb' in files:
        if files['thumb'].filename == '':
            raise ApiErrors({'thumb': ["Vous devez fournir une image d'accroche"]})

    elif 'thumbUrl' not in form:
        raise ApiErrors({'thumb': ["Vous devez fournir une image d'accroche"]})


def check_thumb_quality(thumb: bytes):
    errors = ApiErrors()

    if len(thumb) < MINIMUM_FILE_SIZE:
        errors.add_error('thumb', "L'image doit faire 100 ko minimum")

    image = Image.open(BytesIO(thumb))
    if image.width < 400 or image.height < 400:
        errors.add_error('thumb', "L'image doit faire 400 * 400 px minimum")

    errors.maybe_raise()
