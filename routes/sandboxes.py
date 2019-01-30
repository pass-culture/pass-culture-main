from flask import current_app as app, jsonify
from models.api_errors import ApiErrors
from sandboxes.scripts import getters

@app.route('/sandboxes/<module_name>/<getter_name>', methods=['GET'])
def get_sandbox(module_name, getter_name):
    try:
        print(module_name, getter_name)
        testcafes_module = getattr(getters, module_name)
        getter = getattr(testcafes_module, getter_name)
        obj = getter()
        return jsonify(obj)
    except:
        errors = ApiErrors()
        errors.addError(
            'getter',
            'Il n\'existe pas de tel \"{}/{}\" getter pour la sandbox'.format(
                module_name,
                getter_name
            )
        )
        raise errors
