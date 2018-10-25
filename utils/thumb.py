""" thumb """
from models.api_errors import ApiErrors

ALLOWED_EXTENSIONS = set(['jpg', 'png', 'jpeg', 'gif'])

def get_crop(form):
    if 'croppingRect[x]' in form \
        and 'croppingRect[y]' in form \
        and 'croppingRect[height]' in form:
        return [float(form['croppingRect[x]']),
                float(form['croppingRect[y]']),
                float(form['croppingRect[height]'])]

def has_thumb(files, form):
    if 'thumb' in files:
        if files['thumb'].filename == '':
            return False
    elif 'thumbUrl' not in form:
        return False
    return True

def read_thumb(files=None, form=None):
    if 'thumb' in files:
        thumb = files['thumb']
        #print('thumb', thumb)
        filename_parts = thumb.filename.rsplit('.', 1)
        if len(filename_parts) < 2 \
           or filename_parts[1].lower() not in ALLOWED_EXTENSIONS:
            api_errors = ApiErrors()
            api_errors.addError('thumb', "Cet image manque d'une extension (.png, .jpg...) ou son format n'est pas autorisé")
            raise api_errors
        return thumb.read()

    if 'thumbUrl' in form:
        return form['thumbUrl']
