import datetime
from typing import Union

from pcapi.core.bookings.factories import EducationalBookingFactory
from pcapi.core.bookings.factories import UsedEducationalBookingFactory
from pcapi.core.bookings.models import BookingStatus
from pcapi.core.educational import models as educational_models
import pcapi.core.educational.factories as educational_factories
from pcapi.core.offerers import models as offerers_models
import pcapi.core.offerers.factories as offerers_factories
from pcapi.core.offers.factories import EducationalEventStockFactory
from pcapi.models.feature import FeatureToggle
from pcapi.utils.human_ids import humanize


FAKE_STOCK_DATA: list[dict[str, Union[str, int]]] = [
    {
        "name": "Visite de l'Abbaye Royale + Musée d'art moderne + Nocturne Les étoiles de Fontevraud",
        "price": 1000,
        "timedelta": 20,
        "numberOfTickets": 10,
        "addressType": "other",
        "otherAddress": "1 rue des polissons, Paris 75017",
    },
    {
        "name": "Visite de la mine Gabe Gottes",
        "price": 800,
        "timedelta": 18,
        "numberOfTickets": 30,
        "addressType": "school",
        "otherAddress": "",
    },
    {
        "name": "Clued'au Château",
        "price": 1200,
        "timedelta": 15,
        "numberOfTickets": 25,
        "addressType": "other",
        "otherAddress": "1 rue des polissons, Paris 75017",
    },
    {
        "name": "Visitez le Panthéon, Chef d'œuvre de l'architecte Soufflot",
        "price": 1200,
        "timedelta": 22,
        "numberOfTickets": 20,
        "addressType": "offererVenue",
        "otherAddress": "",
    },
    {
        "name": "Arc de Triomphe : embrassez tout Paris du haut du monument emblématique",
        "price": 1200,
        "timedelta": 25,
        "numberOfTickets": 5,
        "addressType": "other",
        "otherAddress": "1 rue des polissons, Paris 75017",
    },
    {
        "name": "Site archéologique : un des plus vieux villages d'Europe (2500 ans avant JC)",
        "price": 1200,
        "timedelta": 27,
        "numberOfTickets": 40,
        "addressType": "school",
        "otherAddress": "",
    },
    {
        "name": "Spectacle nocturne Lux Salina",
        "price": 600,
        "timedelta": 8,
        "numberOfTickets": 50,
        "addressType": "other",
        "otherAddress": "1 rue des polissons, Paris 75017",
    },
    {
        "name": "Découverte des métiers du patrimoine: Restaurateur(trice) Décorateur(trice), Doreur(reuse)",
        "price": 900,
        "timedelta": 5,
        "numberOfTickets": 15,
        "addressType": "offererVenue",
        "otherAddress": "",
    },
    {
        "name": "Entrée 'Spectacle aux Étoiles' avec conférence 'La Lune... connue et inconnue'",
        "price": 860,
        "timedelta": 9,
        "numberOfTickets": 100,
        "addressType": "school",
        "otherAddress": "",
    },
]

PASSED_STOCK_DATA: list[dict[str, Union[str, int]]] = [
    {
        "name": "Passée: Spectacle nocturne Lux Salina",
        "price": 600,
        "timedelta": 8,
        "numberOfTickets": 50,
        "addressType": "other",
        "otherAddress": "1 rue des polissons, Paris 75017",
    },
    {
        "name": "Passée: Découverte des métiers du patrimoine: Restaurateur(trice) Décorateur(trice), Doreur(reuse)",
        "price": 900,
        "timedelta": 5,
        "numberOfTickets": 15,
        "addressType": "offererVenue",
        "otherAddress": "",
    },
    {
        "name": "Passée: Entrée 'Spectacle aux Étoiles' avec conférence 'La Lune... connue et inconnue'",
        "price": 860,
        "timedelta": 9,
        "numberOfTickets": 100,
        "addressType": "school",
        "otherAddress": "",
    },
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
    educational_current_year = educational_factories.EducationalYearFactory()
    educational_next_year = educational_factories.EducationalYearFactory()

    educational_institutions = [
        educational_factories.EducationalInstitutionFactory(institutionId="0780032L"),
        educational_factories.EducationalInstitutionFactory(institutionId="0781839A"),
        educational_factories.EducationalInstitutionFactory(institutionId="0290047U"),
        educational_factories.EducationalInstitutionFactory(institutionId="0290198H"),
        educational_factories.EducationalInstitutionFactory(institutionId="0910620E"),
        educational_factories.EducationalInstitutionFactory(
            institutionId="0560071Y",
            name=None,
            city=None,
            email=None,
            phoneNumber=None,
        ),
    ]

    # This venue has no adageId hence its validation go through siren validation
    venue = offerers_factories.CollectiveVenueFactory(
        name="Opéra Royal de Versailles",
        siret="95046949400021",
        managingOfferer__siren="950469494",
        managingOfferer__name="Bonne structure pour l'EAC (siren)",
        adageId=None,
    )
    offerers_factories.UserOffererFactory(validationToken=None, offerer=venue.managingOfferer)

    educational_redactor = educational_factories.EducationalRedactorFactory(email="compte.test@education.gouv.fr")
    user_offerer_reimbursements = offerers_factories.UserOffererFactory(
        validationToken=None, user__email="pc.test.payments.eac@example.com"
    )
    venue_reimbursements = offerers_factories.CollectiveVenueFactory(
        name="Théâtre des potirons (remboursements)",
        managingOfferer=user_offerer_reimbursements.offerer,
    )

    venues = []
    for address in ADDRESSES:
        venues.append(
            offerers_factories.CollectiveVenueFactory(
                departementCode=address["department"],
                city=address["city"],
                postalCode=address["postalCode"],
            )
        )

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

    for stock_data in FAKE_STOCK_DATA:
        timedelta = int(stock_data["timedelta"])
        stocks.append(
            educational_factories.CollectiveStockFactory.create_batch(
                2,
                price=stock_data["price"],
                beginningDatetime=now + datetime.timedelta(days=timedelta),
                numberOfTickets=stock_data["numberOfTickets"],
                collectiveOffer__durationMinutes=60,
                collectiveOffer__description="Une description multi-lignes.\nUn lien en description ? https://youtu.be/dQw4w9WgXcQ\n Un email ? mon.email@example.com",
                collectiveOffer__name=stock_data["name"],
                collectiveOffer__venue=venue,
                collectiveOffer__students=[
                    educational_models.StudentLevels.CAP1,
                    educational_models.StudentLevels.CAP2,
                    educational_models.StudentLevels.GENERAL1,
                    educational_models.StudentLevels.GENERAL2,
                ],
                collectiveOffer__offerVenue={
                    "addressType": stock_data["addressType"],
                    "otherAddress": stock_data["otherAddress"],
                    "venueId": humanize(venue.id) if stock_data["addressType"] == "offererVenue" else None,
                },
                collectiveOffer__contactEmail="miss.rond@point.com",
                collectiveOffer__contactPhone="01010100101",
                collectiveOffer__motorDisabilityCompliant=True,
                collectiveOffer__visualDisabilityCompliant=True,
            )[0]
        )

    for stock_data in PASSED_STOCK_DATA:
        timedelta = int(stock_data["timedelta"])
        passed_stocks.append(
            educational_factories.CollectiveStockFactory.create_batch(
                2,
                price=stock_data["price"],
                beginningDatetime=now - datetime.timedelta(days=timedelta),
                numberOfTickets=stock_data["numberOfTickets"],
                collectiveOffer__durationMinutes=60,
                collectiveOffer__description="Une description multi-lignes.\nUn lien en description ? https://youtu.be/dQw4w9WgXcQ\n Un email ? mon.email@example.com",
                collectiveOffer__name=stock_data["name"],
                collectiveOffer__venue=venue,
                collectiveOffer__students=[
                    educational_models.StudentLevels.CAP1,
                    educational_models.StudentLevels.CAP2,
                    educational_models.StudentLevels.GENERAL1,
                    educational_models.StudentLevels.GENERAL2,
                ],
                collectiveOffer__offerVenue={
                    "addressType": stock_data["addressType"],
                    "otherAddress": stock_data["otherAddress"],
                    "venueId": humanize(venue.id) if stock_data["addressType"] == "offererVenue" else None,
                },
                collectiveOffer__contactEmail="miss.rond@point.com",
                collectiveOffer__contactPhone="01010100101",
                collectiveOffer__motorDisabilityCompliant=True,
                collectiveOffer__visualDisabilityCompliant=True,
            )[0]
        )

    for stock_data in FAKE_STOCK_DATA:
        timedelta = int(stock_data["timedelta"])
        next_year_stocks.append(
            educational_factories.CollectiveStockFactory.create_batch(
                2,
                price=stock_data["price"],
                beginningDatetime=now + datetime.timedelta(days=timedelta),
                numberOfTickets=stock_data["numberOfTickets"],
                collectiveOffer__durationMinutes=60,
                collectiveOffer__description="Une description multi-lignes.\nUn lien en description ? https://youtu.be/dQw4w9WgXcQ\n Un email ? mon.email@example.com",
                collectiveOffer__name=stock_data["name"],
                collectiveOffer__venue=venue,
                collectiveOffer__students=[
                    educational_models.StudentLevels.CAP1,
                    educational_models.StudentLevels.CAP2,
                    educational_models.StudentLevels.GENERAL1,
                    educational_models.StudentLevels.GENERAL2,
                ],
                collectiveOffer__offerVenue={
                    "addressType": stock_data["addressType"],
                    "otherAddress": stock_data["otherAddress"],
                    "venueId": humanize(venue.id),
                },
                collectiveOffer__contactEmail="miss.rond@point.com",
                collectiveOffer__contactPhone="01010100101",
                collectiveOffer__motorDisabilityCompliant=True,
                collectiveOffer__visualDisabilityCompliant=True,
            )[0]
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

    if not FeatureToggle.ENABLE_NEW_COLLECTIVE_MODEL.is_active():
        _create_educational_bookings_data(
            educational_redactor,
            educational_institutions,
            educational_current_year,
            educational_next_year,
            venue,
            venue_reimbursements,
        )


def _create_educational_bookings_data(
    educational_redactor: educational_models.EducationalRedactor,
    educational_institutions: list[educational_models.EducationalInstitution],
    educational_current_year: educational_models.EducationalYear,
    educational_next_year: educational_models.EducationalYear,
    venue: offerers_models.Venue,
    venue_reimbursements: offerers_models.Venue,
) -> None:
    now = datetime.datetime.utcnow()
    stocks = []
    for stock_data in FAKE_STOCK_DATA:
        stocks.append(
            EducationalEventStockFactory(
                quantity=100,
                price=stock_data["price"],
                beginningDatetime=now + datetime.timedelta(days=stock_data["timedelta"]),  # type: ignore [arg-type]
                offer__durationMinutes=60,
                offer__withdrawalDetails="Récupération du ticket à l'adresse du lieu",
                offer__description="Une description multi-lignes.\nOù il est notamment question du nombre d'élèves.\nNbr d'élèves max: 50",
                offer__name=stock_data["name"],
                offer__venue=venue,
                offer__extraData={
                    "students": [
                        "CAP - 1re ann\u00e9e",
                        "CAP - 2e ann\u00e9e",
                        "Lyc\u00e9e - Seconde",
                        "Lyc\u00e9e - Premi\u00e8re",
                    ],
                    "offerVenue": {
                        "addressType": "other",
                        "otherAddress": "1 rue des polissons, Paris 75017",
                        "venueId": "",
                    },
                    "contactEmail": "miss.rond@point.com",
                    "contactPhone": "01010100101",
                    "isShowcase": False,
                },
                offer__motorDisabilityCompliant=True,
                offer__visualDisabilityCompliant=True,
            )
        )

    next_year_stocks = [
        EducationalEventStockFactory(
            quantity=100,
            price=1200,
            beginningDatetime=educational_next_year.beginningDate + datetime.timedelta(days=10),
            offer__durationMinutes=60,
            offer__withdrawalDetails="Récupération du ticket à l'adresse du lieu",
            offer__description="Une description multi-lignes.\nOù il est notamment question du nombre d'élèves.\nNbr d'élèves max: 50",
            offer__name="Stage d'initiation à la photographie : prise en main de l'appareil-photo",
            offer__venue=venue,
            offer__extraData={
                "students": [
                    "CAP - 1re ann\u00e9e",
                    "CAP - 2e ann\u00e9e",
                    "Lyc\u00e9e - Seconde",
                    "Lyc\u00e9e - Premi\u00e8re",
                ],
                "offerVenue": {
                    "addressType": "other",
                    "otherAddress": "1 rue des polissons, Paris 75017",
                    "venueId": "",
                },
                "contactEmail": "miss.rond@point.com",
                "contactPhone": "01010100101",
                "isShowcase": False,
            },
            offer__motorDisabilityCompliant=True,
            offer__visualDisabilityCompliant=True,
        ),
        EducationalEventStockFactory(
            quantity=60,
            price=1400,
            beginningDatetime=educational_next_year.beginningDate + datetime.timedelta(days=15),
            offer__durationMinutes=60,
            offer__withdrawalDetails="Récupération du ticket à l'adresse du lieu",
            offer__description="Une description multi-lignes.\nOù il est notamment question du nombre d'élèves.\nNbr d'élèves max: 50",
            offer__name="Explorer la nature au Parc Zoologique et Botanique de Mulhouse",
            offer__venue=venue,
            offer__extraData={
                "students": [
                    "CAP - 1re ann\u00e9e",
                    "CAP - 2e ann\u00e9e",
                    "Lyc\u00e9e - Seconde",
                    "Lyc\u00e9e - Premi\u00e8re",
                ],
                "offerVenue": {
                    "addressType": "other",
                    "otherAddress": "1 rue des polissons, Paris 75017",
                    "venueId": "",
                },
                "contactEmail": "miss.rond@point.com",
                "contactPhone": "01010100101",
                "isShowcase": False,
            },
            offer__motorDisabilityCompliant=True,
            offer__visualDisabilityCompliant=True,
        ),
    ]

    for stock in stocks:
        for educational_institution in educational_institutions:
            EducationalBookingFactory(
                educationalBooking__educationalRedactor=educational_redactor,
                educationalBooking__educationalInstitution=educational_institution,
                educationalBooking__educationalYear=educational_current_year,
                educationalBooking__confirmationLimitDate=now + datetime.timedelta(days=10),
                cancellation_limit_date=now + datetime.timedelta(days=4),
                status=BookingStatus.PENDING,
                stock=stock,
            )

            UsedEducationalBookingFactory(
                educationalBooking__educationalRedactor=educational_redactor,
                educationalBooking__educationalInstitution=educational_institution,
                educationalBooking__educationalYear=educational_current_year,
                educationalBooking__confirmationLimitDate=now - datetime.timedelta(days=20),
                cancellation_limit_date=now - datetime.timedelta(days=15),
                dateUsed=now - datetime.timedelta(8),
                status=BookingStatus.USED,
                stock=EducationalEventStockFactory(
                    quantity=100,
                    price=1200,
                    beginningDatetime=now - datetime.timedelta(days=10),
                    bookingLimitDatetime=now - datetime.timedelta(days=10),
                    offer__venue=venue_reimbursements,
                    offer__extraData={
                        "students": [
                            "CAP - 1re ann\u00e9e",
                            "CAP - 2e ann\u00e9e",
                            "Lyc\u00e9e - Seconde",
                            "Lyc\u00e9e - Premi\u00e8re",
                        ],
                        "offerVenue": {
                            "addressType": "other",
                            "otherAddress": "1 rue des polissons, Paris 75017",
                            "venueId": "",
                        },
                        "contactEmail": "miss.rond@point.com",
                        "contactPhone": "01010100101",
                        "isShowcase": False,
                    },
                    offer__motorDisabilityCompliant=True,
                    offer__visualDisabilityCompliant=True,
                ),
            )

    for next_year_stock in next_year_stocks:
        for educational_institution in educational_institutions:
            EducationalBookingFactory(
                educationalBooking__educationalRedactor=educational_redactor,
                educationalBooking__educationalInstitution=educational_institution,
                educationalBooking__educationalYear=educational_next_year,
                educationalBooking__confirmationLimitDate=now + datetime.timedelta(days=30),
                status=BookingStatus.PENDING,
                stock=next_year_stock,
            )
