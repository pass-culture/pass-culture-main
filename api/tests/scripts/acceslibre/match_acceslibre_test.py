from unittest.mock import patch

import pytest

from pcapi.connectors.acceslibre import AcceslibreInfos
from pcapi.core.offerers import factories as offerers_factories
from pcapi.scripts.acceslibre.match_acceslibre import match_acceslibre


pytestmark = pytest.mark.usefixtures("db_session")


class MatchAcceslibreTest:
    @patch("pcapi.connectors.acceslibre.get_id_at_accessibility_provider")
    def test_match_acceslibre(self, mock_get_id_at_accessibility_provider):
        venue = offerers_factories.VenueFactory(name="Une librairie de test")
        slug = "mon-slug"
        mock_get_id_at_accessibility_provider.side_effect = [
            AcceslibreInfos(slug=slug, url=f"https://acceslibre.beta.gouv.fr/app/erps/{slug}/")
        ]
        match_acceslibre(venue)
        assert venue.accessibilityProvider.externalAccessibilityId == slug
        assert (
            venue.accessibilityProvider.externalAccessibilityUrl == f"https://acceslibre.beta.gouv.fr/app/erps/{slug}/"
        )
        assert venue.action_history[0].extraData == {
            "modified_info": {
                "accessibilityProvider.externalAccessibilityId": {
                    "new_info": slug,
                    "old_info": None,
                },
                "accessibilityProvider.externalAccessibilityUrl": {
                    "new_info": f"https://acceslibre.beta.gouv.fr/app/erps/{slug}/",
                    "old_info": None,
                },
            }
        }
