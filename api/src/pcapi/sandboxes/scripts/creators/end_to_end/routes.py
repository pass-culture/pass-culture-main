import threading
from time import time

from flask import current_app as app

from pcapi.core.offerers.factories import UserOffererFactory
from pcapi.core.users import factories as users_factories
from pcapi.repository.clean_database import clean_all_database
from pcapi.sandboxes.scripts.creators.end_to_end.setup import create_E2E_offerer
from pcapi.sandboxes.scripts.sandbox_industrial import save_ci_sandbox
from pcapi.serialization.decorator import spectree_serialize


@app.route("/e2e/pro/tear-up", methods=["GET"])
@spectree_serialize(on_success_status=204)
def tear_up() -> None:
    start = time()
    clean_all_database()
    threading.Thread(target=save_ci_sandbox, args=(start,)).start()


@app.route("/e2e/pro/tear-down", methods=["GET"])
@spectree_serialize(on_success_status=204)
def tear_down() -> None:
    clean_all_database()


@app.route("/e2e/pro/create-event-individual-offer", methods=["GET"])
@spectree_serialize(on_success_status=204)
def setup_create_event_individual_offer() -> None:
    clean_all_database()
    offerer = create_E2E_offerer()
    pro_adage_eligible = users_factories.ProFactory(
        lastName="PC Test Pro",
        firstName="97 0",
        departementCode="97",
        postalCode="97100",
        email="pro_adage_eligible@example.com",
    )
    UserOffererFactory(offerer=offerer, user=pro_adage_eligible)
