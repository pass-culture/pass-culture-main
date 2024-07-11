from flask import current_app as app
from flask import jsonify

from pcapi.core.finance import factories as finance_factories
from pcapi.core.offerers import factories as offerers_factories
from pcapi.core.users import factories as users_factories
from pcapi.models.api_errors import ApiErrors
from pcapi.repository.clean_database import clean_all_database
from pcapi.routes.apis import private_api
from pcapi.sandboxes.scripts import getters
from pcapi.serialization.decorator import spectree_serialize


@private_api.route("/sanboxes/<module_name>/<getter_name>", methods=["GET"])
def get_sandbox(module_name, getter_name):  # type: ignore [no-untyped-def]
    # FIXME DELETE BEFORE MERGE
    clean_all_database()
    if not hasattr(getters, module_name):
        errors = ApiErrors()
        errors.add_error("module", 'Il n\'existe pas de tel "{}" module de getters pour la sandbox'.format(module_name))
        raise errors

    testcafes_module = getattr(getters, module_name)

    if not hasattr(testcafes_module, getter_name):
        errors = ApiErrors()
        errors.add_error(
            "getter", 'Il n\'existe pas de tel "{} {}" getter pour la sandbox'.format(module_name, getter_name)
        )
        raise errors

    getter = getattr(testcafes_module, getter_name)

    try:
        obj = getter()
        return jsonify(obj)
    except:
        errors = ApiErrors()
        errors.add_error(
            "query",
            'Une erreur s\'est produite lors du calcul de "{} {}" pour la sandbox'.format(module_name, getter_name),
        )
        raise errors
