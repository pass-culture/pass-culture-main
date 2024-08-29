from pcapi.app import app
from pcapi.core.offerers.models import AccessibilityProvider
from pcapi.repository import db

with app.app_context():
    AccessibilityProvider.query.filter(AccessibilityProvider.id == 7760).update(
        {"externalAccessibilityUrl": "https://acceslibre.beta.gouv.fr/app/37-la-riche/a/cinema/erp/la-pleiade-2/"}
    )
    db.session.commit()
