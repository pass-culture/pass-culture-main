from flask import current_app as app, jsonify

from models.api_errors import ApiErrors
from sandboxes.scripts import getters


@app.route('/sandboxes/<module_name>/<getter_name>', methods=['GET'])
def get_sandbox(module_name, getter_name):

    if not hasattr(getters, module_name):
        errors = ApiErrors()
        errors.add_error(
            'module',
            'Il n\'existe pas de tel \"{}\" module de getters pour la sandbox'.format(
                module_name
            )
        )
        raise errors

    testcafes_module = getattr(getters, module_name)

    if not hasattr(testcafes_module, getter_name):
        errors = ApiErrors()
        errors.add_error(
            'getter',
            'Il n\'existe pas de tel \"{} {}\" getter pour la sandbox'.format(
                module_name,
                getter_name
            )
        )
        raise errors

    getter = getattr(testcafes_module, getter_name)

    try:
        obj = getter()
        return jsonify(obj)
    except:
        errors = ApiErrors()
        errors.add_error(
            'query',
            'Une erreur s\'est produite lors du calcul de \"{} {}\" pour la sandbox'.format(
                module_name,
                getter_name
            )
        )
        raise errors
