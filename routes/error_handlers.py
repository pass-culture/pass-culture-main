from flask import current_app as app
import re
import simplejson as json
import traceback
from sqlalchemy.exc import IntegrityError


@app.errorhandler(app.model.ApiErrors)
def restize_api_errors(e):
    print(json.dumps(e.errors))
    return json.dumps(e.errors), 400


def something_went_wrong(e):
    print("UNHANDLED ERROR : ")
    traceback.print_exc()
    return "We're sorry, but something went wrong. The error has been logged and we'll investigate quickly.", 500


@app.errorhandler(ValueError)
def restize_value_error(e):
    if len(e.args)>1 and e.args[1]=='enum':
        return json.dumps([{e.args[2] : 'should be one of '+",".join(map(lambda x : '"'+x+'"', e.args[3]))}]), 400
    else:
        return something_went_wrong(e)


@app.errorhandler(TypeError)
def restize_type_error(e):
    if e.args and len(e.args)>1 and e.args[1]=='geography':
        return json.dumps([{e.args[2]: 'should be a list of floating point numbers like this : [2.22, 3.22]'}]), 400
    elif e.args and len(e.args)>1 and e.args[1] and e.args[1]=='decimal':
        return json.dumps([{e.args[2]: 'should be a decimal number'}]), 400
    elif e.args and len(e.args)>1 and e.args[1] and e.args[1]=='integer':
        return json.dumps([{e.args[2]: 'should be an integer'}]), 400
    else:
        return something_went_wrong(e)


@app.errorhandler(IntegrityError)
def restize_integrity_error(e):
    if hasattr(e, 'orig') and hasattr(e.orig, 'pgcode') and e.orig.pgcode=='23505':
        field = re.search('Key \((.*?)\)=', str(e._message), re.IGNORECASE).group(1)
        return json.dumps([{field: 'already exists in our database'}]), 400
    elif hasattr(e, 'orig') and hasattr(e.orig, 'pgcode') and e.orig.pgcode=='23503':
        field = re.search('Key \((.*?)\)=', str(e._message), re.IGNORECASE).group(1)
        return json.dumps([{field: 'there is no object with this id in our database'}]), 400
    elif hasattr(e, 'orig') and hasattr(e.orig, 'pgcode') and e.orig.pgcode=='23502':
        field = re.search('column "(.*?)"', e.orig.pgerror, re.IGNORECASE).group(1)
        return json.dumps([{field: 'Champ obligatoire'}]), 400
    else:
        return something_went_wrong(e)
