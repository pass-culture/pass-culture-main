from datetime import datetime
from datetime import timedelta
from itertools import count
from itertools import cycle

from pcapi.core.educational import factories as educational_factories
from pcapi.core.educational import models as educational_models
from pcapi.core.offerers import models as offerers_models
from pcapi.models import db
from pcapi.models.offer_mixin import OfferValidationStatus
from pcapi.utils.image_conversion import DO_NOT_CROP


def create_offers(
    offerers: list[offerers_models.Offerer], institutions: list[educational_models.EducationalInstitution]
) -> None:
    reset_offer_id_seq()
    domains = create_domains()
    offerers_iterator = iter(offerers)

    # eac_1
    offerer = next(offerers_iterator)
    create_offers_base_list(
        offerer=offerer,
        institutions=institutions,
        domains=domains,
    )
    create_booking_base_list(
        offerer=offerer,
        institutions=institutions,
        domains=domains,
    )
    # eac_2
    offerer = next(offerers_iterator)
    create_offers_base_list(
        offerer=offerer,
        institutions=institutions,
        domains=domains,
    )
    create_booking_base_list(
        offerer=offerer,
        institutions=institutions,
        domains=domains,
    )

    # eac_pending_bank_informations
    offerer = next(offerers_iterator)
    create_offers_base_list(
        offerer=offerer,
        institutions=institutions,
        domains=domains,
    )
    create_booking_base_list(
        offerer=offerer,
        institutions=institutions,
        domains=domains,
        reimbursed_booking=False,
    )

    # eac_no_cb
    offerer = next(offerers_iterator)
    create_offers_base_list(
        offerer=offerer,
        institutions=institutions,
        domains=domains,
    )
    create_booking_base_list(
        offerer=offerer,
        institutions=institutions,
        domains=domains,
        reimbursed_booking=False,
    )

    # eac_rejected
    offerer = next(offerers_iterator)
    create_offers_base_list(
        offerer=offerer,
        institutions=institutions,
        domains=domains,
    )


def create_offers_base_list(
    offerer: offerers_models.Offerer,
    institutions: list[educational_models.EducationalInstitution],
    domains: list[educational_models.EducationalDomain],
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
    number_iterator = count()
    offers = []
    templates = []
    if basic_offers:
        stock = educational_factories.CollectiveStockFactory(
            collectiveOffer__name=f"offer {next(number_iterator)} pour {offerer.name}",
            collectiveOffer__educational_domains=[next(domains_iterator)],
            collectiveOffer__venue=next(venue_iterator),
            beginningDatetime=datetime.utcnow() + timedelta(days=60),
        )
        offers.append(stock.collectiveOffer)
        stock = educational_factories.CollectiveStockFactory(
            collectiveOffer__name=f"offer {next(number_iterator)} pour {offerer.name}",
            collectiveOffer__educational_domains=[next(domains_iterator)],
            collectiveOffer__venue=next(venue_iterator),
            beginningDatetime=datetime.utcnow() + timedelta(days=60),
        )
        offers.append(stock.collectiveOffer)
        stock = educational_factories.CollectiveStockFactory(
            collectiveOffer__name=f"offer {next(number_iterator)} pour {offerer.name}",
            collectiveOffer__educational_domains=[next(domains_iterator)],
            collectiveOffer__venue=next(venue_iterator),
            beginningDatetime=datetime.utcnow() + timedelta(days=60),
        )
        offers.append(stock.collectiveOffer)
        stock = educational_factories.CollectiveStockFactory(
            collectiveOffer__name=f"offer {next(number_iterator)} pour {offerer.name}",
            collectiveOffer__educational_domains=[next(domains_iterator)],
            collectiveOffer__venue=next(venue_iterator),
            beginningDatetime=datetime.utcnow() + timedelta(days=60),
        )
        offers.append(stock.collectiveOffer)
        stock = educational_factories.CollectiveStockFactory(
            collectiveOffer__name=f"offer {next(number_iterator)} pour {offerer.name}",
            collectiveOffer__educational_domains=[next(domains_iterator)],
            collectiveOffer__venue=next(venue_iterator),
            beginningDatetime=datetime.utcnow() + timedelta(days=60),
        )
        offers.append(stock.collectiveOffer)
    if image_offers:
        stock = educational_factories.CollectiveStockFactory(
            collectiveOffer__name=f"offer {next(number_iterator)} pour {offerer.name} with image",
            collectiveOffer__educational_domains=[next(domains_iterator)],
            collectiveOffer__venue=next(venue_iterator),
            beginningDatetime=datetime.utcnow() + timedelta(days=60),
        )
        add_image_to_offer(stock.collectiveOffer, next(image_iterator))
        offers.append(stock.collectiveOffer)
        stock = educational_factories.CollectiveStockFactory(
            collectiveOffer__name=f"offer {next(number_iterator)} pour {offerer.name} with image",
            collectiveOffer__educational_domains=[next(domains_iterator)],
            collectiveOffer__venue=next(venue_iterator),
            beginningDatetime=datetime.utcnow() + timedelta(days=60),
        )
        add_image_to_offer(stock.collectiveOffer, next(image_iterator))
        offers.append(stock.collectiveOffer)
        stock = educational_factories.CollectiveStockFactory(
            collectiveOffer__name=f"offer {next(number_iterator)} pour {offerer.name} with image",
            collectiveOffer__educational_domains=[next(domains_iterator)],
            collectiveOffer__venue=next(venue_iterator),
            beginningDatetime=datetime.utcnow() + timedelta(days=60),
        )
        add_image_to_offer(stock.collectiveOffer, next(image_iterator))
        offers.append(stock.collectiveOffer)
        stock = educational_factories.CollectiveStockFactory(
            collectiveOffer__name=f"offer {next(number_iterator)} pour {offerer.name} with image",
            collectiveOffer__educational_domains=[next(domains_iterator)],
            collectiveOffer__venue=next(venue_iterator),
            beginningDatetime=datetime.utcnow() + timedelta(days=60),
        )
        add_image_to_offer(stock.collectiveOffer, next(image_iterator))
        offers.append(stock.collectiveOffer)
        stock = educational_factories.CollectiveStockFactory(
            collectiveOffer__name=f"offer {next(number_iterator)} pour {offerer.name} with image",
            collectiveOffer__educational_domains=[next(domains_iterator)],
            collectiveOffer__venue=next(venue_iterator),
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
        educational_factories.CollectiveStockFactory(
            collectiveOffer__name=f"offer {next(number_iterator)} pour {offerer.name} to teacher",
            collectiveOffer__educational_domains=[next(domains_iterator)],
            collectiveOffer__venue=next(venue_iterator),
            collectiveOffer__institution=institution,
            collectiveOffer__teacher=redactor,
            beginningDatetime=datetime.utcnow() + timedelta(days=60),
        )
        educational_factories.CollectiveStockFactory(
            collectiveOffer__name=f"offer {next(number_iterator)} pour {offerer.name} to teacher",
            collectiveOffer__educational_domains=[next(domains_iterator)],
            collectiveOffer__venue=next(venue_iterator),
            collectiveOffer__institution=institution,
            collectiveOffer__teacher=redactor,
            beginningDatetime=datetime.utcnow() + timedelta(days=60),
        )
        educational_factories.CollectiveStockFactory(
            collectiveOffer__name=f"offer {next(number_iterator)} pour {offerer.name} to teacher",
            collectiveOffer__educational_domains=[next(domains_iterator)],
            collectiveOffer__venue=next(venue_iterator),
            collectiveOffer__institution=institution,
            collectiveOffer__teacher=redactor,
            beginningDatetime=datetime.utcnow() + timedelta(days=60),
        )
        educational_factories.CollectiveStockFactory(
            collectiveOffer__name=f"offer {next(number_iterator)} pour {offerer.name} to teacher",
            collectiveOffer__educational_domains=[next(domains_iterator)],
            collectiveOffer__venue=next(venue_iterator),
            collectiveOffer__institution=institution,
            collectiveOffer__teacher=redactor,
            beginningDatetime=datetime.utcnow() + timedelta(days=60),
        )
        educational_factories.CollectiveStockFactory(
            collectiveOffer__name=f"offer {next(number_iterator)} pour {offerer.name} to teacher",
            collectiveOffer__educational_domains=[next(domains_iterator)],
            collectiveOffer__venue=next(venue_iterator),
            collectiveOffer__institution=institution,
            collectiveOffer__teacher=redactor,
            beginningDatetime=datetime.utcnow() + timedelta(days=60),
        )
    if public_api_offers:
        stock = educational_factories.CollectiveStockFactory(
            collectiveOffer__name=f"offer {next(number_iterator)} pour {offerer.name} public api",
            collectiveOffer__educational_domains=[next(domains_iterator)],
            collectiveOffer__venue=next(venue_iterator),
            collectiveOffer__institution=next(institution_iterator),
            collectiveOffer__interventionArea=[],
            collectiveOffer__isPublicApi=True,
            beginningDatetime=datetime.utcnow() + timedelta(days=60),
        )
        offers.append(stock.collectiveOffer)
        stock = educational_factories.CollectiveStockFactory(
            collectiveOffer__name=f"offer {next(number_iterator)} pour {offerer.name} public api",
            collectiveOffer__educational_domains=[next(domains_iterator)],
            collectiveOffer__venue=next(venue_iterator),
            collectiveOffer__institution=next(institution_iterator),
            collectiveOffer__interventionArea=[],
            collectiveOffer__isPublicApi=True,
            beginningDatetime=datetime.utcnow() + timedelta(days=60),
        )
        offers.append(stock.collectiveOffer)
        stock = educational_factories.CollectiveStockFactory(
            collectiveOffer__name=f"offer {next(number_iterator)} pour {offerer.name} public api",
            collectiveOffer__educational_domains=[next(domains_iterator)],
            collectiveOffer__venue=next(venue_iterator),
            collectiveOffer__institution=next(institution_iterator),
            collectiveOffer__interventionArea=[],
            collectiveOffer__isPublicApi=True,
            beginningDatetime=datetime.utcnow() + timedelta(days=60),
        )
        offers.append(stock.collectiveOffer)
        stock = educational_factories.CollectiveStockFactory(
            collectiveOffer__name=f"offer {next(number_iterator)} pour {offerer.name} public api",
            collectiveOffer__educational_domains=[next(domains_iterator)],
            collectiveOffer__venue=next(venue_iterator),
            collectiveOffer__institution=next(institution_iterator),
            collectiveOffer__interventionArea=[],
            collectiveOffer__isPublicApi=True,
            beginningDatetime=datetime.utcnow() + timedelta(days=60),
        )
        offers.append(stock.collectiveOffer)
        stock = educational_factories.CollectiveStockFactory(
            collectiveOffer__name=f"offer {next(number_iterator)} pour {offerer.name} public api",
            collectiveOffer__educational_domains=[next(domains_iterator)],
            collectiveOffer__venue=next(venue_iterator),
            collectiveOffer__institution=next(institution_iterator),
            collectiveOffer__interventionArea=[],
            collectiveOffer__isPublicApi=True,
            beginningDatetime=datetime.utcnow() + timedelta(days=60),
        )
        offers.append(stock.collectiveOffer)
    if expired_offers:
        educational_factories.CollectiveStockFactory(
            collectiveOffer__name=f"offer {next(number_iterator)} pour {offerer.name} expired",
            collectiveOffer__educational_domains=[next(domains_iterator)],
            collectiveOffer__venue=next(venue_iterator),
            bookingLimitDatetime=datetime.utcnow() - timedelta(days=2),
            beginningDatetime=datetime.utcnow(),
        )
        educational_factories.CollectiveStockFactory(
            collectiveOffer__name=f"offer {next(number_iterator)} pour {offerer.name} expired",
            collectiveOffer__educational_domains=[next(domains_iterator)],
            collectiveOffer__venue=next(venue_iterator),
            bookingLimitDatetime=datetime.utcnow() - timedelta(days=2),
            beginningDatetime=datetime.utcnow(),
        )
        educational_factories.CollectiveStockFactory(
            collectiveOffer__name=f"offer {next(number_iterator)} pour {offerer.name} expired",
            collectiveOffer__educational_domains=[next(domains_iterator)],
            collectiveOffer__venue=next(venue_iterator),
            bookingLimitDatetime=datetime.utcnow() - timedelta(days=2),
            beginningDatetime=datetime.utcnow(),
        )
        educational_factories.CollectiveStockFactory(
            collectiveOffer__name=f"offer {next(number_iterator)} pour {offerer.name} expired",
            collectiveOffer__educational_domains=[next(domains_iterator)],
            collectiveOffer__venue=next(venue_iterator),
            bookingLimitDatetime=datetime.utcnow() - timedelta(days=2),
            beginningDatetime=datetime.utcnow(),
        )
        educational_factories.CollectiveStockFactory(
            collectiveOffer__name=f"offer {next(number_iterator)} pour {offerer.name} expired",
            collectiveOffer__educational_domains=[next(domains_iterator)],
            collectiveOffer__venue=next(venue_iterator),
            bookingLimitDatetime=datetime.utcnow() - timedelta(days=2),
            beginningDatetime=datetime.utcnow(),
        )
    if pending_offers:
        educational_factories.CollectiveStockFactory(
            collectiveOffer__name=f"offer {next(number_iterator)} pour {offerer.name} pending",
            collectiveOffer__educational_domains=[next(domains_iterator)],
            collectiveOffer__venue=next(venue_iterator),
            collectiveOffer__validation=OfferValidationStatus.PENDING,
            beginningDatetime=datetime.utcnow() + timedelta(days=60),
        )
        educational_factories.CollectiveStockFactory(
            collectiveOffer__name=f"offer {next(number_iterator)} pour {offerer.name} pending",
            collectiveOffer__educational_domains=[next(domains_iterator)],
            collectiveOffer__venue=next(venue_iterator),
            collectiveOffer__validation=OfferValidationStatus.PENDING,
            beginningDatetime=datetime.utcnow() + timedelta(days=60),
        )
        educational_factories.CollectiveStockFactory(
            collectiveOffer__name=f"offer {next(number_iterator)} pour {offerer.name} pending",
            collectiveOffer__educational_domains=[next(domains_iterator)],
            collectiveOffer__venue=next(venue_iterator),
            collectiveOffer__validation=OfferValidationStatus.PENDING,
            beginningDatetime=datetime.utcnow() + timedelta(days=60),
        )
        educational_factories.CollectiveStockFactory(
            collectiveOffer__name=f"offer {next(number_iterator)} pour {offerer.name} pending",
            collectiveOffer__educational_domains=[next(domains_iterator)],
            collectiveOffer__venue=next(venue_iterator),
            collectiveOffer__validation=OfferValidationStatus.PENDING,
            beginningDatetime=datetime.utcnow() + timedelta(days=60),
        )
        educational_factories.CollectiveStockFactory(
            collectiveOffer__name=f"offer {next(number_iterator)} pour {offerer.name} pending",
            collectiveOffer__educational_domains=[next(domains_iterator)],
            collectiveOffer__venue=next(venue_iterator),
            collectiveOffer__validation=OfferValidationStatus.PENDING,
            beginningDatetime=datetime.utcnow() + timedelta(days=60),
        )
    if offers_next_year:
        current_year = datetime.utcnow().year
        target_year = current_year + 2 if datetime.utcnow().month >= 9 else current_year + 1
        educational_factories.CollectiveStockFactory(
            collectiveOffer__name=f"offer next year {next(number_iterator)} pour {offerer.name}",
            collectiveOffer__educational_domains=[next(domains_iterator)],
            collectiveOffer__venue=next(venue_iterator),
            beginningDatetime=datetime(target_year, 3, 18),
            bookingLimitDatetime=datetime(target_year, 3, 3),
        )
        educational_factories.CollectiveStockFactory(
            collectiveOffer__name=f"offer next year {next(number_iterator)} pour {offerer.name}",
            collectiveOffer__educational_domains=[next(domains_iterator)],
            collectiveOffer__venue=next(venue_iterator),
            beginningDatetime=datetime(target_year, 3, 18),
            bookingLimitDatetime=datetime(target_year, 3, 3),
        )
        educational_factories.CollectiveStockFactory(
            collectiveOffer__name=f"offer next year {next(number_iterator)} pour {offerer.name}",
            collectiveOffer__educational_domains=[next(domains_iterator)],
            collectiveOffer__venue=next(venue_iterator),
            beginningDatetime=datetime(target_year, 3, 18),
            bookingLimitDatetime=datetime(target_year, 3, 3),
        )
        educational_factories.CollectiveStockFactory(
            collectiveOffer__name=f"offer next year {next(number_iterator)} pour {offerer.name}",
            collectiveOffer__educational_domains=[next(domains_iterator)],
            collectiveOffer__venue=next(venue_iterator),
            beginningDatetime=datetime(target_year, 3, 18),
            bookingLimitDatetime=datetime(target_year, 3, 3),
        )
        educational_factories.CollectiveStockFactory(
            collectiveOffer__name=f"offer next year {next(number_iterator)} pour {offerer.name}",
            collectiveOffer__educational_domains=[next(domains_iterator)],
            collectiveOffer__venue=next(venue_iterator),
            beginningDatetime=datetime(target_year, 3, 18),
            bookingLimitDatetime=datetime(target_year, 3, 3),
        )

    if offers_intervention_56:
        stock = educational_factories.CollectiveStockFactory(
            collectiveOffer__name=f"offer {next(number_iterator)} pour {offerer.name} interventionArea 56",
            collectiveOffer__educational_domains=[next(domains_iterator)],
            collectiveOffer__venue=next(venue_iterator),
            collectiveOffer__interventionArea=["56"],
            beginningDatetime=datetime.utcnow() + timedelta(days=60),
        )
        offers.append(stock.collectiveOffer)
        stock = educational_factories.CollectiveStockFactory(
            collectiveOffer__name=f"offer {next(number_iterator)} pour {offerer.name} interventionArea 56",
            collectiveOffer__educational_domains=[next(domains_iterator)],
            collectiveOffer__venue=next(venue_iterator),
            collectiveOffer__interventionArea=["56"],
            beginningDatetime=datetime.utcnow() + timedelta(days=60),
        )
        offers.append(stock.collectiveOffer)
        stock = educational_factories.CollectiveStockFactory(
            collectiveOffer__name=f"offer {next(number_iterator)} pour {offerer.name} interventionArea 56",
            collectiveOffer__educational_domains=[next(domains_iterator)],
            collectiveOffer__venue=next(venue_iterator),
            collectiveOffer__interventionArea=["56"],
            beginningDatetime=datetime.utcnow() + timedelta(days=60),
        )
        offers.append(stock.collectiveOffer)
        stock = educational_factories.CollectiveStockFactory(
            collectiveOffer__name=f"offer {next(number_iterator)} pour {offerer.name} interventionArea 56",
            collectiveOffer__educational_domains=[next(domains_iterator)],
            collectiveOffer__venue=next(venue_iterator),
            collectiveOffer__interventionArea=["56"],
            beginningDatetime=datetime.utcnow() + timedelta(days=60),
        )
        offers.append(stock.collectiveOffer)
        stock = educational_factories.CollectiveStockFactory(
            collectiveOffer__name=f"offer {next(number_iterator)} pour {offerer.name} interventionArea 56",
            collectiveOffer__educational_domains=[next(domains_iterator)],
            collectiveOffer__venue=next(venue_iterator),
            collectiveOffer__interventionArea=["56"],
            beginningDatetime=datetime.utcnow() + timedelta(days=60),
        )
        offers.append(stock.collectiveOffer)
    if offers_intervention_91:
        stock = educational_factories.CollectiveStockFactory(
            collectiveOffer__name=f"offer {next(number_iterator)} pour {offerer.name} interventionArea 91",
            collectiveOffer__educational_domains=[next(domains_iterator)],
            collectiveOffer__venue=next(venue_iterator),
            collectiveOffer__interventionArea=["91"],
            beginningDatetime=datetime.utcnow() + timedelta(days=60),
        )
        offers.append(stock.collectiveOffer)
        stock = educational_factories.CollectiveStockFactory(
            collectiveOffer__name=f"offer {next(number_iterator)} pour {offerer.name} interventionArea 91",
            collectiveOffer__educational_domains=[next(domains_iterator)],
            collectiveOffer__venue=next(venue_iterator),
            collectiveOffer__interventionArea=["91"],
            beginningDatetime=datetime.utcnow() + timedelta(days=60),
        )
        offers.append(stock.collectiveOffer)
        stock = educational_factories.CollectiveStockFactory(
            collectiveOffer__name=f"offer {next(number_iterator)} pour {offerer.name} interventionArea 91",
            collectiveOffer__educational_domains=[next(domains_iterator)],
            collectiveOffer__venue=next(venue_iterator),
            collectiveOffer__interventionArea=["91"],
            beginningDatetime=datetime.utcnow() + timedelta(days=60),
        )
        offers.append(stock.collectiveOffer)
        stock = educational_factories.CollectiveStockFactory(
            collectiveOffer__name=f"offer {next(number_iterator)} pour {offerer.name} interventionArea 91",
            collectiveOffer__educational_domains=[next(domains_iterator)],
            collectiveOffer__venue=next(venue_iterator),
            collectiveOffer__interventionArea=["91"],
            beginningDatetime=datetime.utcnow() + timedelta(days=60),
        )
        offers.append(stock.collectiveOffer)
        stock = educational_factories.CollectiveStockFactory(
            collectiveOffer__name=f"offer {next(number_iterator)} pour {offerer.name} interventionArea 91",
            collectiveOffer__educational_domains=[next(domains_iterator)],
            collectiveOffer__venue=next(venue_iterator),
            collectiveOffer__interventionArea=["91"],
            beginningDatetime=datetime.utcnow() + timedelta(days=60),
        )
        offers.append(stock.collectiveOffer)
    if basic_templates:
        template = educational_factories.CollectiveOfferTemplateFactory(
            name=f"offer {next(number_iterator)} pour {offerer.name} basic template",
            educational_domains=[next(domains_iterator)],
            venue=next(venue_iterator),
        )
        templates.append(template)
        template = educational_factories.CollectiveOfferTemplateFactory(
            name=f"offer {next(number_iterator)} pour {offerer.name} basic template",
            educational_domains=[next(domains_iterator)],
            venue=next(venue_iterator),
        )
        templates.append(template)
        template = educational_factories.CollectiveOfferTemplateFactory(
            name=f"offer {next(number_iterator)} pour {offerer.name} basic template",
            educational_domains=[next(domains_iterator)],
            venue=next(venue_iterator),
        )
        templates.append(template)
        template = educational_factories.CollectiveOfferTemplateFactory(
            name=f"offer {next(number_iterator)} pour {offerer.name} basic template",
            educational_domains=[next(domains_iterator)],
            venue=next(venue_iterator),
        )
        templates.append(template)
        template = educational_factories.CollectiveOfferTemplateFactory(
            name=f"offer {next(number_iterator)} pour {offerer.name} basic template",
            educational_domains=[next(domains_iterator)],
            venue=next(venue_iterator),
        )
        templates.append(template)
        if from_templates_offers:
            educational_factories.CollectiveStockFactory(
                collectiveOffer__name=f"offer {next(number_iterator)} pour {offerer.name} from template to school",
                collectiveOffer__educational_domains=[next(domains_iterator)],
                collectiveOffer__venue=next(venue_iterator),
                collectiveOffer__template=templates[0],
                collectiveOffer__institution=next(institution_iterator),
            )
            educational_factories.CollectiveStockFactory(
                collectiveOffer__name=f"offer {next(number_iterator)} pour {offerer.name} from template to school",
                collectiveOffer__educational_domains=[next(domains_iterator)],
                collectiveOffer__venue=next(venue_iterator),
                collectiveOffer__template=templates[0],
                collectiveOffer__institution=next(institution_iterator),
            )
            educational_factories.CollectiveStockFactory(
                collectiveOffer__name=f"offer {next(number_iterator)} pour {offerer.name} from template to school",
                collectiveOffer__educational_domains=[next(domains_iterator)],
                collectiveOffer__venue=next(venue_iterator),
                collectiveOffer__template=templates[0],
                collectiveOffer__institution=next(institution_iterator),
            )
            educational_factories.CollectiveStockFactory(
                collectiveOffer__name=f"offer {next(number_iterator)} pour {offerer.name} from template to school",
                collectiveOffer__educational_domains=[next(domains_iterator)],
                collectiveOffer__venue=next(venue_iterator),
                collectiveOffer__template=templates[0],
                collectiveOffer__institution=next(institution_iterator),
            )
            educational_factories.CollectiveStockFactory(
                collectiveOffer__name=f"offer {next(number_iterator)} pour {offerer.name} from template to school",
                collectiveOffer__educational_domains=[next(domains_iterator)],
                collectiveOffer__venue=next(venue_iterator),
                collectiveOffer__template=templates[1],
                collectiveOffer__institution=next(institution_iterator),
            )
    if image_template:
        template = educational_factories.CollectiveOfferTemplateFactory(
            name=f"offer {next(number_iterator)} pour {offerer.name} template image",
            educational_domains=[next(domains_iterator)],
            venue=next(venue_iterator),
        )
        add_image_to_offer(template, next(image_iterator))
        templates.append(template)
        template = educational_factories.CollectiveOfferTemplateFactory(
            name=f"offer {next(number_iterator)} pour {offerer.name} template image",
            educational_domains=[next(domains_iterator)],
            venue=next(venue_iterator),
        )
        add_image_to_offer(template, next(image_iterator))
        templates.append(template)
        template = educational_factories.CollectiveOfferTemplateFactory(
            name=f"offer {next(number_iterator)} pour {offerer.name} template image",
            educational_domains=[next(domains_iterator)],
            venue=next(venue_iterator),
        )
        add_image_to_offer(template, next(image_iterator))
        templates.append(template)
        template = educational_factories.CollectiveOfferTemplateFactory(
            name=f"offer {next(number_iterator)} pour {offerer.name} template image",
            educational_domains=[next(domains_iterator)],
            venue=next(venue_iterator),
        )
        add_image_to_offer(template, next(image_iterator))
        templates.append(template)
        template = educational_factories.CollectiveOfferTemplateFactory(
            name=f"offer {next(number_iterator)} pour {offerer.name} template image",
            educational_domains=[next(domains_iterator)],
            venue=next(venue_iterator),
        )
        add_image_to_offer(template, next(image_iterator))
        templates.append(template)
    if offers_with_request:
        number = next(number_iterator)
        template = educational_factories.CollectiveOfferTemplateFactory(
            name=f"offer {number} pour {offerer.name} template request",
            educational_domains=[next(domains_iterator)],
            venue=next(venue_iterator),
        )
        educational_factories.CollectiveOfferRequestFactory(
            collectiveOfferTemplate=template,
            educationalInstitution=next(institution_iterator),
            educationalRedactor__lastName=f"last name {number} {offerer.name}",
            educationalRedactor__firstName=f"first name {number} {offerer.name}",
        )
        templates.append(template)
        number = next(number_iterator)
        template = educational_factories.CollectiveOfferTemplateFactory(
            name=f"offer {number} pour {offerer.name} template request",
            educational_domains=[next(domains_iterator)],
            venue=next(venue_iterator),
        )
        educational_factories.CollectiveOfferRequestFactory(
            collectiveOfferTemplate=template,
            educationalInstitution=next(institution_iterator),
            educationalRedactor__lastName=f"last name {number} {offerer.name}",
            educationalRedactor__firstName=f"first name {number} {offerer.name}",
            totalStudents=12,
            totalTeachers=2,
            phoneNumber="0199000000",
            requestedDate=datetime.utcnow(),
        )
        templates.append(template)
        number = next(number_iterator)
        template = educational_factories.CollectiveOfferTemplateFactory(
            name=f"offer {number} pour {offerer.name} template request",
            educational_domains=[next(domains_iterator)],
            venue=next(venue_iterator),
        )
        educational_factories.CollectiveOfferRequestFactory(
            collectiveOfferTemplate=template,
            educationalInstitution=next(institution_iterator),
            educationalRedactor__lastName=f"last name {number} {offerer.name}",
            educationalRedactor__firstName=f"first name {number} {offerer.name}",
        )
        templates.append(template)
        number = next(number_iterator)
        template = educational_factories.CollectiveOfferTemplateFactory(
            name=f"offer {number} pour {offerer.name} template request",
            educational_domains=[next(domains_iterator)],
            venue=next(venue_iterator),
        )
        educational_factories.CollectiveOfferRequestFactory(
            collectiveOfferTemplate=template,
            educationalInstitution=next(institution_iterator),
            educationalRedactor__lastName=f"last name {number} {offerer.name}",
            educationalRedactor__firstName=f"first name {number} {offerer.name}",
        )
        templates.append(template)
        number = next(number_iterator)
        template = educational_factories.CollectiveOfferTemplateFactory(
            name=f"offer {number} pour {offerer.name} template request",
            educational_domains=[next(domains_iterator)],
            venue=next(venue_iterator),
        )
        educational_factories.CollectiveOfferRequestFactory(
            collectiveOfferTemplate=template,
            educationalInstitution=next(institution_iterator),
            educationalRedactor__lastName=f"last name {number} {offerer.name}",
            educationalRedactor__firstName=f"first name {number} {offerer.name}",
        )
        templates.append(template)
        number = next(number_iterator)
        template = educational_factories.CollectiveOfferTemplateFactory(
            name=f"offer {number} pour {offerer.name} template request",
            educational_domains=[next(domains_iterator)],
            venue=next(venue_iterator),
        )
        educational_factories.CollectiveOfferRequestFactory(
            collectiveOfferTemplate=template,
            educationalInstitution=next(institution_iterator),
            educationalRedactor__lastName=f"last name {number} {offerer.name}",
            educationalRedactor__firstName=f"first name {number} {offerer.name}",
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
        educational_models.EducationalYear.beginningDate < datetime.utcnow(),
        educational_models.EducationalYear.expirationDate > datetime.utcnow(),
    ).one()
    institution_iterator = cycle(institutions)
    number_iterator = count()
    domains_iterator = cycle(domains)
    venue_iterator = cycle(offerer.managedVenues)
    if pending_booking:
        educational_factories.CollectiveBookingFactory(
            collectiveStock__collectiveOffer__name=f"PENDING offer {next(number_iterator)} pour {offerer.name}",
            collectiveStock__collectiveOffer__venue=next(venue_iterator),
            collectiveStock__collectiveOffer__educational_domains=[next(domains_iterator)],
            collectiveStock__bookingLimitDatetime=datetime.utcnow() + timedelta(15),
            collectiveStock__beginningDatetime=datetime.utcnow() + timedelta(days=20),
            educationalYear=current_ansco,
            educationalInstitution=next(institution_iterator),
            status=educational_models.CollectiveBookingStatus.PENDING,
            cancellationReason=None,
            cancellationDate=None,
            dateUsed=None,
            confirmationDate=None,
            cancellationLimitDate=datetime.utcnow() + timedelta(days=17),
            confirmationLimitDate=datetime.utcnow() + timedelta(days=15),
            dateCreated=datetime.utcnow() - timedelta(days=30),
        )
        educational_factories.CollectiveBookingFactory(
            collectiveStock__collectiveOffer__name=f"PENDING offer {next(number_iterator)} pour {offerer.name}",
            collectiveStock__collectiveOffer__venue=next(venue_iterator),
            collectiveStock__collectiveOffer__educational_domains=[next(domains_iterator)],
            collectiveStock__bookingLimitDatetime=datetime.utcnow() + timedelta(15),
            collectiveStock__beginningDatetime=datetime.utcnow() + timedelta(days=20),
            educationalYear=current_ansco,
            educationalInstitution=next(institution_iterator),
            status=educational_models.CollectiveBookingStatus.PENDING,
            cancellationReason=None,
            cancellationDate=None,
            dateUsed=None,
            confirmationDate=None,
            cancellationLimitDate=datetime.utcnow() + timedelta(days=17),
            confirmationLimitDate=datetime.utcnow() + timedelta(days=15),
            dateCreated=datetime.utcnow() - timedelta(days=30),
        )
        educational_factories.CollectiveBookingFactory(
            collectiveStock__collectiveOffer__name=f"PENDING offer {next(number_iterator)} pour {offerer.name}",
            collectiveStock__collectiveOffer__venue=next(venue_iterator),
            collectiveStock__collectiveOffer__educational_domains=[next(domains_iterator)],
            collectiveStock__bookingLimitDatetime=datetime.utcnow() + timedelta(15),
            collectiveStock__beginningDatetime=datetime.utcnow() + timedelta(days=20),
            educationalYear=current_ansco,
            educationalInstitution=next(institution_iterator),
            status=educational_models.CollectiveBookingStatus.PENDING,
            cancellationReason=None,
            cancellationDate=None,
            dateUsed=None,
            confirmationDate=None,
            cancellationLimitDate=datetime.utcnow() + timedelta(days=17),
            confirmationLimitDate=datetime.utcnow() + timedelta(days=15),
            dateCreated=datetime.utcnow() - timedelta(days=30),
        )
        educational_factories.CollectiveBookingFactory(
            collectiveStock__collectiveOffer__name=f"PENDING offer {next(number_iterator)} pour {offerer.name}",
            collectiveStock__collectiveOffer__venue=next(venue_iterator),
            collectiveStock__collectiveOffer__educational_domains=[next(domains_iterator)],
            collectiveStock__bookingLimitDatetime=datetime.utcnow() + timedelta(15),
            collectiveStock__beginningDatetime=datetime.utcnow() + timedelta(days=20),
            educationalYear=current_ansco,
            educationalInstitution=next(institution_iterator),
            status=educational_models.CollectiveBookingStatus.PENDING,
            cancellationReason=None,
            cancellationDate=None,
            dateUsed=None,
            confirmationDate=None,
            cancellationLimitDate=datetime.utcnow() + timedelta(days=17),
            confirmationLimitDate=datetime.utcnow() + timedelta(days=15),
            dateCreated=datetime.utcnow() - timedelta(days=30),
        )
        educational_factories.CollectiveBookingFactory(
            collectiveStock__collectiveOffer__name=f"PENDING offer {next(number_iterator)} pour {offerer.name}",
            collectiveStock__collectiveOffer__venue=next(venue_iterator),
            collectiveStock__collectiveOffer__educational_domains=[next(domains_iterator)],
            collectiveStock__bookingLimitDatetime=datetime.utcnow() + timedelta(15),
            collectiveStock__beginningDatetime=datetime.utcnow() + timedelta(days=20),
            educationalYear=current_ansco,
            educationalInstitution=next(institution_iterator),
            status=educational_models.CollectiveBookingStatus.PENDING,
            cancellationReason=None,
            cancellationDate=None,
            dateUsed=None,
            confirmationDate=None,
            cancellationLimitDate=datetime.utcnow() + timedelta(days=17),
            confirmationLimitDate=datetime.utcnow() + timedelta(days=15),
            dateCreated=datetime.utcnow() - timedelta(days=30),
        )

    if booked_booking:
        educational_factories.CollectiveBookingFactory(
            collectiveStock__collectiveOffer__name=f"BOOKED offer {next(number_iterator)} pour {offerer.name}",
            collectiveStock__collectiveOffer__venue=next(venue_iterator),
            collectiveStock__collectiveOffer__educational_domains=[next(domains_iterator)],
            collectiveStock__beginningDatetime=datetime.utcnow() + timedelta(days=20),
            collectiveStock__bookingLimitDatetime=datetime.utcnow() + timedelta(days=15),
            educationalYear=current_ansco,
            educationalInstitution=next(institution_iterator),
            status=educational_models.CollectiveBookingStatus.CONFIRMED,
            cancellationReason=None,
            cancellationDate=None,
            dateUsed=None,
            confirmationDate=datetime.utcnow() - timedelta(days=1),
            cancellationLimitDate=datetime.utcnow() + timedelta(days=17),
            confirmationLimitDate=datetime.utcnow() + timedelta(days=15),
            dateCreated=datetime.utcnow() - timedelta(days=30),
        )
        educational_factories.CollectiveBookingFactory(
            collectiveStock__collectiveOffer__name=f"BOOKED offer {next(number_iterator)} pour {offerer.name}",
            collectiveStock__collectiveOffer__venue=next(venue_iterator),
            collectiveStock__collectiveOffer__educational_domains=[next(domains_iterator)],
            collectiveStock__beginningDatetime=datetime.utcnow() + timedelta(days=20),
            collectiveStock__bookingLimitDatetime=datetime.utcnow() + timedelta(days=15),
            educationalYear=current_ansco,
            educationalInstitution=next(institution_iterator),
            status=educational_models.CollectiveBookingStatus.CONFIRMED,
            cancellationReason=None,
            cancellationDate=None,
            dateUsed=None,
            confirmationDate=datetime.utcnow() - timedelta(days=1),
            cancellationLimitDate=datetime.utcnow() + timedelta(days=17),
            confirmationLimitDate=datetime.utcnow() + timedelta(days=15),
            dateCreated=datetime.utcnow() - timedelta(days=30),
        )
        educational_factories.CollectiveBookingFactory(
            collectiveStock__collectiveOffer__name=f"BOOKED offer {next(number_iterator)} pour {offerer.name}",
            collectiveStock__collectiveOffer__venue=next(venue_iterator),
            collectiveStock__collectiveOffer__educational_domains=[next(domains_iterator)],
            collectiveStock__beginningDatetime=datetime.utcnow() + timedelta(days=20),
            collectiveStock__bookingLimitDatetime=datetime.utcnow() + timedelta(days=15),
            educationalYear=current_ansco,
            educationalInstitution=next(institution_iterator),
            status=educational_models.CollectiveBookingStatus.CONFIRMED,
            cancellationReason=None,
            cancellationDate=None,
            dateUsed=None,
            confirmationDate=datetime.utcnow() - timedelta(days=1),
            cancellationLimitDate=datetime.utcnow() + timedelta(days=17),
            confirmationLimitDate=datetime.utcnow() + timedelta(days=15),
            dateCreated=datetime.utcnow() - timedelta(days=30),
        )
        educational_factories.CollectiveBookingFactory(
            collectiveStock__collectiveOffer__name=f"BOOKED offer {next(number_iterator)} pour {offerer.name}",
            collectiveStock__collectiveOffer__venue=next(venue_iterator),
            collectiveStock__collectiveOffer__educational_domains=[next(domains_iterator)],
            collectiveStock__beginningDatetime=datetime.utcnow() + timedelta(days=20),
            collectiveStock__bookingLimitDatetime=datetime.utcnow() + timedelta(days=15),
            educationalYear=current_ansco,
            educationalInstitution=next(institution_iterator),
            status=educational_models.CollectiveBookingStatus.CONFIRMED,
            cancellationReason=None,
            cancellationDate=None,
            dateUsed=None,
            confirmationDate=datetime.utcnow() - timedelta(days=1),
            cancellationLimitDate=datetime.utcnow() + timedelta(days=17),
            confirmationLimitDate=datetime.utcnow() + timedelta(days=15),
            dateCreated=datetime.utcnow() - timedelta(days=30),
        )
        educational_factories.CollectiveBookingFactory(
            collectiveStock__collectiveOffer__name=f"BOOKED offer {next(number_iterator)} pour {offerer.name}",
            collectiveStock__collectiveOffer__venue=next(venue_iterator),
            collectiveStock__collectiveOffer__educational_domains=[next(domains_iterator)],
            collectiveStock__beginningDatetime=datetime.utcnow() + timedelta(days=20),
            collectiveStock__bookingLimitDatetime=datetime.utcnow() + timedelta(days=15),
            educationalYear=current_ansco,
            educationalInstitution=next(institution_iterator),
            status=educational_models.CollectiveBookingStatus.CONFIRMED,
            cancellationReason=None,
            cancellationDate=None,
            dateUsed=None,
            confirmationDate=datetime.utcnow() - timedelta(days=1),
            cancellationLimitDate=datetime.utcnow() + timedelta(days=17),
            confirmationLimitDate=datetime.utcnow() + timedelta(days=15),
            dateCreated=datetime.utcnow() - timedelta(days=30),
        )
    if confirmed_booking:
        educational_factories.CollectiveBookingFactory(
            collectiveStock__collectiveOffer__name=f"CONFIRMED offer {next(number_iterator)} pour {offerer.name}",
            collectiveStock__collectiveOffer__venue=next(venue_iterator),
            collectiveStock__collectiveOffer__educational_domains=[next(domains_iterator)],
            collectiveStock__beginningDatetime=datetime.utcnow() + timedelta(days=20),
            collectiveStock__bookingLimitDatetime=datetime.utcnow() - timedelta(days=5),
            educationalYear=current_ansco,
            educationalInstitution=next(institution_iterator),
            status=educational_models.CollectiveBookingStatus.CONFIRMED,
            cancellationReason=None,
            cancellationDate=None,
            dateUsed=None,
            confirmationDate=datetime.utcnow() - timedelta(days=3),
            cancellationLimitDate=datetime.utcnow(),
            confirmationLimitDate=datetime.utcnow() - timedelta(days=2),
            dateCreated=datetime.utcnow() - timedelta(days=30),
        )
        educational_factories.CollectiveBookingFactory(
            collectiveStock__collectiveOffer__name=f"CONFIRMED offer {next(number_iterator)} pour {offerer.name}",
            collectiveStock__collectiveOffer__venue=next(venue_iterator),
            collectiveStock__collectiveOffer__educational_domains=[next(domains_iterator)],
            collectiveStock__beginningDatetime=datetime.utcnow() + timedelta(days=20),
            collectiveStock__bookingLimitDatetime=datetime.utcnow() - timedelta(days=5),
            educationalYear=current_ansco,
            educationalInstitution=next(institution_iterator),
            status=educational_models.CollectiveBookingStatus.CONFIRMED,
            cancellationReason=None,
            cancellationDate=None,
            dateUsed=None,
            confirmationDate=datetime.utcnow() - timedelta(days=3),
            cancellationLimitDate=datetime.utcnow(),
            confirmationLimitDate=datetime.utcnow() - timedelta(days=2),
            dateCreated=datetime.utcnow() - timedelta(days=30),
        )
        educational_factories.CollectiveBookingFactory(
            collectiveStock__collectiveOffer__name=f"CONFIRMED offer {next(number_iterator)} pour {offerer.name}",
            collectiveStock__collectiveOffer__venue=next(venue_iterator),
            collectiveStock__collectiveOffer__educational_domains=[next(domains_iterator)],
            collectiveStock__beginningDatetime=datetime.utcnow() + timedelta(days=20),
            collectiveStock__bookingLimitDatetime=datetime.utcnow() - timedelta(days=5),
            educationalYear=current_ansco,
            educationalInstitution=next(institution_iterator),
            status=educational_models.CollectiveBookingStatus.CONFIRMED,
            cancellationReason=None,
            cancellationDate=None,
            dateUsed=None,
            confirmationDate=datetime.utcnow() - timedelta(days=3),
            cancellationLimitDate=datetime.utcnow(),
            confirmationLimitDate=datetime.utcnow() - timedelta(days=2),
            dateCreated=datetime.utcnow() - timedelta(days=30),
        )
        educational_factories.CollectiveBookingFactory(
            collectiveStock__collectiveOffer__name=f"CONFIRMED offer {next(number_iterator)} pour {offerer.name}",
            collectiveStock__collectiveOffer__venue=next(venue_iterator),
            collectiveStock__collectiveOffer__educational_domains=[next(domains_iterator)],
            collectiveStock__beginningDatetime=datetime.utcnow() + timedelta(days=20),
            collectiveStock__bookingLimitDatetime=datetime.utcnow() - timedelta(days=5),
            educationalYear=current_ansco,
            educationalInstitution=next(institution_iterator),
            status=educational_models.CollectiveBookingStatus.CONFIRMED,
            cancellationReason=None,
            cancellationDate=None,
            dateUsed=None,
            confirmationDate=datetime.utcnow() - timedelta(days=3),
            cancellationLimitDate=datetime.utcnow(),
            confirmationLimitDate=datetime.utcnow() - timedelta(days=2),
            dateCreated=datetime.utcnow() - timedelta(days=30),
        )
        educational_factories.CollectiveBookingFactory(
            collectiveStock__collectiveOffer__name=f"CONFIRMED offer {next(number_iterator)} pour {offerer.name}",
            collectiveStock__collectiveOffer__venue=next(venue_iterator),
            collectiveStock__collectiveOffer__educational_domains=[next(domains_iterator)],
            collectiveStock__beginningDatetime=datetime.utcnow() + timedelta(days=20),
            collectiveStock__bookingLimitDatetime=datetime.utcnow() - timedelta(days=5),
            educationalYear=current_ansco,
            educationalInstitution=next(institution_iterator),
            status=educational_models.CollectiveBookingStatus.CONFIRMED,
            cancellationReason=None,
            cancellationDate=None,
            dateUsed=None,
            confirmationDate=datetime.utcnow() - timedelta(days=3),
            cancellationLimitDate=datetime.utcnow(),
            confirmationLimitDate=datetime.utcnow() - timedelta(days=2),
            dateCreated=datetime.utcnow() - timedelta(days=30),
        )
    if used_booking:
        educational_factories.CollectiveBookingFactory(
            collectiveStock__collectiveOffer__name=f"USED offer {next(number_iterator)} pour {offerer.name}",
            collectiveStock__collectiveOffer__venue=next(venue_iterator),
            collectiveStock__collectiveOffer__educational_domains=[next(domains_iterator)],
            collectiveStock__beginningDatetime=datetime.utcnow(),
            collectiveStock__bookingLimitDatetime=datetime.utcnow() - timedelta(days=15),
            educationalYear=current_ansco,
            educationalInstitution=next(institution_iterator),
            status=educational_models.CollectiveBookingStatus.USED,
            cancellationReason=None,
            cancellationDate=None,
            dateUsed=datetime.utcnow(),
            confirmationDate=datetime.utcnow() - timedelta(days=5),
            cancellationLimitDate=datetime.utcnow() - timedelta(days=2),
            confirmationLimitDate=datetime.utcnow() - timedelta(days=3),
            dateCreated=datetime.utcnow() - timedelta(days=30),
        )
        educational_factories.CollectiveBookingFactory(
            collectiveStock__collectiveOffer__name=f"USED offer {next(number_iterator)} pour {offerer.name}",
            collectiveStock__collectiveOffer__venue=next(venue_iterator),
            collectiveStock__collectiveOffer__educational_domains=[next(domains_iterator)],
            collectiveStock__beginningDatetime=datetime.utcnow(),
            collectiveStock__bookingLimitDatetime=datetime.utcnow() - timedelta(days=15),
            educationalYear=current_ansco,
            educationalInstitution=next(institution_iterator),
            status=educational_models.CollectiveBookingStatus.USED,
            cancellationReason=None,
            cancellationDate=None,
            dateUsed=datetime.utcnow(),
            confirmationDate=datetime.utcnow() - timedelta(days=5),
            cancellationLimitDate=datetime.utcnow() - timedelta(days=2),
            confirmationLimitDate=datetime.utcnow() - timedelta(days=3),
            dateCreated=datetime.utcnow() - timedelta(days=30),
        )
        educational_factories.CollectiveBookingFactory(
            collectiveStock__collectiveOffer__name=f"USED offer {next(number_iterator)} pour {offerer.name}",
            collectiveStock__collectiveOffer__venue=next(venue_iterator),
            collectiveStock__collectiveOffer__educational_domains=[next(domains_iterator)],
            collectiveStock__beginningDatetime=datetime.utcnow(),
            collectiveStock__bookingLimitDatetime=datetime.utcnow() - timedelta(days=15),
            educationalYear=current_ansco,
            educationalInstitution=next(institution_iterator),
            status=educational_models.CollectiveBookingStatus.USED,
            cancellationReason=None,
            cancellationDate=None,
            dateUsed=datetime.utcnow(),
            confirmationDate=datetime.utcnow() - timedelta(days=5),
            cancellationLimitDate=datetime.utcnow() - timedelta(days=2),
            confirmationLimitDate=datetime.utcnow() - timedelta(days=3),
            dateCreated=datetime.utcnow() - timedelta(days=30),
        )
        educational_factories.CollectiveBookingFactory(
            collectiveStock__collectiveOffer__name=f"USED offer {next(number_iterator)} pour {offerer.name}",
            collectiveStock__collectiveOffer__venue=next(venue_iterator),
            collectiveStock__collectiveOffer__educational_domains=[next(domains_iterator)],
            collectiveStock__beginningDatetime=datetime.utcnow(),
            collectiveStock__bookingLimitDatetime=datetime.utcnow() - timedelta(days=15),
            educationalYear=current_ansco,
            educationalInstitution=next(institution_iterator),
            status=educational_models.CollectiveBookingStatus.USED,
            cancellationReason=None,
            cancellationDate=None,
            dateUsed=datetime.utcnow(),
            confirmationDate=datetime.utcnow() - timedelta(days=5),
            cancellationLimitDate=datetime.utcnow() - timedelta(days=2),
            confirmationLimitDate=datetime.utcnow() - timedelta(days=3),
            dateCreated=datetime.utcnow() - timedelta(days=30),
        )
        educational_factories.CollectiveBookingFactory(
            collectiveStock__collectiveOffer__name=f"USED offer {next(number_iterator)} pour {offerer.name}",
            collectiveStock__collectiveOffer__venue=next(venue_iterator),
            collectiveStock__collectiveOffer__educational_domains=[next(domains_iterator)],
            collectiveStock__beginningDatetime=datetime.utcnow(),
            collectiveStock__bookingLimitDatetime=datetime.utcnow() - timedelta(days=15),
            educationalYear=current_ansco,
            educationalInstitution=next(institution_iterator),
            status=educational_models.CollectiveBookingStatus.USED,
            cancellationReason=None,
            cancellationDate=None,
            dateUsed=datetime.utcnow(),
            confirmationDate=datetime.utcnow() - timedelta(days=5),
            cancellationLimitDate=datetime.utcnow() - timedelta(days=2),
            confirmationLimitDate=datetime.utcnow() - timedelta(days=3),
            dateCreated=datetime.utcnow() - timedelta(days=30),
        )
    if reimbursed_booking:
        educational_factories.CollectiveBookingFactory(
            collectiveStock__collectiveOffer__name=f"REIMBURSED offer {next(number_iterator)} pour {offerer.name}",
            collectiveStock__collectiveOffer__venue=next(venue_iterator),
            collectiveStock__collectiveOffer__educational_domains=[next(domains_iterator)],
            collectiveStock__beginningDatetime=datetime.utcnow() - timedelta(days=15),
            collectiveStock__bookingLimitDatetime=datetime.utcnow() - timedelta(days=18),
            educationalYear=current_ansco,
            educationalInstitution=next(institution_iterator),
            status=educational_models.CollectiveBookingStatus.REIMBURSED,
            cancellationReason=None,
            cancellationDate=None,
            dateCreated=datetime.utcnow() - timedelta(days=20),
            dateUsed=datetime.utcnow() - timedelta(days=15),
            confirmationDate=datetime.utcnow() - timedelta(days=18),
            cancellationLimitDate=datetime.utcnow() - timedelta(days=16),
            confirmationLimitDate=datetime.utcnow() - timedelta(days=18),
            reimbursementDate=datetime.utcnow() - timedelta(days=12),
        )
        educational_factories.CollectiveBookingFactory(
            collectiveStock__collectiveOffer__name=f"REIMBURSED offer {next(number_iterator)} pour {offerer.name}",
            collectiveStock__collectiveOffer__venue=next(venue_iterator),
            collectiveStock__collectiveOffer__educational_domains=[next(domains_iterator)],
            collectiveStock__beginningDatetime=datetime.utcnow() - timedelta(days=15),
            collectiveStock__bookingLimitDatetime=datetime.utcnow() - timedelta(days=18),
            educationalYear=current_ansco,
            educationalInstitution=next(institution_iterator),
            status=educational_models.CollectiveBookingStatus.REIMBURSED,
            cancellationReason=None,
            cancellationDate=None,
            dateCreated=datetime.utcnow() - timedelta(days=20),
            dateUsed=datetime.utcnow() - timedelta(days=15),
            confirmationDate=datetime.utcnow() - timedelta(days=18),
            cancellationLimitDate=datetime.utcnow() - timedelta(days=16),
            confirmationLimitDate=datetime.utcnow() - timedelta(days=18),
            reimbursementDate=datetime.utcnow() - timedelta(days=12),
        )
        educational_factories.CollectiveBookingFactory(
            collectiveStock__collectiveOffer__name=f"REIMBURSED offer {next(number_iterator)} pour {offerer.name}",
            collectiveStock__collectiveOffer__venue=next(venue_iterator),
            collectiveStock__collectiveOffer__educational_domains=[next(domains_iterator)],
            collectiveStock__beginningDatetime=datetime.utcnow() - timedelta(days=15),
            collectiveStock__bookingLimitDatetime=datetime.utcnow() - timedelta(days=18),
            educationalYear=current_ansco,
            educationalInstitution=next(institution_iterator),
            status=educational_models.CollectiveBookingStatus.REIMBURSED,
            cancellationReason=None,
            cancellationDate=None,
            dateCreated=datetime.utcnow() - timedelta(days=20),
            dateUsed=datetime.utcnow() - timedelta(days=15),
            confirmationDate=datetime.utcnow() - timedelta(days=18),
            cancellationLimitDate=datetime.utcnow() - timedelta(days=16),
            confirmationLimitDate=datetime.utcnow() - timedelta(days=18),
            reimbursementDate=datetime.utcnow() - timedelta(days=12),
        )
        educational_factories.CollectiveBookingFactory(
            collectiveStock__collectiveOffer__name=f"REIMBURSED offer {next(number_iterator)} pour {offerer.name}",
            collectiveStock__collectiveOffer__venue=next(venue_iterator),
            collectiveStock__collectiveOffer__educational_domains=[next(domains_iterator)],
            collectiveStock__beginningDatetime=datetime.utcnow() - timedelta(days=15),
            collectiveStock__bookingLimitDatetime=datetime.utcnow() - timedelta(days=18),
            educationalYear=current_ansco,
            educationalInstitution=next(institution_iterator),
            status=educational_models.CollectiveBookingStatus.REIMBURSED,
            cancellationReason=None,
            cancellationDate=None,
            dateCreated=datetime.utcnow() - timedelta(days=20),
            dateUsed=datetime.utcnow() - timedelta(days=15),
            confirmationDate=datetime.utcnow() - timedelta(days=18),
            cancellationLimitDate=datetime.utcnow() - timedelta(days=16),
            confirmationLimitDate=datetime.utcnow() - timedelta(days=18),
            reimbursementDate=datetime.utcnow() - timedelta(days=12),
        )
        educational_factories.CollectiveBookingFactory(
            collectiveStock__collectiveOffer__name=f"REIMBURSED offer {next(number_iterator)} pour {offerer.name}",
            collectiveStock__collectiveOffer__venue=next(venue_iterator),
            collectiveStock__collectiveOffer__educational_domains=[next(domains_iterator)],
            collectiveStock__beginningDatetime=datetime.utcnow() - timedelta(days=15),
            collectiveStock__bookingLimitDatetime=datetime.utcnow() - timedelta(days=18),
            educationalYear=current_ansco,
            educationalInstitution=next(institution_iterator),
            status=educational_models.CollectiveBookingStatus.REIMBURSED,
            cancellationReason=None,
            cancellationDate=None,
            dateCreated=datetime.utcnow() - timedelta(days=20),
            dateUsed=datetime.utcnow() - timedelta(days=15),
            confirmationDate=datetime.utcnow() - timedelta(days=18),
            cancellationLimitDate=datetime.utcnow() - timedelta(days=16),
            confirmationLimitDate=datetime.utcnow() - timedelta(days=18),
            reimbursementDate=datetime.utcnow() - timedelta(days=12),
        )
    if cancelled_ac:
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
            dateUsed=None,
            confirmationDate=datetime.utcnow() - timedelta(days=12),
            cancellationLimitDate=datetime.utcnow() + timedelta(days=17),
            confirmationLimitDate=datetime.utcnow() + timedelta(days=15),
        )
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
            dateUsed=None,
            confirmationDate=datetime.utcnow() - timedelta(days=12),
            cancellationLimitDate=datetime.utcnow() + timedelta(days=17),
            confirmationLimitDate=datetime.utcnow() + timedelta(days=15),
        )
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
            dateUsed=None,
            confirmationDate=datetime.utcnow() - timedelta(days=12),
            cancellationLimitDate=datetime.utcnow() + timedelta(days=17),
            confirmationLimitDate=datetime.utcnow() + timedelta(days=15),
        )
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
            dateUsed=None,
            confirmationDate=datetime.utcnow() - timedelta(days=12),
            cancellationLimitDate=datetime.utcnow() + timedelta(days=17),
            confirmationLimitDate=datetime.utcnow() + timedelta(days=15),
        )
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
            dateUsed=None,
            confirmationDate=datetime.utcnow() - timedelta(days=12),
            cancellationLimitDate=datetime.utcnow() + timedelta(days=17),
            confirmationLimitDate=datetime.utcnow() + timedelta(days=15),
        )
    if cancelled_institution:
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
            dateUsed=None,
            confirmationDate=datetime.utcnow() - timedelta(days=12),
            cancellationLimitDate=datetime.utcnow() + timedelta(days=17),
            confirmationLimitDate=datetime.utcnow() + timedelta(days=15),
        )
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
            dateUsed=None,
            confirmationDate=datetime.utcnow() - timedelta(days=12),
            cancellationLimitDate=datetime.utcnow() + timedelta(days=17),
            confirmationLimitDate=datetime.utcnow() + timedelta(days=15),
        )
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
            dateUsed=None,
            confirmationDate=datetime.utcnow() - timedelta(days=12),
            cancellationLimitDate=datetime.utcnow() + timedelta(days=17),
            confirmationLimitDate=datetime.utcnow() + timedelta(days=15),
        )
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
            dateUsed=None,
            confirmationDate=datetime.utcnow() - timedelta(days=12),
            cancellationLimitDate=datetime.utcnow() + timedelta(days=17),
            confirmationLimitDate=datetime.utcnow() + timedelta(days=15),
        )
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
            dateUsed=None,
            confirmationDate=datetime.utcnow() - timedelta(days=12),
            cancellationLimitDate=datetime.utcnow() + timedelta(days=17),
            confirmationLimitDate=datetime.utcnow() + timedelta(days=15),
        )

    if cancelled_expired:
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
            dateUsed=None,
            confirmationDate=None,
            cancellationLimitDate=datetime.utcnow() - timedelta(days=3),
            confirmationLimitDate=datetime.utcnow() - timedelta(days=5),
        )
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
            dateUsed=None,
            confirmationDate=None,
            cancellationLimitDate=datetime.utcnow() - timedelta(days=3),
            confirmationLimitDate=datetime.utcnow() - timedelta(days=5),
        )
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
            dateUsed=None,
            confirmationDate=None,
            cancellationLimitDate=datetime.utcnow() - timedelta(days=3),
            confirmationLimitDate=datetime.utcnow() - timedelta(days=5),
        )
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
            dateUsed=None,
            confirmationDate=None,
            cancellationLimitDate=datetime.utcnow() - timedelta(days=3),
            confirmationLimitDate=datetime.utcnow() - timedelta(days=5),
        )
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
            dateUsed=None,
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


def reset_offer_id_seq() -> None:
    db.session.execute("ALTER SEQUENCE collective_offer_id_seq RESTART WITH 1")
    db.session.execute("ALTER SEQUENCE collective_offer_template_id_seq RESTART WITH 1")
