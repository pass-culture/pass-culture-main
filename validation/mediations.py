from models import ApiErrors

ALLOWED_EXTENSIONS = {'jpg', 'png', 'jpeg', 'gif'}
READABLE_EXTENSIONS = '(%s)' % ', '.join(map(lambda e: f'.{e}', reversed(sorted(ALLOWED_EXTENSIONS))))


def check_thumb_in_request(files, form):
    if 'thumb' in files:
        if files['thumb'].filename == '':
            raise ApiErrors({'thumb': ["Vous devez fournir une image d'accroche"]})

    elif 'thumbUrl' not in form:
        raise ApiErrors({'thumb': ["Vous devez fournir une image d'accroche"]})


def read_thumb(files=None, form=None):
    if 'thumb' in files:
        thumb = files['thumb']
        filename_parts = thumb.filename.rsplit('.', 1)
        if len(filename_parts) < 2 \
                or filename_parts[1].lower() not in ALLOWED_EXTENSIONS:
            raise ApiErrors(
                {'thumb': [f"Cet image manque d'une extension {READABLE_EXTENSIONS} ou son format n'est pas autorisé"]}
            )
        return thumb.read()

    if 'thumbUrl' in form:
        return form['thumbUrl']
