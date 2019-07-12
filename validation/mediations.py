from models import ApiErrors


def check_thumb_in_request(files, form):
    if 'thumb' in files:
        if files['thumb'].filename == '':
            raise ApiErrors({'thumb': ["Vous devez fournir une image d'accroche"]})

    elif 'thumbUrl' not in form:
        raise ApiErrors({'thumb': ["Vous devez fournir une image d'accroche"]})


