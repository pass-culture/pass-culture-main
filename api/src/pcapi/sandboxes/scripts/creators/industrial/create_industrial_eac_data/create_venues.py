import typing
from datetime import datetime
from datetime import timedelta
from itertools import count
from itertools import cycle

from pcapi.core.educational import factories as educational_factories
from pcapi.core.educational.constants import ALL_INTERVENTION_AREA
from pcapi.core.finance import factories as finance_factories
from pcapi.core.geography import factories as geography_factories
from pcapi.core.offerers import factories as offerers_factories
from pcapi.core.offerers import models as offerers_models
from pcapi.sandboxes.scripts.utils.helpers import log_func_duration
from pcapi.utils import date as date_utils
from pcapi.utils import siren as siren_utils


VENUE_EDUCATIONAL_STATUS = {
    2: "Établissement public",
    3: "Association",
    4: "Établissement privé",
    5: "micro-entreprise, auto-entrepreneur",
}


@log_func_duration
def create_eac_venues(offerer_by_name: dict[str, offerers_models.Offerer]) -> None:
    create_venue_educational_status()
    educational_status_iterator = cycle(VENUE_EDUCATIONAL_STATUS.keys())

    # eac_1
    offerer = offerer_by_name["eac_1_lieu"]
    create_venue(
        managingOfferer=offerer,
        name=f"Partenaire culturel {offerer.name} 56",
        reimbursement=True,
        adageId="123546",
        adageInscriptionDate=date_utils.get_naive_utc_now() - timedelta(days=3),
        venueEducationalStatusId=next(educational_status_iterator),
        collectiveInterventionArea=ALL_INTERVENTION_AREA,
        departmentCode="56",
        postalCode="56000",
        city="Lorient",
        street="30 boulevard Léon Blum",
        latitude=47.75,
        longitude=-3.37,
        siret=siren_utils.complete_siren_or_siret(f"{offerer.siren}0001"),
    )

    # eac_2
    offerer = offerer_by_name["eac_2_lieu [BON EAC]"]
    create_venue(
        managingOfferer=offerer,
        name=f"Partenaire culturel {offerer.name} 91",
        adageId="10837",
        adageInscriptionDate=date_utils.get_naive_utc_now() - timedelta(days=5),
        reimbursement=True,
        venueEducationalStatusId=next(educational_status_iterator),
        collectiveInterventionArea=ALL_INTERVENTION_AREA,
        departmentCode="91",
        postalCode="91000",
        city="CORBEIL-ESSONNES",
        street="10 rue Feray",
        latitude=48.60,
        longitude=2.48,
        siret=siren_utils.complete_siren_or_siret(f"{offerer.siren}0001"),
        venueTypeCode=offerers_models.VenueTypeCode.LIBRARY,
    )
    create_venue(
        managingOfferer=offerer,
        name=f"real_venue 1 {offerer.name}",
        venueEducationalStatusId=next(educational_status_iterator),
        collectiveInterventionArea=ALL_INTERVENTION_AREA,
        siret=siren_utils.complete_siren_or_siret(f"{offerer.siren}0002"),
    )

    # eac_pending_bank_informations
    offerer = offerer_by_name["eac_pending_bank_informations"]
    offerers_factories.VenueFactory.create(
        managingOfferer=offerer,
        name=f"Partenaire culturel {offerer.name}",
        adageId="789456",
        adageInscriptionDate=date_utils.get_naive_utc_now() - timedelta(days=30),
        venueEducationalStatusId=next(educational_status_iterator),
        collectiveInterventionArea=ALL_INTERVENTION_AREA,
        siret=siren_utils.complete_siren_or_siret(f"{offerer.siren}0001"),
    )

    # eac_no_cb
    offerer = offerer_by_name["eac_no_cb"]
    create_venue(
        managingOfferer=offerer,
        name=f"real_venue 1 {offerer.name}",
        adageId="698748",
        adageInscriptionDate=date_utils.get_naive_utc_now() - timedelta(days=13),
        venueEducationalStatusId=next(educational_status_iterator),
        collectiveInterventionArea=ALL_INTERVENTION_AREA,
        siret=siren_utils.complete_siren_or_siret(f"{offerer.siren}0001"),
    )

    # eac_rejected
    offerer = offerer_by_name["eac_rejected"]
    create_venue(
        managingOfferer=offerer,
        name=f"Partenaire culturel {offerer.name}",
        reimbursement=True,
        venueEducationalStatusId=next(educational_status_iterator),
        collectiveInterventionArea=ALL_INTERVENTION_AREA,
        siret=siren_utils.complete_siren_or_siret(f"{offerer.siren}0001"),
    )
    create_venue(
        managingOfferer=offerer,
        name=f"real_venue 1 {offerer.name}",
        venueEducationalStatusId=next(educational_status_iterator),
        collectiveInterventionArea=ALL_INTERVENTION_AREA,
        siret=siren_utils.complete_siren_or_siret(f"{offerer.siren}0002"),
    )

    # DMS venues
    application_id_generator = count(11922836)

    # eac_accepte
    offerer = offerer_by_name["eac_accepte"]
    venue = create_venue(
        managingOfferer=offerer,
        name=f"accepted_dms {offerer.name}",
        venueEducationalStatusId=next(educational_status_iterator),
        collectiveInterventionArea=ALL_INTERVENTION_AREA,
        siret=siren_utils.complete_siren_or_siret(f"{offerer.siren}0001"),
    )
    educational_factories.CollectiveDmsApplicationFactory.create(
        venue=venue,
        application=next(application_id_generator),
        procedure=57189,
        lastChangeDate=datetime.fromisoformat("2023-03-26T16:08:35+01:00"),
        depositDate=datetime.fromisoformat("2024-03-23T16:08:33+01:00"),
        expirationDate=datetime.fromisoformat("2025-03-23T16:08:33+01:00"),
        buildDate=datetime.fromisoformat("2023-03-23T16:08:35+01:00"),
        instructionDate=datetime.fromisoformat("2025-03-24T16:08:33+01:00"),
        processingDate=datetime.fromisoformat("2025-03-25T16:08:33+01:00"),
        state="accepte",
    )

    # eac_sans_suite
    offerer = offerer_by_name["eac_sans_suite"]
    venue = create_venue(
        managingOfferer=offerer,
        name=f"accepted_dms {offerer.name}",
        venueEducationalStatusId=next(educational_status_iterator),
        collectiveInterventionArea=ALL_INTERVENTION_AREA,
        siret=siren_utils.complete_siren_or_siret(f"{offerer.siren}0001"),
    )
    educational_factories.CollectiveDmsApplicationFactory.create(
        venue=venue,
        application=next(application_id_generator),
        procedure=57189,
        lastChangeDate=datetime.fromisoformat("2023-03-26T16:08:35+01:00"),
        depositDate=datetime.fromisoformat("2024-03-23T16:08:33+01:00"),
        expirationDate=datetime.fromisoformat("2025-03-23T16:08:33+01:00"),
        buildDate=datetime.fromisoformat("2023-03-23T16:08:35+01:00"),
        instructionDate=datetime.fromisoformat("2025-03-24T16:08:33+01:00"),
        processingDate=datetime.fromisoformat("2025-03-25T16:08:33+01:00"),
        state="sans_suite",
    )

    # eac_en_construction
    offerer = offerer_by_name["eac_en_construction"]
    venue = create_venue(
        managingOfferer=offerer,
        name=f"accepted_dms {offerer.name}",
        venueEducationalStatusId=next(educational_status_iterator),
        collectiveInterventionArea=ALL_INTERVENTION_AREA,
        siret=siren_utils.complete_siren_or_siret(f"{offerer.siren}0001"),
    )
    educational_factories.CollectiveDmsApplicationFactory.create(
        venue=venue,
        application=next(application_id_generator),
        procedure=57189,
        lastChangeDate=datetime.fromisoformat("2023-03-26T16:08:35+01:00"),
        depositDate=datetime.fromisoformat("2024-03-23T16:08:33+01:00"),
        expirationDate=datetime.fromisoformat("2025-03-23T16:08:33+01:00"),
        buildDate=datetime.fromisoformat("2023-03-23T16:08:35+01:00"),
        instructionDate=None,
        processingDate=None,
        state="en_construction",
    )

    # eac_refuse
    offerer = offerer_by_name["eac_refuse"]
    venue = create_venue(
        managingOfferer=offerer,
        name=f"accepted_dms {offerer.name}",
        venueEducationalStatusId=next(educational_status_iterator),
        collectiveInterventionArea=ALL_INTERVENTION_AREA,
        siret=siren_utils.complete_siren_or_siret(f"{offerer.siren}0001"),
    )
    educational_factories.CollectiveDmsApplicationFactory.create(
        venue=venue,
        application=next(application_id_generator),
        procedure=57189,
        lastChangeDate=datetime.fromisoformat("2023-03-26T16:08:35+01:00"),
        depositDate=datetime.fromisoformat("2024-03-23T16:08:33+01:00"),
        expirationDate=datetime.fromisoformat("2025-03-23T16:08:33+01:00"),
        buildDate=datetime.fromisoformat("2023-03-23T16:08:35+01:00"),
        instructionDate=datetime.fromisoformat("2025-03-24T16:08:33+01:00"),
        processingDate=datetime.fromisoformat("2025-03-25T16:08:33+01:00"),
        state="refuse",
    )

    # eac_en_instruction
    offerer = offerer_by_name["eac_en_instruction"]
    venue = create_venue(
        managingOfferer=offerer,
        name=f"accepted_dms {offerer.name}",
        venueEducationalStatusId=next(educational_status_iterator),
        collectiveInterventionArea=ALL_INTERVENTION_AREA,
        siret=siren_utils.complete_siren_or_siret(f"{offerer.siren}0001"),
    )
    educational_factories.CollectiveDmsApplicationFactory.create(
        venue=venue,
        application=next(application_id_generator),
        procedure=57189,
        lastChangeDate=datetime.fromisoformat("2023-03-26T16:08:35+01:00"),
        depositDate=datetime.fromisoformat("2024-03-23T16:08:33+01:00"),
        expirationDate=None,
        buildDate=datetime.fromisoformat("2023-03-23T16:08:35+01:00"),
        instructionDate=datetime.fromisoformat("2025-03-24T16:08:33+01:00"),
        processingDate=None,
        state="en_instruction",
    )

    # eac_complete_30+d
    offerer = offerer_by_name["eac_complete_30+d"]
    venue = create_venue(
        managingOfferer=offerer,
        name=f"accepted_dms {offerer.name}",
        venueEducationalStatusId=next(educational_status_iterator),
        collectiveInterventionArea=ALL_INTERVENTION_AREA,
        siret=siren_utils.complete_siren_or_siret(f"{offerer.siren}0001"),
        adageId="98762",
        adageInscriptionDate=date_utils.get_naive_utc_now() - timedelta(days=30),
    )
    educational_factories.CollectiveDmsApplicationFactory.create(
        venue=venue,
        application=next(application_id_generator),
        procedure=57189,
        lastChangeDate=datetime.fromisoformat("2022-11-08 14:09:33+00:00"),
        depositDate=datetime.fromisoformat("2022-05-17 14:43:22+00:00"),
        expirationDate=datetime.fromisoformat("2025-11-08 14:09:31+00:00"),
        buildDate=datetime.fromisoformat("2022-05-17 14:43:22+00:00"),
        instructionDate=datetime.fromisoformat("2022-10-25 12:40:41+00:00"),
        processingDate=datetime.fromisoformat("2022-11-08 14:09:31+00:00"),
        state="accepte",
    )

    # eac_complete_30-d
    offerer = offerer_by_name["eac_complete_30-d"]
    venue = create_venue(
        managingOfferer=offerer,
        name=f"accepted_dms {offerer.name}",
        venueEducationalStatusId=next(educational_status_iterator),
        collectiveInterventionArea=ALL_INTERVENTION_AREA,
        siret=siren_utils.complete_siren_or_siret(f"{offerer.siren}0001"),
        adageId="98763",
        adageInscriptionDate=date_utils.get_naive_utc_now(),
    )
    educational_factories.CollectiveDmsApplicationFactory.create(
        venue=venue,
        application=next(application_id_generator),
        procedure=57189,
        lastChangeDate=date_utils.get_naive_utc_now(),
        depositDate=datetime.fromisoformat("2022-05-17 14:43:22+00:00"),
        expirationDate=datetime.fromisoformat("2025-11-08 14:09:31+00:00"),
        buildDate=datetime.fromisoformat("2022-05-17 14:43:22+00:00"),
        instructionDate=datetime.fromisoformat("2022-10-25 12:40:41+00:00"),
        processingDate=date_utils.get_naive_utc_now(),
        state="accepte",
    )

    # eac_with_two_adage_venues
    offerer = offerer_by_name["eac_with_two_adage_venues"]
    venue_with_accepted_dms_status = create_venue(
        managingOfferer=offerer,
        name=f"accepted_dms {offerer.name}",
        venueEducationalStatusId=next(educational_status_iterator),
        collectiveInterventionArea=ALL_INTERVENTION_AREA,
        siret=siren_utils.complete_siren_or_siret(f"{offerer.siren}0001"),
    )
    educational_factories.CollectiveDmsApplicationFactory.create(
        venue=venue_with_accepted_dms_status,
        application=next(application_id_generator),
        procedure=57189,
        lastChangeDate=datetime.fromisoformat("2023-03-26T16:08:35+01:00"),
        depositDate=datetime.fromisoformat("2024-03-23T16:08:33+01:00"),
        expirationDate=datetime.fromisoformat("2025-03-23T16:08:33+01:00"),
        buildDate=datetime.fromisoformat("2023-03-23T16:08:35+01:00"),
        instructionDate=datetime.fromisoformat("2025-03-24T16:08:33+01:00"),
        processingDate=datetime.fromisoformat("2025-03-25T16:08:33+01:00"),
        state="accepte",
    )
    venue_with_rejected_dms_status = create_venue(
        managingOfferer=offerer,
        name=f"rejected_dms {offerer.name}",
        venueEducationalStatusId=next(educational_status_iterator),
        collectiveInterventionArea=ALL_INTERVENTION_AREA,
        siret=siren_utils.complete_siren_or_siret(f"{offerer.siren}0002"),
    )
    educational_factories.CollectiveDmsApplicationFactory.create(
        venue=venue_with_rejected_dms_status,
        application=next(application_id_generator),
        procedure=57189,
        lastChangeDate=datetime.fromisoformat("2023-03-26T16:08:35+01:00"),
        depositDate=datetime.fromisoformat("2024-03-23T16:08:33+01:00"),
        expirationDate=datetime.fromisoformat("2025-03-23T16:08:33+01:00"),
        buildDate=datetime.fromisoformat("2023-03-23T16:08:35+01:00"),
        instructionDate=datetime.fromisoformat("2025-03-24T16:08:33+01:00"),
        processingDate=datetime.fromisoformat("2025-03-25T16:08:33+01:00"),
        state="refuse",
    )

    # eac_with_no_offers
    offerer = offerer_by_name["eac_with_no_offers"]
    venue_with_accepted_dms_status = create_venue(
        managingOfferer=offerer,
        name=f"Lieu {offerer.name}",
        venueEducationalStatusId=next(educational_status_iterator),
        collectiveInterventionArea=ALL_INTERVENTION_AREA,
        siret=siren_utils.complete_siren_or_siret(f"{offerer.siren}0001"),
        adageId="98764",
    )

    # eac_with_application_with_no_venue
    offerer = offerer_by_name["eac_with_application_with_no_venue"]
    venue_with_accepted_dms_status = create_venue(
        managingOfferer=offerer,
        name=f"accepted_dms {offerer.name}",
        venueEducationalStatusId=next(educational_status_iterator),
        collectiveInterventionArea=ALL_INTERVENTION_AREA,
        siret=siren_utils.complete_siren_or_siret(f"{offerer.siren}0001"),
    )
    educational_factories.CollectiveDmsApplicationFactory.create(
        venue=venue_with_accepted_dms_status,
        application=next(application_id_generator),
        procedure=57189,
        lastChangeDate=datetime.fromisoformat("2023-03-26T16:08:35+01:00"),
        depositDate=datetime.fromisoformat("2024-03-23T16:08:33+01:00"),
        expirationDate=datetime.fromisoformat("2025-03-23T16:08:33+01:00"),
        buildDate=datetime.fromisoformat("2023-03-23T16:08:35+01:00"),
        instructionDate=datetime.fromisoformat("2025-03-24T16:08:33+01:00"),
        processingDate=datetime.fromisoformat("2025-03-25T16:08:33+01:00"),
        state="accepte",
    )
    educational_factories.CollectiveDmsApplicationWithNoVenueFactory.create(
        siret=siren_utils.complete_siren_or_siret(f"{offerer.siren}0002"),
        application=next(application_id_generator),
        procedure=57189,
        lastChangeDate=datetime.fromisoformat("2023-03-25T16:08:35+01:00"),
        depositDate=datetime.fromisoformat("2024-03-22T16:08:33+01:00"),
        expirationDate=datetime.fromisoformat("2025-03-22T16:08:33+01:00"),
        buildDate=datetime.fromisoformat("2023-03-22T16:08:35+01:00"),
        instructionDate=datetime.fromisoformat("2025-03-23T16:08:33+01:00"),
        processingDate=datetime.fromisoformat("2025-03-24T16:08:33+01:00"),
        state="refuse",
    )

    # eac_with_displayed_status_cases
    offerer = offerer_by_name["eac_with_displayed_status_cases"]
    create_venue(
        managingOfferer=offerer,
        name=f"{offerer.name} PC_PRO",
        reimbursement=True,
        adageId="123547",
        adageInscriptionDate=date_utils.get_naive_utc_now() - timedelta(days=3),
        venueEducationalStatusId=next(educational_status_iterator),
        collectiveInterventionArea=ALL_INTERVENTION_AREA,
        departmentCode="57",
        postalCode="57000",
        city="Lorient",
        street="30 boulevard Léon Blum",
        latitude=47.75,
        longitude=-3.37,
        siret=siren_utils.complete_siren_or_siret(f"{offerer.siren}0001"),
        pricing_point="self",
    )
    create_venue(
        managingOfferer=offerer,
        name=f"{offerer.name} PUBLIC_API",
        reimbursement=True,
        adageId="123548",
        adageInscriptionDate=date_utils.get_naive_utc_now() - timedelta(days=3),
        venueEducationalStatusId=next(educational_status_iterator),
        collectiveInterventionArea=ALL_INTERVENTION_AREA,
        departmentCode="57",
        postalCode="57000",
        city="Lorient",
        street="30 boulevard Léon Blum",
        latitude=47.75,
        longitude=-3.37,
        siret=siren_utils.complete_siren_or_siret(f"{offerer.siren}0002"),
        pricing_point="self",
    )

    # eac_with_deposits_by_period
    offerer = offerer_by_name["eac_with_deposits_by_period"]
    create_venue(
        managingOfferer=offerer,
        name=offerer.name,
        venueEducationalStatusId=next(educational_status_iterator),
        collectiveInterventionArea=ALL_INTERVENTION_AREA,
        siret=siren_utils.complete_siren_or_siret(f"{offerer.siren}0001"),
        adageId="123599",
    )


def create_venue(*, reimbursement: bool = False, **kwargs: typing.Any) -> offerers_models.Venue:
    location_fields = {
        "street",
        "banId",
        "latitude",
        "longitude",
        "postalCode",
        "city",
        "inseeCode",
        "departmentCode",
        "isManualEdition",
    }
    location_kwargs = {k: v for k, v in kwargs.items() if k in location_fields}
    venue_kwargs = {k: v for k, v in kwargs.items() if k not in location_fields}

    venue = offerers_factories.VenueFactory.create(
        **venue_kwargs,
        collectiveEmail="email@exemple.com",
        isPermanent=True,
        offererAddress__address=geography_factories.AddressFactory.create(**location_kwargs),
    )
    if reimbursement:
        bank_account = finance_factories.BankAccountFactory.create(offerer=venue.managingOfferer)
        offerers_factories.VenueBankAccountLinkFactory.create(venue=venue, bankAccount=bank_account)
    return venue


def create_venue_educational_status() -> None:
    for ident, name in VENUE_EDUCATIONAL_STATUS.items():
        offerers_factories.VenueEducationalStatusFactory.create(id=ident, name=name)
