from datetime import date
from datetime import datetime
from datetime import timedelta
from itertools import count
from itertools import cycle
import typing

from pcapi import settings
from pcapi.core import search
from pcapi.core.categories.subcategories_v2 import EacFormat
from pcapi.core.educational import factories as educational_factories
from pcapi.core.educational import models as educational_models
from pcapi.core.finance import factories as finance_factories
from pcapi.core.finance import models as finance_models
from pcapi.core.offerers import models as offerers_models
from pcapi.core.providers import models as providers_models
from pcapi.core.users import factories as user_factory
from pcapi.models import db
from pcapi.models.offer_mixin import OfferValidationStatus
from pcapi.utils import db as db_utils
from pcapi.utils.image_conversion import DO_NOT_CROP

from .create_collective_api_provider import create_collective_api_provider


def create_offers(
    offerers: list[offerers_models.Offerer], institutions: list[educational_models.EducationalInstitution]
) -> None:
    reset_offer_id_seq()
    national_programs = create_national_programs()
    domains = create_domains(national_programs)
    offerers_iterator = iter(offerers)

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

    # eac_with_displayed_status_cases
    offerer = next(o for o in offerers if o.name == "eac_with_displayed_status_cases")
    create_offers_booking_with_different_displayed_status(offerer=offerer, institutions=institutions, domains=domains)
    create_offer_templates_with_different_displayed_status(offerer=offerer, domains=domains)

    search.index_all_collective_offers_and_templates()


def create_offers_base_list(
    *,
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
    size = 5 if not settings.CREATE_ADAGE_TESTING_DATA else len(institutions)
    number_iterator = count()
    offers = []
    templates = []
    if basic_offers:
        for _ in range(size):
            stock = educational_factories.CollectiveStockFactory(
                collectiveOffer__name=f"offer {next(number_iterator)} pour {offerer.name}",
                collectiveOffer__educational_domains=[next(domains_iterator)],
                collectiveOffer__venue=next(venue_iterator),
                collectiveOffer__institution=next(institution_iterator),
                collectiveOffer__nationalProgram=next(national_program_iterator),
                collectiveOffer__bookingEmails=["toto@totoland.com"],
                collectiveOffer__author=user_factory.ProFactory(email="eac_1_lieu@example.com"),
                collectiveOffer__formats=[EacFormat.PROJECTION_AUDIOVISUELLE],
                beginningDatetime=datetime.utcnow() + timedelta(days=60),
            )
            offers.append(stock.collectiveOffer)

        if settings.CREATE_ADAGE_TESTING_DATA:
            # add an offer with and emoji so that ADAGE can check that the encoding works
            institution = educational_models.EducationalInstitution.query.filter(
                educational_models.EducationalInstitution.institutionId == "0131251P"
            ).one()

            stock = educational_factories.CollectiveStockFactory(
                collectiveOffer__name=f"offer {next(number_iterator)} pour {offerer.name} 🍕",
                collectiveOffer__educational_domains=[next(domains_iterator)],
                collectiveOffer__venue=next(venue_iterator),
                collectiveOffer__institution=institution,
                collectiveOffer__nationalProgram=next(national_program_iterator),
                collectiveOffer__bookingEmails=["toto@totoland.com"],
                collectiveOffer__author=user_factory.ProFactory(email="eac_1_lieu@example.com"),
                collectiveOffer__formats=[EacFormat.PROJECTION_AUDIOVISUELLE],
                beginningDatetime=datetime.utcnow() + timedelta(days=60),
            )
            offers.append(stock.collectiveOffer)

    if image_offers:
        for _ in range(size):
            stock = educational_factories.CollectiveStockFactory(
                collectiveOffer__name=f"offer {next(number_iterator)} pour {offerer.name} with image",
                collectiveOffer__educational_domains=[next(domains_iterator)],
                collectiveOffer__venue=next(venue_iterator),
                collectiveOffer__institution=next(institution_iterator),
                collectiveOffer__bookingEmails=["toto@totoland.com"],
                beginningDatetime=datetime.utcnow() + timedelta(days=60),
            )
            add_image_to_offer(stock.collectiveOffer, next(image_iterator))
            offers.append(stock.collectiveOffer)

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
        for _ in range(size):
            stock = educational_factories.CollectiveStockFactory(
                collectiveOffer__name=f"offer {next(number_iterator)} pour {offerer.name} to teacher",
                collectiveOffer__educational_domains=[next(domains_iterator)],
                collectiveOffer__venue=next(venue_iterator),
                collectiveOffer__institution=institution,
                collectiveOffer__teacher=redactor,
                collectiveOffer__bookingEmails=["toto@totoland.com"],
                beginningDatetime=datetime.utcnow() + timedelta(days=60),
            )
            offers.append(stock.collectiveOffer)

    if public_api_offers:
        for _ in range(size):
            stock = educational_factories.CollectiveStockFactory(
                collectiveOffer__name=f"offer {next(number_iterator)} pour {offerer.name} public api",
                collectiveOffer__educational_domains=[next(domains_iterator)],
                collectiveOffer__venue=next(venue_iterator),
                collectiveOffer__institution=next(institution_iterator),
                collectiveOffer__nationalProgram=next(national_program_iterator),
                collectiveOffer__interventionArea=[],
                collectiveOffer__provider=provider,
                collectiveOffer__bookingEmails=["toto@totoland.com"],
                beginningDatetime=datetime.utcnow() + timedelta(days=60),
            )
            offers.append(stock.collectiveOffer)

    if expired_offers:
        for _ in range(size):
            stock = educational_factories.CollectiveStockFactory(
                collectiveOffer__name=f"offer {next(number_iterator)} pour {offerer.name} expired",
                collectiveOffer__educational_domains=[next(domains_iterator)],
                collectiveOffer__venue=next(venue_iterator),
                collectiveOffer__institution=next(institution_iterator),
                collectiveOffer__bookingEmails=["toto@totoland.com"],
                bookingLimitDatetime=datetime.utcnow() - timedelta(days=2),
                beginningDatetime=datetime.utcnow(),
            )
            offers.append(stock.collectiveOffer)

    if pending_offers:
        for _ in range(size):
            educational_factories.CollectiveStockFactory(
                collectiveOffer__name=f"offer {next(number_iterator)} pour {offerer.name} pending",
                collectiveOffer__educational_domains=[next(domains_iterator)],
                collectiveOffer__venue=next(venue_iterator),
                collectiveOffer__institution=next(institution_iterator),
                collectiveOffer__validation=OfferValidationStatus.PENDING,
                collectiveOffer__bookingEmails=["toto@totoland.com"],
                beginningDatetime=datetime.utcnow() + timedelta(days=60),
            )
            offers.append(stock.collectiveOffer)

    if offers_next_year:
        current_year = datetime.utcnow().year
        target_year = current_year + 2 if datetime.utcnow().month >= 9 else current_year + 1
        for _ in range(size):
            stock = educational_factories.CollectiveStockFactory(
                collectiveOffer__name=f"offer next year {next(number_iterator)} pour {offerer.name}",
                collectiveOffer__educational_domains=[next(domains_iterator)],
                collectiveOffer__venue=next(venue_iterator),
                collectiveOffer__institution=next(institution_iterator),
                collectiveOffer__bookingEmails=["toto@totoland.com"],
                beginningDatetime=datetime(target_year, 3, 18),
                bookingLimitDatetime=datetime(target_year, 3, 3),
            )
            offers.append(stock.collectiveOffer)

    if offers_intervention_56:
        for _ in range(size):
            stock = educational_factories.CollectiveStockFactory(
                collectiveOffer__name=f"offer {next(number_iterator)} pour {offerer.name} interventionArea 56",
                collectiveOffer__educational_domains=[next(domains_iterator)],
                collectiveOffer__venue=next(venue_iterator),
                collectiveOffer__institution=next(institution_iterator),
                collectiveOffer__interventionArea=["56"],
                collectiveOffer__bookingEmails=["toto@totoland.com"],
                beginningDatetime=datetime.utcnow() + timedelta(days=60),
            )
            offers.append(stock.collectiveOffer)

    if offers_intervention_91:
        for _ in range(size):
            stock = educational_factories.CollectiveStockFactory(
                collectiveOffer__name=f"offer {next(number_iterator)} pour {offerer.name} interventionArea 91",
                collectiveOffer__educational_domains=[next(domains_iterator)],
                collectiveOffer__venue=next(venue_iterator),
                collectiveOffer__institution=next(institution_iterator),
                collectiveOffer__interventionArea=["91"],
                collectiveOffer__bookingEmails=["toto@totoland.com"],
                beginningDatetime=datetime.utcnow() + timedelta(days=60),
            )
            offers.append(stock.collectiveOffer)

    if basic_templates:
        for _ in range(5):
            template = educational_factories.CollectiveOfferTemplateFactory(
                name=f"offer {next(number_iterator)} pour {offerer.name} basic template",
                educational_domains=[next(domains_iterator)],
                venue=next(venue_iterator),
                bookingEmails=["toto@totoland.com"],
                nationalProgram=next(national_program_iterator),
                author=user_factory.ProFactory(email="eac_1_lieu@example.com"),
                formats=[EacFormat.PROJECTION_AUDIOVISUELLE],
            )
            templates.append(template)

        if from_templates_offers:
            for template in 4 * [templates[0]] + 1 * [templates[1]]:
                educational_factories.CollectiveStockFactory(
                    collectiveOffer__name=f"offer {next(number_iterator)} pour {offerer.name} from template to school",
                    collectiveOffer__educational_domains=[next(domains_iterator)],
                    collectiveOffer__venue=next(venue_iterator),
                    collectiveOffer__template=template,
                    collectiveOffer__institution=next(institution_iterator),
                    collectiveOffer__nationalProgram=next(national_program_iterator),
                    collectiveOffer__bookingEmails=["toto@totoland.com"],
                    beginningDatetime=datetime.utcnow() + timedelta(days=60),
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
        for i in range(size):
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


def create_offers_booking_with_different_displayed_status(
    *,
    offerer: offerers_models.Offerer,
    institutions: list[educational_models.EducationalInstitution],
    domains: list[educational_models.EducationalDomain],
) -> None:
    current_ansco = educational_models.EducationalYear.query.filter(
        educational_models.EducationalYear.beginningDate <= datetime.utcnow(),
        educational_models.EducationalYear.expirationDate >= datetime.utcnow(),
    ).one()
    domains_iterator = cycle(domains)
    venue_iterator = cycle(offerer.managedVenues)
    institution_iterator = cycle(institutions)

    today = datetime.utcnow()
    in_two_weeks = today + timedelta(days=14)
    in_four_weeks = today + timedelta(days=28)

    two_weeks_ago = today - timedelta(days=14)
    four_weeks_ago = today - timedelta(days=28)

    yesterday = today - timedelta(days=1)
    tomorrow = today + timedelta(days=1)

    options: dict[str, dict[str, typing.Any]] = {
        # no bookings
        "Amsterdam": {
            "bookingLimitDatetime": in_two_weeks,
            "beginningDatetime": in_four_weeks,
            "endDatetime": in_four_weeks,
        },
        "Athènes": {
            "bookingLimitDatetime": two_weeks_ago,
            "beginningDatetime": in_two_weeks,
            "endDatetime": in_two_weeks,
        },
        "Berlin": {
            "bookingLimitDatetime": four_weeks_ago,
            "beginningDatetime": two_weeks_ago,
            "endDatetime": in_two_weeks,
        },
        "Bratislava": {
            "bookingLimitDatetime": four_weeks_ago,
            "beginningDatetime": four_weeks_ago,
            "endDatetime": four_weeks_ago,
        },
        # with a pending booking
        "Bruxelles": {
            "bookingLimitDatetime": in_two_weeks,
            "beginningDatetime": in_four_weeks,
            "endDatetime": in_four_weeks,
            "bookingFactory": educational_factories.PendingCollectiveBookingFactory,
        },
        "Bucarest": {
            "bookingLimitDatetime": two_weeks_ago,
            "beginningDatetime": in_two_weeks,
            "endDatetime": in_two_weeks,
            "bookingFactory": educational_factories.PendingCollectiveBookingFactory,
        },
        # with a cancelled booking due to expiration
        "Budapest": {
            "bookingLimitDatetime": two_weeks_ago,
            "beginningDatetime": in_two_weeks,
            "endDatetime": in_two_weeks,
            "bookingFactory": educational_factories.CancelledCollectiveBookingFactory,
            "cancellationReason": educational_models.CollectiveBookingCancellationReasons.EXPIRED,
            "confirmationDate": None,
        },
        "Copenhague": {
            "bookingLimitDatetime": four_weeks_ago,
            "beginningDatetime": two_weeks_ago,
            "endDatetime": in_two_weeks,
            "bookingFactory": educational_factories.CancelledCollectiveBookingFactory,
            "cancellationReason": educational_models.CollectiveBookingCancellationReasons.EXPIRED,
            "confirmationDate": None,
        },
        # with a confirmed booking
        "Dublin": {
            "bookingLimitDatetime": in_two_weeks,
            "beginningDatetime": in_four_weeks,
            "endDatetime": in_four_weeks,
            "bookingFactory": educational_factories.ConfirmedCollectiveBookingFactory,
        },
        "Helsinki": {
            "bookingLimitDatetime": two_weeks_ago,
            "beginningDatetime": in_two_weeks,
            "endDatetime": in_two_weeks,
            "bookingFactory": educational_factories.ConfirmedCollectiveBookingFactory,
        },
        "La Valette": {
            "bookingLimitDatetime": four_weeks_ago,
            "beginningDatetime": two_weeks_ago,
            "endDatetime": in_two_weeks,
            "bookingFactory": educational_factories.ConfirmedCollectiveBookingFactory,
        },
        "Lisbonne": {
            "bookingLimitDatetime": four_weeks_ago,
            "beginningDatetime": yesterday,
            "endDatetime": yesterday,
            "bookingFactory": educational_factories.ConfirmedCollectiveBookingFactory,
        },
        # with a used booking
        "Ljubljana": {
            "bookingLimitDatetime": four_weeks_ago,
            "beginningDatetime": four_weeks_ago,
            "endDatetime": four_weeks_ago,
            "bookingFactory": educational_factories.UsedCollectiveBookingFactory,
        },
        "Luxembourg": {
            "bookingLimitDatetime": four_weeks_ago,
            "beginningDatetime": four_weeks_ago,
            "endDatetime": four_weeks_ago,
            "bookingFactory": educational_factories.ReimbursedCollectiveBookingFactory,
        },
        # with a cancelled booking
        "Madrid": {
            "bookingLimitDatetime": in_two_weeks,
            "beginningDatetime": in_four_weeks,
            "endDatetime": in_four_weeks,
            "bookingFactory": educational_factories.CancelledCollectiveBookingFactory,
            "cancellationReason": educational_models.CollectiveBookingCancellationReasons.OFFERER,
        },
        "Nicosie": {
            "bookingLimitDatetime": two_weeks_ago,
            "beginningDatetime": in_two_weeks,
            "endDatetime": in_two_weeks,
            "bookingFactory": educational_factories.CancelledCollectiveBookingFactory,
            "cancellationReason": educational_models.CollectiveBookingCancellationReasons.OFFERER,
        },
        "Paris": {
            "bookingLimitDatetime": four_weeks_ago,
            "beginningDatetime": two_weeks_ago,
            "endDatetime": in_two_weeks,
            "bookingFactory": educational_factories.CancelledCollectiveBookingFactory,
            "cancellationReason": educational_models.CollectiveBookingCancellationReasons.OFFERER,
        },
        "Prague": {
            "bookingLimitDatetime": four_weeks_ago,
            "beginningDatetime": four_weeks_ago,
            "endDatetime": four_weeks_ago,
            "bookingFactory": educational_factories.CancelledCollectiveBookingFactory,
            "cancellationReason": educational_models.CollectiveBookingCancellationReasons.OFFERER,
        },
        "Londres": {
            "isActive": False,
            "bookingLimitDatetime": in_two_weeks,
            "beginningDatetime": in_four_weeks,
            "endDatetime": in_four_weeks,
        },
        # with a different end date than the beginning date
        "Reykjavik": {
            "bookingLimitDatetime": four_weeks_ago,
            "beginningDatetime": yesterday,
            "endDatetime": tomorrow,
            "bookingFactory": educational_factories.ConfirmedCollectiveBookingFactory,
        },
    }

    for city, attributes in options.items():
        booking_factory = attributes.get("bookingFactory")
        beginning_datetime = attributes["beginningDatetime"]
        end_datetime = attributes["endDatetime"]
        booking_limit_datetime = attributes["bookingLimitDatetime"]
        institution = next(institution_iterator)

        stock = educational_factories.CollectiveStockFactory(
            collectiveOffer__name=f"La culture à {city}",
            collectiveOffer__educational_domains=[next(domains_iterator)],
            collectiveOffer__venue=next(venue_iterator),
            collectiveOffer__validation=OfferValidationStatus.APPROVED,
            collectiveOffer__isActive=attributes.get("isActive", True),
            collectiveOffer__bookingEmails=["toto@totoland.com"],
            collectiveOffer__institution=institution,
            collectiveOffer__formats=[EacFormat.PROJECTION_AUDIOVISUELLE],
            beginningDatetime=beginning_datetime,
            startDatetime=beginning_datetime,
            endDatetime=end_datetime,
            bookingLimitDatetime=booking_limit_datetime,
            priceDetail="Some details",
        )

        if booking_factory:
            booking_attributes = {
                key: attributes[key] for key in ("cancellationReason", "confirmationDate") if key in attributes
            }

            booking_factory(
                collectiveStock=stock,
                educationalYear=current_ansco,
                educationalInstitution=institution,
                confirmationLimitDate=booking_limit_datetime,
                dateCreated=min(datetime.utcnow(), booking_limit_datetime - timedelta(days=1)),
                **booking_attributes,
            )


def create_offer_templates_with_different_displayed_status(
    *,
    offerer: offerers_models.Offerer,
    domains: list[educational_models.EducationalDomain],
) -> None:
    domains_iterator = cycle(domains)
    venue_iterator = cycle(offerer.managedVenues)

    now = datetime.utcnow()
    two_weeks_ago = now - timedelta(days=14)
    yesterday = now - timedelta(days=1)
    in_two_weeks = now + timedelta(days=14)

    options: dict[str, dict[str, typing.Any]] = {
        "Alabama": {"validation": OfferValidationStatus.PENDING},
        "Alaska": {
            "validation": OfferValidationStatus.REJECTED,
            "rejectionReason": educational_models.CollectiveOfferRejectionReason.MISSING_DESCRIPTION,
        },
        "Arizona": {"validation": OfferValidationStatus.DRAFT},
        "Arkansas": {"validation": OfferValidationStatus.APPROVED, "dateArchived": now},
        "California": {"validation": OfferValidationStatus.APPROVED},
        "Colorado": {
            "validation": OfferValidationStatus.APPROVED,
            "dateRange": db_utils.make_timerange(start=two_weeks_ago, end=in_two_weeks),
        },
        "Connecticut": {
            "validation": OfferValidationStatus.APPROVED,
            "dateRange": db_utils.make_timerange(start=two_weeks_ago, end=yesterday),
        },
        "Delaware": {"validation": OfferValidationStatus.APPROVED, "isActive": False},
    }

    for state, attributes in options.items():
        educational_factories.CollectiveOfferTemplateFactory(
            name=f"The culture in {state}",
            validation=attributes["validation"],
            rejectionReason=attributes.get("rejectionReason"),
            isActive=attributes.get("isActive", True),
            dateRange=attributes.get("dateRange"),
            dateArchived=attributes.get("dateArchived"),
            dateCreated=two_weeks_ago,  # necessary to pass constraint template_dates_non_empty_daterange
            venue=next(venue_iterator),
            educational_domains=[next(domains_iterator)],
            bookingEmails=["toto@totoland.com"],
            formats=[EacFormat.PROJECTION_AUDIOVISUELLE],
        )


def create_booking_base_list(
    *,
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
    size = 5 if not settings.CREATE_ADAGE_TESTING_DATA else len(institutions)
    if pending_booking:
        for _i in range(size):
            educational_factories.CollectiveBookingFactory(
                collectiveStock__collectiveOffer__name=f"PENDING offer {next(number_iterator)} pour {offerer.name}",
                collectiveStock__collectiveOffer__venue=next(venue_iterator),
                collectiveStock__collectiveOffer__educational_domains=[next(domains_iterator)],
                collectiveStock__bookingLimitDatetime=datetime.utcnow() + timedelta(15),
                collectiveStock__beginningDatetime=datetime.utcnow() + timedelta(days=20),
                educationalYear=current_ansco,
                educationalInstitution=next(institution_iterator),
                status=educational_models.CollectiveBookingStatus.PENDING,
                confirmationDate=None,
                cancellationLimitDate=datetime.utcnow() + timedelta(days=17),
                confirmationLimitDate=datetime.utcnow() + timedelta(days=15),
                dateCreated=datetime.utcnow() - timedelta(days=30),
            )

    if booked_booking:
        for _i in range(size):
            educational_factories.CollectiveBookingFactory(
                collectiveStock__collectiveOffer__name=f"BOOKED offer {next(number_iterator)} pour {offerer.name}",
                collectiveStock__collectiveOffer__venue=next(venue_iterator),
                collectiveStock__collectiveOffer__educational_domains=[next(domains_iterator)],
                collectiveStock__beginningDatetime=datetime.utcnow() + timedelta(days=20),
                collectiveStock__bookingLimitDatetime=datetime.utcnow() + timedelta(days=15),
                educationalYear=current_ansco,
                educationalInstitution=next(institution_iterator),
                status=educational_models.CollectiveBookingStatus.CONFIRMED,
                confirmationDate=datetime.utcnow() - timedelta(days=1),
                cancellationLimitDate=datetime.utcnow() + timedelta(days=17),
                confirmationLimitDate=datetime.utcnow() + timedelta(days=15),
                dateCreated=datetime.utcnow() - timedelta(days=30),
            )
    if confirmed_booking:
        for _i in range(size):
            educational_factories.CollectiveBookingFactory(
                collectiveStock__collectiveOffer__name=f"CONFIRMED offer {next(number_iterator)} pour {offerer.name}",
                collectiveStock__collectiveOffer__venue=next(venue_iterator),
                collectiveStock__collectiveOffer__educational_domains=[next(domains_iterator)],
                collectiveStock__beginningDatetime=datetime.utcnow() + timedelta(days=20),
                collectiveStock__bookingLimitDatetime=datetime.utcnow() - timedelta(days=5),
                educationalYear=current_ansco,
                educationalInstitution=next(institution_iterator),
                status=educational_models.CollectiveBookingStatus.CONFIRMED,
                confirmationDate=datetime.utcnow() - timedelta(days=3),
                cancellationLimitDate=datetime.utcnow(),
                confirmationLimitDate=datetime.utcnow() - timedelta(days=2),
                dateCreated=datetime.utcnow() - timedelta(days=30),
            )
    if used_booking:
        for i in range(size):
            booking = educational_factories.CollectiveBookingFactory(
                collectiveStock__collectiveOffer__name=f"USED offer {next(number_iterator)} pour {offerer.name}",
                collectiveStock__collectiveOffer__venue=next(venue_iterator),
                collectiveStock__collectiveOffer__educational_domains=[next(domains_iterator)],
                collectiveStock__beginningDatetime=datetime.utcnow()
                - timedelta(days=i + 2),  # all USED booking must be at least 2 days old
                collectiveStock__bookingLimitDatetime=datetime.utcnow() - timedelta(days=15),
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
        for _i in range(size):
            booking = educational_factories.CollectiveBookingFactory(
                collectiveStock__collectiveOffer__name=f"REIMBURSED offer {next(number_iterator)} pour {offerer.name}",
                collectiveStock__collectiveOffer__venue=next(venue_iterator),
                collectiveStock__collectiveOffer__educational_domains=[next(domains_iterator)],
                collectiveStock__beginningDatetime=datetime.utcnow() - timedelta(days=15),
                collectiveStock__bookingLimitDatetime=datetime.utcnow() - timedelta(days=18),
                educationalYear=current_ansco,
                educationalInstitution=next(institution_iterator),
                status=educational_models.CollectiveBookingStatus.REIMBURSED,
                dateCreated=datetime.utcnow() - timedelta(days=20),
                dateUsed=datetime.utcnow() - timedelta(days=15),
                confirmationDate=datetime.utcnow() - timedelta(days=18),
                cancellationLimitDate=datetime.utcnow() - timedelta(days=16),
                confirmationLimitDate=datetime.utcnow() - timedelta(days=18),
                reimbursementDate=datetime.utcnow() - timedelta(days=12),
            )

            finance_factories.CollectivePricingFactory(
                status=finance_models.PricingStatus.INVOICED, collectiveBooking=booking
            )
    if cancelled_ac:
        for _i in range(size):
            educational_factories.CollectiveBookingFactory(
                collectiveStock__collectiveOffer__name=f"CANCELLED BY AC offer {next(number_iterator)} pour {offerer.name}",
                collectiveStock__collectiveOffer__venue=next(venue_iterator),
                collectiveStock__collectiveOffer__educational_domains=[next(domains_iterator)],
                collectiveStock__beginningDatetime=datetime.utcnow() + timedelta(days=20),
                collectiveStock__bookingLimitDatetime=datetime.utcnow() + timedelta(days=15),
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
        for _i in range(size):
            educational_factories.CollectiveBookingFactory(
                collectiveStock__collectiveOffer__name=f"CANCELLED BY EPLE offer {next(number_iterator)} pour {offerer.name}",
                collectiveStock__collectiveOffer__venue=next(venue_iterator),
                collectiveStock__collectiveOffer__educational_domains=[next(domains_iterator)],
                collectiveStock__beginningDatetime=datetime.utcnow() + timedelta(days=20),
                collectiveStock__bookingLimitDatetime=datetime.utcnow() + timedelta(days=15),
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
        for _i in range(size):
            educational_factories.CollectiveBookingFactory(
                collectiveStock__collectiveOffer__name=f"CANCELLED AUTOMATICALLY offer {next(number_iterator)} pour {offerer.name}",
                collectiveStock__collectiveOffer__venue=next(venue_iterator),
                collectiveStock__collectiveOffer__educational_domains=[next(domains_iterator)],
                collectiveStock__beginningDatetime=datetime.utcnow() + timedelta(days=20),
                collectiveStock__bookingLimitDatetime=datetime.utcnow() - timedelta(days=15),
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


def create_domains(
    national_programs: typing.Sequence[educational_models.NationalProgram],
) -> list[educational_models.EducationalDomain]:
    college_au_cinema = [np for np in national_programs if np.id == 1]
    lyceens_apprentis_au_cinema = [np for np in national_programs if np.id == 3]
    olympiade_culturelle = [np for np in national_programs if np.id == 4]
    jeunes_en_librairie = [np for np in national_programs if np.id == 6]
    return [
        educational_factories.EducationalDomainFactory(
            name="Architecture", id=1, nationalPrograms=olympiade_culturelle
        ),
        educational_factories.EducationalDomainFactory(
            name="Arts du cirque et arts de la rue", id=2, nationalPrograms=olympiade_culturelle
        ),
        educational_factories.EducationalDomainFactory(
            name="Arts numériques", id=4, nationalPrograms=olympiade_culturelle
        ),
        educational_factories.EducationalDomainFactory(
            name="Arts visuels, arts plastiques, arts appliqués", id=5, nationalPrograms=olympiade_culturelle
        ),
        educational_factories.EducationalDomainFactory(
            name="Cinéma, audiovisuel",
            id=6,
            nationalPrograms=college_au_cinema + lyceens_apprentis_au_cinema,
        ),
        educational_factories.EducationalDomainFactory(
            name="Culture scientifique, technique et industrielle", id=7, nationalPrograms=olympiade_culturelle
        ),
        educational_factories.EducationalDomainFactory(name="Danse", id=8, nationalPrograms=olympiade_culturelle),
        educational_factories.EducationalDomainFactory(name="Design", id=9, nationalPrograms=olympiade_culturelle),
        educational_factories.EducationalDomainFactory(
            name="Développement durable", id=10, nationalPrograms=olympiade_culturelle
        ),
        educational_factories.EducationalDomainFactory(
            name="Univers du livre, de la lecture et des écritures",
            id=11,
            nationalPrograms=jeunes_en_librairie,
        ),
        educational_factories.EducationalDomainFactory(name="Musique", id=12, nationalPrograms=olympiade_culturelle),
        educational_factories.EducationalDomainFactory(name="Patrimoine", id=13, nationalPrograms=olympiade_culturelle),
        educational_factories.EducationalDomainFactory(
            name="Photographie", id=14, nationalPrograms=olympiade_culturelle
        ),
        educational_factories.EducationalDomainFactory(
            name="Théâtre, expression dramatique, marionnettes", id=15, nationalPrograms=olympiade_culturelle
        ),
        educational_factories.EducationalDomainFactory(
            name="Bande dessinée", id=16, nationalPrograms=olympiade_culturelle
        ),
        educational_factories.EducationalDomainFactory(
            name="Média et information", id=17, nationalPrograms=olympiade_culturelle
        ),
        educational_factories.EducationalDomainFactory(name="Mémoire", id=18, nationalPrograms=olympiade_culturelle),
    ]


def create_national_programs() -> list[educational_models.NationalProgram]:
    return [
        educational_factories.NationalProgramFactory(name="collège au cinéma", id=1),
        educational_factories.NationalProgramFactory(name="Lycéens et apprentis au cinéma", id=3),
        educational_factories.NationalProgramFactory(name="L’Olympiade culturelle", id=4),
        educational_factories.NationalProgramFactory(name="Théâtre au collège", id=5),
        educational_factories.NationalProgramFactory(name="Jeunes en librairie", id=6),
    ]


def reset_offer_id_seq() -> None:
    db.session.execute("ALTER SEQUENCE collective_offer_id_seq RESTART WITH 1")
    db.session.execute("ALTER SEQUENCE collective_offer_template_id_seq RESTART WITH 1")
