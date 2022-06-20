from dataclasses import dataclass
import datetime

from pcapi.core.educational import models as educational_models
import pcapi.core.educational.factories as educational_factories
from pcapi.core.offerers import models as offerers_models
import pcapi.core.offerers.factories as offerers_factories
from pcapi.utils.human_ids import humanize


@dataclass
class StockData:
    name: str
    price: int
    timedelta: int
    numberOfTickets: int
    addressType: str
    otherAddress: str


@dataclass
class TemplateOfferData:
    name: str
    addressType: str
    otherAddress: str


FAKE_STOCK_DATA = [
    StockData(
        name="Visite de l'Abbaye Royale + Musée d'art moderne + Nocturne Les étoiles de Fontevraud",
        price=1000,
        timedelta=20,
        numberOfTickets=10,
        addressType="other",
        otherAddress="1 rue des polissons, Paris 75017",
    ),
    StockData(
        name="Visite de la mine Gabe Gottes",
        price=800,
        timedelta=18,
        numberOfTickets=30,
        addressType="school",
        otherAddress="",
    ),
    StockData(
        name="Clued'au Château",
        price=1200,
        timedelta=15,
        numberOfTickets=25,
        addressType="other",
        otherAddress="1 rue des polissons, Paris 75017",
    ),
    StockData(
        name="Visitez le Panthéon, Chef d'œuvre de l'architecte Soufflot",
        price=1200,
        timedelta=22,
        numberOfTickets=20,
        addressType="offererVenue",
        otherAddress="",
    ),
    StockData(
        name="Arc de Triomphe : embrassez tout Paris du haut du monument emblématique",
        price=1200,
        timedelta=25,
        numberOfTickets=5,
        addressType="other",
        otherAddress="1 rue des polissons, Paris 75017",
    ),
    StockData(
        name="Site archéologique : un des plus vieux villages d'Europe (2500 ans avant JC)",
        price=1200,
        timedelta=27,
        numberOfTickets=40,
        addressType="school",
        otherAddress="",
    ),
    StockData(
        name="Spectacle nocturne Lux Salina",
        price=600,
        timedelta=8,
        numberOfTickets=50,
        addressType="other",
        otherAddress="1 rue des polissons, Paris 75017",
    ),
    StockData(
        name="Découverte des métiers du patrimoine: Restaurateur(trice) Décorateur(trice), Doreur(reuse)",
        price=900,
        timedelta=5,
        numberOfTickets=15,
        addressType="offererVenue",
        otherAddress="",
    ),
    StockData(
        name="Entrée 'Spectacle aux Étoiles' avec conférence 'La Lune... connue et inconnue'",
        price=860,
        timedelta=9,
        numberOfTickets=100,
        addressType="school",
        otherAddress="",
    ),
    StockData(
        name="Le Grognement de la voie lactée - Bonn Park/Paul Moulin, Maia Sandoz",
        price=400,
        timedelta=5,
        numberOfTickets=10,
        addressType="school",
        otherAddress="",
    ),
    StockData(
        name="Baal - Bertolt Brecht / Armel Roussel",
        price=200,
        timedelta=2,
        numberOfTickets=80,
        addressType="offererVenue",
        otherAddress="",
    ),
    StockData(
        name="Intervention Estampe en Partage - Collège Les Célestins de Vichy",
        price=100,
        timedelta=18,
        numberOfTickets=12,
        addressType="offererVenue",
        otherAddress="",
    ),
    StockData(
        name="Sensibilisation au jazz par une approche vivante en lien avec 'Anglet Jazz Festival'",
        price=150,
        timedelta=10,
        numberOfTickets=50,
        addressType="offererVenue",
        otherAddress="",
    ),
    StockData(
        name="L'art de la mosaïque sur la colline de Fourvière",
        price=150,
        timedelta=10,
        numberOfTickets=50,
        addressType="offererVenue",
        otherAddress="",
    ),
    StockData(
        name="À la découverte de la lignée évolutive humaine",
        price=150,
        timedelta=10,
        numberOfTickets=50,
        addressType="offererVenue",
        otherAddress="",
    ),
]

PASSED_STOCK_DATA: list[StockData] = [
    StockData(
        name="Passée: Spectacle nocturne Lux Salina",
        price=600,
        timedelta=8,
        numberOfTickets=50,
        addressType="other",
        otherAddress="1 rue des polissons, Paris 75017",
    ),
    StockData(
        name="Passée: Découverte des métiers du patrimoine: Restaurateur(trice) Décorateur(trice), Doreur(reuse)",
        price=900,
        timedelta=5,
        numberOfTickets=15,
        addressType="offererVenue",
        otherAddress="",
    ),
    StockData(
        name="Passée: Entrée 'Spectacle aux Étoiles' avec conférence 'La Lune... connue et inconnue'",
        price=860,
        timedelta=9,
        numberOfTickets=100,
        addressType="school",
        otherAddress="",
    ),
]

TEMPLATE_OFFERS_DATA = [
    TemplateOfferData(
        name="Visite du studio d'enregistrement de l'EAC collectif",
        addressType="offererVenue",
        otherAddress="",
    ),
    TemplateOfferData(
        name="Plongez au coeur de la pâtisserie du 12 rue Duhesme",
        addressType="other",
        otherAddress="12 rue Duhesme, Paris 75018",
    ),
    TemplateOfferData(
        name="Une offre vitrine pas comme les autres",
        addressType="school",
        otherAddress="",
    ),
]
ADDRESSES = [
    {"department": "04", "postalCode": "04400", "city": "Barcelonnette"},
    {"department": "14", "postalCode": "14000", "city": "Caen"},
    {"department": "44", "postalCode": "44119", "city": "Treillières"},
    {"department": "52", "postalCode": "52300", "city": "Joinville"},
    {"department": "71", "postalCode": "71400", "city": "Autun"},
    {"department": "78", "postalCode": "78646", "city": "Versailles"},
    {"department": "83", "postalCode": "83230", "city": "Bormes-Les-Mimosas"},
    {"department": "85", "postalCode": "85350", "city": "L'île-d'Yeu"},
    {"department": "971", "postalCode": "97140", "city": "Marie-Galante"},
    {"department": "974", "postalCode": "97410", "city": "Saint-Benoît"},
]


def create_industrial_educational_bookings() -> None:
    create_educational_domains()
    educational_current_year = educational_factories.EducationalYearFactory()
    educational_next_year = educational_factories.EducationalYearFactory()

    educational_factories.EducationalInstitutionFactory.create_batch(20)

    educational_institutions = [
        educational_factories.EducationalInstitutionFactory(institutionId="0780032L"),
        educational_factories.EducationalInstitutionFactory(institutionId="0781839A"),
        educational_factories.EducationalInstitutionFactory(institutionId="0290047U"),
        educational_factories.EducationalInstitutionFactory(institutionId="0290198H"),
        educational_factories.EducationalInstitutionFactory(institutionId="0910620E"),
        educational_factories.EducationalInstitutionFactory(
            institutionId="0560071Y",
            email=None,
            phoneNumber=None,
        ),
    ]
    offerer_with_right_siren = offerers_factories.CollectiveOffererFactory(
        siren="950469494",
        name="Bonne structure pour l'EAC (siren)",
    )
    venues = []
    for i in range(0, 3):
        venues.append(
            offerers_factories.CollectiveVenueFactory(
                name=f"[EAC] Opéra Royal de Versailles - Salle {i}",
                siret=f"9504694940002{i}",
                managingOfferer=offerer_with_right_siren,
                adageId=None,
            )
        )

    cnl_like_offerer = offerers_factories.CollectiveOffererFactory(name="[EAC] Structure factice CNL")
    for i in range(0, 3):
        venues.append(
            offerers_factories.CollectiveVenueFactory(
                siret=None,
                managingOfferer=cnl_like_offerer,
                name=f"[EAC] Lieux factice du CNL {i}",
                comment="Ce lieu est un lieu fictif créé pour les tests de l'EAC",
            )
        )

    educational_redactor = educational_factories.EducationalRedactorFactory(email="compte.test@education.gouv.fr")

    for address in ADDRESSES:
        venues.append(
            offerers_factories.CollectiveVenueFactory(
                departementCode=address["department"],
                city=address["city"],
                postalCode=address["postalCode"],
            )
        )

    for venue in venues:
        offerers_factories.UserOffererFactory(validationToken=None, offerer=venue.managingOfferer)

    deposits = []
    for educational_institution in educational_institutions:
        deposits.append(
            educational_factories.EducationalDepositFactory(
                educationalInstitution=educational_institution,
                educationalYear=educational_current_year,
                amount=40000,
            )
        )
        deposits.append(
            educational_factories.EducationalDepositFactory(
                educationalInstitution=educational_institution,
                educationalYear=educational_next_year,
                amount=50000,
                isFinal=False,
            )
        )

    now = datetime.datetime.utcnow()
    stocks: list[educational_models.CollectiveStock] = []
    passed_stocks: list[educational_models.CollectiveStock] = []
    next_year_stocks: list[educational_models.CollectiveStock] = []

    iterable_venues = iter(venues)
    for stock_data in FAKE_STOCK_DATA:
        try:
            venue = next(iterable_venues)
        except StopIteration:
            iterable_venues = iter(venues)
            venue = next(iterable_venues)
        stocks.append(_create_collective_stock(stock_data, now, venue, 2, is_passed=False)[0])

    for stock_data in PASSED_STOCK_DATA:
        try:
            venue = next(iterable_venues)
        except StopIteration:
            iterable_venues = iter(venues)
            venue = next(iterable_venues)
        passed_stocks.append(_create_collective_stock(stock_data, now, venue, 2, is_passed=True)[0])

    for stock_data in FAKE_STOCK_DATA:
        try:
            venue = next(iterable_venues)
        except StopIteration:
            iterable_venues = iter(venues)
            venue = next(iterable_venues)
        next_year_stocks.append(
            _create_collective_stock(stock_data, educational_next_year.beginningDate, venue, 2, is_passed=False)[0]
        )

    iterable_institutions = iter(educational_institutions)
    for stock in stocks:
        try:
            educational_institution = next(iterable_institutions)
        except StopIteration:
            iterable_institutions = iter(educational_institutions)
            educational_institution = next(iterable_institutions)

        educational_factories.PendingCollectiveBookingFactory(
            educationalRedactor=educational_redactor,
            educationalInstitution=educational_institution,
            educationalYear=educational_current_year,
            collectiveStock=stock,
        )
        educational_factories.CancelledCollectiveBookingFactory(
            educationalRedactor=educational_redactor,
            educationalInstitution=educational_institution,
            educationalYear=educational_current_year,
            collectiveStock=stock,
        )

    for stock in passed_stocks:
        try:
            educational_institution = next(iterable_institutions)
        except StopIteration:
            iterable_institutions = iter(educational_institutions)
            educational_institution = next(iterable_institutions)

        educational_factories.UsedCollectiveBookingFactory(
            educationalRedactor=educational_redactor,
            educationalInstitution=educational_institution,
            educationalYear=educational_current_year,
            confirmationLimitDate=stock.beginningDatetime - datetime.timedelta(days=10),
            cancellationLimitDate=stock.beginningDatetime - datetime.timedelta(days=5),
            dateUsed=now - datetime.timedelta(8),
            collectiveStock=stock,
            collectiveStock__beginningDatetime=now - datetime.timedelta(8),
        )

    iterable_institutions = iter(educational_institutions)
    for next_year_stock in next_year_stocks:
        try:
            educational_institution = next(iterable_institutions)
        except StopIteration:
            iterable_institutions = iter(educational_institutions)
            educational_institution = next(iterable_institutions)

        educational_factories.PendingCollectiveBookingFactory(
            educationalRedactor=educational_redactor,
            educationalInstitution=educational_institution,
            educationalYear=educational_next_year,
            confirmationLimitDate=now + datetime.timedelta(days=30),
            collectiveStock=next_year_stock,
        )

    for template_data in TEMPLATE_OFFERS_DATA:
        _create_collective_offer_template(template_data, venue)


def _create_collective_stock(
    stock_data: StockData,
    now: datetime.datetime,
    venue: offerers_models.Venue,
    number_of_stocks: int = 2,
    is_passed: bool = False,
) -> list[educational_models.CollectiveStock]:
    timedelta = int(stock_data.timedelta)

    if is_passed:
        beginningDatetime = now - datetime.timedelta(days=timedelta)
    else:
        beginningDatetime = now + datetime.timedelta(days=timedelta)

    return educational_factories.CollectiveStockFactory.create_batch(
        number_of_stocks,
        price=stock_data.price,
        beginningDatetime=beginningDatetime,
        numberOfTickets=stock_data.numberOfTickets,
        collectiveOffer__durationMinutes=60,
        collectiveOffer__description="Une description multi-lignes.\nUn lien en description ? https://youtu.be/dQw4w9WgXcQ\n Un email ? mon.email@example.com",
        collectiveOffer__name=stock_data.name,
        collectiveOffer__venue=venue,
        collectiveOffer__students=[
            educational_models.StudentLevels.CAP1,
            educational_models.StudentLevels.CAP2,
            educational_models.StudentLevels.GENERAL1,
            educational_models.StudentLevels.GENERAL2,
        ],
        collectiveOffer__offerVenue={
            "addressType": stock_data.addressType,
            "otherAddress": stock_data.otherAddress,
            "venueId": humanize(venue.id),
        },
        collectiveOffer__contactEmail="miss.rond@point.com",
        collectiveOffer__contactPhone="01010100101",
        collectiveOffer__motorDisabilityCompliant=True,
        collectiveOffer__visualDisabilityCompliant=True,
    )


def _create_collective_offer_template(
    offer_data: TemplateOfferData,
    venue: offerers_models.Venue,
) -> None:
    educational_factories.CollectiveOfferTemplateFactory(
        name=offer_data.name,
        durationMinutes=60,
        description="Une description multi-lignes.\nUn lien en description ? https://youtu.be/dQw4w9WgXcQ\n Un email ?",
        venue=venue,
        students=[
            educational_models.StudentLevels.CAP1,
            educational_models.StudentLevels.GENERAL1,
        ],
        offerVenue={
            "addressType": offer_data.addressType,
            "otherAddress": offer_data.otherAddress,
            "venueId": humanize(venue.id),
        },
        contactEmail="miss.rond@point.com",
        contactPhone="01010100101",
        motorDisabilityCompliant=True,
        visualDisabilityCompliant=True,
    )


def create_educational_domains() -> None:
    educational_factories.EducationalDomainFactory(name="Architecture")
    educational_factories.EducationalDomainFactory(name="Arts du cirque et arts de la rue")
    educational_factories.EducationalDomainFactory(name="Gastronomie et arts du goût")
    educational_factories.EducationalDomainFactory(name="Arts numériques")
    educational_factories.EducationalDomainFactory(name="Arts visuels, arts plastiques, arts appliqués")
    educational_factories.EducationalDomainFactory(name="Cinéma, audiovisuel")
    educational_factories.EducationalDomainFactory(name="Culture scientifique, technique et industrielle")
    educational_factories.EducationalDomainFactory(name="Danse")
    educational_factories.EducationalDomainFactory(name="Design")
    educational_factories.EducationalDomainFactory(name="Développement durable")
    educational_factories.EducationalDomainFactory(name="Univers du livre, de la lecture et des écritures")
    educational_factories.EducationalDomainFactory(name="Musique")
    educational_factories.EducationalDomainFactory(name="Patrimoine, mémoire, archéologie")
    educational_factories.EducationalDomainFactory(name="Photographie")
    educational_factories.EducationalDomainFactory(name="Théâtre, expression dramatique, marionnettes")
    educational_factories.EducationalDomainFactory(name="Bande dessinée")
    educational_factories.EducationalDomainFactory(name="Média et information")
