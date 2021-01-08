from enum import Enum

from pcapi.core.bookings import conf


class ExpenseDomain(Enum):
    ALL = "all"
    DIGITAL = "digital"
    PHYSICAL = "physical"


def get_expenses_limit(user, version):
    bookings = user.get_not_cancelled_bookings()
    config = conf.LIMIT_CONFIGURATIONS[version]
    capped_digital_bookings = [booking for booking in bookings if config.digital_cap_applies(booking.stock.offer)]
    capped_physical_bookings = [booking for booking in bookings if config.physical_cap_applies(booking.stock.offer)]
    limits = [
        {
            "domain": ExpenseDomain.ALL.value,
            "current": sum(booking.total_amount for booking in bookings),
            "max": config.TOTAL_CAP,
        }
    ]
    if config.DIGITAL_CAP:
        limits.append(
            {
                "domain": ExpenseDomain.DIGITAL.value,
                "current": sum(booking.total_amount for booking in capped_digital_bookings),
                "max": config.DIGITAL_CAP,
            }
        )
    if config.PHYSICAL_CAP:
        limits.append(
            {
                "domain": ExpenseDomain.PHYSICAL.value,
                "current": sum(booking.total_amount for booking in capped_physical_bookings),
                "max": config.PHYSICAL_CAP,
            }
        )
    return limits
