import datetime

from pcapi.core.bookings.factories import EducationalBookingFactory
from pcapi.core.bookings.models import BookingStatus
import pcapi.core.educational.factories as educational_factories
from pcapi.core.educational.models import EducationalBookingStatus
from pcapi.core.offers.factories import EventStockFactory
from pcapi.core.offers.factories import MediationFactory
from pcapi.core.users.factories import UserFactory
from pcapi.core.users.models import UserRole
from pcapi.sandboxes.scripts.utils.storage_utils import store_public_object_from_sandbox_assets


def create_industrial_educational_bookings() -> None:
    educational_current_year = educational_factories.EducationalYearFactory()
    educational_next_year = educational_factories.EducationalYearFactory()

    versailles_educational_institution1 = educational_factories.EducationalInstitutionFactory(institutionId="0780032L")
    versailles_educational_institution2 = educational_factories.EducationalInstitutionFactory(institutionId="0781839A")
    rennes_educational_institution1 = educational_factories.EducationalInstitutionFactory(institutionId="0290047U")
    rennes_educational_institution2 = educational_factories.EducationalInstitutionFactory(institutionId="0290198H")
    educational_institutions = [
        versailles_educational_institution1,
        versailles_educational_institution2,
        rennes_educational_institution1,
        rennes_educational_institution2,
    ]

    now = datetime.datetime.now(datetime.timezone.utc)

    educational_test_user = UserFactory(
        email="compte.test@education.gouv.fr",
        isBeneficiary=False,
        roles=[UserRole.INSTITUTIONAL_PROJECT_REDACTOR],
        civility="Mme",
    )

    stocks = [
        EventStockFactory(
            quantity=100,
            price=1000,
            beginningDatetime=now + datetime.timedelta(days=20),
            offer__durationMinutes=60,
            offer__withdrawalDetails="Des détails sur comment récupérer l'offre",
            offer__description="Une description multi-lignes.\nOù il est notamment question du nombre d'élèves.\nNbr d'élèves max: 50",
            offer__isEducational=True,
        ),
        EventStockFactory(
            quantity=100, price=800, beginningDatetime=now + datetime.timedelta(days=18), offer__isEducational=True
        ),
        EventStockFactory(
            quantity=100,
            price=1200,
            beginningDatetime=now + datetime.timedelta(days=15),
            offer__venue__postalCode="97400",
            offer__isEducational=True,
        ),
    ]
    for stock in stocks:
        mediation = MediationFactory(offer=stock.offer, credit="Crédit photo")
        store_public_object_from_sandbox_assets("thumbs", mediation, mediation.offer.type)

    next_year_stock = EventStockFactory(
        quantity=100,
        price=1200,
        beginningDatetime=educational_next_year.beginningDate + datetime.timedelta(days=10),
    )

    deposits = []
    for _, educational_institution in enumerate(educational_institutions):
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

    for i in range(3):
        for _, educational_institution in enumerate(educational_institutions):
            EducationalBookingFactory(
                user=educational_test_user,
                educationalBooking__educationalInstitution=educational_institution,
                educationalBooking__educationalYear=educational_current_year,
                educationalBooking__confirmationLimitDate=now + datetime.timedelta(days=10),
                cancellation_limit_date=now + datetime.timedelta(days=4),
                status=BookingStatus.PENDING,
                stock=stocks[i],
            )

    for i in range(3):
        for _, educational_institution in enumerate(educational_institutions):
            EducationalBookingFactory(
                user=educational_test_user,
                educationalBooking__educationalInstitution=educational_institution,
                educationalBooking__educationalYear=educational_next_year,
                status=BookingStatus.PENDING,
                stock=next_year_stock,
            )

    for i in range(3):
        for _, educational_institution in enumerate(educational_institutions):
            EducationalBookingFactory(
                user=educational_test_user,
                educationalBooking__educationalInstitution=educational_institution,
                educationalBooking__educationalYear=educational_current_year,
                educationalBooking__confirmationLimitDate=now + datetime.timedelta(days=3),
                status=BookingStatus.PENDING,
                stock=stocks[i],
            )

    for i in range(3):
        for _, educational_institution in enumerate(educational_institutions):
            EducationalBookingFactory(
                user=educational_test_user,
                educationalBooking__educationalInstitution=educational_institution,
                educationalBooking__educationalYear=educational_current_year,
                educationalBooking__confirmationLimitDate=now + datetime.timedelta(days=10),
                educationalBooking__confirmationDate=now - datetime.timedelta(days=1),
                cancellation_limit_date=now + datetime.timedelta(days=4),
                status=BookingStatus.CONFIRMED,
                stock=stocks[i],
            )

    for i in range(2):
        for _, educational_institution in enumerate(educational_institutions):
            EducationalBookingFactory(
                user=educational_test_user,
                educationalBooking__educationalInstitution=educational_institution,
                educationalBooking__educationalYear=educational_current_year,
                educationalBooking__confirmationLimitDate=now + datetime.timedelta(days=10),
                educationalBooking__confirmationDate=now - datetime.timedelta(days=2),
                cancellation_limit_date=now + datetime.timedelta(days=4),
                cancellation_date=now - datetime.timedelta(days=1),
                status=BookingStatus.CANCELLED,
                isCancelled=True,
                stock=stocks[i],
            )

    for i in range(2):
        for _, educational_institution in enumerate(educational_institutions):
            EducationalBookingFactory(
                user=educational_test_user,
                educationalBooking__educationalInstitution=educational_institution,
                educationalBooking__educationalYear=educational_current_year,
                educationalBooking__confirmationLimitDate=now + datetime.timedelta(days=10),
                educationalBooking__confirmationDate=now - datetime.timedelta(days=2),
                educationalBooking__status=EducationalBookingStatus.REFUSED,
                cancellation_limit_date=now + datetime.timedelta(days=4),
                cancellation_date=now - datetime.timedelta(days=1),
                status=BookingStatus.CANCELLED,
                isCancelled=True,
                stock=stocks[i],
            )

    for i in range(2):
        for _, educational_institution in enumerate(educational_institutions):
            EducationalBookingFactory(
                user=educational_test_user,
                educationalBooking__educationalInstitution=educational_institution,
                educationalBooking__educationalYear=educational_current_year,
                educationalBooking__confirmationLimitDate=now + datetime.timedelta(days=10),
                educationalBooking__confirmationDate=now - datetime.timedelta(days=2),
                educationalBooking__status=EducationalBookingStatus.USED_BY_INSTITUTE,
                cancellation_limit_date=now + datetime.timedelta(days=4),
                status=BookingStatus.CONFIRMED,
                stock=stocks[i],
            )

    for i in range(2):
        for _, educational_institution in enumerate(educational_institutions):
            EducationalBookingFactory(
                user=educational_test_user,
                educationalBooking__educationalInstitution=educational_institution,
                educationalBooking__educationalYear=educational_current_year,
                educationalBooking__confirmationLimitDate=now + datetime.timedelta(days=10),
                educationalBooking__confirmationDate=now - datetime.timedelta(days=2),
                educationalBooking__status=EducationalBookingStatus.USED_BY_INSTITUTE,
                cancellation_limit_date=now + datetime.timedelta(days=4),
                status=BookingStatus.USED,
                dateUsed=now - datetime.timedelta(days=1),
                stock=stocks[i],
            )
