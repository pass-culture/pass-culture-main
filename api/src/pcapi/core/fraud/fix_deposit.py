from datetime import datetime

from dateutil.relativedelta import relativedelta
from sqlalchemy import or_
from sqlalchemy.orm import joinedload

from pcapi.core.bookings.models import Booking
from pcapi.core.bookings.models import BookingStatus
from pcapi.core.bookings.models import IndividualBooking
from pcapi.core.fraud import models as fraud_models
from pcapi.core.offers.models import Stock
from pcapi.core.payments import models as payment_models
from pcapi.core.users import models as users_models
from pcapi.core.users import utils as users_utils
from pcapi.core.users.api import get_domains_credit
from pcapi.models.beneficiary_import_status import ImportStatus
from pcapi.repository import repository


def get_bookings_from_deposit(deposit_id: int) -> list[Booking]:
    return (
        Booking.query.join(Booking.individualBooking)
        .filter(
            IndividualBooking.depositId == deposit_id,
            or_(Booking.status == BookingStatus.USED, Booking.status == BookingStatus.REIMBURSED),
        )
        .options(joinedload(Booking.stock).joinedload(Stock.offer))
        .all()
    )


def find_ubble_anomalies():
    checks: list[fraud_models.BeneficiaryFraudCheck] = (
        fraud_models.BeneficiaryFraudCheck.query.join(users_models.User)
        .filter(
            fraud_models.BeneficiaryFraudCheck.type == fraud_models.FraudCheckType.UBBLE,
            fraud_models.BeneficiaryFraudCheck.eligibilityType == users_models.EligibilityType.AGE18,
            fraud_models.BeneficiaryFraudCheck.status == fraud_models.FraudCheckStatus.OK,
            users_models.User.has_beneficiary_role == False,
        )
        .all()
    )
    print(len(checks))
    none_age = []
    underage_age = []
    young = []
    old = []
    for check in checks:
        content = check.source_data()
        age = users_utils.get_age_at_date(content.get_birth_date(), content.get_registration_datetime())
        if age is None:
            none_age.append(check.id)
        elif age in [15, 16, 17]:
            underage_age.append(check.id)
            check.eligibilityType = users_models.EligibilityType.UNDERAGE
            repository.save(check)
        elif age < 15:
            young.append(check.id)
        elif age > 19:
            old.append(check.id)

    print("none_age", len(none_age))
    print("underage_age", len(underage_age))
    print("young", len(young))
    print("old", len(old))


def fix_deposit():
    users: list[users_models.User] = (
        users_models.User.query.filter(
            users_models.User.has_beneficiary_role,
            users_models.User.dateOfBirth > (datetime.now() - relativedelta(years=18)),
        )
        .join(payment_models.Deposit)
        .order_by(payment_models.Deposit.dateCreated.desc())
        .all()
    )
    print(len(users), "users")
    for user in users:
        used_bookings = get_bookings_from_deposit(user.deposit.id)
        credit = get_domains_credit(user)
        credit_with_used = get_domains_credit(user, used_bookings)
        try:
            imports = next(
                bimport
                for bimport in user.beneficiaryImports
                if ImportStatus.CREATED in [status.status for status in bimport.statuses]
            )
        except:
            imports = None
        print(
            "id:",
            user.id,
            "; age:",
            user.age,
            "; source:",
            imports.source if imports else "vide",
            "; date deposit:",
            user.deposit.dateCreated.date(),
            "; montant initial:",
            user.deposit.amount,
            "; montant restant:",
            credit.all.remaining,
            "; montant restant utilisé:",
            credit_with_used.all.remaining,
        )

    return users
