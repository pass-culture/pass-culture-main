import re
import traceback
import simplejson as json
from flask import current_app as app, jsonify
from sqlalchemy.exc import IntegrityError

from models.api_errors import ApiErrors


@app.errorhandler(ApiErrors)
def restize_api_errors(e):
    print(json.dumps(e.errors))
    return jsonify(e.errors), e.status_code or 400


def something_went_wrong(e):
    print("UNHANDLED ERROR : ")
    traceback.print_exc()
    return "Une erreur technique s'est produite. Elle a été notée, et nous allons investiguer au plus vite.", 500


@app.errorhandler(ValueError)
def restize_value_error(e):
    if len(e.args)>1 and e.args[1] == 'enum':
        return json.dumps([{e.args[2]: ' doit etre dans cette liste : '+",".join(map(lambda x : '"'+x+'"', e.args[3]))}]), 400
    else:
        return something_went_wrong(e)


@app.errorhandler(TypeError)
def restize_type_error(e):
    if e.args and len(e.args)>1 and e.args[1] == 'geography':
        return json.dumps([{e.args[2]: 'doit etre une liste de nombre décimaux comme par exemple : [2.22, 3.22]'}]), 400
    elif e.args and len(e.args)>1 and e.args[1] and e.args[1]=='decimal':
        return json.dumps([{e.args[2]: 'doit être un nombre décimal'}]), 400
    elif e.args and len(e.args)>1 and e.args[1] and e.args[1]=='integer':
        return json.dumps([{e.args[2]: 'doit être un entier'}]), 400
    else:
        return something_went_wrong(e)


@app.errorhandler(IntegrityError)
def restize_integrity_error(e):
    if hasattr(e, 'orig') and hasattr(e.orig, 'pgcode') and e.orig.pgcode=='23505':
        field = re.search('Key \((.*?)\)=', str(e._message), re.IGNORECASE).group(1)
        return json.dumps([{field: 'une entrée avec cet identifiant existe déjà dans notre base de données'}]), 400
    elif hasattr(e, 'orig') and hasattr(e.orig, 'pgcode') and e.orig.pgcode=='23503':
        field = re.search('Key \((.*?)\)=', str(e._message), re.IGNORECASE).group(1)
        return json.dumps([{field: 'aucun objet ne correspond à cet identifiant dans notre base de données'}]), 400
    elif hasattr(e, 'orig') and hasattr(e.orig, 'pgcode') and e.orig.pgcode=='23502':
        field = re.search('column "(.*?)"', e.orig.pgerror, re.IGNORECASE).group(1)
        return json.dumps([{field: 'ce champ est obligatoire'}]), 400
    else:
        return something_went_wrong(e)
