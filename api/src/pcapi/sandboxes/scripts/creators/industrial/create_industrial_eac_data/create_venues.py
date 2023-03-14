from datetime import datetime
from datetime import timedelta
from itertools import chain
from itertools import cycle

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
    )
    # eac_2
    offerer = next(offerer_iterator)
    create_venue(
        managingOfferer=offerer,
        name=f"reimbursementPoint {offerer.name} 91",
        adageId="7894896",
        adageInscriptionDate=datetime.utcnow() - timedelta(days=5),
        reimbursement=True,
        siret="12345678200010",
        venueEducationalStatusId=next(educational_status_iterator),
        collectiveInterventionArea=ALL_INTERVENTION_AREA,
        departementCode="91",
        postalCode="91000",
        city="CORBEIL-ESSONNES",
    )
    create_venue(
        managingOfferer=offerer,
        name=f"real_venue 1 {offerer.name}",
        siret="12345678200036",
        venueEducationalStatusId=next(educational_status_iterator),
        collectiveInterventionArea=ALL_INTERVENTION_AREA,
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
    )
    # eac_rejected
    offerer = next(offerer_iterator)
    create_venue(
        managingOfferer=offerer,
        name=f"reimbursementPoint {offerer.name}",
        reimbursement=True,
        venueEducationalStatusId=next(educational_status_iterator),
        collectiveInterventionArea=ALL_INTERVENTION_AREA,
    )
    create_venue(
        managingOfferer=offerer,
        name=f"real_venue 1 {offerer.name}",
        venueEducationalStatusId=next(educational_status_iterator),
        collectiveInterventionArea=ALL_INTERVENTION_AREA,
    )
    # pending_eac
    offerer = next(offerer_iterator)
    venue = create_venue(
        managingOfferer=offerer,
        name=f"waiting_dms 1 {offerer.name}",
        venueEducationalStatusId=next(educational_status_iterator),
        collectiveInterventionArea=ALL_INTERVENTION_AREA,
        siret="42883745400050",
    )
    educational_factories.CollectiveDmsApplicationFactory(
        venue=venue,
        application=11922836,
        procedure=71675,
        lastChangeDate=datetime.fromisoformat("2023-03-23T16:08:35+01:00"),
        depositDate=datetime.fromisoformat("2024-03-23T16:08:33+01:00"),
        expirationDate=datetime.fromisoformat("2024-03-23T16:08:33+01:00"),
        buildDate=datetime.fromisoformat("2023-03-23T16:08:33+01:00"),
        state="en_construction",
    )


def create_venue(*, reimbursement: bool = False, **kwargs) -> offerers_models.Venue:  # type: ignore [no-untyped-def]
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
