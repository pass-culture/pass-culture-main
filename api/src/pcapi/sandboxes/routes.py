import threading

from flask import current_app as app

from pcapi.repository.clean_database import clean_all_database
from pcapi.sandboxes.scripts.sandbox_industrial import save_ci_sandbox
from pcapi.serialization.decorator import spectree_serialize


@app.route("/e2e/pro/tear-up", methods=["GET"])
@spectree_serialize(on_success_status=204)
def tear_up() -> None:
    clean_all_database()
    threading.Thread(target=save_ci_sandbox).start()


@app.route("/e2e/pro/tear-down", methods=["GET"])
@spectree_serialize(on_success_status=204)
def tear_down() -> None:
    clean_all_database()
