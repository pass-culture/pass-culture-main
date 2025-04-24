import time

from flask import jsonify

import pcapi.core.mails.testing as mails_testing
from pcapi.models.api_errors import ApiErrors
from pcapi.repository.clean_database import clean_all_database
from pcapi.routes.apis import private_api
from pcapi.sandboxes.scripts import getters


@private_api.route("/sandboxes/<module_name>/<getter_name>", methods=["GET"])
def get_sandbox(module_name, getter_name):  # type: ignore [no-untyped-def]
    if not hasattr(getters, module_name):
        errors = ApiErrors()
        errors.add_error("module", 'Il n\'existe pas de tel "{}" module de getters pour la sandbox'.format(module_name))
        raise errors

    cypress_module = getattr(getters, module_name)

    if not hasattr(cypress_module, getter_name):
        errors = ApiErrors()
        errors.add_error(
            "getter", 'Il n\'existe pas de tel "{} {}" getter pour la sandbox'.format(module_name, getter_name)
        )
        raise errors

    getter = getattr(cypress_module, getter_name)

    try:
        print("run CI")
        clean_all_database(reset_ids=True)
        obj = getter()
        return jsonify(obj)
    except Exception as e:
        errors = ApiErrors()
        errors.add_error(
            "query",
            'Une erreur s\'est produite lors du calcul de "{} {}" pour la sandbox : {}'.format(
                module_name, getter_name, e
            ),
        )
        raise errors


# The next endpoints must only be used with EMAIL_BACKEND set to `pcapi.core.mails.backends.testing.TestingBackend`
# otherwise the outbox will be empty
# The next endpoints is only available if ENABLE_TEST_ROUTES is set to 1
@private_api.route("/sandboxes/clear_email_list", methods=["GET"])
def clear_email_list():  # type: ignore [no-untyped-def]
    if len(mails_testing.outbox) != 0:
        mails_testing.outbox.clear()
    return "Outbox cleared"


@private_api.route("/sandboxes/get_unique_email", methods=["GET"])
def get_unique_email():  # type: ignore [no-untyped-def]
    delay = 0
    while len(mails_testing.outbox) == 0 and delay <= 60:
        time.sleep(5)
        delay += 5
    return mails_testing.outbox[0]
