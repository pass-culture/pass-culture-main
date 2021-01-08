from pcapi.core.bookings import conf


PHYSICAL = "physical"
DIGITAL = "digital"
ALL = "all"


def get_expenses_limit(user, version):
    bookings = user.get_not_cancelled_bookings()
    config = conf.LIMIT_CONFIGURATIONS[version]
    capped_digital_bookings = [booking for booking in bookings if config.digital_cap_applies(booking.stock.offer)]
    capped_physical_bookings = [booking for booking in bookings if config.physical_cap_applies(booking.stock.offer)]
    return [
        {
            "domain": ALL,
            "current": sum(booking.total_amount for booking in bookings),
            "max": config.TOTAL_CAP,
        },
        {
            "domain": DIGITAL,
            "current": sum(booking.total_amount for booking in capped_digital_bookings),
            "max": config.DIGITAL_CAP,
        },
        {
            "domain": PHYSICAL,
            "current": sum(booking.total_amount for booking in capped_physical_bookings),
            "max": config.PHYSICAL_CAP,
        },
    ]
