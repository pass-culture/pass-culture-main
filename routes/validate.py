""" validate """
from flask import current_app as app, jsonify, request

import models
from domain.user_emails import send_validation_confirmation_email
from models import ApiErrors, \
    PcObject, UserOfferer, Offerer
from repository.user_offerer_queries import find_user_offerer_email


@app.route("/validate", methods=["GET"])
def validate():
    token = request.args.get('token')

    if token is None:
        e = ApiErrors()
        e.addError('token', 'Vous devez fournir un jeton de validation')
        return jsonify(e.errors), 400

    model_names = request.args.get('modelNames')

    if model_names is None:
        e = ApiErrors()
        e.addError('modelNames', 'Vous devez fournir des noms de classes')
        return jsonify(e.errors), 400

    model_names = model_names.split(',')

    objects_to_validate = []
    for model_name in model_names:
        query = getattr(models, model_name) \
            .query \
            .filter_by(validationToken=token)
        objects_to_validate += query.all()

    if len(objects_to_validate) == 0:
        return "Aucun(e) objet ne correspond à ce code de validation" \
               + " ou l'objet est déjà validé", \
               404

    for obj in objects_to_validate:
        obj.validationToken = None

    PcObject.check_and_save(*objects_to_validate)

    user_offerers = [obj for obj in model_names if isinstance(obj, UserOfferer)]
    user_offerer = None
    if user_offerers :
        user_offerer = user_offerers[0]

    offerer = None
    offerers = [obj for obj in model_names if isinstance(obj, Offerer)]
    if offerers:
        offerer = offerers[0]

    send_validation_confirmation_email(user_offerer, offerer, app.mailjet_client.send.create)
    return "Validation effectuée", 202
