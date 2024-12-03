import logging

import pcapi.core.history.api as history_api
import pcapi.core.history.models as history_models
from pcapi.core.offerers import api as offerers_api
from pcapi.core.offerers import models as offerers_models
from pcapi.models import db


logger = logging.getLogger(__name__)


def match_acceslibre(venue: offerers_models.Venue) -> None:
    old_slug = venue.external_accessibility_id
    old_url = venue.external_accessibility_url
    offerers_api.delete_venue_accessibility_provider(venue)
    # TODO(xordoquy): see why delete_venue_accessibility_provider doesn't synchronize session
    db.session.refresh(venue)
    offerers_api.set_accessibility_provider_id(venue)

    if not venue.accessibilityProvider:
        logger.info("No match found at acceslibre for Venue %s ", venue.id)
        return
    if old_slug != venue.accessibilityProvider.externalAccessibilityId:
        history_api.add_action(
            history_models.ActionType.INFO_MODIFIED,
            author=None,
            venue=venue,
            comment="Recherche automatisée du lieu permanent avec Acceslibre",
            modified_info={
                "accessibilityProvider.externalAccessibilityId": {
                    "old_info": old_slug,
                    "new_info": venue.accessibilityProvider.externalAccessibilityId,
                },
                "accessibilityProvider.externalAccessibilityUrl": {
                    "old_info": old_url,
                    "new_info": venue.accessibilityProvider.externalAccessibilityUrl,
                },
            },
        )

    offerers_api.set_accessibility_infos_from_provider_id(venue)
    db.session.add(venue)
    db.session.commit()
