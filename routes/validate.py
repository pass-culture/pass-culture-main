from flask import current_app as app, jsonify, request

from models.api_errors import ApiErrors


Offerer = app.model.Offerer
User = app.model.User
UserOfferer = app.model.UserOfferer


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
        query = app.model[model_name]\
                .query\
                .filter_by(validationToken=token)
        objects_to_validate += query.all()

    if len(objects_to_validate) == 0:
        return "Aucun(e) objet ne correspond à ce code de validation"\
               + " ou l'objet est déjà validé",\
               404

    for obj in objects_to_validate:
        obj.validationToken = None

    app.model.PcObject.check_and_save(*objects_to_validate)
    return "Validation effectuée", 202
