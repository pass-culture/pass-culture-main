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


@app.route("/e2e/pro/update-venue", methods=["GET"])
@spectree_serialize(on_success_status=204)
def setup_update_venue() -> None:
    clean_all_database()
    users_factories.AdminFactory(
        lastName="PC Test Pro",
        firstName="93 1",
        departementCode="93",
        postalCode="93100",
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
def setup_discovery() -> None:
    clean_all_database()
    educational_factories.EducationalRedactorFactory(
        lastName="PC Test Pro",
        firstName="97 0",
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
        bookingEmail="fake@email.com",
        comment="Salle de cinéma",
        siret="88145723811111",
        venueTypeCode=VenueTypeCode.MOVIE,
    )
    offerers_factories.VenueFactory(
        id=1234567890,
        name="Librairie des GTls",
        venueTypeCode=VenueTypeCode.BOOKSTORE,
        managingOfferer=user_offerer.offerer,
        latitude=45.91967,
        longitude=3.06504,
        address="13 AVENUE BARADUC",
        postalCode="63140",
        city="CHATEL-GUYON",
        departementCode="63",
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
        name="JEAN LE COUTALLER",
        institutionType="COLLEGE",
        city="LORIENT",
        postalCode="56100",
    )
    educational_factories.EducationalYearFactory()
    educational_factories.EducationalDomainFactory()
    fill_adage_playlists()


@app.route("/e2e/pro/tear-down", methods=["GET"])
@spectree_serialize(on_success_status=204)
def tear_down() -> None:
    clean_all_database()
