from pcapi.core.offerers.models import Venue
from pcapi.repository import db
from pcapi.sandboxes.scripts.utils.helpers import log_func_duration


@log_func_duration
def add_accessibility_compliance_to_venues() -> None:
    venues = db.session.query(Venue).all()
    for i, venue in enumerate(venues):
        venue.audioDisabilityCompliant = bool(i & 1)
        venue.mentalDisabilityCompliant = bool(i & 2)
        venue.motorDisabilityCompliant = bool(i & 4)
        venue.visualDisabilityCompliant = bool(i & 8)

    for i in range(0, len(venues), 32):
        venues[i].audioDisabilityCompliant = None
        venues[i].mentalDisabilityCompliant = None
        venues[i].motorDisabilityCompliant = None
        venues[i].visualDisabilityCompliant = None

    db.session.add_all(venues)
    db.session.commit()
