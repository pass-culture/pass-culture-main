""" thumb """
from flask import jsonify, request

from models.api_errors import ApiErrors

ALLOWED_EXTENSIONS = set(['jpg', 'png', 'jpeg', 'gif'])

def get_crop():
    if 'croppingRect[x]' in request.form \
        and 'croppingRect[y]' in request.form \
        and 'croppingRect[height]' in request.form:
        return [float(request.form['croppingRect[x]']),
                float(request.form['croppingRect[y]']),
                float(request.form['croppingRect[height]'])]

def has_thumb():
    if 'thumb' in request.files:
        if request.files['thumb'].filename == '':
            return False
    elif 'thumbUrl' not in request.form:
        return False
    return True

def read_thumb():
    if 'thumb' in request.files:
        thumb = request.files['thumb']
        filename_parts = thumb.filename.rsplit('.', 1)
        if len(filename_parts) < 2 \
           or filename_parts[1].lower() not in ALLOWED_EXTENSIONS:
            api_errors = ApiErrors()
            api_errors.addError('thumb', "Cet image manque d'une extension (.png, .jpg...) ou son format n'est pas autorisé")
            raise api_errors
        return thumb.read()

    if 'thumbUrl' in request.form:
        return request.form['thumbUrl']
