from itertools import chain
from itertools import cycle

from pcapi.core.finance import factories as finance_factories
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
        name=f"reimbursementPoint {offerer.name}",
        reimbursement=True,
        adageId="123546",
        venueEducationalStatusId=next(educational_status_iterator),
        collectiveInterventionArea=ALL_INTERVENTION_AREA,
    )
    # eac_2
    offerer = next(offerer_iterator)
    create_venue(
        managingOfferer=offerer,
        name=f"reimbursementPoint {offerer.name}",
        reimbursement=True,
        siret="12345678200010",
        venueEducationalStatusId=next(educational_status_iterator),
        collectiveInterventionArea=ALL_INTERVENTION_AREA,
    )
    create_venue(
        managingOfferer=offerer,
        name=f"real_venue 1 {offerer.name}",
        siret="12345678200036",
        venueEducationalStatusId=next(educational_status_iterator),
        collectiveInterventionArea=ALL_INTERVENTION_AREA,
    )
    # eac_3
    offerer = next(offerer_iterator)
    create_venue(
        managingOfferer=offerer,
        name=f"reimbursementPoint {offerer.name}",
        reimbursement=True,
        adageId="789456",
        venueEducationalStatusId=next(educational_status_iterator),
        collectiveInterventionArea=ALL_INTERVENTION_AREA,
    )
    create_venue(
        managingOfferer=offerer,
        name=f"real_venue 1 {offerer.name}",
        venueEducationalStatusId=next(educational_status_iterator),
        collectiveInterventionArea=ALL_INTERVENTION_AREA,
    )
    create_venue(
        managingOfferer=offerer,
        name=f"real_venue 2 {offerer.name}",
        venueEducationalStatusId=next(educational_status_iterator),
        collectiveInterventionArea=ALL_INTERVENTION_AREA,
    )
    # eac_no_cb
    offerer = next(offerer_iterator)
    create_venue(
        managingOfferer=offerer,
        name=f"real_venue 1 {offerer.name}",
        adageId="698748",
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


def create_venue(*, reimbursement: bool = False, **kwargs) -> None:  # type: ignore [no-untyped-def]
    venue = offerers_factories.VenueFactory(**kwargs)
    if reimbursement:
        venue.bankInformation = finance_factories.BankInformationFactory()
        offerers_factories.VenueReimbursementPointLinkFactory(
            venue=venue,
            reimbursementPoint=venue,
        )


def create_venue_educational_status() -> None:
    for ident, name in VENUE_EDUCATIONAL_STATUS.items():
        offerers_factories.VenueEducationalStatusFactory(id=ident, name=name)
