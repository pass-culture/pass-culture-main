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
def setup_create_event_individual_offer() -> None:
    clean_all_database()
    pro_user = users_factories.ProFactory(
        lastName="PC Test Pro",
        firstName="97 0",
        departementCode="97",
        postalCode="97100",
        email="pro_adage_eligible@example.com",
    )
    siren = str(MOCK_ADAGE_ELIGIBLE_SIREN)
    venue = offerers_factories.VenueFactory(
        managingOfferer__siren=siren,
        bookingEmail="fake@email.com",
        comment="Salle de cinéma",
        siret="88145723811111",
        venueTypeCode=VenueTypeCode.MOVIE,
    )
    # create bank account to avoid first offer pop up
    finance_factories.BankAccountFactory(offerer=venue.managingOfferer)
    offerers_factories.UserOffererFactory(user=pro_user, offerer=venue.managingOfferer)


@app.route("/e2e/pro/create-thing-individual-offer", methods=["GET"])
@spectree_serialize(on_success_status=204)
def setup_create_thing_individual_offer() -> None:
    clean_all_database()
    pro_user = users_factories.ProFactory(
        lastName="PC Test Pro",
        firstName="97 0",
        departementCode="97",
        postalCode="97100",
        email="pro_adage_eligible@example.com",
    )
    siren = str(MOCK_ADAGE_ELIGIBLE_SIREN)
    venue = offerers_factories.VenueFactory(
        managingOfferer__siren=siren,
        bookingEmail="fake@email.com",
        comment="Salle de cinéma",
        siret=f"{MOCK_ADAGE_ELIGIBLE_SIREN}11111",
        venueTypeCode=VenueTypeCode.MOVIE,
    )
    # create bank account to avoid first offer pop up
    finance_factories.BankAccountFactory(offerer=venue.managingOfferer)
    offerers_factories.UserOffererFactory(user=pro_user, offerer=venue.managingOfferer)


@app.route("/e2e/pro/create-venue", methods=["GET"])
@spectree_serialize(on_success_status=204)
def setup_create_venue() -> None:
    clean_all_database()
    pro_user = users_factories.ProFactory(
        lastName="PC Test Pro",
        firstName="97 0",
        departementCode="97",
        postalCode="97100",
        email="retention_structures@example.com",
    )
    offerer = offerers_factories.OffererFactory(name="Bar des amis", siren="222222233")
    offerers_factories.VenueFactory(
        venueTypeCode=VenueTypeCode.MOVIE,
        managingOfferer=offerer,
    )
    offerers_factories.UserOffererFactory(user=pro_user, offerer=offerer)


@app.route("/e2e/pro/tear-down", methods=["GET"])
@spectree_serialize(on_success_status=204)
def tear_down() -> None:
    clean_all_database()
