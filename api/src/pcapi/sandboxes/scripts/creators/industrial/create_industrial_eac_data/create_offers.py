from datetime import date
from datetime import datetime
from datetime import timedelta
from itertools import count
from itertools import cycle

from pcapi.core.educational import factories as educational_factories
from pcapi.core.educational import models as educational_models
from pcapi.core.finance import factories as finance_factories
from pcapi.core.finance import models as finance_models
from pcapi.core.offerers import models as offerers_models
from pcapi.core.providers import models as providers_models
from pcapi.models import db
from pcapi.models.offer_mixin import OfferValidationStatus
from pcapi.utils.image_conversion import DO_NOT_CROP

from .create_collective_api_provider import create_collective_api_provider


def create_offers(
    offerers: list[offerers_models.Offerer], institutions: list[educational_models.EducationalInstitution]
) -> None:
    reset_offer_id_seq()
    domains = create_domains()
    offerers_iterator = iter(offerers)
    national_programs = create_national_programs()

    # eac_1
    offerer = next(offerers_iterator)
    provider = create_collective_api_provider(offerer.managedVenues)
    create_offers_base_list(
        provider=provider,
        offerer=offerer,
        institutions=institutions,
        domains=domains,
        national_programs=national_programs,
    )
    create_booking_base_list(
        offerer=offerer,
        institutions=institutions,
        domains=domains,
    )
    # eac_2
    offerer = next(offerers_iterator)
    provider = create_collective_api_provider(offerer.managedVenues)
    create_offers_base_list(
        provider=provider,
        offerer=offerer,
        institutions=institutions,
        domains=domains,
        national_programs=national_programs,
    )
    create_booking_base_list(
        offerer=offerer,
        institutions=institutions,
        domains=domains,
    )

    # eac_pending_bank_informations
    offerer = next(offerers_iterator)
    provider = create_collective_api_provider(offerer.managedVenues)
    create_offers_base_list(
        provider=provider,
        offerer=offerer,
        institutions=institutions,
        domains=domains,
        national_programs=national_programs,
    )
    create_booking_base_list(
        offerer=offerer,
        institutions=institutions,
        domains=domains,
        reimbursed_booking=False,
    )

    # eac_no_cb
    offerer = next(offerers_iterator)
    provider = create_collective_api_provider(offerer.managedVenues)
    create_offers_base_list(
        provider=provider,
        offerer=offerer,
        institutions=institutions,
        domains=domains,
        national_programs=national_programs,
    )
    create_booking_base_list(
        offerer=offerer,
        institutions=institutions,
        domains=domains,
        reimbursed_booking=False,
    )


def create_offers_base_list(
    provider: providers_models.Provider,
    offerer: offerers_models.Offerer,
    institutions: list[educational_models.EducationalInstitution],
    domains: list[educational_models.EducationalDomain],
    national_programs: list[educational_models.NationalProgram],
    basic_offers: bool = True,
    basic_templates: bool = True,
    from_templates_offers: bool = True,
    offer_to_teacher: bool = True,
    image_offers: bool = True,
    image_template: bool = True,
    public_api_offers: bool = True,
    expired_offers: bool = True,
    pending_offers: bool = True,
    offers_intervention_56: bool = True,
    offers_intervention_91: bool = True,
    offers_next_year: bool = True,
    offers_with_request: bool = True,
) -> tuple[list[educational_models.CollectiveOffer], list[educational_models.CollectiveOfferTemplate]]:
    domains_iterator = cycle(domains)
    venue_iterator = cycle(offerer.managedVenues)
    image_iterator = cycle(["collective_offer_1.png", "collective_offer_2.jpg"])
    institution_iterator = cycle(institutions)
    national_program_iterator = cycle(national_programs)
    number_iterator = count()
    offers = []
    templates = []
    if basic_offers:
        for _i in range(5):
            stock = educational_factories.CollectiveStockFactory(
                offer__name=f"offer {next(number_iterator)} pour {offerer.name}",
                offer__educational_domains=[next(domains_iterator)],
                offer__venue=next(venue_iterator),
                offer__nationalProgram=next(national_program_iterator),
                offer__bookingEmails=["toto@totoland.com"],
                beginningDatetime=datetime.utcnow() + timedelta(days=60),
            )
            offers.append(stock.offer)
    if image_offers:
        for _i in range(5):
            stock = educational_factories.CollectiveStockFactory(
                offer__name=f"offer {next(number_iterator)} pour {offerer.name} with image",
                offer__educational_domains=[next(domains_iterator)],
                offer__venue=next(venue_iterator),
                offer__bookingEmails=["toto@totoland.com"],
                beginningDatetime=datetime.utcnow() + timedelta(days=60),
            )
            add_image_to_offer(stock.offer, next(image_iterator))
            offers.append(stock.offer)

    if offer_to_teacher:
        institution = educational_models.EducationalInstitution.query.filter(
            educational_models.EducationalInstitution.institutionId == "0560071Y"
        ).one()

        redactor = educational_models.EducationalRedactor.query.filter(
            educational_models.EducationalRedactor.email == "Marianne.Calvayrac@ac-versailles.fr"
        ).one_or_none()
        if not redactor:
            redactor = educational_factories.EducationalRedactorFactory(
                email="Marianne.Calvayrac@ac-versailles.fr",
                firstName="CALVAYRAC",
                lastName="MARIANNE",
                civility="Mme",
            )
        for _i in range(5):
            stock = educational_factories.CollectiveStockFactory(
                offer__name=f"offer {next(number_iterator)} pour {offerer.name} to teacher",
                offer__educational_domains=[next(domains_iterator)],
                offer__venue=next(venue_iterator),
                offer__institution=institution,
                offer__teacher=redactor,
                offer__bookingEmails=["toto@totoland.com"],
                beginningDatetime=datetime.utcnow() + timedelta(days=60),
            )
            offers.append(stock.offer)
    if public_api_offers:
        for _i in range(5):
            stock = educational_factories.CollectiveStockFactory(
                offer__name=f"offer {next(number_iterator)} pour {offerer.name} public api",
                offer__educational_domains=[next(domains_iterator)],
                offer__venue=next(venue_iterator),
                offer__institution=next(institution_iterator),
                offer__nationalProgram=next(national_program_iterator),
                offer__interventionArea=[],
                offer__provider=provider,
                offer__bookingEmails=["toto@totoland.com"],
                beginningDatetime=datetime.utcnow() + timedelta(days=60),
            )
            offers.append(stock.offer)
    if expired_offers:
        for _i in range(5):
            stock = educational_factories.CollectiveStockFactory(
                offer__name=f"offer {next(number_iterator)} pour {offerer.name} expired",
                offer__educational_domains=[next(domains_iterator)],
                offer__venue=next(venue_iterator),
                offer__bookingEmails=["toto@totoland.com"],
                bookingLimitDatetime=datetime.utcnow() - timedelta(days=2),
                beginningDatetime=datetime.utcnow(),
            )
            offers.append(stock.offer)
    if pending_offers:
        for _i in range(5):
            educational_factories.CollectiveStockFactory(
                offer__name=f"offer {next(number_iterator)} pour {offerer.name} pending",
                offer__educational_domains=[next(domains_iterator)],
                offer__venue=next(venue_iterator),
                offer__validation=OfferValidationStatus.PENDING,
                offer__bookingEmails=["toto@totoland.com"],
                beginningDatetime=datetime.utcnow() + timedelta(days=60),
            )
            offers.append(stock.offer)
    if offers_next_year:
        current_year = datetime.utcnow().year
        target_year = current_year + 2 if datetime.utcnow().month >= 9 else current_year + 1
        for _i in range(5):
            stock = educational_factories.CollectiveStockFactory(
                offer__name=f"offer next year {next(number_iterator)} pour {offerer.name}",
                offer__educational_domains=[next(domains_iterator)],
                offer__venue=next(venue_iterator),
                offer__bookingEmails=["toto@totoland.com"],
                beginningDatetime=datetime(target_year, 3, 18),
                bookingLimitDatetime=datetime(target_year, 3, 3),
            )
            offers.append(stock.offer)

    if offers_intervention_56:
        for _ in range(5):
            stock = educational_factories.CollectiveStockFactory(
                offer__name=f"offer {next(number_iterator)} pour {offerer.name} interventionArea 56",
                offer__educational_domains=[next(domains_iterator)],
                offer__venue=next(venue_iterator),
                offer__interventionArea=["56"],
                offer__bookingEmails=["toto@totoland.com"],
                beginningDatetime=datetime.utcnow() + timedelta(days=60),
            )
            offers.append(stock.offer)
    if offers_intervention_91:
        for _i in range(5):
            stock = educational_factories.CollectiveStockFactory(
                offer__name=f"offer {next(number_iterator)} pour {offerer.name} interventionArea 91",
                offer__educational_domains=[next(domains_iterator)],
                offer__venue=next(venue_iterator),
                offer__interventionArea=["91"],
                offer__bookingEmails=["toto@totoland.com"],
                beginningDatetime=datetime.utcnow() + timedelta(days=60),
            )
            offers.append(stock.offer)
    if basic_templates:
        for _i in range(5):
            template = educational_factories.CollectiveOfferTemplateFactory(
                name=f"offer {next(number_iterator)} pour {offerer.name} basic template",
                educational_domains=[next(domains_iterator)],
                venue=next(venue_iterator),
                bookingEmails=["toto@totoland.com"],
                nationalProgram=next(national_program_iterator),
            )
            templates.append(template)
        if from_templates_offers:
            for template in 4 * [templates[0]] + 1 * [templates[1]]:
                educational_factories.CollectiveStockFactory(
                    offer__name=f"offer {next(number_iterator)} pour {offerer.name} from template to school",
                    offer__educational_domains=[next(domains_iterator)],
                    offer__venue=next(venue_iterator),
                    offer__template=template,
                    offer__institution=next(institution_iterator),
                    offer__nationalProgram=next(national_program_iterator),
                    offer__bookingEmails=["toto@totoland.com"],
                )
    if image_template:
        for _ in range(5):
            template = educational_factories.CollectiveOfferTemplateFactory(
                name=f"offer {next(number_iterator)} pour {offerer.name} template image",
                educational_domains=[next(domains_iterator)],
                venue=next(venue_iterator),
                bookingEmails=["toto@totoland.com"],
            )
            add_image_to_offer(template, next(image_iterator))
            templates.append(template)
    if offers_with_request:
        for i in range(5):
            number = next(number_iterator)
            template = educational_factories.CollectiveOfferTemplateFactory(
                name=f"offer {number} pour {offerer.name} template request",
                educational_domains=[next(domains_iterator)],
                venue=next(venue_iterator),
                bookingEmails=["toto@totoland.com"],
            )
            educational_factories.CollectiveOfferRequestFactory(
                collectiveOfferTemplate=template,
                educationalInstitution=next(institution_iterator),
                educationalRedactor__lastName=f"last name {number} {offerer.name}",
                educationalRedactor__firstName=f"first name {number} {offerer.name}",
                totalStudents=12 if i == 0 else None,
                totalTeachers=2 if i == 0 else None,
                phoneNumber="0199000000" if i == 0 else None,
                requestedDate=date.today() if i == 0 else None,
            )
            templates.append(template)
    return offers, templates


def add_image_to_offer(offer: educational_models.HasImageMixin, image_name: str) -> None:
    with open(
        f"./src/pcapi/sandboxes/thumbs/collectif/{image_name}",
        mode="rb",
    ) as file:
        offer.set_image(image=file.read(), credit="CC-BY-SA WIKIPEDIA", crop_params=DO_NOT_CROP)


def create_booking_base_list(
    offerer: offerers_models.Offerer,
    institutions: list[educational_models.EducationalInstitution],
    domains: list[educational_models.EducationalDomain],
    pending_booking: bool = True,
    booked_booking: bool = True,
    confirmed_booking: bool = True,
    used_booking: bool = True,
    reimbursed_booking: bool = True,
    cancelled_ac: bool = True,
    cancelled_institution: bool = True,
    cancelled_expired: bool = True,
) -> None:
    current_ansco = educational_models.EducationalYear.query.filter(
        educational_models.EducationalYear.beginningDate <= datetime.utcnow(),
        educational_models.EducationalYear.expirationDate >= datetime.utcnow(),
    ).one()
    institution_iterator = cycle(institutions)
    number_iterator = count()
    domains_iterator = cycle(domains)
    venue_iterator = cycle(offerer.managedVenues)
    if pending_booking:
        for _i in range(5):
            educational_factories.CollectiveBookingFactory(
                stock__offer__name=f"PENDING offer {next(number_iterator)} pour {offerer.name}",
                stock__offer__venue=next(venue_iterator),
                stock__offer__educational_domains=[next(domains_iterator)],
                stock__bookingLimitDatetime=datetime.utcnow() + timedelta(15),
                stock__beginningDatetime=datetime.utcnow() + timedelta(days=20),
                educationalYear=current_ansco,
                educationalInstitution=next(institution_iterator),
                status=educational_models.CollectiveBookingStatus.PENDING,
                confirmationDate=None,
                cancellationLimitDate=datetime.utcnow() + timedelta(days=17),
                confirmationLimitDate=datetime.utcnow() + timedelta(days=15),
                dateCreated=datetime.utcnow() - timedelta(days=30),
            )

    if booked_booking:
        for _i in range(5):
            educational_factories.CollectiveBookingFactory(
                stock__offer__name=f"BOOKED offer {next(number_iterator)} pour {offerer.name}",
                stock__offer__venue=next(venue_iterator),
                stock__offer__educational_domains=[next(domains_iterator)],
                stock__beginningDatetime=datetime.utcnow() + timedelta(days=20),
                stock__bookingLimitDatetime=datetime.utcnow() + timedelta(days=15),
                educationalYear=current_ansco,
                educationalInstitution=next(institution_iterator),
                status=educational_models.CollectiveBookingStatus.CONFIRMED,
                confirmationDate=datetime.utcnow() - timedelta(days=1),
                cancellationLimitDate=datetime.utcnow() + timedelta(days=17),
                confirmationLimitDate=datetime.utcnow() + timedelta(days=15),
                dateCreated=datetime.utcnow() - timedelta(days=30),
            )
    if confirmed_booking:
        for _i in range(5):
            educational_factories.CollectiveBookingFactory(
                stock__offer__name=f"CONFIRMED offer {next(number_iterator)} pour {offerer.name}",
                stock__offer__venue=next(venue_iterator),
                stock__offer__educational_domains=[next(domains_iterator)],
                stock__beginningDatetime=datetime.utcnow() + timedelta(days=20),
                stock__bookingLimitDatetime=datetime.utcnow() - timedelta(days=5),
                educationalYear=current_ansco,
                educationalInstitution=next(institution_iterator),
                status=educational_models.CollectiveBookingStatus.CONFIRMED,
                confirmationDate=datetime.utcnow() - timedelta(days=3),
                cancellationLimitDate=datetime.utcnow(),
                confirmationLimitDate=datetime.utcnow() - timedelta(days=2),
                dateCreated=datetime.utcnow() - timedelta(days=30),
            )
    if used_booking:
        for _i in range(5):
            booking = educational_factories.CollectiveBookingFactory(
                stock__offer__name=f"USED offer {next(number_iterator)} pour {offerer.name}",
                stock__offer__venue=next(venue_iterator),
                stock__offer__educational_domains=[next(domains_iterator)],
                stock__beginningDatetime=datetime.utcnow(),
                stock__bookingLimitDatetime=datetime.utcnow() - timedelta(days=15),
                educationalYear=current_ansco,
                educationalInstitution=next(institution_iterator),
                status=educational_models.CollectiveBookingStatus.USED,
                dateUsed=datetime.utcnow(),
                confirmationDate=datetime.utcnow() - timedelta(days=5),
                cancellationLimitDate=datetime.utcnow() - timedelta(days=2),
                confirmationLimitDate=datetime.utcnow() - timedelta(days=3),
                dateCreated=datetime.utcnow() - timedelta(days=30),
            )
            finance_factories.UsedBookingFinanceEventFactory(collectiveBooking=booking)
    if reimbursed_booking:
        for _i in range(5):
            educational_factories.CollectiveBookingFactory(
                stock__offer__name=f"REIMBURSED offer {next(number_iterator)} pour {offerer.name}",
                stock__offer__venue=next(venue_iterator),
                stock__offer__educational_domains=[next(domains_iterator)],
                stock__beginningDatetime=datetime.utcnow() - timedelta(days=15),
                stock__bookingLimitDatetime=datetime.utcnow() - timedelta(days=18),
                educationalYear=current_ansco,
                educationalInstitution=next(institution_iterator),
                status=educational_models.CollectiveBookingStatus.REIMBURSED,
                dateCreated=datetime.utcnow() - timedelta(days=20),
                dateUsed=datetime.utcnow() - timedelta(days=15),
                confirmationDate=datetime.utcnow() - timedelta(days=18),
                cancellationLimitDate=datetime.utcnow() - timedelta(days=16),
                confirmationLimitDate=datetime.utcnow() - timedelta(days=18),
                reimbursementDate=datetime.utcnow() - timedelta(days=12),
                pricings=[finance_factories.CollectivePricingFactory(status=finance_models.PricingStatus.INVOICED)],
            )
    if cancelled_ac:
        for _i in range(5):
            educational_factories.CollectiveBookingFactory(
                stock__offer__name=f"CANCELLED BY AC offer {next(number_iterator)} pour {offerer.name}",
                stock__offer__venue=next(venue_iterator),
                stock__offer__educational_domains=[next(domains_iterator)],
                stock__beginningDatetime=datetime.utcnow() + timedelta(days=20),
                stock__bookingLimitDatetime=datetime.utcnow() + timedelta(days=15),
                educationalYear=current_ansco,
                educationalInstitution=next(institution_iterator),
                status=educational_models.CollectiveBookingStatus.CANCELLED,
                cancellationReason=educational_models.CollectiveBookingCancellationReasons.OFFERER,
                cancellationDate=datetime.utcnow() - timedelta(days=1),
                dateCreated=datetime.utcnow() - timedelta(days=20),
                confirmationDate=datetime.utcnow() - timedelta(days=12),
                cancellationLimitDate=datetime.utcnow() + timedelta(days=17),
                confirmationLimitDate=datetime.utcnow() + timedelta(days=15),
            )
    if cancelled_institution:
        for _i in range(5):
            educational_factories.CollectiveBookingFactory(
                stock__offer__name=f"CANCELLED BY EPLE offer {next(number_iterator)} pour {offerer.name}",
                stock__offer__venue=next(venue_iterator),
                stock__offer__educational_domains=[next(domains_iterator)],
                stock__beginningDatetime=datetime.utcnow() + timedelta(days=20),
                stock__bookingLimitDatetime=datetime.utcnow() + timedelta(days=15),
                educationalYear=current_ansco,
                educationalInstitution=next(institution_iterator),
                status=educational_models.CollectiveBookingStatus.CANCELLED,
                cancellationReason=educational_models.CollectiveBookingCancellationReasons.REFUSED_BY_INSTITUTE,
                cancellationDate=datetime.utcnow() - timedelta(days=1),
                dateCreated=datetime.utcnow() - timedelta(days=20),
                confirmationDate=datetime.utcnow() - timedelta(days=12),
                cancellationLimitDate=datetime.utcnow() + timedelta(days=17),
                confirmationLimitDate=datetime.utcnow() + timedelta(days=15),
            )

    if cancelled_expired:
        for _i in range(5):
            educational_factories.CollectiveBookingFactory(
                stock__offer__name=f"CANCELLED AUTOMATICALLY offer {next(number_iterator)} pour {offerer.name}",
                stock__offer__venue=next(venue_iterator),
                stock__offer__educational_domains=[next(domains_iterator)],
                stock__beginningDatetime=datetime.utcnow() + timedelta(days=20),
                stock__bookingLimitDatetime=datetime.utcnow() - timedelta(days=15),
                educationalYear=current_ansco,
                educationalInstitution=next(institution_iterator),
                status=educational_models.CollectiveBookingStatus.CANCELLED,
                cancellationReason=educational_models.CollectiveBookingCancellationReasons.EXPIRED,
                cancellationDate=datetime.utcnow() - timedelta(days=5),
                dateCreated=datetime.utcnow() - timedelta(days=20),
                confirmationDate=None,
                cancellationLimitDate=datetime.utcnow() - timedelta(days=3),
                confirmationLimitDate=datetime.utcnow() - timedelta(days=5),
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


def create_national_programs() -> list[educational_models.NationalProgram]:
    return [
        educational_factories.NationalProgramFactory(name="collège au cinéma", id=1),
        educational_factories.NationalProgramFactory(name="Le Prix des Incorruptibles", id=2),
        educational_factories.NationalProgramFactory(name="Lycéens et apprentis au cinéma", id=3),
        educational_factories.NationalProgramFactory(name="L’Olympiade culturelle", id=4),
        educational_factories.NationalProgramFactory(name="Théâtre au collège", id=5),
    ]


def reset_offer_id_seq() -> None:
    db.session.execute("ALTER SEQUENCE collective_offer_id_seq RESTART WITH 1")
    db.session.execute("ALTER SEQUENCE collective_offer_template_id_seq RESTART WITH 1")
