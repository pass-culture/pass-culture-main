import datetime

from pcapi.core.bookings.factories import EducationalBookingFactory
from pcapi.core.bookings.factories import UsedEducationalBookingFactory
from pcapi.core.bookings.models import BookingStatus
from pcapi.core.educational import models as educational_models
import pcapi.core.educational.factories as educational_factories
from pcapi.core.offerers import models as offerers_models
import pcapi.core.offerers.factories as offerers_factories
from pcapi.core.offers.factories import EducationalEventStockFactory
from pcapi.models.feature import FeatureToggle


FAKE_STOCK_DATA = [
    {
        "name": "Visite de l'Abbaye Royale + Musée d'art moderne + Nocturne Les étoiles de Fontevraud",
        "price": 1000,
        "timedelta": 20,
    },
    {
        "name": "Visite de la mine Gabe Gottes",
        "price": 800,
        "timedelta": 18,
    },
    {
        "name": "Clued'au Château",
        "price": 1200,
        "timedelta": 15,
    },
    {
        "name": "Visitez le Panthéon, Chef d'œuvre de l'architecte Soufflot",
        "price": 1200,
        "timedelta": 22,
    },
    {
        "name": "Arc de Triomphe : embrassez tout Paris du haut du monument emblématique",
        "price": 1200,
        "timedelta": 25,
    },
    {
        "name": "Site archéologique : un des plus vieux villages d'Europe (2500 ans avant JC)",
        "price": 1200,
        "timedelta": 27,
    },
    {
        "name": "Spectacle nocturne Lux Salina",
        "price": 600,
        "timedelta": 8,
    },
    {
        "name": "Découverte des métiers du patrimoine: Restaurateur(trice) Décorateur(trice), Doreur(reuse)",
        "price": 900,
        "timedelta": 5,
    },
    {
        "name": "Entrée 'Spectacle aux Étoiles' avec conférence 'La Lune... connue et inconnue'",
        "price": 860,
        "timedelta": 9,
    },
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
        educational_factories.EducationalInstitutionFactory(institutionId="0560071Y"),
    ]

    # This venue has no adageId hence its validation go through siren validation
    venue = offerers_factories.CollectiveVenueFactory(
        name="Opéra Royal de Versailles",
        siret="95046949400021",
        managingOfferer__siren="950469494",
        adageId=None,
    )
    offerers_factories.UserOffererFactory(validationToken=None, offerer=venue.managingOfferer)

    educational_redactor = educational_factories.EducationalRedactorFactory(email="compte.test@education.gouv.fr")
    user_offerer_reimbursements = offerers_factories.UserOffererFactory(
        validationToken=None, user__email="pc.test.payments.eac@example.com"
    )
    venue_reimbursements = offerers_factories.CollectiveVenueFactory(
        name="Théâtre des potirons",
        managingOfferer=user_offerer_reimbursements.offerer,
    )

    deposits = []
    for educational_institution in educational_institutions:
        deposits.append(
            educational_factories.EducationalDepositFactory(
                educationalInstitution=educational_institution,
                educationalYear=educational_current_year,
                amount=20000,
            )
        )
        deposits.append(
            educational_factories.EducationalDepositFactory(
                educationalInstitution=educational_institution,
                educationalYear=educational_next_year,
                amount=25000,
                isFinal=False,
            )
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
