from flask import url_for
import pytest

from pcapi.core.offerers import factories as offerers_factories


pytestmark = [
    pytest.mark.usefixtures("db_session"),
    pytest.mark.backoffice_v3,
]


class AutocompleteOffererTest:
    @pytest.mark.parametrize(
        "search_query, expected_texts",
        [
            ("", set()),
            ("1", set()),
            ("12", {"Le Cinéma (123456789)", "La Librairie (123444556)"}),
            ("1234", {"Le Cinéma (123456789)", "La Librairie (123444556)"}),
            ("12345", {"Le Cinéma (123456789)"}),
            ("123444556", {"La Librairie (123444556)"}),
            ("789", set()),
            ("100200301", set()),
            ("ciné", {"Le Cinéma (123456789)", "Cinéma concurrent (561234789)"}),
            ("ciné théâtre", set()),
        ],
    )
    def test_autocomplete_offerers(self, authenticated_client, search_query, expected_texts):
        # given
        offerers_factories.OffererFactory(siren="100200300", name="Le Théâtre")
        offerers_factories.OffererFactory(siren="123456789", name="Le Cinéma")
        offerers_factories.OffererFactory(siren="123444556", name="La Librairie")
        offerers_factories.OffererFactory(siren="561234789", name="Cinéma concurrent")

        # when
        response = authenticated_client.get(url_for("backoffice_v3_web.autocomplete_offerers", q=search_query))

        # then
        assert response.status_code == 200
        items = response.json["items"]
        for item in items:
            assert isinstance(item["id"], int)
            assert isinstance(item["text"], str)
        assert {item["text"] for item in items} == expected_texts


class AutocompleteVenueTest:
    @pytest.mark.parametrize(
        "search_query, expected_texts",
        [
            ("", set()),
            ("1", set()),
            ("12", {"Le Cinéma (12345678900018)", "La Librairie (12344455600012)", "La Médiathèque (12345678900011)"}),
            (
                "1234",
                {"Le Cinéma (12345678900018)", "La Librairie (12344455600012)", "La Médiathèque (12345678900011)"},
            ),
            ("12345", {"Le Cinéma (12345678900018)", "La Médiathèque (12345678900011)"}),
            ("123456789", {"Le Cinéma (12345678900018)", "La Médiathèque (12345678900011)"}),
            ("12345678900011", {"La Médiathèque (12345678900011)"}),
            ("789", set()),
            ("100200301", set()),
            ("ciné", {"Le Cinéma (12345678900018)", "Cinéma concurrent (56123478900023)"}),
            ("ciné théâtre", set()),
        ],
    )
    def test_autocomplete_venues(self, authenticated_client, search_query, expected_texts):
        # given
        offerers_factories.VenueFactory(siret="10020030000021", name="Le Théâtre")
        offerers_factories.VenueFactory(siret="12345678900018", name="Le Cinéma")
        offerers_factories.VenueFactory(siret="12344455600012", name="La Librairie")
        offerers_factories.VenueFactory(siret="12345678900011", name="La Médiathèque")
        offerers_factories.VenueFactory(siret="56123478900023", name="Cinéma concurrent")

        # when
        response = authenticated_client.get(url_for("backoffice_v3_web.autocomplete_venues", q=search_query))

        # then
        assert response.status_code == 200
        items = response.json["items"]
        for item in items:
            assert isinstance(item["id"], int)
            assert isinstance(item["text"], str)
        assert {item["text"] for item in items} == expected_texts
