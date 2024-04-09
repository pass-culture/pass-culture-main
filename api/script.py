from pcapi.flask_app import app


app.app_context().push()

import logging

from pcapi.core.educational import models as educational_models
from pcapi.core.finance import models as finance_models
from pcapi.core.finance.api import _delete_dependent_pricings
from pcapi.core.offerers.models import VenuePricingPointLink
from pcapi.models import db


logger = logging.getLogger(__name__)


COLLECTIVE_OFFERS_IDS = [212805, 206771]  # trier par ordre inverse de pricingOrderingDate
NEW_VENUE_ID = 86853
NEW_OFFERER_ID = 35758


def move_collective_offer(collective_offer_id: int) -> None:
    collective_offer = educational_models.CollectiveOffer.query.filter(
        educational_models.CollectiveOffer.id == collective_offer_id
    ).one()
    collective_offer.venueId = NEW_VENUE_ID
    db.session.add(collective_offer)

    collective_booking = collective_offer.collectiveStock.collectiveBookings[
        0
    ]  # only one booking per stock in our case
    collective_booking.venueId = NEW_VENUE_ID
    collective_booking.offererId = NEW_OFFERER_ID
    db.session.add(collective_booking)

    finance_event = finance_models.FinanceEvent.query.filter(
        finance_models.FinanceEvent.collectiveBookingId == collective_booking.id
    ).one()  # only one booking per stock in our case
    pricing = finance_models.Pricing.query.filter(finance_models.Pricing.eventId == finance_event.id).one()
    db.session.delete(pricing)
    _delete_dependent_pricings(
        finance_event,
        log_message="PC-28535: move collective offers on new venue",
    )
    finance_event.venueId = NEW_VENUE_ID
    finance_event.pricingPointId = NEW_VENUE_ID  # the venue is its own pricingPoint
    finance_event.status = finance_models.FinanceEventStatus.READY

    ppoint_link = VenuePricingPointLink.query.filter_by(
        venueId=NEW_VENUE_ID
    ).one()  # je simplifie, ça marche parce qu'il n'y en a qu'un
    finance_event.pricingOrderingDate = max(
        collective_booking.dateUsed,
        collective_booking.collectiveStock.beginningDatetime,
        ppoint_link.timespan.lower,
    )

    db.session.add(finance_event)

    db.session.commit()
    print(collective_offer.venueId)
    print(collective_booking.venueId)
    print(finance_event.venueId)
    print(finance_event.pricingPointId)


def main():
    for id in COLLECTIVE_OFFERS_IDS:
        move_collective_offer(id)


main()

# STAGING
# COL_OFFER 206771 et COLLECTIVEOFFER 212805
# COLLECTIVE OFFER | VENUEID | BOOKING | VENUEID BOOKING | FINANCEEVENT | FINANCEEVENT VENUEID | FINANCEEVENT PRICINGPOINTID | PRICING  |
# 206771           | 86853   | 143371  | 86853           | 21062226     | 69850                |  69850                      | 19937354 |
# 212805           | 86853   | 147188  | 86853           | 21969840     | 69850                | 69850                       |          |

# VERIFICATION

# 206771           |  86853 | 143371 | 86853             | 21062226     | 69850                | 69850                       | 19937354 |
# 212805           | 86853  | 147188 | 86853             | 21969840     | 69850                | 69850                       |          |

# LES VENUES SONT DEJA MISE EN 86853 mais a la semaine derniere, je l'avais fait via requete SQL sans savoir qu'il fallait toucher a la finance. il est possible que le changement de venueid fonctionne.
