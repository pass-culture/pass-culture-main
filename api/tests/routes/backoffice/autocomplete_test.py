import datetime

from flask import url_for
import pytest

from pcapi.core.criteria import factories as criteria_factories
from pcapi.core.offerers import factories as offerers_factories
from pcapi.core.testing import assert_num_queries


pytestmark = [
    pytest.mark.usefixtures("db_session"),
    pytest.mark.backoffice,
]


def _test_autocomplete(authenticated_client, endpoint: str, search_query: str, expected_texts: list[str]):
    # user + session + data requested
    expected_num_queries = 3 if search_query.isnumeric() or len(search_query) >= 2 else 2

    with assert_num_queries(expected_num_queries):
        response = authenticated_client.get(url_for(endpoint, q=search_query))
        assert response.status_code == 200

    items = response.json["items"]
    for item in items:
        assert isinstance(item["id"], int)
        assert isinstance(item["text"], str)
    assert {item["text"] for item in items} == expected_texts


class AutocompleteOffererTest:
    @pytest.mark.parametrize(
        "search_query, expected_texts",
        [
            ("", set()),
            ("1", {"La scène (100200000)"}),
            ("12", {"Le Cinéma (123456789)", "La Librairie (123444556)"}),
            ("1234", {"Le Cinéma (123456789)", "La Librairie (123444556)"}),
            ("12345", {"Le Cinéma (123456789)"}),
            ("123444556", {"La Librairie (123444556)"}),
            ("789", set()),
            ("100200301", set()),
            ("ciné", {"Le Cinéma (123456789)", "Cinéma concurrent (561234789)"}),
            ("cinema", {"Le Cinéma (123456789)", "Cinéma concurrent (561234789)"}),
            ("ciné théâtre", set()),
            ("666666", set()),
            ("666666001", {"Le Théâtre (100200300)"}),
            ("12344", {"Cinéma concurrent (561234789)", "La Librairie (123444556)"}),
        ],
    )
    def test_autocomplete_offerers(self, authenticated_client, search_query, expected_texts):
        offerers_factories.OffererFactory(id=1, siren="100200000", name="La scène")
        offerers_factories.OffererFactory(id=666666001, siren="100200300", name="Le Théâtre")
        offerers_factories.OffererFactory(id=666666002, siren="123456789", name="Le Cinéma")
        offerers_factories.OffererFactory(id=666666003, siren="123444556", name="La Librairie")
        offerers_factories.OffererFactory(id=12344, siren="561234789", name="Cinéma concurrent")

        _test_autocomplete(authenticated_client, "backoffice_web.autocomplete_offerers", search_query, expected_texts)


class AutocompleteVenueTest:
    @pytest.mark.parametrize(
        "search_query, expected_texts",
        [
            ("", set()),
            ("1", {"La scène (10020030000000)"}),
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
            ("cinema", {"Le Cinéma (12345678900018)", "Cinéma concurrent (56123478900023)"}),
            ("ciné théâtre", set()),
            ("666666", set()),
            ("666666001", {"Le Théâtre (10020030000021)"}),
            ("12344", {"Cinéma concurrent (56123478900023)", "La Librairie (12344455600012)"}),
        ],
    )
    def test_autocomplete_venues(self, authenticated_client, search_query, expected_texts):
        offerers_factories.VenueFactory(id=1, siret="10020030000000", name="La scène")
        offerers_factories.VenueFactory(id=666666001, siret="10020030000021", name="Le Théâtre")
        offerers_factories.VenueFactory(id=666666002, siret="12345678900018", name="Le Cinéma")
        offerers_factories.VenueFactory(id=666666003, siret="12344455600012", name="La Librairie")
        offerers_factories.VenueFactory(id=666666004, siret="12345678900011", name="La Médiathèque")
        offerers_factories.VenueFactory(id=12344, siret="56123478900023", name="Cinéma concurrent")

        _test_autocomplete(authenticated_client, "backoffice_web.autocomplete_venues", search_query, expected_texts)


class AutocompleteCriteriaTest:
    @pytest.mark.parametrize(
        "search_query, expected_texts",
        [
            ("", set()),
            ("o", set()),
            ("offre", {"Bonne offre d'appel", "Offre du moment"}),
            ("va", {"Mauvaise accroche (22/02/2023-…)", "Lecture pour les vacances (01/07/2023-31/08/2023)"}),
            ("Cinema", {"Playlist cinéma (…-28/02/2023)"}),
            ("playlist lecture", set()),
        ],
    )
    def test_autocomplete_criteria(self, authenticated_client, search_query, expected_texts):
        criteria_factories.CriterionFactory(name="Bonne offre d'appel")
        criteria_factories.CriterionFactory(name="Mauvaise accroche", startDateTime=datetime.datetime(2023, 2, 22, 12))
        criteria_factories.CriterionFactory(name="Offre du moment")
        criteria_factories.CriterionFactory(
            name="Lecture pour les vacances",
            startDateTime=datetime.datetime(2023, 7, 1, 8),
            endDateTime=datetime.datetime(2023, 8, 31, 21, 59),
        )
        criteria_factories.CriterionFactory(name="Playlist cinéma", endDateTime=datetime.datetime(2023, 2, 28, 22, 59))

        _test_autocomplete(authenticated_client, "backoffice_web.autocomplete_criteria", search_query, expected_texts)
