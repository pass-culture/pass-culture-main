import typing
from datetime import date
from datetime import datetime
from datetime import timedelta
from itertools import count
from itertools import cycle

import sqlalchemy as sa

from pcapi import settings
from pcapi.core import search
from pcapi.core.categories.subcategories import EacFormat
from pcapi.core.educational import factories as educational_factories
from pcapi.core.educational import models as educational_models
from pcapi.core.finance import factories as finance_factories
from pcapi.core.finance import models as finance_models
from pcapi.core.geography import factories as geography_factories
from pcapi.core.offerers import factories as offerers_factories
from pcapi.core.offerers import models as offerers_models
from pcapi.core.providers import models as providers_models
from pcapi.core.users import factories as user_factory
from pcapi.models import db
from pcapi.models.offer_mixin import OfferValidationStatus
from pcapi.sandboxes.scripts.creators.industrial.create_industrial_eac_data.create_collective_api_provider import (
    create_collective_api_provider,
)
from pcapi.utils import db as db_utils
from pcapi.utils.image_conversion import DO_NOT_CROP


class LocationOption(typing.TypedDict):
    name: str
    offerVenue: educational_models.OfferVenueDict
    interventionArea: typing.NotRequired[list[str]]
    locationType: educational_models.CollectiveLocationType
    locationComment: typing.NotRequired[str]
    isManualEdition: typing.NotRequired[bool]
    street: typing.NotRequired[str]  # used in the Address model
    isLocatedAtVenue: typing.NotRequired[bool]  # True in the case offer.venueId = offer.offerVenue.venueId


def get_location_options(venue: offerers_models.Venue, other_venue: offerers_models.Venue) -> list[LocationOption]:
    return [
        {
            "name": "La culture dans la structure de l'acteur",
            "offerVenue": {
                "addressType": educational_models.OfferAddressType.OFFERER_VENUE,
                "venueId": venue.id,
                "otherAddress": "",
            },
            "locationType": educational_models.CollectiveLocationType.ADDRESS,
            "isLocatedAtVenue": True,
        },
        {
            "name": "La culture dans l'école",
            "offerVenue": {
                "addressType": educational_models.OfferAddressType.SCHOOL,
                "venueId": None,
                "otherAddress": "",
            },
            "interventionArea": ["75", "92", "93", "94", "95"],
            "locationType": educational_models.CollectiveLocationType.SCHOOL,
        },
        {
            "name": "La culture à une adresse précise (avec edition manuelle)",
            "offerVenue": {
                "addressType": educational_models.OfferAddressType.OTHER,
                "venueId": None,
                "otherAddress": "35 Bd de Sébastopol, 75001 Paris",
            },
            "interventionArea": ["75", "92", "93", "94", "95"],
            "locationType": educational_models.CollectiveLocationType.ADDRESS,
            "isManualEdition": True,
            "street": "35 Bd de Sébastopol",
        },
        {
            "name": "La culture à une adresse précise",
            "offerVenue": {
                "addressType": educational_models.OfferAddressType.OTHER,
                "venueId": None,
                "otherAddress": "35 Bd de Sébastopol, 75001 Paris",
            },
            "interventionArea": ["75", "92", "93", "94", "95"],
            "locationType": educational_models.CollectiveLocationType.ADDRESS,
            "street": "35 Bd de Sébastopol",
        },
        {
            "name": "La culture dans un lieu flou",
            "offerVenue": {
                "addressType": educational_models.OfferAddressType.OTHER,
                "venueId": None,
                "otherAddress": "A coté de la mairie",
            },
            "interventionArea": ["75", "92", "93", "94", "95"],
            "locationType": educational_models.CollectiveLocationType.TO_BE_DEFINED,
            "locationComment": "A coté de la mairie",
        },
        {
            "name": "La culture chez une autre structure de l'acteur culturel",
            "offerVenue": {
                "addressType": educational_models.OfferAddressType.OFFERER_VENUE,
                "venueId": other_venue.id,
                "otherAddress": "",
            },
            "interventionArea": ["75", "92", "93", "94", "95"],
            "locationType": educational_models.CollectiveLocationType.ADDRESS,
            "isLocatedAtVenue": False,
        },
    ]


def _get_or_create_offerer_address(
    location_option: LocationOption, managing_offerer: offerers_models.Offerer, oa_label: str
) -> offerers_models.OffererAddress | None:
    if location_option["locationType"] != educational_models.CollectiveLocationType.ADDRESS:
        return None

    offer_venue = location_option["offerVenue"]
    if offer_venue["addressType"] == educational_models.OfferAddressType.OFFERER_VENUE:
        target_venue = db.session.query(offerers_models.Venue).get(offer_venue["venueId"])

        if location_option["isLocatedAtVenue"]:
            return target_venue.offererAddress

        # get or create OA with same offerer and adress as target_venue
        label = target_venue.common_name
        target_address = target_venue.offererAddress.address
        offerer_address = (
            db.session.query(offerers_models.OffererAddress)
            .filter(
                offerers_models.OffererAddress.offerer == managing_offerer,
                offerers_models.OffererAddress.address == target_address,
                offerers_models.OffererAddress.label == label,
            )
            .one_or_none()
        )
        if offerer_address is None:
            offerer_address = offerers_factories.OffererAddressFactory.create(
                label=label, address=target_address, offerer=managing_offerer
            )

        return offerer_address

    factory = (
        geography_factories.ManualAddressFactory
        if location_option.get("isManualEdition", False)
        else geography_factories.AddressFactory
    )
    address = factory(street=location_option["street"])
    offerer_address = offerers_factories.OffererAddressFactory.create(
        label=oa_label, address=address, offerer=managing_offerer
    )
    return offerer_address


def create_offers(
    offerers: list[offerers_models.Offerer], institutions: list[educational_models.EducationalInstitution]
) -> None:
    reset_offer_id_seq()
    national_programs, domains = create_national_programs_and_domains()
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
    provider = create_collective_api_provider(offerer.managedVenues)

    venue_pc_pro = next(v for v in offerer.managedVenues if "PC_PRO" in v.name)
    create_collective_offers_with_different_displayed_status(
        institutions=institutions, domains=domains, venue=venue_pc_pro, provider=None
    )
    create_collective_offer_templates_with_different_displayed_status(domains=domains, venue=venue_pc_pro)

    venue_public_api = next(v for v in offerer.managedVenues if "PUBLIC_API" in v.name)
    create_collective_offers_with_different_displayed_status(
        institutions=institutions, domains=domains, venue=venue_public_api, provider=provider
    )

    # eac_with_addresses_cases
    offerer_for_addresses = next(o for o in offerers if o.name == "eac_with_addresses_cases")
    provider_for_addresses = create_collective_api_provider(offerer_for_addresses.managedVenues)

    venue_pc_pro_for_addresses = next(v for v in offerer_for_addresses.managedVenues if "PC_PRO" in v.name)
    other_venue = offerers_factories.VenueFactory.create(
        name=f"{offerer_for_addresses.name} Autre structure",
        managingOfferer=offerer_for_addresses,
        street="17 boulevard de Lyon",
        city="Strasbourg",
        postalCode="67000",
        latitude=48.57,
        longitude=7.73,
    )

    create_collective_offers_with_different_locations(
        institutions=institutions,
        domains=domains,
        venue=venue_pc_pro_for_addresses,
        other_venue=other_venue,
        provider=None,
    )
    create_collective_offers_with_different_locations(
        institutions=institutions,
        domains=domains,
        venue=venue_pc_pro_for_addresses,
        other_venue=other_venue,
        provider=None,
        with_new_format=True,
    )

    create_collective_offer_templates_with_different_locations(
        domains=domains, venue=venue_pc_pro_for_addresses, other_venue=other_venue
    )
    create_collective_offer_templates_with_different_locations(
        domains=domains, venue=venue_pc_pro_for_addresses, other_venue=other_venue, with_new_format=True
    )

    venue_public_api_for_addresses = next(v for v in offerer_for_addresses.managedVenues if "PUBLIC_API" in v.name)
    create_collective_offers_with_different_locations(
        institutions=institutions,
        domains=domains,
        venue=venue_public_api_for_addresses,
        other_venue=other_venue,
        provider=provider_for_addresses,
    )

    create_collective_offers_with_different_locations(
        institutions=institutions,
        domains=domains,
        venue=venue_public_api_for_addresses,
        other_venue=other_venue,
        provider=provider_for_addresses,
        with_new_format=True,
    )

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
            stock = educational_factories.CollectiveStockFactory.create(
                collectiveOffer__name=f"offer {next(number_iterator)} pour {offerer.name}",
                collectiveOffer__educational_domains=[next(domains_iterator)],
                collectiveOffer__venue=next(venue_iterator),
                collectiveOffer__institution=next(institution_iterator),
                collectiveOffer__nationalProgram=next(national_program_iterator),
                collectiveOffer__bookingEmails=["toto@totoland.com"],
                collectiveOffer__author=user_factory.ProFactory.create(email="eac_1_lieu@example.com"),
                collectiveOffer__formats=[EacFormat.PROJECTION_AUDIOVISUELLE],
                startDatetime=datetime.utcnow() + timedelta(days=60),
            )
            offers.append(stock.collectiveOffer)

        if settings.CREATE_ADAGE_TESTING_DATA:
            # add an offer with and emoji so that ADAGE can check that the encoding works
            institution = (
                db.session.query(educational_models.EducationalInstitution)
                .filter(educational_models.EducationalInstitution.institutionId == "0131251P")
                .one()
            )

            stock = educational_factories.CollectiveStockFactory.create(
                collectiveOffer__name=f"offer {next(number_iterator)} pour {offerer.name} 🍕",
                collectiveOffer__educational_domains=[next(domains_iterator)],
                collectiveOffer__venue=next(venue_iterator),
                collectiveOffer__institution=institution,
                collectiveOffer__nationalProgram=next(national_program_iterator),
                collectiveOffer__bookingEmails=["toto@totoland.com"],
                collectiveOffer__author=user_factory.ProFactory.create(email="eac_1_lieu@example.com"),
                collectiveOffer__formats=[EacFormat.PROJECTION_AUDIOVISUELLE],
                startDatetime=datetime.utcnow() + timedelta(days=60),
            )
            offers.append(stock.collectiveOffer)

    if image_offers:
        for _ in range(size):
            stock = educational_factories.CollectiveStockFactory.create(
                collectiveOffer__name=f"offer {next(number_iterator)} pour {offerer.name} with image",
                collectiveOffer__educational_domains=[next(domains_iterator)],
                collectiveOffer__venue=next(venue_iterator),
                collectiveOffer__institution=next(institution_iterator),
                collectiveOffer__bookingEmails=["toto@totoland.com"],
                startDatetime=datetime.utcnow() + timedelta(days=60),
            )
            add_image_to_offer(stock.collectiveOffer, next(image_iterator))
            offers.append(stock.collectiveOffer)

    if offer_to_teacher:
        institution = (
            db.session.query(educational_models.EducationalInstitution)
            .filter(educational_models.EducationalInstitution.institutionId == "0560071Y")
            .one()
        )

        redactor = (
            db.session.query(educational_models.EducationalRedactor)
            .filter(educational_models.EducationalRedactor.email == "Marianne.Calvayrac@ac-versailles.fr")
            .one_or_none()
        )
        if not redactor:
            redactor = educational_factories.EducationalRedactorFactory.create(
                email="Marianne.Calvayrac@ac-versailles.fr",
                firstName="CALVAYRAC",
                lastName="MARIANNE",
                civility="Mme",
            )
        for _ in range(size):
            stock = educational_factories.CollectiveStockFactory.create(
                collectiveOffer__name=f"offer {next(number_iterator)} pour {offerer.name} to teacher",
                collectiveOffer__educational_domains=[next(domains_iterator)],
                collectiveOffer__venue=next(venue_iterator),
                collectiveOffer__institution=institution,
                collectiveOffer__teacher=redactor,
                collectiveOffer__bookingEmails=["toto@totoland.com"],
                startDatetime=datetime.utcnow() + timedelta(days=60),
            )
            offers.append(stock.collectiveOffer)

    if public_api_offers:
        for _ in range(size):
            stock = educational_factories.CollectiveStockFactory.create(
                collectiveOffer__name=f"offer {next(number_iterator)} pour {offerer.name} public api",
                collectiveOffer__educational_domains=[next(domains_iterator)],
                collectiveOffer__venue=next(venue_iterator),
                collectiveOffer__institution=next(institution_iterator),
                collectiveOffer__nationalProgram=next(national_program_iterator),
                collectiveOffer__interventionArea=[],
                collectiveOffer__provider=provider,
                collectiveOffer__bookingEmails=["toto@totoland.com"],
                startDatetime=datetime.utcnow() + timedelta(days=60),
            )
            offers.append(stock.collectiveOffer)

    if expired_offers:
        for _ in range(size):
            stock = educational_factories.CollectiveStockFactory.create(
                collectiveOffer__name=f"offer {next(number_iterator)} pour {offerer.name} expired",
                collectiveOffer__educational_domains=[next(domains_iterator)],
                collectiveOffer__venue=next(venue_iterator),
                collectiveOffer__institution=next(institution_iterator),
                collectiveOffer__bookingEmails=["toto@totoland.com"],
                bookingLimitDatetime=datetime.utcnow() - timedelta(days=2),
                startDatetime=datetime.utcnow(),
            )
            offers.append(stock.collectiveOffer)

    if pending_offers:
        for _ in range(size):
            educational_factories.CollectiveStockFactory.create(
                collectiveOffer__name=f"offer {next(number_iterator)} pour {offerer.name} pending",
                collectiveOffer__educational_domains=[next(domains_iterator)],
                collectiveOffer__venue=next(venue_iterator),
                collectiveOffer__institution=next(institution_iterator),
                collectiveOffer__validation=OfferValidationStatus.PENDING,
                collectiveOffer__bookingEmails=["toto@totoland.com"],
                startDatetime=datetime.utcnow() + timedelta(days=60),
            )
            offers.append(stock.collectiveOffer)

    if offers_next_year:
        current_year = datetime.utcnow().year
        target_year = current_year + 2 if datetime.utcnow().month >= 9 else current_year + 1
        for _ in range(size):
            stock = educational_factories.CollectiveStockFactory.create(
                collectiveOffer__name=f"offer next year {next(number_iterator)} pour {offerer.name}",
                collectiveOffer__educational_domains=[next(domains_iterator)],
                collectiveOffer__venue=next(venue_iterator),
                collectiveOffer__institution=next(institution_iterator),
                collectiveOffer__bookingEmails=["toto@totoland.com"],
                startDatetime=datetime(target_year, 3, 18),
                bookingLimitDatetime=datetime(target_year, 3, 3),
            )
            offers.append(stock.collectiveOffer)

    if offers_intervention_56:
        for _ in range(size):
            stock = educational_factories.CollectiveStockFactory.create(
                collectiveOffer__name=f"offer {next(number_iterator)} pour {offerer.name} interventionArea 56",
                collectiveOffer__educational_domains=[next(domains_iterator)],
                collectiveOffer__venue=next(venue_iterator),
                collectiveOffer__institution=next(institution_iterator),
                collectiveOffer__interventionArea=["56"],
                collectiveOffer__bookingEmails=["toto@totoland.com"],
                startDatetime=datetime.utcnow() + timedelta(days=60),
            )
            offers.append(stock.collectiveOffer)

    if offers_intervention_91:
        for _ in range(size):
            stock = educational_factories.CollectiveStockFactory.create(
                collectiveOffer__name=f"offer {next(number_iterator)} pour {offerer.name} interventionArea 91",
                collectiveOffer__educational_domains=[next(domains_iterator)],
                collectiveOffer__venue=next(venue_iterator),
                collectiveOffer__institution=next(institution_iterator),
                collectiveOffer__interventionArea=["91"],
                collectiveOffer__bookingEmails=["toto@totoland.com"],
                startDatetime=datetime.utcnow() + timedelta(days=60),
            )
            offers.append(stock.collectiveOffer)

    if basic_templates:
        for _ in range(5):
            template = educational_factories.CollectiveOfferTemplateFactory.create(
                name=f"offer {next(number_iterator)} pour {offerer.name} basic template",
                educational_domains=[next(domains_iterator)],
                venue=next(venue_iterator),
                bookingEmails=["toto@totoland.com"],
                nationalProgram=next(national_program_iterator),
                author=user_factory.ProFactory.create(email="eac_1_lieu@example.com"),
                formats=[EacFormat.PROJECTION_AUDIOVISUELLE],
                # set the offer in school to fill the CLASSROOM adage playlist
                offerVenue={
                    "addressType": educational_models.OfferAddressType.SCHOOL,
                    "venueId": None,
                    "otherAddress": "",
                },
                locationType=educational_models.CollectiveLocationType.SCHOOL,
            )
            templates.append(template)

        if from_templates_offers:
            for template in 4 * [templates[0]] + 1 * [templates[1]]:
                educational_factories.CollectiveStockFactory.create(
                    collectiveOffer__name=f"offer {next(number_iterator)} pour {offerer.name} from template to school",
                    collectiveOffer__educational_domains=[next(domains_iterator)],
                    collectiveOffer__venue=next(venue_iterator),
                    collectiveOffer__template=template,
                    collectiveOffer__institution=next(institution_iterator),
                    collectiveOffer__nationalProgram=next(national_program_iterator),
                    collectiveOffer__bookingEmails=["toto@totoland.com"],
                    startDatetime=datetime.utcnow() + timedelta(days=60),
                )

    if image_template:
        for _ in range(5):
            template = educational_factories.CollectiveOfferTemplateFactory.create(
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
            template = educational_factories.CollectiveOfferTemplateFactory.create(
                name=f"offer {number} pour {offerer.name} template request",
                educational_domains=[next(domains_iterator)],
                venue=next(venue_iterator),
                bookingEmails=["toto@totoland.com"],
            )
            educational_factories.CollectiveOfferRequestFactory.create(
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


def create_collective_offers_with_different_displayed_status(
    *,
    institutions: list[educational_models.EducationalInstitution],
    domains: list[educational_models.EducationalDomain],
    venue: offerers_models.Venue,
    provider: providers_models.Provider | None,
) -> None:
    current_ansco = (
        db.session.query(educational_models.EducationalYear)
        .filter(
            educational_models.EducationalYear.beginningDate <= datetime.utcnow(),
            educational_models.EducationalYear.expirationDate >= datetime.utcnow(),
        )
        .one()
    )
    domains_iterator = cycle(domains)
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
            "startDatetime": in_four_weeks,
            "endDatetime": in_four_weeks,
        },
        "Athènes": {
            "bookingLimitDatetime": two_weeks_ago,
            "startDatetime": in_two_weeks,
            "endDatetime": in_two_weeks,
        },
        "Berlin": {
            "bookingLimitDatetime": four_weeks_ago,
            "startDatetime": two_weeks_ago,
            "endDatetime": in_two_weeks,
        },
        "Bratislava": {
            "bookingLimitDatetime": four_weeks_ago,
            "startDatetime": four_weeks_ago,
            "endDatetime": four_weeks_ago,
        },
        # with a pending booking
        "Bruxelles": {
            "bookingLimitDatetime": in_two_weeks,
            "startDatetime": in_four_weeks,
            "endDatetime": in_four_weeks,
            "bookingFactory": educational_factories.PendingCollectiveBookingFactory,
        },
        "Bucarest": {
            "bookingLimitDatetime": two_weeks_ago,
            "startDatetime": in_two_weeks,
            "endDatetime": in_two_weeks,
            "bookingFactory": educational_factories.PendingCollectiveBookingFactory,
        },
        # with a cancelled booking due to expiration
        "Budapest": {
            "bookingLimitDatetime": two_weeks_ago,
            "startDatetime": in_two_weeks,
            "endDatetime": in_two_weeks,
            "bookingFactory": educational_factories.CancelledCollectiveBookingFactory,
            "cancellationReason": educational_models.CollectiveBookingCancellationReasons.EXPIRED,
            "confirmationDate": None,
        },
        "Copenhague": {
            "bookingLimitDatetime": four_weeks_ago,
            "startDatetime": two_weeks_ago,
            "endDatetime": in_two_weeks,
            "bookingFactory": educational_factories.CancelledCollectiveBookingFactory,
            "cancellationReason": educational_models.CollectiveBookingCancellationReasons.EXPIRED,
            "confirmationDate": None,
        },
        # with a confirmed booking
        "Dublin": {
            "bookingLimitDatetime": in_two_weeks,
            "startDatetime": in_four_weeks,
            "endDatetime": in_four_weeks,
            "bookingFactory": educational_factories.ConfirmedCollectiveBookingFactory,
        },
        "Helsinki": {
            "bookingLimitDatetime": two_weeks_ago,
            "startDatetime": in_two_weeks,
            "endDatetime": in_two_weeks,
            "bookingFactory": educational_factories.ConfirmedCollectiveBookingFactory,
        },
        "La Valette": {
            "bookingLimitDatetime": four_weeks_ago,
            "startDatetime": two_weeks_ago,
            "endDatetime": in_two_weeks,
            "bookingFactory": educational_factories.ConfirmedCollectiveBookingFactory,
        },
        "Lisbonne": {
            "bookingLimitDatetime": four_weeks_ago,
            "startDatetime": yesterday,
            "endDatetime": yesterday,
            "bookingFactory": educational_factories.ConfirmedCollectiveBookingFactory,
        },
        # with a used booking
        "Ljubljana": {
            "bookingLimitDatetime": four_weeks_ago,
            "startDatetime": four_weeks_ago,
            "endDatetime": four_weeks_ago,
            "bookingFactory": educational_factories.UsedCollectiveBookingFactory,
        },
        "Luxembourg": {
            "bookingLimitDatetime": four_weeks_ago,
            "startDatetime": four_weeks_ago,
            "endDatetime": four_weeks_ago,
            "bookingFactory": educational_factories.ReimbursedCollectiveBookingFactory,
        },
        # with a cancelled booking
        "Madrid": {
            "bookingLimitDatetime": in_two_weeks,
            "startDatetime": in_four_weeks,
            "endDatetime": in_four_weeks,
            "bookingFactory": educational_factories.CancelledCollectiveBookingFactory,
            "cancellationReason": educational_models.CollectiveBookingCancellationReasons.OFFERER,
        },
        "Nicosie": {
            "bookingLimitDatetime": two_weeks_ago,
            "startDatetime": in_two_weeks,
            "endDatetime": in_two_weeks,
            "bookingFactory": educational_factories.CancelledCollectiveBookingFactory,
            "cancellationReason": educational_models.CollectiveBookingCancellationReasons.OFFERER,
        },
        "Paris": {
            "bookingLimitDatetime": four_weeks_ago,
            "startDatetime": two_weeks_ago,
            "endDatetime": in_two_weeks,
            "bookingFactory": educational_factories.CancelledCollectiveBookingFactory,
            "cancellationReason": educational_models.CollectiveBookingCancellationReasons.OFFERER,
        },
        "Prague": {
            "bookingLimitDatetime": four_weeks_ago,
            "startDatetime": four_weeks_ago,
            "endDatetime": four_weeks_ago,
            "bookingFactory": educational_factories.CancelledCollectiveBookingFactory,
            "cancellationReason": educational_models.CollectiveBookingCancellationReasons.OFFERER,
        },
        # inactive
        "Londres": {
            "isActive": False,
            "bookingLimitDatetime": in_two_weeks,
            "startDatetime": in_four_weeks,
            "endDatetime": in_four_weeks,
        },
        # with a different end date than the start date
        "Reykjavik": {
            "bookingLimitDatetime": four_weeks_ago,
            "startDatetime": yesterday,
            "endDatetime": tomorrow,
            "bookingFactory": educational_factories.ConfirmedCollectiveBookingFactory,
        },
        # draft
        "Rome": {
            "validation": OfferValidationStatus.DRAFT,
            "bookingLimitDatetime": in_two_weeks,
            "startDatetime": in_four_weeks,
            "endDatetime": in_four_weeks,
        },
        # pending
        "Sarajevo": {
            "validation": OfferValidationStatus.PENDING,
            "bookingLimitDatetime": in_two_weeks,
            "startDatetime": in_four_weeks,
            "endDatetime": in_four_weeks,
        },
        # rejected
        "Sofia": {
            "validation": OfferValidationStatus.REJECTED,
            "bookingLimitDatetime": in_two_weeks,
            "startDatetime": in_four_weeks,
            "endDatetime": in_four_weeks,
        },
        # archived
        "Stockholm": {
            "dateArchived": yesterday,
            "isActive": False,
            "bookingLimitDatetime": in_two_weeks,
            "startDatetime": in_four_weeks,
            "endDatetime": in_four_weeks,
        },
    }

    for city, attributes in options.items():
        booking_factory = attributes.get("bookingFactory")
        start_datetime = attributes["startDatetime"]
        end_datetime = attributes["endDatetime"]
        booking_limit_datetime = attributes["bookingLimitDatetime"]
        institution = next(institution_iterator)

        stock = educational_factories.CollectiveStockFactory.create(
            collectiveOffer__name=f"La culture à {city}{' (public api)' if provider is not None else ''}",
            collectiveOffer__educational_domains=[next(domains_iterator)],
            collectiveOffer__venue=venue,
            collectiveOffer__validation=attributes.get("validation", OfferValidationStatus.APPROVED),
            collectiveOffer__isActive=attributes.get("isActive", True),
            collectiveOffer__dateArchived=attributes.get("dateArchived"),
            collectiveOffer__bookingEmails=["toto@totoland.com"],
            collectiveOffer__institution=institution,
            collectiveOffer__formats=[EacFormat.PROJECTION_AUDIOVISUELLE],
            collectiveOffer__provider=provider,
            startDatetime=start_datetime,
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


def create_collective_offer_templates_with_different_displayed_status(
    *, domains: list[educational_models.EducationalDomain], venue: offerers_models.Venue
) -> None:
    domains_iterator = cycle(domains)

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
        educational_factories.CollectiveOfferTemplateFactory.create(
            name=f"The culture in {state}",
            validation=attributes["validation"],
            rejectionReason=attributes.get("rejectionReason"),
            isActive=attributes.get("isActive", True),
            dateRange=attributes.get("dateRange"),
            dateArchived=attributes.get("dateArchived"),
            dateCreated=two_weeks_ago,  # necessary to pass constraint template_dates_non_empty_daterange
            venue=venue,
            educational_domains=[next(domains_iterator)],
            bookingEmails=["toto@totoland.com"],
            formats=[EacFormat.PROJECTION_AUDIOVISUELLE],
        )


def _set_offer_location_columns(
    offer: educational_models.CollectiveOffer | educational_models.CollectiveOfferTemplate,
    location_option: LocationOption,
    offerer: offerers_models.Offerer,
) -> None:
    offer.locationType = location_option.get("locationType")
    offer.locationComment = location_option.get("locationComment")

    oa_label = f"OA pour l'offre {offer.name}"
    if isinstance(offer, educational_models.CollectiveOfferTemplate):
        oa_label += " (template)"

    offer.offererAddress = _get_or_create_offerer_address(
        location_option=location_option, managing_offerer=offerer, oa_label=oa_label
    )


def create_collective_offers_with_different_locations(
    *,
    institutions: list[educational_models.EducationalInstitution],
    domains: list[educational_models.EducationalDomain],
    venue: offerers_models.Venue,
    other_venue: offerers_models.Venue,
    provider: providers_models.Provider | None,
    with_new_format: bool = False,
) -> None:
    domains_iterator = cycle(domains)
    institution_iterator = cycle(institutions)

    for location_option in get_location_options(venue=venue, other_venue=other_venue):
        name = location_option["name"]
        name = f"{name}{' (avec OA)' if with_new_format else ''}{' (public api)' if provider is not None else ''}"

        offer_venue = location_option["offerVenue"]

        collective_stock = educational_factories.CollectiveStockFactory.create(
            collectiveOffer__name=name,
            collectiveOffer__educational_domains=[next(domains_iterator)],
            collectiveOffer__venue=venue,
            collectiveOffer__bookingEmails=["toto@totoland.com"],
            collectiveOffer__institution=next(institution_iterator),
            collectiveOffer__formats=[EacFormat.PROJECTION_AUDIOVISUELLE],
            collectiveOffer__provider=provider,
            collectiveOffer__offerVenue=offer_venue,
            collectiveOffer__interventionArea=location_option.get("interventionArea", []),
        )

        if with_new_format:
            _set_offer_location_columns(
                offer=collective_stock.collectiveOffer, location_option=location_option, offerer=venue.managingOfferer
            )


def create_collective_offer_templates_with_different_locations(
    *,
    domains: list[educational_models.EducationalDomain],
    venue: offerers_models.Venue,
    other_venue: offerers_models.Venue,
    with_new_format: bool = False,
) -> None:
    domains_iterator = cycle(domains)

    for location_option in get_location_options(venue=venue, other_venue=other_venue):
        name = location_option["name"]
        name = f"{name}{' (avec OA)' if with_new_format else ''}"

        offer_venue = location_option["offerVenue"]
        collective_offer_template = educational_factories.CollectiveOfferTemplateFactory.create(
            name=name,
            venue=venue,
            educational_domains=[next(domains_iterator)],
            bookingEmails=["toto@totoland.com"],
            formats=[EacFormat.PROJECTION_AUDIOVISUELLE],
            offerVenue=offer_venue,
            interventionArea=location_option.get("interventionArea", []),
        )

        if with_new_format:
            _set_offer_location_columns(
                offer=collective_offer_template, location_option=location_option, offerer=venue.managingOfferer
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
    current_ansco = (
        db.session.query(educational_models.EducationalYear)
        .filter(
            educational_models.EducationalYear.beginningDate <= datetime.utcnow(),
            educational_models.EducationalYear.expirationDate >= datetime.utcnow(),
        )
        .one()
    )
    institution_iterator = cycle(institutions)
    number_iterator = count()
    domains_iterator = cycle(domains)
    venue_iterator = cycle(offerer.managedVenues)
    size = 5 if not settings.CREATE_ADAGE_TESTING_DATA else len(institutions)
    if pending_booking:
        for _i in range(size):
            educational_factories.CollectiveBookingFactory.create(
                collectiveStock__collectiveOffer__name=f"PENDING offer {next(number_iterator)} pour {offerer.name}",
                collectiveStock__collectiveOffer__venue=next(venue_iterator),
                collectiveStock__collectiveOffer__educational_domains=[next(domains_iterator)],
                collectiveStock__bookingLimitDatetime=datetime.utcnow() + timedelta(15),
                collectiveStock__startDatetime=datetime.utcnow() + timedelta(days=20),
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
            educational_factories.CollectiveBookingFactory.create(
                collectiveStock__collectiveOffer__name=f"BOOKED offer {next(number_iterator)} pour {offerer.name}",
                collectiveStock__collectiveOffer__venue=next(venue_iterator),
                collectiveStock__collectiveOffer__educational_domains=[next(domains_iterator)],
                collectiveStock__startDatetime=datetime.utcnow() + timedelta(days=20),
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
            educational_factories.CollectiveBookingFactory.create(
                collectiveStock__collectiveOffer__name=f"CONFIRMED offer {next(number_iterator)} pour {offerer.name}",
                collectiveStock__collectiveOffer__venue=next(venue_iterator),
                collectiveStock__collectiveOffer__educational_domains=[next(domains_iterator)],
                collectiveStock__startDatetime=datetime.utcnow() + timedelta(days=20),
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
            booking = educational_factories.CollectiveBookingFactory.create(
                collectiveStock__collectiveOffer__name=f"USED offer {next(number_iterator)} pour {offerer.name}",
                collectiveStock__collectiveOffer__venue=next(venue_iterator),
                collectiveStock__collectiveOffer__educational_domains=[next(domains_iterator)],
                collectiveStock__startDatetime=datetime.utcnow()
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
            finance_factories.UsedBookingFinanceEventFactory.create(collectiveBooking=booking)
    if reimbursed_booking:
        for _i in range(size):
            booking = educational_factories.CollectiveBookingFactory.create(
                collectiveStock__collectiveOffer__name=f"REIMBURSED offer {next(number_iterator)} pour {offerer.name}",
                collectiveStock__collectiveOffer__venue=next(venue_iterator),
                collectiveStock__collectiveOffer__educational_domains=[next(domains_iterator)],
                collectiveStock__startDatetime=datetime.utcnow() - timedelta(days=15),
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

            finance_factories.CollectivePricingFactory.create(
                status=finance_models.PricingStatus.INVOICED, collectiveBooking=booking
            )
    if cancelled_ac:
        for _i in range(size):
            educational_factories.CollectiveBookingFactory.create(
                collectiveStock__collectiveOffer__name=f"CANCELLED BY AC offer {next(number_iterator)} pour {offerer.name}",
                collectiveStock__collectiveOffer__venue=next(venue_iterator),
                collectiveStock__collectiveOffer__educational_domains=[next(domains_iterator)],
                collectiveStock__startDatetime=datetime.utcnow() + timedelta(days=20),
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
            educational_factories.CollectiveBookingFactory.create(
                collectiveStock__collectiveOffer__name=f"CANCELLED BY EPLE offer {next(number_iterator)} pour {offerer.name}",
                collectiveStock__collectiveOffer__venue=next(venue_iterator),
                collectiveStock__collectiveOffer__educational_domains=[next(domains_iterator)],
                collectiveStock__startDatetime=datetime.utcnow() + timedelta(days=20),
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
            educational_factories.CollectiveBookingFactory.create(
                collectiveStock__collectiveOffer__name=f"CANCELLED AUTOMATICALLY offer {next(number_iterator)} pour {offerer.name}",
                collectiveStock__collectiveOffer__venue=next(venue_iterator),
                collectiveStock__collectiveOffer__educational_domains=[next(domains_iterator)],
                collectiveStock__startDatetime=datetime.utcnow() + timedelta(days=20),
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


def create_national_programs_and_domains() -> tuple[
    list[educational_models.NationalProgram], list[educational_models.EducationalDomain]
]:
    college_au_cinema = educational_factories.NationalProgramFactory.create(name="Collège au cinéma")
    lyceens_apprentis_au_cinema = educational_factories.NationalProgramFactory.create(
        name="Lycéens et apprentis au cinéma"
    )
    jeunes_en_librairie = educational_factories.NationalProgramFactory.create(name="Jeunes en librairie")
    olympiade_culturelle = educational_factories.NationalProgramFactory.create(
        name="Olympiade culturelle de PARIS 2024", isActive=False
    )
    prado = educational_factories.NationalProgramFactory.create(name="PRADO (plan national de la DILCRAH)")
    national_programs = [
        college_au_cinema,
        lyceens_apprentis_au_cinema,
        jeunes_en_librairie,
        olympiade_culturelle,
        prado,
    ]

    domains = [
        educational_factories.EducationalDomainFactory.create(
            name="Architecture", id=1, nationalPrograms=[olympiade_culturelle, prado]
        ),
        educational_factories.EducationalDomainFactory.create(
            name="Arts du cirque et arts de la rue", id=2, nationalPrograms=[olympiade_culturelle, prado]
        ),
        educational_factories.EducationalDomainFactory.create(
            name="Arts numériques", id=4, nationalPrograms=[olympiade_culturelle, prado]
        ),
        educational_factories.EducationalDomainFactory.create(
            name="Arts visuels, arts plastiques, arts appliqués", id=5, nationalPrograms=[olympiade_culturelle, prado]
        ),
        educational_factories.EducationalDomainFactory.create(
            name="Cinéma, audiovisuel",
            id=6,
            nationalPrograms=[college_au_cinema, lyceens_apprentis_au_cinema, prado],
        ),
        educational_factories.EducationalDomainFactory.create(
            name="Culture scientifique, technique et industrielle",
            id=7,
            nationalPrograms=[olympiade_culturelle, prado],
        ),
        educational_factories.EducationalDomainFactory.create(
            name="Danse", id=8, nationalPrograms=[olympiade_culturelle, prado]
        ),
        educational_factories.EducationalDomainFactory.create(
            name="Design", id=9, nationalPrograms=[olympiade_culturelle, prado]
        ),
        educational_factories.EducationalDomainFactory.create(
            name="Développement durable", id=10, nationalPrograms=[olympiade_culturelle, prado]
        ),
        educational_factories.EducationalDomainFactory.create(
            name="Univers du livre, de la lecture et des écritures",
            id=11,
            nationalPrograms=[jeunes_en_librairie, prado],
        ),
        educational_factories.EducationalDomainFactory.create(
            name="Musique", id=12, nationalPrograms=[olympiade_culturelle, prado]
        ),
        educational_factories.EducationalDomainFactory.create(
            name="Patrimoine", id=13, nationalPrograms=[olympiade_culturelle, prado]
        ),
        educational_factories.EducationalDomainFactory.create(
            name="Photographie", id=14, nationalPrograms=[olympiade_culturelle, prado]
        ),
        educational_factories.EducationalDomainFactory.create(
            name="Théâtre, expression dramatique, marionnettes", id=15, nationalPrograms=[olympiade_culturelle, prado]
        ),
        educational_factories.EducationalDomainFactory.create(
            name="Bande dessinée", id=16, nationalPrograms=[olympiade_culturelle, prado]
        ),
        educational_factories.EducationalDomainFactory.create(
            name="Média et information", id=17, nationalPrograms=[olympiade_culturelle, prado]
        ),
        educational_factories.EducationalDomainFactory.create(
            name="Mémoire", id=18, nationalPrograms=[olympiade_culturelle, prado]
        ),
    ]

    return national_programs, domains


def reset_offer_id_seq() -> None:
    if settings.DATABASE_HAS_SPECIFIC_ROLES:
        db.session.execute(sa.text("SELECT reset_sequence('collective_offer_id_seq')"))
        db.session.execute(sa.text("SELECT reset_sequence('collective_offer_template_id_seq')"))
    else:
        db.session.execute(sa.text("ALTER SEQUENCE collective_offer_id_seq RESTART WITH 1"))
        db.session.execute(sa.text("ALTER SEQUENCE collective_offer_template_id_seq RESTART WITH 1"))
