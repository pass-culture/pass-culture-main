from flask import current_app as app

from pcapi.core.educational import factories as educational_factories
from pcapi.core.educational.utils import DEFAULT_UAI
from pcapi.core.finance import factories as finance_factories
from pcapi.core.offerers import factories as offerers_factories
from pcapi.core.offerers.models import VenueTypeCode
from pcapi.core.users import factories as users_factories
from pcapi.repository.clean_database import clean_all_database
from pcapi.sandboxes.scripts.creators.industrial.create_industrial_eac_data.create_venues import ALL_INTERVENTION_AREA
from pcapi.sandboxes.scripts.creators.industrial.create_industrial_eac_data.create_venues import create_venue
from pcapi.sandboxes.scripts.creators.industrial.create_industrial_eac_data.fill import fill_adage_playlists
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


@app.route("/e2e/pro/update-venue", methods=["GET"])
@spectree_serialize(on_success_status=204)
def setup_data_for_update_venue_e2e_test() -> None:
    clean_all_database()
    users_factories.AdminFactory(
        email="pctest.admin93.0@example.com",
    )
    offerer = offerers_factories.OffererFactory(name="Lieu non dit", siren="222222233")
    offerers_factories.VenueFactory(
        venueTypeCode=VenueTypeCode.MOVIE,
        managingOfferer=offerer,
    )
    offerers_factories.VenueFactory(
        name="Cinéma de la fin Bis",
        venueTypeCode=VenueTypeCode.MOVIE,
        managingOfferer=offerer,
    )
    offerers_factories.VenueLabelFactory(label="Musée de France")


@app.route("/e2e/adage/discovery", methods=["GET"])
@spectree_serialize(on_success_status=204)
def setup__data_for_adage_discovery_e2e_test() -> None:
    clean_all_database()
    educational_factories.EducationalRedactorFactory(
        email="pro_adage_eligible@example.com",
    )
    siren = str(MOCK_ADAGE_ELIGIBLE_SIREN)
    user_offerer = offerers_factories.UserOffererFactory(
        user__email="eac_2_lieu@example.com",
        offerer__name="eac_2_lieu [BON EAC]",
        offerer__siren=siren,
        offerer__allowedOnAdage=True,
    )
    offerers_factories.VenueFactory(
        managingOfferer=user_offerer.offerer,
        comment="Salle de cinéma",
        siret="88145723811111",
        venueTypeCode=VenueTypeCode.MOVIE,
    )
    offerers_factories.VenueFactory(
        id=1234567890,
        name="Librairie des GTls",
        venueTypeCode=VenueTypeCode.BOOKSTORE,
        managingOfferer=user_offerer.offerer,
    )
    venue = create_venue(
        managingOfferer=user_offerer.offerer,
        name=f"real_venue 1 {user_offerer.offerer.name}",
        venueEducationalStatusId=offerers_factories.VenueEducationalStatusFactory().id,  # Établissement public
        collectiveInterventionArea=ALL_INTERVENTION_AREA,
        siret="44460844212690",
    )
    collective_offer_template = educational_factories.CollectiveOfferTemplateFactory(venue=venue, id=58)
    educational_factories.CollectiveOfferFactory(venue=venue, templateId=collective_offer_template.id)
    educational_factories.EducationalInstitutionFactory(
        institutionId=DEFAULT_UAI,
    )
    educational_factories.EducationalYearFactory()
    educational_factories.EducationalDomainFactory()
    fill_adage_playlists()
