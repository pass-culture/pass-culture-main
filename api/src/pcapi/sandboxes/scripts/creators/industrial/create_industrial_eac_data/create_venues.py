from datetime import datetime
from datetime import timedelta
from itertools import count
from itertools import cycle
import typing

from pcapi.core.educational import factories as educational_factories
from pcapi.core.educational.constants import ALL_INTERVENTION_AREA
from pcapi.core.finance import factories as finance_factories
from pcapi.core.offerers import factories as offerers_factories
from pcapi.core.offerers import models as offerers_models
from pcapi.utils import siren as siren_utils


VENUE_EDUCATIONAL_STATUS = {
    2: "Établissement public",
    3: "Association",
    4: "Établissement privé",
    5: "micro-entreprise, auto-entrepreneur",
}


def create_venues(offerer_list: list[offerers_models.Offerer]) -> None:
    create_venue_educational_status()
    offerer_iterator = iter(offerer_list)
    educational_status_iterator = cycle(VENUE_EDUCATIONAL_STATUS.keys())
    # eac_1
    offerer = next(offerer_iterator)
    create_venue(
        managingOfferer=offerer,
        name=f"Partenaire culturel {offerer.name} 56",
        reimbursement=True,
        adageId="123546",
        adageInscriptionDate=datetime.utcnow() - timedelta(days=3),
        venueEducationalStatusId=next(educational_status_iterator),
        collectiveInterventionArea=ALL_INTERVENTION_AREA,
        departementCode="56",
        postalCode="56000",
        city="Lorient",
        street="30 boulevard Léon Blum",
        latitude=47.75,
        longitude=-3.37,
        siret=siren_utils.complete_siren_or_siret(f"{offerer.siren}0001"),
    )
    # eac_2
    offerer = next(offerer_iterator)
    create_venue(
        managingOfferer=offerer,
        name=f"Partenaire culturel {offerer.name} 91",
        adageId="10837",
        adageInscriptionDate=datetime.utcnow() - timedelta(days=5),
        reimbursement=True,
        venueEducationalStatusId=next(educational_status_iterator),
        collectiveInterventionArea=ALL_INTERVENTION_AREA,
        departementCode="91",
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
    offerer = next(offerer_iterator)
    offerers_factories.VenueFactory(
        managingOfferer=offerer,
        name=f"Partenaire culturel {offerer.name}",
        adageId="789456",
        adageInscriptionDate=datetime.utcnow() - timedelta(days=30),
        venueEducationalStatusId=next(educational_status_iterator),
        collectiveInterventionArea=ALL_INTERVENTION_AREA,
        siret=siren_utils.complete_siren_or_siret(f"{offerer.siren}0001"),
    )

    # eac_no_cb
    offerer = next(offerer_iterator)
    create_venue(
        managingOfferer=offerer,
        name=f"real_venue 1 {offerer.name}",
        adageId="698748",
        adageInscriptionDate=datetime.utcnow() - timedelta(days=13),
        venueEducationalStatusId=next(educational_status_iterator),
        collectiveInterventionArea=ALL_INTERVENTION_AREA,
        siret=siren_utils.complete_siren_or_siret(f"{offerer.siren}0001"),
    )
    # eac_rejected
    offerer = next(offerer_iterator)
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
    offerer = next(offerer_iterator)
    venue = create_venue(
        managingOfferer=offerer,
        name=f"accepted_dms {offerer.name}",
        venueEducationalStatusId=next(educational_status_iterator),
        collectiveInterventionArea=ALL_INTERVENTION_AREA,
        siret=siren_utils.complete_siren_or_siret(f"{offerer.siren}0001"),
    )
    educational_factories.CollectiveDmsApplicationFactory(
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
    offerer = next(offerer_iterator)
    venue = create_venue(
        managingOfferer=offerer,
        name=f"accepted_dms {offerer.name}",
        venueEducationalStatusId=next(educational_status_iterator),
        collectiveInterventionArea=ALL_INTERVENTION_AREA,
        siret=siren_utils.complete_siren_or_siret(f"{offerer.siren}0001"),
    )
    educational_factories.CollectiveDmsApplicationFactory(
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
    offerer = next(offerer_iterator)
    venue = create_venue(
        managingOfferer=offerer,
        name=f"accepted_dms {offerer.name}",
        venueEducationalStatusId=next(educational_status_iterator),
        collectiveInterventionArea=ALL_INTERVENTION_AREA,
        siret=siren_utils.complete_siren_or_siret(f"{offerer.siren}0001"),
    )
    educational_factories.CollectiveDmsApplicationFactory(
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
    offerer = next(offerer_iterator)
    venue = create_venue(
        managingOfferer=offerer,
        name=f"accepted_dms {offerer.name}",
        venueEducationalStatusId=next(educational_status_iterator),
        collectiveInterventionArea=ALL_INTERVENTION_AREA,
        siret=siren_utils.complete_siren_or_siret(f"{offerer.siren}0001"),
    )
    educational_factories.CollectiveDmsApplicationFactory(
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
    offerer = next(offerer_iterator)
    venue = create_venue(
        managingOfferer=offerer,
        name=f"accepted_dms {offerer.name}",
        venueEducationalStatusId=next(educational_status_iterator),
        collectiveInterventionArea=ALL_INTERVENTION_AREA,
        siret=siren_utils.complete_siren_or_siret(f"{offerer.siren}0001"),
    )
    educational_factories.CollectiveDmsApplicationFactory(
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
    offerer = next(offerer_iterator)
    venue = create_venue(
        managingOfferer=offerer,
        name=f"accepted_dms {offerer.name}",
        venueEducationalStatusId=next(educational_status_iterator),
        collectiveInterventionArea=ALL_INTERVENTION_AREA,
        siret=siren_utils.complete_siren_or_siret(f"{offerer.siren}0001"),
        adageId="98762",
        adageInscriptionDate=datetime.utcnow() - timedelta(days=30),
    )
    educational_factories.CollectiveDmsApplicationFactory(
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
    offerer = next(offerer_iterator)
    venue = create_venue(
        managingOfferer=offerer,
        name=f"accepted_dms {offerer.name}",
        venueEducationalStatusId=next(educational_status_iterator),
        collectiveInterventionArea=ALL_INTERVENTION_AREA,
        siret=siren_utils.complete_siren_or_siret(f"{offerer.siren}0001"),
        adageId="98763",
        adageInscriptionDate=datetime.utcnow(),
    )
    educational_factories.CollectiveDmsApplicationFactory(
        venue=venue,
        application=next(application_id_generator),
        procedure=57189,
        lastChangeDate=datetime.utcnow(),
        depositDate=datetime.fromisoformat("2022-05-17 14:43:22+00:00"),
        expirationDate=datetime.fromisoformat("2025-11-08 14:09:31+00:00"),
        buildDate=datetime.fromisoformat("2022-05-17 14:43:22+00:00"),
        instructionDate=datetime.fromisoformat("2022-10-25 12:40:41+00:00"),
        processingDate=datetime.utcnow(),
        state="accepte",
    )
    # eac_with_two_adage_venues
    offerer = next(offerer_iterator)
    venue_with_accepted_dms_status = create_venue(
        managingOfferer=offerer,
        name=f"accepted_dms {offerer.name}",
        venueEducationalStatusId=next(educational_status_iterator),
        collectiveInterventionArea=ALL_INTERVENTION_AREA,
        siret=siren_utils.complete_siren_or_siret(f"{offerer.siren}0001"),
    )
    educational_factories.CollectiveDmsApplicationFactory(
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
    educational_factories.CollectiveDmsApplicationFactory(
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
    offerer = next(offerer_iterator)
    venue_with_accepted_dms_status = create_venue(
        managingOfferer=offerer,
        name=f"Lieu {offerer.name}",
        venueEducationalStatusId=next(educational_status_iterator),
        collectiveInterventionArea=ALL_INTERVENTION_AREA,
        siret=siren_utils.complete_siren_or_siret(f"{offerer.siren}0001"),
        adageId="98764",
    )

    # eac_with_application_with_no_venue
    offerer = next(offerer_iterator)
    venue_with_accepted_dms_status = create_venue(
        managingOfferer=offerer,
        name=f"accepted_dms {offerer.name}",
        venueEducationalStatusId=next(educational_status_iterator),
        collectiveInterventionArea=ALL_INTERVENTION_AREA,
        siret=siren_utils.complete_siren_or_siret(f"{offerer.siren}0001"),
    )
    educational_factories.CollectiveDmsApplicationFactory(
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
    educational_factories.CollectiveDmsApplicationWithNoVenueFactory(
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
    offerer = next(offerer_iterator)
    create_venue(
        managingOfferer=offerer,
        name=f"{offerer.name} PC_PRO",
        reimbursement=True,
        adageId="123547",
        adageInscriptionDate=datetime.utcnow() - timedelta(days=3),
        venueEducationalStatusId=next(educational_status_iterator),
        collectiveInterventionArea=ALL_INTERVENTION_AREA,
        departementCode="57",
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
        adageInscriptionDate=datetime.utcnow() - timedelta(days=3),
        venueEducationalStatusId=next(educational_status_iterator),
        collectiveInterventionArea=ALL_INTERVENTION_AREA,
        departementCode="57",
        postalCode="57000",
        city="Lorient",
        street="30 boulevard Léon Blum",
        latitude=47.75,
        longitude=-3.37,
        siret=siren_utils.complete_siren_or_siret(f"{offerer.siren}0002"),
        pricing_point="self",
    )
    # eac_with_addresses_cases
    offerer = next(offerer_iterator)
    create_venue(
        managingOfferer=offerer,
        name=f"{offerer.name} PC_PRO",
        reimbursement=True,
        adageId="123549",
        adageInscriptionDate=datetime.utcnow() - timedelta(days=3),
        venueEducationalStatusId=next(educational_status_iterator),
        collectiveInterventionArea=ALL_INTERVENTION_AREA,
        departementCode="57",
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
        adageId="123550",
        adageInscriptionDate=datetime.utcnow() - timedelta(days=3),
        venueEducationalStatusId=next(educational_status_iterator),
        collectiveInterventionArea=ALL_INTERVENTION_AREA,
        departementCode="33",
        postalCode="33000",
        city="Bordeaux",
        street="10 rue Sainte-Colombe",
        latitude=44.83,
        longitude=-0.57,
        siret=siren_utils.complete_siren_or_siret(f"{offerer.siren}0002"),
        pricing_point="self",
    )


def create_venue(*, reimbursement: bool = False, **kwargs: typing.Any) -> offerers_models.Venue:
    venue = offerers_factories.VenueFactory(**kwargs)
    if reimbursement:
        bank_account = finance_factories.BankAccountFactory(offerer=venue.managingOfferer)
        offerers_factories.VenueBankAccountLinkFactory(venue=venue, bankAccount=bank_account)
    return venue


def create_venue_educational_status() -> None:
    for ident, name in VENUE_EDUCATIONAL_STATUS.items():
        offerers_factories.VenueEducationalStatusFactory(id=ident, name=name)
