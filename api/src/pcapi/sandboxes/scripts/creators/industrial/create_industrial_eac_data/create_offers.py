from datetime import datetime
from datetime import timedelta
from itertools import cycle

from pcapi.core.educational import factories as educational_factories
from pcapi.core.educational import models as educational_models
from pcapi.core.offerers import models as offerers_models


def create_offers(
    offerers: list[offerers_models.Offerer], institutions: list[educational_models.EducationalInstitution]
) -> None:
    domains_iterator = cycle(create_domains())
    offerers_iterator = iter(offerers)
    institutions_iterator = cycle(institutions)

    # eac_1
    offerer = next(offerers_iterator)
    venue_iterator = cycle(offerer.managedVenues)
    number_iterator = iter(range(20))
    educational_factories.CollectiveOfferTemplateFactory(
        name=f"offer {next(number_iterator)} pour {offerer.name}",
        educational_domains=[next(domains_iterator)],
        venue=next(venue_iterator),
    )
    educational_factories.CollectiveStockFactory(
        collectiveOffer__name=f"offer {next(number_iterator)} pour {offerer.name}",
        collectiveOffer__educational_domains=[next(domains_iterator)],
        collectiveOffer__venue=next(venue_iterator),
    )

    # eac_2
    offerer = next(offerers_iterator)
    venue_iterator = cycle(offerer.managedVenues)
    number_iterator = iter(range(20))
    educational_factories.CollectiveOfferTemplateFactory(
        name=f"offer {next(number_iterator)} pour {offerer.name}",
        educational_domains=[next(domains_iterator)],
        venue=next(venue_iterator),
    )
    educational_factories.CollectiveStockFactory(
        collectiveOffer__name=f"offer {next(number_iterator)} pour {offerer.name}",
        collectiveOffer__educational_domains=[next(domains_iterator)],
        collectiveOffer__venue=next(venue_iterator),
    )
    educational_factories.CollectiveOfferTemplateFactory(
        name=f"offer {next(number_iterator)} pour {offerer.name}",
        educational_domains=[next(domains_iterator)],
        venue=next(venue_iterator),
    )
    educational_factories.CollectiveStockFactory(
        collectiveOffer__name=f"offer {next(number_iterator)} pour {offerer.name}",
        collectiveOffer__educational_domains=[next(domains_iterator)],
        collectiveOffer__venue=next(venue_iterator),
    )
    educational_factories.CollectiveOfferTemplateFactory(
        name=f"offer {next(number_iterator)} pour {offerer.name}",
        educational_domains=[next(domains_iterator)],
        venue=next(venue_iterator),
    )
    educational_factories.CollectiveStockFactory(
        collectiveOffer__name=f"offer {next(number_iterator)} pour {offerer.name}",
        collectiveOffer__educational_domains=[next(domains_iterator)],
        collectiveOffer__venue=next(venue_iterator),
    )
    educational_factories.CollectiveOfferTemplateFactory(
        name=f"offer {next(number_iterator)} pour {offerer.name}",
        educational_domains=[next(domains_iterator)],
        venue=next(venue_iterator),
    )
    educational_factories.CollectiveStockFactory(
        collectiveOffer__name=f"offer {next(number_iterator)} pour {offerer.name}",
        collectiveOffer__educational_domains=[next(domains_iterator)],
        collectiveOffer__venue=next(venue_iterator),
    )
    educational_factories.CollectiveOfferTemplateFactory(
        name=f"offer {next(number_iterator)} pour {offerer.name}",
        educational_domains=[next(domains_iterator)],
        venue=next(venue_iterator),
    )
    educational_factories.CollectiveStockFactory(
        collectiveOffer__name=f"offer {next(number_iterator)} pour {offerer.name}",
        collectiveOffer__educational_domains=[next(domains_iterator)],
        collectiveOffer__venue=next(venue_iterator),
    )

    # eac_3
    offerer = next(offerers_iterator)
    venue_iterator = cycle(offerer.managedVenues)
    number_iterator = iter(range(20))
    educational_factories.CollectiveOfferTemplateFactory(
        name=f"offer {next(number_iterator)} pour {offerer.name}",
        educational_domains=[next(domains_iterator)],
        venue=next(venue_iterator),
    )
    educational_factories.CollectiveStockFactory(
        collectiveOffer__name=f"offer {next(number_iterator)} pour {offerer.name}",
        collectiveOffer__educational_domains=[next(domains_iterator)],
        collectiveOffer__venue=next(venue_iterator),
    )
    educational_factories.CollectiveOfferTemplateFactory(
        name=f"offer {next(number_iterator)} pour {offerer.name}",
        educational_domains=[next(domains_iterator)],
        venue=next(venue_iterator),
    )
    educational_factories.CollectiveStockFactory(
        collectiveOffer__name=f"offer {next(number_iterator)} pour {offerer.name}",
        collectiveOffer__educational_domains=[next(domains_iterator)],
        collectiveOffer__venue=next(venue_iterator),
    )
    educational_factories.CollectiveOfferTemplateFactory(
        name=f"offer {next(number_iterator)} pour {offerer.name}",
        educational_domains=[next(domains_iterator)],
        venue=next(venue_iterator),
    )
    educational_factories.CollectiveBookingFactory(
        collectiveStock__collectiveOffer__name=f"PENDING offer {next(number_iterator)} pour {offerer.name}",
        collectiveStock__collectiveOffer__venue=next(venue_iterator),
        collectiveStock__collectiveOffer__educational_domains=[next(domains_iterator)],
        collectiveStock__bookingLimitDatetime=datetime.utcnow() + timedelta(15),
        collectiveStock__beginningDatetime=datetime.utcnow() + timedelta(days=20),
        educationalInstitution=next(institutions_iterator),
        status=educational_models.CollectiveBookingStatus.PENDING,
        cancellationReason=None,
        cancellationDate=None,
        dateUsed=None,
        confirmationDate=None,
        cancellationLimitDate=datetime.utcnow() + timedelta(days=17),
        confirmationLimitDate=datetime.utcnow() + timedelta(days=15),
    )
    educational_factories.CollectiveBookingFactory(
        collectiveStock__collectiveOffer__name=f"CONFIRMED offer {next(number_iterator)} pour {offerer.name}",
        collectiveStock__collectiveOffer__venue=next(venue_iterator),
        collectiveStock__collectiveOffer__educational_domains=[next(domains_iterator)],
        collectiveStock__beginningDatetime=datetime.utcnow() + timedelta(days=20),
        collectiveStock__bookingLimitDatetime=datetime.utcnow() + timedelta(days=15),
        educationalInstitution=next(institutions_iterator),
        status=educational_models.CollectiveBookingStatus.CONFIRMED,
        cancellationReason=None,
        cancellationDate=None,
        dateUsed=None,
        confirmationDate=datetime.utcnow() - timedelta(days=1),
        cancellationLimitDate=datetime.utcnow() + timedelta(days=17),
        confirmationLimitDate=datetime.utcnow() + timedelta(days=15),
    )
    educational_factories.CollectiveBookingFactory(
        collectiveStock__collectiveOffer__name=f"USED offer {next(number_iterator)} pour {offerer.name}",
        collectiveStock__collectiveOffer__venue=next(venue_iterator),
        collectiveStock__collectiveOffer__educational_domains=[next(domains_iterator)],
        collectiveStock__beginningDatetime=datetime.utcnow() - timedelta(days=1),
        collectiveStock__bookingLimitDatetime=datetime.utcnow() - timedelta(days=3),
        educationalInstitution=next(institutions_iterator),
        status=educational_models.CollectiveBookingStatus.USED,
        cancellationReason=None,
        cancellationDate=None,
        dateUsed=datetime.utcnow() - timedelta(days=1),
        confirmationDate=datetime.utcnow() - timedelta(days=1),
        cancellationLimitDate=datetime.utcnow() + timedelta(days=2),
        confirmationLimitDate=datetime.utcnow() + timedelta(days=3),
    )
    educational_factories.CollectiveBookingFactory(
        collectiveStock__collectiveOffer__name=f"CANCELLED offer {next(number_iterator)} pour {offerer.name}",
        collectiveStock__collectiveOffer__venue=next(venue_iterator),
        collectiveStock__collectiveOffer__educational_domains=[next(domains_iterator)],
        collectiveStock__beginningDatetime=datetime.utcnow() + timedelta(days=20),
        collectiveStock__bookingLimitDatetime=datetime.utcnow() + timedelta(days=15),
        educationalInstitution=next(institutions_iterator),
        status=educational_models.CollectiveBookingStatus.CANCELLED,
        cancellationReason=educational_models.CollectiveBookingCancellationReasons.BENEFICIARY,
        cancellationDate=datetime.utcnow() - timedelta(days=1),
        dateCreated=datetime.utcnow() - timedelta(days=15),
        dateUsed=None,
        confirmationDate=datetime.utcnow() - timedelta(days=12),
        cancellationLimitDate=datetime.utcnow() + timedelta(days=17),
        confirmationLimitDate=datetime.utcnow() + timedelta(days=15),
    )
    educational_factories.CollectiveBookingFactory(
        collectiveStock__collectiveOffer__name=f"REIMBURSED offer {next(number_iterator)} pour {offerer.name}",
        collectiveStock__collectiveOffer__venue=next(venue_iterator),
        collectiveStock__collectiveOffer__educational_domains=[next(domains_iterator)],
        collectiveStock__beginningDatetime=datetime.utcnow() - timedelta(days=15),
        collectiveStock__bookingLimitDatetime=datetime.utcnow() - timedelta(days=18),
        educationalInstitution=next(institutions_iterator),
        status=educational_models.CollectiveBookingStatus.REIMBURSED,
        cancellationReason=None,
        cancellationDate=None,
        dateCreated=datetime.utcnow() - timedelta(20),
        dateUsed=datetime.utcnow() - timedelta(days=15),
        confirmationDate=datetime.utcnow() - timedelta(days=18),
        cancellationLimitDate=datetime.utcnow() - timedelta(days=16),
        confirmationLimitDate=datetime.utcnow() - timedelta(days=18),
        reimbursementDate=datetime.utcnow() - timedelta(days=12),
    )

    # eac_no_cb
    offerer = next(offerers_iterator)
    venue_iterator = cycle(offerer.managedVenues)
    number_iterator = iter(range(20))
    educational_factories.CollectiveOfferTemplateFactory(
        name=f"offer {next(number_iterator)} pour {offerer.name}",
        educational_domains=[next(domains_iterator)],
        venue=next(venue_iterator),
    )
    educational_factories.CollectiveStockFactory(
        collectiveOffer__name=f"offer {next(number_iterator)} pour {offerer.name}",
        collectiveOffer__educational_domains=[next(domains_iterator)],
        collectiveOffer__venue=next(venue_iterator),
    )
    educational_factories.CollectiveOfferTemplateFactory(
        name=f"offer {next(number_iterator)} pour {offerer.name}",
        educational_domains=[next(domains_iterator)],
        venue=next(venue_iterator),
    )
    educational_factories.CollectiveStockFactory(
        collectiveOffer__name=f"offer {next(number_iterator)} pour {offerer.name}",
        collectiveOffer__educational_domains=[next(domains_iterator)],
        collectiveOffer__venue=next(venue_iterator),
    )
    educational_factories.CollectiveOfferTemplateFactory(
        name=f"offer {next(number_iterator)} pour {offerer.name}",
        educational_domains=[next(domains_iterator)],
        venue=next(venue_iterator),
    )
    educational_factories.CollectiveStockFactory(
        collectiveOffer__name=f"offer {next(number_iterator)} pour {offerer.name}",
        collectiveOffer__educational_domains=[next(domains_iterator)],
        collectiveOffer__venue=next(venue_iterator),
    )
    educational_factories.CollectiveOfferTemplateFactory(
        name=f"offer {next(number_iterator)} pour {offerer.name}",
        educational_domains=[next(domains_iterator)],
        venue=next(venue_iterator),
    )
    educational_factories.CollectiveStockFactory(
        collectiveOffer__name=f"offer {next(number_iterator)} pour {offerer.name}",
        collectiveOffer__educational_domains=[next(domains_iterator)],
        collectiveOffer__venue=next(venue_iterator),
    )
    educational_factories.CollectiveOfferTemplateFactory(
        name=f"offer {next(number_iterator)} pour {offerer.name}",
        educational_domains=[next(domains_iterator)],
        venue=next(venue_iterator),
    )
    educational_factories.CollectiveStockFactory(
        collectiveOffer__name=f"offer {next(number_iterator)} pour {offerer.name}",
        collectiveOffer__educational_domains=[next(domains_iterator)],
        collectiveOffer__venue=next(venue_iterator),
    )

    # eac_rejected
    offerer = next(offerers_iterator)
    venue_iterator = cycle(offerer.managedVenues)
    number_iterator = iter(range(20))
    educational_factories.CollectiveOfferTemplateFactory(
        name=f"offer {next(number_iterator)} pour {offerer.name}",
        educational_domains=[next(domains_iterator)],
        venue=next(venue_iterator),
    )
    educational_factories.CollectiveStockFactory(
        collectiveOffer__name=f"offer {next(number_iterator)} pour {offerer.name}",
        collectiveOffer__educational_domains=[next(domains_iterator)],
        collectiveOffer__venue=next(venue_iterator),
    )


def create_domains() -> list[educational_models.EducationalDomain]:
    return [
        educational_factories.EducationalDomainFactory(name="Architecture", id=1),
        educational_factories.EducationalDomainFactory(name="Arts du cirque et arts de la rue", id=2),
        educational_factories.EducationalDomainFactory(name="Gastronomie et arts du goût", id=3),
        educational_factories.EducationalDomainFactory(name="Arts numériques", id=4),
        educational_factories.EducationalDomainFactory(name="Arts visuels, arts plastiques, arts appliqués", id=5),
        educational_factories.EducationalDomainFactory(name="Cinéma, audiovisuel", id=6),
        educational_factories.EducationalDomainFactory(name="Culture scientifique, technique et industrielle", id=7),
        educational_factories.EducationalDomainFactory(name="Danse", id=8),
        educational_factories.EducationalDomainFactory(name="Design", id=9),
        educational_factories.EducationalDomainFactory(name="Développement durable", id=10),
        educational_factories.EducationalDomainFactory(name="Univers du livre, de la lecture et des écritures", id=11),
        educational_factories.EducationalDomainFactory(name="Musique", id=12),
        educational_factories.EducationalDomainFactory(name="Patrimoine, mémoire, archéologie", id=13),
        educational_factories.EducationalDomainFactory(name="Photographie", id=14),
        educational_factories.EducationalDomainFactory(name="Théâtre, expression dramatique, marionnettes", id=15),
        educational_factories.EducationalDomainFactory(name="Bande dessinée", id=16),
        educational_factories.EducationalDomainFactory(name="Média et information", id=17),
    ]
