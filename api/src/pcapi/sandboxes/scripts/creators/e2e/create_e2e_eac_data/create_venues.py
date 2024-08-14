from datetime import datetime
from datetime import timedelta
from itertools import chain
from itertools import count
from itertools import cycle
import typing

from pcapi.core.educational import factories as educational_factories
from pcapi.core.finance import factories as finance_factories
from pcapi.core.finance import models as finance_models
from pcapi.core.offerers import factories as offerers_factories
from pcapi.core.offerers import models as offerers_models


MAINLAND_INTERVENTION_AREA = [str(i).zfill(2) for i in chain(range(1, 95), ["2A", "2B", "mainland"]) if i != 20]
ALL_INTERVENTION_AREA = [
    *MAINLAND_INTERVENTION_AREA,
    "971",
    "972",
    "973",
    "974",
    "975",
    "976",
    "all",
]


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
        name=f"reimbursementPoint {offerer.name} 56",
        reimbursement=True,
        adageId="123546",
        adageInscriptionDate=datetime.utcnow() - timedelta(days=3),
        venueEducationalStatusId=next(educational_status_iterator),
        collectiveInterventionArea=ALL_INTERVENTION_AREA,
        departementCode="56",
        postalCode="56000",
        city="Lorient",
        siret="55208131766522",
    )
    # eac_2
    offerer = next(offerer_iterator)
    create_venue(
        managingOfferer=offerer,
        name=f"reimbursementPoint {offerer.name} 91",
        adageId="10837",
        adageInscriptionDate=datetime.utcnow() - timedelta(days=5),
        reimbursement=True,
        venueEducationalStatusId=next(educational_status_iterator),
        collectiveInterventionArea=ALL_INTERVENTION_AREA,
        departementCode="91",
        postalCode="91000",
        city="CORBEIL-ESSONNES",
        siret="44460844212351",
        venueTypeCode=offerers_models.VenueTypeCode.LIBRARY,
    )
    create_venue(
        managingOfferer=offerer,
        name=f"real_venue 1 {offerer.name}",
        venueEducationalStatusId=next(educational_status_iterator),
        collectiveInterventionArea=ALL_INTERVENTION_AREA,
        siret="44460844212690",
    )
    # eac_pending_bank_informations
    offerer = next(offerer_iterator)
    pending_reimbursement_venue = offerers_factories.VenueFactory(
        managingOfferer=offerer,
        name=f"reimbursementPoint {offerer.name}",
        adageId="789456",
        adageInscriptionDate=datetime.utcnow() - timedelta(days=30),
        venueEducationalStatusId=next(educational_status_iterator),
        collectiveInterventionArea=ALL_INTERVENTION_AREA,
        siret="55204695506065",
    )
    pending_reimbursement_venue.bankInformation = finance_factories.BankInformationFactory(
        status=finance_models.BankInformationStatus.DRAFT
    )
    offerers_factories.VenueReimbursementPointLinkFactory(
        venue=pending_reimbursement_venue,
        reimbursementPoint=pending_reimbursement_venue,
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
        siret="44478651100022",
    )
    # eac_rejected
    offerer = next(offerer_iterator)
    create_venue(
        managingOfferer=offerer,
        name=f"reimbursementPoint {offerer.name}",
        reimbursement=True,
        venueEducationalStatusId=next(educational_status_iterator),
        collectiveInterventionArea=ALL_INTERVENTION_AREA,
        siret="89749229400011",
    )
    create_venue(
        managingOfferer=offerer,
        name=f"real_venue 1 {offerer.name}",
        venueEducationalStatusId=next(educational_status_iterator),
        collectiveInterventionArea=ALL_INTERVENTION_AREA,
        siret="89749229400326",
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
        siret="53816052400012",
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
        siret="53816065600012",
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
        siret="84308238900019",
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
        siret="52423735100019",
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
        siret="53816061500018",
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
        siret="45650053700018",
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
        siret="84800945200014",
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
        siret="84817150000384",
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
        siret="84817150000632",
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
        siret="95651314700192",
        adageId="98764",
    )

    # eac_with_application_with_no_venue
    offerer = next(offerer_iterator)
    venue_with_accepted_dms_status = create_venue(
        managingOfferer=offerer,
        name=f"accepted_dms {offerer.name}",
        venueEducationalStatusId=next(educational_status_iterator),
        collectiveInterventionArea=ALL_INTERVENTION_AREA,
        siret="95651315000384",
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
        siret="95651315000387",
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


def create_venue(*, reimbursement: bool = False, **kwargs: typing.Any) -> offerers_models.Venue:
    venue = offerers_factories.VenueFactory(**kwargs)
    if reimbursement:
        venue.bankInformation = finance_factories.BankInformationFactory()
        offerers_factories.VenueReimbursementPointLinkFactory(
            venue=venue,
            reimbursementPoint=venue,
        )
    return venue


def create_venue_educational_status() -> None:
    for ident, name in VENUE_EDUCATIONAL_STATUS.items():
        offerers_factories.VenueEducationalStatusFactory(id=ident, name=name)
