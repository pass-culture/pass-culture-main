from flask import current_app as app

from pcapi.core.finance import factories as finance_factories
from pcapi.core.offerers import factories as offerers_factories
from pcapi.core.offerers.models import VenueTypeCode
from pcapi.core.users import factories as users_factories
from pcapi.repository.clean_database import clean_all_database
from pcapi.sandboxes.scripts.mocks.educational_siren_mocks import MOCK_ADAGE_ELIGIBLE_SIREN
from pcapi.serialization.decorator import spectree_serialize


@app.route("/e2e/pro/create-event-individual-offer", methods=["GET"])
@spectree_serialize(on_success_status=204)
def setup_data_for_create_event_individual_offer_e2e_test() -> None:
    clean_all_database()
    pro_user = users_factories.ProFactory(
        email="pro_adage_eligible@example.com",
    )
    siren = str(MOCK_ADAGE_ELIGIBLE_SIREN)
    venue = offerers_factories.VenueFactory(
        managingOfferer__siren=siren,
        comment="Salle de cinéma",
        siret=f"{siren}11111",
    )
    # create bank account to avoid first offer pop up
    finance_factories.BankAccountFactory(offerer=venue.managingOfferer)
    offerers_factories.UserOffererFactory(user=pro_user, offerer=venue.managingOfferer)


@app.route("/e2e/pro/create-thing-individual-offer", methods=["GET"])
@spectree_serialize(on_success_status=204)
def setup_data_for_create_thing_individual_offer_e2e_test() -> None:
    clean_all_database()
    pro_user = users_factories.ProFactory(
        email="pro_adage_eligible@example.com",
    )
    siren = str(MOCK_ADAGE_ELIGIBLE_SIREN)
    venue = offerers_factories.VenueFactory(
        managingOfferer__siren=siren,
        comment="Salle de cinéma",
        siret=f"{MOCK_ADAGE_ELIGIBLE_SIREN}11111",
    )
    # create bank account to avoid first offer pop up
    finance_factories.BankAccountFactory(offerer=venue.managingOfferer)
    offerers_factories.UserOffererFactory(user=pro_user, offerer=venue.managingOfferer)


@app.route("/e2e/pro/create-venue", methods=["GET"])
@spectree_serialize(on_success_status=204)
def setup_data_for_create_venue_e2e_test() -> None:
    clean_all_database()
    pro_user = users_factories.ProFactory(
        email="retention_structures@example.com",
    )
    offerer = offerers_factories.OffererFactory(name="Bar des amis", siren="222222233")
    offerers_factories.VenueFactory(
        managingOfferer=offerer,
    )
    offerers_factories.UserOffererFactory(user=pro_user, offerer=offerer)


@app.route("/e2e/pro/tear-down", methods=["GET"])
@spectree_serialize(on_success_status=204)
def tear_down() -> None:
    clean_all_database()
