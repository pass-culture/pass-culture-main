import pytest

from pcapi.core.pro_assistant import portal_map


class FindRouteIdTest:
    @pytest.mark.parametrize(
        "path,expected_route_id",
        [
            ("/accueil", "home"),
            ("/offres", "individual_offers"),
            ("/offres/collectives", "collective_bookable_offers"),
            ("/offre/individuelle/12/creation/tarifs", "individual_offer_creation"),
            ("/offre/individuelle/12/edition/tarifs", "individual_offers"),
            ("/offre/creation/collectif/vitrine", "collective_offer_creation"),
            ("/offre/12/collectif/edition", "collective_bookable_offers"),
            ("/offre/12/collectif/vitrine/apercu", "collective_template_offers"),
            ("/administration/remboursements/revenus?annee=2026", "revenue"),
            ("/parametres", "venue_general_information"),
        ],
    )
    def test_known_path(self, path, expected_route_id):
        assert portal_map.find_route_id(path) == expected_route_id

    @pytest.mark.parametrize("path", [None, "", "/inconnu", "/offres/inconnu/12"])
    def test_unknown_path(self, path):
        assert portal_map.find_route_id(path) is None

    def test_every_page_path_is_found(self):
        for page in portal_map.PORTAL_PAGES:
            assert portal_map.find_route_id(page.path) == page.route_id


class RenderForPromptTest:
    def test_contains_every_route_id(self):
        rendered = portal_map.render_for_prompt()

        for route_id in portal_map.ROUTE_IDS:
            assert f"route_id: {route_id}\n" in rendered
