from flask import Flask


def install_routes(app: Flask) -> None:
    from . import (
        adage_data,
        bookings,
        collective_bookings,
        collective_offers,
        collective_stocks,
        features,
        finance,
        headline_offer,
        offerers,
        offers,
        providers,
        reimbursements,
        signup,
        sirene,
        statistics,
        stocks,
        users,
        venue_labels,
        venue_providers,
        venue_types,
        venues,
    )
