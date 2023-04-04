from pcapi.core.educational import factories as educational_factories
from pcapi.core.educational import models as educational_models
from pcapi.core.educational.api.institution import refund_institution


def test_refund_institution_ok(db_session):
    booking = educational_factories.ReimbursedCollectiveBookingFactory()
    deposit = educational_factories.EducationalDepositFactory(
        educationalInstitution=booking.educationalInstitution,
        educationalYear=booking.educationalYear,
    )

    refund_institution(amount=23.24, ticket="pouet", collective_booking_id=booking.id)

    refund = educational_models.CollectiveRefund.query.one_or_none()
    assert refund is not None
    assert refund.educationalYear == booking.educationalYear
    assert refund.educationalInstitution == booking.educationalInstitution
    assert refund.ministry == deposit.ministry
    assert float(refund.amount) == 23.24
    assert refund.ticket == "pouet"
